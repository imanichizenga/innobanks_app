

# import matplotlib.pyplot as plt
# import os
# from django.conf import settings
# import numpy as np

# def generate_performance_chart(examinations, output_path):
#     # Extract exam names and average marks
#     exam_names = [exam['exam_name'] for exam in examinations]
#     average_marks = [exam['average_marks'] for exam in examinations]
    
#     plt.figure(figsize=(10, 6))
#     plt.plot(exam_names, average_marks, marker='o', linestyle='-', color='#4e73df', linewidth=2, markersize=8)
#     plt.fill_between(exam_names, average_marks, alpha=0.1, color='#4e73df')
    
#     plt.title('Academic Performance Trend', fontsize=16, pad=20)
#     plt.xlabel('Examinations', fontsize=12)
#     plt.ylabel('Average Marks (%)', fontsize=12)
#     plt.ylim(0, 100)
#     plt.grid(True, linestyle='--', alpha=0.7)
#     plt.xticks(rotation=45, ha='right')
    
#     for i, mark in enumerate(average_marks):
#         plt.text(i, mark + 2, f'{mark:.1f}%', ha='center', fontsize=10)
    
#     plt.tight_layout()
#     plt.savefig(os.path.join(settings.STATIC_ROOT, 'charts', 'performance_chart.png'), dpi=300, bbox_inches='tight')
#     plt.close()

# def generate_payment_chart(fees, output_path):
#     fee_names = [fee['fee_name'] for fee in fees]
#     amounts = [fee['amount'] for fee in fees]
#     paid = [fee['paid'] for fee in fees]
    
#     x = np.arange(len(fee_names))
#     width = 0.35
    
#     plt.figure(figsize=(10, 6))
#     plt.bar(x - width/2, amounts, width, label='Amount Required', color='#e74a3b')
#     plt.bar(x + width/2, paid, width, label='Amount Paid', color='#1cc88a')
    
#     plt.title('Payment History', fontsize=16, pad=20)
#     plt.xlabel('Fee Types', fontsize=12)
#     plt.ylabel('Amount', fontsize=12)
#     plt.xticks(x, fee_names, rotation=45, ha='right')
#     plt.legend()
#     plt.grid(True, linestyle='--', alpha=0.7)
    
#     plt.tight_layout()
#     plt.savefig(os.path.join(settings.STATIC_ROOT, 'charts', 'payment_chart.png'), dpi=300, bbox_inches='tight')
#     plt.close()

# def generate_charts(academic_data, financial_data):
#     os.makedirs(os.path.join(settings.STATIC_ROOT, 'charts'), exist_ok=True)
#     generate_performance_chart(academic_data['examinations'], 'performance_chart.png')
#     generate_payment_chart(financial_data['fees'], 'payment_chart.png')











# rps_app app models.py: from django.db import models
# from django.conf import settings
# from django.contrib.auth.models import AbstractUser
# import logging
# import face_recognition
# logger = logging.getLogger(__name__)
# import os

# class ExaminationName(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Typically a Teacher
#         on_delete=models.CASCADE,
#         related_name='examination_name',
#         help_text="The user (e.g., teacher) who created this class."
#     )
#     exam_name = models.CharField(max_length=100,blank=True)

#     def __str__(self):
#         return f'{self.exam_name or "Unnamed Class"}'
# from django.db import models
# from django.conf import settings

# class AcademicClassYear(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='acdmc_year',
#         help_text="The user (e.g., teacher) who created this class."
#     )
#     academic_year_name = models.CharField(max_length=100, null=True, blank=True)
#     active_year = models.BooleanField(default=False)

#     def __str__(self):
#         return f'{self.academic_year_name or "Unnamed Academic Year"}'

#     class Meta:
#         verbose_name = "Academic Year"
#         verbose_name_plural = "Academic Years"

# class RegisterClass(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='register_class',
#         help_text="The user (e.g., teacher) who created this class."
#     )
#     class_name = models.CharField(max_length=100, null=True, blank=True)

#     def __str__(self):
#         # Get the active academic year from TeacherClass (if any)
#         teacher_class = self.teacherclass_set.filter(
#             academicclassyear__active_year=True
#         ).select_related('academicclassyear').first()

#         if teacher_class and teacher_class.academicclassyear:
#             return f"{self.class_name or 'Unnamed Class'} ({teacher_class.academicclassyear.academic_year_name})"
#         return f"{self.class_name or 'Unnamed Class'}"

#     class Meta:
#         verbose_name = "Registered Class"
#         verbose_name_plural = "Registered Classes"

#     class Meta:
#         verbose_name = "Registered Class"
#         verbose_name_plural = "Registered Classes"

# class TeacherClass(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='teacher_classes',
#         help_text="The user (e.g., teacher) who created this class."
#     )
#     ClassName = models.ForeignKey(RegisterClass, on_delete=models.CASCADE)
#     academicclassyear = models.ForeignKey(
#         AcademicClassYear,
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         help_text="The academic year associated with this class (optional)."
#     )

#     def __str__(self):
#         if self.academicclassyear:
#             return f'{self.ClassName.class_name} ({self.academicclassyear.academic_year_name})'
#         return f'{self.ClassName.class_name} (No Academic Year)'

