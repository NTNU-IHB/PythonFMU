"""Python FMU builder"""
from __future__ import annotations

import argparse
import importlib
import itertools
import logging
import re
import shutil
import sys
import tempfile
from types import FunctionType
import zipfile
import inspect
from pathlib import Path
from typing import Iterable, Literal, Optional, Tuple, Union
from xml.dom.minidom import parseString
from xml.etree.ElementTree import Element, SubElement, tostring
from .osutil import get_lib_extension, get_platform
from .fmi2slave import FMI2_MODEL_OPTIONS, Fmi2Slave

FilePath = Union[str, Path]
HERE = Path(__file__).parent

logger = logging.getLogger(__name__)

def match_par(txt: str, left: str = "(", right: str = ")") -> tuple[int, Literal[-1]] | tuple[int, int]:
    """
    Finds the position of the matching closing parenthesis for the first opening parenthesis in a given string.
    
    Args:
        txt (str): The input string to search within.
        left (str, optional): The character representing the opening parenthesis. Defaults to "(".
        right (str, optional): The character representing the closing parenthesis. Defaults to ")".
    Returns:
        tuple[int, Literal[-1]] | tuple[int, int]: A tuple containing the position of the first opening parenthesis 
        and the position of the matching closing parenthesis. If no matching closing parenthesis is found, 
        returns the position of the first opening parenthesis and -1.
    Raises:
        AssertionError: If the first opening parenthesis is not found in the input string.
    """

    pos0 = txt.find(left, 0)
    assert pos0 >= 0, f"First {left} not found"
    stack = [pos0]
    i = pos0
    while True:
        i += 1
        if len(txt) <= i:
            return (pos0, -1)
        elif txt[i] == "#":  # comment
            i = txt.find("\n", i)
        elif txt[i:].startswith(left):
            stack.append(i)
        elif txt[i:].startswith(right):
            if len(stack) > 1:
                stack.pop(-1)
            else:
                return (pos0, i)

def get_model_class(src: Path) -> Fmi2Slave:
    """
    Given a source file path, dynamically import the module and find the class that 
    inherits from Fmi2Slave with the longest hierarchy.
    
    Args:
        src (Path): The path to the source file containing the module.
    Returns:
        Fmi2Slave: The class that inherits from Fmi2Slave with the longest hierarchy.
    Raises:
        ValueError: If no class inheriting from Fmi2Slave is found in the module.
        ValueError: If multiple classes with the same hierarchy length are found.
    """

    modulename = src.stem
    module = importlib.import_module(modulename)

    assert inspect.ismodule(module)

    modelclasses: dict[Fmi2Slave, int] = {}

    # get all classes in the module and store them in a dict with their hierarchy length
    for _, obj in inspect.getmembers(module):
        if inspect.isclass(obj):
            mro = inspect.getmro(obj)
            if Fmi2Slave in mro and not inspect.isabstract(obj):
                # store the class and its hierarchy length
                modelclasses.update({obj: len(mro)})

    if not len(modelclasses):
        raise ValueError(f"No child class of Fmi2Slave found in module {src}") from None
    else:
        # Return the class with the longest hierarchy, if no unique class is found, raise errors
        maxlen = max(n for n in modelclasses.values())
        classes = [c for c, n in modelclasses.items() if n == maxlen]
        if not len(classes):
            raise ValueError(f"No child class of Fmi2Slave found in module {src}") from None
        elif len(classes) > 1:
            raise ValueError(f"Non-unique Fmi2Slave-derived class in module {src}. Found {classes}.") from None
        else:
            return classes[0]
        
