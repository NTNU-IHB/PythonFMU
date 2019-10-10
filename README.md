# PythonFMU (work in progress)
Export Python3 code as FMUs


### How do I build an FMU from python code?

1) Download the `Fmi2Slave.py` source file
2) In a new file, create a new class called `Model` extending the `Fmi2Slave` class declared in `Fmi2Slave.py`.
3) Run `pythonfmu-builder`

```
Usage: fmu-builder [-h] [-d=<destFile>] -f=<scriptFile> [Project files...]
      [Project files...]    Additional project files required by the Python script.
  -d, --dest=<destFile>     Where to save the FMU.
  -f, --file=<scriptFile>   Path to the Python script.
  -h, --help                Print this message and quits.

```

##### Example: 

####### Write the script

```python
from pythonfmu.Fmi2Slave import *


class Model(Fmi2Slave):

    Fmi2Slave.modelName = "PythonSlave"  # REQUIRED
    Fmi2Slave.author = "John Doe"
    # Additional model information can be added

    def __init__(self):
        super().__init__()

        self.intOut = 1
        self.realOut = 3.0
        self.register_variable(Integer("intOut").set_causality(Fmi2Causality.output))  # register self.intOut as output
        self.register_variable(Real("realOut").set_causality(Fmi2Causality.output))  # register self.realOut as output

    def doStep(self, currentTime, stepSize):
        print(f"doStep, currentTime={currentTime}, stepSize={stepSize}")

```

####### Create the FMU 

```
java -jar pythonfmu-builder.jar -f model.py pythonfmu
```

In this example a python slave (extending `Fmi2Slave`) is declared in a file named `model.py`. `pythonfmu` is a folder containing additional project files required by `model.py`, including `Fmi2Slave.py`. Project folders such as this will be recursively copied into the FMU 
