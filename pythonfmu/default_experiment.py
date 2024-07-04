class DefaultExperiment:

    def __init__(self, start_time: float = None, stop_time: float = None, step_size: float = None, tolerance: float = None):
        '''Define the default experiment in terms of `start_time`, `stop_time`, `step_size` and `tolerance`.
        All parameters are float type parameters and are optional'''
        self.start_time = start_time
        self.stop_time = stop_time
        self.step_size = step_size
        self.tolerance = tolerance
