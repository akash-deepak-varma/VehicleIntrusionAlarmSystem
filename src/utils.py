import cv2
import numpy as np

def draw_roi_and_alerts(frame, roi_points, box=None, vehicle_id=None):
    # Always draw the yellow ROI boundary
    cv2.polylines(frame, [roi_points], isClosed=True, color=(0, 255, 255), thickness=2)
    
    if box is not None:
        x1, y1, x2, y2 = map(int, box)
        # Draw red alert box if vehicle is in ROI
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.putText(frame, f"ALARM: Vehicle {vehicle_id}", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
def select_roi_dynamically(video_path):
    """
    Opens a window to let the user click points to define an ROI.
    Press 'r' to reset, 'q' to confirm.
    """
    points = []
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read video for ROI selection.")
        return None

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(frame_copy, (x, y), 5, (0, 255, 255), -1)
            if len(points) > 1:
                cv2.line(frame_copy, points[-2], points[-1], (0, 255, 255), 2)
            cv2.imshow("Select ROI - Press 'q' to confirm, 'r' to reset", frame_copy)

    frame_copy = frame.copy()
    cv2.namedWindow("Select ROI - Press 'q' to confirm, 'r' to reset")
    cv2.setMouseCallback("Select ROI - Press 'q' to confirm, 'r' to reset", mouse_callback)

    while True:
        cv2.imshow("Select ROI - Press 'q' to confirm, 'r' to reset", frame_copy)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            points = []
            frame_copy = frame.copy()

    cv2.destroyAllWindows()
    cap.release()
    return np.array(points, np.int32) if len(points) > 2 else None