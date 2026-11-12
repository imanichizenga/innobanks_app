from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import logging
import face_recognition
logger = logging.getLogger(__name__)
import os

class ExaminationName(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Typically a Teacher
        on_delete=models.CASCADE,
        related_name='examination_name',
        help_text="The user (e.g., teacher) who created this class."
    )
    exam_name = models.CharField(max_length=100,blank=True)

    def __str__(self):
        return f'{self.exam_name or "Unnamed Class"}'
from django.db import models
from django.conf import settings

class AcademicClassYear(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='acdmc_year',
        help_text="The user (e.g., teacher) who created this class."
    )
    academic_year_name = models.CharField(max_length=100, null=True, blank=True)
    active_year = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.academic_year_name or "Unnamed Academic Year"}'

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"

class RegisterClass(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='register_class',
        help_text="The user (e.g., teacher) who created this class."
    )
    class_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        # Get the active academic year from TeacherClass (if any)
        teacher_class = self.teacherclass_set.filter(
            academicclassyear__active_year=True
        ).select_related('academicclassyear').first()

        if teacher_class and teacher_class.academicclassyear:
            return f"{self.class_name or 'Unnamed Class'} ({teacher_class.academicclassyear.academic_year_name})"
        return f"{self.class_name or 'Unnamed Class'}"

    class Meta:
        verbose_name = "Registered Class"
        verbose_name_plural = "Registered Classes"

    class Meta:
        verbose_name = "Registered Class"
        verbose_name_plural = "Registered Classes"

class TeacherClass(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_classes',
        help_text="The user (e.g., teacher) who created this class."
    )
    ClassName = models.ForeignKey(RegisterClass, on_delete=models.CASCADE)
    academicclassyear = models.ForeignKey(
        AcademicClassYear,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The academic year associated with this class (optional)."
    )

    def __str__(self):
        if self.academicclassyear:
            return f'{self.ClassName.class_name} ({self.academicclassyear.academic_year_name})'
        return f'{self.ClassName.class_name} (No Academic Year)'

    @property
    def is_active(self):
        """Check if the associated academic year is active."""
        return self.academicclassyear and self.academicclassyear.active_year

    class Meta:
        verbose_name = "Teacher Class"
        verbose_name_plural = "Teacher Classes"

    class Meta:
        verbose_name = "Teacher Class"
        verbose_name_plural = "Teacher Classes"
# rps_app/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('accountant', 'Accountant'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    ]
# 1. The New Unified User Model
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=True)

    

# 2. The Teacher Profile Model (no longer a user model)
class Teacher(models.Model):
    """Profile model for users with the 'TEACHER' role."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='teacher_profile')
    teacherName = models.CharField(max_length=100, null=True, blank=True)
    teacher_key = models.CharField(max_length=20, unique=True, help_text="Unique identifier for the teacher.")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_teachers',
        
    )

    photo = models.ImageField(upload_to='teacher_profile_photo/', null=True, blank=True)  # New: Photo field
    face_encoding = models.BinaryField(null=True, blank=True)  # New: Face encoding field
    teacher_role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='teacher',  # Default value
    )

    def __str__(self):
        return self.teacherName or self.user.username

    def save_face_encoding(self, image_path=None):
        """
        Extract and save face encoding from teacher's photo
        """
        try:
            if image_path is None and self.photo:
                image_path = self.photo.path
            
            if not image_path or not os.path.exists(image_path):
                logger.warning(f"Image path does not exist: {image_path}")
                return False
            
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                logger.warning(f"No face detected in image: {image_path}")
                return False
            
            # Get encoding for the first face found
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if not face_encodings:
                logger.warning(f"Could not extract face encoding from image: {image_path}")
                return False
            
            # Save the first face encoding
            encoding = face_encodings[0]
            self.face_encoding = pickle.dumps(encoding)
            self.save()
            
            logger.info(f"Face encoding saved for teacher: {self.teacherName}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving face encoding for teacher {self.id}: {str(e)}")
            return False
    
    def get_face_encoding(self):
        """Retrieve face encoding if exists"""
        if self.face_encoding:
            try:
                return pickle.loads(self.face_encoding)
            except Exception as e:
                logger.error(f"Error loading face encoding for teacher {self.id}: {str(e)}")
        return None

    def __str__(self):
        return self.teacherName or self.user.username




from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import logging
import pickle
logger = logging.getLogger(__name__)

# Other models remain unchanged...
import json
class Student(models.Model):
    """Profile model for users with the 'STUDENT' role."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    indexNumber = models.CharField(max_length=100, null=True, blank=True)
    fullName = models.CharField(max_length=100, null=True, blank=True)
    sex = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], null=True, blank=True)
    contact = models.BigIntegerField(null=True, blank=True)
    teacherclass = models.ForeignKey('TeacherClass', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='student_profile_photo/', null=True, blank=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_students'
    )
    face_encoding = models.BinaryField(null=True, blank=True)  # Store face encoding
    webauthn_credentials = models.JSONField(
        null=True,
        blank=True,
        help_text="Stores WebAuthn credentials for fingerprint authentication."
    )

    def save_webauthn_credential(self, credential):
        """Save WebAuthn credential for the student."""
        try:
            # Serialize credential to JSON
            credential_data = {
                'id': credential.id,
                'public_key': credential.public_key.decode('utf-8') if isinstance(credential.public_key, bytes) else credential.public_key,
                'sign_count': credential.sign_count,
            }
            self.webauthn_credentials = json.dumps(credential_data)
            self.save()
            logger.info(f"WebAuthn credential saved for student {self.id}")
        except Exception as e:
            logger.error(f"Error saving WebAuthn credential for student {self.id}: {str(e)}")

    def get_webauthn_credential(self):
        """Retrieve WebAuthn credential."""
        if self.webauthn_credentials:
            return json.loads(self.webauthn_credentials)
        return None

    def save_face_encoding(self, image_path):
        """Compute and save face encoding for the student's photo."""
        try:
            import face_recognition
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image, model="hog")
            if encodings:
                self.face_encoding = pickle.dumps(encodings[0])
                self.save()
            else:
                logger.warning(f"No face encodings found for student {self.id}")
        except Exception as e:
            logger.error(f"Error computing face encoding for student {self.id}: {str(e)}")

    def save_face_encoding(self, image_path=None):
        """
        Extract and save face encoding from student's photo
        """
        try:
            if image_path is None and self.photo:
                image_path = self.photo.path
            
            if not image_path or not os.path.exists(image_path):
                logger.warning(f"Image path does not exist: {image_path}")
                return False
            
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            if not face_locations:
                logger.warning(f"No face detected in image: {image_path}")
                return False
            
            # Get encoding for the first face found
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if not face_encodings:
                logger.warning(f"Could not extract face encoding from image: {image_path}")
                return False
            
            # Save the first face encoding
            encoding = face_encodings[0]
            self.face_encoding = pickle.dumps(encoding)
            self.save()
            
            logger.info(f"Face encoding saved for student: {self.fullName}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving face encoding for student {self.id}: {str(e)}")
            return False
    
    def get_face_encoding(self):
        """Retrieve face encoding if exists"""
        if self.face_encoding:
            try:
                return pickle.loads(self.face_encoding)
            except Exception as e:
                logger.error(f"Error loading face encoding for student {self.id}: {str(e)}")
        return None


    def __str__(self):
        return f"{self.fullName or self.user.username} ({self.teacherclass.ClassName})"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        unique_together = ('indexNumber', 'teacherclass')  # Ensure unique indexNumber per class

