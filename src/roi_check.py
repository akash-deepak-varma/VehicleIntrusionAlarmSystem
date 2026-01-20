import cv2

def is_inside_roi(box, roi_points):
    """
    Checks if the vehicle is inside the designated area.
    box: [x1, y1, x2, y2]
    roi_points: numpy array of polygon coordinates
    """
    # Calculate the bottom-center point of the vehicle bounding box
    center_x = int((box[0] + box[2]) / 2)
    center_y = int(box[3]) 
    
    # Returns 1.0 if inside, 0.0 if on edge, -1.0 if outside
    result = cv2.pointPolygonTest(roi_points, (center_x, center_y), False)
    return result >= 0