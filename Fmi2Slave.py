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


class ScalarVariable(ABC):

    vr_counter = 0

    def __init__(self, name):
        self.name = name
        self.causality = None
        self.variability = None
        self.value_reference = ScalarVariable.vr_counter
        ScalarVariable.vr_counter += 1

    def set_causality(self, causality: Fmi2Causality):
        self.causality = causality
        return self

    def set_variability(self, variability: Fmi2Variability):
        self.variability = variability
        return self

    def string_repr(self):
        strRepr = f"<ScalarVariable valueReference={self.value_reference} name={self.name}"
        if self.causality is not None:
            strRepr += f" causality={self.causality}"
        if self.variability is not None:
            strRepr += f" variability={self.variability}"
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

    def __init__(self, modelName):
        self.author = ""
        self.license = ""
        self.modelName = modelName
        self.vars = []
        self.xml = None

    def initialize(self):
        print("initialize")

        varStr = ""
        for var in self.vars:
            varStr += var.string_repr() + "\n"

        self.xml = f"""
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <fmiModelDescription fmiVersion="2.0" modelName={self.modelName} guid="{uuid1()}" author="{self.author}" license="{self.license}" generationTool="PythonFMU" variableNamingConvention="structured">
            <CoSimulation modelIdentifier="{self.modelName}" needsExecutionTool="false" canHandleVariableCommunicationStepSize="true" canInterpolateInputs="false" canBeInstantiatedOnlyOncePerProcess="false" canGetAndSetFMUstate="false" canSerializeFMUstate="false"/>
            <ModelVariables>
                {varStr}
            </ModelVariables>
            <ModelStructure>
            </ModelStructure>
        </fmiModelDescription>
        """
        print(self.xml)
        print(f"value={getattr(self, self.vars[0].name)}")

    def register_variable(self, var):
        self.vars.append(var)

    def setupExperiment(self, startTime: float):
        print(f"setupExperiment, startTime={startTime}")

    def enterInitializationMode(self):
        print("enterInitializationMode")

    def exitInitializationMode(self):
        print("exitInitializationMode")

    @abstractmethod
    def doStep(self, currentTime: float, stepSize: float):
        pass

    def terminate(self):
        print("terminate")

    def getInteger(self, vrs, refs):
        print("getInteger")
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Integer):
                refs[i] = getattr(self, var.name)
            else:
                print(f"Variable with valueReference {vr} is not of type Integer!")

    def getReal(self, vrs, refs):
        print("getReal")
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                refs[i] = getattr(self, var.name)
            else:
                print(f"Variable with valueReference {vr} is not of type Real!")

    def setReal(self, vrs, values):
        print("setReal")
        for i in range(len(vrs)):
            vr = vrs[i]
            var = self.vars[vr]
            if isinstance(var, Real):
                setattr(self, var.name, values[i])
            else:
                print(f"Variable with valueReference {vr} is not of type Real!")
