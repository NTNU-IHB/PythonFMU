import pytest
from pathlib import Path

from pythonfmu.csvbuilder import FmuBuilder


def test_default_experiment(tmp_path):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    script_file = Path(__file__).parent / "slaves/pythonslave_default_ex.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()

    model_description = fmpy.read_model_description(fmu)
    default_experiment = model_description.defaultExperiment

    assert default_experiment.startTime == pytest.approx(1.0)
    assert default_experiment.stopTime == pytest.approx(2)
    assert default_experiment.tolerance == pytest.approx(1e-3)
    assert default_experiment.stepSize == pytest.approx(1e-3)
