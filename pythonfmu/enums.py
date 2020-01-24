from enum import Enum


class Fmi2Causality(Enum):
    parameter = 0,
    calculatedParameter = 1,
    input = 2,
    output = 3,
    local = 4


class Fmi2Initial(Enum):
    exact = 0,
    approx = 1,
    calculated = 2


class Fmi2Variability(Enum):
    constant = 0,
    fixed = 1,
    tunable = 2,
    discrete = 3,
    continuous = 4
