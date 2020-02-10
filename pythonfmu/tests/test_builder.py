import itertools
import platform
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

import pythonfmu
from pythonfmu.builder import FmuBuilder

DEMO = "pythonslave.py"
PROJECT_TEST_CASES = [
    ("dummy.txt",),
    ("dummy.py", "subdir/dummy.txt"),
    ("dummy.py", "subdir/dummy.txt", "subdir/dummy2.txt"),
    ("dummy.py", "subdir/dummy.txt", "subdir2/dummy2.txt"),
]


def get_platform():
    system = platform.system()
    is_64bits = sys.maxsize > 2 ** 32
    platforms = {"Windows": "win", "Linux": "linux", "Darwin": "darwin"}
    return platforms[system] + "64" if is_64bits else "32"


lib_extension = ({"Darwin": "so", "Linux": "so", "Windows": "dll"}).get(
    platform.system(), None
)

# TODO test xml


def test_zip_content(tmp_path):
    script_file = Path(__file__).parent / DEMO

    FmuBuilder.build_FMU(script_file, dest=tmp_path)

    fmu = tmp_path / "PythonSlave.fmu"
    assert fmu.exists()
    assert zipfile.is_zipfile(fmu)

    with zipfile.ZipFile(fmu) as files:
        names = files.namelist()

        assert "modelDescription.xml" in names
        assert "/".join(("resources", DEMO)) in names
        module_file = "/".join(("resources", "slavemodule.txt"))
        assert module_file in names
        assert (
            "/".join(("binaries", get_platform(), f"PythonSlave.{lib_extension}"))
            in names
        )

        # Check sources
        src_folder = Path(pythonfmu.__path__[0]) / "pythonfmu-export"
        for f in itertools.chain(
            src_folder.rglob("*.hpp"),
            src_folder.rglob("*.cpp"),
            src_folder.rglob("CMakeLists.txt"),
        ):
            assert "/".join(("sources", f.relative_to(src_folder).as_posix())) in names
        assert len(names) >= 15  # Library + python script + XML + module name + sources

        with files.open(module_file) as myfile:
            assert myfile.read() == b"pythonslave"


@pytest.mark.parametrize("pfiles", PROJECT_TEST_CASES)
def test_project_files(tmp_path, pfiles):
    script_file = Path(__file__).parent / DEMO
    pfiles = map(Path, pfiles)

    with tempfile.TemporaryDirectory() as project_dir:
        project_dir = Path(project_dir)

        project_files = set()
        for f in pfiles:
            full_name = project_dir / f
            if full_name.suffix:
                full_name.parent.mkdir(parents=True, exist_ok=True)
                full_name.write_text("dummy content")
            else:
                full_name.mkdir(parents=True, exist_ok=True)

            # Add subfolder and not file if common parent exits
            to_remove = None
            for p in project_files:
                if p.parent == full_name.parent or p == full_name.parent:
                    to_remove = p
                    break
            if to_remove is None:
                project_files.add(full_name)
            else:
                project_files.remove(to_remove)
                project_files.add(full_name.parent)

        FmuBuilder.build_FMU(script_file, dest=tmp_path, project_files=project_files)

    fmu = tmp_path / "PythonSlave.fmu"
    with zipfile.ZipFile(fmu) as files:
        names = files.namelist()

        parents = [p.parent for p in pfiles]
        unique_folders = set(parents)
        common_parents = set()
        if len(unique_folders) < len(parents):
            common_parents = set(filter(lambda f: parents.count(f) > 1, unique_folders))

            pfiles = map(lambda f: f if f.parent in common_parents else f.name, pfiles)

        for pfile in pfiles:
            assert f"resources/{pfile!s}" in names


@pytest.mark.parametrize("pfiles", PROJECT_TEST_CASES)
def test_project_files_containing_script(tmp_path, pfiles):
    orig_script_file = Path(__file__).parent / DEMO
    pfiles = map(Path, pfiles)

    with tempfile.TemporaryDirectory() as project_dir:
        project_dir = Path(project_dir)
        script_file = project_dir / DEMO
        with open(orig_script_file) as script_f:
            script_file.write_text(script_f.read())

        for f in pfiles:
            full_name = project_dir / f
            if full_name.suffix:
                full_name.parent.mkdir(parents=True, exist_ok=True)
                full_name.write_text("dummy content")
            else:
                full_name.mkdir(parents=True, exist_ok=True)

        FmuBuilder.build_FMU(
            script_file, dest=tmp_path, project_files=[script_file.parent]
        )

    fmu = tmp_path / "PythonSlave.fmu"
    with zipfile.ZipFile(fmu) as files:
        names = files.namelist()

        parents = [p.parent for p in pfiles]
        unique_folders = set(parents)
        common_parents = set()
        if len(unique_folders) < len(parents):
            common_parents = set(filter(lambda f: parents.count(f) > 1, unique_folders))

            pfiles = map(lambda f: f if f.parent in common_parents else f.name, pfiles)

        for pfile in pfiles:
            assert f"resources/{pfile!s}" in names


def test_documentation(tmp_path):
    script_file = Path(__file__).parent / DEMO

    with tempfile.TemporaryDirectory() as documentation_dir:
        doc_dir = Path(documentation_dir)
        license_file = doc_dir / "licenses" / "license.txt"
        license_file.parent.mkdir()
        license_file.write_text("Dummy license")
        index_file = doc_dir / "index.html"
        index_file.write_text("dummy index")

        FmuBuilder.build_FMU(script_file, dest=tmp_path, documentation_folder=doc_dir)

    fmu = tmp_path / "PythonSlave.fmu"

    with zipfile.ZipFile(fmu) as files:
        names = files.namelist()

        assert "documentation/index.html" in names
        assert "documentation/licenses/license.txt" in names
