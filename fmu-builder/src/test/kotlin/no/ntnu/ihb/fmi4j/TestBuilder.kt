package no.ntnu.ihb.fmi4j

import no.ntnu.ihb.fmi4j.importer.fmi2.Fmu
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.condition.EnabledOnOs
import org.junit.jupiter.api.condition.OS
import java.io.File

@EnabledOnOs(OS.WINDOWS)
class TestBuilder {

    companion object {
        val group = "no.ntnu.ihb.fmi4j"
        val dest = File("build/generated").absolutePath
        val jar = File("../fmu-slaves/build/libs/fmu-slaves.jar").absolutePath
    }

    @Test
    fun testJavaClass() {
        FmuBuilder.main(arrayOf("-f", jar, "-m", "$group.JavaTestSlave", "-d", dest))
        for (i in 0..2) {
            testFmu(File(dest, "Test.fmu"))
        }
    }

    @Test
    fun testKotlinClass() {
        FmuBuilder.main(arrayOf("-f", jar, "-m", "$group.KotlinTestSlave", "-d", dest))
        testFmu(File(dest, "KotlinTestSlave.fmu"))
    }

    private fun testFmu(fmuFile: File) {
        Assertions.assertTrue(fmuFile.exists())

        Fmu.from(fmuFile).use { fmu ->

            val slave1 = fmu.asCoSimulationFmu().newInstance()
            val slave2 = fmu.asCoSimulationFmu().newInstance()

            Assertions.assertTrue(slave1.simpleSetup())
            Assertions.assertTrue(slave2.simpleSetup())

            Assertions.assertTrue(slave1.doStep(0.1))
            Assertions.assertTrue(slave2.doStep(0.1))

            slave1.close()
            slave2.close()

        }

    }

}
