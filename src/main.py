import cv2
import os
import numpy as np
from alerting import send_email_alert
from roi_check import is_inside_roi
from utils import select_roi_dynamically, draw_roi_and_alerts
from ultralytics import YOLO
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# CONFIGURATION
VIDEO_PATH = os.getenv("VIDEOFILE")
MODEL_PATH = r"models\finetune.pt"
VEHICLE_CLASSES = [2, 3, 5, 7]  
RUN_REALTIME = False 

TRACKING_MODE = True 

def run_system():
    source = 0 if RUN_REALTIME else VIDEO_PATH
    ROI_POINTS = select_roi_dynamically(source)

    if ROI_POINTS is None:
        print("No ROI selected. Exiting.")
        return

    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(source)
    
    # Tracking state
    ALREADY_ALERTED_IDS = set()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draw_roi_and_alerts(frame, ROI_POINTS)
        
        if TRACKING_MODE:
            # --- TRACKING-BASED ALARM LOGIC ---
            results = model.track(frame, persist=True, verbose=False)
            for r in results:
                if r.boxes is None or r.boxes.id is None: continue
                
                boxes = r.boxes.xyxy.cpu().numpy()
                track_ids = r.boxes.id.int().cpu().numpy()
                class_ids = r.boxes.cls.int().cpu().numpy()

                for box, track_id, cls_id in zip(boxes, track_ids, class_ids):
                    if cls_id in VEHICLE_CLASSES and is_inside_roi(box, ROI_POINTS):
                        if track_id not in ALREADY_ALERTED_IDS:
                            send_email_alert(frame=frame, timestamp=f"ID_{track_id}_{timestamp}")
                            ALREADY_ALERTED_IDS.add(track_id)
                        draw_roi_and_alerts(frame, ROI_POINTS, box, f"ID:{track_id}")
        
        else:
            # --- TIME-BASED ALARM LOGIC (As before) ---
            results = model.predict(frame, verbose=False)
            alert_triggered = False
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    if cls_id in VEHICLE_CLASSES:
                        coords = map(int, box.xyxy[0])
                        x1, y1, x2, y2 = coords
                        if is_inside_roi([x1, y1, x2, y2], ROI_POINTS):
                            alert_triggered = True
                            draw_roi_and_alerts(frame, ROI_POINTS, [x1, y1, x2, y2], cls_id)
            
            if alert_triggered:
                # Note: send_email_alert already has the cooldown logic internally
                send_email_alert(frame=frame, timestamp=timestamp)

        cv2.imshow("Vehicle Monitoring System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_system()