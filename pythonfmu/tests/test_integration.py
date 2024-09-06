import math
from pathlib import Path

import pytest

from pythonfmu.builder import FmuBuilder

pytestmark = pytest.mark.skipif(
    not FmuBuilder.has_binary(), reason="No binary available for the current platform."
)
fmpy = pytest.importorskip(
    "fmpy", reason="fmpy is required for testing the produced FMU"
)


def mapped(md):
    m = {}
    for v in md.modelVariables:
        m[v.name] = v
    return m


@pytest.mark.integration
def test_integration_demo(tmp_path):
    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()
    res = fmpy.simulate_fmu(str(fmu), stop_time=0.5, validate=False)

    assert res["realOut"][-1] == pytest.approx(res["time"][-1], rel=1e-7)


@pytest.mark.integration
def test_integration_reset(tmp_path):
    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()

    md = fmpy.read_model_description(str(fmu), validate=False)
    unzipdir = fmpy.extract(str(fmu))
    model = fmpy.fmi2.FMU2Slave(guid=md.guid,
                                unzipDirectory=unzipdir,
                                modelIdentifier=md.coSimulation.modelIdentifier,
                                instanceName="instance"
                                )
    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    vars = mapped(md)
    vr = vars["realOut"].valueReference
    dt = 0.1

    initial_value = model.getReal([vr])[0]
    assert initial_value == pytest.approx(3.0, rel=1e-7)
    model.doStep(0.0, dt, True)
    read = model.getReal([vr])[0]
    assert read == pytest.approx(dt, rel=1e-7)
    model.reset()
    read = model.getReal([vr])[0]
    assert read == pytest.approx(initial_value, rel=1e-7)

    model.terminate()
    model.freeInstance()


@pytest.mark.integration
def test_integration_get_state(tmp_path):
    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(
        script_file,
        dest=tmp_path,
        needsExecutionTool="false",
        canGetAndSetFMUstate="true")
    assert fmu.exists()

    md = fmpy.read_model_description(str(fmu), validate=False)
    unzipdir = fmpy.extract(str(fmu))
    model = fmpy.fmi2.FMU2Slave(guid=md.guid,
                                unzipDirectory=unzipdir,
                                modelIdentifier=md.coSimulation.modelIdentifier,
                                instanceName="instance"
                                )
    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    vars = mapped(md)
    vr = vars["realOut"].valueReference
    dt = 0.1
    t = 0.0

    def step_model():
        nonlocal t
        model.doStep(t, dt, True)
        t += dt

    step_model()
    state = model.getFMUstate()
    assert model.getReal([vr])[0] == pytest.approx(dt, rel=1e-7)
    step_model()
    assert model.getReal([vr])[0] == pytest.approx(dt * 2, rel=1e-7)
    model.setFMUstate(state)
    assert model.getReal([vr])[0] == pytest.approx(dt, rel=1e-7)
    step_model()
    assert model.getReal([vr])[0] == pytest.approx(dt * 3, rel=1e-7)
    model.freeFMUstate(state)

    model.terminate()
    model.freeInstance()


@pytest.mark.integration
def test_integration_get_serialize_state(tmp_path):

    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(
        script_file,
        dest=tmp_path,
        canGetAndSetFMUstate="true",
        canSerializeFMUstate="true")
    assert fmu.exists()

    md = fmpy.read_model_description(fmu, validate=False)
    unzip_dir = fmpy.extract(fmu)

    model = fmpy.fmi2.FMU2Slave(
        guid=md.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=md.coSimulation.modelIdentifier,
        instanceName='instance1')

    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    vars = mapped(md)
    vrs = [vars["realOut"].valueReference]
    t = 0.0
    dt = 0.1

    def step_model():
        nonlocal t
        model.doStep(t, dt)
        t += dt

    step_model()
    state = model.getFMUstate()
    assert model.getReal(vrs)[0] == pytest.approx(dt, rel=1e-7)
    step_model()
    assert model.getReal(vrs)[0] == pytest.approx(dt * 2, rel=1e-7)
    model.setFMUstate(state)
    assert model.getReal(vrs)[0] == pytest.approx(dt, rel=1e-7)
    step_model()
    assert model.getReal(vrs)[0] == pytest.approx(dt * 3, rel=1e-7)

    serialize_fmu_state = model.serializeFMUstate(state)
    model.freeFMUstate(state)
    de_serialize_fmu_state = model.deSerializeFMUstate(serialize_fmu_state)
    model.setFMUstate(de_serialize_fmu_state)
    assert model.getReal(vrs)[0] == pytest.approx(dt, rel=1e-7)

    model.freeFMUstate(de_serialize_fmu_state)

    model.terminate()
    model.freeInstance()


