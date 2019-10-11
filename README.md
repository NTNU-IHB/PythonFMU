# PythonFMU (work in progress)
Export Python3 code as FMUs


### How do I build an FMU from python code?

1) Download the `Fmi2Slave.py` source file.
2) In a new file, create a new class called `Model` extending the `Fmi2Slave` class declared in `Fmi2Slave.py`.
3) Run the `pythonfmu-builder.jar` (Built by Github Actions).

```
Usage: pythonfmu-builder [-h] [-d=<destFile>] -f=<scriptFile> [Project files...]
      [Project files...]    Additional project files required by the Python script.
  -d, --dest=<destFile>     Where to save the FMU.
  -f, --file=<scriptFile>   Path to the Python script.
  -h, --help                Print this message and quits.

```

##### Example: 

###### Write the script

```python
from pythonfmu.Fmi2Slave import *


class Model(Fmi2Slave):

    Fmi2Slave.modelName = "PythonSlave"
    Fmi2Slave.author = "John Doe"

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.booleanVariable = True
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output))
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))
        self.register_variable(Boolean("booleanVariable").set_causality(Fmi2Causality.local))

    def do_step(self, current_time, step_size):
        return True
```

###### Create the FMU 

```
java -jar pythonfmu-builder.jar -f model.py pythonfmu
```

In this example a python slave (extending `Fmi2Slave`) is declared in a file named `model.py`. `pythonfmu` is a folder containing additional project files required by `model.py`, including `Fmi2Slave.py`. Project folders such as this will be recursively copied into the FMU.
