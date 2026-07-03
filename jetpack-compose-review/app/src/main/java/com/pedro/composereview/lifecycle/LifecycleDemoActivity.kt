package com.pedro.composereview.lifecycle

import android.os.Bundle
import android.util.Log
import androidx.appcompat.app.AppCompatActivity
import com.pedro.composereview.R

private const val TAG = "LifecycleDemo"

/**
 * Activity clássica (View system + XML), criada só para tornar visível o
 * ciclo de vida completo de Activity + Fragment lado a lado — o app
 * principal (MainActivity) é single-Activity/Compose e não usa Fragments,
 * então esse ciclo não apareceria em nenhum outro lugar do projeto.
 *
 * Toda transição de estado é logada com a tag "LifecycleDemo" (veja o
 * Logcat) e também aparece na tela, escrita pelo próprio
 * [LifecycleDemoFragment].
 */
class LifecycleDemoActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_lifecycle_demo)
        Log.d(TAG, "Activity onCreate")
    }

    override fun onStart() {
        super.onStart()
        Log.d(TAG, "Activity onStart")
    }

    override fun onResume() {
        super.onResume()
        Log.d(TAG, "Activity onResume")
    }

    override fun onPause() {
        super.onPause()
        Log.d(TAG, "Activity onPause")
    }

    override fun onStop() {
        super.onStop()
        Log.d(TAG, "Activity onStop")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "Activity onDestroy")
    }
}
