package no.ntnu.ihb.pythonfmu

import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledOnOs
import org.junit.jupiter.api.condition.OS

@EnabledOnOs(OS.WINDOWS)
class TestBuilder {

    @Test
    fun test() {

        Native().also {
            println(it.getModelDescription("C:/Users/LarsIvar/Documents/IdeaProjects/PythonFMU/fmu-builder/src/main/resources"))
        }


    }

}

class Native {

    external fun getModelDescription(scriptPath: String): String

    companion object {

        init {

            System.loadLibrary("pythonfmu-export")
        }

    }

}
