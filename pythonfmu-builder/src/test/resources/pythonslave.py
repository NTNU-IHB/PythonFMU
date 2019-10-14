
from fmi2slave import *


class PythonSlave(Fmi2Slave):

    Fmi2Slave.modelName = "PythonSlave"
    Fmi2Slave.author = "Lars Ivar Hatledal"
    Fmi2Slave.description = "A simple description"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output).set_description("An integer variable"))
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output).set_description("A real variable"))
        self.register_variable(Boolean("booleanVariable").set_causality(Fmi2Causality.local).set_description("A boolean variable"))

    def do_step(self, current_time, step_size):
        return True
