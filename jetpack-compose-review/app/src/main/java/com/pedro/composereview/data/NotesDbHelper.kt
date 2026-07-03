package com.pedro.composereview.data

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

/** Camada de persistência real por trás do NotesProvider: uma tabela SQLite. */
class NotesDbHelper(context: Context) :
    SQLiteOpenHelper(context, DATABASE_NAME, null, DATABASE_VERSION) {

    override fun onCreate(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE ${NotesContract.TABLE_NAME} (
                ${NotesContract.Columns.ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                ${NotesContract.Columns.TITLE} TEXT NOT NULL,
                ${NotesContract.Columns.CREATED_AT} INTEGER NOT NULL
            )
            """.trimIndent()
        )
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        db.execSQL("DROP TABLE IF EXISTS ${NotesContract.TABLE_NAME}")
        onCreate(db)
    }

    companion object {
        private const val DATABASE_NAME = "notes.db"
        private const val DATABASE_VERSION = 1
    }
}
