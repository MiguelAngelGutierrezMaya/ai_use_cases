import supervision as sv
from PIL import Image
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

class ProcessImageRfdetr:
    def __init__(self, image_path: str, output_path: str):
        self.image_path = image_path
        self.output_path = output_path
        self.model = RFDETRBase()

    def process(self):
        image = Image.open(self.image_path)
        detections = self.model.predict(image, threshold=0.5)

        labels = [
            f"{COCO_CLASSES[class_id]} {confidence:.2f}"
            for class_id, confidence
            in zip(detections.class_id, detections.confidence)
        ]

        annotated_image = image.copy()
        annotated_image = sv.BoxAnnotator().annotate(annotated_image, detections)
        annotated_image = sv.LabelAnnotator().annotate(annotated_image, detections, labels)
        annotated_image.save(self.output_path)

        print(f"Image processed and saved to {self.output_path}")
