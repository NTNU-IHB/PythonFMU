from abc import ABC, abstractmethod
from uuid import uuid1
from enum import Enum


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

    def string_repr(self):
        strRepr = f"<ScalarVariable valueReference=\"{self.value_reference}\" name=\"{self.name}\""
        if self.initial is not None:
            strRepr += f" initial=\"{self.initial.name}\""
        if self.causality is not None:
            strRepr += f" causality=\"{self.causality.name}\""
        if self.variability is not None:
            strRepr += f" variability=\"{self.variability.name}\""
        if self.description is not None:
            strRepr += f" description=\"{self.description}\""
        strRepr += ">\n"
        strRepr += "\t\t\t" + self.sub_string_repr() + "\n"
        return strRepr + "\t\t</ScalarVariable>"

    @abstractmethod
    def sub_string_repr(self):
        pass


class Real(ScalarVariable):

    def __init__(self, name):
        super(Real, self).__init__(name)

    def sub_string_repr(self):
        return f"<Real />"


class Integer(ScalarVariable):

    def __init__(self, name):
        super(Integer, self).__init__(name)

    def sub_string_repr(self):
        return f"<Integer />"


class Boolean(ScalarVariable):

    def __init__(self, name):
        self.value = False
        super(Boolean, self).__init__(name)

    def sub_string_repr(self):
        return f"<Boolean />"


class String(ScalarVariable):

    def __init__(self, name):
        super(String, self).__init__(name)

    def sub_string_repr(self):
        return f"<String />"


class Fmi2Slave(ABC):

    guid = uuid1()
    author = None
    license = None
    version = None
    description = None
    modelName = None

    def __init__(self):
        self.vars = []
        self.xml = None
        if Fmi2Slave.modelName is None:
            raise Exception("No modelName has been specified!")

    def define(self):
        var_str = "\n".join(list(map(lambda v: v.string_repr(), self.vars)))
        outputs = list(filter(lambda v: v.causality == Fmi2Causality.output, self.vars))
        structure_str = ""
        if len(outputs) > 0:
            structure_str += "<Outputs>\n"
            for i in range(len(outputs)):
                structure_str += f"\t\t\t<Unknown index=\"{i+1}\" />\n"
            structure_str += "\t\t</Outputs>"

        desc_str =  f" description=\"{Fmi2Slave.description}\"" if Fmi2Slave.description is not None else ""
        auth_str =  f" author=\"{Fmi2Slave.author}\"" if Fmi2Slave.author is not None else ""
        lic_str =  f" license=\"{Fmi2Slave.license}\"" if Fmi2Slave.license is not None else ""
        ver_str =  f" version=\"{Fmi2Slave.version}\"" if Fmi2Slave.version is not None else ""

        self.xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<fmiModelDescription fmiVersion="2.0" modelName="{Fmi2Slave.modelName}" guid="{Fmi2Slave.guid}"{desc_str}{auth_str}{lic_str}{ver_str} generationTool="PythonFMU" variableNamingConvention="structured">
    <CoSimulation modelIdentifier="{Fmi2Slave.modelName}" needsExecutionTool="true" canHandleVariableCommunicationStepSize="true" canInterpolateInputs="false" canBeInstantiatedOnlyOncePerProcess="true" canGetAndSetFMUstate="false" canSerializeFMUstate="false"/>
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

    def get_integer(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Integer!")

    def get_real(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Real!")

    def get_boolean(self, vrs, refs):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Boolean):
                refs[i] = getattr(self, var.name)
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Boolean!")

    def set_integer(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Integer!")

    def set_real(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Real!")

    def set_boolean(self, vrs, values):
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                setattr(self, var.name, values[i])
            else:
                raise Exception(f"Variable with valueReference={vr} is not of type Boolean!")
