import subprocess

# Define the paths to your Python scripts
script1_path = "C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/two_lane_count.py"
script2_path = "C:/Users/yvant/Downloads/Wifi_ESP32cam (1)/Wifi_ESP32cam/traffic_light_system.py"

# Function to run a Python script in a separate process
def run_script(script_path):
    subprocess.Popen(["python", script_path])

# Run both scripts simultaneously
run_script(script1_path)
run_script(script2_path)