#     @property
#     def is_active(self):
#         """Check if the associated academic year is active."""
#         return self.academicclassyear and self.academicclassyear.active_year

#     class Meta:
#         verbose_name = "Teacher Class"
#         verbose_name_plural = "Teacher Classes"

#     class Meta:
#         verbose_name = "Teacher Class"
#         verbose_name_plural = "Teacher Classes"
# # rps_app/models.py
# from django.db import models
# from django.conf import settings
# from django.contrib.auth.models import AbstractUser

# # 1. The New Unified User Model
# class User(AbstractUser):
#     is_student = models.BooleanField(default=False)
#     is_teacher = models.BooleanField(default=True)

    

# # 2. The Teacher Profile Model (no longer a user model)
# class Teacher(models.Model):
#     """Profile model for users with the 'TEACHER' role."""
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='teacher_profile')
#     teacherName = models.CharField(max_length=100, null=True, blank=True)
#     teacher_key = models.CharField(max_length=20, unique=True, help_text="Unique identifier for the teacher.")
#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='created_teachers',
        
#     )

#     photo = models.ImageField(upload_to='teacher_profile_photo/', null=True, blank=True)  # New: Photo field
#     face_encoding = models.BinaryField(null=True, blank=True)  # New: Face encoding field

#     def __str__(self):
#         return self.teacherName or self.user.username

#     def save_face_encoding(self, image_path=None):
#         """
#         Extract and save face encoding from teacher's photo
#         """
#         try:
#             if image_path is None and self.photo:
#                 image_path = self.photo.path
            
#             if not image_path or not os.path.exists(image_path):
#                 logger.warning(f"Image path does not exist: {image_path}")
#                 return False
            
#             # Load image
#             image = face_recognition.load_image_file(image_path)
            
#             # Detect faces
#             face_locations = face_recognition.face_locations(image)
            
#             if not face_locations:
#                 logger.warning(f"No face detected in image: {image_path}")
#                 return False
            
#             # Get encoding for the first face found
#             face_encodings = face_recognition.face_encodings(image, face_locations)
            
#             if not face_encodings:
#                 logger.warning(f"Could not extract face encoding from image: {image_path}")
#                 return False
            
#             # Save the first face encoding
#             encoding = face_encodings[0]
#             self.face_encoding = pickle.dumps(encoding)
#             self.save()
            
#             logger.info(f"Face encoding saved for teacher: {self.teacherName}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error saving face encoding for teacher {self.id}: {str(e)}")
#             return False
    
#     def get_face_encoding(self):
#         """Retrieve face encoding if exists"""
#         if self.face_encoding:
#             try:
#                 return pickle.loads(self.face_encoding)
#             except Exception as e:
#                 logger.error(f"Error loading face encoding for teacher {self.id}: {str(e)}")
#         return None

#     def __str__(self):
#         return self.teacherName or self.user.username




# from django.db import models
# from django.conf import settings
# from django.contrib.auth.models import AbstractUser
# import logging
# import pickle
# logger = logging.getLogger(__name__)

# # Other models remain unchanged...
# import json
# class Student(models.Model):
#     """Profile model for users with the 'STUDENT' role."""
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='student_profile'
#     )
#     indexNumber = models.CharField(max_length=100, null=True, blank=True)
#     fullName = models.CharField(max_length=100, null=True, blank=True)
#     sex = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
#     contact = models.BigIntegerField(null=True, blank=True)
#     teacherclass = models.ForeignKey('TeacherClass', on_delete=models.CASCADE)
#     photo = models.ImageField(upload_to='student_profile_photo/', null=True, blank=True)
#     manager = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='managed_students'
#     )
#     face_encoding = models.BinaryField(null=True, blank=True)  # Store face encoding
#     webauthn_credentials = models.JSONField(
#         null=True,
#         blank=True,
#         help_text="Stores WebAuthn credentials for fingerprint authentication."
#     )

#     def save_webauthn_credential(self, credential):
#         """Save WebAuthn credential for the student."""
#         try:
#             # Serialize credential to JSON
#             credential_data = {
#                 'id': credential.id,
#                 'public_key': credential.public_key.decode('utf-8') if isinstance(credential.public_key, bytes) else credential.public_key,
#                 'sign_count': credential.sign_count,
#             }
#             self.webauthn_credentials = json.dumps(credential_data)
#             self.save()
#             logger.info(f"WebAuthn credential saved for student {self.id}")
#         except Exception as e:
#             logger.error(f"Error saving WebAuthn credential for student {self.id}: {str(e)}")

#     def get_webauthn_credential(self):
#         """Retrieve WebAuthn credential."""
#         if self.webauthn_credentials:
#             return json.loads(self.webauthn_credentials)
#         return None

#     def save_face_encoding(self, image_path):
#         """Compute and save face encoding for the student's photo."""
#         try:
#             import face_recognition
#             image = face_recognition.load_image_file(image_path)
#             encodings = face_recognition.face_encodings(image, model="hog")
#             if encodings:
#                 self.face_encoding = pickle.dumps(encodings[0])
#                 self.save()
#             else:
#                 logger.warning(f"No face encodings found for student {self.id}")
#         except Exception as e:
#             logger.error(f"Error computing face encoding for student {self.id}: {str(e)}")

