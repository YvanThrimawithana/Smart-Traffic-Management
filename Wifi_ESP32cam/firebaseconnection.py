import cv2
import numpy as np
import time
import firebase_admin
from firebase_admin import credentials, db
from centroid_tracker import CentroidTracker
import ssl
import urllib.request

# URL for the video feed from the IP webcam app on your phone
url = 'http://192.168.1.11/cam-hi.jpg'

# Initialize Firebase Admin SDK
cred = credentials.Certificate("C:/Users/yvant/Downloads/iotproject-e09e8-firebase-adminsdk-9spg3-42a1469f03.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://iotproject-e09e8-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

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

# Define the region of interest (ROI) where cars are allowed
roi_x_start = 280  # Adjust this value based on your specific case
roi_y_start = 200  # Adjust this value based on your specific case
roi_width = 350    # Adjust this value based on your specific case
roi_height = 280   # Adjust this value based on your specific case

# Initialize CentroidTracker
ct = CentroidTracker()

# Set desired FPS
desired_fps = 10

# Function to update count for 8-12pm
def update_count(count):
    ref = db.reference('8-12pm/count')  # Reference to the count node under 8-12pm
    ref.set(count)

car_count_8_12pm = 0  # Initialize count for 8-12pm

# Create an SSL context with certificate verification disabled
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

while True:
    start_time = time.time()  # Record start time of fetching frame
    
    # Use the custom SSL context when making the request to bypass certificate verification
    imgResponse = urllib.request.urlopen(url, context=ssl_context)
    imgNp = np.array(bytearray(imgResponse.read()), dtype=np.uint8)
    img = cv2.imdecode(imgNp, -1)

    classIds, confs, bbox = net.detect(img, confThreshold=0.5)
    
    # Update tracker with new detections
    objects = ct.update(bbox)

    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            if classNames[classId - 1] == 'car':
                x, y, w, h = box
                # Check if the car is within the defined ROI
                if (roi_x_start < x < roi_x_start + roi_width) and (roi_y_start < y < roi_y_start + roi_height):
                    # Check if the car is already being tracked
                    if (x, y) in objects:
                        continue  # Skip if car is already tracked
                    car_count_8_12pm += 1
                    print(f"Car Detected! Count: {car_count_8_12pm}")
                    
    # Update count for 8-12pm in Realtime Database
    update_count(car_count_8_12pm)

    # Draw the ROI on the frame
    cv2.rectangle(img, (roi_x_start, roi_y_start), (roi_x_start + roi_width, roi_y_start + roi_height), (0, 255, 0), 2)

    cv2.imshow('Frame', img)
    
    # Calculate time taken for processing and displaying frame
    time_taken = time.time() - start_time
    
    # Calculate the time to sleep in order to achieve the desired FPS
    sleep_time = 1 / desired_fps - time_taken
    
    # Check if sleep time is positive, if not, set it to 0
    if sleep_time > 0:
        time.sleep(sleep_time)

    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
