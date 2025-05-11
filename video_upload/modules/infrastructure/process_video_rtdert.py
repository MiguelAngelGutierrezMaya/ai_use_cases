#
# Dependencies
#
import torch
import cv2
from PIL import Image
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor


class ProcessVideo:
    def __init__(self, video_path: str, output_path: str):
        #
        # Configure routes and video capture
        #
        self.video_path = video_path
        self.output_path = output_path
        self.cap = cv2.VideoCapture(video_path)

        model_name = "PekingU/rtdetr_r50vd_coco_o365"
        self.image_processor = RTDetrImageProcessor.from_pretrained(model_name)
        self.model = RTDetrForObjectDetection.from_pretrained(model_name)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def process(self):
        #
        # Get video properties
        #
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))

        frame_count = 0
        last_detections = []  # Store last detections

        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            #
            # Process only every n frames
            #
            if frame_count % 1 == 0:
                #
                # Convert the frame to a PIL image
                #
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                #
                # Process the image with RTDetr
                #
                inputs = self.image_processor(images=image, return_tensors="pt").to(self.device)
                with torch.no_grad():
                    outputs = self.model(**inputs)

                results = self.image_processor.post_process_object_detection(outputs,
                                                                             target_sizes=torch.tensor(
                                                                                 [image.size[::-1]]),
                                                                             threshold=0.6)

                #
                # Update last detections
                #
                last_detections = []
                for result in results:
                    for score, label_id, box in zip(result["scores"], result["labels"], result["boxes"]):
                        box = [int(i) for i in box.tolist()]
                        label = self.model.config.id2label[label_id.item()]
                        last_detections.append((box, label, score.item()))

            #
            # Write the last detections on the current frame
            #
            for box, label, score in last_detections:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{label}: {score:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0),
                            2)

            #
            # Write the processed frame to the output file
            #
            out.write(frame)
            frame_count += 1

        self.cap.release()
        out.release()
        print(f"Processed {frame_count} frames and saved to {self.output_path}")
