import cv2
import numpy as np
import face_recognition
import time
import os
from pygame import mixer
import threading

# Ensure directories exist
if not os.path.exists("captured_images"):
    os.makedirs("captured_images")
if not os.path.exists("sounds"):
    os.makedirs("sounds")
if not os.path.exists("family_faces"):
    os.makedirs("family_faces")
    print("Warning: 'family_faces' directory created but you need to add your family images there")

# Sound paths
PERSON_ALERT_SOUND = "sounds/dog_alarm.mp3"  # Main alert sound for person detection

# Initialize pygame mixer for sound playback
mixer.init()

# Create a default beep sound if sound file doesn't exist
def create_default_beep(filepath):
    if not os.path.exists(filepath):
        try:
            import wave
            import struct
            import math
            
            # Create a simple beep sound file
            sample_rate = 44100
            duration = 1.0  # seconds
            frequency = 440  # Hz (A4 note)
            amplitude = 32767
            num_samples = int(duration * sample_rate)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            wav_file = wave.open(filepath, 'w')
            wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
            
            for i in range(num_samples):
                sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
                packed_sample = struct.pack('h', int(sample))
                wav_file.writeframes(packed_sample)
                
            wav_file.close()
            print(f"Created default sound file: {filepath}")
        except Exception as e:
            print(f"Error creating default sound: {e}")

# Create default alert sound if it doesn't exist
create_default_beep(PERSON_ALERT_SOUND)

# Using the same family members as in your original app.py
known_face_encodings = []
known_face_names = ["Family Member", "Family Member", "Family Member", "Senin","Family Member","Family Member","Family Member"]
family_images = ["family_member_1.jpg", "family_member_2.jpg", "jk.jpg", "SENIN.jpg","SAJIL.jpg","SAJIL2.jpg","SAJIL3.jpg"]

# Load known faces from images
for i, file_name in enumerate(family_images):
    image_path = f"family_faces/{file_name}"
    if not os.path.exists(image_path):
        print(f"Error: File not found - {image_path}")
        continue

    try:
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) > 0:
            known_face_encodings.append(encodings[0])  # Take first encoding
            print(f"Loaded face encoding for {known_face_names[i]}")
        else:
            print(f"Warning: No face found in {file_name}")
    except Exception as e:
        print(f"Error loading face image {file_name}: {e}")

print(f"Total loaded known faces: {len(known_face_encodings)}")

# Set up webcam feed
cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Cooldown variables to prevent continuous alerts
alert_cooldown = 5  # Seconds before a new alert can be triggered
last_alert_time = 0
sound_playing = False

# Function to play alert sound
def play_alert_sound():
    global sound_playing
    sound_playing = True
    try:
        mixer.music.load(PERSON_ALERT_SOUND)
        mixer.music.play()
        print("Playing person detection alert sound")
        # Set a timer to reset the sound_playing flag
        time.sleep(2)  # Allow sound to complete
        sound_playing = False
    except Exception as e:
        print(f"Error playing sound: {e}")
        sound_playing = False

# Main detection loop
print("Starting person detection with sound alerts...")
print("Press 'q' to quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame from camera")
        break

    # Process every other frame to improve performance
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find faces in the frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Loop through each face found in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Scale back up face locations since the frame we detected in was 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # See if the face matches any known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"
        face_detected = False

        if True in matches:
            # Find the index of the first matching known face
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]
            face_detected = True
            color = (0, 255, 0)  # Green for recognized faces
        else:
            color = (0, 0, 255)  # Red for unknown faces

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Play alert sound when a known person is detected
        current_time = time.time()
        if face_detected and current_time - last_alert_time > alert_cooldown and not sound_playing:
            last_alert_time = current_time
            # Use a separate thread for playing sound to avoid blocking the main loop
            sound_thread = threading.Thread(target=play_alert_sound)
            sound_thread.daemon = True
            sound_thread.start()
            
            # Capture image of the detected person
            filename = f"captured_images/person_{int(current_time)}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Person detected: {name}. Image saved as {filename}")

    # Display the resulting image
    cv2.imshow('Person Detection with Sound Alert', frame)

    # Hit 'q' on the keyboard to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all windows
cap.release()
cv2.destroyAllWindows()
print("Program terminated")