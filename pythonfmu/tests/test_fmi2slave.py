import pytest

from pythonfmu import Fmi2Slave, Boolean, Integer, Real, String

# TODO test xml

FMI2PY = dict((
    (Boolean, bool),
    (Integer, int),
    (Real, float),
    (String, str)
))
PY2FMI = dict([(v, k) for k, v in FMI2PY.items()])


@pytest.mark.parametrize("model", ["theModelName", None])
def test_Fmi2Slave_constructor(model):
    class Slave(Fmi2Slave):
        modelName = model
        def do_step(self, t, dt):
            return True

    if model is None:
        _ = Slave("instanceSlave")
        assert Slave.modelName == "Slave"
    else:
        _ = Slave("instanceSlave")
        assert Slave.modelName == model

@pytest.mark.parametrize("fmi_type", FMI2PY)
@pytest.mark.parametrize("value", [
    False, 
    22, 
    2./3., 
    "hello_world"
])
def test_Fmi2Slave_getters(fmi_type, value):
    
    class Slave(Fmi2Slave):
        def __init__(self, instance_name):
            super().__init__(instance_name)
            self.var = value
            self.register_variable(PY2FMI[type(value)]("var"))

        def do_step(self, t, dt):
            return True
    
    py_type = FMI2PY[fmi_type]
    fmi_type_name = fmi_type.__qualname__.lower()

    slave = Slave("instanceSlave")
    if type(value) is py_type:
        assert getattr(slave, f"get_{fmi_type_name}")([0, ]) == [value, ]
    else:
        with pytest.raises(TypeError):
            getattr(slave, f"get_{fmi_type_name}")([0, ])


@pytest.mark.parametrize("fmi_type", FMI2PY)
@pytest.mark.parametrize("value", [
    False, 
    22, 
    2./3., 
    "hello_world",
])
def test_Fmi2Slave_setters(fmi_type, value):
    class Slave(Fmi2Slave):
        def __init__(self, instance_name):
            super().__init__(instance_name)
            self.var = None
            self.register_variable(PY2FMI[type(value)]("var"))

        def do_step(self, t, dt):
            return True
    
    slave = Slave("instanceSlave")
    py_type = FMI2PY[fmi_type]
    fmi_type_name = fmi_type.__qualname__.lower()

    if type(value) is py_type:
        set_method = getattr(slave, f"set_{fmi_type_name}")
        set_method([0, ], [value, ])
        assert getattr(slave, f"get_{fmi_type_name}")([0, ]) == [value, ]
    else:
        set_method = getattr(slave, f"set_{fmi_type_name}")
        with pytest.raises(TypeError):
            set_method([0, ], [value, ])
