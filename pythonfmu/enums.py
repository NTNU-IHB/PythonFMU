"""FMI enumerations"""
from enum import Enum, IntEnum


class Fmi2Causality(Enum):
    parameter = 0
    calculatedParameter = 1
    input = 2
    output = 3
    local = 4


class Fmi2Initial(Enum):
    exact = 0
    approx = 1
    calculated = 2


class Fmi2Variability(Enum):
    constant = 0
    fixed = 1
    tunable = 2
    discrete = 3
    continuous = 4


class Fmi2Status(IntEnum):
    ok = 0
    warning = 1
    discard = 2
    error = 3
    fatal = 4

