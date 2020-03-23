"""Python FMU builder"""
import argparse
import tempfile
from pathlib import Path
from typing import Union, Optional
from ._version import __version__
from .fmi2slave import FMI2_MODEL_OPTIONS
from .csvslave import create_csv_slave
from .builder import FmuBuilder

FilePath = Union[str, Path]


class CsvFmuBuilder:

    @staticmethod
    def build_FMU(
        csv_file: FilePath,
        dest: FilePath = ".",
        documentation_folder: Optional[FilePath] = None,
        **options,
    ) -> Path:

        options["project_files"] = {csv_file}

        def build() -> Path:
            with tempfile.TemporaryDirectory(prefix="pythonfmu_") as tempd:
                temp_dir = Path(tempd)
                script_file = temp_dir / (csv_file.stem + ".py")
                with open(script_file, "+w") as f:
                    f.write(create_csv_slave(csv_file))
                options["script_file"] = script_file
                return FmuBuilder.build_FMU(**options)

        return build()


def main():
    parser = argparse.ArgumentParser(
        prog="pythonfmu-csvbuilder", description="Build an FMU from a Python script or CSV file."
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
        dest="script_file",
        help="Path to the CSV file.",
        required=True,
    )

    parser.add_argument(
        "-d", "--dest", dest="dest", help="Where to save the FMU.", default="."
    )

    parser.add_argument(
        "--doc",
        dest="documentation_folder",
        help="Documentation folder to include in the FMU.",
        default=None,
    )

    for option in FMI2_MODEL_OPTIONS:
        action = "store_false" if option.value else "store_true"
        parser.add_argument(
            f"--{option.cli}",
            dest=option.name,
            help=f"If given, {option.name}={action[6:]}",
            action=action
        )

    options = vars(parser.parse_args())
    CsvFmuBuilder.build_FMU(**options)
