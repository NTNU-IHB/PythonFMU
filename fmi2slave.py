from abc import ABC, abstractmethod
from uuid import uuid1
from enum import Enum
import datetime


class Fmi2Causality(Enum):
    parameter = 0,
    calculatedParameter = 1,
    input = 2,
    output = 3,
    local = 4


class Fmi2Variability(Enum):
    constant = 0,
    fixed = 1,
    tunable = 2,
    discrete = 3,
    continuous = 4


class Fmi2Initial(Enum):
    exact = 0,
    approx = 1,
    calculated = 2


class ScalarVariable(ABC):

    vr_counter = 0

    def __init__(self, name):
        self.name = name
        self.initial = None
        self.causality = None
        self.variability = None
        self.description = None
        self.value_reference = ScalarVariable.vr_counter
        ScalarVariable.vr_counter += 1

    def set_description(self, description: str):
        self.description = description
        return self

    def set_initial(self, initial: Fmi2Initial):
        self.initial = initial
        return self

    def set_causality(self, causality: Fmi2Causality):
        self.causality = causality
        return self

    def set_variability(self, variability: Fmi2Variability):
        self.variability = variability
        return self

    def __xml_repr__(self):
        xml_repr = f"\t\t<ScalarVariable valueReference=\"{self.value_reference}\" name=\"{self.name}\""
        if self.initial is not None:
            xml_repr += f" initial=\"{self.initial.name}\""
        if self.causality is not None:
            xml_repr += f" causality=\"{self.causality.name}\""
        if self.variability is not None:
            xml_repr += f" variability=\"{self.variability.name}\""
        if self.description is not None:
            xml_repr += f" description=\"{self.description}\""
        xml_repr += ">\n"
        xml_repr += "\t\t\t" + self.__sub_xml_repr__() + "\n"
        return xml_repr + "\t\t</ScalarVariable>"

    @abstractmethod
    def __sub_xml_repr__(self):
        pass


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
        if Fmi2Slave.modelName is None:
            raise Exception("No modelName has been specified!")

    def __define__(self):
        var_str = "\n".join(list(map(lambda v: v.__xml_repr__(), self.vars)))
        outputs = list(filter(lambda v: v.causality == Fmi2Causality.output, self.vars))
        structure_str = ""
        if len(outputs) > 0:
            structure_str += "\t\t<Outputs>\n"
            for i in range(len(outputs)):
                structure_str += f"\t\t\t<Unknown index=\"{i+1}\" />\n"
            structure_str += "\t\t</Outputs>"

        desc_str = f" description=\"{Fmi2Slave.description}\"" if Fmi2Slave.description is not None else ""
        auth_str = f" author=\"{Fmi2Slave.author}\"" if Fmi2Slave.author is not None else ""
        lic_str = f" license=\"{Fmi2Slave.license}\"" if Fmi2Slave.license is not None else ""
        ver_str = f" version=\"{Fmi2Slave.version}\"" if Fmi2Slave.version is not None else ""
        cop_str = f" copyright=\"{Fmi2Slave.copyright}\"" if Fmi2Slave.copyright is not None else ""

        t = datetime.datetime.now()
        date_str = f"{t.year}-{t.month}-{t.day}T{t.hour}:{t.day}:{t.second}Z"

        return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<fmiModelDescription fmiVersion="2.0" modelName="{Fmi2Slave.modelName}" guid="{Fmi2Slave.guid}"{desc_str}{auth_str}{lic_str}{ver_str}{cop_str} generationTool="PythonFMU" generationDateAndTime="{date_str}" variableNamingConvention="structured">
    <CoSimulation modelIdentifier="{Fmi2Slave.modelName}" needsExecutionTool="true" canHandleVariableCommunicationStepSize="true" canInterpolateInputs="false" canBeInstantiatedOnlyOncePerProcess="false" canGetAndSetFMUstate="false" canSerializeFMUstate="false" canNotUseMemoryManagementFunctions="true"/>
    <ModelVariables>
{var_str}
    </ModelVariables>
    <ModelStructure>
{structure_str}
    </ModelStructure>
</fmiModelDescription>
"""

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


class Real(ScalarVariable):

    def __init__(self, name):
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<Real />"


class Integer(ScalarVariable):

    def __init__(self, name):
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<Integer />"


class Boolean(ScalarVariable):

    def __init__(self, name):
        self.value = False
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<Boolean />"


class String(ScalarVariable):

    def __init__(self, name):
        super().__init__(name)

    def __sub_xml_repr__(self):
        return f"<String />"
