package no.ntnu.ihb.pythonfmu

import no.ntnu.ihb.pythonfmu.util.ModelDescriptionFetcher
import picocli.CommandLine
import java.io.BufferedOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.lang.IllegalStateException
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

object FmuBuilder {

    @CommandLine.Command(name = "fmu-builder")
    class Args : Runnable {

        @CommandLine.Option(names = ["-h", "--help"], description = ["Print this message and quits."], usageHelp = true)
        var showHelp = false

        @CommandLine.Option(names = ["-f", "--file"], description = ["Path to the Python script."], required = true)
        lateinit var scriptFile: File

        @CommandLine.Option(names = ["-d", "--dest"], description = ["Where to save the FMU."], required = false)
        var destFile: File? = null

        override fun run() {

            require(scriptFile.exists()) { "No such File '$scriptFile'" }
            require(scriptFile.name == "model.py") { "File '${scriptFile.name}' must be named 'model.py'!" }

            val scriptDir = scriptFile.absoluteFile.parentFile

            val fmi2SlaveFile = File(scriptDir, "Fmi2Slave.py")
            check(fmi2SlaveFile.exists()) { "No 'Fmi2Slave.py' in script directory!" }

            val xml = ModelDescriptionFetcher.getModelDescription(scriptFile.absoluteFile.parentFile.absolutePath)

            val regex = "modelIdentifier=\"(\\w+)\"".toRegex()
            val groups = regex.findAll(xml).toList().map { it.groupValues }
            val modelIdentifier = groups[0][1]

            val destDir = destFile ?: File(".")
            val destFile = File(destDir, "${modelIdentifier}.fmu").apply {
                if (!exists()) {
                    parentFile.mkdirs()
                    createNewFile()
                }
            }

            ZipOutputStream(BufferedOutputStream(FileOutputStream(destFile))).use { zos ->

                zos.putNextEntry(ZipEntry("modelDescription.xml"))
                zos.write(xml.toByteArray())
                zos.closeEntry()

                zos.putNextEntry(ZipEntry("resources/"))

                zos.putNextEntry(ZipEntry("resources/model.py"))
                FileInputStream(scriptFile).use { fis ->
                    zos.write(fis.readBytes())
                }
                zos.closeEntry()

                zos.putNextEntry(ZipEntry("resources/Fmi2Slave.py"))
                FileInputStream(fmi2SlaveFile).use { fis ->
                    zos.write(fis.readBytes())
                }
                zos.closeEntry()

                zos.putNextEntry(ZipEntry("binaries/"))

                FmuBuilder::class.java.classLoader.getResourceAsStream("binaries/win32/pythonfmu-export.dll")?.use { `is` ->
                    zos.putNextEntry(ZipEntry("binaries/win32/"))
                    zos.putNextEntry(ZipEntry("binaries/win32/$modelIdentifier.dll"))
                    zos.write(`is`.readBytes())
                    zos.closeEntry()
                }

                FmuBuilder::class.java.classLoader.getResourceAsStream("binaries/win64/pythonfmu-export.dll")?.use { `is` ->
                    zos.putNextEntry(ZipEntry("binaries/win64/"))
                    zos.putNextEntry(ZipEntry("binaries/win64/$modelIdentifier.dll"))
                    zos.write(`is`.readBytes())
                    zos.closeEntry()
                }

                FmuBuilder::class.java.classLoader.getResourceAsStream("binaries/linux64/libpythonfmu-export.so")?.use { `is` ->
                    zos.putNextEntry(ZipEntry("binaries/linux64/"))
                    zos.putNextEntry(ZipEntry("binaries/linux64/$modelIdentifier.so"))
                    zos.write(`is`.readBytes())
                    zos.closeEntry()
                }

            }

        }

    }

    @JvmStatic
    fun main(args: Array<String>) {
        CommandLine.run(Args(), System.out, *args)
    }

}
