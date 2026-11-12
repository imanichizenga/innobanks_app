# attendance/urls.py
from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.student_attendance, name='student_attendance'),
    path('<int:class_id>/', views.student_attendance, name='student_attendance_with_class'),
    path('face-recognition/<int:class_id>/', views.process_face_recognition, name='process_face_recognition'),
    path('upload-photo/<int:student_id>/', views.upload_student_photo, name='upload_student_photo'),
    path('pdf/<int:class_id>/', views.generate_attendance_pdf, name='generate_attendance_pdf'),
    path('attendance/<int:class_id>/', views.attendance_table_partial, name='attendance_table_partial'),




    path('staff-attendance/', views.staff_attendance, name='staff_attendance'),
    path('face-recognition/staff/', views.process_staff_face_recognition, name='process_staff_face_recognition'),
    path('upload-teacher-photo/<int:teacher_id>/', views.upload_teacher_photo, name='upload_teacher_photo'),
    path('generate-staff-attendance-pdf/', views.generate_staff_attendance_pdf, name='generate_staff_attendance_pdf'),

    path('manual/students/', views.manual_student_attendance, name='manual_student_attendance'),
    path('manual/staff/', views.manual_staff_attendance, name='manual_staff_attendance'),
    path('manual/reports/students/', views.student_attendance_report, name='student_attendance_report'),
    path('manual/reports/staff/', views.staff_attendance_report, name='staff_attendance_report'),
    path('manual/reports/students/pdf/', views.student_attendance_report, name='student_attendance_report_pdf'),
    path('manual/reports/staff/pdf/', views.staff_attendance_report, name='staff_attendance_report_pdf'),

]
