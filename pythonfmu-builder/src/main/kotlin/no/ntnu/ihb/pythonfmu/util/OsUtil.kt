package no.ntnu.ihb.pythonfmu.util

object OsUtil {

    private const val MAC_OS_LIBRARY_EXTENSION = "dylib"
    private const val WINDOWS_LIBRARY_EXTENSION = "dll"
    private const val LINUX_LIBRARY_EXTENSION = "so"

    val osName: String = System.getProperty("os.name")
    val platformBitness: String = System.getProperty("sun.arch.data.model")

    val is32Bit: Boolean
        get() = platformBitness == "32"

    val is64Bit: Boolean
        get() = platformBitness == "64"

    val isWindows: Boolean
        get() = osName.startsWith("Windows")

    val isLinux: Boolean
        get() = osName.startsWith("Linux")

    val isMac: Boolean
        get() = osName.startsWith("Mac") || osName.startsWith("Darwin")

    val currentOS: String
        get() {
            return when {
                isMac -> "darwin$platformBitness"
                isLinux -> "linux$platformBitness"
                isWindows -> "win$platformBitness"
                else -> throw RuntimeException("Unsupported OS: $osName")
            }
        }

    val libPrefix: String
        get() {
            return when {
                isMac -> "" // NOT SURE IF THIS IS CORRECT!
                isLinux -> "lib"
                isWindows -> ""
                else -> throw RuntimeException("Unsupported OS: $osName")
            }
        }

    val libExtension: String
        get() {
            return when {
                isMac -> MAC_OS_LIBRARY_EXTENSION
                isLinux -> LINUX_LIBRARY_EXTENSION
                isWindows -> WINDOWS_LIBRARY_EXTENSION
                else -> throw RuntimeException("Unsupported OS: $osName")
            }
        }

}
