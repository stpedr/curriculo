package com.pedro.composereview.data

import android.content.ContentResolver
import android.content.ContentUris
import android.content.ContentValues
import android.database.ContentObserver
import android.os.Handler
import android.os.Looper
import android.provider.BaseColumns
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.callbackFlow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.withContext

/**
 * Camada de dados (o "Model" do MVVM): esconde do ViewModel os detalhes
 * de que a fonte de dados é um ContentProvider sobre SQLite. Toda
 * operação de I/O roda em Dispatchers.IO via coroutines, nunca na thread
 * principal.
 */
class NotesRepository(private val contentResolver: ContentResolver) {

    /**
     * callbackFlow "traduz" o mundo de callbacks do Android
     * (ContentObserver.onChange) para o mundo de coroutines (Flow):
     * cada mudança nos dados emite uma nova lista, e quem coleta o Flow
     * (o ViewModel) recebe atualizações automaticamente, sem precisar
     * fazer polling.
     */
    fun observeNotes(): Flow<List<Note>> = callbackFlow {
        val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
            override fun onChange(selfChange: Boolean) {
                trySend(queryNotes())
            }
        }
        contentResolver.registerContentObserver(NotesContract.CONTENT_URI, true, observer)
        trySend(queryNotes())
        awaitClose { contentResolver.unregisterContentObserver(observer) }
    }.flowOn(Dispatchers.IO)

    private fun queryNotes(): List<Note> {
        val notes = mutableListOf<Note>()
        contentResolver.query(NotesContract.CONTENT_URI, null, null, null, null)?.use { cursor ->
            val idIndex = cursor.getColumnIndexOrThrow(BaseColumns._ID)
            val titleIndex = cursor.getColumnIndexOrThrow(NotesContract.Columns.TITLE)
            val createdIndex = cursor.getColumnIndexOrThrow(NotesContract.Columns.CREATED_AT)
            while (cursor.moveToNext()) {
                notes += Note(
                    id = cursor.getLong(idIndex),
                    title = cursor.getString(titleIndex),
                    createdAt = cursor.getLong(createdIndex)
                )
            }
        }
        return notes
    }

    suspend fun addNote(title: String): Unit = withContext(Dispatchers.IO) {
        val values = ContentValues().apply {
            put(NotesContract.Columns.TITLE, title)
            put(NotesContract.Columns.CREATED_AT, System.currentTimeMillis())
        }
        contentResolver.insert(NotesContract.CONTENT_URI, values)
        Unit
    }

    suspend fun deleteNote(id: Long): Unit = withContext(Dispatchers.IO) {
        val itemUri = ContentUris.withAppendedId(NotesContract.CONTENT_URI, id)
        contentResolver.delete(itemUri, null, null)
        Unit
    }
}
