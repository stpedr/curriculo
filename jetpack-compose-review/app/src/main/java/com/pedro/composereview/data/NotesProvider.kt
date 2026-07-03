package com.pedro.composereview.data

import android.content.ContentProvider
import android.content.ContentUris
import android.content.ContentValues
import android.content.UriMatcher
import android.database.Cursor
import android.net.Uri

/**
 * ContentProvider é o componente Android voltado a COMPARTILHAR dados de
 * forma controlada: entre telas do próprio app (via ContentResolver, sem
 * acoplar quem lê a quem persiste) e, se `exported` fosse true, também
 * com outros apps — sempre passando por um contrato de URIs/permissões
 * em vez de expor o banco SQLite diretamente.
 *
 * Este provider expõe a tabela `notes` (ver [NotesDbHelper]) através de
 * duas URIs:
 *   content://<authority>/notes       -> coleção inteira
 *   content://<authority>/notes/{id}  -> uma nota especifica
 */
class NotesProvider : ContentProvider() {

    private lateinit var dbHelper: NotesDbHelper

    override fun onCreate(): Boolean {
        dbHelper = NotesDbHelper(context!!)
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<out String>?,
        selection: String?,
        selectionArgs: Array<out String>?,
        sortOrder: String?
    ): Cursor {
        val db = dbHelper.readableDatabase
        val cursor = when (uriMatcher.match(uri)) {
            NOTES -> db.query(
                NotesContract.TABLE_NAME, projection, selection, selectionArgs,
                null, null, sortOrder ?: "${NotesContract.Columns.CREATED_AT} DESC"
            )
            NOTE_ID -> db.query(
                NotesContract.TABLE_NAME, projection,
                "${NotesContract.Columns.ID} = ?", arrayOf(uri.lastPathSegment),
                null, null, null
            )
            else -> throw IllegalArgumentException("URI desconhecida: $uri")
        }
        cursor.setNotificationUri(context!!.contentResolver, uri)
        return cursor
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri {
        require(uriMatcher.match(uri) == NOTES) { "Insert só é suportado em $uri (coleção)" }
        val db = dbHelper.writableDatabase
        val id = db.insert(NotesContract.TABLE_NAME, null, values)
        val itemUri = ContentUris.withAppendedId(NotesContract.CONTENT_URI, id)
        // notifyChange e quem permite que observadores (ContentObserver)
        // registrados via ContentResolver.registerContentObserver saibam
        // que os dados mudaram, mesmo que tenham sido alterados por
        // outro componente/processo.
        context!!.contentResolver.notifyChange(itemUri, null)
        return itemUri
    }

    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?): Int {
        val db = dbHelper.writableDatabase
        val count = when (uriMatcher.match(uri)) {
            NOTE_ID -> db.delete(
                NotesContract.TABLE_NAME, "${NotesContract.Columns.ID} = ?",
                arrayOf(uri.lastPathSegment)
            )
            NOTES -> db.delete(NotesContract.TABLE_NAME, selection, selectionArgs)
            else -> throw IllegalArgumentException("URI desconhecida: $uri")
        }
        if (count > 0) context!!.contentResolver.notifyChange(uri, null)
        return count
    }

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<out String>?
    ): Int {
        val db = dbHelper.writableDatabase
        val count = when (uriMatcher.match(uri)) {
            NOTE_ID -> db.update(
                NotesContract.TABLE_NAME, values,
                "${NotesContract.Columns.ID} = ?", arrayOf(uri.lastPathSegment)
            )
            NOTES -> db.update(NotesContract.TABLE_NAME, values, selection, selectionArgs)
            else -> throw IllegalArgumentException("URI desconhecida: $uri")
        }
        if (count > 0) context!!.contentResolver.notifyChange(uri, null)
        return count
    }

    override fun getType(uri: Uri): String? = when (uriMatcher.match(uri)) {
        NOTES -> NotesContract.CONTENT_TYPE
        NOTE_ID -> NotesContract.CONTENT_ITEM_TYPE
        else -> null
    }

    companion object {
        private const val NOTES = 1
        private const val NOTE_ID = 2

        private val uriMatcher = UriMatcher(UriMatcher.NO_MATCH).apply {
            addURI(NotesContract.AUTHORITY, "notes", NOTES)
            addURI(NotesContract.AUTHORITY, "notes/#", NOTE_ID)
        }
    }
}
