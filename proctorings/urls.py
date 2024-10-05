# urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('video_feed/', views.video_feed, name='video_feed'),  # For video feed
    path('stop_video_feed/', views.stop_video_feed, name='stop_video_feed'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', auth_views.LoginView.as_view(template_name='index.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('exam/<str:username>/', views.exam_page, name='exam_page'),
    path('submit_exam/', views.submit_exam, name= 'submit_exam'),
    path('result/', views.result, name= 'result'),
    path('submit_quiz/', views.submit_quiz, name= 'submit_quiz'),
    path('generate_report/', views.generate_report, name='generate_report'),
    path('report/<str:username>/', views.report_view, name='report'),
    path('reports/', views.reports, name='reports'),
]
