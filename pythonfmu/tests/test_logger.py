import pytest
from unittest.mock import MagicMock

from pythonfmu.builder import FmuBuilder
from pythonfmu.enums import Fmi2Status

pytestmark = pytest.mark.skipif(
    not FmuBuilder.has_binary(), reason="No binary available for the current platform."
)


@pytest.mark.integration
@pytest.mark.parametrize("debug", [True, False])
@pytest.mark.parametrize("status", Fmi2Status)
def test_logger(tmp_path, debug, status):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    name = "PythonSlaveWithLogger"
    category = "category"
    message = "log message"

    slave_code = f"""from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Status, Fmi2Causality, Integer, Real, Boolean, String


class {name}(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.realIn = 22.0
        self.realOut = 0.0
        self.register_variable(Real("realIn", causality=Fmi2Causality.input))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))


    def do_step(self, current_time, step_size):
        self.log("{message}", {status}, "{category}", {debug})
        return True
"""

    script_file = tmp_path / "orig" / "slavewithlogger.py"
    script_file.parent.mkdir(parents=True, exist_ok=True)
    script_file.write_text(slave_code)

    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path)

    fmu = tmp_path / f"{name}.fmu"
    assert fmu.exists()

    logger = MagicMock()

    fmpy.simulate_fmu(
        str(fmu),
        stop_time=1e-3,
        output_interval=1e-3,
        logger=logger,
        debug_logging=True
    )

    logger.assert_called_once_with(
        logger.call_args[0][0],  # Don't test the first argument
        bytes(name, encoding="utf-8"),
        0,  # TODO this is a hack.
        bytes(category, encoding="utf-8"),
        bytes(message, encoding="utf-8")
    )