#     def save_face_encoding(self, image_path=None):
#         """
#         Extract and save face encoding from student's photo
#         """
#         try:
#             if image_path is None and self.photo:
#                 image_path = self.photo.path
            
#             if not image_path or not os.path.exists(image_path):
#                 logger.warning(f"Image path does not exist: {image_path}")
#                 return False
            
#             # Load image
#             image = face_recognition.load_image_file(image_path)
            
#             # Detect faces
#             face_locations = face_recognition.face_locations(image)
            
#             if not face_locations:
#                 logger.warning(f"No face detected in image: {image_path}")
#                 return False
            
#             # Get encoding for the first face found
#             face_encodings = face_recognition.face_encodings(image, face_locations)
            
#             if not face_encodings:
#                 logger.warning(f"Could not extract face encoding from image: {image_path}")
#                 return False
            
#             # Save the first face encoding
#             encoding = face_encodings[0]
#             self.face_encoding = pickle.dumps(encoding)
#             self.save()
            
#             logger.info(f"Face encoding saved for student: {self.fullName}")
#             return True
            
#         except Exception as e:
#             logger.error(f"Error saving face encoding for student {self.id}: {str(e)}")
#             return False
    
#     def get_face_encoding(self):
#         """Retrieve face encoding if exists"""
#         if self.face_encoding:
#             try:
#                 return pickle.loads(self.face_encoding)
#             except Exception as e:
#                 logger.error(f"Error loading face encoding for student {self.id}: {str(e)}")
#         return None


#     def __str__(self):
#         return f"{self.fullName or self.user.username} ({self.teacherclass.ClassName})"

#     class Meta:
#         verbose_name = "Student"
#         verbose_name_plural = "Students"
#         unique_together = ('indexNumber', 'teacherclass')  # Ensure unique indexNumber per class

# # Other models remain unchanged...

        
# class Subject(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Typically a Teacher
#         on_delete=models.CASCADE,
#         related_name='subjects',
#         help_text="The user (e.g., teacher) who created this subject."
#     )
#     teacherclass = models.ForeignKey(
#         'TeacherClass',
#         on_delete=models.CASCADE,
#         null=True,
#         blank=True,
#         help_text="The class this subject is associated with (optional)."
#     )
#     nameSubject = models.CharField(max_length=100, null=True, blank=True)

#     def __str__(self):
#         return f'{self.nameSubject or "Unnamed Subject"}'

#     class Meta:
#         verbose_name = "Subject"
#         verbose_name_plural = "Subjects"

# # rps_app/models.py

# from django.db import models
# from django.conf import settings

# class Mark(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Typically a Teacher
#         on_delete=models.CASCADE,
#         related_name='marks',
#         help_text="The user (e.g., teacher) who entered this mark."
#     )
#     teacherclass = models.ForeignKey(
#         'TeacherClass',
#         on_delete=models.CASCADE,
#         help_text="The class this mark pertains to."
#     )
#     examinationname = models.ForeignKey(
#         'ExaminationName',
#         on_delete=models.CASCADE,
#         help_text="Examination name",
# 	default = "exam 1"
       
#     )
#     student = models.ForeignKey(
#         'Student',
#         on_delete=models.CASCADE,
#         help_text="The student receiving this mark.",
#         related_name='marks'
#     )
#     subject = models.ForeignKey(
#         'Subject',
#         on_delete=models.CASCADE,
#         help_text="The subject this mark is for."
#     )
#     marks = models.PositiveIntegerField(help_text="The mark value (0-100).")

#     def __str__(self):
#         return f'{self.student.fullName} - {self.subject.nameSubject}: {self.marks}'

#     class Meta:
#         verbose_name = "Mark"
#         verbose_name_plural = "Marks"
        
#         unique_together = ('student', 'subject', 'teacherclass', 'examinationname')

# class TeacherSubject(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Typically a Teacher or admin
#         on_delete=models.CASCADE,
#         related_name='teacher_subject_assignments',
#         help_text="The user who assigned this subject (creator/admin)."
#     )
#     teacherclass = models.ForeignKey(
#         'TeacherClass',
#         on_delete=models.CASCADE,
#         help_text="The class this assignment pertains to."
#     )
#     teacher = models.ForeignKey(
#         'Teacher',  # Specifically a Teacher
#         on_delete=models.CASCADE,
#         related_name='teacher_subjects',
#         help_text="The teacher assigned to teach this subject."
#     )
#     subject = models.ForeignKey(
#         'Subject',
#         on_delete=models.CASCADE,
#         help_text="The subject being assigned."
#     )
#     is_restricted = models.BooleanField(
#         default=False,
#         help_text="If true, the teacher cannot enter marks for this subject."
#     )

#     def __str__(self):
#         return f'{self.teacher.teacherName or self.teacher.username} - {self.subject.nameSubject} ({self.teacherclass.ClassName})'

#     class Meta:
#         verbose_name = "Teacher Subject Assignment"
#         verbose_name_plural = "Teacher Subject Assignments"
#         unique_together = ('teacher', 'subject', 'teacherclass')

