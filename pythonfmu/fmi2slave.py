from abc import ABC, abstractmethod
from io import BytesIO
from collections import namedtuple
from uuid import uuid1
import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

from .enums import Fmi2Causality
from .variables import Boolean, Integer, Real, String

ModelOptions = namedtuple('ModelOptions', ['name', 'value', 'cli'])

FMI2_MODEL_OPTIONS = [
    ModelOptions("needsExecutionTool", False, "external-tool"),
    ModelOptions("canHandleVariableCommunicationStepSize", True, "no-variable-step"),
    ModelOptions("canInterpolateInputs", False, "interpolate-inputs"),
    ModelOptions("canBeInstantiatedOnlyOncePerProcess", False, "only-one-per-process"),
    ModelOptions("canGetAndSetFMUstate", False, "handle-state"),
    ModelOptions("canSerializeFMUstate", False, "serialize-state"),
    ModelOptions("canNotUseMemoryManagementFunctions", True, "use-memory-management"),
]


class Fmi2Slave(ABC):

    guid = uuid1()
    author = None
    license = None
    version = None
    copyright = None
    modelName = None
    description = None

    def __init__(self):
        self.vars = []
        if self.modelName is None:
            raise Exception("No modelName has been specified!")

    def to_xml(self, model_options = dict()):

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
        for v in self.vars:
            variables.append(v.to_xml())

        structure = SubElement(root, 'ModelStructure')
        outputs = list(filter(lambda v: v.causality == Fmi2Causality.output, self.vars))
        
        if outputs:
            outputs_node = SubElement(structure, 'Outputs')
            for i in range(len(outputs)):
                SubElement(outputs_node, 'Unknown', attrib=dict(index=str(i+1)))

        xml_str = parseString(tostring(root, "UTF-8"))
        return xml_str.toprettyxml(encoding='UTF-8')

    def register_variable(self, var):
        self.vars.append(var)

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

    def __get_integer__(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Integer!")

    def __get_real__(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Real!")

    def __get_boolean__(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Boolean):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Boolean!")

    def __get_string__(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, String):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type String!")

    def __set_integer__(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Integer!")

    def __set_real__(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Real!")

    def __set_boolean__(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Boolean):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Boolean!")

    def __set_string__(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, String):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type String!")
