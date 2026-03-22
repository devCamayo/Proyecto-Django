from django.urls import path
from . import views

urlpatterns = [
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/submit/', views.submit, name='submit'),
    path('result/<int:submission_id>/', views.show_exam_result, name='show_exam_result'),  # Cambiado a submission_id
]