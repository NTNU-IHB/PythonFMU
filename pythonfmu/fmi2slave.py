import datetime
from abc import ABC, abstractmethod
from collections import namedtuple, OrderedDict
from typing import Any, ClassVar, Dict, List, Optional
from uuid import uuid1
from xml.etree.ElementTree import Element, SubElement

from .enums import Fmi2Causality, Fmi2Initial, Fmi2Variability
from .variables import Boolean, Integer, Real, ScalarVariable, String

ModelOptions = namedtuple('ModelOptions', ['name', 'value', 'cli'])

FMI2_MODEL_OPTIONS: List[ModelOptions] = [
    ModelOptions("needsExecutionTool", True, "no-external-tool"),
    ModelOptions("canHandleVariableCommunicationStepSize", True, "no-variable-step"),
    ModelOptions("canInterpolateInputs", False, "interpolate-inputs"),
    ModelOptions("canBeInstantiatedOnlyOncePerProcess", False, "only-one-per-process"),
    ModelOptions("canGetAndSetFMUstate", False, "handle-state"),
    ModelOptions("canSerializeFMUstate", False, "serialize-state"),
    ModelOptions("canNotUseMemoryManagementFunctions", True, "use-memory-management"),
]


class Fmi2Slave(ABC):

    guid: ClassVar[str] = uuid1()
    author: ClassVar[Optional[str]] = None
    license: ClassVar[Optional[str]] = None
    version: ClassVar[Optional[str]] = None
    copyright: ClassVar[Optional[str]] = None
    modelName: ClassVar[Optional[str]] = None
    description: ClassVar[Optional[str]] = None

    def __init__(self, instance_name: str):
        self.vars = OrderedDict()
        self.instance_name = instance_name
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
        date_str = t.isoformat(timespec='seconds')

        attrib=dict(
            fmiVersion="2.0",
            modelName=self.modelName,
            guid=f"{self.guid!s}",
            generationTool="PythonFMU",
            generationDateAndTime=date_str,
            variableNamingConvention="structured"
        )
        if self.description is not None:
            attrib['description'] = self.description
        if self.author is not None:
            attrib['author'] = self.author
        if self.license is not None:
            attrib['license'] = self.license
        if self.version is not None:
            attrib['version'] = self.version
        if self.copyright is not None:
            attrib['copyright'] = self.copyright

        root = Element('fmiModelDescription', attrib)

        options = dict()
        for option in FMI2_MODEL_OPTIONS:
            value = model_options.get(option.name, option.value)
            v = "true" if value else "false"
            options[option.name] = v
        options["modelIdentifier"]=self.modelName

        SubElement(root, 'CoSimulation', attrib=options)

        variables = SubElement(root, 'ModelVariables')
        for v in self.vars.values():
            if ScalarVariable.requires_start(v):
                self.__apply_start_value(v)
            variables.append(v.to_xml())

        structure = SubElement(root, 'ModelStructure')
        outputs = list(filter(lambda v: v.causality == Fmi2Causality.output, self.vars.values()))
        
        if outputs:
            outputs_node = SubElement(structure, 'Outputs')
            for i, v in enumerate(self.vars.values()):
                if v.causality == Fmi2Causality.output:
                    SubElement(outputs_node, 'Unknown', attrib=dict(index=str(i+1)))

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

    def setup_experiment(self, start_time: float):
        pass

    def enter_initialization_mode(self):
        pass

    def exit_initialization_mode(self):
        pass

    @abstractmethod
    def do_step(self, current_time: float, step_size: float) -> bool:
        pass

    def reset(self):
        pass

    def terminate(self):
        pass

    def get_value(self, name: str) -> Any:
        """Generic variable getter.
        
        Args:
            name (str): Name of the variable

        Returns:
            (Any) Value of the variable
        """
        return getattr(self, name)

    def set_value(self, name: str, value: Any):
        """Generic variable setter.
        
        Args:
            name (str): Name of the variable
            value (Any): Value of the variable
        """
        setattr(self, name, value)

    def get_integer(self, vrs: List[int]) -> List[int]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, Integer):
                refs.append(int(self.get_value(var.name)))
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type Integer!")
        return refs

    def get_real(self, vrs: List[int]) -> List[float]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, Real):
                refs.append(float(self.get_value(var.name)))
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type Real!")
        return refs

    def get_boolean(self, vrs: List[int]) -> List[bool]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, Boolean):
                refs.append(bool(self.get_value(var.name)))
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type Boolean!")
        return refs

    def get_string(self, vrs: List[int]) -> List[str]:
        refs = list()
        for vr in vrs:
            var = self.vars[vr]
            if isinstance(var, String):
                refs.append(str(self.get_value(var.name)))
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type String!")
        return refs

    def set_integer(self, vrs: List[int], values: List[int]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, Integer):
                self.set_value(var.name, value)
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type Integer!")

    def set_real(self, vrs: List[int], values: List[float]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, Real):
                self.set_value(var.name, value)
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type Real!")

    def set_boolean(self, vrs: List[int], values: List[bool]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, Boolean):
                self.set_value(var.name, value)
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type Boolean!")

    def set_string(self, vrs: List[int], values: List[str]):
        for vr, value in zip(vrs, values):
            var = self.vars[vr]
            if isinstance(var, String):
                self.set_value(var.name, value)
            else:
                raise TypeError(f"Variable with valueReference={vr} is not of type String!")
