import pytest
from pathlib import Path

from pythonfmu.csvbuilder import FmuBuilder


def test_default_experiment(tmp_path):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    script_file = Path(__file__).parent / "slaves/pythonslave_read_file.py"
    project_file = Path(__file__).parent / "data/hello.txt"
    fmu = FmuBuilder.build_FMU(script_file, project_files=[project_file], dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()

    model_description = fmpy.read_model_description(fmu)
