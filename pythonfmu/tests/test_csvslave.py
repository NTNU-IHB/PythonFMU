import pytest
from pathlib import Path

from pythonfmu.csvbuilder import CsvFmuBuilder

EPS = 1e-7
DEMO = "csvdemo.csv"


def test_csvslave(tmp_path):
    fmpy = pytest.importorskip(
        "fmpy", reason="fmpy is not available for testing the produced FMU"
    )

    csv_file = Path(__file__).parent / DEMO

    fmu = CsvFmuBuilder.build_FMU(csv_file, dest=tmp_path)
    assert fmu.exists()

    model_description = fmpy.read_model_description(fmu)
    unzip_dir = fmpy.extract(fmu)

    model = fmpy.fmi2.FMU2Slave(
        guid=model_description.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=model_description.coSimulation.modelIdentifier,
        instanceName='instance1')

    t = 0.0
    dt = 0.1

    def init_model():
        model.instantiate()
        model.setupExperiment()
        model.enterInitializationMode()
        model.exitInitializationMode()

    def step_model():
        nonlocal t
        model.doStep(t, dt)
        t += dt

    print("\n")
    init_model()

    for i in range(1, 5):
        assert model.getInteger([0])[0] == i
        assert model.getReal([1])[0] == pytest.approx(pow(2, i), rel=EPS)
        assert model.getBoolean([2])[0] == i % 2
        assert model.getString([3])[0].decode("utf-8") == str(i)
        step_model()

    model.reset()
    init_model()

    t = 0.0
    dt = 0.05

    ints = []
    actual_ints = [1, 1, 2, 2, 3, 3, 4, 4]
    reals = []
    actual_reals = [2.0, 3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
    for i in range(0, 8):
        ints.append(model.getInteger([0])[0])
        reals.append(model.getReal([1])[0])
        step_model()
    assert ints == actual_ints
    for i in range(0, len(reals)):
        assert reals[i] == pytest.approx(actual_reals[i], rel=EPS)
