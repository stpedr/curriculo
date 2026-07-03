package com.pedro.composereview.prefs

import android.content.Context
import android.content.SharedPreferences

/**
 * SharedPreferences é adequado para pares chave/valor pequenos e simples
 * (flags, contadores, um nome de usuário) — não para dados estruturados
 * ou relacionais (isso é papel do SQLite/ContentProvider, ver
 * [com.pedro.composereview.data.NotesProvider]). Limitações relevantes:
 *
 *  - Sem tipagem/validação de schema: chaves são Strings soltas, fáceis
 *    de digitar errado sem o compilador acusar.
 *  - Sem relações nem consultas: não há "WHERE" ou joins, só get/put por
 *    chave.
 *  - Todo o arquivo XML é lido para a memória na primeira leitura; em
 *    arquivos grandes isso pode custar tempo de I/O logo no início.
 *  - Não é observável de forma nativa em Compose/Flow (é preciso um
 *    OnSharedPreferenceChangeListener manual) — por isso não é uma boa
 *    fonte de verdade reativa como StateFlow.
 *  - `apply()` é assíncrono (grava em disco em background, não bloqueia
 *    a thread chamadora, mas não devolve confirmação); `commit()` é
 *    síncrono e bloqueia até gravar, devolvendo um Boolean de sucesso.
 *
 * Para dados estruturados ou grandes, ou quando se precisa observar
 * mudanças de forma reativa, o substituto recomendado hoje é o Jetpack
 * DataStore (Preferences ou Proto), que expõe os valores como Flow.
 */
class UserPreferences(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun getUserName(): String = prefs.getString(KEY_USER_NAME, "") ?: ""

    fun setUserName(name: String) {
        prefs.edit().putString(KEY_USER_NAME, name).apply()
    }

    fun getNotesCreatedTotal(): Int = prefs.getInt(KEY_NOTES_CREATED, 0)

    fun incrementNotesCreatedTotal() {
        prefs.edit().putInt(KEY_NOTES_CREATED, getNotesCreatedTotal() + 1).apply()
    }

    companion object {
        private const val PREFS_NAME = "compose_review_prefs"
        private const val KEY_USER_NAME = "user_name"
        private const val KEY_NOTES_CREATED = "notes_created_total"
    }
}
