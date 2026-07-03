package com.pedro.composereview.lifecycle

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.TextView
import androidx.fragment.app.Fragment
import com.pedro.composereview.R

private const val TAG = "LifecycleDemo"

/**
 * Fragment tem um ciclo de vida mais granular que a Activity que o
 * hospeda: além de onCreate/onStart/onResume/onPause/onStop/onDestroy,
 * existem onAttach/onDetach (vínculo com a Activity) e
 * onCreateView/onDestroyView (a *view* do fragment pode ser destruída e
 * recriada — por exemplo em ViewPager — sem que o Fragment inteiro seja
 * destruído).
 *
 * Cada callback é registrado em [entries] e reimpresso na tela, então
 * rodar esta demo mostra, na ordem real, como Activity e Fragment se
 * intercalam (ex.: Fragment.onAttach/onCreate acontecem dentro do
 * Activity.onCreate).
 */
class LifecycleDemoFragment : Fragment(R.layout.fragment_lifecycle_demo) {

    private val entries = mutableListOf<String>()

    override fun onAttach(context: Context) {
        super.onAttach(context)
        log("Fragment onAttach")
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        log("Fragment onCreate")
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        log("Fragment onViewCreated")
    }

    override fun onStart() {
        super.onStart()
        log("Fragment onStart")
    }

    override fun onResume() {
        super.onResume()
        log("Fragment onResume")
    }

    override fun onPause() {
        super.onPause()
        log("Fragment onPause")
    }

    override fun onStop() {
        super.onStop()
        log("Fragment onStop")
    }

    override fun onDestroyView() {
        log("Fragment onDestroyView")
        super.onDestroyView()
    }

    override fun onDetach() {
        super.onDetach()
        log("Fragment onDetach")
    }

    private fun log(message: String) {
        Log.d(TAG, message)
        entries += message
        view?.findViewById<TextView>(R.id.text_log)?.text = entries.joinToString("\n")
    }
}
