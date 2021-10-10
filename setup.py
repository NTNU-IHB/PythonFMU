import os
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

cwd = os.getcwd()
WINDOWS = (os.name == 'nt')

buildFolder = "tmp-build"


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        if not os.path.exists(os.path.join(cwd, buildFolder)):
            os.mkdir(os.path.join(cwd, buildFolder))
            build_type = 'Release'
            # configure
            cmake_args = [
                'cmake',
                '../pythonfmu/pythonfmu-export',
                '-DCMAKE_BUILD_TYPE={}'.format(build_type)
            ]
            if WINDOWS:
                cmake_args.append('-A x64')
            os.chdir(os.path.join(cwd, buildFolder))
            subprocess.check_call(cmake_args)
            cmake_args_build = [
                'cmake',
                '--build',
                '.'
            ]
            if WINDOWS:
                cmake_args_build.append('--config Release')
            subprocess.check_call(cmake_args_build)
            os.chdir("..")


class CMakeBuild(build_ext):
    def run(self):
        pass
        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        pass


# See setup.cfg for Python package parameters
setup(
    ext_modules=[CMakeExtension('.')],
    cmdclass=dict(build_ext=CMakeBuild),
)
