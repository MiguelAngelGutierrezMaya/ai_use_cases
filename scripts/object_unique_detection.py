import os
import json

import cv2
import supervision as sv

from datetime import datetime

from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES


# Initialize the model
model = RFDETRBase(pretrain_weights="../rf-detr-base.pth")

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Directory to save the data
output_dir = "object_unique_detection"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# JSON file to save the registry
json_file = os.path.join(output_dir, "registry.json")

# Load the existing registry if it exists
objects_registry = {}
if os.path.exists(json_file):
    with open(json_file, 'r') as f:
        objects_registry = json.load(f)

while True:
    success, frame = cap.read()
    if not success:
        break
    
    # Perform object detection
    detections = model.predict(frame, threshold=0.5)
    
    # Process each detection
    for i, (class_id, confidence, bbox) in enumerate(zip(detections.class_id, detections.confidence, detections.xyxy)):
        # Get the name of the class
        class_name = COCO_CLASSES[class_id]
        
        # Check if it is a unique object (not detected before)
        # or if the current detection has higher confidence
        if class_name not in objects_registry or confidence > objects_registry[class_name]["confidence"]:
            # Extract the region of interest (ROI)
            x1, y1, x2, y2 = map(int, bbox)
            roi = frame[y1:y2, x1:x2]
            
            # Save the cropped image
            img_path = os.path.join(output_dir, f"{class_name}.jpg")
            cv2.imwrite(img_path, roi)
            
            # Update or create registry
            objects_registry[class_name] = {
                "confidence": float(confidence),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "image_path": img_path
            }
            
            # Save the updated registry
            with open(json_file, 'w') as f:
                json.dump(objects_registry, f, indent=4)
            
            print(f"Object updated/saved: {class_name} (Confidence: {confidence:.2f})")
    
    # Create labels for visualization
    labels = [
        f"{COCO_CLASSES[class_id]} {confidence:.2f}"
        for class_id, confidence
        in zip(detections.class_id, detections.confidence)
    ]
    
    # Annotate the frame with detections
    annotated_frame = frame.copy()
    annotated_frame = sv.BoxAnnotator().annotate(annotated_frame, detections)
    annotated_frame = sv.LabelAnnotator().annotate(annotated_frame, detections, labels)
    
    # Show the number of unique objects detected
    cv2.putText(
        annotated_frame, 
        f"Objetos únicos: {len(objects_registry)}", 
        (10, 30), 
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        (0, 255, 0), 
        2
    )
    
    # Show the annotated frame
    cv2.imshow("Webcam", annotated_frame)
    
    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()