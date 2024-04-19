import cv2
import numpy as np
import requests
from PIL import Image
from io import BytesIO
from keras.models import load_model
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
from pytz import timezone


# Initialize Firebase Admin SDK
cred = credentials.Certificate("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/iotproject-e09e8-firebase-adminsdk-9spg3-42a1469f03.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

# Load the model
model = load_model("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/keras_model.h5", compile=False)

# Load the labels
class_names = open("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/labels.txt", "r").readlines()

# Function to fetch image and make predictions
def predict_from_url(url, window_name):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = np.array(img)
    img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_AREA)
    cv2.imshow(window_name, img)
    image = np.asarray(img, dtype=np.float32).reshape(1, 224, 224, 3)
    image = (image / 127.5) - 1
    prediction = model.predict(image)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]
    print("Stream:", window_name)
    print("Class:", class_name[2:], end="")
    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")
    
    # Save to Firebase if class detected is "Ambulance"
    if "Ambulance" in class_name:
        save_to_firebase(window_name)

# Function to save detection information to Firebase
def save_to_firebase(stream_name):
    doc_ref = db.collection(u'detections').document()
    current_time = datetime.now(timezone('Asia/Colombo'))  # Adjust time zone to Sri Lanka (Asia/Colombo)
    doc_ref.set({
        u'stream_name': stream_name,
        u'detection_time': current_time
    })

# URLs for streams
urls = {
    "main": "http://192.168.205.23/cam-lo.jpg",
    "by": "http://192.168.205.46/cam-lo.jpg",
    "opp road": "http://192.168.205.203/cam-lo.jpg"
}

# Create windows for each stream
for window_name in urls.keys():
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 320, 240)

# Loop through each URL
while True:
    try:
        for window_name, url in urls.items():
            predict_from_url(url, window_name)
        keyboard_input = cv2.waitKey(1)
        if keyboard_input == 27:
            break
    except Exception as e:
        print("Error:", e)
        break

cv2.destroyAllWindows()
