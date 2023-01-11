from pythonfmu import Fmi2Causality, Fmi2Slave, Real

try:
    import os
    import tensorflow as tf
    import numpy as np
except ImportError:
    os, np, tf = None, None, None


class MLDemo(Fmi2Slave):
    author = "Magnus Steinstø"
    description = "Limited range TensorFlow sin approximation"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Import Tensorflow model directory created by model.save([some_directory_name])
        try:
            # Fetch model from directory included in the FMU. Included files are not available until after
            # the FMU has been built. Included files and directories will have the same root as this file by default
            self.model = tf.keras.models.load_model(os.path.join(os.path.dirname(__file__), "stored-model"))
        except OSError:
            # Fetch model from local directory when building the FMU. Remember to include this directory
            # in the FMU itself as a project file. Path assumes this command is run from repo root folder
            self.model = tf.keras.models.load_model("./examples/tensorflow-model-export/stored-model")

        self.sin_input = 0.
        self.sin_output_tf = 0.
        self.sin_output_ref = np.sin([self.sin_input])[0]

        self.register_variable(Real("sin_input", causality=Fmi2Causality.input))
        self.register_variable(Real("sin_output_tf", causality=Fmi2Causality.output))
        self.register_variable(Real("sin_output_ref", causality=Fmi2Causality.output))

    def do_step(self, current_time, step_size):
        # Similar to model.predict() with less performance overhead
        self.sin_output_tf = self.model(np.array([self.sin_input]), training=False).numpy()[0][0]
        self.sin_output_ref = np.sin([self.sin_input])[0]
        return True
