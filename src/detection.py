import cv2
import os
from datetime import datetime
from alerting import send_email_alert

VIDEO_PATH = r"C:\Users\surya\Downloads\WhatsApp Video 2026-01-05 at 15.10.02.mp4"
SNAPSHOT_DIR = r"snapshots"
VEHICLE_CLASSES = [2, 3, 5, 7]  
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

RUN_REALTIME = False   


try:
    from ultralytics import YOLO
except ImportError:
    print("Please install ultralytics: pip install ultralytics")
    exit()

model = YOLO(r"models\finetune.pt") 

cap = cv2.VideoCapture(1 if RUN_REALTIME else VIDEO_PATH)
frame_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    
    results = model.predict(frame, verbose=False)

    vehicles_detected = False

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls[0])
            if class_id in VEHICLE_CLASSES:
                vehicles_detected = True
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, f"Vehicle {class_id}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
    if vehicles_detected:
        send_email_alert(
        frame=frame,
        timestamp=timestamp
    )

    
    cv2.imshow("Vehicle Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

