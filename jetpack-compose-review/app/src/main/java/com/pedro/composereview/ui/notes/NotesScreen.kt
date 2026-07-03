package com.pedro.composereview.ui.notes

import android.util.Log
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.livedata.observeAsState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel

private const val TAG = "NotesScreen"

/**
 * A "View" do MVVM: só descreve a UI a partir de `uiState` e repassa
 * eventos do usuário para o ViewModel. Nenhuma regra de negócio (acesso
 * ao ContentProvider, SharedPreferences, coroutines) aparece aqui.
 */
@Composable
fun NotesCard(viewModel: NotesViewModel = viewModel()) {
    // collectAsStateWithLifecycle: coleta o StateFlow apenas enquanto a
    // tela está pelo menos STARTED, pausando a coleta (e o trabalho que
    // ela dispara) quando a Activity vai para background - evita
    // desperdício de recursos comparado a coletar sempre.
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // observeAsState: forma equivalente de consumir LiveData a partir do
    // Compose, incluída aqui só para comparar com StateFlow acima.
    val liveNoteCount by viewModel.noteCountLiveData.observeAsState(initial = 0)

    var input by remember { mutableStateOf("") }
    var userName by remember { mutableStateOf(viewModel.userName()) }

    ObserveLifecycle(tag = TAG)

    Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp)) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(
                value = userName,
                onValueChange = {
                    userName = it
                    viewModel.setUserName(it)
                },
                label = { Text("Seu nome (SharedPreferences)") },
                modifier = Modifier.fillMaxWidth()
            )
            Text(
                "Notas criadas no total (SharedPreferences): ${viewModel.notesCreatedTotal()}",
                style = MaterialTheme.typography.bodySmall
            )
            Text(
                "Notas agora — StateFlow: ${uiState.notes.size} | LiveData: $liveNoteCount",
                style = MaterialTheme.typography.bodySmall
            )

            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = input,
                    onValueChange = { input = it },
                    label = { Text("Nova nota") },
                    modifier = Modifier.weight(1f)
                )
                Button(onClick = {
                    viewModel.addNote(input)
                    input = ""
                }) { Text("Add") }
            }

            when {
                uiState.isLoading -> CircularProgressIndicator()
                uiState.notes.isEmpty() -> Text(
                    "Nenhuma nota ainda.",
                    style = MaterialTheme.typography.bodySmall
                )
                else -> LazyColumn(modifier = Modifier.heightIn(max = 220.dp)) {
                    items(uiState.notes, key = { it.id }) { note ->
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(text = note.title, modifier = Modifier.weight(1f))
                            TextButton(onClick = { viewModel.deleteNote(note.id) }) { Text("Remover") }
                        }
                    }
                }
            }
        }
    }
}

/**
 * Ponte entre o Lifecycle "clássico" (Activity/Fragment) e o Compose:
 * DisposableEffect registra um observador enquanto este composable
 * estiver na composição e o remove em `onDispose`, evitando vazar o
 * observador quando a tela sai da árvore.
 */
@Composable
private fun ObserveLifecycle(tag: String) {
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_START || event == Lifecycle.Event.ON_STOP) {
                Log.d(tag, "Lifecycle event: $event")
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }
}
