import pytest

from pythonfmu import FmuBuilder


@pytest.mark.integration
def test_py_extension(tmp_path):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    slave_code = """from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Causality, Integer, Real, Boolean, String

class PythonSlaveUsingExt(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.realIn = 22.0
        self.realOut = 0.0
        self.register_variable(Real("realIn", causality=Fmi2Causality.input))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))

    def do_step(self, current_time, step_size):
        import fmi2facade
        print(fmi2facade.test("Passing message to c"))
        print("before log")
        print(fmi2facade.log())
        return True
"""

    script_file = tmp_path / "orig" / "slavewithexception.py"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    script_file.write_text(slave_code)

    FmuBuilder.build_FMU(script_file, dest=tmp_path)

    fmu = tmp_path / "PythonSlaveUsingExt.fmu"
    assert fmu.exists()

    fmpy.simulate_fmu(str(fmu), stop_time=0.1)
