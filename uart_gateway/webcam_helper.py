import cv2  # Install opencv-python

class WebcamHelper: 
    def __init__(self, default_webcam: int = 0) -> None:
        self.default_webcam = default_webcam

        #CAMERA can be 0 or 1 based on default camera of your computer
        self.camera = cv2.VideoCapture(self.default_webcam)

    def get_webcam_image(self):
        ret, img = self.camera.read()
        return img