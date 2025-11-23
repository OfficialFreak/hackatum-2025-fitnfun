import cv2
import numpy as np
import time
from ultralytics import YOLO

# --- 1. The State Management Class ---
class PoseTracker:
    def __init__(self, name, target_duration=10):
        self.name = name
        self.target_duration = target_duration # Seconds to hold
        self.start_time = None
        self.last_seen_time = 0
        self.completed = False

        # "Chill" factor: How long (seconds) allowed to "lose" the pose
        # before resetting the timer. Handles flickering.
        self.grace_period = 2.0

    def update(self, is_detected):
        current_time = time.time()

        if is_detected:
            self.last_seen_time = current_time
            if self.start_time is None:
                self.start_time = current_time # Start the timer
                self.completed = False
        else:
            # If we haven't seen the pose for longer than the grace period, reset.
            if self.start_time is not None and (current_time - self.last_seen_time > self.grace_period):
                self.start_time = None # Reset timer

        return self.get_status(current_time)

    def get_status(self, current_time):
        if self.completed:
            return f"{self.name}: DONE!", (0, 255, 0) # Green

        if self.start_time is not None:
            elapsed = current_time - self.start_time
            remaining = max(0, self.target_duration - elapsed)

            if remaining == 0:
                self.completed = True
                return f"{self.name}: DONE!", (0, 255, 0)

            # Display countdown
            return f"{self.name}: {int(remaining)}s", (0, 255, 255) # Yellow/Orange

        return f"Waiting for {self.name}...", (100, 100, 100) # Grey

# --- 2. Math Helpers ---
def calculate_distance(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)
    return np.linalg.norm(p1 - p2)

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360 - angle
    return angle

def in_range(actual, target, inaccuracy) -> bool:
    return target - inaccuracy <= actual <= target + inaccuracy

# --- 3. Setup ---
model = YOLO('yolov8n-pose.pt')
cap = cv2.VideoCapture(0)

# Initialize trackers for the specific moves you want to count
tracker_twist = PoseTracker("Seated Twist", target_duration=120)
tracker_moon_l = PoseTracker("Left Crescent", target_duration=15)
tracker_moon_r = PoseTracker("Right Crescent", target_duration=15)
tracker_rolls  = PoseTracker("Shoulder Rolls", target_duration=20)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO
    results = model(frame, verbose=False)
    annotated_frame = frame

    try:
        # Get Keypoints
        k = results[0].keypoints.xy.cpu().numpy()[0]

        # Map Keypoints (Indices based on COCO)
        # 5:L_Shldr, 7:L_Elbow, 9:L_Wrist, 11:L_Hip
        # 6:R_Shldr, 8:R_Elbow, 10:R_Wrist, 12:R_Hip

        l_sh, l_el, l_wr, l_hi = k[5], k[7], k[9], k[11]
        r_sh, r_el, r_wr, r_hi = k[6], k[8], k[10], k[12]

        # Calculate Angles
        ang_l_armpit = calculate_angle(l_hi, l_sh, l_el)
        ang_r_armpit = calculate_angle(r_hi, r_sh, r_el)
        ang_l_elbow  = calculate_angle(l_sh, l_el, l_wr)
        ang_r_elbow  = calculate_angle(r_sh, r_el, r_wr)

        # --- DETECT SPECIFIC POSES (Your Logic) ---

        # 1. Twisted Seat
        # Logic: Shoulders close + specific arm angles
        is_twisted_pose = (calculate_distance(l_sh, r_sh) < 100) and \
                          in_range(ang_l_armpit, 20, 20) and in_range(ang_l_elbow, 140, 30) and \
                          in_range(ang_r_armpit, 10, 20) and in_range(ang_r_elbow, 130, 30)

        # 2. Shoulder Rolls (Sitting Normally)
        # Logic: Arms roughly down/relaxed
        is_rolling_pose = in_range(ang_l_armpit, 30, 20) and in_range(ang_l_elbow, 160, 30) and \
                          in_range(ang_r_armpit, 30, 20) and in_range(ang_r_elbow, 160, 30)

        # 3. Crescent Moon (Left)
        is_moon_l = in_range(ang_l_armpit, 140, 30) and in_range(ang_l_elbow, 120, 40) and \
                    in_range(ang_r_armpit, 180, 30) and in_range(ang_r_elbow, 140, 40)

        # 4. Crescent Moon (Right)
        is_moon_r = in_range(ang_l_armpit, 180, 30) and in_range(ang_l_elbow, 160, 40) and \
                    in_range(ang_r_armpit, 170, 30) and in_range(ang_r_elbow, 140, 40)

        # --- UPDATE TIMERS ---
        # We update ALL trackers every frame.
        # If the pose is detected, it counts down. If not, it waits/resets.

        text_twist, col_twist = tracker_twist.update(is_twisted_pose)
        text_roll, col_roll   = tracker_rolls.update(is_rolling_pose)
        text_moon_l, col_moon_l = tracker_moon_l.update(is_moon_l)
        text_moon_r, col_moon_r = tracker_moon_r.update(is_moon_r)

        # --- DISPLAY UI ---
        # We stack the text so we can see all statuses
        y_pos = 50
        line_height = 40

        # Only show the ones that are Active or Done (to keep screen clean)
        # Or show all if you prefer debugging
        ui_items = [
            (text_twist, col_twist, tracker_twist),
            (text_roll, col_roll, tracker_rolls),
            (text_moon_l, col_moon_l, tracker_moon_l),
            (text_moon_r, col_moon_r, tracker_moon_r)
        ]

        for text, color, tracker_obj in ui_items:
            # Show if active (timer running) OR completed OR recently active
            if tracker_obj.start_time is not None or tracker_obj.completed:
                cv2.putText(annotated_frame, text, (30, y_pos),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                y_pos += line_height

    except Exception as e:
        print(f"Error: {e}")
        pass

    cv2.imshow('Yoga Trainer', annotated_frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
