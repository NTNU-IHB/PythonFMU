"""Define the abstract facade class."""
import json
import datetime
from abc import ABC, abstractmethod
from collections import OrderedDict, namedtuple
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid1
from xml.etree.ElementTree import Element, SubElement
from ctypes import cdll, c_char_p, c_void_p, c_int, c_bool

from .osutil import get_lib_extension, get_platform
from ._version import __version__ as VERSION
from .enums import Fmi2Status, Fmi2Causality, Fmi2Initial, Fmi2Variability
from .variables import Boolean, Integer, Real, ScalarVariable, String

ModelOptions = namedtuple("ModelOptions", ["name", "value", "cli"])

FMI2_MODEL_OPTIONS: List[ModelOptions] = [
    ModelOptions("needsExecutionTool", True, "no-external-tool"),
    ModelOptions("canHandleVariableCommunicationStepSize", True, "no-variable-step"),
    ModelOptions("canInterpolateInputs", False, "interpolate-inputs"),
    ModelOptions("canBeInstantiatedOnlyOncePerProcess", False, "only-one-per-process"),
    ModelOptions("canGetAndSetFMUstate", False, "handle-state"),
    ModelOptions("canSerializeFMUstate", False, "serialize-state"),
    ModelOptions("canNotUseMemoryManagementFunctions", True, "use-memory-management")
]


