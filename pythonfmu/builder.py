"""Python FMU builder"""
import argparse
import importlib
import itertools
from pathlib import Path
import platform
import shutil
import tempfile
from typing import Iterable, Optional, Set, Union
import zipfile

from .fmi2slave import Fmi2Slave

FilePath = Union[str, Path]
HERE = Path(__file__).parent

lib_prefix = "lib" if platform.system() == "Linux" else ""

lib_extension = ({"Linux": "so", "Windows": "dll"}).get(platform.system(), None)


class ModelDescriptionFetcher:

    @staticmethod
    def get_model_description(
        filepath: Path, module_name: str, class_name: Optional[str] = None
    ) -> str:
        # Import the user interface
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        fmu_interface = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fmu_interface)
        # Instantiate the interface
        class_name = class_name or getattr(fmu_interface, "slave_class")
        instance = getattr(fmu_interface, class_name)()
        if not isinstance(instance, Fmi2Slave):
            raise TypeError(
                f"The provided class '{class_name}' does not inherit from {Fmi2Slave.__qualname__}"
            )
        # Produce the xml
        return instance.modelName, instance.to_xml()


class FmuBuilder:

    FMI2SLAVE_FILENAME = HERE / "fmi2slave.py"

    @staticmethod
    def __readXML(
        script_file: Path,
        module_name: str,
        project_files: Set[Path],
        class_name: Optional[str] = None,
    ) -> str:
        with tempfile.TemporaryDirectory(prefix="pythonfmu_") as tempd:
            temp_dir = Path(tempd)
            shutil.copy2(script_file, temp_dir)
            for file_ in project_files:
                if file_ == script_file.parent:
                    new_folder = temp_dir / file_.name
                    new_folder.mkdir()
                    for f in file_.iterdir():
                        if f.is_dir():
                            dest = new_folder / f.name
                            shutil.copytree(f, dest)
                        elif f.name != script_file.name:
                            shutil.copy2(f, new_folder)
                else:
                    if file_.is_dir():
                        dest = temp_dir / file_.name
                        shutil.copytree(file_, dest)
                    else:
                        shutil.copy2(file_, temp_dir)

            return ModelDescriptionFetcher.get_model_description(
                temp_dir.absolute() / script_file.name, module_name, class_name
            )

    @staticmethod
    def build_FMU(
        script_file: FilePath,
        dest: FilePath = ".",
        project_files: Iterable[FilePath] = [],
        class_name: Optional[str] = None,
    ):
        script_file = Path(script_file)
        if not script_file.exists():
            raise ValueError(f"No such file {script_file!s}")
        if not script_file.suffix.endswith(".py"):
            raise ValueError(f"File {script_file!s} must have extension '.py'!")

        dest = Path(dest)
        if not dest.exists():
            dest.mkdir(parents=True)
        project_files = set([Path(f) for f in project_files])

        script_parent = script_file.resolve().parent.absolute()
        module_name = script_file.stem
        model_identifier, xml = FmuBuilder.__readXML(script_file, module_name, project_files, class_name)

        dest_file = dest / f"{model_identifier}.fmu"

        with zipfile.ZipFile(dest_file, "w") as zip_fmu:
            zip_fmu.writestr("modelDescription.xml", xml)

            resource = Path("resources")

            zip_fmu.write(script_file, arcname=resource.joinpath(script_file.name))
            zip_fmu.writestr(str(resource.joinpath("slavemodule.txt")), module_name)

            # Add project files
            # TODO

            # Add FMI API wrapping Python class
            binaries = Path("binaries")
            src_binaries = HERE / "resources" / "binaries"
            for f in itertools.chain(
                src_binaries.rglob("*.dll"), src_binaries.rglob("*.so")
            ):
                relative_f = f.relative_to(src_binaries)
                arcname = (
                    binaries
                    / relative_f.parent
                    / f"{model_identifier}{relative_f.suffix}"
                )
                zip_fmu.write(f, arcname=arcname)

    @staticmethod
    def main():
        parser = argparse.ArgumentParser(
            prog="pythonfmu-builder", description="Build a FMU from a Python script."
        )

        parser.add_argument(
            "-f",
            "--file",
            dest="script_file",
            help="Path to the Python script.",
            required=True,
        )
        parser.add_argument(
            "-c",
            "--class",
            dest="class_name",
            help="Class name of the inter",
            default=None,
        )
        parser.add_argument(
            "-d", "--dest", dest="dest", help="Where to save the FMU.", default=None
        )
        parser.add_argument(
            "project_files",
            metavar="Project files",
            nargs="*",
            help="Additional project files required by the Python script.",
            default=[],
        )

        options = parser.parse_args()
        FmuBuilder.build_FMU(
            options.script_file,
            options.dest or ".",
            options.project_files,
            options.class_name,
        )


if __name__ == "__main__":
    FmuBuilder.main()
