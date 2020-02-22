from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Fmi2Variability, Integer, Real, Boolean, String


class PythonSlave(Fmi2Slave):

    author = "John Doe"
    description = "A simple description"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.intParam = 42
        self.intOut = 23
        self.realOut = 3.0
        self.booleanVariable = True
        self.stringVariable = "Hello World!"
        self.realIn = 2./3.
        self.booleanParameter = False
        self.stringParameter = "dog"
        self.register_variable(
            Integer("intParam", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))
        self.register_variable(Real("realIn", causality=Fmi2Causality.input))
        self.register_variable(Boolean("booleanParameter", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))
        self.register_variable(String("stringParameter", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))

        self.register_variable(Integer("intOut", causality=Fmi2Causality.output))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable", causality=Fmi2Causality.local))
        self.register_variable(String("stringVariable", causality=Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        self.realOut = current_time + step_size
        return True
