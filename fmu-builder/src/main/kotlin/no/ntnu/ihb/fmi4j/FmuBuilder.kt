package no.ntnu.ihb.fmi4j

import no.ntnu.ihb.fmi4j.modeldescription.fmi2.Fmi2ModelDescription
import picocli.CommandLine
import java.io.*
import java.net.URLClassLoader
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
import javax.xml.bind.JAXB

object FmuBuilder {

    @CommandLine.Command(name = "fmu-builder")
    class Args : Runnable {

        @CommandLine.Option(names = ["-h", "--help"], description = ["Print this message and quits."], usageHelp = true)
        var showHelp = false

        @CommandLine.Option(names = ["-f", "--file"], description = ["Path to the Jar."], required = true)
        lateinit var jarFile: File

        @CommandLine.Option(names = ["-d", "--dest"], description = ["Where to save the FMU."], required = false)
        var destFile: File? = null

        @CommandLine.Option(names = ["-m", "--main"], description = ["Fully qualified name if the main class."], required = true)
        lateinit var mainClass: String

        override fun run() {

            require(jarFile.name.endsWith(".jar")) { "File $jarFile is not a .jar!" }
            require(jarFile.exists()) {"No such File '$jarFile'"}

            val classLoader = URLClassLoader(arrayOf(jarFile.toURI().toURL()))
            val superClass = classLoader.loadClass("no.ntnu.ihb.fmi4j.Fmi2Slave")
            val subClass = classLoader.loadClass(mainClass)
            val instance = subClass.newInstance()

            val define = superClass.getDeclaredMethod("define")
            define.isAccessible = true
            define.invoke(instance)
            val getModelDescription = superClass.getDeclaredMethod("getModelDescription")
            getModelDescription.isAccessible = true
            val md = getModelDescription.invoke(instance) as Fmi2ModelDescription
            val modelIdentifier = md.coSimulation.modelIdentifier

            val bos = ByteArrayOutputStream()
            JAXB.marshal(md, bos)

            val destDir = destFile ?: File(".")
            val destFile = File(destDir, "${modelIdentifier}.fmu").apply {
                if (!exists()) {
                    parentFile.mkdirs()
                    createNewFile()
                }
            }

            ZipOutputStream(BufferedOutputStream(FileOutputStream(destFile))).use { zos ->

                zos.putNextEntry(ZipEntry("modelDescription.xml"))
                zos.write(bos.toByteArray())
                zos.closeEntry()

                zos.putNextEntry(ZipEntry("resources/"))
                zos.putNextEntry(ZipEntry("resources/model.jar"))

                FileInputStream(jarFile).use { fis ->
                    zos.write(fis.readBytes())
                }
                zos.closeEntry()

                zos.putNextEntry(ZipEntry("resources/mainclass.txt"))
                zos.write(mainClass.toByteArray())
                zos.closeEntry()


                zos.putNextEntry(ZipEntry("binaries/"))

                FmuBuilder::class.java.classLoader.getResourceAsStream("binaries/win32/fmi4j-export.dll")?.use { `is` ->
                    zos.putNextEntry(ZipEntry("binaries/win32/"))
                    zos.putNextEntry(ZipEntry("binaries/win32/$modelIdentifier.dll"))
                    zos.write(`is`.readBytes())
                    zos.closeEntry()
                }

                FmuBuilder::class.java.classLoader.getResourceAsStream("binaries/win64/fmi4j-export.dll")?.use { `is` ->
                    zos.putNextEntry(ZipEntry("binaries/win64/"))
                    zos.putNextEntry(ZipEntry("binaries/win64/$modelIdentifier.dll"))
                    zos.write(`is`.readBytes())
                    zos.closeEntry()
                }

                FmuBuilder::class.java.classLoader.getResourceAsStream("binaries/linux64/libfmi4j-export.so")?.use { `is` ->
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
