from .models import ProctoringLog



logs= ProctoringLog.objects.filter(user='joshirabindra2058')

print(logs)
