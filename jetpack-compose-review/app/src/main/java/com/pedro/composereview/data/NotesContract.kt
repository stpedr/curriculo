package com.pedro.composereview.data

import android.net.Uri
import android.provider.BaseColumns

/**
 * Contrato público do NotesProvider: authority, URIs e nomes de coluna.
 * Qualquer app (inclusive este) que queira ler/escrever notas via
 * ContentResolver depende apenas deste contrato, nunca do SQLite por trás.
 */
object NotesContract {

    const val AUTHORITY = "com.pedro.composereview.provider"
    private const val PATH_NOTES = "notes"

    val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/$PATH_NOTES")

    const val CONTENT_TYPE = "vnd.android.cursor.dir/vnd.$AUTHORITY.$PATH_NOTES"
    const val CONTENT_ITEM_TYPE = "vnd.android.cursor.item/vnd.$AUTHORITY.$PATH_NOTES"

    const val TABLE_NAME = "notes"

    object Columns {
        const val ID = BaseColumns._ID
        const val TITLE = "title"
        const val CREATED_AT = "created_at"
    }
}
