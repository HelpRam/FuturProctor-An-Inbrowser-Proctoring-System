from django.core.management.base import BaseCommand
from .models import Question, Subject
import json
from datetime import datetime
import re
import ast
from .models import ProctoringLog

class Command(BaseCommand):
    help = "Populates the database with dummy questions"

    def handle(self, *args, **kwargs):
        questions = [
            {
                "subject": "Mathematics",
                "text": "What is the value of π (Pi) approximately?",
                "option_a": "3.14",  # Correct Answer
                "option_b": "2.71",  # Wrong Answer
                "option_c": "1.41",  # Wrong Answer
                "option_d": "0.57",  # Wrong Answer
                "correct_answer": "A",
            },
            {
                "subject": "Science",
                "text": "What is the chemical symbol for water?",
                "option_a": "O2",  # Wrong Answer
                "option_b": "H2O",  # Correct Answer
                "option_c": "CO2",  # Wrong Answer
                "option_d": "NaCl",  # Wrong Answer
                "correct_answer": "B",
            },
            {
                "subject": "History",
                "text": "Who was the first president of the United States?",
                "option_a": "Abraham Lincoln",  # Wrong Answer
                "option_b": "George Washington",  # Correct Answer
                "option_c": "Thomas Jefferson",  # Wrong Answer
                "option_d": "John Adams",  # Wrong Answer
                "correct_answer": "B",
            },
            # Add other questions similarly
        ]

        for question_data in questions:
            subject, _ = Subject.objects.get_or_create(name=question_data["subject"])
            Question.objects.create(
                subject=subject,
                text=question_data["text"],
                option_a=question_data["option_a"],
                option_b=question_data["option_b"],
                option_c=question_data["option_c"],
                option_d=question_data["option_d"],
                correct_answer=question_data["correct_answer"],
            )

        self.stdout.write(self.style.SUCCESS("Successfully populated dummy questions"))


def sanitize_log_entry(entry):
    """
    Replace single quotes with double quotes and tuples with list-like structures for JSON compatibility.
    """
    # Replace single quotes with double quotes
    entry = re.sub(r"'", '"', entry)

    # Replace Python tuple-like structures (e.g., ('item', confidence)) with JSON-compatible lists
    entry = re.sub(r"\(([^)]+)\)", r"[\1]", entry)

    return entry


def process_log_file(username):
    total_entries = 0
    cheating_detected = 0
    no_cheating_detected = 0
    cheating_types = {
        "No Face Detected": 0,
        "Multiple Faces": 0,
        "Unauthorized Objects": 0,
        "Suspicious Head Movement": 0,
        "Suspicious Audio": 0,
    }
    object_detection_count = {}
    multiple_people_count = 0
    no_face_detected_count = 0
    suspicious_audio_count = 0
    logs= ProctoringLog.objects.filter(user=username).values()
    print("Logs: ", logs)
    for entry in logs:

        print("entry", entry)
        total_entries += 1

        if entry["status"] == "Cheating Detected":
            cheating_detected += 1
            details = entry["details"]

            if "Face Count: " in details:
                try:
                    face_count = int(details.split("Face Count: ")[1].split(",")[0])
                except (IndexError, ValueError):
                    # Handle the case where the split does not produce the expected result
                    face_count = 0
            else:
                face_count = 0

            if face_count == 0:
                cheating_types["No Face Detected"] += 1
                no_face_detected_count += 1
            elif face_count > 1:
                cheating_types["Multiple Faces"] += 1
                multiple_people_count += 1

            if "Detected Objects: []" not in details:
                cheating_types["Unauthorized Objects"] += 1
                objects = details.split("Detected Objects: [")[1].split("]")[0]
                for obj in objects.split("),"):
                    try:
                        obj_name = obj.split('"')[1]  # Adjusted to split by double quotes
                    except (IndexError, ValueError):
                    # Handle the case where the split does not produce the expected result
                        obj_name= ''
                    
                    object_detection_count[obj_name] = (
                        object_detection_count.get(obj_name, 0) + 1
                    )

            if (
                "Head Pose: No head detected" not in details
                and "Head Pose: -1" not in details
            ):
                cheating_types["Suspicious Head Movement"] += 1

            if "Suspicious audio detected" in details:
                cheating_types["Suspicious Audio"] += 1
                suspicious_audio_count += 1
        else:
            no_cheating_detected += 1

    cheating_percentage = (cheating_detected / total_entries) * 100

    if cheating_percentage < 10:
        overall_verdict = "Low probability of cheating"
        verdict_color = "success"
    elif cheating_percentage < 30:
        overall_verdict = "Moderate probability of cheating"
        verdict_color = "warning"
    else:
        overall_verdict = "High probability of cheating"
        verdict_color = "danger"

    context = {
        "total_entries": total_entries,
        "cheating_detected": cheating_detected,
        "no_cheating_detected": no_cheating_detected,
        "cheating_types": cheating_types,
        "object_detection_count": object_detection_count,
        "multiple_people_count": multiple_people_count,
        "no_face_detected_count": no_face_detected_count,
        "suspicious_audio_count": suspicious_audio_count,
        "overall_verdict": overall_verdict,
        "verdict_color": verdict_color,
        "cheating_percentage": round(cheating_percentage, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return context
