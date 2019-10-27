package no.ntnu.ihb.pythonfmu.util

import java.io.File
import java.io.FileOutputStream
import java.nio.file.Files

object ModelDescriptionFetcher {

    private val fileName = "${OsUtil.libPrefix}pythonfmu-export.${OsUtil.libExtension}"

    init {

        val tempFolder = Files.createTempDirectory("pythonfmu_dll").toFile()
        val pythonFmuDll = File(tempFolder, fileName)
        try {
            val resourceName = "binaries/${OsUtil.currentOS}/$fileName"
            ModelDescriptionFetcher::class.java.classLoader
                    .getResourceAsStream(resourceName)?.use { `is` ->
                        FileOutputStream(pythonFmuDll).use { fos ->
                            `is`.copyTo(fos)
                        }
                    } ?: throw IllegalStateException("NO such resource '$resourceName'!")
            System.load(pythonFmuDll.absolutePath)
        } catch (ex: Exception) {
            tempFolder.deleteRecursively()
            throw RuntimeException(ex)
        } finally {
            pythonFmuDll.deleteOnExit()
            tempFolder.deleteOnExit()
        }

    }

    external fun getModelDescription(scriptDir: String, moduleName: String): String

}
