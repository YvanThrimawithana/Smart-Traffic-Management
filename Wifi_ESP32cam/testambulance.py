import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Selenium setup
options = webdriver.EdgeOptions()  # Use EdgeOptions for Microsoft Edge
options.add_argument("--use-fake-ui-for-media-stream")  # Allows accessing microphone without user prompt
service = Service("C:/Users/yvant/Downloads/edgedriver_win64/msedgedriver.exe")
driver = webdriver.Edge(service=service, options=options)
driver.maximize_window()

# Open the webpage
driver.get("C:/Users/yvant/Downloads/soundetect/index.html")  # Specify the path to your HTML file

# Function to check if an ambulance is detected
def check_for_ambulance():
    try:
        label_container = driver.find_element(By.ID, "label-container")
        labels = label_container.find_elements(By.TAG_NAME, "div")
        for label in labels:
            if label.text.startswith("Ambulance"):
                probability = float(label.text.split(":")[1].strip())
                if probability > 0.80:
                    print("Ambulance detected!")
                    return
        print("No ambulance detected.")
    except Exception as e:
        print("Error occurred while checking for ambulance:", e)

# Main loop to continuously check for ambulance
try:
    while True:
        check_for_ambulance()
        time.sleep(0.5)  # Check every half second
except KeyboardInterrupt:
    print("Program terminated by user.")

# Close the browser
driver.quit()
