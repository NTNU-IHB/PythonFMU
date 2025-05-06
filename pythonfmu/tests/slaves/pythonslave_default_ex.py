from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Fmi2Variability, Integer, DefaultExperiment


class PythonSlaveDefaultExperiment(Fmi2Slave):
    default_experiment = DefaultExperiment(start_time=1, stop_time=2, tolerance=1e-3, step_size=1e-3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dummy = 1

        self.register_variable(Integer("dummy", causality=Fmi2Causality.output, variability=Fmi2Variability.constant))

    def do_step(self, current_time, step_size):
        return True
