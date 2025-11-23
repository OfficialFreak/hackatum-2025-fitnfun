import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLOv8 Pose model (it will download automatically on first run)
model = YOLO('yolov8n-pose.pt')

def calculate_distance(p1, p2):
    """Calculates Euclidean distance between two [x, y] points"""
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p1 - p2)

def calculate_angle(a, b, c):
    """
    Calculates the angle at point 'b' given three points a, b, c.
    Points are expected as [x, y] pairs.
    """
    a = np.array(a) # Start
    b = np.array(b) # Mid (Vertex)
    c = np.array(c) # End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def in_range(actual, target, inaccuracy) -> bool:
    return target - inaccuracy <= actual <= target + inaccuracy

# Start Webcam
cap = cv2.VideoCapture(0)

# Keypoint Indices in YOLO (COCO format):
# 5: Left Shoulder,  7: Left Elbow,  9: Left Wrist
# 6: Right Shoulder, 8: Right Elbow, 10: Right Wrist
# 11: Left Hip,      12: Right Hip

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO inference
    results = model(frame, verbose=False)

    # Visualize the skeleton on the frame automatically
    annotated_frame = results[0].plot()

    # Extract Keypoints
    # results[0].keypoints.xy is a tensor of shape (N_People, 17, 2)
    try:
        keypoints = results[0].keypoints.xy.cpu().numpy()[0] # Get 1st person detected

        # Extract coordinates (x, y)
        # If confidence is low, these might be [0, 0], so ideally check confidence too
        l_shoulder = keypoints[5]
        l_elbow    = keypoints[7]
        l_wrist    = keypoints[9]
        l_hip      = keypoints[11]

        r_shoulder = keypoints[6]
        r_elbow    = keypoints[8]
        r_wrist    = keypoints[10]
        r_hip      = keypoints[12]

        # Calculate Angles
        angle_l_armpit = calculate_angle(l_hip, l_shoulder, l_elbow)
        angle_r_armpit = calculate_angle(r_hip, r_shoulder, r_elbow)

        angle_l_elbow = calculate_angle(l_shoulder, l_elbow, l_wrist)
        angle_r_elbow = calculate_angle(r_shoulder, r_elbow, r_wrist)

        # Check for the seated twist
        is_twisted = (calculate_distance(l_shoulder, r_shoulder) < 100)
        arms_to_the_armrest = in_range(angle_l_armpit, 20, 20) and in_range(angle_l_elbow, 140, 30) and in_range(angle_r_armpit, 10, 20) and in_range(angle_r_elbow, 130, 30)
        # Change direction

        # Shoulder rolls
        sitting_normally = in_range(angle_l_armpit, 30, 20) and in_range(angle_l_elbow, 160, 30) and in_range(angle_r_armpit, 30, 20) and in_range(angle_r_elbow, 160, 30)
        # I guess Schultern anziehen relativ wär nice

        # Seated Crescent Moon Pose
        crescent_moon_pose_left = in_range(angle_l_armpit, 140, 30) and in_range(angle_l_elbow, 120, 40) and in_range(angle_r_armpit, 180, 30) and in_range(angle_r_elbow, 140, 40)
        crescent_moon_pose_right = in_range(angle_l_armpit, 180, 30) and in_range(angle_l_elbow, 160, 40) and in_range(angle_r_armpit, 170, 30) and in_range(angle_r_elbow, 140, 40)

        status_text = f'{"Twisted Seat" if is_twisted and arms_to_the_armrest else ""} {"Shoulder Rolls" if sitting_normally else ""} {"Seated Crescent Moon Pose" if crescent_moon_pose_left or crescent_moon_pose_right else ""}'
        # Optional: Display the angles for debugging
        cv2.putText(annotated_frame, f"L_Armpit: {int(angle_l_armpit)}", (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"L_Elbow: {int(angle_l_elbow)}", (50, 80 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"R_Armpit: {int(angle_r_armpit)}", (50, 80 + 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f"R_Elbow: {int(angle_r_elbow)}", (50, 80 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    except IndexError:
        # No person detected
        pass

    cv2.putText(annotated_frame, status_text or "", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    cv2.imshow('Yoga Move Detection', annotated_frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
