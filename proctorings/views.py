from django.shortcuts import render, redirect, get_object_or_404
from .google_sheets import get_sheet_data
from django.contrib.auth import authenticate, login
from .models import FormResponse, Question
from datetime import datetime
from django.utils import timezone
from django.db import IntegrityError
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import base64
from django.core.files.base import ContentFile
import cv2
from django.http import StreamingHttpResponse
from .ml_models.face_recognitions import gen_frames
from django.http import JsonResponse
from .models import FormResponse, Question, ProctoringLog
import threading
from .models import ProctoringLog
import cv2
import os
import time
import numpy as np
from datetime import datetime
import json
from proctorings.utils import process_log_file
from .models import CheatingLog, FormResponse  # Assuming you have these models
from proctorings.ml_models.audio_detection import audio_detection
from proctorings.ml_models.facial_detections import detectFace
from proctorings.ml_models.object_detections import detectObject
from proctorings.ml_models.head_pose_estimation import head_pose_detection
from .google_sheets import get_sheet_data  # Assuming this is for retrieving data
from .models import ProctoringLog
from venv import logger
import logging


# Log file path
log_file_path = os.path.join('logs', 'activity_log.txt')
if not os.path.exists('logs'):
    os.makedirs('logs')

# Function to get specific fields of the User model
def get_user_info(user):
    # Only include these specific fields
    selected_fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff']
    field_data = {}
    for field in selected_fields:
        if hasattr(user, field):
            field_data[field] = getattr(user, field)
    return field_data

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def video_feed(request):
    # Use the webcam as the camera
    camera = cv2.VideoCapture(0)
    return StreamingHttpResponse(gen_frames(camera, request),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def stop_video_feed(request):
    if request.method == 'POST':
        # Logic to stop the webcam stream on the backend
        # This might involve closing a video capture object or halting the stream.
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

    
def index(request):
    if request.method == 'POST':
        # Get login credentials from the form in index.html
        username = request.POST.get('email')
        password = request.POST.get('password')
        captured_photo = request.POST.get('captured_photo')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
                # If a photo was captured, save it to the user's profile or session
            if captured_photo:
                format, imgstr = captured_photo.split(';base64,')
                ext = format.split('/')[-1]
                photo_data = ContentFile(base64.b64decode(imgstr), name=f"{username}_captured.{ext}")

                # Save the captured image in session (to pass it to the home page)
                request.session['captured_photo'] = captured_photo
                request.session['username']=username

            # Log the user in
            login(request, user)

            # Redirect to the home page after successful login
            return redirect('home')

        else:
            # If login fails, display an error message
            messages.error(request, 'Invalid username or password.')

    return render(request, 'index.html')

@login_required(login_url='/')
def home(request):
    user_info = None
    # Get the captured photo from the session
    captured_photo = request.session.get('captured_photo', None)
    username = request.session.get('username', None)
    
    if username:
        try:
            # Fetch the User object using the username
            user = User.objects.get(username=username)
            # Pass the User object to get_user_info instead of username
            user_info = get_user_info(user)
        except User.DoesNotExist:
            user_info = None
    form_responses = FormResponse.objects.filter(email=user_info.get('email')) if user_info else []
    context = {
        'captured_photo': captured_photo,
        'username': username,
        'user_info': user_info,
        'form_responses': form_responses 
    }
    return render(request, 'home.html', context)



def convert_drive_link_to_direct_download(drive_url):
    """
    Convert a Google Drive share link to a direct download link.
    """
    if 'drive.google.com' in drive_url:
        if 'id=' in drive_url:
            # Handle URL format: https://drive.google.com/open?id=FILE_ID
            file_id = drive_url.split('id=')[1]
        elif '/d/' in drive_url:
            # Handle URL format: https://drive.google.com/file/d/FILE_ID/view
            file_id = drive_url.split('/d/')[1].split('/')[0]
        else:
            print("Invalid Google Drive link format.")
            return None
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return None


def save_sheet_data_to_model(data):
    FormResponse.objects.all().delete()  # Clear all existing FormResponse records

    # Skip the header row
    for index, row in enumerate(data):
        if index == 0:  # This is the header row
            continue
        
        if len(row) < 6:
            continue  # Skip rows that don't have enough data

        try:
            timestamp = datetime.strptime(row[0], '%m/%d/%Y %H:%M:%S')
            timestamp = timezone.make_aware(timestamp)

            # Check if the entry already exists based on email (assuming email is unique)
            if not FormResponse.objects.filter(email=row[3]).exists():
                
                # Handle photo upload
                photo_url = row[4]
                photo_path = None
                if photo_url:
                    direct_photo_url = convert_drive_link_to_direct_download(photo_url)
                    if direct_photo_url:
                        photo_name = f"{row[3].split('@')[0]}.jpg"
                        photo_file_path = f'photos/{photo_name}'

                        # Check if the photo already exists before downloading
                        if not default_storage.exists(photo_file_path):
                            photo_response = requests.get(direct_photo_url)
                            photo_path = default_storage.save(photo_file_path, ContentFile(photo_response.content))
                        else:
                            photo_path = photo_file_path  # Use existing file

                # Handle CV upload
                cv_url = row[5]
                cv_path = None
                if cv_url:
                    direct_cv_url = convert_drive_link_to_direct_download(cv_url)
                    if direct_cv_url:
                        cv_name = f"{row[3].split('@')[0]}_cv.pdf"
                        cv_file_path = f'cvs/{cv_name}'

                        # Check if the CV already exists before downloading
                        if not default_storage.exists(cv_file_path):
                            cv_response = requests.get(direct_cv_url)
                            cv_path = default_storage.save(cv_file_path, ContentFile(cv_response.content))
                        else:
                            cv_path = cv_file_path  # Use existing file

                # Create the FormResponse instance
                form_response = FormResponse(
                    timestamp=timestamp,
                    name=row[1],
                    address=row[2],
                    email=row[3],
                    photo=photo_path,
                    cv=cv_path,
                    feedback=row[6] if len(row) > 6 else None,
                )
                form_response.save()

                # Create a user from form response after saving
                create_user_from_form_response(row)
            else:
                print(f"Entry for {row[3]} already exists, skipping.")

        except ValueError as e:
            print(f"Error parsing row {row}: {e}")
        except IntegrityError as e:
            print(f"Error saving row {row}: {e}")

def create_user_from_form_response(row):
    print("Creating user from form response")
    
    email = row[3]  # Full email
    username = email.split('@')[0]  # Part before '@' as username and password
    password = username  # Set password to the same as the username
    name = row[1]
    
    # Split the name into first and last names
    full_name = name.split()
    first_name = full_name[0]
    last_name = full_name[-1] if len(full_name) > 1 else ''  # Handles cases where there may not be a last name
    
    print(full_name)
    
    # Check if user already exists
    if not User.objects.filter(username=username).exists():
        print(f"Creating user with username: {username}")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
    
        user.save()
        print(f"User {username} created successfully.")
    else:
        print(f"User with username {username} already exists.")



@login_required(login_url='/')
def exam_page(request, username):
    if request.method == 'POST':
        # Start the ML model in a background thread
        def proctoring_system(username):
            log_file = f"{username}.log"
            report_file = "report.html"

            # Initialize variables
            cap = cv2.VideoCapture(0)  # Open webcam
            cheat_count = 0  # Total cheat count
            consecutive_cheat_events = 0
            alert_threshold = 3
            report_interval = 300  # 5 minutes
            next_report_time = time.time() + report_interval
            real_time_alert = False
            interval_logs = []  # Activity logs within each 5-minute interval

            def log_activity_in_db(activity, username):
                # No need to fetch the User instance, just log the username directly
                ProctoringLog.objects.create(
                    user=username,  # Save the username as a string
                    time=timezone.now(),
                    status=activity['status'],
                    details=activity['details']
                )
            # Function to log activity
            def log_activity(log_file, activity):
                with open(log_file, 'a') as file:
                    file.write(str(activity) + '\n')

            # Function to determine cheating
            def detect_cheating(detected_objects, head_pose, face_count, audio_detected):
                nonlocal cheat_count, consecutive_cheat_events, real_time_alert
                cheated = False

                if any(obj in ['cell phone', 'phone', 'book'] for obj, _ in detected_objects):
                    cheat_count += 1
                    consecutive_cheat_events += 1
                    cheated = True

                if head_pose in ['left', 'right', 'down']:
                    cheat_count += 1
                    consecutive_cheat_events += 1
                    cheated = True

                if face_count > 1:
                    cheat_count += 1
                    consecutive_cheat_events += 1
                    cheated = True

                if audio_detected == "Suspicious audio detected":
                    cheat_count += 1
                    consecutive_cheat_events += 1
                    cheated = True

                if not cheated:
                    consecutive_cheat_events = 0

                if consecutive_cheat_events >= alert_threshold:
                    real_time_alert = True

                return cheated

            def audio_thread_function():
                while True:
                    audio_status = audio_detection()  # Get the returned status
                    print(f"Audio detection status: {audio_status}")
                    time.sleep(10)  # Run every 10 seconds

            # Start the audio detection thread
            audio_thread = threading.Thread(target=audio_thread_function)
            audio_thread.daemon = True
            audio_thread.start()

            # Main detection loop
            start_time = time.time()
            model_interval = 10  # 10 seconds for each model to run
            next_model_time = time.time() + model_interval

            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture frame from camera.")
                    break

                current_time_str = datetime.now().strftime("%H:%M:%S")

                # Run models sequentially
                if time.time() >= next_model_time:
                    face_count, faces = detectFace(frame)
                    head_pose = head_pose_detection(faces, frame) if face_count > 0 else "No head detected."
                    detected_objects = detectObject(frame)
                    audio_status = audio_detection()

                    cheating = detect_cheating(detected_objects, head_pose, face_count, audio_status)

                    # Log activity
                    status = "Cheating Detected" if cheating else "No Cheating Detected"
                    activity = {
                        'time': current_time_str,
                        'status': status,
                        'details': f"Face Count: {face_count}, Detected Objects: {detected_objects}, Head Pose: {head_pose}, Audio: {audio_status}"
                    }
                    log_activity(log_file, activity)

                    # Update next model time
                    next_model_time += model_interval
                    log_activity_in_db(activity, username)
                # Break loop on exit
                key = cv2.waitKey(1)
                if key == 27:  # Press 'Esc' to exit
                    break

            cap.release()
            cv2.destroyAllWindows()


        # Start the proctoring system in a background thread
        proctoring_thread = threading.Thread(target=proctoring_system, args=(username,))
        proctoring_thread.start()

        username = request.session.get('username', None)
        # Render the exam page immediately
        # read questions 
        subject = 'ai' 
        with open(f"D://proctoring_systems//proctorings//dummy_data//ai.json") as file:
            data = json.load(file)
        questions = data

        # Render the exam page immediately
        return render(request, 'exam_page.html', questions)
    questions = Question.objects.all()
    context = {
        'questions': questions, 
        'username': username
           }
    return render(request, 'exam_page.html', context)

def submit_exam(request):
    return render(request,'submit_exam.html')

def reports(request):
    users = ProctoringLog.objects.values('user').distinct()  # Get distinct users as dictionaries
    print('Users:', users)  # This will print a list of dictionaries containing 'user' keys

    # If you want to extract and print the actual usernames:
    usernames = [user_dict['user'] for user_dict in users]  # Extract the 'user' values from the dictionaries
    print('Usernames:', usernames)
    return render(request, 'reports.html', {'users': users})

# def reports(request):
#     try:
#         logs = ProctoringLog.objects.filter(user='joshirabindra2058')  # Fetch all logs
#         if logs.exists():  # Check if there are any logs
#             context = {'logs': logs}

#             return render(request, 'reports.html', context)
#         else:
#             return render(request, 'reports.html', {'error': 'No logs available'})
#     except Exception as e:
#         # Log the error or print it for debugging
#         print(f"Error generating report: {e}")
#         return render(request, 'reports.html', {'error': 'An error occurred while generating the report'})

def submit_quiz(request):
    return render(request,'submit_quiz.html')

def result(request):
    if request.method == 'POST':
        # Load the correct answers from the JSON file
        subject = 'ai'  # or dynamically fetch the subject
        with open(f"D://proctoring_systems//proctorings//dummy_data//ai.json") as file:
            data = json.load(file)
        # Filter based on subject if needed
        questions = [q for q in data['questions']]
        total_questions = len(questions)
        correct_answers = 0

        # Iterate over questions and check the answers submitted
        for question in questions:
            id = question['id']
            #print(f"question id: {id}")
            user_answer = request.POST.get(f'answer_{id}')
            #print(f"correct answer: {question['correct_answer']}")
            #print(f"user answer: {user_answer}")
            if user_answer == question['correct_answer']:
                correct_answers += 1

        # Calculate the score
        score = (correct_answers / total_questions) * 100

        # Pass the results to the template
        context = {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score': score,
            'username': request.POST.get('username')
        }

        return render(request, 'result.html', context)

def generate_report(request, username):
    print(f"Generating report for user: {username}")  # Debugging output
    if request.method == 'POST':
        # Your existing logic...
        return render(request, 'report_generated.html', {'username': username})

def result_view(request):
    if request.method == "POST":
        submitted_answers = request.POST  # Contains the user's submitted answers
        correct_answers = 0
        total_questions = Question.objects.count()

        # Loop through questions and check answers
        for i, question in enumerate(Question.objects.all(), start=1):
            selected_answer = submitted_answers.get(f"q{i}")
            if selected_answer == question.correct_answer:
                correct_answers += 1

        # Calculate score as percentage
        score = (correct_answers / total_questions) * 100

        # Render result page with score
        return render(
            request,
            "result.html",
            {
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
            },
        )

    return redirect("result.html")


          
                
# Configure logger
logger = logging.getLogger(__name__)

def report_view(request, username):
    logs = ProctoringLog.objects.filter(user= username)  # Fetch all logs

    context = process_log_file(username)
    return render(request, "report.html", {'username': username,'context': context, 'logs': logs})