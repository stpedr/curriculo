# Compose Review

Aplicação Android mínima em Jetpack Compose, criada para revisar os seguintes
conceitos: `@Composable`, composição/recomposição, `state`, `remember`,
`mutableStateOf` e UI declarativa.

## Como abrir

1. Abra a pasta `jetpack-compose-review/` no Android Studio (Koala ou mais
   recente).
2. Deixe o Android Studio gerar o Gradle Wrapper automaticamente (`File >
   Sync Project with Gradle Files`).
3. Rode o módulo `app` em um emulador ou dispositivo com Android 7.0+ (API 24).

## Estrutura

```
app/src/main/java/com/pedro/composereview/
├── MainActivity.kt          # Activity + todos os Composables da tela
└── ui/theme/                # Theme.kt, Color.kt, Type.kt (Material 3)
```

A explicação detalhada da estrutura e de como cada conceito de Compose
aparece no código está em [`docs/revisao-jetpack-compose.pdf`](docs/revisao-jetpack-compose.pdf)
(gerado a partir de `docs/revisao-jetpack-compose.tex`).
