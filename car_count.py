import cv2
import numpy as np
import time
import urllib.request
from centroid_tracker import CentroidTracker
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialize Firebase
cred = credentials.Certificate("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/iotproject-e09e8-firebase-adminsdk-9spg3-42a1469f03.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Define the URLs for the video feeds from the IP cameras
url1 = 'http://192.168.205.203/cam-lo.jpg'
url2 = 'http://192.168.205.23/cam-lo.jpg'  # Example URL for second camera
url3 = 'http://192.168.205.46/cam-lo.jpg'  # Example URL for third camera

# Load COCO class names
classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

# Load SSD model
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Define the region of interest (ROI) where cars are allowed for camera 1
roi_x_start_cam1 = 120
roi_y_start_cam1 = 50
roi_width_cam1 = 100
roi_height_cam1 = 90

# Define the region of interest (ROI) where cars are allowed for camera 2
roi_x_start_cam2 = 100
roi_y_start_cam2 = 100
roi_width_cam2 = 100
roi_height_cam2 = 120

# Define the region of interest (ROI) where cars are allowed for camera 3
roi_x_start_cam3 = 120
roi_y_start_cam3 = 40
roi_width_cam3 = 80
roi_height_cam3 = 90

# Initialize CentroidTracker for all cameras
ct1 = CentroidTracker()
ct2 = CentroidTracker()
ct3 = CentroidTracker()

# Set desired FPS
desired_fps = 1000

# Function to get document name based on current time
def get_document_name(current_time):
    if 8 <= current_time.hour < 12:
        return "8am - 11.59am"
    elif 12 <= current_time.hour < 16:
        return "12pm - 3.59pm"
    elif 16 <= current_time.hour < 20:
        return "4pm - 7.59pm"
    elif 20 <= current_time.hour <= 23:
        return "8pm - 11.59pm"
    else:
        return "12am - 7.59am"

while True:
    start_time = time.time()  # Record start time of fetching frame

    # Fetch frame from camera 1
    try:
        imgResponse1 = urllib.request.urlopen(url1)
        imgNp1 = np.array(bytearray(imgResponse1.read()), dtype=np.uint8)
        img1 = cv2.imdecode(imgNp1, -1)
    except Exception as e:
        print(f"Error fetching frame from camera 1: {e}")
        img1 = None

    # Fetch frame from camera 2
    try:
        imgResponse2 = urllib.request.urlopen(url2)
        imgNp2 = np.array(bytearray(imgResponse2.read()), dtype=np.uint8)
        img2 = cv2.imdecode(imgNp2, -1)
    except Exception as e:
        print(f"Error fetching frame from camera 2: {e}")
        img2 = None

    # Fetch frame from camera 3
    try:
        imgResponse3 = urllib.request.urlopen(url3)
        imgNp3 = np.array(bytearray(imgResponse3.read()), dtype=np.uint8)
        img3 = cv2.imdecode(imgNp3, -1)
    except Exception as e:
        print(f"Error fetching frame from camera 3: {e}")
        img3 = None

    if img1 is not None:
        # Detect objects in camera 1 frame
        classIds, confs, bbox = net.detect(img1, confThreshold=0.5)

        # Update tracker with new detections for camera 1
        objects1 = ct1.update(bbox)

        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                class_name = classNames[classId - 1]
                #print(f"Detected in camera 1: {class_name}")  # Commented out printing of class name
                if class_name in ['car', 'boat', 'truck', 'mouse','cup','oven','cell phone']:  # Check if the detected object is a car or boat
                    x, y, w, h = box
                    # Check if the object is within the defined ROI for camera 1
                    if (roi_x_start_cam1 < x < roi_x_start_cam1 + roi_width_cam1) and (roi_y_start_cam1 < y < roi_y_start_cam1 + roi_height_cam1):
                        # Update Firestore with the new count for the left ROI for camera 1
                        current_time = datetime.now()  # Get current timestamp
                        document_name = get_document_name(current_time)
                        doc_ref = db.collection(u'car_count').document(document_name)
                        doc_ref.update({
                            u'opp_road': firestore.Increment(1)
                        })

    if img2 is not None:
        # Detect objects in camera 2 frame
        classIds, confs, bbox = net.detect(img2, confThreshold=0.5)

        # Update tracker with new detections for camera 2
        objects2 = ct2.update(bbox)

        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                class_name = classNames[classId - 1]
                # print(f"Detected in camera 2: {class_name}")  # Commented out printing of class name
                if class_name in ['car', 'boat', 'truck', 'mouse','cup','cell phone']:  # Check if the detected object is a car or boat
                    x, y, w, h = box
                    # Check if the object is within the defined ROI for camera 2
                    if (roi_x_start_cam2 < x < roi_x_start_cam2 + roi_width_cam2) and (roi_y_start_cam2 < y < roi_y_start_cam2 + roi_height_cam2):
                        # Update Firestore with the new count for the left ROI for camera 2
                        current_time = datetime.now()  # Get current timestamp
                        document_name = get_document_name(current_time)
                        doc_ref = db.collection(u'car_count').document(document_name)
                        doc_ref.update({
                            u'main': firestore.Increment(1)
                        })

    if img3 is not None:
        # Detect objects in camera 3 frame
        classIds, confs, bbox = net.detect(img3, confThreshold=0.5)

        # Update tracker with new detections for camera 3
        objects3 = ct3.update(bbox)

        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                class_name = classNames[classId - 1]
                # print(f"Detected in camera 3: {class_name}")  # Commented out printing of class name
                if class_name in ['car', 'boat', 'truck', 'mouse','cup','cell phone']:  # Check if the detected object is a car or boat
                    x, y, w, h = box
                    # Check if the object is within the defined ROI for camera 3
                    if (roi_x_start_cam3 < x < roi_x_start_cam3 + roi_width_cam3) and (roi_y_start_cam3 < y < roi_y_start_cam3 + roi_height_cam3):
                        # Update Firestore with the new count for the "opp road" field for camera 3
                        current_time = datetime.now()  # Get current timestamp
                        document_name = get_document_name(current_time)
                        doc_ref = db.collection(u'car_count').document(document_name)
                        doc_ref.set({
                            u'by': firestore.Increment(1)
                        }, merge=True)  # Merge set to True to create the field if it doesn't exist

    if img1 is not None:
        # Draw the ROI on camera 1 frame
        cv2.rectangle(img1, (roi_x_start_cam1, roi_y_start_cam1), (roi_x_start_cam1 + roi_width_cam1, roi_y_start_cam1 + roi_height_cam1), (0, 255, 0), 2)

        # Display camera 1 frame
        cv2.imshow('Camera 1', img1)

    if img2 is not None:
        # Draw the ROI on camera 2 frame
        cv2.rectangle(img2, (roi_x_start_cam2, roi_y_start_cam2), (roi_x_start_cam2 + roi_width_cam2, roi_y_start_cam2 + roi_height_cam2), (0, 255, 0), 2)

        # Display camera 2 frame
        cv2.imshow('Camera 2', img2)

    if img3 is not None:
        # Draw the ROI on camera 3 frame
        cv2.rectangle(img3, (roi_x_start_cam3, roi_y_start_cam3), (roi_x_start_cam3 + roi_width_cam3, roi_y_start_cam3 + roi_height_cam3), (0, 255, 0), 2)

        # Display camera 3 frame
        cv2.imshow('BY ROAD', img3)

    # Calculate time taken for processing and displaying frame
    time_taken = time.time() - start_time

    # Calculate the time to sleep in order to achieve the desired FPS
    sleep_time = 0.01 - time_taken  # Adjust for 0.5 seconds delay

    # Check if sleep time is positive, if not, set it to 0
    if sleep_time > 0:
        time.sleep(sleep_time)

    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
