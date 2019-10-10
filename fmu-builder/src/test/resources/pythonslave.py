
from Fmi2Slave import *


class Model(Fmi2Slave):

    Fmi2Slave.modelName = "PythonSlave"
    Fmi2Slave.author = "Lars Ivar Hatledal"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output))
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))

    def doStep(self, currentTime: float, stepSize: float):
        print(f"doStep, currentTime={currentTime}, stepSize={stepSize}")
