import cv2
import time
import supervision as sv
import os

from datetime import datetime
from collections import defaultdict
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

import matplotlib
# Configure matplotlib to not use GUI
import matplotlib.pyplot as plt

matplotlib.use('Agg')

# Configuration of directories
output_dir = "object_specified_detection"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

os.makedirs(os.path.join(output_dir, "detections"), exist_ok=True)
os.makedirs(os.path.join(output_dir, "statistics"), exist_ok=True)

# Define objects of interest with custom configurations
OBJECTS_OF_INTEREST = {
    "remote": {"priority": "medium", "color": (0, 0, 255)},
    "person": {"priority": "high", "color": (255, 165, 0)},
    "book": {"priority": "low", "color": (255, 0, 255)},
}

# Initialize model
model = RFDETRBase(resolution=448, pretrain_weights="../rf-detr-base.pth")

# Initialize webcam
cap = cv2.VideoCapture(0)
box_annotator = sv.BoxAnnotator()

# Variables for statistics and tracking (only for objects of interest)
statistics = {
    "total_detections": defaultdict(int),
    "generated_records": defaultdict(int),
    "average_confidence": defaultdict(list),
    "time_history": [],
    "detection_history": []
}

# Minimum time between records of the same type (in seconds)
time_between_records = 5
last_record = defaultdict(float)

# Utility functions
def register_detection(frame, obj, confidence, bbox):
    """Save a frame with the highlighted detection"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/detections/{obj}_{timestamp}.jpg"

    # Highlight the detected object
    highlighted = frame.copy()
    x1, y1, x2, y2 = [int(c) for c in bbox]
    color = OBJECTS_OF_INTEREST[obj]["color"]
    cv2.rectangle(highlighted, (x1, y1), (x2, y2), color, 4)
    cv2.putText(highlighted, f"{obj} ({confidence:.2f})", (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Add detection information
    info_text = f"Detection: {obj} | Priority: {OBJECTS_OF_INTEREST[obj]['priority'].upper()} | Confidence: {confidence:.2f} | {timestamp}"
    cv2.putText(highlighted, info_text, (10, frame.shape[0]-20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imwrite(filename, highlighted)
    return filename

# Main loop for capture and processing
try:
    prev_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        # Timestamp for this frame
        timestamp = datetime.now()

        # Execute the detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = model.predict(rgb_frame, threshold=0.45)

        # Filtrar solo los objetos de interés
        filtered_indexes = []
        filtered_boxes = []
        filtered_class_ids = []
        filtered_confidences = []
        filtered_labels = []
        filtered_colors = []

        objects_in_scene = defaultdict(int)
        total_objects_of_interest = 0

        # Filter detections to include only objects of interest
        for i, (class_id, confidence, box) in enumerate(zip(
                detections.class_id,
                detections.confidence,
                detections.xyxy)):

            class_name = COCO_CLASSES[class_id]

            # Only process if it is an object of interest
            if class_name in OBJECTS_OF_INTEREST:
                filtered_indexes.append(i)
                filtered_boxes.append(box)
                filtered_class_ids.append(class_id)
                filtered_confidences.append(confidence)

                # Increment the counter for this object
                objects_in_scene[class_name] += 1
                total_objects_of_interest += 1

                # Add to statistics
                statistics["total_detections"][class_name] += 1
                statistics["average_confidence"][class_name].append(float(confidence))

                # Prepare label and color for visualization
                color = OBJECTS_OF_INTEREST[class_name]["color"]
                priority = OBJECTS_OF_INTEREST[class_name]["priority"]
                label = f"{class_name} [{priority.upper()}]"
                filtered_labels.append(label)
                filtered_colors.append(color)

                # Check if we should register this detection
                current_time = time.time()
                if current_time - last_record[class_name] > time_between_records:
                    # Register detection with screenshot
                    detection_image = register_detection(frame, class_name, confidence, box)

                    # Update the time of the last record
                    last_record[class_name] = current_time
                    statistics["generated_records"][class_name] += 1

                    print(f"Object of interest detected: {class_name} - Image saved: {detection_image}")

        # Update history only if there are objects of interest
        if len(filtered_indexes) > 0:
            statistics["time_history"].append(timestamp)
            statistics["detection_history"].append(total_objects_of_interest)

        # Create a clean frame for visualization (without annotations)
        clean_frame = frame.copy()

        # Draw only the filtered objects of interest manually
        for i, (box, label, color) in enumerate(zip(filtered_boxes, filtered_labels, filtered_colors)):
            x1, y1, x2, y2 = [int(c) for c in box]
            # Draw rectangle
            cv2.rectangle(clean_frame, (x1, y1), (x2, y2), color, 2)
            # Add label
            cv2.putText(clean_frame, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Show FPS
        cv2.putText(clean_frame, f"FPS: {fps:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Show only the frame with the detections
        cv2.imshow("Object Monitoring", clean_frame)

        # Exit with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by the user")
finally:
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

    # If no detections, show message and exit
    if not statistics["total_detections"]:
        print("No objects of interest were detected during the session.")
        exit()

    # Save final statistics
    timestamp_final = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Generate summary graph (only objects of interest)
    plt.figure(figsize=(15, 10))

    # Graph 1: Total detections
    plt.subplot(2, 2, 1)
    objects = list(statistics["total_detections"].keys())
    values = list(statistics["total_detections"].values())
    plt.bar(objects, values)
    plt.title('Total Detections of Objects of Interest')
    plt.xticks(rotation=45)

    # Graph 2: Generated records
    plt.subplot(2, 2, 2)
    objects = list(statistics["generated_records"].keys())
    values = list(statistics["generated_records"].values())
    plt.bar(objects, values, color='orange')
    plt.title('Images Registered by Object')
    plt.xticks(rotation=45)

    # Graph 3: Average confidence
    plt.subplot(2, 2, 3)
    objects = []
    values = []
    for obj, confidence in statistics["average_confidence"].items():
        if confidence:
            objects.append(obj)
            values.append(sum(confidence) / len(confidence))
    plt.bar(objects, values, color='green')
    plt.title('Average Confidence by Object')
    plt.xticks(rotation=45)

    # Graph 4: Timeline of detections
    plt.subplot(2, 2, 4)
    plt.plot(statistics["time_history"], statistics["detection_history"])
    plt.title('Objects of Interest Detected Over Time')
    plt.xticks(rotation=45)

    plt.tight_layout()
    # Save the graph without showing it
    plt.savefig(f"{output_dir}/statistics/summary_{timestamp_final}.png")
    plt.close()  # Close the figure after saving it

    print("\n===== SESSION SUMMARY =====")
    
    total_time = 0
    if statistics["time_history"]:
        total_time = (datetime.now() - statistics["time_history"][0]).total_seconds()

    print(f"Total time: {total_time:.2f} seconds")
    print(f"Total objects of interest detected: {sum(statistics['total_detections'].values())}")
    print(f"Total images registered: {sum(statistics['generated_records'].values())}")
    print(f"Objects of interest detected:")

    for obj, count in sorted(statistics["total_detections"].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {obj}: {count} times")

    print(f"\nReport saved in: {output_dir}statistics/summary_{timestamp_final}.png")
    print(f"Images saved in: detections/")