import os
import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO
from pygame import mixer
import requests
import json
from pymongo import MongoClient
from datetime import datetime

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")  # Connect to MongoDB server
db = client["animal_detection"]  # Database name
alerts_collection = db["alerts"]  # Collection for storing alerts

# Telegram Bot Configuration
BOT_TOKEN = "7726687998:AAHHkM8x8bwo3PDsw7Of1jCHeSZGBORn0q8"  # Your bot token
CHAT_ID = "812723861"  # Your chat ID (Group ID)

CONTROL_SERVER_URL = "http://127.0.0.1:5001"  # Control server URL

def send_telegram_alert(image_path, chat_id, token, message):
    """Send image and message via Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(image_path, "rb") as photo:
        payload = {"chat_id": chat_id, "caption": message}
        files = {"photo": photo}
        response = requests.post(url, data=payload, files=files)
        return response.json()

def send_alert_to_server(alert_message, image_path, alarm_type=None):
    """Send alert to the control server and save to MongoDB."""
    url = f"{CONTROL_SERVER_URL}/add_alert"
    data = {
        "alert_message": alert_message,
        "image_path": image_path,
        "alarm_type": alarm_type
    }
    try:
        response = requests.post(url, json=data)
        # Add logging for the response
        print(f"Server Response: {response.status_code} - {response.text}")
        if response.status_code == 201:
            print("Alert sent successfully to control server!")
        else:
            print(f"Failed to send alert to control server: {response.json()}")
    except Exception as e:
        print(f"Error sending alert to server: {e}")

    # Store alert in MongoDB
    alert_data = {
        "alert_message": alert_message,
        "image_path": image_path,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Add timestamp
        "alarm_type": alarm_type
    }
    try:
        alerts_collection.insert_one(alert_data)  # Insert alert data into MongoDB
        print("Alert stored in MongoDB!")
    except Exception as e:
        print(f"Error storing alert in MongoDB: {e}")
    
    # Send alert to the control server (if needed)
    url = f"{CONTROL_SERVER_URL}/add_alert"
    data = {
        "alert_message": alert_message,
        "image_path": image_path,
         "alarm_type": alarm_type
    }
    try:
        response = requests.post(url, json=data)
        if response.status_code == 201:
            print("Alert sent successfully to control server!")
        else:
            print(f"Failed to send alert to control server: {response.json()}")
    except Exception as e:
        print(f"Error sending alert to server: {e}")

# Initialize pygame mixer
mixer.init()

# Alarm sound paths
DOG_ALARM_PATH = "sounds/dog_alarm.mp3"
CAT_ALARM_PATH = "sounds/cat_alarm.mp3"
ELE_ALARM_PATH = "sounds/elephant_alarm.mp3"

# Alarm control state
if "is_alarm_playing" not in st.session_state:
    st.session_state.is_alarm_playing = False

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

def play_alarm(sound_file):
    """Play the alarm sound if not already playing."""
    if not st.session_state.is_alarm_playing:
        try:
            mixer.music.load(sound_file)
            mixer.music.play(loops=-1)  # Loop the alarm until stopped
            st.session_state.is_alarm_playing = True
        except Exception as e:
            st.error(f"Error playing sound: {e}")

def stop_alarm():
    """Stop the alarm sound if it is playing."""
    if st.session_state.is_alarm_playing:
        try:
            mixer.music.stop()
            st.session_state.is_alarm_playing = False
            st.success("Alarm stopped.")
        except Exception as e:
            st.error(f"Error stopping sound: {e}")
    else:
        st.warning("No alarm is playing!")

# Streamlit UI
st.title("Animal Detection System with Alerts")
uploaded_file = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Save uploaded file locally
    image_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Load the image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Perform detection
    results = model.predict(image_rgb, conf=0.5)

    # Draw bounding boxes
    dog_detected = False
    cat_detected = False
    elephant_detected = False
    for result in results[0].boxes:
        cls = int(result.cls[0])
        conf = float(result.conf[0])
        label = results[0].names[cls]
        x1, y1, x2, y2 = map(int, result.xyxy[0])
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(image, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Actions for specific animals
        if label.lower() == "dog" and conf > 0.5:
            dog_detected = True
        elif label.lower() == "cat" and conf > 0.3:
            cat_detected = True
        elif label.lower() == "elephant" and conf > 0.3:
            elephant_detected = True

    # Save annotated image
    annotated_path = os.path.join("uploads", f"annotated_{uploaded_file.name}")
    cv2.imwrite(annotated_path, image)

    # Get the absolute path
    abs_annotated_path = os.path.abspath(annotated_path)  # Change is here

    # Send alert and play alarms
    if dog_detected:
        st.warning("⚠️ Warning: Dog detected!")
        send_telegram_alert(abs_annotated_path, CHAT_ID, BOT_TOKEN, "Warning: Dog detected!")
        send_alert_to_server("⚠️ Warning: Dog detected!", abs_annotated_path, "dog")
        # play_alarm(DOG_ALARM_PATH)  # Remove local play alarm

    if cat_detected:
        st.error("🚨 Alert: Cat detected!")
        send_telegram_alert(abs_annotated_path, CHAT_ID, BOT_TOKEN, "Alert: Cat detected!")
        send_alert_to_server("🚨 Alert: Cat detected!", abs_annotated_path, "cat")
        # play_alarm(CAT_ALARM_PATH) # Remove local play alarm

    if elephant_detected:
        st.error("🚨 Alert: Elephant detected!")
        send_telegram_alert(abs_annotated_path, CHAT_ID, BOT_TOKEN, "Alert: Elephant detected!")
        send_alert_to_server("🚨 Alert: Elephant detected!", abs_annotated_path, "elephant")
        # play_alarm(ELE_ALARM_PATH) # Remove local play alarm

    # Display annotated image
    st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Detection Results", use_container_width=True)

    # Stop alarm button
    stop_alarm_button = st.button("Stop Alarm")
    if stop_alarm_button:
        stop_alarm()

else:
    st.write("Please upload an image.")