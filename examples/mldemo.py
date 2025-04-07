from pythonfmu import Fmi2Causality, Fmi2Slave, Real

import pathlib  # pathlib is included in the Python Standard Library

try:
    import tensorflow as tf
    import numpy as np
except ImportError: # Trick to be able to generate the FMU without TensorFlow and NumPy installed
    np, tf = None, None


class MLDemo(Fmi2Slave):
    author = "Magnus Steinstø"
    description = "Limited range TensorFlow sin approximation"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Import Tensorflow model directory created by model.save(["stored-model"])
        parent_path = pathlib.Path(__file__).parent
        # Check if building or initializing
        if parent_path.name == "resources":
            # __init__ called from within FMU (probably)
            # Path relative to "resources" directory root within the FMU
            model_dir_path = parent_path / "stored-model.keras"
            if model_dir_path.exists():
                try:
                    # Fetch saved model from directory included in the FMU
                    self.model = tf.keras.models.load_model(model_dir_path)
                except AttributeError:
                    print("Unable to load model from directory. Has TensorFlow been included in the environment?")
                except OSError:
                    print("Unable to load model from directory. Has the correct directory been specified?")
            else:
                print("No model directory found. Has the directory been included in the FMU when building?")

        self.sin_input = 0.
        self.sin_output_tf = 0.
        self.sin_output_ref = 0.

        self.register_variable(Real("sin_input", causality=Fmi2Causality.input))
        self.register_variable(Real("sin_output_tf", causality=Fmi2Causality.output))
        self.register_variable(Real("sin_output_ref", causality=Fmi2Causality.output))

    def do_step(self, current_time, step_size):
        # Similar to model.predict() with less performance overhead
        self.sin_output_tf = self.model(np.array([self.sin_input]), training=False).numpy()[0][0]
        self.sin_output_ref = np.sin([self.sin_input])[0]
        return True
