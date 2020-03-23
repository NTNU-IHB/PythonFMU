import argparse
import tempfile
from pathlib import Path
from typing import Union, Optional
from ._version import __version__
from .fmi2slave import FMI2_MODEL_OPTIONS
from .builder import FmuBuilder

FilePath = Union[str, Path]


def create_csv_slave(csvfile: FilePath):
    classname = csvfile.stem
    filename = csvfile.name
    return f"""
from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Fmi2Variability, Real
import csv

EPS = 1e-6

def lerp(v0: float, v1: float, t: float) -> float:
    return (1 - t) * v0 + t * v1


def normalize(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


class {classname}(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.current_index = 0
        self.next_index = None
        self.current_time = 0.0
        data = dict()

        def read_csv():
            with open(self.resources + '/' + "{filename}") as f:
                return list(csv.reader(f, delimiter=','))

        rows = read_csv()
        headers = list(map(lambda h: h.strip(), rows[0]))
        self.times = []

        for i in range(1, len(headers)):
            header = headers[i]
            data[header] = []

            def get_value(header):
                current_value = data[header][self.current_index]
                if self.next_index is None:
                    return current_value
                next_value = data[header][self.next_index]

                current_value_t = self.times[self.current_index]
                next_value_t = self.times[self.next_index]

                t = normalize(self.current_time, current_value_t, next_value_t, 0, 1)
                return lerp(current_value, next_value, t)

            self.register_variable(
                Real(header,
                     causality=Fmi2Causality.output,
                     variability=Fmi2Variability.constant,
                     getter=lambda header=header: get_value(header)))

        for i in range(1, len(rows)):
            values = list(map(lambda x: float(x), rows[i]))
            self.times.append(values[0])
            for j in range(1, len(values)):
                data[headers[j]].append(values[j])

        self.register_variable(Real("end_time",
                                    causality=Fmi2Causality.output,
                                    variability=Fmi2Variability.constant,
                                    getter=lambda: self.times[-1]))

    def find_indices(self, t, dt):
        current_t = self.times[self.current_index]
        while current_t < t:
            self.current_index += 1
            current_t = self.times[self.current_index]
        if dt == 0:
            return
        self.next_index = self.current_index +1
        next_t = self.times[self.next_index]
        while next_t < (t + dt):
            if abs(next_t - (t + dt)) <= EPS:
                return 
            self.next_index += 1
            next_t = self.times[self.next_index]

    def setup_experiment(self, start_time: float):
        self.current_time = start_time
        self.find_indices(start_time, 0)

    def do_step(self, current_time: float, step_size: float) -> bool:
        self.current_time = current_time + step_size
        self.find_indices(current_time, step_size)
        return True
    """


class CsvFmuBuilder:

    @staticmethod
    def build_FMU(
        csv_file: FilePath,
        dest: FilePath = ".",
        **options,
    ) -> Path:

        if not csv_file.exists():
            raise ValueError(f"No such file {csv_file!s}")
        if not csv_file.suffix.endswith(".csv"):
            raise ValueError(f"File {csv_file!s} must have extension '.csv'!")

        options["dest"] = dest
        options["project_files"] = {csv_file}

        with tempfile.TemporaryDirectory(prefix="pythonfmu_") as tempd:
            temp_dir = Path(tempd)
            script_file = temp_dir / (csv_file.stem + ".py")
            with open(script_file, "+w") as f:
                f.write(create_csv_slave(csv_file))
            options["script_file"] = script_file
            return FmuBuilder.build_FMU(**options)


def main():
    parser = argparse.ArgumentParser(
        prog="pythonfmu-csvbuilder", description="Build an FMU from a Python script or CSV file."
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__
    )

    parser.add_argument(
        "-f",
        "--file",
        dest="script_file",
        help="Path to the CSV file.",
        required=True,
    )

    parser.add_argument(
        "-d", "--dest", dest="dest", help="Where to save the FMU.", default="."
    )

    parser.add_argument(
        "--doc",
        dest="documentation_folder",
        help="Documentation folder to include in the FMU.",
        default=None,
    )

    for option in FMI2_MODEL_OPTIONS:
        action = "store_false" if option.value else "store_true"
        parser.add_argument(
            f"--{option.cli}",
            dest=option.name,
            help=f"If given, {option.name}={action[6:]}",
            action=action
        )

    options = vars(parser.parse_args())
    CsvFmuBuilder.build_FMU(**options)
