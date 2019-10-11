
from Fmi2Slave import *


class Model(Fmi2Slave):

    Fmi2Slave.modelName = "PythonSlave"
    Fmi2Slave.author = "Lars Ivar Hatledal"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output))
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable").set_causality(Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        return True
