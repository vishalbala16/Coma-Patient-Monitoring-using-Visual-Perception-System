import tkinter as tk
import tkinter as tkk
from tkinter import Message, Text
import pandas as pd       
import tkinter.ttk as ttk
import tkinter.font as font
import tkinter.messagebox as tm
from PIL import Image, ImageTk
from SMS_Utility import send_sms
import cv2
import firebase_handler as fbh
from datetime import datetime
import dlib
import numpy as np
from tensorflow.keras.models import load_model
from mediapipe import solutions as mp

# GUI Constants
bgcolor = "#020f12"
bgcolor1 = "#05d7ff"
fgcolor = "#ffffff"
btnTxt = "#000000"

# Initialize AI Components
class AIComponents:
    def __init__(self):
        self.emotion_detector = None
        self.pose_estimator = None
        self.face_detector = None
        self.landmark_predictor = None
        
    def initialize(self):
        try:
            self.emotion_detector = load_model('emotion_model.h5')
            self.pose_estimator = mp.face_mesh.FaceMesh(
                max_num_faces=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            self.face_detector = dlib.get_frontal_face_detector()
            self.landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
            return True
        except Exception as e:
            print(f"Error initializing AI components: {e}")
            return False

class MonitoringSystem:
    def __init__(self):
        self.ai_components = AIComponents()
        self.activity_log = []
        self.msg_sent = False
        self.alarm_system = AlarmSystem()
        self.alert_cooldown = 60  # seconds between alerts
        self.last_alert_time = 0
        
    def process_frame(self, frame, patient_id, mobile_number):
        if frame is None:
            return frame
            
        current_time = time.time()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.ai_components.face_detector(gray)
        
        alert_status = "Normal"
        
        for face in faces:
            landmarks = self.ai_components.landmark_predictor(gray, face)
            
            # Get face ROI
            x1, y1 = face.left(), face.top()
            x2, y2 = face.right(), face.bottom()
            face_roi = gray[y1:y2, x1:x2]
            
            # Process with AI components
            emotion = self.detect_emotion(face_roi)
            head_pose = self.get_head_pose(frame)
            blink_ratio = self.calculate_blink_ratio(landmarks)
            
            # Record activity
            activity = {
                'timestamp': datetime.now(),
                'emotion': emotion,
                'head_pose': head_pose,
                'blink_ratio': blink_ratio
            }
            self.activity_log.append(activity)
            
            # Check for alerts
            if self.should_alert(activity):
                if not self.msg_sent and (current_time - self.last_alert_time) > self.alert_cooldown:
                    self.send_alert(mobile_number, activity)
                    self.alarm_system.play_alarm()
                    self.last_alert_time = current_time
                    alert_status = "ALERT!"
            
            # Draw information on frame
            cv2.putText(frame, f"Emotion: {emotion}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Blink Ratio: {blink_ratio:.2f}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Status: {alert_status}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, 
                       (0, 0, 255) if alert_status == "ALERT!" else (0, 255, 0), 2)
            
        return frame

    def should_alert(self, activity):
        """
        Determine if an alert should be triggered based on the current activity
        """
        # Example alert conditions
        if activity['emotion'] in ['Fear', 'Distress']:
            return True
        
        if activity['blink_ratio'] > 5.0:  # Prolonged eye closure
            return True
            
        if abs(activity['head_pose'].get('pitch', 0)) > 45:  # Extreme head tilt
            return True
            
        return False

    def send_alert(self, mobile_number, activity):
        """
        Send alert via SMS and trigger alarm
        """
        try:
            message = f"ALERT: Abnormal patient activity detected!\n"
            message += f"Emotion: {activity['emotion']}\n"
            message += f"Blink Ratio: {activity['blink_ratio']:.2f}\n"
            message += f"Time: {activity['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send SMS
            send_sms(mobile_number, message)
            self.msg_sent = True
            
        except Exception as e:
            print(f"Error sending alert: {e}")

    def cleanup(self):
        """
        Cleanup resources when monitoring is stopped
        """
        self.alarm_system.stop_alarm()

def destroyprocess():
    if hasattr(window, 'monitoring_system'):
        window.monitoring_system.cleanup()
    map.release()
    window.destroy()


def Home():
    print("Started")
    global window
    
    monitoring_system = MonitoringSystem()
    window.monitoring_system = monitoring_system  # Store reference for cleanup
    
    window = tk.Tk()
    window.title("Real Time Coma Patient Monitoring Using Visual Perception System")
    window.geometry('1280x720')
    window.configure(background=bgcolor)
    
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)

    frame1 = tk.Frame(window, bg=bgcolor)
    frame1.pack(pady=30, side="bottom", fill="x")

    message1 = tk.Label(window, 
                       text="Real Time Coma Patient Monitoring Using Visual Perception System",
                       bg=bgcolor, fg=fgcolor, width=50, height=3,
                       font=('times', 30, 'bold'))
    message1.pack(pady=5, side="top")

    label = tk.Label(window)
    label.pack(pady=5, expand=True)
    cap = cv2.VideoCapture(0)

    def show_frames():
        global paused, isProcessing
        if not isProcessing and not paused:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                
                # Process frame with AI monitoring system
                if hasattr(window, 'current_patient_id') and hasattr(window, 'current_mobile'):
                    frame = monitoring_system.process_frame(
                        frame, 
                        window.current_patient_id, 
                        window.current_mobile
                    )
                
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                label.imgtk = imgtk
                label.configure(image=imgtk)
        label.after(20, show_frames)

    global started, paused, isProcessing
    started = False
    paused = True
    isProcessing = False

    def preview():
        global started, paused, isProcessing
        isProcessing = False
        paused = not paused
        if not started:
            started = True
            show_frames()

    def monitorprocess():
        monitor_window = tk.Tk()
        monitor_window.title("Monitor Process")
        monitor_window.geometry("300x150")

        def on_submit():
            user_input = entry.get()
            if user_input.strip():
                try:
                    mo_number, partner_name = fbh.fetch_patient_and_spectator_data(str(user_input))
                    if not mo_number:
                        tk.messagebox.showwarning("Input Error", "Please enter a valid ID")
                    else:
                        window.current_patient_id = user_input
                        window.current_mobile = mo_number
                        monitor_window.destroy()
                        global paused
                        paused = False
                        if not started:
                            show_frames()
                except Exception as e:
                    tk.messagebox.showwarning("Error", f"An error occurred: {str(e)}")
            else:
                tk.messagebox.showwarning("Input Error", "Please enter a valid ID")

        label = tk.Label(monitor_window, text="Enter Patient ID:")
        label.pack(pady=10)

        entry = tk.Entry(monitor_window, width=30)
        entry.pack(pady=5)

        submit_button = tk.Button(monitor_window, text="Submit", command=on_submit)
        submit_button.pack(pady=10)

    def destroyprocess():
        cap.release()
        window.destroy()

    browse = tk.Button(frame1, text="Start", command=monitorprocess,
                      fg=btnTxt, bg=bgcolor1, width=26, height=2,
                      activebackground="Red", font=('times', 15, ' bold '))
    browse.pack(padx=10, pady=10, side=tk.LEFT, expand=True)

    quitWindow = tk.Button(frame1, text="Quit", command=destroyprocess,
                          fg=btnTxt, bg=bgcolor1, width=26, height=2,
                          activebackground="Red", font=('times', 15, ' bold '))
    quitWindow.pack(padx=10, pady=10, side=tk.LEFT, expand=True)

    preview_btn = tk.Button(frame1, text="Preview", command=preview,
                           fg=btnTxt, bg=bgcolor1, width=26, height=2,
                           activebackground="Red", font=('times', 15, ' bold '))
    preview_btn.pack(padx=10, pady=10, side=tk.LEFT, expand=True)

    window.mainloop()

if __name__ == "__main__":
    Home()
