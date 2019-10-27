# PythonFMU (work in progress)
> A lightweight framework that enables the packaging of Python3.x code as co-simulation FMUs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/NTNU-IHB/PythonFMU/issues)

[![Gitter](https://badges.gitter.im/NTNU-IHB/FMI4j.svg)](https://gitter.im/NTNU-IHB/PythonFMU?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)


### How do I build an FMU from python code?

1) Download the [fmi2slave](fmi2slave.py) module.
2) Create a new class extending the `Fmi2Slave` class declared in the `fmi2slave` module. 
3) Run `pythonfmu-builder.jar` (Built by Github Actions).

```
Usage: pythonfmu-builder [-h] -c=<className> [-d=<destFile>] -f=<scriptFile>
                         [Project files...]
      [Project files...]    Additional project files required by the Python script.
  -d, --dest=<destFile>     Where to save the FMU.
  -f, --file=<scriptFile>   Path to the Python script.
  -h, --help                Print this message and quits.
```

##### Example: 

###### Write the script

```python

from pythonfmu.fmi2slave import *

slave_class = "PythonSlave"  # REQUIRED - Name of the class extending Fmi2Slave


class PythonSlave(Fmi2Slave):

    Fmi2Slave.author = "John Doe"
    Fmi2Slave.modelName = "PythonSlave"  # REQUIRED
    Fmi2Slave.description = "A simple description"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.stringVariable = "Hello World!"
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output))
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable").set_causality(Fmi2Causality.local))
        self.register_variable(String("stringVariable").set_causality(Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        return True

```

###### Create the FMU 

```
java -jar pythonfmu-builder.jar -f pythonslave.py pythonfmu
```

In this example a python class named `PythonSlave` that extends `Fmi2Slave` is declared in a file named `pythonslave.py`. 
`pythonfmu` is a folder containing additional project files required by the python script, including `fmi2slave.py`. 
Project folders such as this will be recursively copied into the FMU. Multiple project files/folders may be added.


### Note

PythonFMU does not bundle Python, which makes it a tool coupling solution. This means that you can not expect the generated FMU to work on a different system (The system would need a compatible Python version and libraries). 
PythonFMU does not automatically resolve 3rd party dependencies either. If your code includes e.g. `numpy`, the target system also needs to have `numpy` installed.

PythonFMU requires a x64 Python installation (You are however free to build x86 binaries yourself).

***

Would you rather build FMUs in Java? Check out [FMI4j](https://github.com/NTNU-IHB/FMI4j)! 
Need to distribute your FMUs? [FMU-proxy](https://github.com/NTNU-IHB/FMU-proxy) to the rescue! 
