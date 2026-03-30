import argparse
import re
import zipfile
from pathlib import Path, PurePosixPath
from typing import Union


def info(fmu: Union[str, Path]) -> None:
    """Display information about a generated FMU.

    Inspects the FMU archive and prints:
      - Supported platforms derived from FMI binaries in the binaries/ directory
        (e.g. Windows (x64), Linux (x64))
      - Compiled model(s) (.pyd / .so) found in the resources/ directory,
        including Python implementation (CPython, PyPy, GraalPy),
        Python version (e.g. cp314), and platform architecture
      - Python package dependencies from resources/requirements.txt

    Args:
        fmu (str or pathlib.Path): Path to the FMU file.
    """
    fmu = Path(fmu)
    if not fmu.exists():
        raise FileNotFoundError(f"FMU file not found: {fmu}")

    with zipfile.ZipFile(fmu) as zf:
        names = zf.namelist()

        # --- Supported platforms (FMI binaries in binaries/) ---
        platform_folders = {
            PurePosixPath(n).parent.name
            for n in names
            if n.startswith("binaries/")
            and not n.endswith("/")
        }

        if platform_folders:
            print("Supported platforms:")
            for folder in sorted(platform_folders):
                print(f"  {_friendly_platform(folder)}")
        else:
            print("No supported platforms found (no FMI binaries).")

        # --- Locate .pyd / .so compiled models in resources/ (first level only) ---
        bin_files = [
            n for n in names
            if n.startswith("resources/")
            and "/" not in n[len("resources/"):]
            and (n.endswith(".pyd") or n.endswith(".so"))
        ]

        if bin_files:
            print("\nCompiled model(s):")
            for bf in bin_files:
                fname = PurePosixPath(bf).name
                print(f"  {fname}")
                _print_extension_info(fname)
        else:
            print("\nNo compiled model (.pyd / .so) found.")

        # --- Requirements ---
        req_path = "resources/requirements.txt"
        if req_path in names:
            print("\nPython package dependencies (requirements.txt):")
            with zf.open(req_path) as rf:
                content = rf.read().decode("utf-8")
                for line in content.splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#"):
                        print(f"  {stripped}")
        else:
            print("\nNo requirements.txt found in resources/.")


def _friendly_platform(folder: str) -> str:
    """Map an FMI binary folder name to platform name.

    Examples:
        win64   -> Windows (x64)
        linux64 -> Linux (x64)
        darwin64 -> macOS (x64)
    """
    _PLATFORM_LABELS = {
        "win64": "Windows (x64)",
        "win32": "Windows (x86)",
        "linux64": "Linux (x64)",
        "linux32": "Linux (x86)",
        "darwin64": "macOS (x64)",
        "darwin32": "macOS (x86)",
    }
    return _PLATFORM_LABELS.get(folder, folder)


def _print_extension_info(filename: str) -> None:
    """Parse a compiled Python extension filename and print platform and Python version.

    Recognised patterns (CPython, PyPy, GraalPy):
        modulename.cpython-314-x86_64-linux-gnu.so
        modulename.cp314-win_amd64.pyd
        modulename.pypy310-pp73-x86_64-linux-gnu.so
        modulename.pypy39-pp73-win_amd64.pyd
        modulename.graalpy-24_1-native-x86_64-linux-gnu.so
    """
    stem = filename.rsplit(".", 1)[0]  # drop final extension

    impl_name: str | None = None
    version_tag: str | None = None
    version_display: str | None = None

    cp_match = re.search(r"[._](cpython-|cp)(\d+)", stem)
    pypy_match = re.search(r"[._](pypy)(\d+)", stem)
    graalpy_match = re.search(r"[._](graalpy)-([0-9_]+)", stem)

    if cp_match:
        raw_ver = cp_match.group(2)
        impl_name = "CPython"
        version_tag = f"cp{raw_ver}"
        version_display = f"{raw_ver[0]}.{raw_ver[1:]}"
    elif pypy_match:
        raw_ver = pypy_match.group(2)
        impl_name = "PyPy"
        version_tag = f"pp{raw_ver}"
        version_display = f"{raw_ver[0]}.{raw_ver[1:]}"
    elif graalpy_match:
        raw_ver = graalpy_match.group(2)  # e.g. "24_1"
        impl_name = "GraalPy"
        version_tag = f"graalpy-{raw_ver}"
        version_display = raw_ver.replace("_", ".")

    if impl_name is not None:
        print(f"    Python impl    : {impl_name}")
        print(f"    Python version : {version_tag} ({impl_name} {version_display})")
    else:
        print("    Python impl    : unknown")
        print("    Python version : unknown")

    # Platform / architecture – everything after the implementation+version tag.
    # Build a combined pattern that matches any of the three known prefixes.
    plat_match = re.search(
        r"[._](?:cpython-|cp|pypy|graalpy-)[\d_]+(?:-pp\d+)?[.-](.+)", stem
    )
    if plat_match:
        platform_tag = plat_match.group(1)
        print(f"    Platform arch  : {platform_tag}")
    else:
        # Fallback: derive from extension
        if filename.endswith(".pyd"):
            print("    Platform arch  : win (exact arch unknown)")
        elif filename.endswith(".so"):
            print("    Platform arch  : linux/macOS (exact arch unknown)")
        else:
            print("    Platform arch  : unknown")


def create_command_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-f",
        "--file",
        dest="fmu",
        help="Path to the FMU file to inspect.",
        required=True,
    )

    parser.set_defaults(execute=info)

