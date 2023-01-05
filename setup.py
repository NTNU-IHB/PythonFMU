import os
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

cwd = os.getcwd()
WINDOWS = (os.name == 'nt')

buildFolder = "build"
nativeSources = os.path.join(cwd, "pythonfmu", "pythonfmu-export")


class CMakeExtension(Extension):
    def __init__(self, name):
        super().__init__(name, sources=[])


class CMakeBuild(build_ext):
    def run(self):
        for ext in self.extensions:
            self.build_extension(ext)
        super().run()

    def build_extension(self, ext):
        os.chdir(nativeSources)
        if not os.path.exists(buildFolder):
            os.mkdir(buildFolder)
        build_type = 'Release'
        # configure
        cmake_args = [
            'cmake', '.', '-B', buildFolder,
            '-DCMAKE_BUILD_TYPE={}'.format(build_type)
        ]
        if WINDOWS:
            cmake_args.extend(['-A', 'x64'])

        subprocess.check_call(cmake_args)
        cmake_args_build = [
            'cmake', '--build', buildFolder
        ]
        if WINDOWS:
            cmake_args_build.extend(['--config', 'Release'])
        subprocess.check_call(cmake_args_build)
        os.chdir(cwd)


# See setup.cfg for Python package parameters
setup(
    ext_modules=[CMakeExtension('.')],
    cmdclass=dict(build_ext=CMakeBuild)
)