# Other models remain unchanged...

        
class Subject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Typically a Teacher
        on_delete=models.CASCADE,
        related_name='subjects',
        help_text="The user (e.g., teacher) who created this subject."
    )
    teacherclass = models.ForeignKey(
        'TeacherClass',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The class this subject is associated with (optional)."
    )
    nameSubject = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f'{self.nameSubject or "Unnamed Subject"}'

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

# rps_app/models.py

from django.db import models
from django.conf import settings

class Mark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Typically a Teacher
        on_delete=models.CASCADE,
        related_name='marks',
        help_text="The user (e.g., teacher) who entered this mark."
    )
    teacherclass = models.ForeignKey(
        'TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this mark pertains to."
    )
    examinationname = models.ForeignKey(
        'ExaminationName',
        on_delete=models.CASCADE,
        help_text="Examination name",
	default = "exam 1"
       
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        help_text="The student receiving this mark.",
        related_name='marks'
    )
    subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        help_text="The subject this mark is for."
    )
    marks = models.PositiveIntegerField(help_text="The mark value (0-100).")

    def __str__(self):
        return f'{self.student.fullName} - {self.subject.nameSubject}: {self.marks}'

    class Meta:
        verbose_name = "Mark"
        verbose_name_plural = "Marks"
        
        unique_together = ('student', 'subject', 'teacherclass', 'examinationname')

class TeacherSubject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Typically a Teacher or admin
        on_delete=models.CASCADE,
        related_name='teacher_subject_assignments',
        help_text="The user who assigned this subject (creator/admin)."
    )
    teacherclass = models.ForeignKey(
        'TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this assignment pertains to."
    )
    teacher = models.ForeignKey(
        'Teacher',  # Specifically a Teacher
        on_delete=models.CASCADE,
        related_name='teacher_subjects',
        help_text="The teacher assigned to teach this subject."
    )
    subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        help_text="The subject being assigned."
    )
    is_restricted = models.BooleanField(
        default=False,
        help_text="If true, the teacher cannot enter marks for this subject."
    )

    def __str__(self):
        return f'{self.teacher.teacherName or self.teacher.username} - {self.subject.nameSubject} ({self.teacherclass.ClassName})'

    class Meta:
        verbose_name = "Teacher Subject Assignment"
        verbose_name_plural = "Teacher Subject Assignments"
        unique_together = ('teacher', 'subject', 'teacherclass')
from django.db import models
from django.conf import settings

class GradingModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Typically a Teacher
        on_delete=models.CASCADE,
        related_name='grading_models',
        help_text="The user who defined this grading system."
    )
    is_advance = models.BooleanField(default=False, help_text="Indicates if this is an advanced grading system.")
    is_primary = models.BooleanField(default=False, help_text="Indicates if this is a primary grading system.")
    grade_a = models.IntegerField(default=80, null=True)
    grade_b = models.IntegerField(default=70, null=True)
    grade_c = models.IntegerField(default=60, null=True)
    grade_d = models.IntegerField(default=50, null=True)
    grade_e = models.IntegerField(default=40, null=True)
    grade_s = models.IntegerField(default=35, null=True)
    grade_f = models.IntegerField(default=0, null=True)
    division_1 = models.IntegerField(default=17, null=True)
    division_2 = models.IntegerField(default=21, null=True)
    division_3 = models.IntegerField(default=25, null=True)
    division_4 = models.IntegerField(default=35, null=True)

    def __str__(self):
        if self.is_primary:
            level = "Primary"
        elif self.is_advance:
            level = "A-Level"
        else:
            level = "O-Level"
        return f"{level} Grading (User: {self.user.username}) - ID: {self.id}"

    def get_thresholds(self):
        """Return a dictionary of grade thresholds and their corresponding letter grades."""
        thresholds = {}
        if self.grade_a is not None:
            thresholds[self.grade_a] = 'A'
        if self.grade_b is not None:
            thresholds[self.grade_b] = 'B'
        if self.grade_c is not None:
            thresholds[self.grade_c] = 'C'
        if self.grade_d is not None:
            thresholds[self.grade_d] = 'D'
        
        # Handle grade_f based on level
        grade_f_grade = 'E' if self.is_primary else 'F'
        if self.grade_f is not None:
            thresholds[self.grade_f] = grade_f_grade
        
        if not self.is_primary:
            if self.grade_e is not None:
                thresholds[self.grade_e] = 'E'
            if self.grade_s is not None:
                thresholds[self.grade_s] = 'S'
        
        return thresholds

    class Meta:
        verbose_name = "Grading System"
        verbose_name_plural = "Grading Systems"
        unique_together = ('user', 'is_primary', 'is_advance')

        
class DisplayModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Can be Teacher or Student
        on_delete=models.CASCADE,
        related_name='displays',
        help_text="The user who created this display."
    )
    header = models.CharField(max_length=100, null=True, blank=True)
    body = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='image/', null=True, blank=True)

    def __str__(self):
        return f'{self.header or "Unnamed Display"}'

    class Meta:
        verbose_name = "Display Model"
        verbose_name_plural = "Display Models"

class ExcludeSubject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Typically a Teacher
        on_delete=models.CASCADE,
        related_name='excluded_subjects',
        help_text="The user who excluded this subject."
    )
    exclude_subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        help_text="The subject being excluded."
    )

    def __str__(self):
        return f'Subject Excluded: {self.exclude_subject.nameSubject}'

    class Meta:
        verbose_name = "Excluded Subject"
        verbose_name_plural = "Excluded Subjects"

# models.py
class StudentSubject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_subjects',
        help_text="The user (e.g., teacher) who assigned these students to the subject."
    )
    teacherclass = models.ForeignKey(
        'TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this subject assignment pertains to."
    )
    subject = models.ManyToManyField(  # Changed from ForeignKey to ManyToManyField
        'Subject',
        help_text="The subjects the students are enrolled in."
    )
    student = models.ManyToManyField(
        'Student',
        related_name='subject_enrollments',
        help_text="Students enrolled in these subjects."
    )

    def __str__(self):
        subject_names = ", ".join(s.nameSubject or "Unnamed Subject" for s in self.subject.all())
        return f'Students in {subject_names} ({self.teacherclass.ClassName})'

    class Meta:
        verbose_name = "Student Subject Assignment"
        verbose_name_plural = "Student Subject Assignments"

class UserSessionAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Can be Teacher or Student
        on_delete=models.CASCADE,
        related_name='session_accounts',
        help_text="The user this session belongs to."
    )
    session_key = models.CharField(max_length=40, unique=True)
    username = models.CharField(max_length=150)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} - {self.session_key}"

    class Meta:
        verbose_name = "User Session Account"
        verbose_name_plural = "User Session Accounts"
# models.py
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

class TermMarksUpload(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='term_marks_uploads',
        help_text="The user (e.g., teacher) who uploaded this file."
    )
    teacherclass = models.ForeignKey(
        'TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this term marks pertain to."
    )
    term_name = models.CharField(
        max_length=50,
        help_text="The term these marks are for (e.g., Term 1, Midterm, etc.)."
    )
    pdf_file = models.FileField(
        upload_to='term_marks_pdfs/',  # Subdirectory within MEDIA_ROOT
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="PDF file containing marks for this term."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    for_merging_pdf = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.term_name} Marks for {self.teacherclass.ClassName}"

    class Meta:
        verbose_name = "Term Marks Upload"
        verbose_name_plural = "Term Marks Uploads"
        unique_together = ('teacherclass', 'term_name')


# rps_app/models.py
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
import secrets
import string
from rps_app.utils import get_email_settings

class EmailVerificationOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification_otps',
        help_text="User associated with this OTP."
    )
    email = models.EmailField(
        max_length=254,
        help_text="Email address for OTP."
    )
    otp_code = models.CharField(
        max_length=6,
        help_text="6-digit OTP code."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When OTP was created."
    )
    expires_at = models.DateTimeField(
        help_text="When OTP expires."
    )
    is_used = models.BooleanField(
        default=False,
        help_text="Whether OTP has been used."
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether the email has been verified."
    )
    purpose = models.CharField(
        max_length=20,
        choices=[('verification', 'Email Verification'), ('reset', 'Password Reset')],
        default='reset',
        help_text="Purpose of the OTP."
    )

    def __str__(self):
        return f"OTP for {self.user.username} ({self.purpose})"

    class Meta:
        verbose_name = "Email Verification OTP"
        verbose_name_plural = "Email Verification OTPs"

    def generate_otp(self):
        """Generate and save a 6-digit OTP."""
        self.otp_code = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.expires_at = timezone.now() + timedelta(minutes=15)
        self.save()
        return self.otp_code

    def send_otp_email(self):
        """Send OTP to user's email using dynamic email configuration."""
        subject = "Email Verification OTP" if self.purpose == 'verification' else "Password Reset OTP"
        message = f"Your OTP is {self.otp_code}. It expires in 15 minutes."
        logger.info(f"Attempting to send OTP to {self.email} for user {self.user.username} ({self.purpose})")
        
        try:
            email_settings = get_email_settings(self.user)
            logger.debug(f"Email settings: {email_settings}")
            original_settings = {
                'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
                'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
                'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
                'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
                'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
                'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
                'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            }
            for key, value in email_settings.items():
                setattr(settings, key, value)
            send_mail(
                subject,
                message,
                email_settings['DEFAULT_FROM_EMAIL'],
                [self.email],
                fail_silently=False,
            )
            logger.info(f"OTP email sent successfully to {self.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send OTP email to {self.email}: {str(e)}")
            return False
        finally:
            for key, value in original_settings.items():
                if value is not None:
                    setattr(settings, key, value)
                else:
                    delattr(settings, key) if hasattr(settings, key) else None

    def is_valid(self):
        """Check if OTP is valid."""
        return not self.is_used and timezone.now() <= self.expires_at

    def verify_otp(self, input_otp):
        """Verify OTP and update status."""
        if self.is_valid() and self.otp_code == input_otp:
            self.is_used = True
            if self.purpose == 'verification':
                self.is_verified = True
            self.save()
            return True
        return False


# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'  # Gmail SMTP host
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'britishschooltz9@gmail.com'  # Your Gmail address
# EMAIL_HOST_PASSWORD = 'asck jcua lrxe yshb'     # Gmail App Password (not your regular password)
# DEFAULT_FROM_EMAIL = 'britishschooltz9@gmail.com'

class EmailConfiguration(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_configuration',
        help_text="The user associated with this email configuration."
    )
    email_backend = models.CharField(
        max_length=200,
        default='django.core.mail.backends.smtp.EmailBackend',
        help_text="The email backend to use (e.g., SMTP backend)."
    )
    email_host = models.CharField(
        max_length=100,
        default='smtp.gmail.com',
        help_text="The SMTP host for sending emails."
    )
    email_port = models.PositiveIntegerField(
        default=587,
        help_text="The port to use for the SMTP server."
    )
    email_use_tls = models.BooleanField(
        default=True,
        help_text="Whether to use TLS for secure email transmission."
    )
    email_host_user = models.CharField(
        max_length=254,
        help_text="The email address used for authentication with the SMTP server.",
        default="britishschooltz9@gmail.com"
    )
    email_host_password = models.CharField(
        max_length=100,
        help_text="The password or app-specific password for the email account.",
        default="asck jcua lrxe yshb"
    )
    default_from_email = models.EmailField(
        max_length=254,
        help_text="The default 'from' email address for sending emails.",
        default="britishschooltz9@gmail.com"
    )

    def __str__(self):
        return f"Email Configuration for {self.user.username}"

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"




class RequiredSubject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subject_required',
        help_text="The user (e.g., teacher) who assigned these students to the subject."
    )
    LEVEL = (
        ('Olevel','O LEVEL'),
        ('Alevel','A LEVEL'),
        ('Primary','PRIMARY'),
        )
    subject = models.ForeignKey(Subject,on_delete=models.CASCADE)
    level = models.CharField(max_length=100,choices=LEVEL,blank=False,null=True)
    teacherclass = models.ForeignKey(
        'TeacherClass',
        on_delete=models.CASCADE,
        help_text="The class this subject assignment pertains to.",
        null=True,
        related_name='required_subjects'
    )

    def __str__(self):
        return f"{self.level}"
    