# class GradingModel(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Typically a Teacher
#         on_delete=models.CASCADE,
#         related_name='grading_models',
#         help_text="The user who defined this grading system."
#     )
#     is_advance = models.BooleanField(default=False, help_text="Indicates if this is an advanced grading system.")
#     grade_a = models.IntegerField(default=80)
#     grade_b = models.IntegerField(default=70)
#     grade_c = models.IntegerField(default=60)
#     grade_d = models.IntegerField(default=50)
#     grade_e = models.IntegerField(default=40)
#     grade_s = models.IntegerField(default=35)
#     grade_f = models.IntegerField(default=0)
#     division_1 = models.IntegerField(default=17)
#     division_2 = models.IntegerField(default=21)
#     division_3 = models.IntegerField(default=25)
#     division_4 = models.IntegerField(default=35)

#     def __str__(self):
#         level = "A-Level" if self.is_advance else "O-Level"
#         return f"{level} Grading (User: {self.user.username}) - ID: {self.id}"

#     def get_thresholds(self):
#         """Return a dictionary of grade thresholds and their corresponding letter grades."""
#         return {
#             self.grade_a: 'A',
#             self.grade_b: 'B',
#             self.grade_c: 'C',
#             self.grade_d: 'D',
#             self.grade_e: 'E',
#             self.grade_s: 'S',
#             self.grade_f: 'F'
#         }

#     class Meta:
#         verbose_name = "Grading System"
#         verbose_name_plural = "Grading Systems"

# class DisplayModel(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Can be Teacher or Student
#         on_delete=models.CASCADE,
#         related_name='displays',
#         help_text="The user who created this display."
#     )
#     header = models.CharField(max_length=100, null=True, blank=True)
#     body = models.CharField(max_length=100, null=True, blank=True)
#     image = models.ImageField(upload_to='image/', null=True, blank=True)

#     def __str__(self):
#         return f'{self.header or "Unnamed Display"}'

#     class Meta:
#         verbose_name = "Display Model"
#         verbose_name_plural = "Display Models"

# class ExcludeSubject(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Typically a Teacher
#         on_delete=models.CASCADE,
#         related_name='excluded_subjects',
#         help_text="The user who excluded this subject."
#     )
#     exclude_subject = models.ForeignKey(
#         'Subject',
#         on_delete=models.CASCADE,
#         help_text="The subject being excluded."
#     )

#     def __str__(self):
#         return f'Subject Excluded: {self.exclude_subject.nameSubject}'

#     class Meta:
#         verbose_name = "Excluded Subject"
#         verbose_name_plural = "Excluded Subjects"

# # models.py
# class StudentSubject(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='student_subjects',
#         help_text="The user (e.g., teacher) who assigned these students to the subject."
#     )
#     teacherclass = models.ForeignKey(
#         'TeacherClass',
#         on_delete=models.CASCADE,
#         help_text="The class this subject assignment pertains to."
#     )
#     subject = models.ManyToManyField(  # Changed from ForeignKey to ManyToManyField
#         'Subject',
#         help_text="The subjects the students are enrolled in."
#     )
#     student = models.ManyToManyField(
#         'Student',
#         related_name='subject_enrollments',
#         help_text="Students enrolled in these subjects."
#     )

#     def __str__(self):
#         subject_names = ", ".join(s.nameSubject or "Unnamed Subject" for s in self.subject.all())
#         return f'Students in {subject_names} ({self.teacherclass.ClassName})'

#     class Meta:
#         verbose_name = "Student Subject Assignment"
#         verbose_name_plural = "Student Subject Assignments"

# class UserSessionAccount(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Can be Teacher or Student
#         on_delete=models.CASCADE,
#         related_name='session_accounts',
#         help_text="The user this session belongs to."
#     )
#     session_key = models.CharField(max_length=40, unique=True)
#     username = models.CharField(max_length=150)
#     last_login = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)

#     def __str__(self):
#         return f"{self.username} - {self.session_key}"

#     class Meta:
#         verbose_name = "User Session Account"
#         verbose_name_plural = "User Session Accounts"
# # models.py
# from django.db import models
# from django.conf import settings
# from django.core.validators import FileExtensionValidator

# class TermMarksUpload(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='term_marks_uploads',
#         help_text="The user (e.g., teacher) who uploaded this file."
#     )
#     teacherclass = models.ForeignKey(
#         'TeacherClass',
#         on_delete=models.CASCADE,
#         help_text="The class this term marks pertain to."
#     )
#     term_name = models.CharField(
#         max_length=50,
#         help_text="The term these marks are for (e.g., Term 1, Midterm, etc.)."
#     )
#     pdf_file = models.FileField(
#         upload_to='term_marks_pdfs/',  # Subdirectory within MEDIA_ROOT
#         validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
#         help_text="PDF file containing marks for this term."
#     )
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     for_merging_pdf = models.BooleanField(default=False)
#     def __str__(self):
#         return f"{self.term_name} Marks for {self.teacherclass.ClassName}"

#     class Meta:
#         verbose_name = "Term Marks Upload"
#         verbose_name_plural = "Term Marks Uploads"
#         unique_together = ('teacherclass', 'term_name')


# # rps_app/models.py
# from django.db import models
# from django.conf import settings
# from django.core.mail import send_mail
# from datetime import timedelta
# from django.utils import timezone
# import secrets
# import string
# from rps_app.utils import get_email_settings

