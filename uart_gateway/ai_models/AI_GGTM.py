### Google Teachable Machine
from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
import pathlib

class GGTeachableMachineHelper:
    def __init__(self) -> None:
        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        current_file_dir = pathlib.Path(__file__).parent.resolve()

        # Load the model
        self.model = load_model(str(current_file_dir) + "/converted_keras/keras_model.h5", compile=False)

        # Load the labels
        self.class_names = open(str(current_file_dir) + "/converted_keras/labels.txt", "r").readlines()

    def image_detector(self, image):
        # Resize the raw image into (224-height,224-width) pixels
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)

        # Make the image a numpy array and reshape it to the models input shape.
        image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)

        # Normalize the image array
        image = (image / 127.5) - 1

        # Predicts the model
        prediction = self.model.predict(image)
        index = np.argmax(prediction)
        class_name = self.class_names[index]
        #confidence_score = prediction[0][index] #to get confidence score
        return class_name[2:]
