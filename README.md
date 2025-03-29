# Intruder-Detection
This project uses AI-driven face and animal detection to identify intruders in real-time. Implemented with CNNs, YOLO, and Grassmann’s algorithm, it alerts users via Telegram and triggers emergency alarms. Features include facial recognition, motion detection, night vision, and automated responses for enhanced security.
Intruder Detection System

Overview

The Intruder Detection System is an AI-powered security solution that uses advanced computer vision techniques to identify intruders and unwanted animals in real time. By leveraging Convolutional Neural Networks (CNNs), YOLO object detection, and Grassmann’s algorithm, the system provides accurate facial and animal recognition. It sends real-time alerts via Telegram and triggers emergency alarms, ensuring quick responses to potential threats.

Features

Real-Time Intruder Detection: Identifies unauthorized persons using facial recognition.

Animal Detection: Differentiates between harmful and harmless animals.

YOLO Object Detection: Accurately detects and classifies objects, intruders, and vehicles.

Instant Notifications: Sends real-time alerts via the Telegram app.

Behavior Monitoring: Detects suspicious activities such as loitering.

Night Vision Support: Ensures efficient operation even in low-light conditions.

Automated Response System: Triggers alarms and can integrate with smart home security systems.

Customizable Alerts: Users can configure notification settings as per their preferences.


Technology Stack

Programming Language: Python

Machine Learning Libraries: TensorFlow, PyTorch, Scikit-learn

Computer Vision: OpenCV, YOLOv5

Data Handling: Pandas, NumPy

Messaging & Alerts: Telegram API


Methodology

1. Data Capture: Cameras and sensors collect live video and motion data.


2. Object & Facial Detection: The system uses YOLO and CNNs to recognize faces and objects.


3. Intruder Identification: Grassmann’s algorithm determines if a person is familiar or an intruder.


4. Alert Generation: When a threat is detected, alerts are sent via Telegram, and alarms are triggered.


5. Continuous Learning: AI models improve over time with new data and user feedback.



Limitations & Future Enhancements

Accuracy may drop in low-light conditions.

Detection range is limited based on camera placement.

Future improvements include high-resolution cameras, infrared sensors, and multi-angle training data.
