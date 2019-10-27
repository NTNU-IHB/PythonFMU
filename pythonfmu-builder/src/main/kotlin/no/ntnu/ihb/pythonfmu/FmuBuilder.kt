package no.ntnu.ihb.pythonfmu

import no.ntnu.ihb.pythonfmu.util.ModelDescriptionFetcher
import picocli.CommandLine
import java.io.BufferedOutputStream
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.nio.file.Files
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

object FmuBuilder {

    private const val fmi2slaveFileName = "fmi2slave.py"

    private fun readXML(scriptFile: File, moduleName: String, projectFiles: List<File>): String {

        val tempDir =  Files.createTempDirectory("pythonfmu_").toFile()
        try {
            scriptFile.copyTo(File(tempDir, scriptFile.name))
            projectFiles.forEach {
                it.copyRecursively(File(tempDir, it.name))
            }

            return ModelDescriptionFetcher
                    .getModelDescription(tempDir.absolutePath, moduleName)
        } finally {
            tempDir.deleteRecursively()
        }

    }

    @CommandLine.Command(name = "pythonfmu-builder")
    class Args : Runnable {

        @CommandLine.Option(names = ["-h", "--help"], description = ["Print this message and quits."], usageHelp = true)
        var showHelp = false

        @CommandLine.Option(names = ["-f", "--file"], description = ["Path to the Python script."], required = true)
        lateinit var scriptFile: File

        @CommandLine.Option(names = ["-d", "--dest"], description = ["Where to save the FMU."], required = false)
        var destFile: File? = null

        @CommandLine.Parameters(arity = "0..*", paramLabel = "Project files", description = ["Additional project files required by the Python script."])
        var projectFiles = mutableListOf<File>()

        override fun run() {

            require(scriptFile.exists()) { "No such File '$scriptFile'" }
            require(scriptFile.name.endsWith(".py")) { "File '${scriptFile.name}' must have extension '.py'!" }

            val scriptParentFile = scriptFile.absoluteFile.parentFile
            val moduleName = scriptFile.nameWithoutExtension
            val xml = readXML(scriptFile, moduleName, projectFiles)

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

            var fmi2SlavePyFileFound = false

            ZipOutputStream(BufferedOutputStream(FileOutputStream(destFile))).use { zos ->

                fun addFile(file: File, parentDirName: String) {

                    if (file.name == fmi2slaveFileName) {
                        fmi2SlavePyFileFound = true
                    }

                    val fileName = "$parentDirName/${file.name}"
                    if (file.isDirectory) {
                        if (file.name != "__pycache__") {
                            file.listFiles()?.forEach { addFile(it, fileName) }
                        }
                    } else {
                        zos.putNextEntry(ZipEntry(fileName))
                        FileInputStream(file).use { fis ->
                            zos.write(fis.readBytes())
                        }
                        zos.closeEntry()
                    }

                }

                zos.putNextEntry(ZipEntry("modelDescription.xml"))
                zos.write(xml.toByteArray())
                zos.closeEntry()

                zos.putNextEntry(ZipEntry("resources/"))
                addFile(scriptFile, "resources")

                zos.putNextEntry(ZipEntry("resources/slavemodule.txt"))
                zos.write(moduleName.toByteArray())
                zos.closeEntry()

                if (projectFiles.isEmpty()) {
                    val fmi2SlaveFile = File(scriptParentFile, fmi2slaveFileName)
                    if (fmi2SlaveFile.exists()) {
                        addFile(fmi2SlaveFile, "resources")
                    }
                } else {
                    projectFiles.forEach { projectFile ->
                        addFile(projectFile, "resources")
                    }
                }

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

            require(fmi2SlavePyFileFound) { "No file named $fmi2slaveFileName provided!" }

        }

    }

    @JvmStatic
    fun main(args: Array<String>) {
        CommandLine.run(Args(), System.out, *args)
    }

}
