###Yolo v5s
import torch

class YoloHelper:
    def __init__(self) -> None:
        #Load model
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  

    def yolo_detected_object(self, img):
        #Inference
        results = self.model(img)

        #Results
        #you can see the more information of the result by executing results.print()  # or .show(), .save(), .crop(), .pandas(), etc.
        #results.pandas().xyxy[0] im predictions (pandas)
        names = results.pandas().xyxy[0]['name'].to_numpy()
        return names