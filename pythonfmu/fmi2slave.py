"""Define the abstract facade class."""
import json
import datetime
from abc import ABC, abstractmethod
from collections import OrderedDict, namedtuple
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid1
from xml.etree.ElementTree import Element, SubElement

from .logmsg import LogMsg
from .default_experiment import DefaultExperiment
from ._version import __version__ as VERSION
from .enums import Fmi2Type, Fmi2Status, Fmi2Causality, Fmi2Initial, Fmi2Variability
from .variables import Boolean, Integer, Real, ScalarVariable, String

ModelOptions = namedtuple("ModelOptions", ["name", "value", "cli"])

FMI2_MODEL_OPTIONS: List[ModelOptions] = [
    ModelOptions("needsExecutionTool", True, "no-external-tool"),
    ModelOptions("canHandleVariableCommunicationStepSize", True, "no-variable-step"),
    ModelOptions("canInterpolateInputs", False, "interpolate-inputs"),
    ModelOptions("canBeInstantiatedOnlyOncePerProcess", False, "only-one-per-process"),
    ModelOptions("canGetAndSetFMUstate", False, "handle-state"),
    ModelOptions("canSerializeFMUstate", False, "serialize-state")
]


class Fmi2Slave(ABC):
    """Abstract facade class to execute Python through FMI standard."""

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
        self.visible = kwargs.get("visible", False)
        self.log_queue = []

        self.guid = uuid1()
        self.author: Optional[str] = None
        self.license: Optional[str] = None
        self.version: Optional[str] = None
        self.copyright: Optional[str] = None
        self.modelName: Optional[str] = self.__class__.__name__
        self.description: Optional[str] = None
        self.default_experiment: Optional[DefaultExperiment] = None

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
        # use getattr to allow either class or instance attributes to be used
        for attr in ["description", "author", "license", "version", "copyright"]:
            value = getattr(self.__class__, attr, getattr(self, attr, None))
            if value is not None:
                attrib[attr] = value

        root = Element("fmiModelDescription", attrib)

        options = dict()
        for option in FMI2_MODEL_OPTIONS:
            value = model_options.get(option.name, option.value)
            options[option.name] = str(value).lower()
        options["modelIdentifier"] = self.modelName
        options["canNotUseMemoryManagementFunctions"] = "true"

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

        def_ex = getattr(self.__class__, "default_experiment", getattr(self, "default_experiment", None))
        if def_ex is not None:
            attrib = dict()
            if def_ex.start_time is not None:
                attrib["startTime"] = str(def_ex.start_time)
            if def_ex.stop_time is not None:
                attrib["stopTime"] = str(def_ex.stop_time)
            if def_ex.step_size is not None:
                attrib["stepSize"] = str(def_ex.step_size)
            if def_ex.tolerance is not None:
                attrib["tolerance"] = str(def_ex.tolerance)
            SubElement(root, "DefaultExperiment", attrib)

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

    def register_variable(self, var: ScalarVariable, nested: bool = True):
        """Register a variable as FMU interface.
        
        Args:
            var (ScalarVariable): The variable to be registered
            nested (bool): Optional, does the "." in the variable name reflect an object hierarchy to access it? Default True
        """
        variable_reference = len(self.vars)
        self.vars[variable_reference] = var
        # Set the unique value reference
        var.value_reference = variable_reference
        owner = self
        if var.getter is None and nested and "." in var.name:
            split = var.name.split(".")
            split.pop(-1)
            for s in split:
                owner = getattr(owner, s)
        if var.getter is None:
            var.getter = lambda: getattr(owner, var.local_name)
        if var.setter is None and hasattr(owner, var.local_name) and var.variability != Fmi2Variability.constant:
            var.setter = lambda v: setattr(owner, var.local_name, v)

    def setup_experiment(self, start_time: float, stop_time: Optional[float], tolerance: Optional[float]):
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
                v = vars_by_name[name]
                if v.setter is not None:
                    v.setter(value)

    @staticmethod
    def _fmu_state_to_bytes(state: Dict[str, Any]) -> bytes:
        return json.dumps(state).encode("utf-8")

    @staticmethod
    def _fmu_state_from_bytes(state: bytes) -> Dict[str, Any]:
        return json.loads(state.decode("utf-8"))

    def _get_log_queue(self):
        return self.log_queue

    def log(
            self,
            msg: str,
            status: Fmi2Status = Fmi2Status.ok,
            category: Optional[str] = None,
            debug=None
    ):
        """Log a message to the FMU logger.
        
        Args:
            msg (str) : Log message
            status (Fmi2Status) : Optional, message status (default ok)
            category (str or None) : Optional, message category (default derived from status)
            debug (bool) : Deprecated (has no effect)
        """
        if debug is not None:
            print(f"WARNING: 'debug' argument is deprecated and has no effect.")

        if category is None:
            category = f"logStatus{status.name.capitalize()}"
            if category not in self.log_categories:
                category = "logAll"
        log_msg = LogMsg(status, category, msg)
        self.log_queue.append(log_msg)
