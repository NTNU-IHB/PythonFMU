package no.ntnu.ihb.pythonfmu

import no.ntnu.ihb.fmi4j.importer.fmi2.Fmu
import no.ntnu.ihb.fmi4j.readInteger
import no.ntnu.ihb.fmi4j.readReal
import no.ntnu.ihb.fmi4j.writeInteger
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import java.io.File

class TestBuilder {

    @Test
    fun testBuilder() {

        val dest = "build/generated"
        val scriptFile = File(TestBuilder::class.java.classLoader.getResource("pythonslave.py").file).absolutePath

        FmuBuilder.main(arrayOf("-f", scriptFile, "-d", dest))

        val fmuFile = File(dest, "PythonSlave.fmu")
        Assertions.assertTrue(fmuFile.exists())

        Fmu.from(fmuFile).use { fmu ->

            fmu.asCoSimulationFmu().newInstance().use { slave ->

                slave.simpleSetup()

                for (i in 0 until 10) {
                    slave.doStep(1.0/100)
                }

                Assertions.assertEquals(1, slave.readInteger(0).value)
                Assertions.assertEquals(3.0, slave.readReal("realOut").value)

                Assertions.assertTrue(slave.writeInteger(0, 2).isOK())
                Assertions.assertEquals(2, slave.readInteger(0).value)

                slave.terminate()

            }

        }

    }

}
