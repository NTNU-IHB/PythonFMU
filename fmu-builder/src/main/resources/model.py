
from Fmi2Slave import *

class Model(Fmi2Slave):

    def __init__(self):
        super(Model, self).__init__("PythonSlave")

        self.author = "Lars Ivar Hatledal"
        self.realOut = 3.0
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))

    def doStep(self, currentTime: float, stepSize: float):
        print(f"doStep, currentTime={currentTime}, stepSize={stepSize}")