@pytest.mark.integration
def test_integration_get(tmp_path):
    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()

    md = fmpy.read_model_description(fmu, validate=False)
    unzip_dir = fmpy.extract(fmu)

    model = fmpy.fmi2.FMU2Slave(
        guid=md.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=md.coSimulation.modelIdentifier,
        instanceName='instance1')

    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    to_test = {
        "intParam": 42,
        "intOut": 23,
        "realOut": 3.0,
        "booleanVariable": True,
        "stringVariable": "Hello World!",
        "realIn": 2.0 / 3.0,
        "booleanParameter": False,
        "stringParameter": "dog",
        "container.someReal": 99.0,
        "container.subContainer.someInteger": -15
    }

    model_value = None
    variables = mapped(md)
    for key, value in to_test.items():
        var = variables[key]
        vrs = [var.valueReference]
        if var.type == "Integer":
            model_value = model.getInteger(vrs)[0]
        elif var.type == "Real":
            model_value = model.getReal(vrs)[0]
        elif var.type == "Boolean":
            model_value = model.getBoolean(vrs)[0]
        elif var.type == "String":
            model_value = model.getString(vrs)[0].decode("UTF-8")
        else:
            pytest.xfail("Unsupported type")

        assert model_value == value

    model.terminate()
    model.freeInstance()


@pytest.mark.integration
def test_integration_read_from_file(tmp_path):
    script_file = Path(__file__).parent / "slaves/pythonslave_read_file.py"
    project_file = Path(__file__).parent / "data/hello.txt"
    fmu = FmuBuilder.build_FMU(script_file, project_files=[project_file], dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()

    md = fmpy.read_model_description(fmu)
    unzip_dir = fmpy.extract(fmu)

    model = fmpy.fmi2.FMU2Slave(
        guid=md.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=md.coSimulation.modelIdentifier,
        instanceName='instance1')

    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    variables = mapped(md)
    var = variables["file_content"]
    model_value = model.getString([var.valueReference])[0].decode("UTF-8")

    with (open(project_file, 'r')) as file:
        data = file.read()

    assert model_value == data

    model.terminate()
    model.freeInstance()


@pytest.mark.integration
def test_integration_set(tmp_path):
    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path, needsExecutionTool="false")
    assert fmu.exists()

    md = fmpy.read_model_description(fmu, validate=False)
    unzip_dir = fmpy.extract(fmu)

    model = fmpy.fmi2.FMU2Slave(
        guid=md.guid,
        unzipDirectory=unzip_dir,
        modelIdentifier=md.coSimulation.modelIdentifier,
        instanceName='instance1')

    model.instantiate()
    model.setupExperiment()
    model.enterInitializationMode()
    model.exitInitializationMode()

    to_test = {
        "intParam": 20,
        "realIn": 1.0 / 3.0,
        "booleanParameter": True,
        "stringParameter": "cat",
        "container.someReal": 42.0,
        "container.subContainer.someInteger": 421
    }

    model_value = None
    variables = mapped(md)
    for key, value in to_test.items():
        var = variables[key]
        vrs = [var.valueReference]
        if var.type == "Integer":
            model.setInteger(vrs, [value])
            model_value = model.getInteger(vrs)[0]
        elif var.type == "Real":
            model.setReal(vrs, [value])
            model_value = model.getReal(vrs)[0]
        elif var.type == "Boolean":
            model.setBoolean(vrs, [value])
            model_value = model.getBoolean(vrs)[0]
        elif var.type == "String":
            model.setString(vrs, [value])
            model_value = model.getString(vrs)[0].decode("UTF-8")
        else:
            pytest.xfail("Unsupported type")

        assert model_value == value

    model.terminate()
    model.freeInstance()


@pytest.mark.integration
def test_simple_integration_fmpy(tmp_path):

    script_file = Path(__file__).parent / "slaves/pythonslave.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path)
    assert fmu.exists()
    res = fmpy.simulate_fmu(str(fmu), stop_time=2.0, validate=False)

    assert res["realOut"][-1] == pytest.approx(res["time"][-1], rel=1e-7)


@pytest.mark.integration
def test_integration_has_local_dep(tmp_path):

    script_file = Path(__file__).parent / "slaves/slavewithdep.py"
    local_file = Path(__file__).parent / "slaves/localmodule.py"

    fmu = FmuBuilder.build_FMU(
        script_file,
        dest=tmp_path,
        project_files=[local_file],
        needsExecutionTool="false",
    )
    assert fmu.exists()

    res = fmpy.simulate_fmu(str(fmu), stop_time=0.5)

    assert res["realOut"][-1] == pytest.approx(
        22.0 * 5.0 * math.exp(res["time"][-1] / 0.1), rel=1e-7
    )


@pytest.mark.integration
def test_integration_throw_py_error(tmp_path):

    script_file = Path(__file__).parent / "slaves/PythonSlaveWithException.py"
    fmu = FmuBuilder.build_FMU(script_file, dest=tmp_path)
    assert fmu.exists()

    with pytest.raises(Exception):
        fmpy.simulate_fmu(str(fmu), stop_time=1.0)