def update_model_parameters(src: Path, model: Fmi2Slave, newargs: dict) -> str:
    """
    Update the model parameters in the __init__ function of a given module.
    This function modifies the default values of the parameters in the __init__
    function of the specified model with the new values provided in the newargs
    dictionary. It returns the updated module code as a string.

    Args:
        src (Path): The path to the source file containing the module.
        model (Fmi2Slave): The model object whose __init__ function parameters
                           need to be updated.
        newargs (dict): A dictionary containing the new parameter values. The
                        keys should be the parameter names and the values should
                        be the new default values.
    Returns:
        str: The updated module code as a string.
    Raises:
        AssertionError: If the __init__ function is not found in the module.
    """

    init: FunctionType = None
    modulename = src.stem
    module = importlib.import_module(modulename)

    # Find the __init__ function in the module
    for name, obj in inspect.getmembers(model):
        if inspect.isfunction(obj) and name == "__init__":
            init = obj
            break

    module_lines = inspect.getsourcelines(module)

    assert init is not None, f"__init__() function not found in module {src}, model {model}"
    sig = inspect.signature(init)
    pars = sig.parameters
    newpars = []

    # Replace the default values of the parameters with the new provided values
    for p in pars:
        if p in newargs:
            par = pars[p].replace(default=newargs[p])
        else:
            par = pars[p]
        newpars.append(par)
    signew = inspect.Signature(parameters=newpars)

    # Replace the signature of the __init__ function
    init_line = inspect.getsourcelines(init)[1]
    from_init = "".join(line for line in module_lines[0][init_line - 1 :])
    init_pos = from_init.find("__init__")
    start, end = (match_par(from_init[init_pos - 1 :])[i] + init_pos for i in range(2))

    from_init = from_init.replace(from_init[start - 1 : end], str(signew), 1)
    module_code = "".join(line for line in module_lines[0][: init_line - 1]) + from_init

    # Ensure that Optional is imported from typing.
    module_code = "from typing import Optional\n" + module_code

    return module_code

def get_model_description(filepath: Path, module_name: str, class_name: str) -> Tuple[str, Element]:
    """Extract the FMU model description as XML.

    Args:
        filepath (pathlib.Path) : script file path
        module_name (str) : python module to load

    Returns:
        Tuple[str, xml.etree.TreeElement.Element] : FMU model name, model description
    """
    # Add current folder to handle local dependencies
    sys.path.insert(0, str(filepath.parent))
    try:
        # Import the user interface
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        fmu_interface = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fmu_interface)
        # Instantiate the interface
        instance = getattr(fmu_interface, class_name)(instance_name="dummyInstance", resources=str(filepath.parent))
    finally:
        sys.path.remove(str(filepath.parent))  # remove inserted temporary path

    if not isinstance(instance, Fmi2Slave):
        raise TypeError(
            f"The provided class '{class_name}' does not inherit from {Fmi2Slave.__qualname__}"
        )
    # Produce the xml
    return instance.modelName, instance.to_xml()

