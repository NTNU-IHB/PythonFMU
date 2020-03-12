import itertools
import pytest
from unittest.mock import call, MagicMock

from pythonfmu.builder import FmuBuilder
from pythonfmu.enums import Fmi2Status

pytestmark = pytest.mark.skipif(
    not FmuBuilder.has_binary(), reason="No binary available for the current platform."
)


@pytest.mark.integration
def test_logger(tmp_path):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    name = "PythonSlaveWithLogger"
    category = "category"
    message = "log message"

    log_calls = [
        (
            f"{status.name.upper()} - {debug} - {message}", 
            status, 
            category, 
            debug
        ) for debug, status in itertools.product([True, False], Fmi2Status)
    ]

    fmu_calls = "\n".join([
        '        self.log("{}", Fmi2Status.{}, "{}", {})'.format(c[0], c[1].name, c[2], c[3]) for c in log_calls
    ])

    slave_code = f"""from pythonfmu.fmi2slave import Fmi2Slave, Fmi2Status, Fmi2Causality, Integer, Real, Boolean, String


class {name}(Fmi2Slave):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.realIn = 22.0
        self.realOut = 0.0
        self.register_variable(Real("realIn", causality=Fmi2Causality.input))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))


    def do_step(self, current_time, step_size):
{fmu_calls}
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

    expected_calls = [
        call(
            logger.call_args[0][0],  # Don't test the first argument
            bytes(name, encoding="utf-8"),
            int(c[1]),
            bytes(c[2], encoding="utf-8"),
            bytes(c[0], encoding="utf-8")
        ) for c in log_calls
    ]

    logger.assert_has_calls(expected_calls)