# class EmailVerificationOTP(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='email_verification_otps',
#         help_text="User associated with this OTP."
#     )
#     email = models.EmailField(
#         max_length=254,
#         help_text="Email address for OTP."
#     )
#     otp_code = models.CharField(
#         max_length=6,
#         help_text="6-digit OTP code."
#     )
#     created_at = models.DateTimeField(
#         auto_now_add=True,
#         help_text="When OTP was created."
#     )
#     expires_at = models.DateTimeField(
#         help_text="When OTP expires."
#     )
#     is_used = models.BooleanField(
#         default=False,
#         help_text="Whether OTP has been used."
#     )
#     is_verified = models.BooleanField(
#         default=False,
#         help_text="Whether the email has been verified."
#     )
#     purpose = models.CharField(
#         max_length=20,
#         choices=[('verification', 'Email Verification'), ('reset', 'Password Reset')],
#         default='reset',
#         help_text="Purpose of the OTP."
#     )

#     def __str__(self):
#         return f"OTP for {self.user.username} ({self.purpose})"

#     class Meta:
#         verbose_name = "Email Verification OTP"
#         verbose_name_plural = "Email Verification OTPs"

#     def generate_otp(self):
#         """Generate and save a 6-digit OTP."""
#         self.otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))
#         self.expires_at = timezone.now() + timedelta(minutes=15)
#         self.save()
#         return self.otp_code

#     def send_otp_email(self):
#         """Send OTP to user's email using dynamic email configuration."""
#         subject = "Email Verification OTP" if self.purpose == 'verification' else "Password Reset OTP"
#         message = f"Your OTP is {self.otp_code}. It expires in 15 minutes."
#         logger.info(f"Attempting to send OTP to {self.email} for user {self.user.username} ({self.purpose})")
        
#         try:
#             email_settings = get_email_settings(self.user)
#             logger.debug(f"Email settings: {email_settings}")
#             original_settings = {
#                 'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
#                 'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
#                 'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
#                 'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
#                 'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
#                 'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
#                 'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
#             }
#             for key, value in email_settings.items():
#                 setattr(settings, key, value)
#             send_mail(
#                 subject,
#                 message,
#                 email_settings['DEFAULT_FROM_EMAIL'],
#                 [self.email],
#                 fail_silently=False,
#             )
#             logger.info(f"OTP email sent successfully to {self.email}")
#             return True
#         except Exception as e:
#             logger.error(f"Failed to send OTP email to {self.email}: {str(e)}")
#             return False
#         finally:
#             for key, value in original_settings.items():
#                 if value is not None:
#                     setattr(settings, key, value)
#                 else:
#                     delattr(settings, key) if hasattr(settings, key) else None

#     def is_valid(self):
#         """Check if OTP is valid."""
#         return not self.is_used and timezone.now() <= self.expires_at

#     def verify_otp(self, input_otp):
#         """Verify OTP and update status."""
#         if self.is_valid() and self.otp_code == input_otp:
#             self.is_used = True
#             if self.purpose == 'verification':
#                 self.is_verified = True
#             self.save()
#             return True
#         return False


# # EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# # EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP host
# # EMAIL_PORT = 587
# # EMAIL_USE_TLS = True
# # EMAIL_HOST_USER = 'britishschooltz9@gmail.com'  # Your Gmail address
# # EMAIL_HOST_PASSWORD = 'asck jcua lrxe yshb'     # Gmail App Password (not your regular password)
# # DEFAULT_FROM_EMAIL = 'britishschooltz9@gmail.com'

# class EmailConfiguration(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='email_configuration',
#         help_text="The user associated with this email configuration."
#     )
#     email_backend = models.CharField(
#         max_length=200,
#         default='django.core.mail.backends.smtp.EmailBackend',
#         help_text="The email backend to use (e.g., SMTP backend)."
#     )
#     email_host = models.CharField(
#         max_length=100,
#         default='smtp.gmail.com',
#         help_text="The SMTP host for sending emails."
#     )
#     email_port = models.PositiveIntegerField(
#         default=587,
#         help_text="The port to use for the SMTP server."
#     )
#     email_use_tls = models.BooleanField(
#         default=True,
#         help_text="Whether to use TLS for secure email transmission."
#     )
#     email_host_user = models.CharField(
#         max_length=254,
#         help_text="The email address used for authentication with the SMTP server.",
#         default="britishschooltz9@gmail.com"
#     )
#     email_host_password = models.CharField(
#         max_length=100,
#         help_text="The password or app-specific password for the email account.",
#         default="asck jcua lrxe yshb"
#     )
#     default_from_email = models.EmailField(
#         max_length=254,
#         help_text="The default 'from' email address for sending emails.",
#         default="britishschooltz9@gmail.com"
#     )

#     def __str__(self):
#         return f"Email Configuration for {self.user.username}"

#     class Meta:
#         verbose_name = "Email Configuration"
#         verbose_name_plural = "Email Configurations"




# class RequiredSubject(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='subject_required',
#         help_text="The user (e.g., teacher) who assigned these students to the subject."
#     )
#     LEVEL = (('Olevel','O LEVEL'),
#              ('Alevel','A LEVEL'))
#     subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
#     level = models.CharField(max_length=100,choices=LEVEL,blank=False,null=True)

#     def __str__(self):
#         return f"{self.level}"
    

