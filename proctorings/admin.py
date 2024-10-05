from django.contrib import admin
from django.utils.html import format_html
from .models import FormResponse, Subject, Question, Exam
from .models import ProctoringLog

@admin.register(ProctoringLog)
class ProctoringLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'time', 'status', 'details')
    search_fields = ('user__username', 'status', 'time')
    list_filter = ('time', 'status')

@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'email', 'timestamp','feedback', 'photo_tag', 'cv_link')  # Display name, email, timestamp, photo, and CV
    search_fields = ('name', 'email')
    list_filter = ('timestamp',)

    def photo_tag(self, obj):
        if obj.photo:
            return format_html(
                '<a href="{}" target="_blank">View Photo</a>',
                obj.photo.url, obj.photo.url
            )
        return "No Photo"

    def cv_link(self, obj):
        if obj.cv:
            return format_html('<a href="{}" target="_blank">View CV</a>'.format(obj.cv.url))
        return "No CV"

    photo_tag.short_description = 'Photo'  # Title for the photo column
    cv_link.short_description = 'CV'  # Title for the CV column

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Allows adding extra questions from the subject admin page


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "subject", "correct_answer")
    search_fields = ("text", "subject__name")
    list_filter = ("subject",)

    # This allows you to define the fields displayed when creating or editing a question
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "subject",
                    "text",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                )
            },
        ),
    )


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("subject", "date", "duration_minutes")
    search_fields = ("subject__name", "date")
    filter_horizontal = (
        "questions",
    )  # Allows selecting multiple questions in the admin