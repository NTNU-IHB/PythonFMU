# PythonFMU (work in progress)

> A lightweight framework that enables the packaging of Python3.x code as co-simulation FMUs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/NTNU-IHB/PythonFMU/issues)

[![Gitter](https://badges.gitter.im/NTNU-IHB/FMI4j.svg)](https://gitter.im/NTNU-IHB/PythonFMU?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


### How do I build an FMU from python code?

1) Install `pythonfmu` package:
```bash
pip install git+https://github.com/fcollonval/PythonFMU.git
```
2) Create a new class extending the `Fmi2Slave` class declared in the `pythonfmu.fmi2slave` module. 
3) Run `pythonfmu-builder` to create the fmu.

```
usage: pythonfmu-builder [-h] -f SCRIPT_FILE [-c CLASS_NAME] [-d DEST] [--external-tool] [--no-variable-step] [--interpolate-inputs]
                         [--only-one-per-process] [--handle-state] [--serialize-state] [--use-memory-management]
                         [Project files [Project files ...]]

Build a FMU from a Python script.

positional arguments:
  Project files         Additional project files required by the Python script.

optional arguments:
  -h, --help            show this help message and exit
  -f SCRIPT_FILE, --file SCRIPT_FILE
                        Path to the Python script.
  -c CLASS_NAME, --class CLASS_NAME
                        Class name of the inter
  -d DEST, --dest DEST  Where to save the FMU.
fmu options:
  --external-tool
  --no-variable-step
  --interpolate-inputs
  --only-one-per-process
  --handle-state
  --serialize-state
  --use-memory-management
```

##### Example: 

###### Write the script

```python

from pythonfmu import Fmi2Causality, Fmi2Slave, Boolean, Integer, Real, String

slave_class = "PythonSlave"  # REQUIRED - Name of the class extending Fmi2Slave


class PythonSlave(Fmi2Slave):

    author = "John Doe"
    modelName = "PythonSlave"  # REQUIRED
    description = "A simple description"

    def __init__(self):
        super().__init__()

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


###### Use the FMU

The generate FMU can be executed with [`pyfmi`]().

```bash
pip install pyfmi
python -c "from pyfmi import load_fmu; m = load_fmu('MyFMU.fmu'); res = m.simulate(final_time=1); print(res['time'])"
```

### Note

PythonFMU does not bundle Python, which makes it a tool coupling solution. This means that you can not expect the generated FMU to work on a different system (The system would need a compatible Python version and libraries). 
PythonFMU does not automatically resolve 3rd party dependencies either. If your code includes e.g. `numpy`, the target system also needs to have `numpy` installed.

To `pip` install PythonFMU you will need a compiler.

***

Would you rather build FMUs in Java? Check out [FMI4j](https://github.com/NTNU-IHB/FMI4j)!  
Need to distribute your FMUs? [FMU-proxy](https://github.com/NTNU-IHB/FMU-proxy) to the rescue! 
