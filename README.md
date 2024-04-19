# Smart Traffic Management System (STMS)
## Resources used 

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Arduino](https://img.shields.io/badge/Arduino-00878F?style=for-the-badge&logo=arduino&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-008ACC?style=for-the-badge&logo=matplotlib&logoColor=white) ![Centroid Tracker](https://img.shields.io/badge/Centroid%20Tracker-FFA500?style=for-the-badge) ![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge) ![HTML](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

## Demo videos

https://nsbm365-my.sharepoint.com/:u:/g/personal/yrthrimawithana_students_nsbm_ac_lk/ETAC0NGz35FNuEJWpoX_n_kBM3E5g7XX0qgKYEGPGRrsqQ?e=ThkLwJ

In Sri lanka the levels of traffic congestions during peak hours are quite high. This is due to ineffective traffic control systems. 

**Data Collection** 

In order to solve this real world issue our team as developed an STMS which makes use of cameras and object detections models to gather traffic data such as car counts from various lanes in a junctions. 
the collected data are then stored in firebase as follows (figure 1). 

**Data Analysis**

Collected data is then analyzed and the system will be ready to control traffic beforehand. 

**Data Implementation**

Once the system has identified the route with the most amout traffic it will communicate with the esp32 motherboard on which traffic lights turn green and which turn rd 

**Emergency featurs**

Using techable machine by google we make two emergency vehicle detection models 

1. to detect emergency vehicle using esp32 cam footage 

2. To detect emergency vehicle sirens using microphone

Cam based detections will be saved and the siren will trigger it to retreive the latest uploaded detection entry within a 5 minute period of the real time (figure 2) and allow that route to go through 

**Admin Panel**(Figure 3)

Robust admin panel to view and monitor traffic flow along with statistical data of the car counts in each time slots and amount of ambulances going thru each router 




## Features

- Car detection 
- Traffic analysis 
- Emergency vehicle detection
- Admin Panel with statistical data


# Screenshots

 ![image](https://github.com/YvanThrimawithana/Smart-Traffic-Management-System/assets/132426595/7932942e-08c0-433e-bfb8-35c1225c222b)



![image](https://github.com/YvanThrimawithana/Smart-Traffic-Management-System/assets/132426595/7442d6f2-32a3-431e-a1f2-639f3f6c27c6)




![image](https://github.com/YvanThrimawithana/Smart-Traffic-Management-System/assets/132426595/3ec38a19-2f8c-416b-96c8-0c596f5d8050)



## Authors
- [@YvanThrimawithana](https://github.com/YvanThrimawithana)
- [@PKSAmasha](https://github.com/PKSAmasha)
- [@AmarHisham](https://github.com/AmarHisham)
- [@KDissanayake](https://github.com/KDissanayake)
- [@Kumodh-Dinsara](https://github.com/Kumodh-Dinsara)
- [@ryanmariofdo](https://github.com/ryanmariofdo)





