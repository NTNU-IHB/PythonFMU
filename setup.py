from pathlib import Path
import os
import shutil
import sys
import platform
import subprocess

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=""):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake must be installed to build the following extensions: "
                + ", ".join(e.name for e in self.extensions)
            )

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        system = platform.system()
        is_64bits = sys.maxsize > 2**32
        platforms = {
            "Darwin": "darwin",
            "Linux": "linux", 
            "Windows": "win",
        }
        platform_ = platforms[system] + "64" if is_64bits else "32"
        extdir = Path(self.get_ext_fullpath(ext.name)).parent.absolute() / "resources" / "binaries" / platform_
        extdir.mkdir(parents=True, exist_ok=True)
        
        cmake_args = [
            f"-DPython3_ROOT_DIR={sys.prefix}"
        ]

        cfg = "Debug" if self.debug else "Release"
        build_args = ["--config", cfg]

        if platform.system() == "Windows":
            cmake_args += [
                f"-DCMAKE_RUNTIME_OUTPUT_DIRECTORY_{cfg.upper()}={extdir!s}",
                f"-DCMAKE_BUILD_TYPE={cfg}"
            ]
            if is_64bits and os.environ.get("CMAKE_GENERATOR", "Visual Studio").startswith("Visual Studio"):
                # To deactivate this option, you need to SET "CMAKE_GENERATOR=generator" for example `NMake Makefiles`
                cmake_args += ['-A', 'x64']  # Valid only for CMAKE_GENERATOR="Visual Studio ..."
            # build_args += ['--', '/m']
        else:
            cmake_args += [
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir!s}",
                f"-DCMAKE_BUILD_TYPE={cfg}"
            ]
            # build_args += ['--', '-j2']

        env = os.environ.copy()
        env["CXXFLAGS"] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get("CXXFLAGS", ""), self.distribution.get_version()
        )

        if os.path.exists(self.build_temp):
            shutil.rmtree(self.build_temp)
        os.makedirs(self.build_temp)

        subprocess.check_call(
            ["cmake", ext.sourcedir] + cmake_args, cwd=self.build_temp, env=env
        )
        subprocess.check_call(
            ["cmake", "--build", "."] + build_args, cwd=self.build_temp
        )


# See setup.cfg for Python package parameters
setup(
    ext_modules=[CMakeExtension("pythonfmu.export", "pythonfmu/pythonfmu-export")],
    cmdclass=dict(build_ext=CMakeBuild),
)
