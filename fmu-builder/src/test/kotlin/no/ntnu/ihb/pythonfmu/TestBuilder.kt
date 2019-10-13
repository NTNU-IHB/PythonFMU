package no.ntnu.ihb.pythonfmu

import no.ntnu.ihb.fmi4j.*
import no.ntnu.ihb.fmi4j.importer.fmi2.Fmu
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import java.io.File

class TestBuilder {

    @Test
    fun testBuilder() {

        val dest = "build/generated"
        val scriptFile = File(TestBuilder::class.java.classLoader.getResource("pythonslave.py").file).absolutePath

        FmuBuilder.main(arrayOf("-f", scriptFile, "-c", "PythonSlave", "-d", dest))

        val fmuFile = File(dest, "PythonSlave.fmu")
        Assertions.assertTrue(fmuFile.exists())

        Fmu.from(fmuFile).use { fmu ->

            fmu.asCoSimulationFmu().newInstance().use { slave ->

                Assertions.assertTrue(slave.simpleSetup())

                val dt = 1.0/100
                for (i in 0 until 10) {
                    Assertions.assertTrue(slave.doStep(dt))
                }

                Assertions.assertEquals(1, slave.readInteger(0).value)
                Assertions.assertEquals(3.0, slave.readReal("realOut").value)

                Assertions.assertTrue(slave.writeInteger("intOut", 2).isOK())
                Assertions.assertEquals(2, slave.readInteger("intOut").value)

                Assertions.assertTrue(slave.writeReal("realOut", 6.0).isOK())
                Assertions.assertEquals(6.0, slave.readReal("realOut").value)

                Assertions.assertTrue(slave.readBoolean("booleanVariable").value)

                slave.terminate()

            }

        }

    }

}
