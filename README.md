# Coma-Patient-Monitoring-using-Visual-Perception-System
This project is an AI-powered, non-invasive solution designed to continuously monitor coma patients using a visual perception system. It leverages computer vision and facial landmark detection to identify subtle physical indicators of consciousness, such as eye blinking and lip movement—key signs of neurological activity.
This project presents an intelligent, non-invasive system to monitor coma patients in real time using advanced computer vision techniques. Built with Python, OpenCV, Dlib, and integrated with facial landmark detection, the system captures subtle signs of neurological activity such as eye blinking, lip movement, and facial expressions to assess the consciousness level of coma patients.

🚀 Features |📷 Real-time video processing using OpenCV👁️ Facial feature tracking using Haar Cascade and Dlib | 🧠 Detection of micro-movements (eye blinks, lip movement) indicating neurological responses
| 🔔 Automated alert system (SMS/Alarm) to notify doctors and caregivers | 💻 GUI built with Tkinter for easy interaction | 🧪 Advanced image preprocessing using Gaussian Blur to reduce noise | 🗄️ MySQL backend for patient data storage and access

💡 Technologies Used
*Python 3.6+
*OpenCV
*Dlib
*Tkinter
*NumPy
*Twilio API (for alerts)
*MySQL

📚 Project Objectives
*Enable continuous, automated monitoring of coma patients.
*Eliminate the need for invasive sensors.
*Alert caregivers and family members in case of spontaneous patient activity.
*Provide a user-friendly interface for medical staff.

📸 Sample Use Cases
*ICU rooms where constant patient monitoring is critical.
*Remote health monitoring setups with minimal human intervention.
*Supplementary tool for assessing patient recovery progress.

🛠️ Step-by-Step Implementation Guide
📁 1. Setup Your Development Environment
🔧 Software Requirements
*Python 3.6+
*MySQL Server
*PyCharm or VSCode (IDE)

Required Python Libraries:
pip install opencv-python dlib imutils numpy playsound twilio pillow

📷 2. Prepare Hardware
*A computer or laptop with:
*Webcam (built-in or external)
*Minimum 8GB RAM and Intel i5 processor
*Stable Internet (for Twilio API to send SMS)

🧠 3. Project Structure
Create the following folders and files:

coma-monitoring/
├── main.py                # Main GUI file
├── monitor.py             # Video processing & detection logic
├── shape_predictor_68_face_landmarks.dat
├── testsms.py             # Twilio SMS alert script
├── requirements.txt
└── README.md

🧩 4. Implement Core Modules
a. Facial Movement Detection
*Use OpenCV & Dlib to:
*Detect face using Haar Cascade
*Track facial landmarks
*Measure blinking (eye aspect ratio)
*Detect mouth movement via pixel difference

b. Gaussian Blur
*Apply to reduce image noise for more accurate detection:
*blurred = cv2.GaussianBlur(frame, (5, 5), 0)

c. Alert System (Twilio API)
*Setup Twilio account
*Use twilio.rest.Client to send SMS:
*from twilio.rest import Client
*client = Client("ACCOUNT_SID", "AUTH_TOKEN")
*client.messages.create(
    to="+91xxxxxxxxxx",
    from_="Your_Twilio_Number",
    body="Alert! Movement detected in coma patient.")
    
💻 5. Create GUI (Tkinter)
*Design start/stop buttons
*Show real-time camera feed
*Display patient ID and monitoring status

🗄️ 6. Connect to MySQL Database
*Create a table to store patient IDs and timestamp of activity.
*Use mysql-connector-python to insert logs:

import mysql.connector
conn = mysql.connector.connect(user='root', password='password', ...)
cursor = conn.cursor()
cursor.execute("INSERT INTO activity_log (...) VALUES (...)")

🧪 7. Test the System
*Unit test each module (detection, alerts, GUI)
*Use sample videos or simulate facial movement
*Perform real-time testing using a webcam

🚨 8. Deploy and Monitor
*Run main.py to launch the system
*Use in a controlled environment like a demo ICU setup
*Ensure alert delivery and logging works correctly
