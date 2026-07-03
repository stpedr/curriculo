# Compose Review

Aplicação Android de exemplo criada para revisar:

- Jetpack Compose: `@Composable`, composição/recomposição, `state`,
  `remember`, `mutableStateOf`, UI declarativa;
- Content Provider e compartilhamento de dados;
- SharedPreferences e suas limitações;
- Activity/Fragment lifecycle;
- Coroutines;
- MVVM;
- StateFlow / LiveData.

## Como abrir

1. Abra a pasta `jetpack-compose-review/` no Android Studio (Koala ou mais
   recente).
2. Deixe o Android Studio gerar o Gradle Wrapper automaticamente (`File >
   Sync Project with Gradle Files`).
3. Rode o módulo `app` em um emulador ou dispositivo com Android 7.0+ (API 24).

## Estrutura

```
app/src/main/java/com/pedro/composereview/
├── MainActivity.kt          # Activity Compose + telas 1 (contador) e 2 (tarefas)
├── data/                    # ContentProvider + SQLite (tela 3: Notas)
│   ├── Note.kt
│   ├── NotesContract.kt
│   ├── NotesDbHelper.kt
│   ├── NotesProvider.kt
│   └── NotesRepository.kt   # Coroutines + Flow sobre o ContentProvider
├── prefs/
│   └── UserPreferences.kt   # SharedPreferences
├── ui/
│   ├── notes/
│   │   ├── NotesViewModel.kt  # MVVM + StateFlow/LiveData
│   │   └── NotesScreen.kt     # tela 3, Compose
│   └── theme/                 # Theme.kt, Color.kt, Type.kt (Material 3)
└── lifecycle/                # demo clássica de Activity/Fragment (Views + XML)
    ├── LifecycleDemoActivity.kt
    └── LifecycleDemoFragment.kt
```

A tela principal (Compose) tem 4 seções: **Contador** e **Lista de
tarefas** (Compose "puro", estado local), **Notas** (MVVM completo:
ContentProvider + SharedPreferences + Coroutines + StateFlow/LiveData) e
um botão para abrir a **demo de lifecycle** (Activity/Fragment clássicos
com Views/XML, fora do fluxo Compose).

A explicação detalhada de cada tópico e de como ele aparece no código
está em [`docs/revisao-jetpack-compose.pdf`](docs/revisao-jetpack-compose.pdf)
(gerado a partir de `docs/revisao-jetpack-compose.tex`).
