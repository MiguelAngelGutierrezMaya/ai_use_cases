import supervision as sv

from typing import Any

from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

class ProcessVideo:
    def __init__(self, video_path: str, output_path: str):
        self.video_path = video_path
        self.output_path = output_path
        self.model = RFDETRBase()
    
    def _callback(self, frame: Any, _: int) -> Any:
        detections = self.model.predict(frame, threshold=0.5)
            
        labels = [
            f"{COCO_CLASSES[class_id]} {confidence:.2f}"
            for class_id, confidence
            in zip(detections.class_id, detections.confidence)
        ]

        annotated_frame = frame.copy()
        annotated_frame = sv.BoxAnnotator().annotate(annotated_frame, detections)
        annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels)
        return annotated_frame

    def process(self) -> None:
        sv.process_video(
            source_path=self.video_path,
            target_path=self.output_path,
            callback=self._callback
        )

        print(f"Video processed and saved to {self.output_path}")