# class SmsConfiguration(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         help_text="The user (e.g., teacher) who assigned these students to the subject."
#     )
#     url_required = models.URLField(default="https://apisms.beem.africa/v1/send")
#     source_addr = models.CharField(default='innobanks',max_length=20)
#     destination_addr = models.CharField(default="255616257477",max_length=20)
#     message = models.TextField(default="innobanks messages")
#     username = models.CharField(default="fa41fbc274f5097c",max_length=50)
#     pswd = models.CharField(default="YzVhOTRlYmNhMmRkYWU5ZjBlYzUyY2U1NmNmYTNkNmIzZjZkODc3MjQzNDk3ZWMyNDE3MTJjN2Q5NTVlMTI2NA==",max_length=500)

#     def __str__(self):
#         return f"{self.source_addr}"


#     class Meta:
#         verbose_name = "SMS CONFIGURATIONS"
#         verbose_name_plural = "SMS CONFIGURATION"


# class Subscriber(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         help_text="Select subscriber"
#     )
#     is_subscribe = models.BooleanField(default=False)

#     def __str__(self):
#         return f'{self.user}'
    
#     class Meta:
#         verbose_name = 'Subscriber'
#         verbose_name_plural = 'System subscribers'  # Fixed typo in verbose_name_plural


# from django.db import models
# from django.conf import settings

# from django.db import models
# from django.conf import settings

# class SourceDocument(models.Model):
#     """
#     A document (image or PDF) that contains a signature/stamp
#     we want to extract and reuse.
#     """
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         help_text="user with source document",
#         related_name='source_document'
#     )
#     comment = models.CharField(max_length=200, null=True, blank=True)
#     file_signature = models.FileField(upload_to="source_docs/", null=True, blank=True)
#     file_stamp = models.FileField(upload_to="source_docs/", null=True, blank=True)
#     extracted_signature = models.ImageField(
#         upload_to="signatures/",
#         blank=True, null=True,
#         help_text="Signature extracted as transparent PNG",
#     )
#     extracted_stamp = models.ImageField(
#         upload_to="stamps/",
#         blank=True, null=True,
#         help_text="Stamp extracted as transparent PNG",
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.comment or f"Document for {self.user.username}"




# class RemarkRange(models.Model):
#     min_value = models.IntegerField(help_text="Enter the minimum value of the range",null=True)
#     max_value = models.IntegerField(help_text="Enter the maximum value of the range",null=True)
#     remark = models.CharField(max_length=100, help_text="Remark for this range",null=True)

#     class Meta:
#         verbose_name = "Remark Range"
#         verbose_name_plural = "Remark Ranges"
#         ordering = ['min_value']

#     def __str__(self):
#         return f"{self.min_value} - {self.max_value}: {self.remark}"

#     def contains(self, value):
#         """
#         Check if a value falls inside this range.
#         Example: obj.contains(15) → True if 15 is between min_value and max_value
#         """
#         return self.min_value <= value <= self.max_value
# .....................
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from rps_app.models import TeacherClass, GradingModel, DisplayModel, ExaminationName, RequiredSubject, Subject, Student, Mark, Teacher
# import pandas as pd
# from datetime import datetime
# import logging
# import os
# import psutil  # For memory usage logging
# from PIL import Image as PILImage

# logger = logging.getLogger(__name__)

# @login_required
# def download_pdf(request, class_id, grade_id, report_id='', examination_name_id=None):
#     # Log memory usage at the start
#     process = psutil.Process()
#     logger.debug(f"Memory usage at start: {process.memory_info().rss / 1024 / 1024:.2f} MB")

#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id else DisplayModel.objects.filter(user=request.user).first()
    
#     # Retrieve examination_name_id from request or session
#     examination_name_id = request.POST.get('examination_id', examination_name_id or request.session.get('selected_examination_id'))
#     if not examination_name_id:
#         messages.error(request, "No examination selected.")
#         return redirect('all_student_marks')
    
#     examination_name = get_object_or_404(ExaminationName, id=examination_name_id, user=request.user)

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subject_ids = required_subjects.values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=subject_ids, user=request.user).order_by('nameSubject')

#     mark_filter = models_Q(subject__in=subjects, examinationname=examination_name)
    
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(mark_filter).select_related('subject', 'examinationname', 'user'))
#     )

#     # Fetch teacher names for marks
#     all_marks = Mark.objects.filter(teacherclass=teacherclass, subject__in=subjects, examinationname=examination_name).select_related('user')
#     teacher_map = {}
#     for mark in all_marks:
#         if mark.user_id:
#             teacher = Teacher.objects.filter(user=mark.user).first()
#             teacher_map[mark.user_id] = teacher.teacherName or mark.user.username if teacher else mark.user.username

#     if grading.is_advance:
#         exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject_id', flat=True))
#         grade_thresholds = {
#             grading.grade_a: 'A',
#             grading.grade_b: 'B',
#             grading.grade_c: 'C',
#             grading.grade_d: 'D',
#             grading.grade_e: 'E',
#             grading.grade_s: 'S',
#             grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#     else:
#         exclude_subjects = set()
#         grade_thresholds = {
#             grading.grade_a: 'A',
#             grading.grade_b: 'B',
#             grading.grade_c: 'C',
#             grading.grade_d: 'D',
#             grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

