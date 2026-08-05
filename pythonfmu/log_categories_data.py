"""Canonical fmi2Status -> log category mapping.

Single source of truth shared with the native library: at CMake build time,
tools/generate_log_categories_header.py imports this module and generates
LogCategories.hpp (included by src/pythonfmu/Logger.hpp), so the compiled
library and pythonfmu.fmi2slave.Fmi2Slave.log_categories can never diverge.

Edit only this file; the generated C++ header must not be hand-edited.
"""
from typing import List, Tuple

# (fmi2Status C enumerator, category name, description)
LOG_CATEGORIES: List[Tuple[str, str, str]] = [
    ("fmi2Warning", "logStatusWarning", "Log messages with fmi2Warning status."),
    ("fmi2Discard", "logStatusDiscard", "Log messages with fmi2Discard status."),
    ("fmi2Error", "logStatusError", "Log messages with fmi2Error status."),
    ("fmi2Fatal", "logStatusFatal", "Log messages with fmi2Fatal status."),
]

# Fallback category used for statuses not covered above (e.g. fmi2OK, fmi2Pending).
LOG_ALL_CATEGORY = "logAll"
LOG_ALL_DESCRIPTION = "Log all messages."