class Fmi2Slave(ABC):
    """Abstract facade class to execute Python through FMI standard."""

    guid: ClassVar[str] = uuid1()
    author: ClassVar[Optional[str]] = None
    license: ClassVar[Optional[str]] = None
    version: ClassVar[Optional[str]] = None
    copyright: ClassVar[Optional[str]] = None
    modelName: ClassVar[Optional[str]] = None
    description: ClassVar[Optional[str]] = None

    # Dictionary of (category, description) entries
    log_categories: Dict[str, str] = {
        "logStatusWarning": "Log messages with fmi2Warning status.",
        "logStatusDiscard": "Log messages with fmi2Discard status.",
        "logStatusError": "Log messages with fmi2Error status.",
        "logStatusFatal": "Log messages with fmi2Fatal status.",
        "logAll": "Log all messages."
    }

    def __init__(self, **kwargs):
        self.vars = OrderedDict()
        self.instance_name = kwargs["instance_name"]
        self.resources = kwargs.get("resources", None)
        self.logger = kwargs.get("logger", None)
        self.visible = kwargs.get("visible", False)
        self.__lib = None
        self.__lib_error = False

        if self.__class__.modelName is None:
            self.__class__.modelName = self.__class__.__name__

    def to_xml(self, model_options: Dict[str, str] = dict()) -> Element:
        """Build the XML representation of the model.
        
        Args:
            model_options (Dict[str, str]) : FMU model options
        
        Returns:
            (xml.etree.TreeElement.Element) XML description of the FMU
        """

        t = datetime.datetime.now(datetime.timezone.utc)
        date_str = t.isoformat(timespec="seconds")

        attrib = dict(
            fmiVersion="2.0",
            modelName=self.modelName,
            guid=f"{self.guid!s}",
            generationTool=f"PythonFMU {VERSION}",
            generationDateAndTime=date_str,
            variableNamingConvention="structured"
        )
        if self.description is not None:
            attrib["description"] = self.description
        if self.author is not None:
            attrib["author"] = self.author
        if self.license is not None:
            attrib["license"] = self.license
        if self.version is not None:
            attrib["version"] = self.version
        if self.copyright is not None:
            attrib["copyright"] = self.copyright

        root = Element("fmiModelDescription", attrib)

        options = dict()
        for option in FMI2_MODEL_OPTIONS:
            value = model_options.get(option.name, option.value)
            options[option.name] = str(value).lower()
        options["modelIdentifier"] = self.modelName

        SubElement(root, "CoSimulation", attrib=options)

        if len(self.log_categories) > 0:
            categories = SubElement(root, "LogCategories")
            for category, description in self.log_categories.items():
                categories.append(
                    Element(
                        "Category",
                        attrib={"name": category, "description": description},
                    )
                )

        variables = SubElement(root, "ModelVariables")
        for v in self.vars.values():
            if ScalarVariable.requires_start(v):
                self.__apply_start_value(v)
            variables.append(v.to_xml())

        structure = SubElement(root, "ModelStructure")
        outputs = list(
            filter(lambda v: v.causality == Fmi2Causality.output, self.vars.values())
        )

        if outputs:
            outputs_node = SubElement(structure, "Outputs")
            for i, v in enumerate(self.vars.values()):
                if v.causality == Fmi2Causality.output:
                    SubElement(outputs_node, "Unknown", attrib=dict(index=str(i + 1)))

        return root

    def __apply_start_value(self, var: ScalarVariable):
        vrs = [var.value_reference]

        if isinstance(var, Integer):
            refs = self.get_integer(vrs)
        elif isinstance(var, Real):
            refs = self.get_real(vrs)
        elif isinstance(var, Boolean):
            refs = self.get_boolean(vrs)
        elif isinstance(var, String):
            refs = self.get_string(vrs)
        else:
            raise Exception(f"Unsupported type!")

        var.start = refs[0]

    def register_variable(self, var: ScalarVariable):
        variable_reference = len(self.vars)
        self.vars[variable_reference] = var
        # Set the unique value reference
        var.value_reference = variable_reference
        if (
            var.getter is None
            or var.setter is None
            and ScalarVariable.setter_required(var)
        ):
            owner = self
            if "." in var.name:
                split = var.name.split(".")
                split.pop(-1)
                for s in split:
                    owner = getattr(owner, s)
            if var.getter is None:
                var.getter = lambda: getattr(owner, var.local_name)
            if var.setter is None and ScalarVariable.setter_required(var):
                var.setter = lambda v: setattr(owner, var.local_name, v)

    def setup_experiment(self, start_time: float):
        pass

    def enter_initialization_mode(self):
        pass

    def exit_initialization_mode(self):
        pass

    @abstractmethod
    def do_step(self, current_time: float, step_size: float) -> bool:
        pass

    def terminate(self):
        pass

    def get_integer(self, vrs: List[int]) -> List[int]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, Integer):
                refs.append(int(var.getter()))
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type Integer!"
                )
        return refs

    def get_real(self, vrs: List[int]) -> List[float]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, Real):
                refs.append(float(var.getter()))
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type Real!"
                )
        return refs

    def get_boolean(self, vrs: List[int]) -> List[bool]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, Boolean):
                refs.append(bool(var.getter()))
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type Boolean!"
                )
        return refs

    def get_string(self, vrs: List[int]) -> List[str]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, String):
                refs.append(str(var.getter()))
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type String!"
                )
        return refs

    def set_integer(self, vrs: List[int], values: List[int]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, Integer):
                var.setter(value)
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type Integer!"
                )

    def set_real(self, vrs: List[int], values: List[float]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, Real):
                var.setter(value)
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type Real!"
                )

    def set_boolean(self, vrs: List[int], values: List[bool]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, Boolean):
                var.setter(value)
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type Boolean!"
                )

    def set_string(self, vrs: List[int], values: List[str]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, String):
                var.setter(value)
            else:
                raise TypeError(
                    f"Variable with valueReference={vr} is not of type String!"
                )

    def _get_fmu_state(self) -> Dict[str, Any]:
        state = dict()
        for var in self.vars.values():
            state[var.name] = var.getter()
        return state

    def _set_fmu_state(self, state: Dict[str, Any]):
        vars_by_name = dict([(v.name, v) for v in self.vars.values()])
        for name, value in state.items():
            if name not in vars_by_name:
                setattr(self, name, value)
            else:
                vars_by_name[name].setter(value)

    @staticmethod
    def _fmu_state_to_bytes(state: Dict[str, Any]) -> bytes:
        return json.dumps(state).encode("utf-8")

    @staticmethod
    def _fmu_state_from_bytes(state: bytes) -> Dict[str, Any]:
        return json.loads(state.decode("utf-8"))

    def log(
        self,
        msg: str,
        status: Fmi2Status = Fmi2Status.ok,
        category: Optional[str] = None,
        debug: bool = False
    ):
        """Log a message to the FMU logger.
        
        Args:
            msg (str) : Log message
            status (Fmi2Status) : Optional, message status (default ok)
            category (str or None) : Optional, message category (default derived from status)
            debug (bool) : Optional, is this a debug message (default False)
        """
        if self.logger is not None and self.resources is not None:
            if self.__lib is None and not self.__lib_error:
                library_path = (
                    Path(self.resources).parent
                    / "binaries"
                    / get_platform()
                    / (self.modelName + "." + get_lib_extension())
                )
                try:
                    self.__lib = cdll.LoadLibrary(str(library_path))
                except:
                    self.__lib_error = True
                    print(
                        f"Warning. Unable to setup logging for FMU instance: {self.instance_name}"
                    )
            if not self.__lib_error:
                if category is None:
                    category = f"logStatus{status.name.capitalize()}"
                    if category not in self.log_categories:
                        category = "logAll"

                self.__lib.pylog(
                    c_void_p(self.logger),
                    c_int(int(status)),
                    c_char_p(category.encode("utf-8")),
                    c_char_p(msg.encode("utf-8")),
                    c_bool(debug)
                )