#     # Initialize PDF response
#     response = HttpResponse(content_type='application/pdf')
#     exam_suffix = f"_{examination_name.exam_name.replace(' ', '_')}"
#     filename = f"student_report_{teacherclass.ClassName or 'Unnamed_Class'}{exam_suffix}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#     body_style.fontSize = 7

#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     def get_grade(mark):
#         if mark is None or pd.isna(mark):
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_remark(grade):
#         remark_map = {
#             'A': 'Excellent',
#             'B': 'Very Good',
#             'C': 'Good',
#             'D': 'Pass',
#             'E': 'Poor',
#             'S': 'Subsidiary',
#             'F': 'Fail',
#             '-': '-'
#         }
#         return remark_map.get(grade, '-')

#     def get_division(grades_for_division):
#         filtered_grades = [g for g in grades_for_division if g != '-']
#         num_valid_subjects = len(filtered_grades)
#         req_subs = 3 if grading.is_advance else 7
#         if num_valid_subjects < req_subs:
#             return "Inc", 0
#         sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:req_subs]
#         total_points = sum(grade_points[g] for g in sorted_grades)
#         for threshold in division_thresholds:
#             if total_points <= threshold['max']:
#                 return threshold['label'], total_points
#         return 'IV', total_points

#     # Header with DisplayModel
#     header_text = display.header if display else f"Results for {teacherclass.ClassName or 'Unnamed Class'} - {examination_name.exam_name}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(display.body if display else f"Comprehensive Academic Summary - {teacherclass.ClassName}", subheader_style))
#     elements.append(Spacer(1, 8))

#     if display and display.image:
#         try:
#             image_path = display.image.path
#             logger.debug(f"Checking image file: {image_path}")
#             if not os.path.exists(image_path):
#                 logger.error(f"Image file does not exist: {image_path}")
#                 raise FileNotFoundError(f"Image file not found: {image_path}")
#             if not os.access(image_path, os.R_OK):
#                 logger.error(f"Image file not readable: {image_path}")
#                 raise PermissionError(f"No read permission for image: {image_path}")
            
#             # Verify image with Pillow
#             logger.debug(f"Validating image with Pillow: {image_path}")
#             with PILImage.open(image_path) as img:
#                 img.verify()  # Check if image is valid
#                 logger.debug(f"Image verified successfully: {image_path}")
            
#             # Load image into ReportLab
#             logger.debug(f"Loading image into ReportLab: {image_path}")
#             icon = Image(image_path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.5*cm))
#             logger.debug(f"Successfully loaded image: {image_path}")
#         except Exception as e:
#             logger.error(f"Error loading DisplayModel image: {str(e)}")
#             elements.append(Paragraph(f"Error loading image: {str(e)}", body_style))
#             elements.append(Spacer(1, 0.5*cm))
#         finally:
#             # Log memory usage after image processing
#             logger.debug(f"Memory usage after image processing: {process.memory_info().rss / 1024 / 1024:.2f} MB")

#     if not students.exists() or not subjects.exists():
#         elements.append(Paragraph("No data available for this class.", body_style))
#     else:
#         # Aggregate student data
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination_name)),
#             average_marks=Avg('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination_name))
#         ).select_related('teacherclass')
#         student_data = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             marks_list = []
#             grades_for_division = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname=examination_name).first()
#                 mark_value = mark.marks if mark else None
#                 grade = get_grade(mark_value)
#                 teacher_name = teacher_map.get(mark.user_id, '-') if mark and mark.user_id else '-'
#                 if mark_value is not None:  # Only include subjects with valid marks
#                     marks_list.append({
#                         'subject_id': subject.id,
#                         'subject_name': subject.nameSubject,
#                         'mark': mark_value,
#                         'grade': grade,
#                         'is_excluded': subject.id in exclude_subjects,
#                         'teacher_name': teacher_name
#                     })
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)
#             has_valid_marks = any(grade != '-' for grade in grades_for_division)
#             division, total_points = get_division(grades_for_division)
#             student_data.append({
#                 'id': student.id,
#                 'fullName': student.fullName or 'Unnamed',
#                 'sex': student.sex or '-',
#                 'indexNumber': student.indexNumber or '-',
#                 'marks': marks_list,
#                 'total_marks': total_marks,
#                 'average_marks': average_marks,
#                 'grade': get_grade(average_marks),
#                 'division': division,
#                 'total_points': total_points,
#                 'has_valid_marks': has_valid_marks
#             })

#         student_data.sort(key=lambda x: (-x['has_valid_marks'], -x['total_marks']))

#         # Summary Table
#         elements.append(Paragraph("Academic Results", subheader_style))
#         header = ['Pos', 'Student Name', 'Sex', 'Index No'] + [s.nameSubject for s in subjects] + ['Total', 'Avg', 'Grade', 'Div', 'Pts']
#         table_data = [header]
#         for i, student in enumerate(student_data, 1):
#             row = [str(i), student['fullName'], student['sex'], student['indexNumber']]
#             for subject in subjects:
#                 mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                 if mark_info:
#                     sub_table = Table([[str(mark_info['mark']) if mark_info['mark'] is not None else '-', mark_info['grade']]],
#                                      colWidths=[14, 14], hAlign='CENTER')
#                     sub_table.setStyle(TableStyle([
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTSIZE', (0, 0), (-1, -1), 5),
#                         ('LEADING', (0, 0), (-1, -1), 6),
#                         ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                     ]))
#                     row.append(sub_table)
#                 else:
#                     row.append('-')
#             row.extend([
#                 f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                 f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                 student['grade'],
#                 student['division'],
#                 str(student['total_points']) if student['total_points'] > 0 else '-'
#             ])
#             table_data.append(row)

