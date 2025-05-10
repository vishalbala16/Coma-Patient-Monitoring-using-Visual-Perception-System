# -*- coding: utf-8 -*-
from datetime import datetime
from threading import Thread
import cv2
import dlib
import imutils
import numpy as np
import pandas as pd
import saccademodel
from imutils import face_utils
from numpy.ma import hypot
from PIL import Image, ImageTk
from Media_Player import play_alarm
from SMS_Utility import send_sms
import firebase_handler as fbh
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import tensorflow as tf
from mediapipe import solutions as mp

# Global variables
global cap
motion_list = [None, None]
time_list = []
df_list = []
patient_id = 0
mobile_number = "9336674149"
patient_name = "sri"

class EmotionDetector:
    def __init__(self):
        self.emotion_model = load_model('emotion_model.h5')
        self.emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

    def detect_emotion(self, face_roi):
        roi = cv2.resize(face_roi, (48, 48))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        preds = self.emotion_model.predict(roi)[0]
        emotion = self.emotions[preds.argmax()]
        return emotion, preds.max()

class PoseEstimator:
    def __init__(self):
        self.mp_face_mesh = mp.face_mesh.FaceMesh(
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def get_head_pose(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.mp_face_mesh.process(frame_rgb)
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]
            return self.calculate_pose_angles(face_landmarks)
        return None

    def calculate_pose_angles(self, landmarks):
        # Implement pose angle calculation logic
        # Returns pitch, yaw, roll angles
        return {'pitch': 0, 'yaw': 0, 'roll': 0}  # Placeholder

class PatientMonitoringAnalytics:
    def __init__(self):
        self.db = fbh.get_database()
        
    def log_activity(self, patient_id, activity_data):
        self.db.child(f"patients/{patient_id}/activity").push(activity_data)
        
    def analyze_trends(self, patient_id, timeframe_hours=24):
        activities = self.db.child(f"patients/{patient_id}/activity").get()
        df = pd.DataFrame(activities)
        
        metrics = {
            'avg_blink_rate': df['blink_ratio'].mean(),
            'emotion_distribution': df['emotion'].value_counts().to_dict(),
            'movement_patterns': self.analyze_movement_patterns(df),
            'alert_frequency': len(df[df['alert_triggered'] == True])
        }
        return metrics

    def analyze_movement_patterns(self, df):
        # Implement movement pattern analysis
        return {}

def should_trigger_alert(activity_log, window_size=30):
    if len(activity_log) < window_size:
        return False
        
    recent_activity = activity_log[-window_size:]
    prolonged_no_movement = all(not a['speaking'] for a in recent_activity)
    abnormal_blink_pattern = analyze_blink_pattern(recent_activity)
    distressed_emotion = any(a['emotion'] in ['Fear', 'Distress'] and a['emotion_confidence'] > 0.8 
                           for a in recent_activity)
    
    return prolonged_no_movement or abnormal_blink_pattern or distressed_emotion

def analyze_blink_pattern(activity_log):
    blink_ratios = [a['blink_ratio'] for a in activity_log]
    mean_ratio = np.mean(blink_ratios)
    std_ratio = np.std(blink_ratios)
    return mean_ratio > 5.0 or std_ratio > 2.0

def process(id:int, mo_number, p_name:str):
    global patient_id, mobile_number, patient_name
    patient_name = p_name
    patient_id = id
    mobile_number = mo_number

    global df_list, motion_list, msg_sent
    msg_sent = False

    # Initialize detectors and predictors
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    emotion_detector = EmotionDetector()
    pose_estimator = PoseEstimator()
    analytics = PatientMonitoringAnalytics()

    # Constants
    FRAMES_TO_PERSIST = 5
    MIN_SIZE_FOR_MOVEMENT = 500
    MOVEMENT_DETECTED_PERSISTENCE = 100
    
    # Flags
    sflag = False
    ebflag = False
    mflag = False

    def is_speaking(prev_img, curr_img, debug=False, threshold=700, width=800, height=800):
        prev_img = cv2.resize(prev_img, (width, height))
        curr_img = cv2.resize(curr_img, (width, height))
        diff = cv2.absdiff(prev_img, curr_img)
        norm = np.sum(diff) / (width * height) * 100
        return norm > threshold

    def midpoint(p1, p2):
        return int((p1.x + p2.x) / 2), int((p1.y + p2.y) / 2)

    def get_blinking_ratio(eye_points, facial_landmarks):
        left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
        right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
        center_top = midpoint(facial_landmarks.part(eye_points[1]),
                            facial_landmarks.part(eye_points[2]))
        center_bottom = midpoint(facial_landmarks.part(eye_points[5]),
                               facial_landmarks.part(eye_points[4]))
        
        hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
        ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)
        
        hor_line_length = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
        ver_line_length = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))
        
        ratio = hor_line_length / ver_line_length
        return ratio

    # Initialize camera
    cap = cv2.VideoCapture(0)
    cap.release()
    cap = cv2.VideoCapture(0)
    
    # Set camera resolution
    desired_width = 1040
    desired_height = 480
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_height)

    # Initialize variables
    first_frame = None
    next_frame = None
    font = cv2.FONT_HERSHEY_SIMPLEX
    delay_counter = 0
    movement_persistent_counter = 0
    prev_mouth_img = None
    activity_log = []

    while True:
        ret, frame = cap.read()
        if not ret:
            print("CAPTURE ERROR")
            continue

        frame = imutils.resize(frame, width=750)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            # Get face landmarks
            landmarks = predictor(gray, face)
            
            # Get face ROI
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()
            face_roi = gray[y1:y2, x1:x2]

            # Detect emotion
            emotion, confidence = emotion_detector.detect_emotion(face_roi)
            
            # Get head pose
            head_pose = pose_estimator.get_head_pose(frame)
            
            # Get blink ratio
            left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
            right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
            blink_ratio = (left_eye_ratio + right_eye_ratio) / 2

            # Check for eye blinking
            if blink_ratio > 4.7:
                ebflag = True
                cv2.putText(frame, "EYE BLINKING", (50, 150), 1, 5, (0, 0, 0), 2)

            # Record activity
            activity = {
                'timestamp': datetime.now(),
                'emotion': emotion,
                'emotion_confidence': confidence,
                'head_pose': head_pose,
                'blink_ratio': blink_ratio,
                'speaking': sflag,
                'alert_triggered': False
            }
            activity_log.append(activity)
            
            # Check for alerts
            if should_trigger_alert(activity_log):
                if not msg_sent:
                    alert_message = f"Alert: Abnormal activity detected for patient {patient_name}"
                    send_sms(mobile_number, alert_message)
                    play_alarm()
                    msg_sent = True
                    activity['alert_triggered'] = True

            # Log activity to database
            analytics.log_activity(patient_id, activity)

            # Display information
            cv2.putText(frame, f"Emotion: {emotion}", (10, 30), font, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Blink Ratio: {blink_ratio:.2f}", (10, 60), font, 0.7, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Patient Monitoring", frame)

        # Break loop on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    process(1, "9336674149", "Patient1")
