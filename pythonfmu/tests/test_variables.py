import pytest

from pythonfmu.variables import ScalarVariable


def test_ScalarVariable_reference_set_once_only():
    v = ScalarVariable('variable')
    v.value_reference = 22

    with pytest.raises(RuntimeError):
        v.value_reference = 33
