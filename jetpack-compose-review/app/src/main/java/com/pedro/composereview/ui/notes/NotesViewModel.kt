package com.pedro.composereview.ui.notes

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.asLiveData
import androidx.lifecycle.viewModelScope
import com.pedro.composereview.data.Note
import com.pedro.composereview.data.NotesRepository
import com.pedro.composereview.prefs.UserPreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class NotesUiState(
    val notes: List<Note> = emptyList(),
    val isLoading: Boolean = true
)

/**
 * ViewModel: o "V" que fica entre a UI (Compose) e o Model
 * (NotesRepository/SharedPreferences). Ele sobrevive a recomposições e a
 * mudanças de configuração (rotação de tela), e não conhece nada de
 * Compose — só expõe estado observável e funções para a UI chamar.
 *
 * Isso é MVVM: a View (NotesScreen) apenas renderiza `uiState` e envia
 * eventos (addNote, deleteNote); toda a lógica de "o que fazer com esse
 * evento" mora aqui, não na função @Composable.
 */
class NotesViewModel(application: Application) : AndroidViewModel(application) {

    private val repository = NotesRepository(application.contentResolver)
    private val preferences = UserPreferences(application)

    private val _uiState = MutableStateFlow(NotesUiState())

    /**
     * StateFlow: sempre tem um valor atual (não há "sem estado inicial"),
     * suporta múltiplos coletores e é a fonte de verdade única da tela.
     * É a opção recomendada hoje para expor estado de UI a partir de um
     * ViewModel.
     */
    val uiState: StateFlow<NotesUiState> = _uiState.asStateFlow()

    /**
     * LiveData incluída apenas para comparação no relatório: também é
     * observável e lifecycle-aware, mas não tem operadores de coroutines
     * nativos e, antes do Compose, exigia `observe(lifecycleOwner) { }`
     * em vez de coleta via Flow. Aqui ela é derivada do próprio
     * StateFlow com `asLiveData()`.
     */
    val noteCountLiveData: LiveData<Int> = uiState.map { it.notes.size }.asLiveData()

    init {
        // viewModelScope é cancelado automaticamente quando o ViewModel
        // é destruído (onCleared), evitando vazamento de coroutines.
        viewModelScope.launch {
            repository.observeNotes().collect { notes ->
                _uiState.update { current -> current.copy(notes = notes, isLoading = false) }
            }
        }
    }

    fun addNote(title: String) {
        val trimmed = title.trim()
        if (trimmed.isEmpty()) return
        viewModelScope.launch {
            repository.addNote(trimmed)
            preferences.incrementNotesCreatedTotal()
        }
    }

    fun deleteNote(id: Long) {
        viewModelScope.launch { repository.deleteNote(id) }
    }

    fun notesCreatedTotal(): Int = preferences.getNotesCreatedTotal()

    fun userName(): String = preferences.getUserName()

    fun setUserName(name: String) = preferences.setUserName(name)
}
