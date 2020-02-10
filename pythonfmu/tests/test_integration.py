import math
import tempfile
from pathlib import Path

import pytest

from pythonfmu.builder import FmuBuilder

pyfmi = pytest.importorskip(
    "pyfmi", reason="pyfmi is required for testing the produced FMU"
)


DEMO = "pythonslave.py"


@pytest.mark.integration
def test_integration_demo(tmp_path):

    script_file = Path(__file__).parent / DEMO

    FmuBuilder.build_FMU(script_file, dest=tmp_path, needsExecutionTool="false")

    fmu = tmp_path / "PythonSlave.fmu"
    assert fmu.exists()
    model = pyfmi.load_fmu(str(fmu))
    res = model.simulate(final_time=0.5)

    assert res["realOut"][-1] == pytest.approx(res["time"][-1], rel=1e-7)


# TODO fmpy generate a Segmentation fault at line PyObject* sys_module = PyImport_ImportModule("sys"); in PyObjectWrapper
# @pytest.mark.integration
# def test_simple_integration_fmpy(tmp_path):
#     fmpy = pytest.importorskip(
#         "fmpy", reason="fmpy is not available for testing the produced FMU"
#     )

#     script_file = Path(__file__).parent / DEMO

#     FmuBuilder.build_FMU(script_file, dest=tmp_path)

#     fmu = tmp_path / "PythonSlave.fmu"
#     assert fmu.exists()
#     res = fmpy.simulate_fmu(str(fmu), stop_time=2.0)

#     assert res["realOut"][-1] == pytest.approx(res["time"][-1], rel=1e-7)


@pytest.mark.integration
def test_integration_has_local_dep(tmp_path):
    slave_code = """import math
from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Integer, Real, Boolean, String
from localmodule import get_amplitude, get_time_constant

slave_class = "PythonSlaveWithDep"


class PythonSlaveWithDep(Fmi2Slave):

    modelName = "PythonSlaveWithDep"

    def __init__(self):
        super().__init__()

        self.realIn = 22.0
        self.realOut = 0.0
        self.register_variable(Real("realIn", start=22., causality=Fmi2Causality.input))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))

    def do_step(self, current_time, step_size):
        self.realOut = self.realIn * get_amplitude() * math.exp((current_time + step_size) / get_time_constant())
        return True
"""

    local_module = """def get_amplitude():
    return 5.

def get_time_constant():
    return 0.1
"""

    script_file = tmp_path / "orig" / "slavewithdep.py"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    script_file.write_text(slave_code)

    local_file = script_file.parent / "localmodule.py"
    local_file.write_text(local_module)

    FmuBuilder.build_FMU(
        script_file,
        dest=tmp_path,
        project_files=[local_file],
        needsExecutionTool="false",
    )

    fmu = tmp_path / "PythonSlaveWithDep.fmu"
    assert fmu.exists()
    model = pyfmi.load_fmu(str(fmu))
    res = model.simulate(final_time=0.5)

    assert res["realOut"][-1] == pytest.approx(
        22.0 * 5.0 * math.exp(res["time"][-1] / 0.1), rel=1e-7
    )
