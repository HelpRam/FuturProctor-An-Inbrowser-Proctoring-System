# Check Master Branch for Source Code:
# **FuturProctor: An In-Browser Proctoring System**

FuturProctor is an advanced **web-based proctoring system** designed to **ensure integrity** during online exams and interviews. By integrating artificial intelligence (AI) with education, the system provides a robust solution for preventing cheating and ensuring fair assessments.

Leveraging cutting-edge technologies such as **YOLOv8 (object detection)**, **dlib (facial detection)**, **head pose estimation**, and **audio monitoring**, this system continuously monitors the exam environment for any suspicious activities. It automatically detects unauthorized devices, abnormal movements, and unusual sounds during the exam or interview.

FuturProctor blends the power of AI with educational integrity to ensure that both exams and interviews are conducted securely.

---
![MCQ Generator Screenshot](images/Screenshot_2024-11-21_003256.png)

## 🚀 **Features**

### 👤 **Face Recognition Login**
- Use **face recognition** to securely log in and start exams or interviews, eliminating the need for passwords or manual logins.
- Ensures that the person taking the exam is the correct participant.

### 📷 **Real-Time Object Detection**
- The **YOLOv8 model** is used to detect objects in the exam environment. The system continuously checks for unauthorized devices such as phones or books.
- If detected, the system triggers an alert.

### 🧑‍💻 **Head Pose Estimation**
- Tracks head movements in real-time to ensure the participant’s attention remains focused on the screen.
- Detects abnormal head movements (e.g., looking away from the screen) and notifies the proctor.

### 🎤 **Background Audio Monitoring**
- **Sound recording** continuously monitors for unusual noises (such as talking, typing, or background sounds from external devices).
- If suspicious sounds are detected, the system triggers an audible **beep** to alert the participant.

### 📊 **Comprehensive Exam Activity Logging**
- Logs all actions during the exam, including detected faces, objects, sounds, and head movements.
- Provides **detailed reports** that allow institutions to assess exam integrity after the session.

### 📈 **Cheating Detection Reports**
- Institutions receive detailed reports on potential cheating activities, including analysis of face detection, audio, and head movements.
- Reports also include detected objects and any abnormal behavior.

### 🏫 **Institution-Specific Exam Creation**
- Institutions can create exams tailored to their specific needs and monitor the exam environment using FuturProctor's suite of AI tools.

---

## 🛠️ **Technology Stack**

- **Python 3.12**
- **Django 5.1.1**
- **PyTorch 2.4.1**
- **OpenCV 4.10.0**
- **dlib 19.24.6**
- **NumPy 1.26.4**
- **Matplotlib 3.9.2**
- **Seaborn 0.13.2**

---

## 📁 **Project Structure**

```
futurproctor/
├── .myenv/                     # Virtual environment folder
├── logs/                        # Logs for monitoring
├── media/                       
│   ├── cvs/                    # Object detection results
│   ├── photos/                 # Photos for face recognition
├── object_detection_model/      # Trained YOLOv8 model
├── proctoring_systems/
│   ├── __pycache__/            # Compiled Python files
│   ├── management/             
│   ├── migrations/             
│   ├── ml_models/              # Machine learning models
│   ├── templates/              
│   ├── __init__.py             
│   ├── admin.py                
│   ├── apps.py                 
│   ├── google_sheets.py        
│   ├── models.py               
│   ├── tests.py                
│   ├── urls.py                 
│   └── views.py                
├── shape_predictor_model/       # Model for face detection landmarks
├── check.py                     # Additional scripts
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
├── report.html                  # Exam reports
├── requirements.txt             # Project dependencies
└── yolov8n.pt                   # YOLOv8 pre-trained model
```

---

## 🚀 **Getting Started**

1. **Clone the repository**:

    ```bash
    git clone https://github.com/HelpRam/FuturProctor-An-Inbrowser-Proctoring-System.git
    cd futurproctor
    ```

2. **Set up a virtual environment**:

    ```bash
    python -m venv .myenv
    source .myenv/bin/activate  # On Windows: .myenv\Scripts\activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run migrations**:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. **Start the development server**:

    ```bash
    python manage.py runserver
    ```

---

## 📝 **Usage**

- **Institution Admins**: Admins can log into the system, create exams, set proctoring rules, and manage participant data.
- **Students**: Students log in via facial recognition, and the system monitors them throughout the exam. The proctoring system tracks:
  - Multiple faces in the frame.
  - Unusual head movements.
  - Unauthorized objects.
  - Suspicious background sounds.
- **Reports**: Institutions can view detailed logs of suspicious activities after the exam, including head pose, face detection, and object monitoring.

---

## 🤖 **Model Architectures & Key Features**

### 1. **Object Detection Model (YOLOv3)**

YOLOv8 (You Only Look Once) is a cutting-edge object detection model known for its **real-time processing** capability and **accuracy**. It detects objects within an image or video and assigns each object a bounding box.

**How YOLOv3 works:**
- YOLOv3 divides the input image into a grid.
- Each grid cell predicts the class and bounding box for detected objects.
- It also generates probabilities for each object in the frame.
- The model was fine-tuned with custom data to detect suspicious items such as mobile phones and books.

**Why YOLOv3?**
- It’s fast and performs well in real-time applications, making it suitable for online exam monitoring.
  
### 2. **Sound Recording Model**

The sound monitoring system uses **PyAudio** to record continuous audio input, while **NumPy** processes the audio data. If any loud or unusual sound is detected, the system triggers a **beep sound** using **Winsound**.

### 3. **Facial Detection Model (dlib)**

The **dlib** library provides a **pre-trained face detection model** capable of detecting faces and facial landmarks in real-time. The system uses **dlib** to:
- Detect faces in the video feed.
- Track facial landmarks for identifying gaze direction, which is crucial for **head pose estimation**.
- Alert the system if multiple faces are detected in the frame.

**dlib's Role in the System:**
- dlib’s facial landmark detection helps in accurate head pose estimation and gaze tracking.
- It works seamlessly with **OpenCV** to process video frames and provide real-time facial analysis.

### 4. **Head Pose Movement Estimation**

Head pose estimation calculates the orientation of the head (up, down, left, right) based on facial landmarks. The system uses **dlib**, **cv2**, and **NumPy** to detect the **3D position of key points** on the face and project them into **2D space** to estimate head orientation.

**Functions in Use**:
- `get_2d_points()`: Projects the 3D points (from the face landmarks) into the 2D space of the image.
- `draw_annotation_box()`: Draws a box around the face to visualize head orientation.
- `head_pose_points()`: Calculates the angles to estimate head movement (e.g., turning the head to the side).

This system helps ensure that participants stay focused on the screen and alerts if there are **suspicious movements**.

---

## 🤝 **Contributing**

We welcome contributions, issues, and feature requests! Feel free to check the issues page and contribute.

---

## 🎓 **About**

FuturProctor was developed by a dedicated team aiming to bring **AI-powered solutions** to online exams, ensuring their **integrity** and **fairness**. The system integrates various cutting-edge AI technologies, including object detection, facial recognition, sound monitoring, and head pose estimation, to create a secure and efficient proctoring experience for institutions and exam participants.

