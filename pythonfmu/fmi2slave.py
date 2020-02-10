import datetime
from abc import ABC, abstractmethod
from collections import namedtuple
from io import BytesIO
from typing import ClassVar, Dict, List, Optional
from uuid import uuid1
from xml.etree.ElementTree import Element, SubElement

from .enums import Fmi2Causality, Fmi2Initial, Fmi2Variability
from .variables import Boolean, Integer, Real, ScalarVariable, String

ModelOptions = namedtuple('ModelOptions', ['name', 'value', 'cli'])

FMI2_MODEL_OPTIONS = [
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

    def __init__(self):
        self.vars = dict()
        if self.modelName is None:
            raise Exception("No modelName has been specified!")

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
            if self.__requires_start__(v):
                self.__set_start__(v)
            variables.append(v.to_xml())

        structure = SubElement(root, 'ModelStructure')
        outputs = list(filter(lambda v: v.causality == Fmi2Causality.output, self.vars.values()))
        
        if outputs:
            outputs_node = SubElement(structure, 'Outputs')
            for i in range(len(outputs)):
                SubElement(outputs_node, 'Unknown', attrib=dict(index=str(i+1)))

        return root

    @staticmethod
    def __requires_start__(v: ScalarVariable) -> bool:
        return v.initial == Fmi2Initial.exact or \
               v.initial == Fmi2Initial.approx or \
               v.causality == Fmi2Causality.input or \
               v.causality == Fmi2Causality.parameter or \
               v.variability == Fmi2Variability.constant

    def __set_start__(self, var: ScalarVariable):
        refs = [None]
        vrs = [var.value_reference]

        if isinstance(var, Integer):
            self.__get_integer__(vrs, refs)
        elif isinstance(var, Real):
            self.__get_real__(vrs, refs)
        elif isinstance(var, Boolean):
            vrs.append(var.value_reference)
            self.__get_boolean__(vrs, refs)
        elif isinstance(var, String):
            vrs.append(var.value_reference)
            self.__get_string__(vrs, refs)
        else:
            raise Exception(f"Unsupported type!")

        var.__set_start__(refs[0])

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

    def __get_integer__(self, vrs: List[int], refs: List[int]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Integer!")

    def __get_real__(self, vrs: List[int], refs: List[float]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Real!")

    def __get_boolean__(self, vrs: List[int], refs: List[bool]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Boolean):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Boolean!")

    def __get_string__(self, vrs: List[int], refs: List[str]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, String):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type String!")

    def __set_integer__(self, vrs: List[int], values: List[int]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Integer!")

    def __set_real__(self, vrs: List[int], values: List[float]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Real!")

    def __set_boolean__(self, vrs: List[int], values: List[bool]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Boolean):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Boolean!")

    def __set_string__(self, vrs: List[int], values: List[str]):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, String):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type String!")
