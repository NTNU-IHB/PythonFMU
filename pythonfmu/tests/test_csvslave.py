import pytest
from pathlib import Path

from pythonfmu.builder import FmuBuilder

EPS = 1e-7
DEMO = "csvdemo.csv"

def test_csvslave(tmp_path):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    csv_file = Path(__file__).parent / DEMO

    fmu = FmuBuilder.build_FMU(csv_file, dest=tmp_path)
    assert fmu.exists()

    model_description = fmpy.read_model_description(fmu)
    unzip_dir = fmpy.extract(fmu)

    model = fmpy.fmi2.FMU2Slave(
        guid=model_description.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=model_description.coSimulation.modelIdentifier,
        instanceName='instance1')

    vrs = [0, 1]
    t = 0.0
    dt = 0.1

    def step_model():
        nonlocal t
        model.doStep(t, dt)
        t += dt

    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    for i in range(1, 6):
        values = model.getReal(vrs)
        assert values[0] == pytest.approx(i, rel=EPS)
        assert values[1] == pytest.approx(pow(2, i), rel=EPS)
        step_model()
