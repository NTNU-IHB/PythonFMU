"""FMI enumerations"""
from enum import Enum, IntEnum


class Fmi2Type(Enum):
    '''FMI 2 variable types: integer, real, boolean, string, enumeration'''
    integer = 0
    real = 1
    boolean = 2
    string = 3
    enumeration = 4


class Fmi2Causality(Enum):
    '''FMI 2 causality setting: parameter, calculatedParameter, input, output, local'''
    parameter = 0
    calculatedParameter = 1
    input = 2
    output = 3
    local = 4


class Fmi2Initial(Enum):
    '''FMI 2 initial setting: exact, approx, calculated'''
    exact = 0
    approx = 1
    calculated = 2


class Fmi2Variability(Enum):
    '''FMI 2 variability setting: constant, fixed, tunable, discrete, continuous'''
    constant = 0
    fixed = 1
    tunable = 2
    discrete = 3
    continuous = 4


class Fmi2Status(IntEnum):
    '''FMI 2 status types: ok, warning, discard, error, fatal'''
    ok = 0
    warning = 1
    discard = 2
    error = 3
    fatal = 4


class PackageManager(Enum):
    """Enumeration of Python packages manager. pip, conda"""
    pip = "pip"
    conda = "conda"
