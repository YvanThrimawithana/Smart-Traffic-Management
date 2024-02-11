import cv2
import urllib.request
import numpy as np

url = 'http://192.168.60.23/cam-hi.jpg'

classNames = []
classFile = 'coco.names'
with open(classFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

car_count = 0

# Define the region of interest (ROI) where cars are allowed
roi_x_start = 290  # Adjust this value based on your specific case
roi_y_start = 0   # Adjust this value based on your specific case
roi_width = 350    # Adjust this value based on your specific case
roi_height = 480   # Adjust this value based on your specific case

while True:
    imgResponse = urllib.request.urlopen(url)
    imgNp = np.array(bytearray(imgResponse.read()), dtype=np.uint8)
    img = cv2.imdecode(imgNp, -1)

    classIds, confs, bbox = net.detect(img, confThreshold=0.5)

    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            if classNames[classId - 1] == 'car':
                x, y, w, h = box
                # Check if the car is within the defined ROI
                if (roi_x_start < x < roi_x_start + roi_width) and (roi_y_start < y < roi_y_start + roi_height):
                    car_count += 1
                    print(f"Car Detected! Count: {car_count}")

    # Draw the ROI on the frame
    cv2.rectangle(img, (roi_x_start, roi_y_start), (roi_x_start + roi_width, roi_y_start + roi_height), (0, 255, 0), 2)

    cv2.imshow('Frame', img)

    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
