package com.pedro.composereview

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.wrapContentWidth
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.pedro.composereview.lifecycle.LifecycleDemoActivity
import com.pedro.composereview.ui.notes.NotesCard
import com.pedro.composereview.ui.theme.ComposeReviewTheme

private const val TAG = "MainActivity"

/**
 * Activity: único ponto de entrada Android. Toda a UI abaixo dela é
 * construída de forma declarativa com Jetpack Compose (nada de XML/Views
 * — a exceção fica isolada em [LifecycleDemoActivity], criada só para
 * comparar com o ciclo de vida clássico de Activity/Fragment).
 *
 * Os overrides abaixo tornam visível (via Logcat, tag "MainActivity") o
 * ciclo de vida padrão da Activity: onCreate roda uma única vez; onStart
 * e onStop marcam visibilidade; onResume/onPause marcam o foco de
 * interação; onDestroy fecha o ciclo.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate")
        setContent {
            ComposeReviewTheme {
                Surface(modifier = Modifier) {
                    ReviewApp()
                }
            }
        }
    }

    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart")
    }

    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume")
    }

    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause")
    }

    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy")
    }
}

/** Composable raiz: apenas descreve a UI, sem logica de estado propria. */
@Composable
fun ReviewApp() {
    val context = LocalContext.current

    Scaffold(
        topBar = { TopAppBar(title = { Text("Jetpack Compose Review") }) }
    ) { padding ->
        Column(
            modifier = Modifier
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            SectionTitle("1. Contador (state + mutableStateOf + remember)")
            CounterCard()

            Divider()

            SectionTitle("2. Lista de tarefas (state hoisting)")
            TodoCard()

            Divider()

            SectionTitle("3. Notas (MVVM + ContentProvider + Coroutines + StateFlow/LiveData)")
            NotesCard()

            Divider()

            SectionTitle("4. Activity/Fragment lifecycle")
            Text(
                "Abre uma tela separada (Views + XML) que loga cada callback " +
                    "de ciclo de vida de Activity e Fragment no Logcat (tag \"LifecycleDemo\").",
                style = MaterialTheme.typography.bodySmall
            )
            OutlinedButton(onClick = {
                context.startActivity(Intent(context, LifecycleDemoActivity::class.java))
            }) { Text("Abrir demo de lifecycle") }
        }
    }
}

@Composable
private fun SectionTitle(text: String) {
    Text(text = text, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.titleMedium)
}

/**
 * Composable stateful: possui seu proprio estado (count) criado com
 * `remember { mutableStateOf(...) }`. Cada chamada a `count++` muda o
 * estado, o que invalida a composicao e agenda uma RECOMPOSICAO deste
 * Composable (Compose executa a funcao de novo, sem recriar a Activity
 * nem a arvore de Views).
 *
 * `recompositions` NAO e um MutableState: e um contador comum guardado
 * com `remember`. Ele e incrementado toda vez que a funcao roda de novo,
 * o que serve apenas para tornar a recomposicao visivel na tela, sem
 * disparar recomposicoes adicionais por si mesmo.
 */
@Composable
fun CounterCard() {
    var count by remember { mutableStateOf(0) }
    val recompositions = remember { intArrayOf(0) }
    recompositions[0] += 1

    Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp)) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("Valor: $count", style = MaterialTheme.typography.headlineSmall)
            Text(
                "Esta seção recompôs ${recompositions[0]} vez(es)",
                style = MaterialTheme.typography.bodySmall
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { count++ }) { Text("+1") }
                Button(onClick = { count-- }) { Text("-1") }
                TextButton(onClick = { count = 0 }) { Text("Resetar") }
            }
        }
    }
}

/**
 * Composable stateful "pai": guarda o estado (texto digitado e lista de
 * tarefas) e o repassa para composables filhos SEM estado proprio
 * (TaskList/TaskRow), que apenas recebem dados e callbacks. Esse padrao
 * e chamado de "state hoisting": o estado sobe para o dono que faz
 * sentido controla-lo, e os filhos ficam simples, reutilizaveis e
 * faceis de pre-visualizar/testar.
 */
@Composable
fun TodoCard() {
    var input by remember { mutableStateOf("") }
    val tasks = remember { mutableStateListOf("Revisar @Composable", "Estudar remember") }

    Card(modifier = Modifier.fillMaxWidth(), elevation = CardDefaults.cardElevation(2.dp)) {
        Column(modifier = Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = input,
                    onValueChange = { input = it },
                    label = { Text("Nova tarefa") },
                    modifier = Modifier.weight(1f)
                )
                Button(
                    onClick = {
                        if (input.isNotBlank()) {
                            tasks.add(input.trim())
                            input = ""
                        }
                    },
                    modifier = Modifier.wrapContentWidth()
                ) { Text("Add") }
            }

            Spacer(modifier = Modifier.height(4.dp))

            TaskList(tasks = tasks, onRemove = { task -> tasks.remove(task) })
        }
    }
}

/** Composable stateless: recebe uma lista e um callback, apenas descreve a UI. */
@Composable
fun TaskList(tasks: List<String>, onRemove: (String) -> Unit) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        if (tasks.isEmpty()) {
            Text("Nenhuma tarefa ainda.", style = MaterialTheme.typography.bodySmall)
        }
        tasks.forEach { task ->
            TaskRow(task = task, onRemove = { onRemove(task) })
        }
    }
}

/** Composable stateless e reutilizavel: uma unica linha de tarefa. */
@Composable
fun TaskRow(task: String, onRemove: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(text = task, modifier = Modifier.weight(1f))
        TextButton(onClick = onRemove) { Text("Remover") }
    }
}
