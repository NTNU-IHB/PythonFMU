from pathlib import Path


def create(filename):
    path = Path(filename)
    classname = path.stem
    return f"""
    from .fmi2slave import Fmi2Slave, Fmi2Causality, Fmi2Variability, Real
import csv


def lerp(v0: float, v1: float, t: float) -> float:
    return (1 - t) * v0 + t * v1


def map(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class {classname}(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_index = 0
        self.next_index = None
        self.current_time = 0.0
        values = dict()

        def read_csv():
            csvpath = self.resources + '/' + {path.name}
            with open(csvpath) as csvfile:
                return csv.reader(csvfile, delimiter=',')

        rows = read_csv().split('\n')
        headers = rows[0].strip().split(',')
        self.times = []

        for i in range(1, len(headers)):
            header = headers[i]
            values[headers[i]] = []

            def getter():
                current_value = values[header][self.current_index]
                next_value = values[header][self.next_index]

                current_value_t = self.times[self.current_index]
                next_value_t = self.times[self.next_index]
                t = map(self.current_time, current_value_t, next_value_t, 0, 1)

                return lerp(current_value, next_value, t)

            self.register_variable(
                Real(header,
                     causality=Fmi2Causality.output,
                     variability=Fmi2Variability.constant,
                     getter=getter()))

        for i in range(1, len(rows)):
            values = rows[i].strip().split(',')
            self.times.append(values[0])
            for j in range(1, len(values)):
                values[headers[j]].append(values[j])

        self.register_variable(Real("end_time",
                                    causality=Fmi2Causality.output,
                                    variability=Fmi2Variability.constant,
                                    getter=lambda: self.times[-1]))

    def find_indices(self, t, dt):
        current_t = self.times[self.current_index]
        while current_t <= t:
            self.current_index += 1
            current_t = self.times[self.current_index]

        self.next_index = self.current_index +1
        next_t = self.times[self.next_index]
        while next_t <= t + dt:
            self.next_index += 1
            next_t = self.times[self.next_index]

    def setup_experiment(self, start_time: float):
        self.current_time = start_time
        self.find_indices(start_time, 0)

    def do_step(self, current_time: float, step_size: float) -> bool:
        self.current_time = current_time
        self.find_indices(current_time, step_size)
        return True
    """
