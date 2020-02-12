# PythonFMU

> A lightweight framework that enables the packaging of Python3.x code as co-simulation FMUs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/NTNU-IHB/PythonFMU/issues)
[![CI](https://github.com/NTNU-IHB/PythonFMU/workflows/CI/badge.svg)](https://github.com/NTNU-IHB/PythonFMU/actions?query=workflow%3ACI)
[![PyPI](https://img.shields.io/pypi/v/pythonfmu)](https://pypi.org/project/pythonfmu/)

[![Gitter](https://badges.gitter.im/NTNU-IHB/FMI4j.svg)](https://gitter.im/NTNU-IHB/PythonFMU?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


### How do I build an FMU from python code?

1) Install `pythonfmu` package:
```bash
pip install git+https://github.com/NTNU-IHB/PythonFMU.git
```
2) Create a new class extending the `Fmi2Slave` class declared in the `pythonfmu.fmi2slave` module. 
3) Run `pythonfmu-builder` to create the fmu.

```
usage: pythonfmu-builder [-h] -f SCRIPT_FILE [-d DEST]
                         [--doc DOCUMENTATION_FOLDER]
                         [Project files [Project files ...]]

Build a FMU from a Python script.

positional arguments:
  Project files         Additional project files required by the Python
                        script.

optional arguments:
  -h, --help            show this help message and exit
  -f SCRIPT_FILE, --file SCRIPT_FILE
                        Path to the Python script.
  -d DEST, --dest DEST  Where to save the FMU.
  --doc DOCUMENTATION_FOLDER
                        Documentation folder to include in the FMU.
```

##### Example: 

###### Write the script

```python

from pythonfmu import Fmi2Causality, Fmi2Slave, Boolean, Integer, Real, String

slave_class = "PythonSlave"  # REQUIRED - Name of the class extending Fmi2Slave


class PythonSlave(Fmi2Slave):

    author = "John Doe"
    description = "A simple description"

    def __init__(self, instance_name):
        super().__init__(instance_name)

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.stringVariable = "Hello World!"
        self.register_variable(Integer("intOut", causality=Fmi2Causality.output))
        self.register_variable(Real("realOut", causality=Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable", causality=Fmi2Causality.local))
        self.register_variable(String("stringVariable", causality=Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        return True

```

###### Create the FMU 

```
pythonfmu-builder -f pythonslave.py pythonfmu
```

In this example a python class named `PythonSlave` that extends `Fmi2Slave` is declared in a file named `pythonslave.py`. 
`pythonfmu` is a optional folder containing additional project files required by the python script. 
Project folders such as this will be recursively copied into the FMU. Multiple project files/folders may be added.

### Note

PythonFMU does not bundle Python, which makes it a tool coupling solution. This means that you can not expect the generated FMU to work on a different system (The system would need a compatible Python version and libraries). But to ease its usage the wrapper is compile using
the limited Python API. So the provided binary libraries for Linux and Windows 64-bits should
be compatible with any Python 3 environment. If you need to compile the wrapper for on a specific configuration,
you will need cmake and a C++ compiler. The commands for building the wrapper on Linux and on Windows can be seen in 
the [GitHub workflow](./.github/workflows/main.yml).

PythonFMU does not automatically resolve 3rd party dependencies either. If your code includes e.g. `numpy`, the target system also needs to have `numpy` installed.

***

Would you rather build FMUs in Java? Check out [FMI4j](https://github.com/NTNU-IHB/FMI4j)!  
Need to distribute your FMUs? [FMU-proxy](https://github.com/NTNU-IHB/FMU-proxy) to the rescue! 


### Credits

This works has been possible thanks to the contributions of @markaren from NTNU-IHB and @fcollonval from Safran SA.
