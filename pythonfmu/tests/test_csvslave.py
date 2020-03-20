import pytest
from pathlib import Path

import pythonfmu
from pythonfmu.builder import FmuBuilder
from pythonfmu.csvslave import create

DEMO = "csvdemo.csv"

def test_csvslave(tmp_path):
    csv_file = Path(__file__).parent / DEMO

    print(create(csv_file))

    #fmu = FmuBuilder.build_FMU(csv_file, dest=tmp_path)
    #assert fmu.exists()



