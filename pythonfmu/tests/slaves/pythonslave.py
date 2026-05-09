from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Fmi2Variability, Integer, Real, Boolean, String, Enumeration, TypeEnum, Item


class Container:
    pass


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
        self.realIn = 2. / 3.
        self.realIn2 = 2. / 3.
        self.booleanParameter = False
        self.stringParameter = "dog"
        self.enumParameter = 0

        self.register_type(TypeEnum("enumType", item=[Item("red", 0), Item("green", 1), Item("blue", 2)]))

        self.register_variable(
            Integer("intParam", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))
        self.register_variable(Real("realIn", causality=Fmi2Causality.input))
        self.register_variable(Real("realIn2", causality=Fmi2Causality.input, start=30.0, min_=-100.0, max_=100.0,
                                    unit="m", display_unit="ft", relative_quantity=True, nominal=10.0, unbounded=False,
                                    derivative=1, reinit=True))
        self.register_variable(
            Boolean("booleanParameter", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))
        self.register_variable(
            String("stringParameter", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))
        self.register_variable(
            Enumeration("enumParameter", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable,
                        declared_type="enumType"))

        self.register_variable(Integer("intOut", causality=Fmi2Causality.output))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable", causality=Fmi2Causality.local))
        self.register_variable(String("stringVariable", causality=Fmi2Causality.local))

        self.container = Container()
        self.container.someReal = 99.0
        self.container.subContainer = sub = Container()
        sub.someInteger = -15
        self.register_variable(
            Real("container.someReal", causality=Fmi2Causality.parameter, variability=Fmi2Variability.tunable))
        self.register_variable(
            Integer("container.subContainer.someInteger", causality=Fmi2Causality.parameter,
                    variability=Fmi2Variability.tunable))

    def do_step(self, current_time, step_size):
        self.realOut = current_time + step_size
        return True

    def enter_initialization_mode(self):
        self.intOut = self.intParam
        self.container.someReal = self.intParam