class FmuBuilder:

    @staticmethod
    def build_FMU(
        script_file: FilePath,
        dest: FilePath = ".",
        project_files: Iterable[FilePath] = set(),
        documentation_folder: Optional[FilePath] = None,
        newargs: dict | None = None,
        **options,
    ) -> Path:
        """ Build the FMU from the Python script, additional project files and documentatiion.

        Args:
            script_file (FilePath): The main Python script containing the Python model class
            dest (FilePath)='.': Optional destination path.
               If this is a full file name with '.fmu' extension, it is used as FMU file name.
               Otherwise the FMU file name is constructed automatically from the script file name.
            project_files (Iterable[FilePath]): Optional list/tuple of additional project files needed to run model
            documentation_folder (FilePath): Optional additional documentation (beyond modelDescription)
            newargs (dict): Optional dict of replacements of model class __init__() arguments.
        """
        script_file = Path(script_file)
        if not script_file.exists():
            raise ValueError(f"No such file {script_file!s}")
        if not script_file.suffix.endswith(".py"):
            raise ValueError(f"File {script_file!s} must have extension '.py'!")
        
        dest = Path(dest)
        if ( dest.suffix == '.fmu' and # explicit FMU file name shall always have suffix '.fmu'
             ( dest.is_file() or # Note that .is_file() returns False if the file does not yet exist
               not dest.is_dir())): # if dest represents an (existing) directory we cannot interpret as file!
            dest_file = dest
            dest = dest.parent
        else:
            dest_file = "" # FMU file name is automatically generated below
        if not dest.exists():
            dest.mkdir(parents=True)
        project_files = set(map(Path, project_files))

        if documentation_folder is not None:
            documentation_folder = Path(documentation_folder)
            if not documentation_folder.exists():
                raise ValueError(
                    f"The documentation folder does not exists {documentation_folder!s}"
                )

        if script_file.parent not in sys.path:
            sys.path.insert(0, str(script_file.parent))

        module_name = script_file.stem
        model_class = get_model_class(script_file)

        with tempfile.TemporaryDirectory(prefix="pythonfmu_") as tempd:
            temp_dir = Path(tempd)

            if newargs:
                model_file = temp_dir / f"{module_name}.py"
                updated_code = update_model_parameters(script_file, model_class, newargs)

                # Write the updated code to a new file
                model_file.write_text(updated_code)
            else:
                shutil.copy2(script_file, temp_dir)

            # Embed pythonfmu in the FMU so it does not need to be included
            dep_folder = temp_dir / "pythonfmu"
            dep_folder.mkdir()
            for dep in HERE.glob('*.py'):  # Find all python files at the same level as this one
                shutil.copy2(dep, dep_folder)
            for file_ in project_files:
                if file_ == script_file.parent:
                    new_folder = temp_dir / file_.name
                    new_folder.mkdir()
                    for f in file_.iterdir():
                        if f.is_dir():
                            temp_dest = new_folder / f.name
                            shutil.copytree(f, temp_dest)
                        elif f.name != script_file.name:
                            shutil.copy2(f, new_folder)
                        else:
                            logger.debug(
                                "Skip file with the same name as the script found in project file."
                            )
                else:
                    if file_.is_dir():
                        temp_dest = temp_dir / file_.name
                        shutil.copytree(file_, temp_dest)
                    else:
                        assert file_.name != script_file.name, ( # avoid the inclusion of the script in project files
                            "It seems that the script file is included a second time in the project_files")
                        shutil.copy2(file_, temp_dir)

            model_identifier, xml = get_model_description(
                temp_dir.absolute() / script_file.name, module_name, model_class.__name__
            )
            dest_file = dest / f"{model_identifier}.fmu" if dest_file == "" else dest_file

            type_node = xml.find("CoSimulation")
            option_names = [opt.name for opt in FMI2_MODEL_OPTIONS]
            for option, value in options.items():
                if option in option_names:
                    type_node.set(option, str(value).lower())

            with zipfile.ZipFile(dest_file, "w") as zip_fmu:

                resource = Path("resources")

                # Add files copied in temporary directory
                for f in temp_dir.rglob("*"):
                    if f.is_file() and f.parent.name != "__pycache__":
                        relative_f = f.relative_to(temp_dir)
                        zip_fmu.write(f, arcname=(resource / relative_f))

                # Add information for the Python loader
                zip_fmu.writestr(str(resource.joinpath("slavemodule.txt")), module_name)

                # Add FMI API wrapping Python class library
                binaries = Path("binaries")
                src_binaries = HERE / "resources" / "binaries"
                for f in itertools.chain(
                    src_binaries.rglob("*.dll"),
                    src_binaries.rglob("*.so"),
                    src_binaries.rglob("*.dylib"),
                ):
                    relative_f = f.relative_to(src_binaries)
                    arcname = (
                        binaries
                        / relative_f.parent
                        / f"{model_identifier}{relative_f.suffix}"
                    )
                    zip_fmu.write(f, arcname=arcname)

                # Add the documentation folder
                if documentation_folder is not None:
                    documentation = Path("documentation")
                    for f in documentation_folder.rglob("*"):
                        if f.is_file():
                            relative_f = f.relative_to(documentation_folder)
                            zip_fmu.write(f, arcname=(documentation / relative_f))

                # Add the model description
                xml_str = parseString(tostring(xml, "UTF-8"))
                zip_fmu.writestr(
                    "modelDescription.xml", xml_str.toprettyxml(encoding="UTF-8")
                )
            if newargs is not None:
                sys.modules.pop(Path(script_file).stem)  # otherwise old script may be active when loading the FMU!

            return dest_file

    @staticmethod
    def has_binary() -> bool:
        """Does the binary for this platform exits?"""
        binary_folder = get_platform()
        lib_ext = get_lib_extension() or "*"  # if library extension is unknown, it will look for '*.*' in src_binaries
        src_binaries = HERE / "resources" / "binaries" / binary_folder
        return src_binaries.exists() and len(list(src_binaries.glob(f"*.{lib_ext}"))) >= 1


def create_command_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-f",
        "--file",
        dest="script_file",
        help="Path to the Python script.",
        required=True
    )

    parser.add_argument(
        "-d", "--dest", dest="dest", help="Where to save the FMU.", default="."
    )

    parser.add_argument(
        "--doc",
        dest="documentation_folder",
        help="Documentation folder to include in the FMU.",
        default=None
    )

    for option in FMI2_MODEL_OPTIONS:
        action = "store_false" if option.value else "store_true"
        parser.add_argument(
            f"--{option.cli}",
            dest=option.name,
            help=f"If given, {option.name}={action[6:]}",
            action=action
        )

    parser.add_argument(
        "project_files",
        metavar="Project files",
        nargs="*",
        help="Additional project files required by the Python script.",
        default=set()
    )

    parser.set_defaults(execute=FmuBuilder.build_FMU)