class SmsConfiguration(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rps_sms_configuration",
        help_text="The user (e.g., teacher) who assigned these students to the subject."
    )
    url_required = models.URLField(default="https://apisms.beem.africa/v1/send")
    source_addr = models.CharField(default='innobanks',max_length=20)
    destination_addr = models.CharField(default="255616257477",max_length=20)
    message = models.TextField(default="innobanks messages")
    username = models.CharField(default="fa41fbc274f5097c",max_length=50)
    pswd = models.CharField(default="YzVhOTRlYmNhMmRkYWU5ZjBlYzUyY2U1NmNmYTNkNmIzZjZkODc3MjQzNDk3ZWMyNDE3MTJjN2Q5NTVlMTI2NA==",max_length=500)

    def __str__(self):
        return f"{self.source_addr}"


    class Meta:
        verbose_name = "SMS CONFIGURATIONS"
        verbose_name_plural = "SMS CONFIGURATION"


class StudentCommunicationLog(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('message', 'Message'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='student_communications'
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='communication_logs'
    )
    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default='message',
        null=True,
        blank=True
    )
    recipient = models.CharField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='sent',
        null=True,
        blank=True
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.student} - {self.channel or 'message'} ({self.status})"


class Subscriber(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="Select subscriber"
    )
    is_subscribe = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user}'
    
    class Meta:
        verbose_name = 'Subscriber'
        verbose_name_plural = 'System subscribers'  # Fixed typo in verbose_name_plural


from django.db import models
from django.conf import settings

from django.db import models
from django.conf import settings

