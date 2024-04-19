import time
import socket
import firebase_admin
from firebase_admin import credentials, firestore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from datetime import datetime, timedelta
import pytz
from google.cloud.firestore_v1.document import DocumentSnapshot


# Firebase setup
cred = credentials.Certificate("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/iotproject-e09e8-firebase-adminsdk-9spg3-42a1469f03.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ESP32 setup
esp32_ip = '192.168.208.44'  # Replace with the actual IP address of your ESP32
esp32_port = 8080
esp32 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
esp32.connect((esp32_ip, esp32_port))

# Selenium setup
options = webdriver.EdgeOptions()
options.add_argument("--use-fake-ui-for-media-stream")
service = Service("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service, options=options)
driver.maximize_window()
driver.get("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/final/AbulanceSirenDetect.html")

# Set Sri Lankan timezone
srilanka_tz = pytz.timezone('Asia/Colombo')

# Global variables
last_sent_sequence = None
ambulance_detection_count = 0
reset_timer = None
reset_duration = 3  # Duration in seconds for resetting to initial state

# Function to check if an ambulance is detected
def check_for_ambulance():
    global ambulance_detection_count
    
    try:
        label_container = driver.find_element(By.ID, "label-container")
        labels = label_container.find_elements(By.TAG_NAME, "div")
        detected = False  # Variable to track if an ambulance is detected
        for label in labels:
            if label.text.startswith("Ambulance"):
                probability = float(label.text.split(":")[1].strip())
                if probability > 0.80:
                    print("Ambulance detected")
                    ambulance_detection_count += 1
                    detected = True  # Set detected flag
                    if ambulance_detection_count == 3:
                        print("Ambulance detected 3 times, retrieving recent entry from Firebase.")
                        retrieve_recent_entry()
                        ambulance_detection_count = 0  # Reset count
        if not detected:  # If no ambulance is detected in the current loop
            ambulance_detection_count = 0  # Reset count
            check_reset_timer()  # Check reset timer
        return detected  # Indicate ambulance detection
    except Exception as e:
        print("Error occurred while checking for ambulance:", e)
        return False

# Function to retrieve the latest entry posted to Firebase within 30 seconds before the third detection of an ambulance
def retrieve_recent_entry():
    try:
        # Define the time range in UTC timezone
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=5)  # Change to 5 minutes
        
        # Query to retrieve entries within the time range
        query = db.collection('detections').where(u'detection_time', u'>=', start_time).where(u'detection_time', u'<=', end_time).order_by(u'detection_time', direction=firestore.Query.DESCENDING).limit(1)
        
        # Execute the query
        docs = query.stream()
        
        for doc in docs:
            if isinstance(doc, DocumentSnapshot):
                doc_data = doc.to_dict()
                if doc_data is not None:
                    stream_name = doc_data.get('stream_name')
                    print("Recent entry retrieved from Firebase - Stream Name:", stream_name)
                    change_lights_accordingly(stream_name)
                    return
        print("No recent entry found within the specified time frame.")
    except Exception as e:
        print("Error occurred while retrieving recent entry from Firebase:", e)

# Function to change lights accordingly based on the stream name
def change_lights_accordingly(stream_name):
    if stream_name == "main":
        send_sequence_signal("100")  # Red lights for "main" stream
    elif stream_name == "by":
        send_sequence_signal("101")  # Red lights for "by" stream
    elif stream_name == "opp road":
        send_sequence_signal("102")  # Red lights for "opp road" stream
    else:
        print("Invalid stream name:", stream_name)


# Function to send sequence signals to ESP32 based on car count
def send_sequence_signal(sequence):
    global last_sent_sequence
    if sequence != last_sent_sequence:  # Check if it's a new sequence
        try:
            sequence_bytes = bytes(sequence, 'utf-8')
            esp32.sendall(sequence_bytes)
            print("Sequence signal sent to ESP32:", sequence)
            last_sent_sequence = sequence  # Update the last sent sequence
        except Exception as e:
            print("Error occurred while sending sequence signal to ESP32:", e)

# Function to retrieve car count and determine sequence signal to send
def car_count_and_send_signal():
    try:
        now = datetime.now(srilanka_tz)
        current_time = now.strftime("%I%p").lower()
        if current_time == '12am' or current_time == '01am' or current_time == '02am' or current_time == '03am':
            doc_id = '12am - 7.59am'
        elif current_time == '08am' or current_time == '09am' or current_time == '10am' or current_time == '11am':
            doc_id = '8am - 11.59am'
        elif current_time == '12pm' or current_time == '01pm' or current_time == '02pm' or current_time == '03pm':
            doc_id = '12pm - 3.59pm'
        elif current_time == '04pm' or current_time == '05pm' or current_time == '06pm' or current_time == '07pm':
            doc_id = '4pm - 7.59pm'
        elif current_time == '08pm' or current_time == '09pm' or current_time == '10pm' or current_time == '11pm':
            doc_id = '8pm - 11.59pm'
        else:
            doc_id = '12am - 7.59am'

        doc_ref = db.collection('car_count').document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            car_count_main = doc.to_dict().get('main')
            car_count_by = doc.to_dict().get('by')
            car_count_opp = doc.to_dict().get('opp_road')  # Retrieve count for opposing road
            if car_count_main is not None and car_count_by is not None and car_count_opp is not None:
                if car_count_main > car_count_by and car_count_main > car_count_opp:
                    send_sequence_signal("100")  # Send signal for Sequence 1
                elif car_count_by > car_count_main and car_count_by > car_count_opp:
                    send_sequence_signal("101")  # Send signal for Sequence 2
                elif car_count_opp > car_count_main and car_count_opp > car_count_by:
                    send_sequence_signal("102")  # Send signal for Sequence 3
        else:
            print("No such document!")
    except KeyboardInterrupt:
        pass

# Function to start reset timer
def start_reset_timer():
    global reset_timer
    reset_timer = datetime.now() + timedelta(seconds=reset_duration)

# Function to check reset timer and reset the system if needed
def check_reset_timer():
    global reset_timer, last_sent_sequence
    if reset_timer and datetime.now() >= reset_timer:
        print("Resetting to initial state after no ambulance detection.")
        car_count_and_send_signal()  # Call car count function to reset sequence
        last_sent_sequence = None  # Reset last sent sequence
        reset_timer = None  # Reset timer

try:
    while True:
        if not check_for_ambulance():  # If no ambulance detected
            car_count_and_send_signal()  # Proceed with car count analysis and sending sequence signals
        time.sleep(1)  # Check every 1 second
except KeyboardInterrupt:
    print("Program terminated by user.")

# Close connections and browser
esp32.close()
driver.quit()
