"""CLI command to deploy a FMU."""
import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Union

from ._version import __version__
from .enums import PackageManager


# Dictionary of ("default file name", "associated package manager")
ENVIRONMENT_FILES = {
    "requirements.txt": PackageManager.pip,
    "environment.yaml": PackageManager.conda,
    "environment.yml": PackageManager.conda
}


def deploy(
    fmu_file: Union[str, Path],
    environment_filename: Union[str, Path, None],
    package_manager: Union[str, PackageManager, None]
) -> None:
    """Install Python dependency packages from requirement file shipped within the FMU.
    
    Args:
        fmu_file (str or pathlib.Path) : FMU file path
        environment_filename (str or pathlib.Path) : optional, requirements file within the `resources` folder of the FMU
        package_manager (str) : optional, Python package manager
    """
    fmu_file = Path(fmu_file)
    manager = None
    if package_manager is not None:
        manager = PackageManager(package_manager)

    env_content = None
    environment = None
    with zipfile.ZipFile(fmu_file) as files:
        names = files.namelist()

        environment = None
        if environment_filename is None:
            for spec in ENVIRONMENT_FILES:
                test = Path("resources") / spec
                if str(test) in names:
                    environment = test
                    manager = manager or ENVIRONMENT_FILES[spec]
                    break
            if environment is None:
                raise ValueError("Unable to find requirement file in the FMU resources folder.")
        else:
            environment = Path("resources") / environment_filename
            if str(environment) not in names:
                raise ValueError(f"Unable to find requirement file {environment_filename!s} in the FMU resources folder.")

            if manager is None:
                if environment_filename in ENVIRONMENT_FILES:
                    manager = ENVIRONMENT_FILES[environment_filename]
                elif environment_filename.endswith(".yaml") or environment_filename.endswith(".yml"):
                    manager = PackageManager.conda
                else:
                    manager = PackageManager.pip

        with files.open(str(environment), mode='r') as env_file:
            env_content = env_file.read()

    with TemporaryDirectory() as tmp:
        tempd = Path(tmp)

        copy_env = tempd / environment.name
        copy_env.write_bytes(env_content)

        if manager == PackageManager.pip:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", f"{copy_env!s}", "--progress-bar", "off"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
        elif manager == PackageManager.conda:
            conda_exe = os.environ.get("CONDA_EXE", "conda")
            subprocess.run(
                [conda_exe, "env", "update", f"--file={copy_env!s}", "--quiet"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )


def main():

    parser = argparse.ArgumentParser(
        prog="pythonfmu-deploy", 
        description="""Deploy a Python FMU.
        
        The command will look in the `resources` folder for one of the following files:
        - `requirements.txt`: Install dependencies using pip package manager
        - `environment.yaml`: Update the current environment using the conda package manager

        If you specify a environment file but no package manager, `conda` will be selected
        for `.yaml` and `.yml` otherwise `pip` will be used.

        The tool assume the Python environment in which the FMU should be executed
        is the current one.
        """
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="fmu_file",
        help="Path to the Python FMU.",
        required=True,
    )

    parser.add_argument(
        "-e",
        "--env",
        dest="env_file",
        help="Requirements or environment file.",
        default=None
    )

    parser.add_argument('pkg_manager', choices=['pip', 'conda'], default=None)