class SourceDocument(models.Model):
    """
    A document (image or PDF) that contains a signature/stamp
    we want to extract and reuse.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="user with source document",
        related_name='source_document'
    )
    comment = models.CharField(max_length=200, null=True, blank=True)
    file_signature = models.FileField(upload_to="source_docs/", null=True, blank=True)
    file_stamp = models.FileField(upload_to="source_docs/", null=True, blank=True)
    extracted_signature = models.ImageField(
        upload_to="signatures/",
        blank=True, null=True,
        help_text="Signature extracted as transparent PNG",
    )
    extracted_stamp = models.ImageField(
        upload_to="stamps/",
        blank=True, null=True,
        help_text="Stamp extracted as transparent PNG",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    allow_to_be_used = models.BooleanField(default=False, help_text="Allow this document to be used in reports")

    def __str__(self):
        return self.comment or f"Document for {self.user.username}"




class RemarkRange(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        help_text="user with source document",
        related_name='remark_range',
        null=True
    )
    min_value = models.IntegerField(help_text="Enter the minimum value of the range",null=True)
    max_value = models.IntegerField(help_text="Enter the maximum value of the range",null=True)
    remark = models.CharField(max_length=100, help_text="Remark for this range",null=True)

    class Meta:
        verbose_name = "Remark Range"
        verbose_name_plural = "Remark Ranges"
        ordering = ['min_value']

    def __str__(self):
        return f"{self.min_value} - {self.max_value}: {self.remark}"

    def contains(self, value):
        """
        Check if a value falls inside this range.
        Example: obj.contains(15) → True if 15 is between min_value and max_value
        """
        return self.min_value <= value <= self.max_value
from django.conf import settings
from django.db import models

class Payment(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100, null=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    callback_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.status}"


class PaymentNotification(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_notifications',
        null=True,
        blank=True
    )
    order_id = models.CharField(max_length=100, null=True)  # Added: Links to order
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')  # Added: Matches __str__
    success_payment = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)  # Added: Links to Payment

    def __str__(self):
        return f"{self.order_id} - {self.status}"



class UserAmount(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_amounts',
        null=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,default=20000)

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class CompositeSubject(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='composite_subjects',
        null=True,
        blank=True
    )
    subject_name = models.CharField(max_length=100, null=True, blank=True)
    subjects = models.ManyToManyField(
        Subject,
        related_name='composite_subject_groups',
        blank=True
    )
    allow_to_use = models.BooleanField(default=False)

    def __str__(self):
        return self.subject_name or "Unnamed Composite Subject"



class UserPermission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_perm',
        null=True,
        blank=True
    )
    teacher=models.OneToOneField(Teacher,on_delete=models.CASCADE,null=True)
    can_view_attendance = models.BooleanField(default=False)
    can_view_registration = models.BooleanField(default=False)
    can_view_settings = models.BooleanField(default=False)

    #settings permission
    can_view_output = models.BooleanField(default=False)
    can_modify_grading_system = models.BooleanField(default=False)
    can_modify_display = models.BooleanField(default=False)
    can_modify_teacher_subject = models.BooleanField(default=False)
    can_modify_student_subject = models.BooleanField(default=False)
    can_modify_excluded_subject = models.BooleanField(default=False)
    can_modify_subject_settings = models.BooleanField(default=False)
    can_modify_stamp_and_signature = models.BooleanField(default=False)
    can_modify_comments = models.BooleanField(default=False)
    can_modify_composite_subject = models.BooleanField(default=False)

    #registration permission
    can_view_crm = models.BooleanField(default=False, null=True, blank=True)
    can_manage_home_enquiries = models.BooleanField(default=False)
    can_modify_academic_year = models.BooleanField(default=False)
    can_modify_venue = models.BooleanField(default=False)
    can_modify_examination = models.BooleanField(default=False)
    can_modify_subjects = models.BooleanField(default=False)
    can_modify_students = models.BooleanField(default=False)
    can_manage_student_applications = models.BooleanField(default=False, null=True, blank=True)
    can_modify_staff = models.BooleanField(default=False)
    can_manage_student_id = models.BooleanField(default=False, null=True, blank=True)

    #attendance permission
    can_open_staff_attendance = models.BooleanField(default=False)
    can_open_student_attendance = models.BooleanField(default=False)
    can_search_student = models.BooleanField(default=False)
    can_retreve_student = models.BooleanField(default=False)


    #output permission
    can_view_best_student = models.BooleanField(default=False)
    can_view_results = models.BooleanField(default=False)
    can_view_subject_analysis = models.BooleanField(default=False)
    can_view_grade_analysis = models.BooleanField(default=False)
    can_view_division_analysis = models.BooleanField(default=False)

    # Transport permissions
    can_view_transport = models.BooleanField(default=False)
    can_manage_vehicle = models.BooleanField(default=False)
    can_manage_route = models.BooleanField(default=False)
    can_manage_fuel = models.BooleanField(default=False)
    can_manage_maintenance = models.BooleanField(default=False)
    can_manage_expense = models.BooleanField(default=False)
    can_view_transport_dashboard = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.teacher}'




# rps_app/models.py (updated sections only - add/replace these in your existing file)
# ... (keep all existing models as-is, but update ChatMessage and ChatRoom)

# --- add to the top with other imports ---
from django.db import models

# --- replace the whole ChatMessage model ---
class ChatMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        null=True
    )
    message = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    # 0 = delivered to server, 1 = receiver online, 2 = seen
    status = models.PositiveSmallIntegerField(
        default=0,
        choices=[(0, 'Delivered'), (1, 'Online'), (2, 'Seen')],
        db_index=True
    )
    is_read = models.BooleanField(default=False)   # kept for older code

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['receiver', 'is_read', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.message or 'File'}"

# --- new model for reactions ---
class MessageReaction(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reactions',null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=True)
    emoji = models.CharField(max_length=10,null=True)   # e.g. "👍" or "heart"

    class Meta:
        unique_together = ('message', 'user', 'emoji')
        indexes = [models.Index(fields=['message'])]

    def __str__(self):
        return f"{self.user} reacted {self.emoji} to {self.message.id}"

class ChatRoom(models.Model):
    """
    Represents a direct chat room between two users (student and teacher/manager).
    """
    user1_id = models.IntegerField(help_text="ID of first participant (e.g., student).", default=0)
    user2_id = models.IntegerField(help_text="ID of second participant (e.g., teacher or manager).", default=0)
    created_at = models.DateTimeField(default=timezone.now)
    last_message = models.ForeignKey(
        ChatMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_room',
        help_text="The most recent message in this room."
    )

    class Meta:
        unique_together = ('user1_id', 'user2_id')
        verbose_name = "Chat Room"
        verbose_name_plural = "Chat Rooms"

    def save(self, *args, **kwargs):
        # Ensure user1_id < user2_id
        if self.user1_id > self.user2_id:
            self.user1_id, self.user2_id = self.user2_id, self.user1_id
        super().save(*args, **kwargs)

    @property
    def room_name(self):
        """Unique room name for WebSocket group."""
        return f"chat_{self.user1_id}_{self.user2_id}"

    def __str__(self):
        # Lazy load users if needed
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            u1 = User.objects.get(id=self.user1_id)
            u2 = User.objects.get(id=self.user2_id)
            return f"Chat between {u1.username} and {u2.username}"
        except User.DoesNotExist:
            return f"Chat Room {self.user1_id}-{self.user2_id}"


class TeacherClassStream(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='class_stream',
        null=True,
        blank=True
    )
    stream_name = models.CharField(max_length=100,null=True,blank=True)
    teacherclass=models.ManyToManyField(TeacherClass,blank=True)

    def __str__(self):
        return f'{self.stream_name}'



from django.db import models
from django.conf import settings


STUDENT_ACADEMIC_LEVEL_CHOICES = [
    ('FTNA', 'FTNA'),
    ('CSEE', 'CSEE'),
    ('ACSEE', 'ACSEE'),
    ('ECDE', 'ECDE'),
    ('English course', 'English course'),
    ('Computer course', 'Computer course'),
    ('pre form five', 'pre form five'),
]

STUDENT_ID_GROUP_CHOICES = [
    ('O_LEVEL', 'O level'),
    ('A_LEVEL', 'A level'),
    ('SHORT_COURSE', 'Short course'),
]


class StudentAcademicInformation(models.Model):
    student = models.OneToOneField(
        'Student',
        on_delete=models.CASCADE,
        related_name='academic_information',
        null=True,
        blank=True
    )
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    academic_level = models.CharField(max_length=100, choices=STUDENT_ACADEMIC_LEVEL_CHOICES, null=True, blank=True)
    academic_year = models.CharField(max_length=100, null=True, blank=True)
    class_name = models.CharField(max_length=100, null=True, blank=True)
    class_focus = models.CharField(max_length=100, null=True, blank=True)
    class_stream = models.CharField(max_length=100, null=True, blank=True)
    short_course_validity_months = models.PositiveSmallIntegerField(
        choices=[(3, "3 months"), (6, "6 months"), (12, "12 months")],
        null=True,
        blank=True
    )
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.student:
            return f"Academic Info - {self.student.fullName or self.student.user.username}"
        return "Academic Info"


class StudentIDAppearanceSetting(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_id_appearance_settings',
        null=True,
        blank=True
    )
    academic_level = models.CharField(max_length=50, choices=STUDENT_ACADEMIC_LEVEL_CHOICES, null=True, blank=True)
    group = models.CharField(max_length=50, choices=STUDENT_ID_GROUP_CHOICES, null=True, blank=True)
    use_badge = models.BooleanField(default=False)
    badge_text = models.CharField(max_length=50, null=True, blank=True)
    front_header_color = models.CharField(max_length=20, null=True, blank=True)
    front_body_color = models.CharField(max_length=20, null=True, blank=True)
    front_accent_color = models.CharField(max_length=20, null=True, blank=True)
    front_text_color = models.CharField(max_length=20, null=True, blank=True)
    back_header_color = models.CharField(max_length=20, null=True, blank=True)
    back_body_color = models.CharField(max_length=20, null=True, blank=True)
    back_accent_color = models.CharField(max_length=20, null=True, blank=True)
    back_text_color = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.academic_level or 'Student ID'} appearance - {self.user or 'global'}"

    class Meta:
        verbose_name = "Student ID Appearance Setting"
        verbose_name_plural = "Student ID Appearance Settings"
        unique_together = ('user', 'academic_level')


class StudentIDGlobalSetting(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_id_global_setting',
        null=True,
        blank=True
    )
    logo = models.ImageField(upload_to='student_id_logos/', null=True, blank=True)
    logo_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    horizontal_logo_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    vertical_logo_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    header_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    horizontal_header_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    vertical_header_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    title_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    horizontal_title_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    vertical_title_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    subtitle_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    vertical_subtitle_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    horizontal_subtitle_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    title_x_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    title_y_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horizontal_title_x_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horizontal_title_y_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vertical_title_x_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vertical_title_y_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    subtitle_x_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    subtitle_y_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horizontal_subtitle_x_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    horizontal_subtitle_y_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vertical_subtitle_x_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    vertical_subtitle_y_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    apply_layout_adjustments_horizontal = models.BooleanField(default=False)
    apply_layout_adjustments_vertical = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Student ID branding - {self.user or 'global'}"

    class Meta:
        verbose_name = "Student ID Global Setting"
        verbose_name_plural = "Student ID Global Settings"


class StudentGuardianInformation(models.Model):
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('grandparent', 'Grandparent'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]

    student = models.OneToOneField(
        'Student',
        on_delete=models.CASCADE,
        related_name='guardian_information',
        null=True,
        blank=True
    )
    guardian_name = models.CharField(max_length=150, null=True, blank=True)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    alternative_phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    occupation = models.CharField(max_length=150, null=True, blank=True)
    national_id = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    ward = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.student:
            return f"Guardian - {self.student.fullName or self.student.user.username}"
        return "Guardian Information"


class StudentSponsorInformation(models.Model):
    SPONSOR_TYPE_CHOICES = [
        ('parent', 'Parent'),
        ('guardian', 'Guardian'),
        ('company', 'Company'),
        ('organization', 'Organization'),
        ('government', 'Government'),
        ('ngo', 'NGO'),
        ('religious', 'Religious Institution'),
        ('other', 'Other'),
    ]

    student = models.OneToOneField(
        'Student',
        on_delete=models.CASCADE,
        related_name='sponsor_information',
        null=True,
        blank=True
    )
    sponsor_name = models.CharField(max_length=150, null=True, blank=True)
    sponsor_type = models.CharField(max_length=50, choices=SPONSOR_TYPE_CHOICES, null=True, blank=True)
    contact_person = models.CharField(max_length=150, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    alternative_phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    amount_supported = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_frequency = models.CharField(max_length=50, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.student:
            return f"Sponsor - {self.student.fullName or self.student.user.username}"
        return "Sponsor Information"


class StudentMedicalInformation(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    student = models.OneToOneField(
        'Student',
        on_delete=models.CASCADE,
        related_name='medical_information',
        null=True,
        blank=True
    )
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    chronic_conditions = models.TextField(null=True, blank=True)
    disabilities = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    doctor_name = models.CharField(max_length=150, null=True, blank=True)
    doctor_phone = models.CharField(max_length=30, null=True, blank=True)
    hospital_name = models.CharField(max_length=150, null=True, blank=True)
    hospital_phone = models.CharField(max_length=30, null=True, blank=True)
    insurance_provider = models.CharField(max_length=150, null=True, blank=True)
    insurance_number = models.CharField(max_length=100, null=True, blank=True)
    special_notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.student:
            return f"Medical - {self.student.fullName or self.student.user.username}"
        return "Medical Information"


class StudentEmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('grandparent', 'Grandparent'),
        ('guardian', 'Guardian'),
        ('friend', 'Friend'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=150, null=True, blank=True)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    alternative_phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_primary = models.BooleanField(default=False, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.student:
            return f"Emergency Contact - {self.full_name} ({self.student.fullName or self.student.user.username})"
        return self.full_name or "Emergency Contact"


class StudentPassportPhoto(models.Model):
    student = models.OneToOneField(
        'Student',
        on_delete=models.CASCADE,
        related_name='passport_photo_information',
        null=True,
        blank=True
    )
    passport_photo = models.ImageField(upload_to='student_passport_photos/', null=True, blank=True)
    photo_comment = models.CharField(max_length=255, null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        if self.student:
            return f"Passport Photo - {self.student.fullName or self.student.user.username}"
        return "Passport Photo"


from django.db import models
from django.conf import settings


class TeacherAcademicInformation(models.Model):
    teacher = models.OneToOneField(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='academic_information',
        null=True,
        blank=True
    )
    employee_id = models.CharField(max_length=100, null=True, blank=True)
    registration_number = models.CharField(max_length=100, null=True, blank=True)
    qualification = models.CharField(max_length=150, null=True, blank=True)
    specialization = models.CharField(max_length=150, null=True, blank=True)
    academic_level = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.teacher:
            return f"Teacher Academic Info - {self.teacher.teacherName or self.teacher.user.username}"
        return "Teacher Academic Information"


class TeacherPersonalInformation(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('other', 'Other'),
    ]

    teacher = models.OneToOneField(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='personal_information',
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=150, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    national_id = models.CharField(max_length=100, null=True, blank=True)
    passport_number = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    alternative_phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100, null=True, blank=True)
    ward = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.teacher:
            return f"Teacher Personal Info - {self.teacher.teacherName or self.teacher.user.username}"
        return "Teacher Personal Information"


class TeacherEmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('spouse', 'Spouse'),
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('uncle', 'Uncle'),
        ('aunt', 'Aunt'),
        ('friend', 'Friend'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]

    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        null=True,
        blank=True
    )
    full_name = models.CharField(max_length=150, null=True, blank=True)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES, null=True, blank=True)
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    alternative_phone_number = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_primary = models.BooleanField(default=False, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        teacher_name = self.teacher.teacherName if self.teacher else "Unknown Teacher"
        return f"{self.full_name or 'Emergency Contact'} - {teacher_name}"


class TeacherMedicalInformation(models.Model):
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    teacher = models.OneToOneField(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='medical_information',
        null=True,
        blank=True
    )
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    chronic_conditions = models.TextField(null=True, blank=True)
    disabilities = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    doctor_name = models.CharField(max_length=150, null=True, blank=True)
    doctor_phone = models.CharField(max_length=30, null=True, blank=True)
    hospital_name = models.CharField(max_length=150, null=True, blank=True)
    hospital_phone = models.CharField(max_length=30, null=True, blank=True)
    insurance_provider = models.CharField(max_length=150, null=True, blank=True)
    insurance_number = models.CharField(max_length=100, null=True, blank=True)
    special_notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.teacher:
            return f"Teacher Medical - {self.teacher.teacherName or self.teacher.user.username}"
        return "Teacher Medical Information"


class TeacherPassportPhoto(models.Model):
    teacher = models.OneToOneField(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='passport_photo_information',
        null=True,
        blank=True
    )
    passport_photo = models.ImageField(upload_to='teacher_passport_photos/', null=True, blank=True)
    photo_comment = models.CharField(max_length=255, null=True, blank=True)
    captured_at = models.DateTimeField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        if self.teacher:
            return f"Teacher Passport Photo - {self.teacher.teacherName or self.teacher.user.username}"
        return "Teacher Passport Photo"


class TeacherBankInformation(models.Model):
    teacher = models.OneToOneField(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='bank_information',
        null=True,
        blank=True
    )
    bank_name = models.CharField(max_length=150, null=True, blank=True)
    account_name = models.CharField(max_length=150, null=True, blank=True)
    account_number = models.CharField(max_length=100, null=True, blank=True)
    branch_name = models.CharField(max_length=150, null=True, blank=True)
    mobile_payment_name = models.CharField(max_length=150, null=True, blank=True)
    mobile_payment_number = models.CharField(max_length=30, null=True, blank=True)
    tin_number = models.CharField(max_length=100, null=True, blank=True)
    nssf_number = models.CharField(max_length=100, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        if self.teacher:
            return f"Teacher Bank Info - {self.teacher.teacherName or self.teacher.user.username}"
        return "Teacher Bank Information"


class TeacherContract(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('temporary', 'Temporary'),
        ('intern', 'Intern'),
        ('volunteer', 'Volunteer'),
        ('consultant', 'Consultant'),
        ('other', 'Other'),
    ]

    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='contracts',
        null=True,
        blank=True
    )
    contract_title = models.CharField(max_length=200, null=True, blank=True)
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES, null=True, blank=True)
    employer_name = models.CharField(max_length=150, null=True, blank=True)
    contract_reference = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    signed_date = models.DateField(null=True, blank=True)
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=20, null=True, blank=True)
    contract_file = models.FileField(upload_to='teacher_contracts/', null=True, blank=True)
    signed_contract_file = models.FileField(upload_to='teacher_contracts/signed/', null=True, blank=True)
    contract_notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=False, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        teacher_name = self.teacher.teacherName if self.teacher else "Unknown Teacher"
        return f"{self.contract_title or 'Contract'} - {teacher_name}"


class TeacherDocument(models.Model):
    teacher = models.ForeignKey(
        'Teacher',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    document_name = models.CharField(max_length=150, null=True, blank=True)
    document_type = models.CharField(max_length=100, null=True, blank=True)
    document_file = models.FileField(upload_to='teacher_documents/', null=True, blank=True)
    document_number = models.CharField(max_length=100, null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        teacher_name = self.teacher.teacherName if self.teacher else "Unknown Teacher"
        return f"{self.document_name or 'Document'} - {teacher_name}"


class Vehicle(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicles',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)  # e.g. "School Bus 1"
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50,null=True)  # Bus, Van, etc.
    capacity = models.PositiveIntegerField(null=True)

    driver = models.ForeignKey(
        'Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'teacher_role': 'driver'}
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.plate_number}"


class Route(models.Model):
    name = models.CharField(max_length=100,null=True)  # e.g. "Mbagala Route"
    start_location = models.CharField(max_length=100,null=True)
    end_location = models.CharField(max_length=100,null=True)

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='routes',null=True)

    def __str__(self):
        return self.name


class FuelRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_records',null=True)
    date = models.DateField(null=True)
    liters = models.FloatField(null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2,null=True)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.vehicle} - {self.liters}L"
    

class Maintenance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenances',null=True)
    description = models.TextField(null=True)  # Oil change, repair, etc.
    cost = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.description}"


class VehicleExpense(models.Model):
    EXPENSE_TYPES = [
        ('latra', 'LATRA'),
        ('fine', 'Traffic Fine'),
        ('insurance', 'Insurance'),
        ('other', 'Other'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='expenses',null=True)
    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES,null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    description = models.TextField(blank=True,null=True)
    date = models.DateField(null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.expense_type}"


class CRMLead(models.Model):
    ACADEMIC_CLASS_CHOICES = [
        ('pre form one', 'pre form one'),
        ('FTNA', 'FTNA'),
        ('CSEE', 'CSEE'),
        ('ACSEE', 'ACSEE'),
        ('pre form five', 'pre form five'),
        ('computer course', 'computer course'),
        ('english course', 'english course'),
        ('ECDE', 'ECDE'),
    ]

    SOURCE_CHOICES = [
        ('Walk In', 'Walk In'),
        ('Call', 'Call'),
        ('WhatsApp', 'WhatsApp'),
        ('Website', 'Website'),
        ('Referral', 'Referral'),
        ('Social Media', 'Social Media'),
        ('Other', 'Other'),
    ]

    HOW_DID_YOU_KNOW_US_CHOICES = [
        ('Friend', 'Friend'),
        ('Parent', 'Parent'),
        ('Social Media', 'Social Media'),
        ('Website', 'Website'),
        ('Advertisement', 'Advertisement'),
        ('Walk In', 'Walk In'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('New', 'New'),
        ('Contacted', 'Contacted'),
        ('Interested', 'Interested'),
        ('Follow Up', 'Follow Up'),
        ('Enrolled', 'Enrolled'),
        ('Closed', 'Closed'),
        ('Lost', 'Lost'),
    ]

    name = models.CharField(max_length=180)
    phone = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    student_first_name = models.CharField(max_length=120, null=True, blank=True)
    student_middle_name = models.CharField(max_length=120, null=True, blank=True)
    student_last_name = models.CharField(max_length=120, null=True, blank=True)
    academic_class = models.CharField(max_length=40, choices=ACADEMIC_CLASS_CHOICES)
    focus = models.CharField(max_length=140, null=True, blank=True)
    source = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    how_did_you_know_us = models.CharField(max_length=30, choices=HOW_DID_YOU_KNOW_US_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='New')
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_leads',
    )
    served_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='served_crm_leads',
        help_text='The actual logged-in user who recorded/served this CRM lead.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def _user_display_name(self, user):
        if not user:
            return "Unknown"
        full_name = user.get_full_name().strip()
        return full_name or getattr(user, 'username', None) or getattr(user, 'email', None) or "Unknown"

    def served_by_name(self):
        return self._user_display_name(self.served_by)

    def owner_name(self):
        return self._user_display_name(self.created_by)

    def __str__(self):
        lead_name = self.name or "Unnamed Lead"
        lead_phone = self.phone or "No phone"
        return f"{lead_name} ({lead_phone})"


class StudentApplication(models.Model):
    STATUS_CHOICES = [
        ("not_returned", "Not Returned"),
        ("on_progress", "On Progress"),
        ("admitted", "Admitted"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_applications",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    application_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    academic_level = models.CharField(max_length=100, null=True, blank=True)
    academic_year = models.ForeignKey(AcademicClassYear, on_delete=models.SET_NULL, null=True, blank=True)
    class_name = models.CharField(max_length=100, null=True, blank=True)
    class_focus = models.CharField(max_length=100, null=True, blank=True)
    application_type = models.CharField(max_length=50, null=True, blank=True)
    entry_mode = models.CharField(max_length=50, null=True, blank=True)
    application_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    national_id_number = models.CharField(max_length=100, null=True, blank=True)

    guardian_first_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_middle_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_last_name = models.CharField(max_length=100, null=True, blank=True)
    guardian_email = models.EmailField(null=True, blank=True)
    guardian_phone = models.CharField(max_length=50, null=True, blank=True)
    guardian_address = models.CharField(max_length=255, null=True, blank=True)
    guardian_occupation = models.CharField(max_length=100, null=True, blank=True)

    sponsor_type = models.CharField(max_length=50, null=True, blank=True)
    sponsor_name = models.CharField(max_length=150, null=True, blank=True)
    sponsor_email = models.EmailField(null=True, blank=True)
    sponsor_phone = models.CharField(max_length=50, null=True, blank=True)
    sponsor_address = models.CharField(max_length=255, null=True, blank=True)
    sponsor_details = models.TextField(null=True, blank=True)

    personal_skills = models.TextField(null=True, blank=True)
    previous_school = models.CharField(max_length=255, null=True, blank=True)
    preferred_session_time = models.CharField(max_length=50, null=True, blank=True)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="not_returned", null=True, blank=True)
    student = models.ForeignKey("Student", on_delete=models.SET_NULL, null=True, blank=True, related_name="applications")

    class Meta:
        ordering = ["-created_at"]

    @property
    def full_name(self):
        return " ".join(part for part in [self.first_name, self.middle_name, self.last_name] if part).strip()

    @property
    def guardian_full_name(self):
        return " ".join(part for part in [self.guardian_first_name, self.guardian_middle_name, self.guardian_last_name] if part).strip()

    def __str__(self):
        return f"{self.application_number or 'Application'} - {self.full_name or 'Unnamed'}"
