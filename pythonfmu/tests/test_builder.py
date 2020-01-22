from pathlib import Path
import tempfile

import pytest

from pythonfmu.builder import FmuBuilder

try:
    import pyfmi
except ImportError:
    pyfmi = None

DEMO = "pythonslave.py"


def test_rawbuilder():
    script_file = Path(__file__).parent / DEMO

    with tempfile.TemporaryDirectory() as tmp_dir:
        FmuBuilder.build_FMU(script_file, dest=tmp_dir)

        fmus = list(Path(tmp_dir).rglob("*.fmu"))

        assert len(fmus) == 1

        pyfmi = pytest.importorskip("pyfmi", reason="pyfmi is required for testing the produced FMU")
        model = pyfmi.load_fmu(str(fmus[0]))
        res = model.simulate(final_time=2.)
