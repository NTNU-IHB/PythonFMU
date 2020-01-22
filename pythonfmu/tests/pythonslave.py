from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Integer, Real, Boolean, String

from random import random as randn

slave_class = "PythonSlave"  # REQUIRED - Name of the class extending Fmi2Slave


class PythonSlave(Fmi2Slave):

    Fmi2Slave.author = "John Doe"
    Fmi2Slave.modelName = "PythonSlave"  # REQUIRED
    Fmi2Slave.description = "A simple description"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.stringVariable = "Hello World!"
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output))
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable").set_causality(Fmi2Causality.local))
        self.register_variable(String("stringVariable").set_causality(Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        self.realOut = randn()
        return True