#         available_width = A4[0] - 30
#         total_columns = len(table_data[0])
#         base_width = available_width / total_columns
#         col_widths = ([base_width * 0.5] + [base_width * 2.5] + [base_width * 0.5] + [base_width * 1.8] + 
#                       [base_width * 0.9] * len(subjects) + [base_width * 0.6] * 5)

#         summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#         summary_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTSIZE', (0, 0), (-1, -1), 5),
#             ('LEADING', (0, 0), (-1, -1), 6),
#         ]))
#         elements.append(KeepTogether(summary_table))
#         elements.append(Spacer(1, 10))

#         # Individual Student Reports
#         total_students = len(student_data)
#         for i, student in enumerate(student_data, 1):
#             elements.append(PageBreak())
#             header_data = []
#             if display and display.image:
#                 try:
#                     image_path = display.image.path
#                     logger.debug(f"Checking image file for student report: {image_path}")
#                     if not os.path.exists(image_path):
#                         logger.error(f"Image file does not exist: {image_path}")
#                         raise FileNotFoundError(f"Image file not found: {image_path}")
#                     if not os.access(image_path, os.R_OK):
#                         logger.error(f"Image file not readable: {image_path}")
#                         raise PermissionError(f"No read permission for image: {image_path}")
                    
#                     # Verify image with Pillow
#                     logger.debug(f"Validating image with Pillow: {image_path}")
#                     with PILImage.open(image_path) as img:
#                         img.verify()
#                         logger.debug(f"Image verified successfully: {image_path}")
                    
#                     # Load image into ReportLab
#                     logger.debug(f"Loading image into ReportLab: {image_path}")
#                     icon = Image(image_path, width=2*cm, height=2*cm)
#                     icon.drawHeight = 2*cm
#                     icon.drawWidth = 2*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#                     logger.debug(f"Successfully loaded image for student report: {image_path}")
#                 except Exception as e:
#                     logger.error(f"Error loading DisplayModel image for student report: {str(e)}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"Student Report for {teacherclass.ClassName}", header_style),
#                     Spacer(1, 4),
#                     Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                 ]])

#             header_table = Table(header_data, colWidths=[3*cm, A4[0]-45-3*cm])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                 ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                 ('LEFTPADDING', (0, 0), (0, 0), 10),
#                 ('RIGHTPADDING', (1, 0), (1, 0), 10),
#             ]))
#             elements.append(header_table)
#             elements.append(Spacer(1, 10))

#             elements.append(Paragraph(f"Student Name: {student['fullName']}", bold_style))
#             elements.append(Spacer(1, 6))
#             elements.append(Paragraph(f"Index Number: {student['indexNumber']}", bold_style))
#             elements.append(Spacer(1, 6))
#             elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#             elements.append(Spacer(1, 10))

#             elements.append(Paragraph("Academic Performance", body_style))
#             marks_header = ['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']
#             marks_table_data = [marks_header]
#             valid_marks = [m for m in student['marks'] if m['grade'] != '-']
#             for mark_info in valid_marks:
#                 remark = get_remark(mark_info['grade'])
#                 marks_table_data.append([
#                     mark_info['subject_name'],
#                     f"{mark_info['mark']:.2f}" if mark_info['mark'] is not None else '-',
#                     mark_info['grade'],
#                     mark_info['teacher_name'],
#                     remark
#                 ])
#             if len(valid_marks) == 0:
#                 marks_table_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#             marks_table = Table(marks_table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], repeatRows=1)
#             marks_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#             ]))
#             elements.append(marks_table)
#             elements.append(Spacer(1, 12))

#             summary_data = [
#                 [f"Total Marks: {student['total_marks']:.2f}" if student['total_marks'] > 0 else 'Total Marks: -',
#                  f"Average: {student['average_marks']:.2f}" if student['average_marks'] > 0 else 'Average: -',
#                  f"Overall Grade: {student['grade']}"],
#                 [f"Division: {student['division']}",
#                  f"Total Points: {student['total_points'] if student['total_points'] > 0 else '-'}",
#                  f"Position in Class: {i}/{total_students}"]
#             ]
#             summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
#             summary_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 7),
#             ]))
#             elements.append(summary_table)
#             elements.append(Spacer(1, 12))

#             # Add signature area
#             elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#     # Log memory usage before PDF generation
#     logger.debug(f"Memory usage before PDF generation: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    
#     try:
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         logger.debug(f"Memory usage after PDF generation: {process.memory_info().rss / 1024 / 1024:.2f} MB")
#         messages.success(request, 'Examination-based results report generated successfully!')
#         return response
#     except Exception as e:
#         logger.error(f"Error generating PDF: {str(e)}")
#         messages.error(request, f"Error generating PDF: {str(e)}")
#         return redirect('all_student_marks')

# ..................Now in the pdf generated by this view, check well SourceDocument and RemarkRange model, i need in the section of individual student (student report form) report before the the principle signature should be that signature from SourceDocument, also stamp should be that extracted 
