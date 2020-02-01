from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Integer, Real, Boolean, String

slave_class = "PythonSlave"  # REQUIRED - Name of the class extending Fmi2Slave


class PythonSlave(Fmi2Slave):

    author = "John Doe"
    modelName = "PythonSlave"  # REQUIRED
    description = "A simple description"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.stringVariable = "Hello World!"
        self.register_variable(Integer("intOut", causality=Fmi2Causality.output))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable", causality=Fmi2Causality.local))
        self.register_variable(String("stringVariable", causality=Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        self.realOut = current_time + step_size
        return True
