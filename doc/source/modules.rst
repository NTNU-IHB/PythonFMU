Modules documentation
=====================
This section documents the contents of the PythonFMU package.

As an alternative to using the command line interface for generating FMUs, they can also be generated programmatically through a code like 
(assuming that fmi2slave has been extended, generating the `scriptFile`)

.. code-block:: python

   import tempfile
   import zipfile
   from pathlib import Path

  from pythonfmu.builder import FmuBuilder #builder, csvbuilder, deploy
   from pythonfmu._version import __version__

   if __name__ == '__main__':
       def build( scriptFile): 
           with tempfile.TemporaryDirectory() as documentation_dir:
               doc_dir = Path(documentation_dir)
               license_file = doc_dir / "licenses" / "license.txt"
               license_file.parent.mkdir()
               license_file.write_text("Dummy license")
               index_file = doc_dir / "index.html"
               index_file.write_text("dummy index")
               return FmuBuilder.build_FMU(scriptFile, dest='.', documentation_folder=doc_dir)
       build('basic_example.py')

builder
-------
Python FMU builder

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `csvbuilder`_
   * - Uses: 
     - `fmi2slave`_, `osutil`_
   * - Imports: 
     - argparse, importlib, ittertools, logging, pathlib, re, shutil, sys, tempfile, typing, xml, zipfile

.. autofunction:: pythonfmu.builder.get_model_description

.. autoclass:: pythonfmu.builder.FmuBuilder
   :members:
   
csvbuilder
----------
Python FMU builder from CSV

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - 
   * - Uses: 
     - `fmi2slave`_, `builder`_
   * - Imports: 
     - argparse, pathlib, tempfile, typing

.. autoclass:: pythonfmu.csvbuilder.CsvFmuBuilder
   :members:
   
default_experiment
------------------
Define the FMU default experiment

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `fmi2slave`_
   * - Uses: 
     - 
   * - Imports: 
     - 

.. autoclass:: pythonfmu.default_experiment.DefaultExperiment
   :members:

deploy
------
CLI command to deploy a FMU

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - 
   * - Uses: 
     - `enums`_
   * - Imports: 
     - argparse, os, pathlib, tempfile, typing, subprocess, sys, zipfile

.. autofunction:: pythonfmu.deploy.deploy

enums
-----
FMI enumerations (extensions of standard class Enum) for FMI variables

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `deploy`_, `fmi2slave`_, `variables`_
   * - Uses: 
     -  
   * - Imports: 
     - enum

* Fmi2Type
* Fmi2Causality
* Fmi2Initial
* Fmi2Variability
* Fmi2Status
* PackageManager (pip or conda)

fmi2slave
---------
Construct the abstract facade class (to be extended by applications)

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `builder`_, `csvbuilder`_
   * - Uses: 
     - `default_experiment`_, `enums`_, `logmsg`_, `variables`_, `_version`_ 
   * - Imports: 
     - abc, collections, datetime, json, pathlib, typing, uuid, xml

.. autoclass:: pythonfmu.fmi2slave.Fmi2Slave
   :members:

logmsg
------
Generate standard FMU log messages

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `fmi2slave`_
   * - Uses: 
     - 
   * - Imports: 
     - 

.. autoclass:: pythonfmu.logmsg.LogMsg
   :members:

osutil
------

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `builder`_
   * - Uses: 
     - 
   * - Imports: 
     - sys, platform

.. autofunction:: pythonfmu.osutil.get_platform

.. autofunction:: pythonfmu.osutil.get_lib_extension

variables
---------

.. list-table::
   :widths: 20 100
   :align: left

   * - Used by: 
     - `fmi2slave`_
   * - Uses: 
     - `enums`_
   * - Imports: 
     - abc, enum, typing, xml

.. autoclass:: pythonfmu.variables.ScalarVariable

.. autoclass:: pythonfmu.variables.Real

.. autoclass:: pythonfmu.variables.Integer

.. autoclass:: pythonfmu.variables.Boolean

.. autoclass:: pythonfmu.variables.String



