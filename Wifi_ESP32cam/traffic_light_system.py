import time
import socket
import firebase_admin
from firebase_admin import credentials, firestore
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from datetime import datetime
import pytz

# Firebase setup
cred = credentials.Certificate("C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/iotproject-e09e8-firebase-adminsdk-9spg3-42a1469f03.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# ESP32 setup
esp32_ip = '192.168.1.19'  # Replace with the actual IP address of your ESP32
esp32_port = 8080
esp32 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
esp32.connect((esp32_ip, esp32_port))



# Selenium setup
options = webdriver.EdgeOptions()
options.add_argument("--use-fake-ui-for-media-stream")
service = Service("C:/Users/yvant/Downloads/edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service, options=options)
driver.maximize_window()
driver.get("C:/Users/yvant/Downloads/soundetect/index.html")

# Set Sri Lankan timezone
srilanka_tz = pytz.timezone('Asia/Colombo')

# Function to check if an ambulance is detected
def check_for_ambulance():
    try:
        label_container = driver.find_element(By.ID, "label-container")
        labels = label_container.find_elements(By.TAG_NAME, "div")
        for label in labels:
            if label.text.startswith("Ambulance"):
                probability = float(label.text.split(":")[1].strip())
                if probability > 0.80:
                    print("Ambulance")
                    esp32.sendall(b'1')  # Send signal to ESP32 to turn on green light
                    return True  # Indicate ambulance detection
        print("No ambulance detected.")
        return False  # Indicate no ambulance detection
    except Exception as e:
        print("Error occurred while checking for ambulance:", e)
        return False

# Function to retrieve car count and control traffic lights
def car_count_and_control_lights():
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
            if car_count_main is not None and car_count_by is not None:
                if car_count_main > car_count_by:
                    esp32.sendall(b'1')  # Send signal to ESP32 to turn on green light
                    print("Signal sent to ESP32 to turn on the green light.")
                else:
                    esp32.sendall(b'0')  # Send signal to ESP32 to turn on the red light
                    print("Signal sent to ESP32 to turn on the red light.")
            else:
                print("Main or By count is None!")
        else:
            print("No such document!")
    except KeyboardInterrupt:
        pass

try:
    while True:
        if not check_for_ambulance():  # If no ambulance detected
            car_count_and_control_lights()  # Proceed with car count analysis and controlling lights
        time.sleep(1)  # Check every 10 seconds
except KeyboardInterrupt:
    print("Program terminated by user.")

# Close connections and browser
esp32.close()
driver.quit()
