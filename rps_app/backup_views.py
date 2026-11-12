# # Standard Django Imports
# from django.contrib import messages
# from django.contrib.auth import (
#     authenticate,
#     get_user_model,
#     login as auth_login,
#     logout,
#     update_session_auth_hash,
# )
# from website.models import About,Contact,Footer,Gallery,Service
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.contrib.auth.forms import PasswordChangeForm
# from django.core.exceptions import (
#     MultipleObjectsReturned,
#     ObjectDoesNotExist,
#     ValidationError,
# )
# from finance.models import StudentFocus,StudentRegistration
# from django.core.paginator import Paginator
# from django.db import transaction
# from django.db.models import Avg, Count, Prefetch, Q, Sum
# from django.http import HttpResponse, JsonResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.template.loader import render_to_string
# from django.urls import reverse
# from django.utils import timezone
# from django.db import models
# from django.contrib.sessions.models import Session
# # Project-Specific Imports
# from .forms import StudentSubjectForm, TeacherSubjectForm
# from .models import (
#     DisplayModel,
#     EmailVerificationOTP,
#     ExaminationName,
#     ExcludeSubject,
#     GradingModel,
#     Mark,
#     RequiredSubject,
#     Student,
#     StudentSubject,
#     Subject,
#     Teacher,
#     TeacherClass,
#     TeacherSubject,
#     TermMarksUpload,
#     User,
#     UserSessionAccount,
# )

# # Third-Party Library Imports
# import pandas as pd
# import requests
# import tabula
# from openpyxl import Workbook
# from openpyxl.styles import Alignment, Border, Font, Side
# from openpyxl.utils import get_column_letter
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.units import inch
# from reportlab.platypus import (
#     KeepTogether,
#     PageBreak,
#     Paragraph,
#     SimpleDocTemplate,
#     Spacer,
#     Table,
#     TableStyle,
# )
# from requests.auth import HTTPBasicAuth
# from django.db.models import Q as models_Q
# # Standard Python Libraries
# import json
# import logging
# import os
# import re
# from datetime import datetime
# from io import BytesIO



# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.shortcuts import redirect, render, get_object_or_404
# from django.urls import reverse
# from .models import Student, TeacherClass, User



# @login_required
# @transaction.atomic
# def create_student(request):
#     # Authorization: Ensure only teachers can access this view
#     if not request.user.is_teacher:
#         messages.error(request, "You are not authorized to perform this action.")
#         return redirect('teacher_dashboard')

#     # Handle POST request for creating a student
#     if request.method == 'POST':
#         fullName = request.POST.get('fullName', '').strip()
#         sex = request.POST.get('sex', '').strip().upper()
#         indexNumber = request.POST.get('indexNumber', '').strip()
#         teacherclass_id = request.POST.get('teacherclass')
#         contact = request.POST.get('contact', '').strip()

#         if not all([fullName, sex, indexNumber, teacherclass_id, contact]):
#             messages.error(request, "All fields are required.")
#             return redirect(f"{reverse('create_student')}?class={teacherclass_id or ''}")

#         try:
#             teacherclass = get_object_or_404(TeacherClass, id=teacherclass_id, user=request.user)

#             # ✅ Check if student with this indexNumber already exists under another manager
#             if Student.objects.filter(
#                 Q(indexNumber=indexNumber, teacherclass=teacherclass) |
#                 Q(indexNumber=indexNumber)
#             ).exclude(manager=request.user).exists():
#                 messages.error(
#                     request,
#                     f"A student with index number {indexNumber} already exists (managed by another user)."
#                 )
#                 return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#             # ✅ Check if a User with this indexNumber (username) exists or create new
#             username = indexNumber
#             password = str(contact)  # Default password = contact number
#             user, user_created = User.objects.get_or_create(
#                 username=username,
#                 defaults={'is_student': True, 'is_teacher': False}
#             )

#             if user_created:
#                 user.set_password(password)
#                 user.save()

#             # ✅ Check if a Student profile already exists for this class (same manager)
#             if Student.objects.filter(user=user, teacherclass=teacherclass, manager=request.user).exists():
#                 messages.error(
#                     request,
#                     f"A student with index number {indexNumber} already exists in this class."
#                 )
#                 return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#             # ✅ Create the Student profile
#             student = Student.objects.create(
#                 user=user,
#                 indexNumber=indexNumber,
#                 fullName=fullName,
#                 sex=sex,
#                 contact=contact,
#                 teacherclass=teacherclass,
#                 manager=request.user
#             )

#             messages.success(
#                 request,
#                 f"Student {fullName} created successfully. "
#                 f"Username: {indexNumber}, Default Password: {contact}"
#             )
#             return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#         except Exception as e:
#             messages.error(request, f"An unexpected error occurred: {str(e)}")
#             return redirect(f"{reverse('create_student')}?class={teacherclass_id or ''}")

#     # ✅ Handle GET request
#     classes = TeacherClass.objects.filter(
#         user=request.user,
#         academicclassyear__active_year=True
#     ).order_by('ClassName')

#     selected_class_id = request.GET.get('class')
#     students = Student.objects.none()
#     selected_class = None

#     if selected_class_id:
#         selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=request.user)
#         students = Student.objects.filter(
#             manager=request.user,
#             teacherclass=selected_class
#         ).order_by('fullName').select_related('user')

#     context = {
#         'classes': classes,
#         'students': students,
#         'selected_class': selected_class,
#     }
#     return render(request, 'create_student.html', context)


# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db import transaction
# from django.shortcuts import redirect, get_object_or_404
# from django.urls import reverse
# from django.db.models import Q
# import pandas as pd

# from .models import Student, TeacherClass, User


# @login_required
# @transaction.atomic
# def upload_students(request):
#     if not request.user.is_teacher:
#         messages.error(request, "You are not authorized to perform this action.")
#         return redirect('teacher_dashboard')

#     if request.method == 'POST':
#         teacherclass_id = request.POST.get('teacherclass')
#         if not teacherclass_id:
#             messages.error(request, "Please select a class before uploading.")
#             return redirect('create_student')

#         try:
#             teacherclass = get_object_or_404(
#                 TeacherClass,
#                 id=teacherclass_id,
#                 user=request.user,
#                 academicclassyear__active_year=True
#             )

#             file = request.FILES.get('file')
#             if not file:
#                 messages.error(request, "No file was uploaded.")
#                 return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#             # File reading and validation
#             file_extension = file.name.split('.')[-1].lower()
#             if file_extension == 'csv':
#                 df = pd.read_csv(file)
#             elif file_extension in ['xls', 'xlsx']:
#                 df = pd.read_excel(file)
#             else:
#                 messages.error(request, "Unsupported file format. Please upload a CSV or Excel file.")
#                 return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#             # Ensure required columns exist
#             required_columns = ['fullName', 'sex', 'indexNumber', 'contact']
#             if not all(col in df.columns for col in required_columns):
#                 messages.error(
#                     request,
#                     "File must contain 'fullName', 'sex', 'indexNumber', and 'contact' columns."
#                 )
#                 return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#             for index, row in df.iterrows():
#                 try:
#                     index_number = str(row['indexNumber']).strip()
#                     full_name = str(row['fullName']).strip()
#                     contact = str(row['contact']).strip()
#                     sex = str(row['sex']).strip().upper()

#                     if not all([index_number, full_name, contact, sex]):
#                         messages.warning(request, f"Skipping row {index + 2}: Contains empty required values.")
#                         continue

#                     if sex not in ['M', 'F', 'O']:
#                         messages.warning(request, f"Skipping row {index + 2}: Invalid sex value. Must be 'M', 'F', or 'O'.")
#                         continue

#                 except (ValueError, TypeError) as e:
#                     messages.warning(request, f"Skipping row {index + 2}: Invalid data format. Error: {e}")
#                     continue

#                 # Check for existing student in the same teacherclass
#                 existing_student = Student.objects.filter(
#                     indexNumber=index_number,
#                     teacherclass=teacherclass,
#                     manager=request.user
#                 ).first()

#                 username = index_number

#                 # Check if indexNumber is used by another manager
#                 if Student.objects.filter(
#                     Q(indexNumber=index_number)
#                 ).exclude(manager=request.user).exists():
#                     messages.warning(
#                         request,
#                         f"Skipping row {index + 2}: Student with index number {index_number} already exists (managed by another user)."
#                     )
#                     continue

#                 # Update or create the User object
#                 user, user_created = User.objects.get_or_create(
#                     username=username,
#                     defaults={'is_student': True, 'is_teacher': False}
#                 )

#                 if user_created:
#                     user.set_password(contact)  # Default password = contact
#                     user.save()
#                 elif existing_student:
#                     # Update user password if student exists
#                     user.set_password(contact)
#                     user.save()

#                 if existing_student:
#                     # Update existing student
#                     existing_student.fullName = full_name
#                     existing_student.sex = sex
#                     existing_student.contact = contact
#                     existing_student.save()
#                     messages.success(request, f"Student '{full_name}' updated successfully.")
#                 else:
#                     # Create new student
#                     Student.objects.create(
#                         user=user,
#                         indexNumber=index_number,
#                         fullName=full_name,
#                         sex=sex,
#                         contact=contact,
#                         teacherclass=teacherclass,
#                         manager=request.user,
#                     )
#                     messages.success(request, f"Student '{full_name}' created successfully.")

#         except Exception as e:
#             messages.error(request, f"A critical error occurred while processing the file: {str(e)}")
#             return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#         return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#     return redirect('create_student')

# @login_required
# def delete_student(request, id):
#     # Retrieve the student managed by the current user
#     student = get_object_or_404(Student, id=id, manager=request.user)
#     teacherclass_id = student.teacherclass.id

#     if request.method == 'POST':
#         student_user = student.user
#         student.delete()
#         student_user.delete()  # Delete the associated User
#         messages.success(request, f"Student '{student.fullName}' deleted successfully.")
#         return redirect(f"{reverse('create_student')}?class={teacherclass_id}")

#     return render(request, 'confirm_deletion.html', {'message': student.fullName})




# @login_required
# @transaction.atomic
# def update_student(request, id):
#     # Retrieve the student managed by the current user
#     student = get_object_or_404(Student, id=id, manager=request.user)
    
#     # Fetch all TeacherClass instances assigned to the user, ordered by ClassName
#     teacher_classes = TeacherClass.objects.filter(
#         user=request.user
#     ).select_related('ClassName', 'academicclassyear').order_by('ClassName__class_name')

#     if request.method == 'POST':
#         fullName = request.POST.get('fullName', '').strip()
#         sex = request.POST.get('sex', '').strip().upper()
#         indexNumber = request.POST.get('indexNumber', '').strip()
#         teacherclass_id = request.POST.get('teacherclass')
#         contact = request.POST.get('contact', '').strip()

#         # Validate inputs
#         if not all([fullName, sex, indexNumber, contact]):
#             messages.error(request, "All fields are required.")
#             return render(request, 'update_student.html', {'st': student, 'teacher_classes': teacher_classes})

#         # Get the selected TeacherClass
#         teacher_class = student.teacherclass
#         if teacherclass_id:
#             teacher_class = get_object_or_404(TeacherClass, id=teacherclass_id, user=request.user)

#         # Check if indexNumber already exists in this class or under another manager (excluding current student)
#         if Student.objects.filter(
#             Q(indexNumber=indexNumber, teacherclass=teacher_class) |
#             Q(indexNumber=indexNumber)
#         ).exclude(id=student.id).exclude(manager=request.user).exists():
#             messages.error(
#                 request,
#                 f'Index number "{indexNumber}" is already used by another student (possibly managed by another teacher).'
#             )
#             return render(request, 'update_student.html', {'st': student, 'teacher_classes': teacher_classes})

#         # Check if the username is unique in User model (excluding current student)
#         if student.user.username != indexNumber and User.objects.filter(username=indexNumber).exclude(id=student.user.id).exists():
#             messages.error(request, f'Username "{indexNumber}" is already in use by another user.')
#             return render(request, 'update_student.html', {'st': student, 'teacher_classes': teacher_classes})

#         # Update student fields
#         student.fullName = fullName
#         student.sex = sex
#         student.indexNumber = indexNumber
#         student.contact = contact
#         student.teacherclass = teacher_class
#         student.save()

#         # Update associated User
#         student.user.username = indexNumber
#         student.user.set_password(str(contact))
#         student.user.save()

#         messages.success(request, f'{student.fullName} updated successfully. New password set to: {contact}')
#         return redirect(f"{reverse('create_student')}?class={student.teacherclass.id}")

#     return render(request, 'update_student.html', {
#         'st': student,
#         'teacher_classes': teacher_classes,
#     })



# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from .models import User, Teacher

# @login_required
# @transaction.atomic
# def create_teacher(request):
#     # Authorization: Only superusers or teachers with is_teacher=True can create users
#     if not (request.user.is_superuser or request.user.is_teacher):
#         messages.error(request, "You don’t have permission to create users.")
#         return redirect('homepage')

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         teacher_name = request.POST.get('teacherName')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirmPassword')  # New field for password confirmation
#         teacher_key = request.POST.get('teacher_key')
#         role = request.POST.get('role')

#         # Validate all required fields
#         required_fields = [username, teacher_name, email, password, confirm_password, role]
#         if not all(required_fields):
#             messages.error(request, 'All fields are required.')
#             return redirect('create_teacher')

#         # Validate password confirmation
#         if password != confirm_password:
#             messages.error(request, 'Passwords do not match.')
#             return redirect('create_teacher')

#         # Validate teacher_key for Teachers and Accountants
#         if role in ['Teacher', 'Accountant'] and not teacher_key:
#             messages.error(request, 'Teacher key is required for Teachers and Accountants.')
#             return redirect('create_teacher')

#         # Uniqueness checks
#         if User.objects.filter(username=username).exists():
#             messages.error(request, f'A user with username "{username}" already exists.')
#             return redirect('create_teacher')
#         if User.objects.filter(email=email).exists():
#             messages.error(request, f'A user with email "{email}" already exists.')
#             return redirect('create_teacher')
#         if role in ['Teacher', 'Accountant'] and teacher_key and Teacher.objects.filter(teacher_key=teacher_key).exists():
#             messages.error(request, f'A teacher with key "{teacher_key}" already exists.')
#             return redirect('create_teacher')

#         try:
#             # Set user attributes based on role
#             is_teacher = role in ['Teacher', 'Accountant']
#             is_staff = role == 'Accountant'
#             is_active = True  # All roles are active by default

#             # Create the User object
#             new_user = User.objects.create_user(
#                 username=username,
#                 email=email,
#                 password=password,
#                 is_teacher=is_teacher,
#                 is_student=False,
#                 is_staff=is_staff,
#                 is_active=is_active
#             )

#             # Create Teacher profile for Teachers and Accountants
#             if role in ['Teacher', 'Accountant']:
#                 Teacher.objects.create(
#                     user=new_user,
#                     teacherName=teacher_name,
#                     teacher_key=teacher_key,
#                     created_by=request.user if request.user.is_teacher else None
#                 )

#             messages.success(request, f'User "{teacher_name}" ({role}) was created successfully!')
#             return redirect('create_teacher')

#         except Exception as e:
#             messages.error(request, f'An unexpected error occurred: {str(e)}')
#             return redirect('create_teacher')

#     # GET request: Display existing teachers created by the current user
#     teachers = Teacher.objects.filter(created_by=request.user)
#     return render(request, 'teachers.html', {'teachers': teachers})

# from django.contrib.auth.decorators import login_required
# from django.db import transaction
# from django.contrib import messages
# from django.shortcuts import redirect, render
# from django.contrib.auth import get_user_model
# from rps_app.models import Teacher

# User = get_user_model()

# @login_required
# @transaction.atomic
# def update_teacher(request, teacher_id):
#     # Authorization: Only superusers or teachers with is_teacher=True can update users
#     if not (request.user.is_superuser or request.user.is_teacher):
#         messages.error(request, "You don’t have permission to update users.")
#         return redirect('create_teacher')

#     try:
#         teacher = Teacher.objects.get(id=teacher_id)
#         user = teacher.user
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher not found.")
#         return redirect('create_teacher')

#     if request.method == 'POST':
#         username = request.POST.get('username')
#         teacher_name = request.POST.get('teacherName')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirmPassword')
#         teacher_key = request.POST.get('teacher_key')
#         role = request.POST.get('role')

#         # Validate required fields
#         required_fields = [username, teacher_name, email, role]
#         if not all(required_fields):
#             messages.error(request, 'All fields except password are required.')
#             return redirect('update_teacher', teacher_id=teacher_id)

#         # Validate password if provided
#         if password or confirm_password:
#             if password != confirm_password:
#                 messages.error(request, 'Passwords do not match.')
#                 return redirect('update_teacher', teacher_id=teacher_id)

#         # Validate teacher_key for Teachers and Accountants
#         if role in ['Teacher', 'Accountant'] and not teacher_key:
#             messages.error(request, 'Teacher key is required for Teachers and Accountants.')
#             return redirect('update_teacher', teacher_id=teacher_id)

#         # Uniqueness checks (exclude current user/teacher)
#         if User.objects.filter(username=username).exclude(id=user.id).exists():
#             messages.error(request, f'A user with username "{username}" already exists.')
#             return redirect('update_teacher', teacher_id=teacher_id)
#         if User.objects.filter(email=email).exclude(id=user.id).exists():
#             messages.error(request, f'A user with email "{email}" already exists.')
#             return redirect('update_teacher', teacher_id=teacher_id)
#         if role in ['Teacher', 'Accountant'] and teacher_key and Teacher.objects.filter(teacher_key=teacher_key).exclude(id=teacher.id).exists():
#             messages.error(request, f'A teacher with key "{teacher_key}" already exists.')
#             return redirect('update_teacher', teacher_id=teacher_id)

#         try:
#             # Update User object
#             user.username = username
#             user.email = email
#             if password:  # Update password only if provided
#                 user.set_password(password)
#             user.is_teacher = role in ['Teacher', 'Accountant']
#             user.is_staff = role == 'Accountant'
#             user.is_active = True
#             user.save()

#             # Update Teacher profile
#             teacher.teacherName = teacher_name
#             if role in ['Teacher', 'Accountant']:
#                 teacher.teacher_key = teacher_key
#             else:
#                 teacher.teacher_key = None  # Clear teacher_key for Content Creator
#             teacher.save()

#             messages.success(request, f'User "{teacher_name}" ({role}) was updated successfully!')
#             return redirect('create_teacher')

#         except Exception as e:
#             messages.error(request, f'An unexpected error occurred: {str(e)}')
#             return redirect('update_teacher', teacher_id=teacher_id)

#     # GET request: Render update form
#     return render(request, 'update_teacher.html', {
#         'teacher': teacher,
#         'user': user,
#     })



# @login_required
# def delete_teacher(request, id):
#     # Retrieve the teacher profile (id is the Teacher model's primary key)
#     teacher_profile = get_object_or_404(Teacher, id=id)

#     # Permission Check: Superuser or the original creator can delete
#     if not (request.user.is_superuser or teacher_profile.created_by == request.user):
#         messages.error(request, "You don’t have permission to delete this teacher.")
#         return redirect('teacher_dashboard')

#     if request.method == 'POST':
#         teacher_name = teacher_profile.teacherName
#         # Delete the User object (cascades to Teacher profile)
#         teacher_profile.user.delete()
#         messages.success(request, f'Teacher "{teacher_name}" was deleted successfully.')
#         return redirect('create_teacher')

#     return render(request, 'confirm_deletion.html', {'message': teacher_profile.teacherName})


# @login_required
# def update_teacher(request, id):
#     # Retrieve the teacher profile (id is the Teacher model's primary key)
#     teacher_profile = get_object_or_404(Teacher, id=id)

#     # Permission Check: Superuser or the original creator can update
#     if not (request.user.is_superuser or teacher_profile.created_by == request.user):
#         messages.error(request, "You don’t have permission to update this teacher.")
#         return redirect('teacher_dashboard')

#     if request.method == 'POST':
#         teacher_name = request.POST.get('teacherName', teacher_profile.teacherName)
#         new_teacher_key = request.POST.get('teacher_key', teacher_profile.teacher_key)
#         email = request.POST.get('email', teacher_profile.user.email)
#         password = request.POST.get('password')

#         # Check if the new teacher key is unique
#         if Teacher.objects.filter(teacher_key=new_teacher_key).exclude(id=id).exists():
#             messages.error(request, f'The teacher key "{new_teacher_key}" is already in use.')
#             return render(request, 'update_teacher.html', {'teacher': teacher_profile})

#         # Check if the email is unique
#         if email != teacher_profile.user.email and User.objects.filter(email=email).exists():
#             messages.error(request, f'A user with email "{email}" already exists.')
#             return render(request, 'update_teacher.html', {'teacher': teacher_profile})

#         # Update teacher profile
#         teacher_profile.teacherName = teacher_name
#         teacher_profile.teacher_key = new_teacher_key
#         teacher_profile.save()

#         # Update user details
#         teacher_profile.user.email = email
#         if password:
#             teacher_profile.user.set_password(password)
#         teacher_profile.user.save()

#         messages.success(request, f'Teacher "{teacher_profile.teacherName}" was updated successfully.')
#         return redirect('create_teacher')

#     return render(request, 'update_teacher.html', {'teacher': teacher_profile})
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.contrib import messages
# from .models import Subject, TeacherClass, Teacher

# @login_required
# def create_subject(request):
#     # Ensure the user is a teacher
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can create subjects.")
#         return redirect('homepage')

#     try:
#         # Get the teacher's profile
#         teacher_profile = Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     # Get classes managed by the teacher (created_by or user)
#     teacher_classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)

#     if request.method == 'POST':
#         nameSubject = request.POST.get('nameSubject')
#         teacherclass_id = request.POST.get('teacherclass')

#         # Validate inputs
#         if not nameSubject:
#             messages.error(request, "Subject name is required.")
#             return render(request, 'subjects.html', {
#                 'subjects': Subject.objects.filter(user=request.user),
#                 'teacher_classes': teacher_classes
#             })

#         # Validate teacherclass if provided
#         teacherclass = None
#         if teacherclass_id:
#             try:
#                 teacherclass = TeacherClass.objects.get(id=teacherclass_id, user=request.user,academiclassyear__active_year=True)
#             except TeacherClass.DoesNotExist:
#                 messages.error(request, "Selected class is invalid or not managed by you.")
#                 return render(request, 'subjects.html', {
#                     'subjects': Subject.objects.filter(user=request.user),
#                     'teacher_classes': teacher_classes
#                 })

#         # Create the subject
#         subject = Subject.objects.create(
#             user=request.user,
#             nameSubject=nameSubject,
#             teacherclass=teacherclass
#         )
#         messages.success(request, f'Subject "{nameSubject}" added successfully!')
#         return render(request, 'subjects.html', {
#             'subjects': Subject.objects.filter(user=request.user),
#             'teacher_classes': teacher_classes
#         })
#     else:
#         # GET request: Show the form and existing subjects
#         return render(request, 'subjects.html', {
#             'subjects': Subject.objects.filter(user=request.user),
#             'teacher_classes': teacher_classes
#         })

# @login_required
# def delete_subject(request, id):
#     # Ensure the user is a teacher
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can delete subjects.")
#         return redirect('homepage')

#     # Retrieve the subject for the current user
#     global_subject = get_object_or_404(Subject, id=id, user=request.user)
#     teacher_classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)

#     if request.method == 'POST':
#         subject_name = global_subject.nameSubject
#         global_subject.delete()
#         messages.success(request, f'{subject_name} deleted successfully')
#         return render(request, 'subjects.html', {
#             'subjects': Subject.objects.filter(user=request.user),
#             'teacher_classes': teacher_classes
#         })
#     return render(request, 'confirm_deletion.html', {
#         'message': global_subject.nameSubject,
#         'subject': global_subject
#     })

# @login_required
# def update_subject(request, id):
#     # Ensure the user is a teacher
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can update subjects.")
#         return redirect('homepage')

#     # Retrieve the subject for the current user
#     global_subject = get_object_or_404(Subject, id=id, user=request.user)
#     teacher_classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)

#     if request.method == 'POST':
#         nameSubject = request.POST.get('nameSubject')
#         teacherclass_id = request.POST.get('teacherclass')

#         # Validate inputs
#         if not nameSubject:
#             messages.error(request, "Subject name is required.")
#             return render(request, 'update_subject.html', {
#                 'subject': global_subject,
#                 'teacher_classes': teacher_classes
#             })

#         # Validate teacherclass if provided
#         teacherclass = None
#         if teacherclass_id:
#             try:
#                 teacherclass = TeacherClass.objects.get(id=teacherclass_id, user=request.user,academicclassyear__active_year=True)
#             except TeacherClass.DoesNotExist:
#                 messages.error(request, "Selected class is invalid or not managed by you.")
#                 return render(request, 'update_subject.html', {
#                     'subject': global_subject,
#                     'teacher_classes': teacher_classes
#                 })

#         # Update subject data
#         global_subject.nameSubject = nameSubject
#         global_subject.teacherclass = teacherclass
#         global_subject.save()

#         messages.success(request, f'{global_subject.nameSubject} updated successfully')
#         return render(request, 'subjects.html', {
#             'subjects': Subject.objects.filter(user=request.user),
#             'teacher_classes': teacher_classes
#         })
#     return render(request, 'update_subject.html', {
#         'message': f'Update, {global_subject.nameSubject}',
#         'subject': global_subject,
#         'teacher_classes': teacher_classes
#     })



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.contrib import messages
# from .forms import TeacherSubjectForm
# from .models import TeacherSubject


# @login_required
# def assign_teachers(request):
#     # Fetch all TeacherSubject assignments for the current user
#     teacher_subjects = TeacherSubject.objects.filter(
#         user=request.user
#     ).select_related('teacher', 'subject', 'teacherclass', 'teacherclass__ClassName', 'teacherclass__academicclassyear')

#     if request.method == 'POST':
#         form = TeacherSubjectForm(
#             request.POST,
#             user=request.user,
#             initial_teacher_id=request.session.get('selected_teacher_id'),
#             initial_teacherclass_id=request.session.get('selected_teacherclass_id')
#         )
#         if form.is_valid():
#             teacher_subject = form.save(commit=False)
#             teacher_subject.user = request.user  # The creator
#             teacher_subject.save()
#             # Store selected teacher and teacherclass in session
#             request.session['selected_teacher_id'] = str(teacher_subject.teacher.id)
#             request.session['selected_teacherclass_id'] = str(teacher_subject.teacherclass.id)
#             messages.success(
#                 request,
#                 f'Teacher {teacher_subject.teacher.teacherName} assigned to {teacher_subject.subject.nameSubject} in {teacher_subject.teacherclass.ClassName.class_name} ({teacher_subject.teacherclass.academicclassyear.academic_year_name or "No Academic Year"}) successfully'
#             )
#             # Reset form with preselected teacher and teacherclass
#             form = TeacherSubjectForm(
#                 user=request.user,
#                 initial_teacher_id=request.session.get('selected_teacher_id'),
#                 initial_teacherclass_id=request.session.get('selected_teacherclass_id')
#             )
#         else:
#             messages.error(request, 'Failed to assign teacher. Please check the form.')
#     else:
#         # Initialize form with preselected values from session
#         form = TeacherSubjectForm(
#             user=request.user,
#             initial_teacher_id=request.session.get('selected_teacher_id'),
#             initial_teacherclass_id=request.session.get('selected_teacherclass_id')
#         )

#     return render(request, 'assign_teachers.html', {
#         'form': form,
#         'teacher_subjects': teacher_subjects,
#     })




# @login_required
# def teacher_subject_list(request):
#     # Fetch teacher-subject associations for the current user with related data
#     teacher_subjects = TeacherSubject.objects.filter(
#         user=request.user
#     ).select_related('teacher', 'subject', 'teacherclass', 'teacherclass__academicclassyear', 'teacherclass__ClassName')
    
#     return render(request, 'teacher_subject_list.html', {'teacher_subjects': teacher_subjects})



# @login_required
# def delete_assigned_teacher(request, id):
#     """
#     View to delete a TeacherSubject record with confirmation, ensuring it belongs to the current user.
#     """
#     # Retrieve the teacher-subject association for the current user only
#     teacher_subject = get_object_or_404(TeacherSubject, id=id, user=request.user)

#     if request.method == 'POST':
#         # Delete the record
#         teacher_subject.delete()
#         messages.success(request, "Record deleted successfully.")
#         return redirect('teacher_subject_list')  # Adjust the URL name to match your list view

#     # Render the confirmation page if the request method is GET
#     return render(request, 'confirm_deletion.html', {'teacher_subject': teacher_subject})


# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .forms import TeacherSubjectForm
# from .models import TeacherSubject

# @login_required
# def update_teacher_subject(request, id):
#     # Fetch TeacherSubject with related teacherclass and academicclassyear, ensuring active year
#     teacher_subject = get_object_or_404(
#         TeacherSubject,
#         id=id,
#         user=request.user,
#         teacherclass__academicclassyear__active_year=True
#     )
    
#     if request.method == 'POST':
#         form = TeacherSubjectForm(request.POST, instance=teacher_subject, user=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request,
#                 f'Teacher assignment for {teacher_subject.teacher.teacherName} in {teacher_subject.subject.nameSubject} ({teacher_subject.teacherclass.ClassName.class_name}) updated successfully.'
#             )
#             return redirect('assign_teachers')
#         else:
#             messages.error(request, 'Failed to update assignment. Please check the form.')
#     else:
#         form = TeacherSubjectForm(instance=teacher_subject, user=request.user)

#     return render(request, 'update_teacher_subject.html', {
#         'form': form,
#         'teacher_subject': teacher_subject,
#     })




# @login_required
# def teacher_students_subjects_view(request):
#     if request.method == 'POST':
#         teacher_id = request.POST.get('teacher_id')

#         # Handle restriction updates if coming from the teacher subject list
#         if not teacher_id:  # Only process restrictions if no teacher_id is present
#             # Get all TeacherSubject objects for the current user to check against
#             teacher_subjects = TeacherSubject.objects.filter(user=request.user)
#             for ts in teacher_subjects:
#                 # Check if the restriction checkbox is in the POST data
#                 restrict_key = f'restrict_{ts.id}'
#                 is_restricted = restrict_key in request.POST and request.POST[restrict_key] == 'on'
#                 ts.is_restricted = is_restricted
#                 ts.save()
#             return render(request,'teacher_subject_list.html',{'message':'Restriction Applied Successfully','teacher_subjects':teacher_subjects})
#           # Ensure this URL is defined

#         # If teacher_id is provided, handle the marks submission
#         if teacher_id:
#             if Teacher.objects.filter(id=teacher_id, user=request.user).exists():
#                 teacher = get_object_or_404(Teacher, id=teacher_id, user=request.user)

#                 # Fetch subjects taught by this specific teacher
#                 subjects = Subject.objects.filter(teachersubject__teacher=teacher, user=request.user).distinct()

#                 # Fetch students enrolled in these subjects
#                 students = Student.objects.filter(studentsubject__subject__in=subjects).distinct()

#                 # Create a dictionary to check if a student is enrolled in a subject
#                 student_subject_enrollment = {
#                     student.id: {
#                         subject.id: StudentSubject.objects.filter(student=student, subject=subject).exists()
#                         for subject in subjects
#                     }
#                     for student in students
#                 }

#                 # Fetch TeacherSubject instances for this teacher
#                 teacher_subjects_dict = {
#                     subject.id: TeacherSubject.objects.filter(
#                         teacher=teacher,
#                         subject=subject,
#                         user=request.user
#                     ).first()
#                     for subject in subjects
#                 }

#                 # Fetch existing marks for students and subjects
#                 student_marks = {
#                     student.id: {
#                         subject.id: Mark.objects.filter(
#                             student=student,
#                             subject=subject,
#                             user=request.user
#                         ).first()
#                         for subject in subjects
#                     }
#                     for student in students
#                 }

#                 # Process marks only if the teacher is not restricted for the subject
#                 marks_saved = False
#                 for student in students:
#                     for subject in subjects:
#                         mark_value = request.POST.get(f'marks_{student.id}_{subject.id}')
#                         if mark_value:
#                             teacher_subject = teacher_subjects_dict.get(subject.id)
#                             if teacher_subject and not teacher_subject.is_restricted:
#                                 Mark.objects.update_or_create(
#                                     user=request.user,
#                                     student=student,
#                                     subject=subject,
#                                     teacherclass=teacher_subject.teacherclass,
#                                     defaults={'marks': mark_value}
#                                 )
#                                 marks_saved = True

#                 if marks_saved:
#                     messages.success(request, "Marks have been saved successfully!")
#                 elif not subjects.exists():
#                     messages.info(request, "No subjects assigned to this teacher.")

#                 context = {
#                     'teacher': teacher,
#                     'subjects': subjects,
#                     'students': students,
#                     'student_subject_enrollment': student_subject_enrollment,
#                     'teacher_subjects': teacher_subjects_dict,
#                     'student_marks': student_marks,
#                 }
#                 return render(request, 'teacher_students_subjects.html', context)
#             else:
#                 return render(request, 'teacher_id.html', {'message': "Teacher not found or you don't have permission."})

#     # GET request: show teacher subject list
    
#     teacher_subjects = TeacherSubject.objects.filter(user=request.user)
#     return render(request, 'teacher_subject_list.html', {'teacher_subjects': teacher_subjects})




# @login_required
# def grading_form(request):
#     all_grades = GradingModel.objects.filter(user=request.user)
#     o_level_grades = all_grades.filter(is_advance=False)
#     a_level_grades = all_grades.filter(is_advance=True)
#     display = DisplayModel.objects.filter(user=request.user)
    
#     # Check for session message (e.g., from delete)
#     message = request.session.pop('message', None) if request.session.get('message') else None
    
#     if request.method == 'POST':
#         try:
#             is_advance = 'is_advance' in request.POST
#             grade_a = request.POST.get('grade_a')
#             grade_b = request.POST.get('grade_b')
#             grade_c = request.POST.get('grade_c')
#             grade_d = request.POST.get('grade_d')
#             grade_e = request.POST.get('grade_e', '')
#             grade_s = request.POST.get('grade_s', '')
#             grade_f = request.POST.get('grade_f')
#             division_1 = request.POST.get('division_1')
#             division_2 = request.POST.get('division_2')
#             division_3 = request.POST.get('division_3')
#             division_4 = request.POST.get('division_4')

#             # Convert to integers
#             grade_a = int(grade_a) if grade_a else None
#             grade_b = int(grade_b) if grade_b else None
#             grade_c = int(grade_c) if grade_c else None
#             grade_d = int(grade_d) if grade_d else None
#             grade_e = int(grade_e) if grade_e and is_advance else None
#             grade_s = int(grade_s) if grade_s and is_advance else None
#             grade_f = int(grade_f) if grade_f else None
#             division_1 = int(division_1) if division_1 else None
#             division_2 = int(division_2) if division_2 else None
#             division_3 = int(division_3) if division_3 else None
#             division_4 = int(division_4) if division_4 else None

#             # Check for required fields
#             required_fields = [grade_a, grade_b, grade_c, grade_d, grade_f, division_1, division_2, division_3, division_4]
#             if None in required_fields:
#                 raise ValueError("All required fields (A, B, C, D, F, and Divisions) must be filled.")

#             # Validation
#             grades_to_check = [grade_a, grade_b, grade_c, grade_d, grade_f]
#             if is_advance and grade_e is not None and grade_s is not None:
#                 grades_to_check.extend([grade_e, grade_s])

#             if not all(0 <= x <= 100 for x in grades_to_check):
#                 raise ValidationError("All grades must be between 0 and 100.")
#             if not (grade_a > grade_b > grade_c > grade_d > grade_f):
#                 raise ValidationError("Grades must be in descending order: A > B > C > D > F.")
#             if is_advance and grade_e is not None and grade_s is not None and not (grade_d > grade_e > grade_s > grade_f):
#                 raise ValidationError("Advanced grades must be in descending order: D > E > S > F.")
#             if not all(x > 0 for x in [division_1, division_2, division_3, division_4]):
#                 raise ValidationError("Division thresholds must be positive numbers.")

#             # Create grading system
#             GradingModel.objects.create(
#                 user=request.user,
#                 is_advance=is_advance,
#                 grade_a=grade_a,
#                 grade_b=grade_b,
#                 grade_c=grade_c,
#                 grade_d=grade_d,
#                 grade_e=grade_e if is_advance else 45,  # Default for A-Level
#                 grade_s=grade_s if is_advance else 35,  # Default for A-Level
#                 grade_f=grade_f,
#                 division_1=division_1,
#                 division_2=division_2,
#                 division_3=division_3,
#                 division_4=division_4
#             )

#             messages.success(request, "Your custom Grading System Recorded")
#             return redirect('grading_form')

#         except ValueError as e:
#             messages.error(request, str(e) if str(e) != "" else "Please enter valid numbers for all required fields.")
#         except ValidationError as e:
#             messages.error(request, str(e))
#         except Exception as e:
#             messages.error(request, f"An unexpected error occurred: {str(e)}")

#         # Re-render with error
#         return render(request, 'grading_form.html', {
#             'o_level_grades': o_level_grades,
#             'a_level_grades': a_level_grades,
#             'display': display
#         })

#     return render(request, 'grading_form.html', {
#         'o_level_grades': o_level_grades,
#         'a_level_grades': a_level_grades,
#         'display': display,
#         'message': message
#     })




# @login_required
# def delete_grading_system(request, id):
#     grading = get_object_or_404(GradingModel, id=id, user=request.user)
#     grading.delete()
#     messages.success(request, "Grading system deleted successfully!")
#     return redirect('grading_form')



# @login_required
# def update_grading_system(request, id):
#     # Retrieve the grading system for the current user
#     global_grading_system = get_object_or_404(GradingModel, id=id, user=request.user)
    
#     if request.method == 'POST':
#         is_advance = 'is_advance' in request.POST
#         grade_a = request.POST.get('grade_a')
#         grade_b = request.POST.get('grade_b')
#         grade_c = request.POST.get('grade_c')
#         grade_d = request.POST.get('grade_d')
#         grade_e = request.POST.get('grade_e')
#         grade_s = request.POST.get('grade_s')
#         grade_f = request.POST.get('grade_f')
        
#         division_1 = request.POST.get('division_1')
#         division_2 = request.POST.get('division_2')
#         division_3 = request.POST.get('division_3')
#         division_4 = request.POST.get('division_4')

#         # Update the existing grading system
#         global_grading_system.is_advance = is_advance
#         global_grading_system.grade_a = grade_a
#         global_grading_system.grade_b = grade_b
#         global_grading_system.grade_c = grade_c
#         global_grading_system.grade_d = grade_d
#         global_grading_system.grade_e = grade_e
#         global_grading_system.grade_s = grade_s
#         global_grading_system.grade_f = grade_f

#         global_grading_system.division_1 = division_1
#         global_grading_system.division_2 = division_2
#         global_grading_system.division_3 = division_3
#         global_grading_system.division_4 = division_4

#         global_grading_system.save()

#         grades = GradingModel.objects.filter(user=request.user)
#         display_updates = DisplayModel.objects.filter(user=request.user)

#         return render(
#             request,
#             'grading_form.html',
#             {
#                 'message': f'Grade of ID {global_grading_system.id} UPDATED SUCCESSFULLY',
#                 'grades': grades,
#                 'display':display_updates
#             }
#         )
#     return render(
#         request,
#         'update_grading_system.html',
#         {
#             'grades': global_grading_system
#         }
#     )

# from website.models import Host,Top
# def get_host_object(request):
#     hostname = request.get_host().split(':')[0] 
#     print(hostname)
#     try:
#         return Host.objects.get(host_name=hostname)
#     except Host.DoesNotExist:
#         raise HttpResponse('Host does not exist')


# def login_view(request):
#     host = get_host_object(request)
#     footer = Footer.objects.all()
#     gallery = Gallery.objects.all()
#     service = Service.objects.all()
#     contact = Contact.objects.all()
#     about = About.objects.first()
#     top = Top.objects.filter(host_required=host).first()
#     context = {
#         'footer': footer,
#         'gallery': gallery,
#         'service': service,
#         'contact': contact,
#         'about': about,
#         'top': top
#     }

#     if request.method == 'POST':
#         username_input = request.POST.get('username')
#         password_input = request.POST.get('password1')

#         if not username_input or not password_input:
#             messages.error(request, 'Please provide both username and password.')
#             return redirect('login_view')

#         user = authenticate(request, username=username_input, password=password_input)

#         if user is None:
#             messages.error(request, 'Invalid username or password.')
#             return redirect('login_view')

#         if not user.is_active:
#             messages.error(request, 'This account is inactive. Please contact the administrator.')
#             return redirect('login_view')

#         # Log the user in
#         auth_login(request, user)
#         # Ensure session is created
#         if not request.session.session_key:
#             request.session.save()

#         # Update last login and create/update UserSessionAccount
#         user.last_login = timezone.now()
#         user.save(update_fields=['last_login'])

#         session_key = request.session.session_key
#         if session_key:
#             try:
#                 UserSessionAccount.objects.update_or_create(
#                     user=user,
#                     session_key=session_key,
#                     defaults={
#                         'username': user.username,
#                         'last_login': timezone.now(),
#                         'is_active': True
#                     }
#                 )
#             except Exception as e:
#                 logger.error(f"Error creating UserSessionAccount for user {user.username}: {str(e)}")
#                 messages.warning(request, 'Session tracking failed. You are logged in, but session data may not be recorded.')
#         else:
#             logger.error(f"Session key not generated for user {user.username}")
#             messages.warning(request, 'Session could not be initialized. Please try again.')

#         try:
#             if user.is_student:
#                 # Try to get Student profile for active AcademicClassYear
#                 try:
#                     student_profile = Student.objects.filter(
#                         user=user,
#                         teacherclass__academicclassyear__active_year=True
#                     ).select_related('teacherclass__academicclassyear').first()

#                     if not student_profile:
#                         # Fallback to any Student profile if no active year is found
#                         student_profile = Student.objects.filter(user=user).first()
#                         if not student_profile:
#                             logger.error(f"No Student profile found for user {user.username}")
#                             messages.error(request, 'Student profile not found. Please contact the administrator.')
#                             return redirect('login_view')
#                         else:
#                             messages.warning(request, f'No active academic year found for {user.username}. Using default profile.')
                    
#                     full_name = student_profile.fullName or user.username
#                     messages.success(request, f'Welcome Student, {full_name}!')
#                     # Store student ID in session for student_profile view
#                     request.session['student_id'] = student_profile.id
#                     return redirect('student_profile')

#                 except Student.MultipleObjectsReturned:
#                     logger.error(f"Multiple Student profiles found for user {user.username}")
#                     # Select the profile with active AcademicClassYear
#                     student_profile = Student.objects.filter(
#                         user=user,
#                         teacherclass__academicclassyear__active_year=True
#                     ).first()
#                     if student_profile:
#                         full_name = student_profile.fullName or user.username
#                         messages.success(request, f'Welcome Student, {full_name}!')
#                         request.session['student_id'] = student_profile.id
#                         return redirect('student_profile')
#                     else:
#                         messages.error(request, 'Multiple student profiles found, but none for an active academic year. Please contact the administrator.')
#                         return redirect('login_view')

#             elif user.is_teacher:
#                 try:
#                     teacher_profile = Teacher.objects.get(user=user)
#                     full_name = teacher_profile.teacherName or user.username
#                     if user.is_superuser:

#                         messages.success(request, f'Welcome, {full_name}!')
#                         return redirect('create_teacher')
#                     else:
#                         messages.success(request, f'Welcome Teacher, {full_name}!')
#                         return redirect('teacher_profile')
#                 except Teacher.DoesNotExist:
#                     logger.error(f"Teacher profile missing for user {user.username}")
#                     messages.error(request, 'Teacher profile not found. Please contact the administrator.')
#                     return redirect('login_view')
#             else:
#                 logger.warning(f"User {user.username} has no valid role (is_student={user.is_student}, is_teacher={user.is_teacher})")
#                 messages.error(request, 'Invalid user role. Please contact the administrator.')
#                 return redirect('login_view')

#         except Exception as e:
#             logger.error(f"Unexpected error for user {user.username}: {str(e)}")
#             messages.error(request, f'An unexpected error occurred: {str(e)}. Please contact the administrator.')
#             return redirect('login_view')

#     return render(request, 'login.html', context)
    
# def user_logout(request):
#     if request.user.is_authenticated:
#         # Get the current user's ID
#         user_id = request.user.id
        
#         # Delete all sessions for this user
#         active_sessions = Session.objects.filter(
#             expire_date__gte=timezone.now()  # Only active (non-expired) sessions
#         )
#         for session in active_sessions:
#             session_data = session.get_decoded()
#             if str(user_id) == str(session_data.get('_auth_user_id')):
#                 session.delete()  # Delete the session

#     # Log out the current session
#     messages.success(request,'You logout to all devices, Login again')
#     logout(request)
    
#     # Redirect to login page
#     return redirect('login_view')



# # Assuming this is your teacher_validation view


# def determine_grade(marks, grading_system):
#     """Determine the grade based on the grading system."""
#     if marks >= grading_system.grade_a:
#         return 'A'
#     elif marks >= grading_system.grade_b:
#         return 'B'
#     elif marks >= grading_system.grade_c:
#         return 'C'
#     elif marks >= grading_system.grade_d:
#         return 'D'
#     elif marks >= grading_system.grade_e:
#         return 'E'
#     elif marks >= grading_system.grade_s:
#         return 'S'
#     else:
#         return 'F'

# # rps_app/views.py

# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.db.models import Avg, Q
# from .models import TeacherClass, Student, GradingModel, ExaminationName
# import logging

# logger = logging.getLogger(__name__)
# @login_required
# def result_evaluation(request):
#     # Fetch initial data for the form dropdowns
#     teacher_classes = TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True)
#     examinations = ExaminationName.objects.filter(user=request.user)
    
#     context = {
#         'teacher_classes': teacher_classes,
#         'examinations': examinations,
#     }

#     if request.method == 'POST':
#         teacherclass_id = request.POST.get('teacherclass')
#         examination_id = request.POST.get('examination')  # Get examination_id
#         below_average_str = request.POST.get('below_average')

#         try:
#             if not all([teacherclass_id, examination_id, below_average_str]):
#                 context['message'] = 'Please fill in all fields.'
#                 return render(request, 'evaluation_form.html', context)

#             selected_class = get_object_or_404(
#                 TeacherClass,
#                 id=teacherclass_id,
#                 user=request.user,
#                 academicclassyear__active_year=True
#             )
#             selected_examination = get_object_or_404(
#                 ExaminationName,
#                 id=examination_id,
#                 user=request.user
#             )
#             below_average = int(below_average_str)

#             # Create a Q object to filter marks specifically for the selected examination
#             marks_filter = Q(marks__examinationname=selected_examination)

#             # ✅ Return Student objects (with annotation), not dicts
#             below_average_students = (
#                 Student.objects.filter(teacherclass=selected_class)
#                 .annotate(
#                     average_marks=Avg('marks__marks', filter=marks_filter, default=0)
#                 )
#                 .filter(
#                     average_marks__lt=below_average,
#                     average_marks__gt=0
#                 )
#                 .select_related("teacherclass__ClassName", "teacherclass__academicclassyear")  # optimize queries
#                 .order_by("average_marks")
#             )

#             result_context = {
#                 'below_average': below_average,
#                 'below_average_students': below_average_students,
#                 'selected_class': selected_class,
#                 'selected_examination': selected_examination,
#                 'message': 'No students were found matching your criteria.' if not below_average_students.exists() else None
#             }
#             return render(request, 'evaluation_results.html', result_context)

#         except ValueError:
#             context['message'] = 'Please enter a valid numeric value for the average grade (0-100).'
#             return render(request, 'evaluation_form.html', context)
#         except Exception as e:
#             logger.error(f"An unexpected error occurred in result_evaluation: {str(e)}")
#             return render(request, 'error.html', {
#                 'error_message': f"An unexpected error occurred. Please try again."
#             })

#     return render(request, 'evaluation_form.html', context)



# @login_required
# def top_and_bottom_students(request):
#     # Get the current user
#     current_user = request.user
    
#     # Get all teachers created by this user (including self if not created by another)
#     created_teachers = Teacher.objects.filter(
#         models.Q(created_by=current_user) | models.Q(id=current_user.id)
#     )
    
#     # Get all classes managed by these teachers
#     teacher_classes = TeacherClass.objects.filter(
#         user__in=created_teachers,academicclassyear__active_year=True
#     )
    
#     # If a specific class is selected via GET parameter
#     selected_class_id = request.GET.get('class_id')
#     selected_class = None
    
#     if selected_class_id:
#         try:
#             selected_class = TeacherClass.objects.get(
#                 id=selected_class_id,
#                 user__in=created_teachers,
#                 academicclassyear__active_year=True
#             )
            
#             # Calculate averages for selected class across all relevant teachers
#             student_averages = Mark.objects.filter(
#                 teacherclass=selected_class,
#                 user__in=created_teachers
#             ).values(
#                 'student__id',
#                 'student__fullName'
#             ).annotate(
#                 avg_mark=Avg('marks')
#             )
            
#             # Top students (highest to lowest)
#             top_students = student_averages.order_by('-avg_mark')[:10]
#             # Bottom students (highest of the bottom to lowest)
#             bottom_students = student_averages.order_by('avg_mark').reverse()[:10]
#             # or alternatively: bottom_students = student_averages.order_by('-avg_mark')[::-1][:10]
            
#         except TeacherClass.DoesNotExist:
#             top_students = []
#             bottom_students = []
#     else:
#         # Show all classes' data
#         class_data = {}
#         for teacher_class in teacher_classes:
#             student_averages = Mark.objects.filter(
#                 teacherclass=teacher_class,
#                 user__in=created_teachers
#             ).values(
#                 'student__id',
#                 'student__fullName'
#             ).annotate(
#                 avg_mark=Avg('marks')
#             )
            
#             class_data[teacher_class] = {
#                 'top_students': student_averages.order_by('-avg_mark')[:10],
#                 'bottom_students': student_averages.order_by('avg_mark').reverse()[:10]
#             }
        
#         top_students = None
#         bottom_students = None

#     context = {
#         'teacher_classes': teacher_classes,
#         'selected_class': selected_class,
#         'top_students': top_students,
#         'bottom_students': bottom_students,
#         'class_data': class_data if not selected_class else None,
#     }
#     return render(request, 'top_bottom_students.html', context)

# # rps_app/views.py

# import logging
# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import GradingModel, Teacher, TeacherClass, RequiredSubject, Subject, Mark, ExaminationName
# @login_required
# def top_ten_subjects(request):
#     logger = logging.getLogger(__name__)

#     def determine_grade(mark, grading):
#         # (Helper function remains the same)
#         if grading.is_advance:
#             if mark >= grading.grade_a: return 'A'
#             elif mark >= grading.grade_b: return 'B'
#             elif mark >= grading.grade_c: return 'C'
#             elif mark >= grading.grade_d: return 'D'
#             elif mark >= grading.grade_e: return 'E'
#             elif mark >= grading.grade_s: return 'S'
#             else: return 'F'
#         else:
#             if mark >= grading.grade_a: return 'A'
#             elif mark >= grading.grade_b: return 'B'
#             elif mark >= grading.grade_c: return 'C'
#             elif mark >= grading.grade_d: return 'D'
#             else: return 'F'

#     # Fetch data for the selection form
#     grades_display = GradingModel.objects.filter(user=request.user)
#     examinations_display = ExaminationName.objects.filter(user=request.user)
#     classes_display = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)  # Fetch classes

#     context = {
#         'grades': grades_display,
#         'examinations': examinations_display,
#         'classes': classes_display,  # Add classes to context
#     }

#     if request.method == 'POST':
#         grade_id = request.POST.get('grade_id')
#         examination_id = request.POST.get('examination_id')
#         class_id = request.POST.get('class_id')  # Get the selected class ID

#         # --- Form Validation ---
#         if not grade_id or not examination_id or not class_id:
#             context['error_message'] = "Please select a grading system, an examination, and a class."
#             return render(request, 'gpa_options.html', context)

#         # Fetch selected objects
#         grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         examination_required = get_object_or_404(ExaminationName, id=examination_id, user=request.user)
#         selected_class = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)

#         level = 'Alevel' if grading_required.is_advance else 'Olevel'
        
#         grade_points = {'A': 1.0, 'B': 2.0, 'C': 3.0, 'D': 4.0, **({'E': 5.0, 'S': 6.0, 'F': 7.0} if grading_required.is_advance else {'F': 5.0})}

#         subordinate_teachers = Teacher.objects.filter(created_by=request.user).values_list('user_id', flat=True)
#         all_teacher_user_ids = list(subordinate_teachers) + [request.user.id]

#         class_subjects_data = []
#         subjects_data = []
        
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subjects = Subject.objects.filter(id__in=required_subjects.values('subject_id'), user=request.user)

#         for subject in subjects:
#             marks = Mark.objects.filter(
#                 subject=subject,
#                 user_id__in=all_teacher_user_ids,
#                 teacherclass=selected_class,  # Filter by selected class
#                 examinationname=examination_required
#             )
            
#             if marks.exists():
#                 total_points = sum(grade_points.get(determine_grade(mark.marks, grading_required), 0) for mark in marks)
#                 student_count = marks.count()
#                 gpa = round(total_points / student_count, 2) if student_count > 0 else 0.00
                
#                 subjects_data.append({
#                     'subject': subject,
#                     'gpa': gpa,
#                 })

#         sorted_subjects = sorted(subjects_data, key=lambda x: x['gpa'])[:10]
        
#         if sorted_subjects:
#             class_subjects_data.append({
#                 'class': selected_class,
#                 'subjects': sorted_subjects
#             })

#         return render(request, 'top_ten_subjects.html', {
#             'class_subjects_data': class_subjects_data,
#             'grading_system': grading_required,
#             'examination': examination_required,
#             'level': level
#         })

#     return render(request, 'gpa_options.html', context)
    
# @login_required
# def display(request):
#     if request.method == 'POST':
#         header = request.POST.get('header', '')
#         body = request.POST.get('body', '')
#         image = request.FILES.get('image_uploaded')  # Use .get() to handle no file selected

#         if image:  # Check if an image was actually uploaded
#             DisplayModel.objects.create(
#                 user=request.user,
#                 header=header,
#                 body=body,
#                 image=image
#             )
#             message = 'Custom Display Saved Successfully'
#         else:
#             message = 'No image file uploaded'

#         display_model = DisplayModel.objects.filter(user=request.user)
#         return render(request, 'display.html', {'message': message, 'display': display_model})
#     else:
#         updated_display = DisplayModel.objects.filter(user=request.user)
#         return render(request, 'display.html', {'display': updated_display})

# @login_required
# def delete_display(request,id):
#     if request.method == 'POST':
#         d = DisplayModel.objects.filter(user=request.user,id=id)
#         d.delete()
#         updated_display = DisplayModel.objects.filter(user=request.user)
#         return render(request,'display.html',{'message':'Successfully deletion','display':updated_display})
#     return render(request,'confirm_deletion.html')


# from openpyxl.styles import PatternFill, Border, Side, Font, Alignment


# @login_required
# def download_excel(request, class_id):
#     teacherclass = get_object_or_404(TeacherClass, id=class_id,academicclassyear__active_year=True)
#     students = Student.objects.filter(class_id=teacherclass).prefetch_related('marks')
#     subjects = Subject.objects.filter(class_id=teacherclass)

#     # Prepare data for Excel
#     data = {
#         'S/No': [],
#         'Student Name': [],
#         'Sex': [],
#         'Index Number': [],
#     }
#     for subject in subjects:
#         data[f"{subject.nameSubject} Marks"] = []
#         data[f"{subject.nameSubject} Grade"] = []
#     data.update({
#         'Total Marks': [],
#         'Average': [],
#         'Grade': [],
#         'Position': [],
#         'Division': [],
#         'Points': [],
#     })

#     for i, student in enumerate(students, 1):
#         data['S/No'].append(i)
#         data['Student Name'].append(student.fullName or 'Unnamed')
#         data['Sex'].append(student.sex or '-')
#         data['Index Number'].append(student.indexNumber or '-')
#         for subject in subjects:
#             mark = student.marks.filter(subject=subject.id).first()
#             data[f"{subject.nameSubject} Marks"].append(mark.mark if mark else '-')
#             data[f"{subject.nameSubject} Grade"].append(mark.grade if mark else '-')
#         data['Total Marks'].append(student.total_marks or '-')
#         data['Average'].append(f"{student.average_marks:.2f}" if student.average_marks else '-')
#         data['Grade'].append(student.grade or '-')
#         data['Position'].append(student.position or '-')
#         data['Division'].append(student.division or '-')
#         data['Points'].append(student.total_points or '-')

#     # Create DataFrame
#     df = pd.DataFrame(data)

#     # Excel setup
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename="student_report_{teacherclass.ClassName}.xlsx"'

#     # Write to Excel with styling
#     wb = Workbook()
#     ws = wb.active
#     ws.title = f"{teacherclass.ClassName} Results"

#     # Write DataFrame to worksheet
#     for r in df.to_numpy():
#         ws.append(r.tolist())

#     # Styling
#     header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
#     border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
#     for cell in ws[1]:  # Header row
#         cell.fill = header_fill
#         cell.font = Font(color="FFFFFF", bold=True)
#         cell.alignment = Alignment(horizontal='center', vertical='center')
#         cell.border = border

#     for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
#         for cell in row:
#             cell.border = border
#             cell.alignment = Alignment(horizontal='center', vertical='center')
#             if cell.column_letter in ['B', 'D']:  # Adjust for wider columns
#                 ws.column_dimensions[cell.column_letter].width = 20
#             else:
#                 ws.column_dimensions[cell.column_letter].width = 12

#     # Save to response
#     wb.save(response)
#     return response



# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from .models import ExaminationName, Student, Mark, TeacherClass # Make sure TeacherClass is imported

# # rps_app/views.py

# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import ExaminationName, Student, Mark, TeacherClass, Teacher # Make sure Teacher is imported

# @login_required
# def search_result(request):
#     """
#     Handles student result search, filtering marks by RequiredSubject.
#     Blocks students and restricts access for accountants.
#     """
#     # Block students and accountants
#     if hasattr(request.user, 'is_student') and request.user.is_student:
#         logger.warning(f"Student {request.user.username} attempted to access search_result")
#         return render(request, 'search.html', {
#             'message': 'Students are not allowed to search.'
#         })
#     if request.session.get('teacher_role') == 'Accountant':
#         logger.warning(f"Accountant {request.user.username} attempted to access search_result")
#         return render(request, 'search.html', {
#             'message': 'Accountants are not allowed to access this page.'
#         })

#     # Fetch all relevant user IDs (user and their subordinates)
#     subordinate_user_ids = Teacher.objects.filter(created_by=request.user).values_list('user_id', flat=True)
#     all_user_ids = list(subordinate_user_ids) + [request.user.id]

#     # Fetch classes and examinations for the user and subordinates
#     class_names = TeacherClass.objects.filter(user_id__in=all_user_ids, academicclassyear__active_year=True).distinct()
#     examination_names = ExaminationName.objects.filter(user_id__in=all_user_ids).distinct()

#     # Fetch required subjects for the current user
#     required_subjects = RequiredSubject.objects.filter(user=request.user)
#     required_subject_ids = required_subjects.values_list('subject__id', flat=True)

#     context = {
#         'examination_names': examination_names,
#         'class_names': class_names,
#         'no_subjects_configured': not required_subjects.exists(),
#     }

#     # If no required subjects, return early with message
#     if not required_subjects.exists():
#         logger.info(f"No required subjects configured for user {request.user.username}")
#         context['message'] = 'No subject Configured'
#         return render(request, 'search.html', context)

#     if request.method == 'POST':
#         student_name = request.POST.get('searched_student', '').strip()
#         examination_id = request.POST.get('examination_id')
#         class_id = request.POST.get('class_id')

#         # Input Validation
#         if not student_name:
#             context['message'] = 'Please enter a student name.'
#             logger.warning(f"Empty student name in search by {request.user.username}")
#             return render(request, 'search.html', context)
        
#         if not examination_id:
#             context['message'] = 'Please select an examination.'
#             logger.warning(f"No examination selected in search by {request.user.username}")
#             return render(request, 'search.html', context)
        
#         if not class_id:
#             context['message'] = 'Please select a class.'
#             logger.warning(f"No class selected in search by {request.user.username}")
#             return render(request, 'search.html', context)

#         # Verify class and examination exist for the user
#         try:
#             selected_class = class_names.get(id=class_id)
#             selected_exam = examination_names.get(id=examination_id)
#         except TeacherClass.DoesNotExist:
#             context['message'] = 'Selected class is invalid or you do not have permission.'
#             logger.error(f"Class {class_id} not found for user {request.user.username}")
#             return render(request, 'search.html', context)
#         except ExaminationName.DoesNotExist:
#             context['message'] = 'Selected examination is invalid or you do not have permission.'
#             logger.error(f"Examination {examination_id} not found for user {request.user.username}")
#             return render(request, 'search.html', context)

#         # Search for students in the selected class
#         students = Student.objects.filter(
#             teacherclass_id=class_id,
#             fullName__icontains=student_name,
#             manager__in=all_user_ids  # Allow students managed by user or subordinates
#         )
#         logger.debug(f"Searching for student '{student_name}' in class {class_id}. Found {students.count()} students")

#         student = students.first()

#         if student:
#             # Filter marks by required subjects
#             student_searched = Mark.objects.filter(
#                 student=student,
#                 examinationname_id=examination_id,
#                 subject__id__in=required_subject_ids
#             ).select_related('subject', 'examinationname')

#             if not student_searched.exists():
#                 context['message'] = f'No results found for "{student.fullName}" in the selected examination for required subjects.'
#                 logger.info(f"No marks found for student {student.fullName} in exam {selected_exam.exam_name}")
            
#             context['student_searched'] = student_searched
#             context['student'] = student
#         else:
#             context['message'] = f'Student named "{student_name}" was not found in the selected class.'
#             logger.info(f"No student found with name '{student_name}' in class {class_id}")

#         return render(request, 'search.html', context)

#     # For GET requests
#     return render(request, 'search.html', context)

  
    
    
# @login_required
# def grading_system(request):
#     grades=GradingModel.objects.filter(user=request.user)
#     display = DisplayModel.objects.filter(user=request.user)
#     print(f'display {display.count()}')
#     return render(request,'grading_system.html',{'grades':grades,'display':display})
    
    
# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import TeacherSubject, StudentSubject, Mark, ExaminationName, Student, Subject, AcademicClassYear, EmailVerificationOTP
# from django.conf import settings

# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .models import TeacherSubject, StudentSubject, Mark, ExaminationName, Student, Subject, AcademicClassYear, EmailVerificationOTP
# from django.conf import settings

# @login_required
# def teacher_dashboard(request):
#     # Fetch subjects assigned to the logged-in teacher
#     user = request.user
#     # Check if the user has any verified OTP
#     is_email_verified = EmailVerificationOTP.objects.filter(
#         user=user, is_verified=True, purpose='verification'
#     ).exists()

#     # For GET: Fetch all TeacherSubject instances for the teacher, regardless of active year
#     teacher_subjects = TeacherSubject.objects.filter(
#         teacher=user
#     ).select_related('subject', 'teacherclass', 'teacherclass__academicclassyear', 'teacherclass__ClassName')

#     # Get distinct subjects assigned to the teacher
#     subjects = Subject.objects.filter(
#         teachersubject__teacher=user
#     ).distinct()

#     if request.method == 'POST':
#         # For POST: Only process marks for active TeacherClass
#         active_teacher_subjects = TeacherSubject.objects.filter(
#             teacher=user,
#             teacherclass__academicclassyear__active_year=True
#         ).select_related('subject', 'teacherclass', 'teacherclass__academicclassyear')

#         # Get distinct subjects for active TeacherClass
#         active_subjects = Subject.objects.filter(
#             teachersubject__teacher=user,
#             teachersubject__teacherclass__academicclassyear__active_year=True
#         ).distinct()

#         # Fetch students enrolled in subjects taught by this teacher for active TeacherClass
#         students = Student.objects.filter(
#             studentsubject__subject__in=active_subjects,
#             studentsubject__teacherclass__academicclassyear__active_year=True
#         ).distinct().select_related('user').order_by('fullName')

#         # Create a dictionary to check if a student is enrolled in a subject
#         student_subject_enrollment = {
#             student.id: {
#                 subject.id: StudentSubject.objects.filter(
#                     student=student,
#                     subject=subject,
#                     teacherclass__academicclassyear__active_year=True
#                 ).exists()
#                 for subject in active_subjects
#             }
#             for student in students
#         }

#         # Fetch TeacherSubject instances for active TeacherClass
#         teacher_subjects_dict = {
#             subject.id: TeacherSubject.objects.filter(
#                 teacher=user,
#                 subject=subject,
#                 teacherclass__academicclassyear__active_year=True
#             ).first()
#             for subject in active_subjects
#         }

#         # Fetch existing marks for students and subjects in active TeacherClass
#         student_marks = {
#             student.id: {
#                 subject.id: Mark.objects.filter(
#                     student=student,
#                     subject=subject,
#                     user=user,
#                     teacherclass__academicclassyear__active_year=True
#                 ).first()
#                 for subject in active_subjects
#             }
#             for student in students
#         }

#         # Process marks only if the teacher is not restricted for the subject
#         marks_saved = False
#         examination_name_id = request.session.get('selected_examination_id')
#         if not examination_name_id:
#             messages.error(request, "Please select an examination first.")
#             return redirect('select_examination_name', teacher_subject_id=active_teacher_subjects.first().id if active_teacher_subjects.exists() else 0)

#         try:
#             examination_name = ExaminationName.objects.get(
#                 id=examination_name_id,
#                 user=user
#             )
#         except ExaminationName.DoesNotExist:
#             messages.error(request, "Selected examination name is invalid.")
#             if 'selected_examination_id' in request.session:
#                 del request.session['selected_examination_id']
#             return redirect('select_examination_name', teacher_subject_id=active_teacher_subjects.first().id if active_teacher_subjects.exists() else 0)

#         for student in students:
#             for subject in active_subjects:
#                 mark_value = request.POST.get(f'marks_{student.id}_{subject.id}')
#                 if mark_value and mark_value.strip():
#                     teacher_subject = teacher_subjects_dict.get(subject.id)
#                     if teacher_subject and not teacher_subject.is_restricted:
#                         try:
#                             mark_value = float(mark_value)
#                             if not (0 <= mark_value <= 100):
#                                 raise ValueError("Marks must be between 0 and 100.")
#                             Mark.objects.update_or_create(
#                                 user=user,
#                                 student=student,
#                                 subject=subject,
#                                 teacherclass=teacher_subject.teacherclass,
#                                 examinationname=examination_name,
#                                 defaults={'marks': mark_value}
#                             )
#                             marks_saved = True
#                         except ValueError as e:
#                             messages.error(request, f"Invalid mark for {student.fullName or student.user.username} in {subject.nameSubject}: {e}")
#                             return redirect('teacher_dashboard')

#         if marks_saved:
#             messages.success(request, "Marks have been saved successfully!")
#         elif not active_subjects.exists():
#             messages.info(request, "No subjects assigned to you for an active academic year.")

#         context = {
#             'subjects': active_subjects,
#             'students': students,
#             'student_subject_enrollment': student_subject_enrollment,
#             'teacher_subjects': teacher_subjects_dict,
#             'student_marks': student_marks,
#             'is_verified': is_email_verified,
#             'examination_name': examination_name,
#         }
#         return render(request, 'teacher_students_subjects.html', context)

#     # GET request: Show all assigned subjects and their TeacherClass with AcademicClassYear
#     context = {
#         'teacher_subjects': teacher_subjects,
#         'subjects': subjects,
#         'is_verified': is_email_verified,
#     }
#     return render(request, 'teacher_dashboard.html', context)




# @login_required
# def exclude_subject(request):
#     if request.method == 'POST':
#         subject_id = request.POST.get('subject')
#         subject = Subject.objects.get(id=subject_id)
#         user = request.user  # Assuming authentication middleware is set up
        
#         # Create or check if the subject is already excluded
#         ExcludeSubject.objects.get_or_create(user=user, exclude_subject=subject)
#         return redirect('exclude_subject')

#     # Fetch data for rendering
#     exclude_subjects = ExcludeSubject.objects.filter(user=request.user)
#     all_subjects = Subject.objects.filter(user=request.user)
    
#     return render(request, 'exclude_subject.html', {
#         'exclude_subjects': exclude_subjects,
#         'subjects': all_subjects
#     })


# @login_required
# def create_student_subject(request):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     assignments = StudentSubject.objects.filter(user=request.user)

#     # Group assignments by student and class
#     student_assignments = {}
#     for assignment in assignments:
#         teacherclass = assignment.teacherclass
#         for student in assignment.student.all():
#             key = (student.id, teacherclass.id)  # Unique key per student and class
#             if key not in student_assignments:
#                 student_assignments[key] = {
#                     'student': student,
#                     'teacherclass': teacherclass,
#                     'subjects': []
#                 }
#             student_assignments[key]['subjects'].append(assignment.subject.nameSubject)

#     # Convert to list with comma-separated subjects
#     student_assignments_list = [
#         {
#             'student': data['student'],
#             'teacherclass': data['teacherclass'],
#             'subjects': ', '.join(data['subjects'])
#         }
#         for data in student_assignments.values()
#     ]

#     return render(request, 'create_student_subject.html', {
#         'classes': classes,
#         'student_assignments': student_assignments_list
#     })


# @login_required
# def select_class(request, class_id=None):
#     # Ensure the user is a teacher or superuser
#     if not (request.user.is_teacher or request.user.is_superuser):
#         messages.error(request, "Only teachers or administrators can access this page.")
#         return redirect('homepage')

#     try:
#         # Verify teacher profile exists
#         Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     # Get classes managed by the user
#     teacher_classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     student_subject_data = None

#     if class_id:
#         # Validate the selected class
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         # Get students in the selected class
#         students = Student.objects.filter(teacherclass=teacherclass, manager=request.user)

#         student_subject_data = []
#         for student in students:
#             # Fetch subjects for this student in the selected class
#             student_subjects = Subject.objects.filter(
#                 studentsubject__student=student,
#                 studentsubject__user=request.user,
#                 studentsubject__teacherclass=teacherclass
#             ).distinct()
#             student_subject_data.append({
#                 'student_id': student.id,
#                 'student_name': student.fullName or student.user.username,
#                 'class_name': teacherclass.ClassName,
#                 'subject_list': student_subjects,
#             })

#     return render(request, 'select_class.html', {
#         'teacher_classes': teacher_classes,
#         'student_subject_data': student_subject_data,
#         'class_id': class_id
#     })


# @login_required
# def assign_students_to_subject(request, class_id):
#     # Ensure user is a teacher
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can access this page.")
#         return redirect('teacher_dashboard')

#     try:
#         teacher_profile = request.user.teacher_profile.get()
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Contact your administrator.")
#         return redirect('teacher_dashboard')

#     # Get the class
#     teacherclass = get_object_or_404(
#         TeacherClass,
#         id=class_id,
#         user__in=[request.user, teacher_profile.created_by]
#     )

#     students = Student.objects.filter(
#         teacherclass=teacherclass,
#         manager__in=[request.user, teacher_profile.created_by]
#     ).select_related('user')

#     if request.method == 'POST':
#         form = StudentSubjectForm(
#             request.POST,
#             user=request.user,
#             teacherclass=teacherclass
#         )
#         if form.is_valid():
#             assigned_count, skipped_count = form.save(commit=True)

#             if assigned_count > 0:
#                 messages.success(request, f"Successfully assigned {assigned_count} student-subject pair(s).")
#             if skipped_count > 0:
#                 messages.info(request, f"Skipped {skipped_count} already existing assignment(s).")

#             return redirect('select_class', class_id=class_id)
#     else:
#         form = StudentSubjectForm(user=request.user, teacherclass=teacherclass)

#     return render(request, 'assign_students.html', {
#         'form': form,
#         'teacherclass': teacherclass,
#         'students': students,
#     })




# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render
# from .models import Student, StudentSubject, TeacherClass
# from .forms import StudentSubjectForm

# @login_required
# def update_student_subject(request, id):
#     # Get the student, ensuring they are managed by the current user
#     student = get_object_or_404(
#         Student,
#         id=id,
#         manager=request.user
#     )

#     if request.method == 'POST':
#         form = StudentSubjectForm(
#             request.POST,
#             user=request.user,
#             student=student,
#             teacherclass=student.teacherclass
#         )
#         if form.is_valid():
#             assigned_count, skipped_count = form.save(commit=True)
#             if assigned_count > 0:
#                 messages.success(request, f"Subjects for {student.fullName} updated successfully!")
#             if skipped_count > 0:
#                 messages.info(request, f"Skipped {skipped_count} already existing assignment(s).")
#             return redirect('select_class', class_id=student.teacherclass.id)
#     else:
#         form = StudentSubjectForm(
#             user=request.user,
#             student=student,
#             teacherclass=student.teacherclass
#         )

#     # Fetch current subjects for display in the template
#     student_subject = StudentSubject.objects.filter(
#         student=student,
#         user=request.user,
#         teacherclass=student.teacherclass
#     ).first()
#     current_subjects = student_subject.subject.all() if student_subject else []

#     return render(request, 'update_student_subjects.html', {
#         'form': form,
#         'student': student,
#         'teacherclass': student.teacherclass,
#         'current_subjects': current_subjects
#     })

# @login_required
# def list_student_subjects(request):
#     student_subjects = StudentSubject.objects.filter(user=request.user).prefetch_related('student', 'subject')
    
#     # Create a dictionary to organize students and their subjects
#     students_subjects = {}
#     for entry in student_subjects:
#         for student in entry.student.all():
#             if student not in students_subjects: 
#                 students_subjects[student] = []
#             students_subjects[student].append(entry.subject)

#     return render(request, 'list_student_subjects.html', {'students_subjects': students_subjects})






# @login_required
# def delete_student_subjects(request, student_id, subject_id=None):
#     # Get the student, ensuring they are managed by the current user or linked via teacherclass
#     student = get_object_or_404(
#         Student, 
#         id=student_id, 
#         manager=request.user  # Check if the user is the manager of the student
#     )
    
#     if subject_id and request.method == "GET":  # Single subject deletion via URL
#         subject = get_object_or_404(
#             Subject, 
#             id=subject_id, 
#             user=request.user  # Ensure the subject belongs to the user
#         )
        
#         # Find StudentSubject records for this student and subject
#         student_subjects = StudentSubject.objects.filter(
#             student=student,
#             subject=subject,
#             user=request.user,
#             teacherclass=student.teacherclass
#         )

#         if student_subjects.exists():
#             for student_subject in student_subjects:
#                 # Remove the specified subject
#                 student_subject.subject.remove(subject)
#                 # Delete related marks
#                 Mark.objects.filter(
#                     student=student, 
#                     subject=subject, 
#                     teacherclass=student.teacherclass
#                 ).delete()
#                 # Clean up if no subjects remain
#                 if not student_subject.subject.exists():
#                     student_subject.delete()
#             messages.success(request, f"Subject '{subject.nameSubject}' removed from {student.fullName}.")
#         else:
#             messages.error(request, f"Subject '{subject.nameSubject}' not found for {student.fullName}.")
        
#         return redirect('select_class', class_id=student.teacherclass.id)
    
#     messages.error(request, "Invalid request.")
#     return redirect('select_class', class_id=student.teacherclass.id)


# @login_required 
# def verify_registration_number(request):
#     if request.method == 'POST':
#         registration_number = request.POST['accesskey']
        
#         # Check if the registration number matches the user's associated number
#         if request.user.registration_number == registration_number:
#             # Set session variable to mark the registration as verified
#             request.session['registration_verified'] = True
#             return redirect('create_subject')  # Redirect to the page they were trying to access
#         else:
#             return render(request,'user_admin_access.html',{'message':'Authentication Fail'})
    
#     return render(request, 'user_admin_access.html')



# @login_required
# def update_teacher_subject(request, id):
#     # Fetch TeacherSubject with related teacherclass and academicclassyear, ensuring active year
#     teacher_subject = get_object_or_404(
#         TeacherSubject,
#         id=id,
#         user=request.user,
#         teacherclass__academicclassyear__active_year=True
#     )
    
#     if request.method == 'POST':
#         form = TeacherSubjectForm(request.POST, instance=teacher_subject, user=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(
#                 request,
#                 f'Teacher assignment for {teacher_subject.teacher.teacherName} in {teacher_subject.subject.nameSubject} ({teacher_subject.teacherclass.ClassName.class_name}) updated successfully.'
#             )
#             return redirect('assign_teachers')
#         else:
#             messages.error(request, 'Failed to update assignment. Please check the form.')
#     else:
#         form = TeacherSubjectForm(instance=teacher_subject, user=request.user)

#     return render(request, 'update_teacher_subject.html', {
#         'form': form,
#         'teacher_subject': teacher_subject,
#     })


# @login_required
# def select_pdf_options(request):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)
#     display = DisplayModel.objects.filter(user=request.user)
#     examination_names = ExaminationName.objects.filter(user=request.user)

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')
#         report_id = request.POST.get('report_id')
#         examination_id = request.POST.get('examination_id')

#         # Validate inputs
#         if not (class_id and grade_id and examination_id and
#                 TeacherClass.objects.filter(id=class_id, user=request.user).exists() and
#                 GradingModel.objects.filter(id=grade_id, user=request.user).exists() and
#                 ExaminationName.objects.filter(id=examination_id, user=request.user).exists()):
#             messages.error(request, "Invalid selection. Please choose valid class, grading system, and examination.")
#             return render(request, 'select_pdf_options.html', {
#                 'classes': classes,
#                 'grades': grades,
#                 'display': display,
#                 'examination_names': examination_names,
#             })

#         # Redirect to the PDF download view with the selected options
#         return redirect('download_pdf', class_id=class_id, grade_id=grade_id, examination_name_id=examination_id, report_id=report_id or '')

#     return render(request, 'select_pdf_options.html', {
#         'classes': classes,
#         'grades': grades,
#         'display': display,
#         'examination_names': examination_names,
#     })

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import AcademicClassYear, TeacherClass, Teacher, RegisterClass
# from django.conf import settings

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import AcademicClassYear, TeacherClass, Teacher, RegisterClass
# from django.conf import settings

# @login_required
# def create_academic_year(request):
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can create academic years.")
#         return redirect('homepage')

#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     if request.method == 'POST':
#         academic_year_name = request.POST.get('academic_year_name')
#         active_year = request.POST.get('active_year') == 'on'

#         if not academic_year_name:
#             messages.error(request, "Academic year name is required.")
#             return render(request, 'academic_year.html', {
#                 'academic_years': AcademicClassYear.objects.filter(user=request.user)
#             })

#         academic_year = AcademicClassYear.objects.create(
#             user=request.user,
#             academic_year_name=academic_year_name,
#             active_year=active_year
#         )
#         messages.success(request, f'Academic Year "{academic_year_name}" added successfully!')
#         return render(request, 'academic_year.html', {
#             'academic_years': AcademicClassYear.objects.filter(user=request.user)
#         })
#     else:
#         return render(request, 'academic_year.html', {
#             'academic_years': AcademicClassYear.objects.filter(user=request.user)
#         })

# @login_required
# def toggle_academic_year(request, year_id):
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can toggle academic years.")
#         return redirect('homepage')

#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     try:
#         academic_year = AcademicClassYear.objects.get(id=year_id,user=request.user)
#         academic_year.active_year = not academic_year.active_year
#         academic_year.save()
#         status = "activated" if academic_year.active_year else "deactivated"
#         messages.success(request, f'Academic Year "{academic_year.academic_year_name}" {status} successfully!')
#     except AcademicClassYear.DoesNotExist:
#         messages.error(request, "Academic year not found.")

#     return redirect('create_academic_year')

# @login_required
# def create_teacher_class(request):
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can create classes.")
#         return redirect('homepage')

#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     active_years = AcademicClassYear.objects.filter(active_year=True,user=request.user)

#     if request.method == 'POST':
#         class_name = request.POST.get('ClassName')

#         if not class_name:
#             messages.error(request, "Class name is required.")
#             return render(request, 'create_teacher_class.html', {
#                 'classes': RegisterClass.objects.filter(user=request.user),
#                 'active_years': active_years,
#                 'teacher_classes': TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True)
#             })

#         register_class, created = RegisterClass.objects.get_or_create(
#             user=request.user,
#             class_name=class_name
#         )
#         messages.success(request, f'Class "{class_name}" added successfully!')
#         return render(request, 'create_teacher_class.html', {
#             'classes': RegisterClass.objects.filter(user=request.user),
#             'active_years': active_years,
#             'teacher_classes': TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True)
#         })
#     else:
#         return render(request, 'create_teacher_class.html', {
#             'classes': RegisterClass.objects.filter(user=request.user),
#             'active_years': active_years,
#             'teacher_classes': TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True)
#         })

# @login_required
# def assign_academic_year(request):
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can assign academic years.")
#         return redirect('homepage')

#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     active_years = AcademicClassYear.objects.filter(active_year=True,user=request.user)
#     classes = RegisterClass.objects.filter(user=request.user)

#     if request.method == 'POST':
#         register_class_id = request.POST.get('selected_register_class')
#         academic_year_id = request.POST.get('academicclassyear')

#         try:
#             register_class = RegisterClass.objects.get(id=register_class_id, user=request.user)
#             academic_year = AcademicClassYear.objects.get(id=academic_year_id, active_year=True,user=request.user)
            
#             # Create a new TeacherClass instance instead of updating
#             teacher_class = TeacherClass.objects.create(
#                 user=request.user,
#                 ClassName=register_class,
#                 academicclassyear=academic_year
#             )
#             messages.success(request, f'Academic year "{academic_year.academic_year_name}" assigned to class "{register_class.class_name}" successfully!')
#         except RegisterClass.DoesNotExist:
#             messages.error(request, "Selected class is invalid or not owned by you.")
#         except AcademicClassYear.DoesNotExist:
#             messages.error(request, "Selected academic year is invalid or not active.")
        
#         return render(request, 'create_teacher_class.html', {
#             'classes': RegisterClass.objects.filter(user=request.user),
#             'active_years': active_years,
#             'teacher_classes': TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True)
#         })

#     return render(request, 'create_teacher_class.html', {
#         'classes': RegisterClass.objects.filter(user=request.user),
#         'active_years': active_years,
#         'teacher_classes': TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True)
#     })

# @login_required
# def select_teacher_class(request):
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can select classes.")
#         return redirect('homepage')

#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Please contact the administrator.")
#         return redirect('homepage')

#     active_years = AcademicClassYear.objects.filter(active_year=True,user=request.user)
#     active_classes = TeacherClass.objects.filter(academicclassyear__active_year=True)

#     if request.method == 'POST':
#         teacher_class_id = request.POST.get('selected_teacher_class')
#         try:
#             selected_class = TeacherClass.objects.get(id=teacher_class_id, academicclassyear__active_year=True)
#             # Store selected class in session or perform desired action
#             request.session['selected_teacher_class'] = teacher_class_id
#             messages.success(request, f'Class "{selected_class.ClassName.class_name}" selected successfully!')
#             return redirect('create_teacher_class')  # Or redirect to appropriate view
#         except TeacherClass.DoesNotExist:
#             messages.error(request, "Selected class is invalid or not associated with an active academic year.")
    
#     return render(request, 'create_teacher_class.html', {
#         'classes': TeacherClass.objects.filter(user=request.user, academicclassyear__active_year=True),
#         'active_years': active_years,
#         'active_classes': active_classes
#     })


# @login_required
# def delete_academic_year(request, id):
#     # Ensure the user is a teacher
#     if not request.user.is_teacher:
#         messages.error(request, "Only teachers can delete academic years.")
#         return redirect('homepage')

#     try:
#         academic_year = AcademicClassYear.objects.get(id=id,user=request.user)
#         academic_year.delete()
#         messages.success(request, f'Academic Year "{academic_year.academic_year_name}" deleted successfully!')
#     except AcademicClassYear.DoesNotExist:
#         messages.error(request, "Academic year not found.")
#     return redirect('create_academic_year')


# @login_required
# def select_examination_name(request, teacher_subject_id):
#     try:
#         # Get the Teacher profile for the logged-in user
#         teacher_profile = request.user.teacher_profile.get()
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Contact your administrator.")
#         return redirect('teacher_dashboard')

#     # Check if the teacher has a creator (created_by)
#     if not teacher_profile.created_by:
#         messages.error(request, "No creator found. Contact your administrator.")
#         return redirect('teacher_dashboard')

#     # Get examination names created by the teacher's creator
#     examination_names = ExaminationName.objects.filter(user=teacher_profile.created_by)

#     if not examination_names.exists():
#         messages.error(request, "No examination names available. Contact your administrator.")
#         return redirect('teacher_dashboard')

#     if request.method == 'POST':
#         examination_name_id = request.POST.get('examination_name_id')
#         if examination_name_id:
#             try:
#                 examination_name = examination_names.get(id=examination_name_id)
#                 request.session['selected_examination_id'] = examination_name_id
#                 messages.success(request, f"Examination '{examination_name.exam_name}' selected.")
#                 return redirect('fill_marks', teacher_subject_id=teacher_subject_id)
#             except ExaminationName.DoesNotExist:
#                 messages.error(request, "Invalid examination name selected.")
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     context = {
#         'examination_names': examination_names,
#         'teacher_subject_id': teacher_subject_id,
#     }
#     return render(request, 'examination_selection.html', context)


# @login_required
# def fill_marks(request, teacher_subject_id):
#     # Check if an examination name is selected
#     examination_name_id = request.session.get('selected_examination_id')
#     if not examination_name_id:
#         messages.error(request, "Please select an examination first.")
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     try:
#         # Get the Teacher profile for the logged-in user
#         teacher_profile = request.user.teacher_profile.get()
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Contact your administrator.")
#         return redirect('teacher_dashboard')

#     try:
#         # Get the examination name using the teacher's creator
#         examination_name = ExaminationName.objects.get(
#             id=examination_name_id,
#             user=teacher_profile.created_by
#         )
#     except ExaminationName.DoesNotExist:
#         messages.error(request, "Selected examination name is invalid.")
#         if 'selected_examination_id' in request.session:
#             del request.session['selected_examination_id']
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     # Get the assignment for the logged-in teacher
#     teacher_subject = get_object_or_404(
#         TeacherSubject,
#         id=teacher_subject_id,
#         teacher=teacher_profile  # Use the teacher profile instead of request.user
#     )

#     # Get students enrolled in this subject and class via StudentSubject
#     student_subjects = StudentSubject.objects.filter(
#         teacherclass=teacher_subject.teacherclass,
#         subject=teacher_subject.subject
#     )

#     if student_subjects.exists():
#         # Use ManyToManyField to get students
#         student_ids = set()
#         for student_subject in student_subjects:
#             student_ids.update(student_subject.student.values_list('id', flat=True))
#         students = Student.objects.filter(id__in=student_ids).select_related('user')
#     else:
#         students = Student.objects.none()

#     # Fetch existing marks as a dictionary
#     student_marks = {
#         mark.student_id: mark.marks for mark in Mark.objects.filter(
#             teacherclass=teacher_subject.teacherclass,
#             subject=teacher_subject.subject,
#             examinationname=examination_name,
#             student__in=students
#         )
#     }

#     # Fetch saved marks for the summary table
#     saved_marks = Mark.objects.filter(
#         teacherclass=teacher_subject.teacherclass,
#         subject=teacher_subject.subject,
#         examinationname=examination_name,
#         student__in=students
#     ).select_related('student')

#     if request.method == 'POST':
#         if teacher_subject.is_restricted:
#             messages.error(request, "Marks for this subject are restricted.")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         for student in students:
#             mark_value = request.POST.get(f'marks_{student.id}')
#             if mark_value and mark_value.strip():
#                 try:
#                     mark_value = float(mark_value)
#                     if not (0 <= mark_value <= 100):
#                         raise ValueError("Marks must be between 0 and 100.")
#                     Mark.objects.update_or_create(
#                         teacherclass=teacher_subject.teacherclass,
#                         subject=teacher_subject.subject,
#                         examinationname=examination_name,
#                         student=student,
#                         defaults={
#                             'marks': mark_value,
#                             'user': request.user
#                         }
#                     )
#                 except ValueError as e:
#                     messages.error(request, f"Invalid mark for {student.fullName or student.user.username}: {e}")
#                     return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         messages.success(request, "Marks saved successfully!")
#         return redirect('teacher_dashboard')

#     context = {
#         'teacher_subject': teacher_subject,
#         'students': students,
#         'student_marks': student_marks,
#         'saved_marks': saved_marks,
#         'examination_name': examination_name,
#     }
#     return render(request, 'fill_marks.html', context)
# # rps_app/views.py


# @login_required
# def teacher_dashboard(request):
#     # Ensure the user is a teacher
#     if not request.user.is_teacher and not request.user.is_active:
#         messages.error(request, "Access Denied: This dashboard is for teachers only.")
#         return redirect('login_view')  # Or your login page

#     try:
#         # Get the Teacher instance for the logged-in user
#         teacher_profile = Teacher.objects.get(user=request.user)
#         # Filter TeacherSubject by the Teacher instance
#         teacher_subjects = TeacherSubject.objects.filter(teacher=teacher_profile).select_related('subject', 'teacherclass')
        
#         context = {
#             'teacher_subjects': teacher_subjects,
#         }
#         return render(request, 'teacher_dashboard.html', context)

#     except Teacher.DoesNotExist:
#         # Handle case where a user has is_teacher=True but no Teacher profile
#         messages.error(request, "Your teacher profile could not be found.")
#         return redirect('base')  # Or another appropriate redirect

# def base(request):
#     return render(request,'base.html')


# def delete_excluded_subject(request,id):
#     if request.method == 'POST':
#         dl_excluded_subject = ExcludeSubject.objects.get(user=request.user,id=id)
#         dl_excluded_subject.delete()
#         return redirect('exclude_subject')
#     return render(request,'confirm_deletion.html')


# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, render
# from django.contrib import messages
# from django.db.models import Sum
# import logging
# import os

# logger = logging.getLogger(__name__)

# @login_required
# def upload_term_marks(request):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)
#     examination_names = ExaminationName.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#         'examinations': examination_names,  # Changed to match template
#     }

#     logger.info(f"User {request.user} accessed upload_term_marks, method: {request.method}")

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')
#         examination_id = request.POST.get('examination_id')  # Added to capture examination_id
#         action = request.POST.get('action')

#         logger.info(f"Received POST: class_id={class_id}, grade_id={grade_id}, examination_id={examination_id}, action={action}")
#         logger.info(f"POST data: {request.POST}")
#         logger.info(f"FILES data: {list(request.FILES.keys())}")

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user,academicclassyear__active_year=True).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             logger.error(f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}")
#             return render(request, 'upload_term_marks.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id
#         context['selected_examination_id'] = examination_id  # Added to preserve selection

#         # Handle Delete Action
#         if action == 'delete':
#             upload_id = request.POST.get('upload_id')
#             try:
#                 upload = TermMarksUpload.objects.get(id=upload_id, user=request.user, teacherclass=teacherclass)
#                 if os.path.exists(upload.pdf_file.path):
#                     os.remove(upload.pdf_file.path)
#                 upload.delete()
#                 messages.success(request, f"Deleted {upload.term_name} PDF successfully.")
#                 logger.info(f"Deleted upload ID {upload_id} for {teacherclass.ClassName}")
#             except TermMarksUpload.DoesNotExist:
#                 messages.error(request, "Upload not found.")
#                 logger.error(f"Upload ID {upload_id} not found")
#             except Exception as e:
#                 messages.error(request, f"Error deleting PDF: {str(e)}")
#                 logger.error(f"Delete exception: {str(e)}")

#         # Handle Update Action
#         elif action == 'update':
#             upload_id = request.POST.get('upload_id')
#             new_term_name = request.POST.get('new_term_name')
#             new_pdf_file = request.FILES.get('new_pdf_file')
#             try:
#                 upload = TermMarksUpload.objects.get(id=upload_id, user=request.user, teacherclass=teacherclass)
#                 if new_term_name:
#                     upload.term_name = new_term_name
#                 if new_pdf_file:
#                     if os.path.exists(upload.pdf_file.path):
#                         os.remove(upload.pdf_file.path)
#                     upload.pdf_file = new_pdf_file
#                 upload.save()
#                 messages.success(request, f"Updated {upload.term_name} PDF successfully.")
#                 logger.info(f"Updated upload ID {upload_id} for {teacherclass.ClassName}")
#             except TermMarksUpload.DoesNotExist:
#                 messages.error(request, "Upload not found.")
#                 logger.error(f"Upload ID {upload_id} not found")
#             except Exception as e:
#                 messages.error(request, f"Error updating PDF: {str(e)}")
#                 logger.error(f"Update exception: {str(e)}")

#         # Handle Upload Action (default)
#         elif action == 'upload' or not action:
#             logger.info(f"Upload started for user {request.user}, class {teacherclass.ClassName}")
#             uploaded_files = 0
#             term_names = {key: value for key, value in request.POST.items() if key.startswith('term_name_')}

#             if not request.FILES:
#                 messages.error(request, "No PDF files selected. Please choose at least one file.")
#                 logger.error("No files in request.FILES")
#             else:
#                 for key in request.FILES:
#                     if key.startswith('pdf_file_'):
#                         index = key.replace('pdf_file_', '')
#                         term_name = term_names.get(f'term_name_{index}', f'Term {index}')
#                         pdf_file = request.FILES[key]
#                         logger.info(f"Processing {key}: term_name={term_name}, file={pdf_file.name}, size={pdf_file.size}")
#                         try:
#                             instance, created = TermMarksUpload.objects.update_or_create(
#                                 user=request.user,
#                                 teacherclass=teacherclass,
#                                 term_name=term_name,
#                                 defaults={'pdf_file': pdf_file}
#                             )
#                             if os.path.exists(instance.pdf_file.path):
#                                 uploaded_files += 1
#                                 logger.info(f"Saved {term_name} at {instance.pdf_file.path}, created={created}")
#                             else:
#                                 messages.error(request, f"Failed to save {term_name} to {instance.pdf_file.path}")
#                                 logger.error(f"File not found at {instance.pdf_file.path}")
#                         except Exception as e:
#                             messages.error(request, f"Error saving {term_name}: {str(e)}")
#                             logger.error(f"Exception: {str(e)}")

#                 if uploaded_files > 0:
#                     messages.success(request, f"Successfully uploaded {uploaded_files} PDFs.")
#                 else:
#                     messages.error(request, "No PDFs uploaded successfully.")
#                 logger.info(f"Upload completed: {uploaded_files} files saved")

#         # Fetch uploaded PDFs for display
#         context['uploads'] = TermMarksUpload.objects.filter(user=request.user, teacherclass=teacherclass)
#         return render(request, 'upload_term_marks.html', context)

#     # For GET request, display existing uploads if a class is selected
#     if 'class_id' in request.GET:
#         class_id = request.GET.get('class_id')
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         context['teacherclass'] = teacherclass
#         context['uploads'] = TermMarksUpload.objects.filter(user=request.user, teacherclass=teacherclass)

#     return render(request, 'upload_term_marks.html', context)


# @login_required
# def delete_all_data(request, class_id):
#     if request.method == 'POST':
#         try:
#             # Get the specific TeacherClass instance
#             teacher_class = TeacherClass.objects.get(id=class_id, user=request.user,academicclassyear__active_year=True)

#             # Get all teachers created by the logged-in user
#             created_teachers = Teacher.objects.filter(created_by=request.user)
#             # Include the logged-in user themselves in the deletion scope
#             teacher_ids = list(created_teachers.values_list('id', flat=True)) + [request.user.id]

#             # Filter marks by teachers (created by the user or the user themselves) and the specific class
#             marks_to_delete = Mark.objects.filter(
#                 user__id__in=teacher_ids,
#                 teacherclass=teacher_class
#             )

#             # Perform the deletion
#             deleted_count, _ = marks_to_delete.delete()
#             messages.success(request, f'All {deleted_count} marks for class "{teacher_class.ClassName}" entered by you and your created teachers have been deleted.')
#             return redirect('teacher_dashboard')

#         except TeacherClass.DoesNotExist:
#             messages.error(request, 'The specified class does not exist or you do not have permission to delete its marks.')
#             return redirect('teacher_dashboard')

#     # For GET request, render the confirmation page
#     try:
#         teacher_class = TeacherClass.objects.get(id=class_id, user=request.user,academicclassyear__active_year=True)
#         context = {'teacher_class': teacher_class}
#         return render(request, 'confirm_deletion.html', context)
#     except TeacherClass.DoesNotExist:
#         messages.error(request, 'Invalid class selected.')
#         return redirect('teacher_dashboard')







# @login_required
# def change_password(request, teacher_id=None):
#     try:
#         # Determine which teacher is being modified
#         if teacher_id:
#             if not request.user.created_teachers.exists():
#                 messages.error(request, "You don't have permission to change other teachers' passwords.")
#                 return redirect('teacher_dashboard')
#             teacher = get_object_or_404(Teacher, id=teacher_id)
#             if request.user != teacher.created_by:
#                 messages.error(request, "You can only change passwords for teachers you created.")
#                 return redirect('teacher_dashboard')
#         else:
#             teacher = request.user

#         logger.info(f"Processing password change for teacher: {teacher.username}")

#         if request.method == 'POST':
#             logger.info(f"POST data: {request.POST}")
#             form = PasswordChangeForm(user=teacher, data=request.POST)
            
#             # If creator is changing password, old_password is not required
#             if request.user != teacher:
#                 form.fields['old_password'].required = False
#                 logger.info("Changing password for another teacher - old_password not required")
            
#             if form.is_valid():
#                 logger.info("Form is valid, saving...")
#                 form.save()
#                 if request.user == teacher:
#                     update_session_auth_hash(request, form.user)
#                 messages.success(request, 'Password successfully changed!, Login again')
#                 return redirect('user_logout')
#             else:
#                 logger.error(f"Form errors: {form.errors.as_json()}")
#                 messages.error(request, 'Please correct the errors below.')
#         else:
#             form = PasswordChangeForm(user=teacher)
#             if request.user != teacher:
#                 form.fields['old_password'].required = False

#         return render(request, 'change_password.html', {
#             'form': form,
#             'teacher': teacher
#         })
#     except Exception as e:
#         logger.error(f"Server error in change_password: {str(e)}", exc_info=True)
#         messages.error(request, 'An unexpected error occurred. Please try again.')
#         return render(request, 'change_password.html', {'form': form, 'teacher': teacher})



# def delete_class(request,id):
#     if request.method == 'POST':
#         class_deleted = TeacherClass.objects.get(id=id,academicclassyear__active_year=True)
#         class_deleted.delete()
#         updated_class = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#         messages.success(request,'You Successfully delete class')
#         return render(request,'create_teacher_class.html',{'classes':updated_class})
#     return render(request,'confirm_deletion.html')

# from finance.models import StudentFee,PayFee
# from decimal import Decimal
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db.models import Sum, Avg
# from django.db.models import Q as models_Q
# from django.urls import reverse
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db.models import Sum, Avg
# from django.db.models import Q as models_Q
# from django.urls import reverse

# from decimal import Decimal
# import base64
# from django.utils import timezone
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.db.models import Sum, Avg, Q
# from django.contrib.auth.decorators import login_required

# import json
# from decimal import Decimal
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db.models import Sum, Avg
# from rps_app.models import Student, ExaminationName, GradingModel, DisplayModel, Subject, Mark, Teacher
# from finance.models import StudentFee, PayFee, Discount
# from django.db.models import Q as models_Q
# import json
# from decimal import Decimal

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.db.models import Sum, Avg
# from rps_app.models import Student, ExaminationName, GradingModel, DisplayModel, Subject, Mark, Teacher
# from finance.models import StudentFee, PayFee, Discount
# from django.db.models import Q as models_Q
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import cm
# from decimal import Decimal
# from datetime import datetime

# @login_required
# def download_student_report(request):
#     if not request.user.is_student:
#         messages.error(request, "You are not authorized to access this report.")
#         return redirect('login_view')

#     # Get all Student profiles for the logged-in user
#     student_profiles = Student.objects.filter(user=request.user).select_related('teacherclass__academicclassyear', 'manager')
#     if not student_profiles.exists():
#         messages.error(request, "Student profile not found.")
#         return redirect('login_view')

#     # Initialize PDF
#     response = HttpResponse(content_type='application/pdf')
#     filename = f"student_report_{student_profiles.first().indexNumber}.pdf".replace(" ", "_")
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
#     elements = []

#     # Styles
#     styles = getSampleStyleSheet()
#     header_style = ParagraphStyle(
#         name='Header',
#         parent=styles['Heading1'],
#         fontSize=16,
#         alignment=1,  # Center alignment
#         spaceAfter=10,
#         textColor=colors.darkblue,
#         leading=20
#     )
#     subheader_style = ParagraphStyle(
#         name='Subheader',
#         parent=styles['Heading2'],
#         fontSize=12,
#         alignment=0,  # Left alignment for class sections
#         spaceAfter=8,
#         textColor=colors.black
#     )
#     body_style = ParagraphStyle(
#         name='Body',
#         parent=styles['BodyText'],
#         fontSize=9,  # Smaller font for table cells
#         alignment=0,
#         spaceAfter=6,
#         leading=10
#     )
#     footer_style = ParagraphStyle(
#         name='Footer',
#         parent=styles['BodyText'],
#         fontSize=8,
#         alignment=1,
#         textColor=colors.grey
#     )
#     discount_style = ParagraphStyle(
#         name='Discount',
#         parent=styles['BodyText'],
#         fontSize=10,
#         textColor=colors.red,
#         spaceAfter=6
#     )
#     summary_style = ParagraphStyle(
#         name='Summary',
#         parent=styles['BodyText'],
#         fontSize=10,
#         alignment=0,
#         spaceAfter=6,
#         textColor=colors.black,
#         fontName='Helvetica-Bold'
#     )

#     # Header Section
#     student = student_profiles.first()
#     elements.append(Paragraph(f"Student Report for {student.fullName}", header_style))
#     display = DisplayModel.objects.filter(user=student.manager).first()
#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.5*cm))
#         except Exception as e:
#             print(f"Error loading DisplayModel image: {e}")

#     elements.append(Paragraph(
#         f"<b>Index:</b> {student.indexNumber} | <b>Contact:</b> {student.contact} | <b>Gender:</b> {student.sex}",
#         subheader_style
#     ))
#     elements.append(Paragraph(
#         f"Generated by: {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}",
#         footer_style
#     ))
#     elements.append(Spacer(1, 1*cm))

#     # Prepare data
#     academic_data = []
#     financial_data = []
#     attendance_data = []
#     total_required_all = Decimal('0.00')
#     total_paid_all = Decimal('0.00')
#     total_discount_all = Decimal('0.00')
#     total_initial_payment = Decimal('0.00')

#     for student in student_profiles:
#         teacherclass = student.teacherclass
#         manager = student.manager

#         # Define grade thresholds
#         grading_required = GradingModel.objects.filter(user=manager).first()
#         if grading_required:
#             if grading_required.is_advance:
#                 grade_thresholds = {
#                     grading_required.grade_a: 'A',
#                     grading_required.grade_b: 'B',
#                     grading_required.grade_c: 'C',
#                     grading_required.grade_d: 'D',
#                     grading_required.grade_e: 'E',
#                     grading_required.grade_s: 'S',
#                     grading_required.grade_f: 'F'
#                 }
#             else:
#                 grade_thresholds = {
#                     grading_required.grade_a: 'A',
#                     grading_required.grade_b: 'B',
#                     grading_required.grade_c: 'C',
#                     grading_required.grade_d: 'D',
#                     grading_required.grade_f: 'F'
#                 }
#         else:
#             grade_thresholds = {
#                 80: 'A',
#                 70: 'B',
#                 60: 'C',
#                 50: 'D',
#                 0: 'F'
#             }

#         # Academic Data
#         examination_names = ExaminationName.objects.filter(user=manager)
#         subjects = Subject.objects.filter(teacherclass=teacherclass, user=manager)
#         class_data = {
#             'class_name': teacherclass.ClassName.class_name,
#             'academic_year': teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A',
#             'examinations': []
#         }

#         for exam in examination_names:
#             marks = Mark.objects.filter(
#                 student=student,
#                 examinationname=exam,
#                 teacherclass=teacherclass
#             ).select_related('subject')

#             if not subjects.exists():
#                 subjects = Subject.objects.filter(id__in=marks.values('subject')).distinct()

#             exam_data = {
#                 'exam_name': exam.exam_name,
#                 'subjects': [],
#                 'total_marks': 0,
#                 'average_marks': 0,
#                 'position': None,
#                 'total_students': Student.objects.filter(teacherclass=teacherclass).count()
#             }

#             for subject in subjects:
#                 mark_obj = marks.filter(subject=subject).first()
#                 mark_value = mark_obj.marks if mark_obj else None
#                 grade = '-'

#                 if mark_value is not None and grading_required:
#                     for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                         if mark_value >= threshold:
#                             grade = letter_grade
#                             break

#                 exam_data['subjects'].append({
#                     'name': subject.nameSubject if subject else 'Unknown Subject',
#                     'mark': mark_value if mark_value is not None else 'N/A',
#                     'grade': grade
#                 })

#             exam_marks = marks.aggregate(
#                 total=Sum('marks'),
#                 average=Avg('marks')
#             )
#             exam_data['total_marks'] = exam_marks['total'] or 0
#             exam_data['average_marks'] = round(exam_marks['average'] or 0, 2) if exam_marks['average'] else 0

#             students_ranked = Student.objects.filter(teacherclass=teacherclass).annotate(
#                 total_marks=Sum('marks__marks', filter=models_Q(
#                     marks__examinationname=exam,
#                     marks__teacherclass=teacherclass
#                 ))
#             ).order_by('-total_marks')

#             for idx, s in enumerate(students_ranked, 1):
#                 if s.id == student.id:
#                     exam_data['position'] = idx
#                     break

#             class_data['examinations'].append(exam_data)

#         academic_data.append(class_data)

#         # Financial Data
#         class_financial_data = {
#             'class_name': teacherclass.ClassName.class_name,
#             'academic_year': teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A',
#             'fees': [],
#             'total_required': Decimal('0.00'),
#             'total_paid': Decimal('0.00'),
#             'total_discount': Decimal('0.00'),
#             'initial_payment': Decimal('0.00'),
#             'total_balance': Decimal('0.00')
#         }

#         student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#         accountants = Teacher.objects.filter(created_by=manager).values_list('user', flat=True)
#         all_payments = PayFee.objects.filter(
#             student=student,
#             user__in=accountants,
#             fee__in=student_fees.values('fee')
#         ).select_related('fee').order_by('-date_paid')
#         discounts = Discount.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#         total_discount = discounts.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
#         class_financial_data['total_discount'] = total_discount

#         # Fetch initial payment
#         student_focus = StudentFocus.objects.filter(student=student).first()
#         if student_focus:
#             student_registration = StudentRegistration.objects.filter(studentfocus=student_focus).first()
#             if student_registration and student_registration.initial_payment:
#                 class_financial_data['initial_payment'] = student_registration.initial_payment
#                 total_initial_payment += student_registration.initial_payment

#         for fee_assignment in student_fees:
#             fee = fee_assignment.fee
#             payments = all_payments.filter(fee=fee)
#             paid_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#             discount = discounts.filter(fee=fee).first()
#             discount_amount = discount.discount_amount if discount else Decimal('0.00')
#             adjusted_amount = fee_assignment.amount_required - discount_amount

#             payment_timing = "No Payment"
#             if payments.exists():
#                 latest_payment = payments.order_by('-date_paid').first()
#                 if latest_payment and latest_payment.date_paid:
#                     if latest_payment.date_paid < fee_assignment.start_date:
#                         payment_timing = "In Advance"
#                     elif fee_assignment.start_date <= latest_payment.date_paid <= fee_assignment.end_date:
#                         payment_timing = "On Time"
#                     elif latest_payment.date_paid > fee_assignment.end_date:
#                         payment_timing = "After Deadline"

#             fee_data = {
#                 'fee_name': fee.fee_name,
#                 'amount_required': fee_assignment.amount_required,
#                 'discount': discount_amount,
#                 'adjusted_amount': adjusted_amount,
#                 'paid': paid_amount,
#                 'balance': adjusted_amount - paid_amount,
#                 'status': 'Paid' if paid_amount >= adjusted_amount else 'Pending',
#                 'payment_timing': payment_timing,
#                 'start_date': fee_assignment.start_date,
#                 'end_date': fee_assignment.end_date,
#                 'payments': [{
#                     'date': p.date_paid.strftime('%Y-%m-%d'),
#                     'amount': p.amount_paid,
#                     'description': p.description or '-',
#                     'payer_account_no': p.payer_account_no or '-'
#                 } for p in payments]
#             }

#             class_financial_data['fees'].append(fee_data)
#             class_financial_data['total_required'] += adjusted_amount
#             class_financial_data['total_paid'] += paid_amount
#             class_financial_data['total_balance'] += (adjusted_amount - paid_amount)

#             total_required_all += adjusted_amount
#             total_paid_all += paid_amount
#             total_discount_all += discount_amount

#         financial_data.append(class_financial_data)

#         # Attendance Data
#         current_date = timezone.now().date()
#         current_month = current_date.month
#         current_year = current_date.year
#         days_in_month = calendar.monthrange(current_year, current_month)[1]
#         date_headers = [date(current_year, current_month, i + 1) for i in range(days_in_month)]

#         attendances = StudentAttendance.objects.filter(student=student, date__in=date_headers).values('date', 'status', 'check_in_time', 'check_out_time')
#         attendance_dict = {att['date']: {
#             'status': att['status'],
#             'check_in_time': att['check_in_time'],
#             'check_out_time': att['check_out_time']
#         } for att in attendances}

#         class_attendance_data = []
#         for day in date_headers:
#             if day <= current_date:
#                 entry = attendance_dict.get(day, {'status': 'absent', 'check_in_time': None, 'check_out_time': None})
#                 status = entry['status']
#                 check_in_time = entry['check_in_time'].strftime('%H:%M') if entry['check_in_time'] else '-'
#                 check_out_time = entry['check_out_time'].strftime('%H:%M') if entry['check_out_time'] else '-'
#             else:
#                 status = '-'
#                 check_in_time = '-'
#                 check_out_time = '-'
#             class_attendance_data.append({
#                 'date': day,
#                 'status': 'Present' if status == 'present' else 'Absent' if status == 'absent' else '-',
#                 'check_in_time': check_in_time,
#                 'check_out_time': check_out_time
#             })

#         present_count = sum(1 for att in class_attendance_data if att['status'] == 'Present')
#         absent_count = sum(1 for att in class_attendance_data if att['status'] == 'Absent')
#         total_days = len([d for d in date_headers if d <= current_date])
#         attendance_rate = round((present_count / total_days * 100), 2) if total_days > 0 else 0

#         class_attendance = {
#             'class_name': teacherclass.ClassName.class_name,
#             'academic_year': teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A',
#             'month': calendar.month_name[current_month],
#             'year': current_year,
#             'attendance_data': class_attendance_data,
#             'present_count': present_count,
#             'absent_count': absent_count,
#             'total_days': total_days,
#             'attendance_rate': attendance_rate
#         }
#         attendance_data.append(class_attendance)

#     # Academic Section
#     elements.append(Paragraph("Academic Performance", header_style))
#     if not academic_data:
#         elements.append(Paragraph("No academic data available.", body_style))
#     else:
#         page_width = A4[0] - 2 * 1.5*cm
#         col_widths = [
#             0.35 * page_width,  # Subject
#             0.15 * page_width,  # Marks
#             0.15 * page_width,  # Grade
#             0.35 * page_width   # Performance (%)
#         ]

#         for class_data in academic_data:
#             elements.append(Paragraph(f"Class: {class_data['class_name']} ({class_data['academic_year']})", subheader_style))
#             elements.append(Spacer(1, 0.5*cm))

#             for exam in class_data['examinations']:
#                 elements.append(Paragraph(f"Examination: {exam['exam_name']}", body_style))
#                 table_data = [['Subject', 'Marks', 'Grade', 'Performance (%)']]
#                 for subject in exam['subjects']:
#                     table_data.append([
#                         Paragraph(subject['name'], body_style),
#                         Paragraph(str(subject['mark']), body_style),
#                         Paragraph(subject['grade'], body_style),
#                         Paragraph(str(subject['mark']) if subject['mark'] != 'N/A' else '0', body_style)
#                     ])
#                 if not exam['subjects']:
#                     table_data.append(['No subjects available', '-', '-', '-'])

#                 table = Table(table_data, colWidths=col_widths)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 10),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('FONTSIZE', (0, 1), (-1, -1), 9),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 elements.append(table)
#                 summary = f"Total Marks: {exam['total_marks']} | Average: {exam['average_marks']:.2f}% | Position: {exam['position'] or '-'}/{exam['total_students'] or '-'}"
#                 elements.append(Paragraph(summary, body_style))
#                 elements.append(Spacer(1, 0.5*cm))

#             elements.append(Spacer(1, 1*cm))

#     # Financial Section
#     elements.append(Paragraph("Financial Information", header_style))
#     if not financial_data:
#         elements.append(Paragraph("No financial data available.", body_style))
#     else:
#         page_width = A4[0] - 2 * 1.5*cm
#         col_widths_fees = [
#             0.20 * page_width,  # Fee
#             0.12 * page_width,  # Amount Required
#             0.12 * page_width,  # Discount
#             0.12 * page_width,  # Adjusted Amount
#             0.12 * page_width,  # Paid
#             0.12 * page_width,  # Balance
#             0.12 * page_width,  # Status
#             0.18 * page_width   # Payment Timing
#         ]
#         col_widths_payments = [
#             0.20 * page_width,  # Fee
#             0.15 * page_width,  # Date
#             0.15 * page_width,  # Amount
#             0.25 * page_width,  # Payer Account
#             0.25 * page_width   # Description
#         ]

#         for class_data in financial_data:
#             elements.append(Paragraph(f"Class: {class_data['class_name']} ({class_data['academic_year']})", subheader_style))
#             elements.append(Spacer(1, 0.5*cm))

#             # Fee Table
#             table_data = [['Fee', 'Amt. Required', 'Discount', 'Adj. Amt.', 'Paid', 'Balance', 'Status', 'Timing']]
#             for fee in class_data['fees']:
#                 table_data.append([
#                     Paragraph(fee['fee_name'], body_style),
#                     Paragraph(f"{fee['amount_required']:.2f}", body_style),
#                     Paragraph(f"{fee['discount']:.2f}", body_style),
#                     Paragraph(f"{fee['adjusted_amount']:.2f}", body_style),
#                     Paragraph(f"{fee['paid']:.2f}", body_style),
#                     Paragraph(f"{fee['balance']:.2f}", body_style),
#                     Paragraph(fee['status'], body_style),
#                     Paragraph(fee['payment_timing'], body_style)
#                 ])
#             if not class_data['fees']:
#                 table_data.append(['No fees assigned', '-', '-', '-', '-', '-', '-', '-'])

#             table = Table(table_data, colWidths=col_widths_fees)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('FONTSIZE', (0, 1), (-1, -1), 9),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                 ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                 ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#             ]))
#             elements.append(table)

#             # Class Financial Summary
#             summary = (
#                 f"Total Required: {class_data['total_required']:.2f} | "
#                 f"Total Paid: {class_data['total_paid']:.2f} | "
#                 f"Balance: {class_data['total_balance']:.2f} | "
#                 f"Total Discount: {class_data['total_discount']:.2f} | "
#                 f"Initial Payment: {class_data['initial_payment']:.2f}"
#             )
#             elements.append(Paragraph(summary, discount_style if class_data['total_discount'] > 0 else summary_style))
#             elements.append(Spacer(1, 0.5*cm))

#             # Payment Records
#             elements.append(Paragraph("Payment Records", body_style))
#             table_data = [['Fee', 'Date', 'Amount', 'Payer Account', 'Description']]
#             for fee in class_data['fees']:
#                 for payment in fee['payments']:
#                     table_data.append([
#                         Paragraph(fee['fee_name'], body_style),
#                         Paragraph(payment['date'], body_style),
#                         Paragraph(f"{payment['amount']:.2f}", body_style),
#                         Paragraph(payment['payer_account_no'], body_style),
#                         Paragraph(payment['description'], body_style)
#                     ])
#             if not any(fee['payments'] for fee in class_data['fees']):
#                 table_data.append(['No payment records found', '-', '-', '-', '-'])

#             table = Table(table_data, colWidths=col_widths_payments)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('FONTSIZE', (0, 1), (-1, -1), 9),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                 ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                 ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#             ]))
#             elements.append(table)
#             elements.append(Spacer(1, 1*cm))

#         # Overall Financial Summary
#         elements.append(Paragraph("Overall Financial Summary", subheader_style))
#         summary = (
#             f"Total Required: {total_required_all:.2f} | "
#             f"Total Paid: {total_paid_all:.2f} | "
#             f"Total Balance: {total_required_all - total_paid_all:.2f} | "
#             f"Total Discount: {total_discount_all:.2f} | "
#             f"Total Initial Payment: {total_initial_payment:.2f}"
#         )
#         elements.append(Paragraph(summary, discount_style if total_discount_all > 0 else summary_style))
#         elements.append(Spacer(1, 1*cm))

#     # Attendance Section
#     elements.append(Paragraph("Attendance Records", header_style))
#     if not attendance_data:
#         elements.append(Paragraph("No attendance data available.", body_style))
#     else:
#         page_width = A4[0] - 2 * 1.5*cm
#         col_widths_attendance = [
#             0.25 * page_width,  # Date
#             0.25 * page_width,  # Status
#             0.25 * page_width,  # Check-In Time
#             0.25 * page_width   # Check-Out Time
#         ]

#         for class_data in attendance_data:
#             elements.append(Paragraph(
#                 f"Class: {class_data['class_name']} ({class_data['academic_year']}) - {class_data['month']} {class_data['year']}",
#                 subheader_style
#             ))
#             elements.append(Spacer(1, 0.5*cm))

#             # Attendance Table
#             table_data = [['Date', 'Status', 'Check-In Time', 'Check-Out Time']]
#             for att in class_data['attendance_data']:
#                 table_data.append([
#                     Paragraph(att['date'].strftime('%Y-%m-%d'), body_style),
#                     Paragraph(att['status'], body_style),
#                     Paragraph(att['check_in_time'], body_style),
#                     Paragraph(att['check_out_time'], body_style)
#                 ])
#             if not class_data['attendance_data']:
#                 table_data.append(['No attendance records', '-', '-', '-'])

#             table = Table(table_data, colWidths=col_widths_attendance)
#             table.setStyle(TableStyle([
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, 0), 10),
#                 ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                 ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('FONTSIZE', (0, 1), (-1, -1), 9),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                 ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                 ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#             ]))
#             elements.append(table)

#             # Attendance Summary
#             summary = (
#                 f"Present Days: {class_data['present_count']} | "
#                 f"Absent Days: {class_data['absent_count']} | "
#                 f"Total Days: {class_data['total_days']} | "
#                 f"Attendance Rate: {class_data['attendance_rate']:.2f}%"
#             )
#             elements.append(Paragraph(summary, summary_style))
#             elements.append(Spacer(1, 1*cm))

#     # Build PDF
#     try:
#         doc.build(elements)
#         messages.success(request, 'You successfully generated the PDF, kindly check your downloads!')
#         return response
#     except Exception as e:
#         messages.error(request, f"Error generating PDF: {str(e)}")
#         return redirect('student_profile')


# from django.contrib import messages
# from django.shortcuts import render, redirect
# from django.db.models import Sum, Avg
# from django.urls import reverse
# from django.core.serializers.json import DjangoJSONEncoder
# import json
# from decimal import Decimal
# from django.db.models import Q as models_Q
# import calendar
# from attendance.models import StudentAttendance
# from datetime import date

# @login_required
# def student_profile(request):
#     if not request.user.is_student:
#         messages.error(request, "You are not authorized to view this page.")
#         return redirect('login_view')

#     # Get all Student profiles for the logged-in user
#     student_profiles = Student.objects.filter(user=request.user).select_related('teacherclass__academicclassyear', 'manager')
#     if not student_profiles.exists():
#         messages.error(request, "Student profile not found.")
#         return redirect('login_view')

#     academic_data = []
#     performance_chart_labels = []
#     performance_chart_data = []

#     financial_data = []
#     total_required_all = Decimal('0.00')
#     total_paid_all = Decimal('0.00')
#     total_discount_all = Decimal('0.00')
#     total_initial_payment = Decimal('0.00')
#     payment_chart_labels = []
#     payment_chart_amounts = []
#     payment_chart_paid = []

#     attendance_data = []  # Attendance data per class

#     for student in student_profiles:
#         teacherclass = student.teacherclass
#         manager = student.manager
#         photo = student.photo

#         # Academic Data (unchanged)
#         examination_names = ExaminationName.objects.filter(user=manager)
#         if not examination_names.exists():
#             messages.warning(request, f"No examinations found for class: {teacherclass.ClassName}")

#         grading_required = GradingModel.objects.filter(user=manager).first()
#         if not grading_required:
#             messages.warning(request, f"No grading system defined for class: {teacherclass.ClassName}")

#         display = DisplayModel.objects.filter(user=manager).first()

#         subjects = Subject.objects.filter(teacherclass=teacherclass, user=manager)
#         if not subjects.exists():
#             messages.warning(request, f"No subjects found for class: {teacherclass.ClassName}")

#         # Define grade thresholds
#         if grading_required:
#             if grading_required.is_advance:
#                 grade_thresholds = {
#                     grading_required.grade_a: 'A',
#                     grading_required.grade_b: 'B',
#                     grading_required.grade_c: 'C',
#                     grading_required.grade_d: 'D',
#                     grading_required.grade_e: 'E',
#                     grading_required.grade_s: 'S',
#                     grading_required.grade_f: 'F'
#                 }
#             else:
#                 grade_thresholds = {
#                     grading_required.grade_a: 'A',
#                     grading_required.grade_b: 'B',
#                     grading_required.grade_c: 'C',
#                     grading_required.grade_d: 'D',
#                     grading_required.grade_f: 'F'
#                 }
#         else:
#             grade_thresholds = {
#                 80: 'A',
#                 70: 'B',
#                 60: 'C',
#                 50: 'D',
#                 0: 'F'
#             }

#         class_data = {
#             'class_name': teacherclass.ClassName.class_name,
#             'academic_year': teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A',
#             'examinations': [],
#         }

#         for exam in examination_names:
#             marks = Mark.objects.filter(
#                 student=student,
#                 examinationname=exam,
#                 teacherclass=teacherclass
#             ).select_related('subject')

#             if not marks.exists():
#                 messages.warning(request, f"No marks found for exam: {exam.exam_name} in class: {teacherclass.ClassName}")

#             if not subjects.exists():
#                 subjects = Subject.objects.filter(id__in=marks.values('subject')).distinct()
#                 if subjects.exists():
#                     messages.info(request, f"Using subjects from marks for exam: {exam.exam_name} in class: {teacherclass.ClassName}")
#                 else:
#                     messages.warning(request, f"No subjects associated with marks for exam: {exam.exam_name} in class: {teacherclass.ClassName}")

#             exam_data = {
#                 'exam_name': exam.exam_name,
#                 'subjects': [],
#                 'total_marks': 0,
#                 'average_marks': 0,
#                 'position': None,
#                 'total_students': Student.objects.filter(teacherclass=teacherclass).count()
#             }

#             for subject in subjects:
#                 mark_obj = marks.filter(subject=subject).first()
#                 mark_value = mark_obj.marks if mark_obj else None
#                 grade = '-'

#                 if mark_value is not None and grading_required:
#                     for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                         if mark_value >= threshold:
#                             grade = letter_grade
#                             break

#                 exam_data['subjects'].append({
#                     'name': subject.nameSubject if subject else 'Unknown Subject',
#                     'mark': mark_value if mark_value is not None else 'N/A',
#                     'grade': grade
#                 })

#             exam_marks = marks.aggregate(
#                 total=Sum('marks'),
#                 average=Avg('marks')
#             )
#             exam_data['total_marks'] = exam_marks['total'] or 0
#             exam_data['average_marks'] = round(exam_marks['average'] or 0, 2) if exam_marks['average'] else 0

#             students_ranked = Student.objects.filter(teacherclass=teacherclass).annotate(
#                 total_marks=Sum('marks__marks', filter=models_Q(
#                     marks__examinationname=exam,
#                     marks__teacherclass=teacherclass
#                 ))
#             ).order_by('-total_marks')

#             for idx, s in enumerate(students_ranked, 1):
#                 if s.id == student.id:
#                     exam_data['position'] = idx
#                     break

#             class_data['examinations'].append(exam_data)
#             performance_chart_labels.append(f"{exam.exam_name} ({class_data['class_name']} - {class_data['academic_year']})")
#             performance_chart_data.append(exam_data['average_marks'])

#         academic_data.append(class_data)

#         # Financial Data per TeacherClass
#         class_financial_data = {
#             'class_name': teacherclass.ClassName.class_name,
#             'academic_year': teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A',
#             'fees': [],
#             'total_required': Decimal('0.00'),
#             'total_paid': Decimal('0.00'),
#             'total_discount': Decimal('0.00'),
#             'initial_payment': Decimal('0.00'),
#             'total_balance': Decimal('0.00'),
#             'payment_chart': {
#                 'labels': [],
#                 'amounts': [],
#                 'paid': []
#             }
#         }

#         # Fetch all student fees, payments, and discounts
#         student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#         accountants = Teacher.objects.filter(created_by=manager).values_list('user', flat=True)
#         all_payments = PayFee.objects.filter(
#             student=student,
#             user__in=accountants,
#             fee__in=student_fees.values('fee')
#         ).select_related('fee').order_by('-date_paid')

#         discounts = Discount.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#         total_discount = discounts.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0.00')
#         class_financial_data['total_discount'] = total_discount

#         # Fetch initial payment from StudentRegistration
#         student_focus = StudentFocus.objects.filter(student=student).first()
#         if student_focus:
#             student_registration = StudentRegistration.objects.filter(studentfocus=student_focus).first()
#             if student_registration and student_registration.initial_payment:
#                 class_financial_data['initial_payment'] = student_registration.initial_payment
#                 total_initial_payment += student_registration.initial_payment

#         for fee_assignment in student_fees:
#             fee = fee_assignment.fee
#             payments = all_payments.filter(fee=fee)
#             paid_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#             discount = discounts.filter(fee=fee).first()
#             discount_amount = discount.discount_amount if discount else Decimal('0.00')
#             adjusted_amount = fee_assignment.amount_required - discount_amount

#             payment_timing = "No Payment"
#             if payments.exists():
#                 latest_payment = payments.order_by('-date_paid').first()
#                 if latest_payment and latest_payment.date_paid:
#                     if latest_payment.date_paid < fee_assignment.start_date:
#                         payment_timing = "In Advance"
#                     elif fee_assignment.start_date <= latest_payment.date_paid <= fee_assignment.end_date:
#                         payment_timing = "On Time"
#                     elif latest_payment.date_paid > fee_assignment.end_date:
#                         payment_timing = "After Deadline"

#             fee_data = {
#                 'fee_name': fee.fee_name,
#                 'amount_required': fee_assignment.amount_required,
#                 'discount': discount_amount,
#                 'adjusted_amount': adjusted_amount,
#                 'paid': paid_amount,
#                 'balance': adjusted_amount - paid_amount,
#                 'status': 'Paid' if paid_amount >= adjusted_amount else 'Pending',
#                 'payment_timing': payment_timing,
#                 'start_date': fee_assignment.start_date,
#                 'end_date': fee_assignment.end_date,
#                 'payments': [{
#                     'date': p.date_paid.strftime('%Y-%m-%d'),
#                     'amount': p.amount_paid,
#                     'description': p.description or '-',
#                     'payer_account_no': p.payer_account_no or '-'
#                 } for p in payments]
#             }

#             class_financial_data['fees'].append(fee_data)
#             class_financial_data['total_required'] += adjusted_amount
#             class_financial_data['total_paid'] += paid_amount
#             class_financial_data['total_balance'] += (adjusted_amount - paid_amount)
#             class_financial_data['payment_chart']['labels'].append(fee.fee_name)
#             class_financial_data['payment_chart']['amounts'].append(float(adjusted_amount))
#             class_financial_data['payment_chart']['paid'].append(float(paid_amount))

#             # Aggregate for overall totals
#             total_required_all += adjusted_amount
#             total_paid_all += paid_amount
#             total_discount_all += discount_amount
#             payment_chart_labels.append(f"{fee.fee_name} ({class_financial_data['class_name']} - {class_financial_data['academic_year']})")
#             payment_chart_amounts.append(float(adjusted_amount))
#             payment_chart_paid.append(float(paid_amount))

#         financial_data.append(class_financial_data)

#         # Attendance Data per TeacherClass
#         current_date = timezone.now().date()
#         current_month = current_date.month
#         current_year = current_date.year
#         days_in_month = calendar.monthrange(current_year, current_month)[1]
#         date_headers = [date(current_year, current_month, i + 1) for i in range(days_in_month)]

#         attendances = StudentAttendance.objects.filter(student=student, date__in=date_headers).values('date', 'status', 'check_in_time', 'check_out_time')
#         attendance_dict = {att['date']: {
#             'status': att['status'],
#             'check_in_time': att['check_in_time'],
#             'check_out_time': att['check_out_time']
#         } for att in attendances}

#         class_attendance_data = []
#         for day in date_headers:
#             if day <= current_date:
#                 entry = attendance_dict.get(day, {'status': 'absent', 'check_in_time': None, 'check_out_time': None})
#                 status = entry['status']
#                 check_in_time = entry['check_in_time'].strftime('%H:%M') if entry['check_in_time'] else '-'
#                 check_out_time = entry['check_out_time'].strftime('%H:%M') if entry['check_out_time'] else '-'
#             else:
#                 status = '-'
#                 check_in_time = '-'
#                 check_out_time = '-'
#             class_attendance_data.append({
#                 'date': day,
#                 'status': 'P' if status == 'present' else 'A' if status == 'absent' else '-',
#                 'check_in_time': check_in_time,
#                 'check_out_time': check_out_time
#             })

#         present_count = sum(1 for att in class_attendance_data if att['status'] == 'P')
#         absent_count = sum(1 for att in class_attendance_data if att['status'] == 'A')
#         total_days = len([d for d in date_headers if d <= current_date])
#         attendance_rate = round((present_count / total_days * 100), 2) if total_days > 0 else 0

#         class_attendance = {
#             'class_name': teacherclass.ClassName.class_name,
#             'academic_year': teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A',
#             'month': calendar.month_name[current_month],
#             'year': current_year,
#             'attendance_data': class_attendance_data,
#             'present_count': present_count,
#             'absent_count': absent_count,
#             'total_days': total_days,
#             'attendance_rate': attendance_rate
#         }
#         attendance_data.append(class_attendance)

#     context = {
#         'student': {
#             'fullName': student_profiles.first().fullName,
#             'indexNumber': student_profiles.first().indexNumber,
#             'sex': student_profiles.first().sex,
#             'contact': student_profiles.first().contact,
#             'photo': photo
#         },
#         'academic': {
#             'classes': academic_data,
#             'grading_system': 'Advanced' if grading_required and grading_required.is_advance else 'Ordinary',
#             'performance_chart': {
#                 'labels': json.dumps(performance_chart_labels, cls=DjangoJSONEncoder),
#                 'data': json.dumps(performance_chart_data, cls=DjangoJSONEncoder)
#             }
#         },
#         'financial': {
#             'classes': financial_data,
#             'total_required': total_required_all,
#             'total_paid': total_paid_all,
#             'total_balance': total_required_all - total_paid_all,
#             'total_discount': total_discount_all,
#             'total_initial_payment': total_initial_payment,
#             'all_payments': [{
#                 'fee_name': p.fee.fee_name,
#                 'date': p.date_paid.strftime('%Y-%m-%d'),
#                 'amount': p.amount_paid,
#                 'description': p.description or '-',
#                 'payer_account_no': p.payer_account_no or '-',
#                 'class_name': p.fee.teacherclass.ClassName.class_name,
#                 'academic_year': p.fee.teacherclass.academicclassyear.academic_year_name if p.fee.teacherclass.academicclassyear else 'N/A'
#             } for p in all_payments],
#             'payment_chart': {
#                 'labels': json.dumps(payment_chart_labels, cls=DjangoJSONEncoder),
#                 'amounts': json.dumps(payment_chart_amounts, cls=DjangoJSONEncoder),
#                 'paid': json.dumps(payment_chart_paid, cls=DjangoJSONEncoder)
#             }
#         },
#         'attendance': {
#             'classes': attendance_data
#         },
#         'display': display,
#         'subjects': subjects
#     }

#     return render(request, 'student_profile.html', context)


# @login_required
# def change_profile_photo(request):
#     if not request.user.is_student:
#         messages.error(request, "You are not authorized to perform this action.")
#         return redirect('student_profile')

#     try:
#         student = Student.objects.get(user=request.user)
#     except Student.DoesNotExist:
#         messages.error(request, "Student profile not found.")
#         return redirect('student_profile')

#     if request.method == 'POST':
#         if 'photo' in request.FILES:
#             student.photo = request.FILES['photo']
#             student.save()
#             messages.success(request, "Profile photo updated successfully.")
#         else:
#             messages.error(request, "Please select an image file.")
#         return redirect('student_profile')

#     # If not POST, redirect back to profile (shouldn't happen with form)
#     return redirect('student_profile')


# @login_required
# def send_single_student_sms(request):
#     # Check for SmsConfiguration existence first
#     try:
#         sms_data = SmsConfiguration.objects.get(user=request.user)
#     except SmsConfiguration.DoesNotExist:
#         logger.error("No SMS configuration found for user")
#         messages.error(request, "No sms configuration")
#         return render(request, 'send_single_student_sms.html', {
#             'teacher_classes': TeacherClass.objects.filter(user=request.user).order_by('ClassName'),
#             'students': Student.objects.none(),
#             'selected_class_id': None
#         })

#     teacher_classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName')
#     description = DisplayModel.objects.filter(user=request.user).last()
#     url_required = sms_data.url_required
#     source_address = sms_data.source_addr
#     username_required = sms_data.username
#     pswd = sms_data.pswd

#     # Get selected class_id from GET parameters
#     class_id = request.GET.get('class_id', '')
#     selected_class_id = class_id if class_id and class_id.strip() else None

#     # Filter students
#     students = Student.objects.filter(
#         Q(user=request.user) | Q(manager=request.user)
#     )
#     if selected_class_id:
#         try:
#             students = students.filter(teacherclass__id=selected_class_id)
#             logger.debug(f"Found {students.count()} students for class_id={selected_class_id}")
#         except ValueError:
#             logger.error(f"Invalid class_id: {class_id}")
#             messages.error(request, "Invalid class ID selected.")
#             students = Student.objects.none()

#     if request.method == 'POST':
#         try:
#             # Get student IDs from hidden input (joined by commas)
#             student_ids_str = request.POST.get('student_ids_hidden', '')
#             message = request.POST.get('message')

#             # Convert comma-separated string to list
#             student_ids = student_ids_str.split(',') if student_ids_str else []

#             if not student_ids or not message:
#                 logger.error(f"Missing data: student_ids={student_ids}, message={message}")
#                 messages.error(request, "Please select at least one student and enter a message.")
#                 return render(request, 'send_single_student_sms.html', {
#                     'teacher_classes': teacher_classes,
#                     'students': students,
#                     'selected_class_id': selected_class_id
#                 })

#             # Fetch students
#             students_to_message = Student.objects.filter(
#                 Q(id__in=student_ids) & (Q(user=request.user) | Q(manager=request.user))
#             )
#             if not students_to_message.exists():
#                 logger.error(f"No valid students found for IDs: {student_ids}")
#                 messages.error(request, "No valid students selected.")
#                 return render(request, 'send_single_student_sms.html', {
#                     'teacher_classes': teacher_classes,
#                     'students': students,
#                     'selected_class_id': selected_class_id
#                 })

#             success_count = 0
#             for student in students_to_message:
#                 if not student.contact or not isinstance(student.contact, int) or student.contact < 255000000000:
#                     logger.warning(f"Invalid contact for {student.fullName}: {student.contact}")
#                     messages.error(request, f"Invalid or missing contact number for {student.fullName}.")
#                     continue

#                 dest_addr = str(student.contact)
#                 logger.info(f"Sending SMS to {student.fullName} at {dest_addr}")

#                 sms_content = f"{description.header if description else 'Message'},\n{message}\n..Powered By InnoBanks."

#                 payload = {
#                     "source_addr": source_address,
#                     "encoding": 0,
#                     "message": sms_content,
#                     "recipients": [
#                         {
#                             "recipient_id": student.id,
#                             "dest_addr": dest_addr
#                         }
#                     ]
#                 }

#                 response = requests.post(url_required, json=payload, auth=HTTPBasicAuth(username_required, pswd))

#                 if response.status_code == 200:
#                     logger.info(f"SMS sent successfully to {student.fullName}")
#                     messages.success(request, f"Message sent successfully to {student.fullName}!")
#                     success_count += 1
#                 else:
#                     logger.error(f"Failed to send SMS to {student.fullName}. Error: {response.text}")
#                     messages.error(request, f"Failed to send message to {student.fullName}. Error: {response.text}")

#             if success_count == len(student_ids):
#                 messages.success(request, "Messages sent successfully to all selected students!")
#             elif success_count > 0:
#                 messages.warning(request, f"Messages sent to {success_count} of {len(student_ids)} selected students.")

#         except Exception as e:
#             logger.error(f"Error sending SMS: {str(e)}")
#             messages.error(request, f"Error: {str(e)}")

#         return render(request, 'send_single_student_sms.html', {
#             'teacher_classes': teacher_classes,
#             'students': students,
#             'selected_class_id': selected_class_id
#         })

#     return render(request, 'send_single_student_sms.html', {
#         'teacher_classes': teacher_classes,
#         'students': students,
#         'selected_class_id': selected_class_id
#     })
    
# @login_required
# def search_students(request):
#     query = request.GET.get('q', '')
#     class_id = request.GET.get('class_id', '')
    
#     logger.debug(f"Search students: user={request.user.username}, query={query}, class_id={class_id}")

#     # Start with students where the user is either the 'user' or 'manager'
#     students = Student.objects.filter(
#         Q(user=request.user) | Q(manager=request.user)
#     )
    
#     # Log all students before class filter
#     logger.debug(f"Students before class filter: {students.count()}")

#     # Filter by class if provided
#     if class_id and class_id.strip():
#         try:
#             students = students.filter(teacherclass__id=class_id)
#             logger.debug(f"Students after class filter: {students.count()}")
#         except ValueError:
#             logger.error(f"Invalid class_id: {class_id}")
#             return JsonResponse({'students': [], 'error': 'Invalid class ID'})

#     # Filter by search query (fullName or indexNumber)
#     if query:
#         students = students.filter(
#             Q(fullName__icontains=query) | 
#             Q(indexNumber__icontains=query)
#         )
    
#     logger.debug(f"Final students found: {students.count()}")

#     students_data = [
#         {
#             'id': student.id,
#             'fullName': student.fullName or 'Unnamed Student',
#             'indexNumber': student.indexNumber or 'No Index',
#             'className': student.teacherclass.ClassName if student.teacherclass else 'No Class'
#         }
#         for student in students
#     ]
    
#     return JsonResponse({'students': students_data})



# @csrf_exempt  # Using CSRF token in headers, so exempting CSRF check here
# @require_POST
# def update_merge_selection(request):
#     try:
#         # Parse JSON body from the request
#         data = json.loads(request.body)
#         upload_id = data.get('upload_id')
#         for_merging_pdf = data.get('for_merging_pdf')

#         # Validate inputs
#         if upload_id is None or for_merging_pdf is None:
#             return JsonResponse({'success': False, 'error': 'Missing upload_id or for_merging_pdf'}, status=400)

#         # Get and update the TermMarksUpload instance
#         upload = TermMarksUpload.objects.get(id=upload_id)
#         upload.for_merging_pdf = for_merging_pdf
#         upload.save()

#         return JsonResponse({'success': True}, status=200)

#     except TermMarksUpload.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Upload not found'}, status=404)
#     except json.JSONDecodeError:
#         return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
#     except Exception as e:
#         return JsonResponse({'success': False, 'error': str(e)}, status=500)
# from .models import ExaminationName

# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from django.db.models import Q, Sum, Avg
# from django.contrib.auth.decorators import login_required
# import json
# import logging
# import requests
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.db.models import Sum, Avg, Q
# from django.http import JsonResponse
# from .models import TeacherClass, GradingModel, ExaminationName, Student, Subject, Mark, ExcludeSubject, RequiredSubject, SmsConfiguration, DisplayModel
# import requests
# from requests.auth import HTTPBasicAuth
# import logging
# from django.db.models import Prefetch

# logger = logging.getLogger(__name__)

# @login_required
# def send_student_sms(request):
#     if request.method != 'POST':
#         messages.error(request, "Invalid request method.")
#         return render(request, 'all_student_marks.html', {
#             'classes': TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName')
#         })

#     # Parse form data
#     student_ids_str = request.POST.get('student_ids_hidden', '')
#     class_id = request.POST.get('class_id')
#     grade_id = request.POST.get('grade_id')
#     examination_id = request.POST.get('examination_id')
#     custom_message = request.POST.get('message', '')

#     # Convert comma-separated student IDs to list
#     student_ids = [id.strip() for id in student_ids_str.split(',') if id.strip()] if student_ids_str else []

#     # Validate inputs
#     if not class_id or not grade_id or not examination_id:
#         messages.error(request, "Class, grade, or examination not specified.")
#         return render(request, 'all_student_marks.html', {
#             'classes': TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName')
#         })

#     # Fetch necessary objects
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#     grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     examination = get_object_or_404(ExaminationName, id=examination_id, user=request.user)
#     description = DisplayModel.objects.filter(user=request.user).last()

#     if not student_ids:
#         messages.error(request, "Please select at least one student.")
#         return render(request, 'all_student_marks.html', {
#             'teacherclass': teacherclass,
#             'grading_required': grading_required,
#             'selected_examination': examination,
#             'classes': TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName'),
#             'students': Student.objects.filter(teacherclass__id=class_id).prefetch_related('marks'),
#             'subjects': Subject.objects.filter(teacherclass__id=class_id),
#             'exclude_subjects': ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True),
#             'display': DisplayModel.objects.filter(user=request.user)
#         })

#     # Fetch SMS configuration
#     sms_data = get_object_or_404(SmsConfiguration, user=request.user)
#     url_required = sms_data.url_required
#     source_address = sms_data.source_addr
#     username_required = sms_data.username
#     pswd = sms_data.pswd

#     # Fetch selected students
#     students = Student.objects.filter(
#         Q(id__in=student_ids) & Q(teacherclass=teacherclass)
#     ).prefetch_related('marks')
#     if not students.exists():
#         messages.error(request, "No valid students selected.")
#         return render(request, 'all_student_marks.html', {
#             'teacherclass': teacherclass,
#             'grading_required': grading_required,
#             'selected_examination': examination,
#             'classes': TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName'),
#             'students': Student.objects.filter(teacherclass__id=class_id).prefetch_related('marks'),
#             'subjects': Subject.objects.filter(teacherclass__id=class_id),
#             'exclude_subjects': ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True),
#             'display': DisplayModel.objects.filter(user=request.user)
#         })

#     # Get filtered subjects
#     required_subjects = RequiredSubject.objects.filter(
#         user=request.user,
#         level='Alevel' if grading_required.is_advance else 'Olevel'
#     ).values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=required_subjects, user=request.user)

#     # Define grading logic
#     if grading_required.is_advance:
#         exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#         grade_thresholds = {
#             grading_required.grade_a: 'A',
#             grading_required.grade_b: 'B',
#             grading_required.grade_c: 'C',
#             grading_required.grade_d: 'D',
#             grading_required.grade_e: 'E',
#             grading_required.grade_s: 'S',
#             grading_required.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         min_subjects_for_division = 3
#     else:
#         exclude_subjects = []
#         grade_thresholds = {
#             grading_required.grade_a: 'A',
#             grading_required.grade_b: 'B',
#             grading_required.grade_c: 'C',
#             grading_required.grade_d: 'D',
#             grading_required.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}
#         min_subjects_for_division = 7

#     division_thresholds = [
#         {'max': grading_required.division_1, 'label': 'I'},
#         {'max': grading_required.division_2, 'label': 'II'},
#         {'max': grading_required.division_3, 'label': 'III'},
#         {'max': grading_required.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

#     # Pre-calculate marks and averages for all students in the class
#     students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#         total_marks=Sum('marks__marks', filter=Q(marks__subject__id__in=required_subjects, marks__examinationname=examination)),
#         average_marks=Avg('marks__marks', filter=Q(marks__subject__id__in=required_subjects, marks__examinationname=examination))
#     ).order_by('-average_marks')

#     marks_evaluation_dict = {
#         s.id: {
#             'total_marks': s.total_marks or 0,
#             'average_marks': s.average_marks or 0,
#             'position': idx + 1
#         } for idx, s in enumerate(students_marks_evaluation)
#     }

#     # Prepare student data for template (same as all_student_marks)
#     student_data = []
#     for student in students_marks_evaluation:
#         student_marks = []
#         all_grades = []
#         grades_for_division = []

#         student_subjects_with_marks = Mark.objects.filter(
#             student=student,
#             teacherclass=teacherclass,
#             examinationname=examination,
#             subject__in=subjects
#         ).select_related('subject')

#         for subject in subjects:
#             mark_obj = student_subjects_with_marks.filter(subject=subject).first()
#             mark_value = mark_obj.marks if mark_obj else None
#             grade = '-'
#             if mark_value is not None:
#                 for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                     if mark_value >= threshold:
#                         grade = letter_grade
#                         break
#             if mark_value is not None:
#                 student_marks.append({
#                     'subject': subject.id,
#                     'subject_name': subject.nameSubject,
#                     'mark': mark_value,
#                     'grade': grade,
#                     'is_excluded': subject.id in exclude_subjects
#                 })
#             all_grades.append(grade)
#             if not grading_required.is_advance or subject.id not in exclude_subjects:
#                 grades_for_division.append(grade)

#         filtered_grades = [g for g in grades_for_division if g != '-']
#         num_valid_subjects = len(filtered_grades)

#         if num_valid_subjects < min_subjects_for_division:
#             division = "Inc"
#             total_points = 0
#         else:
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:min_subjects_for_division]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break

#         student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#         overall_grade = 'F'
#         for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#             if student_average >= threshold:
#                 overall_grade = letter_grade
#                 break

#         has_valid_marks = any(grade != '-' for grade in all_grades)

#         student_data.append({
#             'id': student.id,
#             'fullName': student.fullName,
#             'sex': student.sex,
#             'indexNumber': student.indexNumber,
#             'marks': student_marks,
#             'total_marks': marks_evaluation_dict.get(student.id, {}).get('total_marks', 0),
#             'average_marks': student_average,
#             'grade': overall_grade,
#             'division': division,
#             'total_points': total_points,
#             'has_valid_marks': has_valid_marks
#         })

#     # Sort students by marks and assign positions
#     student_data.sort(key=lambda x: (-x['has_valid_marks'], -x['average_marks']))
#     for position, student in enumerate(student_data, 1):
#         student['position'] = position

#     # Send SMS to selected students
#     success_count = 0
#     error_messages = []

#     for student in students:
#         if not student.contact or not isinstance(student.contact, int) or student.contact < 255000000000:
#             error_messages.append(f"Invalid or missing contact number for {student.fullName}: {student.contact}")
#             logger.warning(f"Invalid contact for {student.fullName}: {student.contact}")
#             messages.error(request, f"Invalid or missing contact number for {student.fullName}.")
#             continue

#         dest_addr = str(student.contact)
#         logger.info(f"Sending SMS to {student.fullName} at {dest_addr}")

#         # Fetch marks for filtered subjects and specific examination
#         marks = Mark.objects.filter(
#             student=student,
#             teacherclass=teacherclass,
#             subject__id__in=required_subjects,
#             examinationname=examination
#         ).select_related('subject')
#         subjects_text = ""
#         all_grades = []
#         grades_for_division = []

#         if marks.exists():
#             subjects_list = []
#             for mark in marks:
#                 mark_value = mark.marks
#                 if mark_value is None:
#                     continue
#                 grade = '-'
#                 for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                     if mark_value >= threshold:
#                         grade = letter_grade
#                         break
#                 if grade != '-':
#                     subjects_list.append(f"{mark.subject.nameSubject}: {mark.marks} ({grade})")
#                     all_grades.append(grade)
#                     if not (grading_required.is_advance and mark.subject_id in exclude_subjects):
#                         grades_for_division.append(grade)
#             subjects_text = ", ".join(subjects_list) if subjects_list else "No valid marks available"
#         else:
#             subjects_text = "No valid marks available"

#         # Calculate division and points
#         filtered_grades = [g for g in grades_for_division if g != '-']
#         num_valid_subjects = len(filtered_grades)

#         if num_valid_subjects < min_subjects_for_division:
#             division = "Inc"
#             total_points = 0
#         else:
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:min_subjects_for_division]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break

#         student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#         overall_grade = 'F'
#         for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#             if student_average >= threshold:
#                 overall_grade = letter_grade
#                 break

#         header = description.header if description else f"{examination.exam_name} Results"
#         body = description.body if description else ""

#         # Construct SMS
#         sms_content = (
#             f"{header}\n{body}\n{custom_message}\n"
#             f"Results for {examination.exam_name}: {student.fullName}\n"
#             f"Subjects: {subjects_text}\n"
#             f"Total Marks: {marks_evaluation_dict.get(student.id, {}).get('total_marks', 0)}\n"
#             f"Average: {student_average:.2f}\n"
#             f"Position: {marks_evaluation_dict.get(student.id, {}).get('position', '-')}\n"
#             f"Grade: {overall_grade}\n"
#             f"Division: {division}\n"
#             f"Points: {total_points}\n"
#             f"..Powered By InnoBanks."
#         )

#         data = {
#             "source_addr": source_address,
#             "encoding": 0,
#             "message": sms_content,
#             "recipients": [{"recipient_id": student.id, "dest_addr": dest_addr}]
#         }

#         try:
#             response = requests.post(url_required, json=data, auth=HTTPBasicAuth(username_required, pswd))
#             if response.status_code == 200:
#                 success_count += 1
#                 messages.success(request, f"Message sent successfully to {student.fullName}!")
#             else:
#                 error_messages.append(f"Failed to send SMS to {student.fullName}. Error: {response.text}")
#                 logger.error(f"API response for {student.fullName}: {response.text}")
#                 messages.error(request, f"Failed to send message to {student.fullName}. Error: {response.text}")
#         except requests.RequestException as e:
#             error_messages.append(f"Failed to send SMS to {student.fullName}. Exception: {str(e)}")
#             logger.error(f"Exception for {student.fullName}: {str(e)}")
#             messages.error(request, f"Failed to send message to {student.fullName}. Exception: {str(e)}")

#     # Prepare messages for response
#     if success_count == len(student_ids):
#         messages.success(request, "Messages sent successfully to all selected students!")
#     elif success_count > 0:
#         messages.warning(request, f"Messages sent to {success_count} of {len(student_ids)} selected students.")
#     else:
#         messages.error(request, "No messages were sent due to errors.")

#     # If AJAX request, return JSON response
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         message_list = []
#         for message in messages.get_messages(request):
#             message_list.append({
#                 'message': str(message),
#                 'tags': message.tags
#             })
#         return JsonResponse({
#             'messages': message_list
#         })

#     # Prepare context for template
#     context = {
#         'students': student_data,
#         'subjects': subjects,
#         'display': [description] if description else DisplayModel.objects.filter(user=request.user)[:1],
#         'teacherclass': teacherclass,
#         'classes': TeacherClass.objects.filter(user=request.user).order_by('ClassName'),
#         'grades': GradingModel.objects.filter(user=request.user),
#         'examination_names': ExaminationName.objects.filter(user=request.user),
#         'selected_examination': examination,
#         'grading_required': grading_required,
#         'exclude_subjects': list(exclude_subjects) if grading_required.is_advance else [],
#     }

#     return render(request, 'all_student_marks.html', context)




# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404, render
# from django.contrib import messages
# from django.db.models import Q, Sum, Avg
# from django.conf import settings
# from django.core.mail import EmailMessage
# from django.utils import timezone
# from .models import TeacherClass, Student, GradingModel, ExaminationName, DisplayModel, Subject, Mark, ExcludeSubject, RequiredSubject
# from finance.models import StudentFee,Discount,PayFee
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from io import BytesIO
# import logging
# from rps_app.utils import get_email_settings  # Added import for get_email_settings
# from decimal import Decimal

# # Set up logging



# # Set up logging
# logger = logging.getLogger(__name__)

# @login_required
# def send_student_emails(request):
#     # Initialize response data for AJAX
#     response_data = {'messages': []}

#     if request.method != 'POST':
#         messages.error(request, "Invalid request method.")
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             response_data['messages'].append({'message': "Invalid request method.", 'tags': 'error'})
#             return JsonResponse(response_data, status=400)
#         return render(request, 'all_student_marks.html', {
#             'classes': TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName')
#         })

#     # Parse form data
#     student_ids_str = request.POST.get('student_ids_hidden', '')
#     class_id = request.POST.get('class_id')
#     grade_id = request.POST.get('grade_id')
#     examination_id = request.POST.get('examination_id')
#     custom_message = request.POST.get('message', '')

#     # Convert comma-separated student IDs to list
#     student_ids = [id.strip() for id in student_ids_str.split(',') if id.strip()] if student_ids_str else []

#     # Validate inputs
#     if not class_id or not grade_id or not examination_id:
#         messages.error(request, "Class, grade, or examination not specified.")
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             response_data['messages'].append({'message': "Class, grade, or examination not specified.", 'tags': 'error'})
#             return JsonResponse(response_data, status=400)
#         return render(request, 'all_student_marks.html', {
#             'classes': TeacherClass.objects.filter(user=request.user).order_by('ClassName')
#         })

#     try:
#         # Fetch necessary objects
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         examination = get_object_or_404(ExaminationName, id=examination_id, user=request.user)
#         description = DisplayModel.objects.filter(user=request.user).last()

#         if not student_ids:
#             messages.error(request, "Please select at least one student.")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 response_data['messages'].append({'message': "Please select at least one student.", 'tags': 'error'})
#                 return JsonResponse(response_data, status=400)
#             return render(request, 'all_student_marks.html', {
#                 'teacherclass': teacherclass,
#                 'grading_required': grading_required,
#                 'selected_examination': examination,
#                 'classes': TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName'),
#                 'students': Student.objects.filter(teacherclass__id=class_id).prefetch_related('marks'),
#                 'subjects': Subject.objects.filter(teacherclass__id=class_id),
#                 'exclude_subjects': ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True),
#                 'display': DisplayModel.objects.filter(user=request.user)
#             })

#         # Fetch email settings
#         try:
#             email_settings = get_email_settings(request.user)
#         except Exception as e:
#             messages.error(request, f"Failed to load email configuration: {str(e)}")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 response_data['messages'].append({'message': f"Failed to load email configuration: {str(e)}", 'tags': 'error'})
#                 return JsonResponse(response_data, status=500)
#             return render(request, 'all_student_marks.html', {
#                 'teacherclass': teacherclass,
#                 'grading_required': grading_required,
#                 'selected_examination': examination,
#                 'classes': TeacherClass.objects.filter(user=request.user).order_by('ClassName'),
#                 'students': Student.objects.filter(teacherclass__id=class_id).prefetch_related('marks'),
#                 'subjects': Subject.objects.filter(teacherclass__id=class_id),
#                 'exclude_subjects': ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True),
#                 'display': DisplayModel.objects.filter(user=request.user)
#             })

#         # Fetch selected students with prefetch for efficiency
#         students = Student.objects.filter(
#             Q(id__in=student_ids) & Q(teacherclass=teacherclass)
#         ).prefetch_related('marks__subject', 'marks__examinationname', 'assigned_fees__fee', 'payfee', 'discount_set')

#         if not students.exists():
#             messages.error(request, "No valid students selected.")
#             if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#                 response_data['messages'].append({'message': "No valid students selected.", 'tags': 'error'})
#                 return JsonResponse(response_data, status=400)
#             return render(request, 'all_student_marks.html', {
#                 'teacherclass': teacherclass,
#                 'grading_required': grading_required,
#                 'selected_examination': examination,
#                 'classes': TeacherClass.objects.filter(user=request.user).order_by('ClassName'),
#                 'students': Student.objects.filter(teacherclass__id=class_id).prefetch_related('marks'),
#                 'subjects': Subject.objects.filter(teacherclass__id=class_id),
#                 'exclude_subjects': ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True),
#                 'display': DisplayModel.objects.filter(user=request.user)
#             })

#         # Get filtered subjects
#         required_subjects = RequiredSubject.objects.filter(
#             user=request.user,
#             level='Alevel' if grading_required.is_advance else 'Olevel'
#         ).values_list('subject_id', flat=True)
#         subjects = Subject.objects.filter(id__in=required_subjects, user=request.user)

#         # Define grading logic
#         if grading_required.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading_required.grade_a: 'A',
#                 grading_required.grade_b: 'B',
#                 grading_required.grade_c: 'C',
#                 grading_required.grade_d: 'D',
#                 grading_required.grade_e: 'E',
#                 grading_required.grade_s: 'S',
#                 grading_required.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#             min_subjects_for_division = 3
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading_required.grade_a: 'A',
#                 grading_required.grade_b: 'B',
#                 grading_required.grade_c: 'C',
#                 grading_required.grade_d: 'D',
#                 grading_required.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}
#             min_subjects_for_division = 7

#         division_thresholds = [
#             {'max': grading_required.division_1, 'label': 'I'},
#             {'max': grading_required.division_2, 'label': 'II'},
#             {'max': grading_required.division_3, 'label': 'III'},
#             {'max': grading_required.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         # Pre-calculate marks and averages for all students in the class
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=Q(marks__subject__id__in=required_subjects, marks__examinationname=examination)),
#             average_marks=Avg('marks__marks', filter=Q(marks__subject__id__in=required_subjects, marks__examinationname=examination))
#         ).order_by('-average_marks')

#         marks_evaluation_dict = {
#             s.id: {
#                 'total_marks': s.total_marks or 0,
#                 'average_marks': s.average_marks or 0,
#                 'position': idx + 1
#             } for idx, s in enumerate(students_marks_evaluation)
#         }

#         # Send emails to selected students
#         success_count = 0
#         error_messages = []

#         for student in students:
#             if not student.user.email:
#                 error_messages.append(f"Invalid or missing email for {student.fullName}")
#                 logger.warning(f"Invalid email for {student.fullName}: {student.user.email}")
#                 messages.error(request, f"Invalid or missing email for {student.fullName}.")
#                 continue

#             recipient_email = student.user.email
#             logger.info(f"Sending email to {student.fullName} at {recipient_email}")

#             # Fetch marks for filtered subjects and specific examination
#             marks = student.marks.filter(
#                 teacherclass=teacherclass,
#                 subject__id__in=required_subjects,
#                 examinationname=examination
#             )
#             subjects_text = ""
#             all_grades = []
#             grades_for_division = []

#             if marks.exists():
#                 subjects_list = []
#                 for mark in marks:
#                     mark_value = mark.marks
#                     if mark_value is None:
#                         continue
#                     grade = '-'
#                     for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                         if mark_value >= threshold:
#                             grade = letter_grade
#                             break
#                     if grade != '-':
#                         subjects_list.append(f"{mark.subject.nameSubject}: {mark.marks} ({grade})")
#                         all_grades.append(grade)
#                         if not (grading_required.is_advance and mark.subject_id in exclude_subjects):
#                             grades_for_division.append(grade)
#                 subjects_text = "\n".join(subjects_list) if subjects_list else "No valid marks available"
#             else:
#                 subjects_text = "No valid marks available"

#             # Calculate division and points
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)

#             if num_valid_subjects < min_subjects_for_division:
#                 division = "Inc"
#                 total_points = 0
#             else:
#                 sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:min_subjects_for_division]
#                 total_points = sum(grade_points[g] for g in sorted_grades)
#                 division = 'IV'
#                 for threshold in division_thresholds:
#                     if total_points <= threshold['max']:
#                         division = threshold['label']
#                         break

#             student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#             overall_grade = 'F'
#             for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                 if student_average >= threshold:
#                     overall_grade = letter_grade
#                     break

#             header = description.header if description else f"{examination.exam_name} Results"
#             body = description.body if description else ""

#             # Construct email content (academic info only)
#             email_subject = f"{examination.exam_name} Results for {student.fullName}"
#             email_content = (
#                 f"{header}\n"
#                 f"{body}\n"
#                 f"{custom_message}\n\n"
#                 f"Results for {examination.exam_name}\n"
#                 f"Student: {student.fullName}\n"
#                 f"Subjects:\n{subjects_text}\n"
#                 f"Total Marks: {marks_evaluation_dict.get(student.id, {}).get('total_marks', 0)}\n"
#                 f"Average: {student_average:.2f}\n"
#                 f"Position: {marks_evaluation_dict.get(student.id, {}).get('position', '-')}\n"
#                 f"Grade: {overall_grade}\n"
#                 f"Division: {division}\n"
#                 f"Points: {total_points}\n\n"
#                 f"Please find attached a detailed report of your academic and financial information.\n"
#                 f"Powered by InnoBanks."
#             )

#             # Initialize original_settings before try block
#             original_settings = {
#                 'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
#                 'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
#                 'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
#                 'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
#                 'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
#                 'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
#                 'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
#             }

#             # Generate PDF with academic and financial data
#             try:
#                 # Fetch financial data
#                 student_fees = student.assigned_fees.filter(teacherclass=teacherclass)
#                 accountants = Teacher.objects.filter(created_by=teacherclass.user).values_list('user', flat=True)
#                 all_payments = student.payfee.filter(user__in=accountants).order_by('-date_paid')
#                 discounts = student.discount_set.filter(teacherclass=teacherclass, fee__in=[sf.fee for sf in student_fees])
#                 total_discount = sum(d.discount_amount for d in discounts) or Decimal('0.00')

#                 # Prepare academic data for PDF
#                 academic_data = [{
#                     'exam_name': examination.exam_name,
#                     'subjects': [],
#                     'total_marks': marks_evaluation_dict.get(student.id, {}).get('total_marks', 0),
#                     'average_marks': round(marks_evaluation_dict.get(student.id, {}).get('average_marks', 0), 2),
#                     'position': marks_evaluation_dict.get(student.id, {}).get('position', None),
#                     'total_students': Student.objects.filter(teacherclass=teacherclass).count(),
#                     'division': division,
#                     'points': total_points,
#                     'overall_grade': overall_grade
#                 }]
#                 for mark in marks:
#                     mark_value = mark.marks if mark.marks is not None else None
#                     grade = '-'
#                     if mark_value is not None:
#                         for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                             if mark_value >= threshold:
#                                 grade = letter_grade
#                                 break
#                     academic_data[0]['subjects'].append({
#                         'name': mark.subject.nameSubject if mark.subject else 'Unknown Subject',
#                         'mark': mark_value if mark_value is not None else 'N/A',
#                         'grade': grade
#                     })

#                 # Prepare financial data for PDF
#                 financial_data = []
#                 total_required = Decimal('0.00')
#                 total_paid = Decimal('0.00')

#                 for fee_assignment in student_fees:
#                     fee = fee_assignment.fee
#                     payments = all_payments.filter(fee=fee)
#                     paid_amount = payments.aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#                     discount = discounts.filter(fee=fee).first()
#                     discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                     adjusted_amount = fee.amount - discount_amount

#                     payment_timing = "No Payment"
#                     if payments:
#                         latest_payment = payments.order_by('-date_paid').first()
#                         if latest_payment and latest_payment.date_paid:
#                             if latest_payment.date_paid < fee.start_date:
#                                 payment_timing = "In Advance"
#                             elif fee.start_date <= latest_payment.date_paid <= fee.end_date:
#                                 payment_timing = "On Time"
#                             elif latest_payment.date_paid > fee.end_date:
#                                 payment_timing = "After Deadline"

#                     financial_data.append({
#                         'fee_name': fee.fee_name,
#                         'amount': fee.amount,
#                         'discount': discount_amount,
#                         'adjusted_amount': adjusted_amount,
#                         'paid': paid_amount,
#                         'balance': adjusted_amount - paid_amount,
#                         'status': 'Paid' if paid_amount >= adjusted_amount else 'Pending',
#                         'payment_timing': payment_timing,
#                         'payments': [{
#                             'date': p.date_paid.strftime('%Y-%m-%d'),
#                             'amount': p.amount_paid,
#                             'description': p.description or '-',
#                             'payer_account_no': p.payer_account_no or '-'
#                         } for p in payments]
#                     })

#                     total_required += adjusted_amount
#                     total_paid += paid_amount

#                 # Initialize PDF
#                 buffer = BytesIO()
#                 doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
#                 elements = []

#                 # Styles
#                 styles = getSampleStyleSheet()
#                 header_style = ParagraphStyle(
#                     name='Header',
#                     parent=styles['Heading1'],
#                     fontSize=16,
#                     alignment=1,  # Center alignment
#                     spaceAfter=10,
#                     textColor=colors.darkblue,
#                     leading=20
#                 )
#                 subheader_style = ParagraphStyle(
#                     name='Subheader',
#                     parent=styles['Heading2'],
#                     fontSize=12,
#                     alignment=1,  # Center alignment
#                     spaceAfter=8,
#                     textColor=colors.black
#                 )
#                 body_style = ParagraphStyle(
#                     name='Body',
#                     parent=styles['BodyText'],
#                     fontSize=9,  # Smaller font for table cells
#                     alignment=0,
#                     spaceAfter=6,
#                     leading=10
#                 )
#                 footer_style = ParagraphStyle(
#                     name='Footer',
#                     parent=styles['BodyText'],
#                     fontSize=8,
#                     alignment=1,
#                     textColor=colors.grey
#                 )
#                 discount_style = ParagraphStyle(
#                     name='Discount',
#                     parent=styles['BodyText'],
#                     fontSize=10,
#                     textColor=colors.red,
#                     spaceAfter=6
#                 )

#                 # Header and Icon
#                 elements.append(Paragraph(f"Student Report for {student.fullName}", header_style))
#                 if description and description.image:
#                     try:
#                         icon = Image(description.image.path, width=2*cm, height=2*cm)
#                         icon.hAlign = 'CENTER'
#                         elements.append(icon)
#                         elements.append(Spacer(1, 0.5*cm))
#                     except Exception as e:
#                         logger.warning(f"Error loading DisplayModel image for {student.fullName}: {e}")

#                 elements.append(Paragraph(
#                     f"<b>Index:</b> {student.indexNumber} | <b>Class:</b> {teacherclass.ClassName} | <b>Grading:</b> {'Advanced' if grading_required.is_advance else 'Ordinary'}",
#                     subheader_style
#                 ))
#                 elements.append(Paragraph(
#                     f"Generated by: {request.user.username} on {timezone.now().strftime('%Y-%m-%d %H:%M')}",
#                     footer_style
#                 ))
#                 elements.append(Spacer(1, 1*cm))

#                 # Academic Section
#                 elements.append(Paragraph("Academic Performance", subheader_style))
#                 if not academic_data or not academic_data[0]['subjects']:
#                     elements.append(Paragraph("No examination data available.", body_style))
#                 else:
#                     for exam in academic_data:
#                         elements.append(Paragraph(f"Examination: {exam['exam_name']}", subheader_style))
#                         # Calculate responsive column widths
#                         page_width = A4[0] - 2 * 1.5*cm
#                         col_widths = [
#                             0.35 * page_width,  # Subject
#                             0.15 * page_width,  # Marks
#                             0.15 * page_width,  # Grade
#                             0.35 * page_width   # Performance (%)
#                         ]
#                         # Academic Table
#                         table_data = [['Subject', 'Marks', 'Grade', 'Performance (%)']]
#                         for subject in exam['subjects']:
#                             table_data.append([
#                                 Paragraph(subject['name'], body_style),
#                                 Paragraph(str(subject['mark']), body_style),
#                                 Paragraph(subject['grade'], body_style),
#                                 Paragraph(str(subject['mark']) if subject['mark'] != 'N/A' else '0', body_style)
#                             ])
#                         if not exam['subjects']:
#                             table_data.append(['No subjects available', '-', '-', '-'])
                        
#                         table = Table(table_data, colWidths=col_widths)
#                         table.setStyle(TableStyle([
#                             ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                             ('FONTSIZE', (0, 0), (-1, 0), 10),
#                             ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                             ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                             ('FONTSIZE', (0, 1), (-1, -1), 9),
#                             ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                             ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                             ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                         ]))
#                         elements.append(table)
#                         # Summary
#                         summary = (
#                             f"Total Marks: {exam['total_marks']} | "
#                             f"Average: {exam['average_marks']:.2f}% | "
#                             f"Position: {exam['position'] or '-'}/{exam['total_students'] or '-'} | "
#                             f"Grade: {exam['overall_grade']} | "
#                             f"Division: {exam['division']} | "
#                             f"Points: {exam['points']}"
#                         )
#                         elements.append(Spacer(1, 0.5*cm))
#                         elements.append(Paragraph(summary, body_style))
#                         elements.append(Spacer(1, 1*cm))

#                 # Financial Section
#                 elements.append(Paragraph("Financial Information", subheader_style))
#                 if not financial_data:
#                     elements.append(Paragraph("No financial data available.", body_style))
#                 else:
#                     # Financial Table
#                     page_width = A4[0] - 2 * 1.5*cm
#                     col_widths = [
#                         0.20 * page_width,  # Fee
#                         0.12 * page_width,  # Original Amount
#                         0.12 * page_width,  # Discount
#                         0.12 * page_width,  # Adjusted Amount
#                         0.12 * page_width,  # Paid
#                         0.12 * page_width,  # Balance
#                         0.12 * page_width,  # Status
#                         0.18 * page_width   # Payment Timing
#                     ]
#                     table_data = [['Fee', 'Orig. Amt.', 'Discount', 'Adj. Amt.', 'Paid', 'Balance', 'Status', 'Payment Timing']]
#                     for fee in financial_data:
#                         table_data.append([
#                             Paragraph(fee['fee_name'], body_style),
#                             Paragraph(f"{fee['amount']:.2f}", body_style),
#                             Paragraph(f"{fee['discount']:.2f}", body_style),
#                             Paragraph(f"{fee['adjusted_amount']:.2f}", body_style),
#                             Paragraph(f"{fee['paid']:.2f}", body_style),
#                             Paragraph(f"{fee['balance']:.2f}", body_style),
#                             Paragraph(fee['status'], body_style),
#                             Paragraph(fee['payment_timing'], body_style)
#                         ])
                    
#                     table = Table(table_data, colWidths=col_widths)
#                     table.setStyle(TableStyle([
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                         ('FONTSIZE', (0, 0), (-1, 0), 10),
#                         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                         ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                         ('FONTSIZE', (0, 1), (-1, -1), 9),
#                         ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                         ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                     ]))
#                     elements.append(table)
#                     # Financial Summary
#                     summary = f"Total Required: {total_required:.2f} | Total Paid: {total_paid:.2f} | Total Balance: {total_required - total_paid:.2f} | Total Discount: {total_discount:.2f}"
#                     elements.append(Spacer(1, 0.5*cm))
#                     elements.append(Paragraph(summary, discount_style if total_discount > 0 else body_style))

#                     # Payment Records
#                     elements.append(Spacer(1, 1*cm))
#                     elements.append(Paragraph("Payment Records", subheader_style))
#                     col_widths = [
#                         0.20 * page_width,  # Fee
#                         0.15 * page_width,  # Date
#                         0.15 * page_width,  # Amount
#                         0.25 * page_width,  # Payer Account
#                         0.25 * page_width   # Description
#                     ]
#                     table_data = [['Fee', 'Date', 'Amount', 'Payer Account', 'Description']]
#                     for payment in all_payments:
#                         table_data.append([
#                             Paragraph(payment.fee.fee_name, body_style),
#                             Paragraph(payment.date_paid.strftime('%Y-%m-%d'), body_style),
#                             Paragraph(f"{payment.amount_paid:.2f}", body_style),
#                             Paragraph(payment.payer_account_no or '-', body_style),
#                             Paragraph(payment.description or '-', body_style)
#                         ])
#                     if not all_payments.exists():
#                         table_data.append(['No payment records found', '-', '-', '-', '-'])
                    
#                     table = Table(table_data, colWidths=col_widths)
#                     table.setStyle(TableStyle([
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                         ('FONTSIZE', (0, 0), (-1, 0), 10),
#                         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                         ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                         ('FONTSIZE', (0, 1), (-1, -1), 9),
#                         ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                         ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                     ]))
#                     elements.append(table)

#                 # Build PDF
#                 doc.build(elements)
#                 pdf_content = buffer.getvalue()
#                 buffer.close()

#                 # Send email with attachment
#                 email = EmailMessage(
#                     subject=email_subject,
#                     body=email_content,
#                     from_email=email_settings['DEFAULT_FROM_EMAIL'],
#                     to=[recipient_email],
#                 )
#                 email.attach(f"student_report_{student.indexNumber}.pdf".replace(" ", "_"), pdf_content, 'application/pdf')

#                 # Set email settings
#                 for key, value in email_settings.items():
#                     setattr(settings, key, value)

#                 # Send email
#                 email.send(fail_silently=False)

#                 success_count += 1
#                 messages.success(request, f"Email sent successfully to {student.fullName}!")
#             except Exception as e:
#                 error_messages.append(f"Failed to send email to {student.fullName}. Exception: {str(e)}")
#                 logger.error(f"Exception for {student.fullName}: {str(e)}")
#                 messages.error(request, f"Failed to send email to {student.fullName}. Exception: {str(e)}")
#                 buffer.close() if 'buffer' in locals() else None
#             finally:
#                 # Restore original settings
#                 for key, value in original_settings.items():
#                     if value is not None:
#                         setattr(settings, key, value)
#                     else:
#                         delattr(settings, key) if hasattr(settings, key) else None

#         # Prepare messages for response
#         if success_count == len(student_ids):
#             messages.success(request, "Emails sent successfully to all selected students!")
#         elif success_count > 0:
#             messages.warning(request, f"Emails sent to {success_count} of {len(student_ids)} selected students.")
#         else:
#             messages.error(request, "No emails were sent due to errors.")

#     except Exception as e:
#         messages.error(request, f"An unexpected error occurred: {str(e)}")
#         logger.error(f"Unexpected error in send_student_emails: {str(e)}")
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             response_data['messages'].append({'message': f"An unexpected error occurred: {str(e)}", 'tags': 'error'})
#             return JsonResponse(response_data, status=500)

#     # If AJAX request, return JSON response
#     if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         for message in messages.get_messages(request):
#             response_data['messages'].append({
#                 'message': str(message),
#                 'tags': message.tags
#             })
#         return JsonResponse(response_data)

#     # Prepare context for template
#     student_data = []
#     for student in students_marks_evaluation:
#         student_marks = []
#         all_grades = []
#         grades_for_division = []

#         student_subjects_with_marks = Mark.objects.filter(
#             student=student,
#             teacherclass=teacherclass,
#             examinationname=examination,
#             subject__in=subjects
#         ).select_related('subject')

#         for subject in subjects:
#             mark_obj = student_subjects_with_marks.filter(subject=subject).first()
#             mark_value = mark_obj.marks if mark_obj else None
#             grade = '-'
#             if mark_value is not None:
#                 for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                     if mark_value >= threshold:
#                         grade = letter_grade
#                         break
#             if mark_value is not None:
#                 student_marks.append({
#                     'subject': subject.id,
#                     'subject_name': subject.nameSubject,
#                     'mark': mark_value,
#                     'grade': grade,
#                     'is_excluded': subject.id in exclude_subjects
#                 })
#             all_grades.append(grade)
#             if not grading_required.is_advance or subject.id not in exclude_subjects:
#                 grades_for_division.append(grade)

#         filtered_grades = [g for g in grades_for_division if g != '-']
#         num_valid_subjects = len(filtered_grades)

#         if num_valid_subjects < min_subjects_for_division:
#             division = "Inc"
#             total_points = 0
#         else:
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:min_subjects_for_division]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break

#         student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#         overall_grade = 'F'
#         for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#             if student_average >= threshold:
#                 overall_grade = letter_grade
#                 break

#         has_valid_marks = any(grade != '-' for grade in all_grades)

#         student_data.append({
#             'id': student.id,
#             'fullName': student.fullName,
#             'sex': student.sex,
#             'indexNumber': student.indexNumber,
#             'marks': student_marks,
#             'total_marks': marks_evaluation_dict.get(student.id, {}).get('total_marks', 0),
#             'average_marks': student_average,
#             'grade': overall_grade,
#             'division': division,
#             'total_points': total_points,
#             'has_valid_marks': has_valid_marks
#         })

#     student_data.sort(key=lambda x: (-x['has_valid_marks'], -x['average_marks']))
#     for position, student in enumerate(student_data, 1):
#         student['position'] = position

#     context = {
#         'students': student_data,
#         'subjects': subjects,
#         'display': [description] if description else DisplayModel.objects.filter(user=request.user)[:1],
#         'teacherclass': teacherclass,
#         'classes': TeacherClass.objects.filter(user=request.user).order_by('ClassName'),
#         'grades': GradingModel.objects.filter(user=request.user),
#         'examination_names': ExaminationName.objects.filter(user=request.user),
#         'selected_examination': examination,
#         'grading_required': grading_required,
#         'exclude_subjects': list(exclude_subjects) if grading_required.is_advance else [],
#     }

#     return render(request, 'all_student_marks.html', context)

# @login_required
# def search_students(request):
#     query = request.GET.get('q', '')
#     class_id = request.GET.get('class_id', '')
    
#     # Start with all students for the user
#     students = Student.objects.filter(user=request.user)
    
#     # Filter by class if provided
#     if class_id:
#         students = students.filter(teacherclass__id=class_id)
    
#     # Filter by search query (fullName or indexNumber)
#     if query:
#         students = students.filter(
#             models.Q(fullName__icontains=query) | 
#             models.Q(indexNumber__icontains=query)
#         )
    
#     # Prepare response data
#     students_data = [
#         {
#             'id': student.id,
#             'fullName': student.fullName,
#             'indexNumber': student.indexNumber,
#             'className': student.teacherclass.ClassName if student.teacherclass else 'No Class'
#         }
#         for student in students
#     ]
    
#     return JsonResponse({'students': students_data})



# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import render, get_object_or_404
# from django.contrib import messages
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from .models import TeacherClass, GradingModel, Subject, RequiredSubject, ExcludeSubject, Student, TermMarksUpload
# import datetime
# import os
# import tabula
# import pandas as pd
# import re

# @login_required
# def ca_based_result(request, class_id=None, grade_id=None):
#     # Prefetch related data
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).prefetch_related('student_set')
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user,academicclassyear__active_year=True).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'ca_based_result.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         # Verify teacher authorization
#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by
#         except Teacher.DoesNotExist:
#             messages.error(request, "Your account is not linked to a valid teacher profile.")
#             return redirect('teacher_dashboard')

#         if not creator:
#             messages.error(request, "You are not authorized to generate reports.")
#             return redirect('teacher_dashboard')

#         # Determine level
#         level = 'Alevel' if grading.is_advance else 'Olevel'
        
#         # Fetch required subjects
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subject_ids = required_subjects.values_list('subject_id', flat=True)
#         subjects_db = Subject.objects.filter(id__in=subject_ids, user=request.user)
#         subjects_map = {s.nameSubject: s for s in subjects_db}

#         # Grading setup
#         if grading.is_advance:
#             exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True))
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_e: 'E', grading.grade_s: 'S',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = set()
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         # Fetch term uploads
#         term_uploads = TermMarksUpload.objects.filter(
#             user=request.user,
#             teacherclass=teacherclass,
#             for_merging_pdf=False
#         ).select_related('teacherclass')
#         if not term_uploads.exists():
#             messages.error(request, "No unchecked term marks PDFs available for generating CA-based results.")
#             return render(request, 'ca_based_result.html', context)

#         # Process PDFs
#         term_data = {}
#         subjects_set = set()
#         for upload in term_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file for {upload.term_name} not found at {pdf_path}.")
#                 return render(request, 'ca_based_result.html', context)

#             try:
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, stream=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in {upload.term_name} PDF.")
#                     return render(request, 'ca_based_result.html', context)

#                 df = pd.concat([df.dropna(how='all') for df in dfs], ignore_index=True)
#                 df.columns = df.columns.str.strip()
#                 if all(col not in df.columns for col in ['S/No', 'Student Name', 'Sex', 'Index No']):
#                     messages.error(request, f"Missing required headers in {upload.term_name} PDF.")
#                     return render(request, 'ca_based_result.html', context)

#                 df = df.rename(columns={'S/No': 'S/No', 'Student Name': 'fullName', 'Sex': 'sex', 'Index No': 'indexNumber'})
#                 term_data[upload.term_name] = df
#                 excluded_cols = ['S/No', 'fullName', 'sex', 'indexNumber', 'Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']
#                 subjects_set.update([col for col in df.columns if col not in excluded_cols and col in subjects_map])
#             except Exception as e:
#                 messages.error(request, f"Error processing PDF for {upload.term_name}: {str(e)}.")
#                 return render(request, 'ca_based_result.html', context)

#         students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#             Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects_db).select_related('subject', 'user'))
#         )
#         student_data = []

#         def get_grade(mark):
#             if pd.isna(mark) or mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_remark(grade):
#             remark_map = {
#                 'A': 'Excellent',
#                 'B': 'Very Good',
#                 'C': 'Good',
#                 'D': 'Pass',
#                 'E': 'Poor',
#                 'S': 'Subsidiary',
#                 'F': 'Fail',
#                 '-': '-'
#             }
#             return remark_map.get(grade, '-')

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         # Process students
#         for student in students:
#             student_dict = {'id': student.id, 'fullName': student.fullName, 'sex': student.sex, 'indexNumber': student.indexNumber}
#             marks_list = []
#             total_marks = 0
#             subject_count = 0

#             for subject_name in subjects_set:
#                 if subject_name not in subjects_map:
#                     continue
#                 subject = subjects_map[subject_name]
#                 marks = []
#                 for term_name, term_df in term_data.items():
#                     student_row = term_df[term_df['indexNumber'] == str(student.indexNumber)]
#                     if not student_row.empty and subject_name in student_row.columns:
#                         mark = student_row[subject_name].iloc[0]
#                         try:
#                             if isinstance(mark, str):
#                                 numeric_part = re.search(r'^\d+\.?\d*', mark)
#                                 mark = float(numeric_part.group()) if numeric_part else 0
#                             else:
#                                 mark = float(mark) if pd.notna(mark) else 0
#                             marks.append(mark)
#                         except:
#                             marks.append(0)
#                     else:
#                         marks.append(0)

#                 annual_mark = sum(marks)
#                 if annual_mark > 0:
#                     grade = get_grade(annual_mark)
#                     # Fetch teacher name from Mark model
#                     mark_obj = student.marks.filter(subject=subject).first()
#                     teacher_name = mark_obj.user.teacher_profile.first().teacherName or mark_obj.user.username if mark_obj and mark_obj.user else '-'
#                     marks_list.append({
#                         'subject_id': subject.id,
#                         'subject_name': subject_name,
#                         'mark': annual_mark,
#                         'grade': grade,
#                         'teacher': teacher_name,
#                         'is_excluded': subject.id in exclude_subjects
#                     })
#                     total_marks += annual_mark
#                     subject_count += 1

#             if not marks_list:
#                 continue

#             student_dict['marks'] = marks_list
#             student_dict['total_marks'] = total_marks
#             student_dict['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student_dict['grade'] = get_grade(student_dict['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student_dict['division'] = division
#             student_dict['total_points'] = total_points

#             student_data.append(student_dict)

#         student_data.sort(key=lambda x: x['total_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         # Generate PDF
#         response = HttpResponse(content_type='application/pdf')
#         filename = f"CABasedResults_{teacherclass.ClassName.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style = styles['Heading1']
#         subheader_style = styles['Heading2']
#         body_style = styles['BodyText']
#         footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#         bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#         header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#         body_style.fontSize = 7

#         def add_page_number(canvas, doc):
#             page_num = canvas.getPageNumber()
#             text = f"Page {page_num}"
#             canvas.saveState()
#             canvas.setFont("Helvetica", 8)
#             canvas.setFillColor(colors.grey)
#             canvas.drawCentredString(A4[0]/2, 15, text)
#             canvas.restoreState()

#         display = DisplayModel.objects.filter(user=request.user).first()
#         header_text = display.header if display else f"CA-Based Results for {teacherclass.ClassName}"
#         elements.append(Paragraph(header_text, header_style))
#         elements.append(Spacer(1, 4))
#         elements.append(Paragraph(display.body if display else f"Continuous Assessment Summary - {teacherclass.ClassName}", subheader_style))
#         elements.append(Spacer(1, 8))

#         if display and display.image:
#             try:
#                 icon = Image(display.image.path, width=2*cm, height=2*cm)
#                 icon.hAlign = 'CENTER'
#                 elements.append(icon)
#                 elements.append(Spacer(1, 0.5*cm))
#             except Exception as e:
#                 print(f"Error loading DisplayModel image: {e}")

#         if not student_data:
#             elements.append(Paragraph("No data available for this class from unchecked PDFs.", body_style))
#         else:
#             elements.append(Paragraph("Continuous Assessment Results", subheader_style))
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] +
#                            [s.nameSubject for s in subjects_db if s.nameSubject in subjects_set] +
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullName'] or '-', student['sex'] or '-', student['indexNumber'] or '-']
#                 subject_marks = {m['subject_name']: m['mark'] for m in student['marks']}
#                 for subject in subjects_db:
#                     if subject.nameSubject in subjects_set:
#                         mark = subject_marks.get(subject.nameSubject, 0)
#                         grade = next((m['grade'] for m in student['marks'] if m['subject_name'] == subject.nameSubject), '-')
#                         if mark > 0:
#                             sub_table = Table([[f"{mark:.2f}", grade]], colWidths=[10, 12], hAlign='CENTER')
#                             sub_table.setStyle(TableStyle([
#                                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                                 ('FONTSIZE', (0, 0), (-1, -1), 4),
#                                 ('LEADING', (0, 0), (-1, -1), 8),
#                                 ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                             ]))
#                             row.append(sub_table)
#                         else:
#                             row.append('-')

#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len([s for s in subjects_db if s.nameSubject in subjects_set]) +
#                           [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#             # Individual Student Reports
#             for i, student in enumerate(student_data):
#                 student_elements = []
#                 if i > 0:
#                     student_elements.append(Spacer(1, 10))
#                     student_elements.append(PageBreak())
#                 header_data = []
#                 if display and display.image:
#                     try:
#                         icon = Image(display.image.path, width=2*cm, height=2*cm)
#                         icon.drawHeight = 2*cm
#                         icon.drawWidth = 2*cm
#                         icon.hAlign = 'LEFT'
#                         header_data.append([icon, [
#                             Paragraph(display.header if display else f"CA-Based Report for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                     except Exception as e:
#                         print(f"Error loading DisplayModel image: {e}")
#                         header_data.append(['', [
#                             Paragraph(display.header if display else f"CA-Based Report for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                 else:
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"CA-Based Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])

#                 header_table = Table(header_data, colWidths=[3*cm, A4[0]-45-3*cm])
#                 header_table.setStyle(TableStyle([
#                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                     ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                     ('LEFTPADDING', (0, 0), (0, 0), 10),
#                     ('RIGHTPADDING', (1, 0), (1, 0), 10),
#                 ]))
#                 student_elements.append(header_table)
#                 student_elements.append(Spacer(1, 10))

#                 # Add Student Details
#                 student_elements.append(Paragraph(f"Student Name: {student['fullName'] or 'Unnamed Student'}", bold_style))
#                 student_elements.append(Spacer(1, 6))
#                 student_elements.append(Paragraph(f"Index Number: {student['indexNumber'] or '-'}", bold_style))
#                 student_elements.append(Spacer(1, 6))
#                 student_elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#                 student_elements.append(Spacer(1, 10))

#                 # Academic Results
#                 student_elements.append(Paragraph("Continuous Assessment Results", body_style))
#                 student_data_table = [['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']]
#                 grades_for_division = []
#                 for mark in student['marks']:
#                     remark = get_remark(mark['grade'])
#                     student_data_table.append([
#                         mark['subject_name'] or 'Unnamed',
#                         f"{mark['mark']:.2f}" if mark['mark'] > 0 else '-',
#                         mark['grade'],
#                         mark['teacher'],
#                         remark
#                     ])
#                     if not mark['is_excluded']:
#                         grades_for_division.append(mark['grade'])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '-', '-'])

#                 student_table = Table(student_data_table, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 student_elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 student_elements.append(Spacer(1, 6))
#                 student_elements.append(Paragraph(summary, body_style))
#                 student_elements.append(Spacer(1, 12))
#                 student_elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#                 elements.extend(student_elements)

#         elements.append(Spacer(1, 12))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", footer_style))
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'CA-based results report generated successfully!')
#         return response

#     return render(request, 'ca_based_result.html', context)
# User = get_user_model()

# def request_otp(request, purpose='reset'):
#     """Handle OTP request for email verification or password reset."""
#     if request.method == 'POST':
#         email = request.POST.get('email')

#         if request.user.is_authenticated:
#             user = request.user  # Use the authenticated user

#             # Check if the email is associated with another user
#             if User.objects.filter(email=email).exclude(id=user.id).exists():
#                 messages.error(request, "This email is already associated with another account.")
#                 return redirect('request_otp', purpose=purpose)

#             # If purpose is verification, check if already verified
#             if purpose == 'verification' and EmailVerificationOTP.objects.filter(user=user, is_verified=True, email=email).exists():
#                 messages.error(request, "Email already verified.")
#                 return redirect('request_otp', purpose=purpose)

#             # Update the user's email if it's different
#             if user.email != email:
#                 user.email = email
#              #   user.is_active = False   Deactivate until verified (for verification purpose)
#                 user.save()
#                 messages.info(request, "Email updated. Please verify your email.")
#         else:
#             # For unauthenticated users, check if email exists
#             try:
#                 user = User.objects.get(email=email)
#             except User.DoesNotExist:
#                 messages.error(request, "No valid account associated with this email.")
#                 return redirect('request_otp', purpose=purpose)

#         # Invalidate previous OTPs for the same user, email, and purpose
#         EmailVerificationOTP.objects.filter(
#             user=user, email=email, purpose=purpose, is_used=False
#         ).update(is_used=True)

#         # Create instance without saving to DB yet
#         otp_instance = EmailVerificationOTP(
#             user=user,
#             email=email,
#             is_used=False,
#             is_verified=False,
#             purpose=purpose
#         )
#         # Generate OTP and set expires_at before saving
#         otp_instance.generate_otp()  # This sets otp_code and expires_at, and saves
#         if otp_instance.send_otp_email():
#             messages.success(request, f"OTP sent to {email}.")
#             return redirect('verify_otp', email=email, purpose=purpose)
#         else:
#             messages.error(request, "Failed to send OTP. Try again.")

#     template = 'request_otp.html'
#     return render(request, template, {'purpose': purpose})

# def verify_otp(request, email, purpose='reset'):
#     """Verify OTP for email verification or password reset."""
#     if request.method == 'POST':
#         otp = request.POST.get('otp')
#         user = request.user
#         try:
#             otp_instance = EmailVerificationOTP.objects.get(
#                 email=email, is_used=False, purpose=purpose
#             )
#             if otp_instance.verify_otp(otp):
#                 if purpose == 'verification':
#                     # Activate user account upon verification
#                     otp_instance.user.is_active = True
#                     otp_instance.user.save()
#                     messages.success(request, "Email verified successfully.")
#                     if request.user.is_active:
#                         return redirect('teacher_profile' if user.is_teacher else 'student_profile')
#                     else:
#                         return redirect('teacher_profile' if user.is_teacher else 'student_profile')
#                 else:
#                     messages.success(request, "OTP verified. You can reset your password.")
#                     return redirect('password_reset', email=email)
#             else:
#                 messages.error(request, "Invalid or expired OTP.")
#         except ObjectDoesNotExist:
#             messages.error(request, "No valid OTP found.")
#         except EmailVerificationOTP.MultipleObjectsReturned:
#             messages.error(request, "Multiple OTPs found. Please request a new OTP.")
#             return redirect('request_otp', purpose=purpose)
#     return render(request, 'verify_otp.html', {'email': email, 'purpose': purpose})

# def password_reset(request, email):
#     """Handle password reset after OTP verification."""
#     try:
#         # Get the most recent OTP that is used (verified) but not yet marked as verified
#         otp_instance = EmailVerificationOTP.objects.filter(
#             email=email, purpose='reset', is_used=True, is_verified=False
#         ).order_by('-created_at').first()
#         if not otp_instance:
#             raise ObjectDoesNotExist
#         user = otp_instance.user
#     except ObjectDoesNotExist:
#         messages.error(request, "No valid OTP verification found. Please request a new OTP.")
#         return redirect('request_otp', purpose='reset')

#     if request.method == 'POST':
#         password = request.POST.get('password')
#         confirm_password = request.POST.get('confirm_password')
#         if password != confirm_password:
#             messages.error(request, "Passwords do not match.")
#         elif len(password) < 8:
#             messages.error(request, "Password must be at least 8 characters long.")
#         else:
#             try:
#                 user.set_password(password)
#                 user.is_active = True  # Ensure user is active after password reset
#                 user.save()
#                 otp_instance.is_verified = True
#                 otp_instance.save()
#                 messages.success(request, "Password reset successfully. You can now log in.")
#                 return redirect('login_view')
#             except Exception as e:
#                 messages.error(request, "An error occurred while resetting the password.")
#     return render(request, 'password_reset.html', {'email': email})


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import RequiredSubject, Subject
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from django.contrib import messages
# from .models import RequiredSubject, Subject
# import logging

# logger = logging.getLogger(__name__)
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.db import transaction
# from .models import RequiredSubject, Subject
# import logging

# logger = logging.getLogger(__name__)

# @login_required
# def required_subjects_view(request):
#     # Query all RequiredSubject and Subject objects for the user
#     required_subjects = RequiredSubject.objects.filter(user=request.user)
#     subjects = Subject.objects.filter(user=request.user)
    
#     if request.method == 'POST':
#         logger.debug(f"POST data: {request.POST}")
#         subject_id = request.POST.get('subject')
#         level = request.POST.get('level')
        
#         if subject_id and level in ['Olevel', 'Alevel']:
#             try:
#                 with transaction.atomic():
#                     subject = Subject.objects.get(id=subject_id, user=request.user)
#                     required_subject = RequiredSubject(user=request.user, subject=subject, level=level)
#                     required_subject.save()
#                     messages.success(request, f"Subject '{subject.nameSubject}' assigned to {level} successfully!")
#                     logger.info(f"Assigned subject {subject.nameSubject} to {level} for user {request.user.username}")
#                 return redirect('required_subjects')
#             except Subject.DoesNotExist:
#                 messages.error(request, "Selected subject does not exist or you do not have permission.")
#                 logger.error(f"Subject {subject_id} not found for user {request.user.username}")
#             except Exception as e:
#                 messages.error(request, f"Error assigning subject: {str(e)}")
#                 logger.error(f"Error assigning subject {subject_id}: {str(e)}", exc_info=True)
#         else:
#             messages.error(request, "Please select both a valid subject and level.")
#             logger.warning(f"Invalid form data: subject_id={subject_id}, level={level}")
    
#     context = {
#         'required_subjects': required_subjects,
#         'subjects': subjects,
#     }
#     return render(request, 'required_subjects.html', context)

# @login_required
# def update_required_subject(request, id):
#     required_subject = get_object_or_404(RequiredSubject, id=id, user=request.user)
#     subjects = Subject.objects.filter(user=request.user)
    
#     if request.method == 'POST':
#         logger.debug(f"POST data: {request.POST}")
#         subject_id = request.POST.get('subject')
#         level = request.POST.get('level')
        
#         if subject_id and level in ['Olevel', 'Alevel']:
#             try:
#                 with transaction.atomic():
#                     subject = Subject.objects.get(id=subject_id, user=request.user)
#                     required_subject.subject = subject
#                     required_subject.level = level
#                     required_subject.save()
#                     messages.success(request, f"Subject '{subject.nameSubject}' updated to {level} successfully!")
#                     logger.info(f"Updated subject to {subject.nameSubject} for {level} by {request.user.username}")
#                 return redirect('required_subjects')
#             except Subject.DoesNotExist:
#                 messages.error(request, "Selected subject does not exist or you do not have permission.")
#                 logger.error(f"Subject {subject_id} not found for user {request.user.username}")
#             except Exception as e:
#                 messages.error(request, f"Error updating subject: {str(e)}")
#                 logger.error(f"Error updating subject {id}: {str(e)}", exc_info=True)
#         else:
#             messages.error(request, "Please select both a valid subject and level.")
#             logger.warning(f"Invalid update data: subject_id={subject_id}, level={level}")
    
#     context = {
#         'required_subject': required_subject,
#         'subjects': subjects,
#     }
#     return render(request, 'update_required_subject.html', context)

# @login_required
# def delete_required_subject(request, id):
#     required_subject = get_object_or_404(RequiredSubject, id=id, user=request.user)
    
#     if request.method == 'POST':
#         try:
#             with transaction.atomic():
#                 subject_name = required_subject.subject.nameSubject
#                 required_subject.delete()
#                 messages.success(request, f"Subject '{subject_name}' deleted successfully!")
#                 logger.info(f"Deleted subject {subject_name} by {request.user.username}")
#             return redirect('required_subjects')
#         except Exception as e:
#             messages.error(request, f"Error deleting subject: {str(e)}")
#             logger.error(f"Error deleting subject {id}: {str(e)}", exc_info=True)
    
#     context = {
#         'required_subject': required_subject,
#     }
#     return render(request, 'delete_required_subject.html', context)

# def homepage(request):
#     return render(request,'the_british/index.html')
    
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import ExaminationName
# from .forms import ExaminationNameForm
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import ExaminationName
# from .forms import ExaminationNameForm

# @login_required
# def examination_list(request):
#     examinations = ExaminationName.objects.filter(user=request.user)
#     return render(request, 'examination_list.html', {'examinations': examinations})

# @login_required
# def examination_create(request):
#     if request.method == 'POST':
#         form = ExaminationNameForm(request.POST)
#         if form.is_valid():
#             examination = form.save(commit=False)
#             examination.user = request.user
#             examination.save()
#             messages.success(request, 'Examination created successfully!')
#             return redirect('examination_list')
#     else:
#         form = ExaminationNameForm()
#     return render(request, 'examination_form.html', {'form': form, 'title': 'Create Examination'})

# @login_required
# def examination_update(request, pk):
#     examination = get_object_or_404(ExaminationName, pk=pk, user=request.user)
#     if request.method == 'POST':
#         form = ExaminationNameForm(request.POST, instance=examination)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Examination updated successfully!')
#             return redirect('examination_list')
#     else:
#         form = ExaminationNameForm(instance=examination)
#     return render(request, 'examination_form.html', {'form': form, 'title': 'Update Examination'})

# @login_required
# def examination_delete(request, pk):
#     examination = get_object_or_404(ExaminationName, pk=pk, user=request.user)
#     if request.method == 'POST':
#         examination.delete()
#         messages.success(request, 'Examination deleted successfully!')
#         return redirect('examination_list')
#     return redirect('examination_list')
    
    
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import ExaminationName, TeacherSubject

# @login_required
# def select_examination(request, teacher_subject_id):
#     teacher_subject = get_object_or_404(TeacherSubject, id=teacher_subject_id, teacher=request.user)
#     examinations = ExaminationName.objects.filter(user=request.user)
    
#     if not examinations.exists():
#         messages.error(request, "No examination names available. Please create one first.")
#         return redirect('examination_create')
    
#     if request.method == 'POST':
#         exam_id = request.POST.get('examination_id')
#         if exam_id:
#             try:
#                 examination = ExaminationName.objects.get(id=exam_id, user=request.user)
#                 request.session['selected_examination_id'] = exam_id
#                 request.session['selected_examination_name'] = examination.exam_name
#                 return redirect('fill_marks', teacher_subject_id=teacher_subject_id)
#             except ExaminationName.DoesNotExist:
#                 messages.error(request, "Invalid examination selected.")
    
#     context = {
#         'teacher_subject': teacher_subject,
#         'examinations': examinations,
#     }
#     return render(request, 'select_examination.html', context)

# @login_required
# def change_examination(request, teacher_subject_id):
#     if 'selected_examination_id' in request.session:
#         del request.session['selected_examination_id']
#         del request.session['selected_examination_name']
#     return redirect('select_examination', teacher_subject_id=teacher_subject_id)
    

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.db.models import Sum, Avg, Q
# from django.http import JsonResponse
# from .models import TeacherClass, GradingModel, ExaminationName, Student, Subject, Mark, ExcludeSubject, RequiredSubject, SmsConfiguration, DisplayModel
# import requests
# from requests.auth import HTTPBasicAuth
# import logging
# from django.db.models import Prefetch
# from django.db.models import Q as models_Q

# logger = logging.getLogger(__name__)

# @login_required
# def all_student_marks(request, class_id=None, examination_name_id=None):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).order_by('ClassName')
#     grades = GradingModel.objects.filter(user=request.user)
#     display = DisplayModel.objects.filter(user=request.user)
#     examination_names = ExaminationName.objects.filter(user=request.user)

#     if request.method == 'POST' or class_id:
#         class_id = request.POST.get('class_id', class_id)
#         grade_id = request.POST.get('grade_id')
#         report_id = request.POST.get('report_id')
#         examination_name_id = request.POST.get('examination_id', examination_name_id)

#         if not class_id or not grade_id or not examination_name_id or not TeacherClass.objects.filter(id=class_id, user=request.user,academicclassyear__active_year=True).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists() or not ExaminationName.objects.filter(id=examination_name_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id}, Grade ID {grade_id}, or Examination ID {examination_name_id}.")
#             return render(request, 'grading_system.html', {
#                 'grades': grades,
#                 'display': display,
#                 'classes': classes,
#                 'examination_names': examination_names
#             })

#         # Store examination_name_id in session for download_pdf
#         request.session['selected_examination_id'] = examination_name_id
#         examination_name = get_object_or_404(ExaminationName, id=examination_name_id, user=request.user)
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         report_display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id and DisplayModel.objects.filter(id=report_id, user=request.user).exists() else None

#         # Determine level based on is_advance
#         level = 'Alevel' if grading_required.is_advance else 'Olevel'
        
#         # Fetch filtered subjects using RequiredSubject
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subject_ids = required_subjects.values_list('subject_id', flat=True)
#         subjects = Subject.objects.filter(id__in=subject_ids, user=request.user)

#         if not subjects.exists():
#             logger.warning(f"No subjects found for TeacherClass {teacherclass.ClassName} at level {level}")
#             messages.warning(request, f"No subjects defined for '{teacherclass.ClassName}' at {level}. Add subjects to proceed.")

#         if grading_required.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading_required.grade_a: 'A',
#                 grading_required.grade_b: 'B',
#                 grading_required.grade_c: 'C',
#                 grading_required.grade_d: 'D',
#                 grading_required.grade_e: 'E',
#                 grading_required.grade_s: 'S',
#                 grading_required.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#             min_subjects_for_division = 3
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading_required.grade_a: 'A',
#                 grading_required.grade_b: 'B',
#                 grading_required.grade_c: 'C',
#                 grading_required.grade_d: 'D',
#                 grading_required.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}
#             min_subjects_for_division = 7

#         # Filter marks by examinationname
#         mark_filter = models_Q(marks__subject__in=subjects, marks__examinationname=examination_name)
#         students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#             Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects, examinationname=examination_name).select_related('subject'))
#         )
#         if not students.exists():
#             logger.warning(f"No students found for TeacherClass {teacherclass.ClassName}")
#             messages.warning(request, f"No students enrolled in '{teacherclass.ClassName}'.")

#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination_name)),
#             average_marks=Avg('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination_name))
#         )

#         marks_evaluation_dict = {
#             s.id: {
#                 'total_marks': s.total_marks or 0,
#                 'average_marks': s.average_marks or 0
#             } for s in students_marks_evaluation
#         }

#         division_thresholds = [
#             {'max': grading_required.division_1, 'label': 'I'},
#             {'max': grading_required.division_2, 'label': 'II'},
#             {'max': grading_required.division_3, 'label': 'III'},
#             {'max': grading_required.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         student_data = []
#         for student in students:
#             student_marks = []
#             all_grades = []
#             grades_for_division = []

#             student_subjects_with_marks = Mark.objects.filter(student=student, teacherclass=teacherclass, examinationname=examination_name, subject__in=subjects).select_related('subject')
#             subject_ids_with_marks = student_subjects_with_marks.values_list('subject_id', flat=True)

#             for subject in subjects:
#                 mark_obj = student.marks.filter(subject=subject, teacherclass=teacherclass, examinationname=examination_name).first()
#                 mark_value = mark_obj.marks if mark_obj else None
#                 grade = '-'
#                 if mark_value is not None:
#                     for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                         if mark_value >= threshold:
#                             grade = letter_grade
#                             break
#                 if mark_value is not None:
#                     student_marks.append({
#                         'subject': subject.id,
#                         'subject_name': subject.nameSubject,
#                         'mark': mark_value,
#                         'grade': grade,
#                         'is_excluded': subject.id in exclude_subjects
#                     })
#                 all_grades.append(grade)
#                 if not grading_required.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             logger.debug(f"Student {student.fullName} marks: {student_marks}")

#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)

#             if num_valid_subjects < min_subjects_for_division:
#                 division = "Inc"
#                 total_points = 0
#             else:
#                 sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:min_subjects_for_division]
#                 total_points = sum(grade_points[g] for g in sorted_grades)
#                 division = 'IV'
#                 for threshold in division_thresholds:
#                     if total_points <= threshold['max']:
#                         division = threshold['label']
#                         break

#             student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#             overall_grade = 'F'
#             for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                 if student_average >= threshold:
#                     overall_grade = letter_grade
#                     break

#             has_valid_marks = any(grade != '-' for grade in all_grades)

#             student_data.append({
#                 'id': student.id,
#                 'fullName': student.fullName,
#                 'sex': student.sex,
#                 'indexNumber': student.indexNumber,
#                 'marks': student_marks,
#                 'total_marks': marks_evaluation_dict.get(student.id, {}).get('total_marks', 0),
#                 'average_marks': student_average,
#                 'grade': overall_grade,
#                 'division': division,
#                 'total_points': total_points,
#                 'has_valid_marks': has_valid_marks,
#                 'teacherclass': {
#                 'id': teacherclass.id,
#                 'ClassName': teacherclass.ClassName or "Unnamed Class"
#     }
#             })

#         student_data.sort(key=lambda x: (-x['has_valid_marks'], -x['average_marks']))
#         for position, student in enumerate(student_data, 1):
#             student['position'] = position

#         context = {
#             'students': student_data,
#             'subjects': subjects,
#             'display': [report_display] if report_display else display[:1],
#             'teacherclass': teacherclass,
#             'classes': classes,
#             'grades': grades,
#             'examination_names': examination_names,
#             'selected_examination': examination_name,
#             'grading_required': grading_required,
#             'exclude_subjects': list(exclude_subjects) if grading_required.is_advance else [],
#         }
#         logger.debug(f"Context prepared: {len(student_data)} students, {len(subjects)} subjects")
#         return render(request, 'all_student_marks.html', context)

#     return render(request, 'grading_system.html', {
#         'grades': grades,
#         'display': display,
#         'classes': classes,
#         'examination_names': examination_names,
#         'teacherclass': None  # Ensure teacherclass is None when no class is selected
#     })


# @login_required
# def filter_class_results(request):
#     if request.method != 'POST' or not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#         return JsonResponse({'error': 'Invalid request'}, status=400)

#     class_id = request.POST.get('class_id')
#     grade_id = request.POST.get('grade_id')
#     examination_id = request.POST.get('examination_id')

#     if not class_id or not grade_id or not examination_id:
#         return JsonResponse({'error': 'Class, grade, or examination not specified'}, status=400)

#     # Validate objects
#     try:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#         grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         examination = get_object_or_404(ExaminationName, id=examination_id, user=request.user)
#     except Exception as e:
#         logger.error(f"Error fetching objects: {str(e)}")
#         return JsonResponse({'error': 'Invalid class, grade, or examination'}, status=400)

#     # Determine level
#     level = 'Alevel' if grading_required.is_advance else 'Olevel'

#     # Fetch filtered subjects
#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subject_ids = required_subjects.values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=subject_ids, user=request.user)

#     if not subjects.exists():
#         logger.warning(f"No subjects found for TeacherClass {teacherclass.ClassName.class_name} at level {level}")
#         return JsonResponse({'error': f"No subjects defined for '{teacherclass.ClassName.class_name}' at {level}."}, status=400)

#     # Grading logic
#     if grading_required.is_advance:
#         exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#         grade_thresholds = {
#             grading_required.grade_a: 'A',
#             grading_required.grade_b: 'B',
#             grading_required.grade_c: 'C',
#             grading_required.grade_d: 'D',
#             grading_required.grade_e: 'E',
#             grading_required.grade_s: 'S',
#             grading_required.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         min_subjects_for_division = 3
#     else:
#         exclude_subjects = []
#         grade_thresholds = {
#             grading_required.grade_a: 'A',
#             grading_required.grade_b: 'B',
#             grading_required.grade_c: 'C',
#             grading_required.grade_d: 'D',
#             grading_required.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}
#         min_subjects_for_division = 7

#     division_thresholds = [
#         {'max': grading_required.division_1, 'label': 'I'},
#         {'max': grading_required.division_2, 'label': 'II'},
#         {'max': grading_required.division_3, 'label': 'III'},
#         {'max': grading_required.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

#     # Fetch students and marks
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects, examinationname=examination).select_related('subject'))
#     )

#     if not students.exists():
#         logger.warning(f"No students found for TeacherClass {teacherclass.ClassName.class_name}")
#         return JsonResponse({'error': f"No students enrolled in '{teacherclass.ClassName.class_name}'."}, status=400)

#     students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#         total_marks=Sum('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination)),
#         average_marks=Avg('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination))
#     )

#     marks_evaluation_dict = {
#         s.id: {
#             'total_marks': s.total_marks or 0,
#             'average_marks': s.average_marks or 0
#         } for s in students_marks_evaluation
#     }

#     # Prepare student data
#     student_data = []
#     for student in students:
#         student_marks = []
#         all_grades = []
#         grades_for_division = []

#         student_subjects_with_marks = Mark.objects.filter(
#             student=student,
#             teacherclass=teacherclass,
#             examinationname=examination,
#             subject__in=subjects
#         ).select_related('subject')

#         for subject in subjects:
#             mark_obj = student.marks.filter(subject=subject, teacherclass=teacherclass, examinationname=examination).first()
#             mark_value = mark_obj.marks if mark_obj else None
#             grade = '-'
#             if mark_value is not None:
#                 for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#                     if mark_value >= threshold:
#                         grade = letter_grade
#                         break
#                 student_marks.append({
#                     'subject': subject.id,
#                     'subject_name': subject.nameSubject,
#                     'mark': mark_value,
#                     'grade': grade,
#                     'is_excluded': subject.id in exclude_subjects
#                 })
#             all_grades.append(grade)
#             if not grading_required.is_advance or subject.id not in exclude_subjects:
#                 grades_for_division.append(grade)

#         filtered_grades = [g for g in grades_for_division if g != '-']
#         num_valid_subjects = len(filtered_grades)

#         if num_valid_subjects < min_subjects_for_division:
#             division = "Inc"
#             total_points = 0
#         else:
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:min_subjects_for_division]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break

#         student_average = marks_evaluation_dict.get(student.id, {}).get('average_marks', 0)
#         overall_grade = 'F'
#         for threshold, letter_grade in sorted(grade_thresholds.items(), reverse=True):
#             if student_average >= threshold:
#                 overall_grade = letter_grade
#                 break

#         has_valid_marks = any(grade != '-' for grade in all_grades)

#         student_data.append({
#             'id': student.id,
#             'fullName': student.fullName or 'Unnamed Student',
#             'sex': student.sex or '-',
#             'indexNumber': student.indexNumber or '-',
#             'marks': student_marks,
#             'total_marks': marks_evaluation_dict.get(student.id, {}).get('total_marks', 0),
#             'average_marks': student_average,
#             'grade': overall_grade,
#             'division': division,
#             'total_points': total_points,
#             'has_valid_marks': has_valid_marks
#         })

#     student_data.sort(key=lambda x: (-x['has_valid_marks'], -x['average_marks']))
#     for position, student in enumerate(student_data, 1):
#         student['position'] = position

#     # Prepare subjects data for JSON response
#     subjects_data = [{
#         'id': subject.id,
#         'nameSubject': subject.nameSubject or 'Unnamed Subject',
#         'is_excluded': subject.id in exclude_subjects
#     } for subject in subjects]

#     return JsonResponse({
#         'class_id': class_id,
#         'class_name': teacherclass.ClassName.class_name or 'Unnamed Class',  # Corrected to access class_name
#         'grading_level': 'A-Level' if grading_required.is_advance else 'O-Level',
#         'examination_name': examination.exam_name or 'Unnamed Examination',
#         'students': student_data,
#         'subjects': subjects_data,
#         'exclude_subjects': list(exclude_subjects),
#         'success': True
#     }, status=200)
    




# @login_required
# def fill_marks(request, teacher_subject_id):
#     # Check if an examination name is selected
#     examination_name_id = request.session.get('selected_examination_id')
#     if not examination_name_id:
#         messages.error(request, "Please select an examination first.")
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     try:
#         # Get the Teacher profile for the logged-in user
#         teacher_profile = request.user.teacher_profile.get()
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Contact your administrator.")
#         return redirect('teacher_profile')

#     try:
#         # Get the examination name using the teacher's creator
#         examination_name = ExaminationName.objects.get(
#             id=examination_name_id,
#             user=teacher_profile.created_by
#         )
#     except ExaminationName.DoesNotExist:
#         messages.error(request, "Selected examination name is invalid.")
#         if 'selected_examination_id' in request.session:
#             del request.session['selected_examination_id']
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     # Get the assignment for the logged-in teacher
#     teacher_subject = get_object_or_404(
#         TeacherSubject,
#         id=teacher_subject_id,
#         teacher=teacher_profile
#     )

#     # Get the specific TeacherClass and ensure its AcademicClassYear is active
#     current_teacher_class = teacher_subject.teacherclass
#     try:
#         academic_class_year = current_teacher_class.academicclassyear
#         if not academic_class_year.active_year:
#             messages.error(request, f"The academic year '{academic_class_year.academic_year_name}' for this class is not active.")
#             return redirect('teacher_profile')
#     except AttributeError:
#         messages.error(request, "No academic year associated with this class.")
#         return redirect('teacher_profile')

#     # Get students enrolled in this specific TeacherClass and subject via StudentSubject
#     student_subjects = StudentSubject.objects.filter(
#         teacherclass=current_teacher_class,
#         subject=teacher_subject.subject,
#         teacherclass__academicclassyear__active_year=True
#     )

#     if student_subjects.exists():
#         # Get student IDs for this specific TeacherClass
#         student_ids = set()
#         for student_subject in student_subjects:
#             student_ids.update(student_subject.student.values_list('id', flat=True))
#         students = Student.objects.filter(
#             id__in=student_ids,
#             teacherclass=current_teacher_class,
#             teacherclass__academicclassyear__active_year=True
#         ).select_related('user').order_by('fullName')
#     else:
#         students = Student.objects.none()

#     # Fetch existing marks only for the current TeacherClass, subject, and examination
#     student_marks = {
#         mark.student_id: mark.marks for mark in Mark.objects.filter(
#             teacherclass=current_teacher_class,
#             subject=teacher_subject.subject,
#             examinationname=examination_name,
#             student__in=students,
#             teacherclass__academicclassyear__active_year=True
#         )
#     }

#     # Fetch saved marks for the summary table
#     saved_marks = Mark.objects.filter(
#         teacherclass=current_teacher_class,
#         subject=teacher_subject.subject,
#         examinationname=examination_name,
#         student__in=students,
#         teacherclass__academicclassyear__active_year=True
#     ).select_related('student').order_by('student__fullName')

#     if request.method == 'POST':
#         if teacher_subject.is_restricted:
#             messages.error(request, "Marks for this subject are restricted.")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         for student in students:
#             mark_value = request.POST.get(f'marks_{student.id}')
#             if mark_value and mark_value.strip():
#                 try:
#                     mark_value = float(mark_value)
#                     if not (0 <= mark_value <= 100):
#                         raise ValueError("Marks must be between 0 and 100.")
#                     Mark.objects.update_or_create(
#                         teacherclass=current_teacher_class,
#                         subject=teacher_subject.subject,
#                         examinationname=examination_name,
#                         student=student,
#                         defaults={
#                             'marks': mark_value,
#                             'user': request.user
#                         }
#                     )
#                 except ValueError as e:
#                     messages.error(request, f"Invalid mark for {student.fullName or student.user.username}: {e}")
#                     return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         messages.success(request, f"You successfully save marks for {teacher_subject.subject.nameSubject} in {current_teacher_class.ClassName.class_name}.")
#         return redirect('teacher_profile')

#     context = {
#         'teacher_subject': teacher_subject,
#         'students': students,
#         'student_marks': student_marks,
#         'saved_marks': saved_marks,
#         'examination_name': examination_name,
#         'academic_class_year': academic_class_year,
#         'current_teacher_class': current_teacher_class,
#     }
#     return render(request, 'fill_marks.html', context)
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER, TA_LEFT
# from reportlab.lib.units import cm, inch
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from .models import TeacherClass, GradingModel, DisplayModel, ExaminationName, Student, Subject, Mark, ExcludeSubject, RequiredSubject
# from datetime import datetime
# import pandas as pd

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from reportlab.lib.units import cm, inch
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from datetime import datetime
# import pandas as pd

# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
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

# logger = logging.getLogger(__name__)


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
#         for student in student_data:
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
#                  f"Position in Class: {i}"]
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


# @login_required
# def generate_annual_final_marks(request, class_id=None, grade_id=None, examination_name_id=None):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)
#     examination_names = ExaminationName.objects.filter(user=request.user)
#     context = {
#         'classes': classes,
#         'grades': grades,
#         'examination_names': examination_names,
#     }

#     if request.method != 'POST':
#         return render(request, 'generate_annual_final_marks.html', context)

#     if not class_id or not grade_id:
#         messages.error(request, "Invalid class or grading system selection.")
#         return render(request, 'generate_annual_final_marks.html', context)

#     try:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     except:
#         messages.error(request, "Invalid class or grading system selection.")
#         return render(request, 'generate_annual_final_marks.html', context)

#     # Verify teacher authorization
#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#         creator = teacher_profile.created_by
#     except Teacher.DoesNotExist:
#         messages.error(request, "Your account is not linked to a valid teacher profile.")
#         return redirect('teacher_dashboard')

#     if not creator:
#         messages.error(request, "You are not authorized to generate reports.")
#         return redirect('teacher_dashboard')

#     examination_name = None
#     if examination_name_id:
#         examination_name = get_object_or_404(ExaminationName, id=examination_name_id, user=request.user)
#     context.update({
#         'teacherclass': teacherclass,
#         'selected_grade_id': grade_id,
#         'selected_examination': examination_name,
#     })

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subject_ids = RequiredSubject.objects.filter(user=request.user, level=level).values_list('subject_id', flat=True)
#     subjects_db = Subject.objects.filter(id__in=required_subject_ids, user=request.user)
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(teacherclass=teacherclass).select_related('subject'))
#     )
#     if not students.exists():
#         messages.error(request, f"No students found for {teacherclass.ClassName}.")
#         return render(request, 'generate_annual_final_marks.html', context)

#     exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject_id', flat=True))
#     grade_thresholds = {
#         grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#         grading.grade_d: 'D', grading.grade_f: 'F'
#     }
#     grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}
#     if grading.is_advance:
#         grade_thresholds.update({grading.grade_e: 'E', grading.grade_s: 'S'})
#         grade_points.update({'E': 5, 'S': 6, 'F': 7})
#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

#     def get_grade(mark):
#         if mark is None or mark <= 0:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_division(grades):
#         valid_grades = [g for g in grades if g != '-']
#         req_subs = 3 if grading.is_advance else 7
#         if len(valid_grades) < req_subs:
#             return "Inc", 0
#         sorted_points = sorted([grade_points[g] for g in valid_grades])[:req_subs]
#         total_points = sum(sorted_points)
#         for d in division_thresholds:
#             if total_points <= d['max']:
#                 return d['label'], total_points
#         return 'IV', total_points

#     student_data = []
#     for student in students:
#         final_marks_list = []
#         total_final_marks = 0
#         for subject in subjects_db:
#             marks_for_subject = student.marks.filter(subject=subject)
#             final_mark = 0
#             if examination_name:
#                 mark_obj = marks_for_subject.filter(examinationname=examination_name).first()
#                 final_mark = mark_obj.marks if mark_obj else 0
#             else:
#                 if marks_for_subject.exists():
#                     aggregation = marks_for_subject.aggregate(average=Avg('marks'))
#                     final_mark = aggregation['average'] or 0
#             if final_mark > 0:
#                 final_marks_list.append({
#                     'subject_name': subject.nameSubject,
#                     'mark': final_mark,
#                     'grade': get_grade(final_mark),
#                     'is_excluded': subject.id in exclude_subjects,
#                 })
#                 total_final_marks += final_mark
#         if not final_marks_list:
#             continue
#         avg_marks = total_final_marks / len(final_marks_list) if final_marks_list else 0
#         grades_for_div = [m['grade'] for m in final_marks_list if not m['is_excluded']]
#         division, total_points = get_division(grades_for_div)
#         student_data.append({
#             'id': student.id,
#             'fullName': student.fullName,
#             'sex': student.sex,
#             'indexNumber': student.indexNumber,
#             'marks': final_marks_list,
#             'total_marks': total_final_marks,
#             'average_marks': avg_marks,
#             'grade': get_grade(avg_marks),
#             'division': division,
#             'total_points': total_points,
#         })
#     student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#     for i, data in enumerate(student_data, 1):
#         data['position'] = i

#     # Generate PDF
#     response = HttpResponse(content_type='application/pdf')
#     report_type = examination_name.exam_name.replace(' ', '_') if examination_name else "AnnualReport"
#     filename = f"FinalMarks_{teacherclass.ClassName.replace(' ', '_')}_{report_type}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = TA_CENTER
#     body_style.fontSize = 7

#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     display = DisplayModel.objects.filter(user=request.user).first()
#     header_text = display.header if display else f"Final Marks Report for {teacherclass.ClassName}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(display.body if display else f"Academic Summary - {teacherclass.ClassName}", subheader_style))
#     elements.append(Spacer(1, 8))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.5*cm))
#         except Exception as e:
#             print(f"Error loading DisplayModel image: {e}")

#     if not student_data:
#         elements.append(Paragraph("No data available to generate a report.", body_style))
#     else:
#         elements.append(Paragraph("Academic Results", subheader_style))
#         header = ['Pos', 'Student Name', 'Index No.'] + [s.nameSubject for s in subjects_db] + ['Total', 'Avg', 'Grade', 'Div', 'Pts']
#         table_data = [header]
#         for student in student_data:
#             row = [student['position'], student['fullName'], student['indexNumber']]
#             marks_map = {m['subject_name']: f"{m['mark']:.1f}" for m in student['marks']}
#             for s in subjects_db:
#                 row.append(marks_map.get(s.nameSubject, '-'))
#             row.extend([
#                 f"{student['total_marks']:.2f}",
#                 f"{student['average_marks']:.2f}",
#                 student['grade'],
#                 student['division'],
#                 student['total_points'] or '-',
#             ])
#             table_data.append(row)

#         available_width = A4[0] - 30
#         num_subjects = len(subjects_db)
#         fixed_col_widths = {'pos': 25, 'name': 95, 'index': 60, 'total': 38, 'avg': 38, 'grade': 32, 'div': 25, 'pts': 25}
#         total_fixed_width = sum(fixed_col_widths.values())
#         subject_col_width = (available_width - total_fixed_width) / num_subjects if num_subjects > 0 else 0
#         col_widths = ([fixed_col_widths['pos'], fixed_col_widths['name'], fixed_col_widths['index']] +
#                       [subject_col_width] * num_subjects +
#                       [fixed_col_widths['total'], fixed_col_widths['avg'], fixed_col_widths['grade'], fixed_col_widths['div'], fixed_col_widths['pts']])

#         summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#         summary_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTSIZE', (0, 0), (-1, -1), 7),
#         ]))
#         elements.append(summary_table)
#         elements.append(Spacer(1, 10))

#         # Individual Student Reports
#         for student in student_data:
#             elements.append(PageBreak())
#             header_data = []
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=2*cm, height=2*cm)
#                     icon.drawHeight = 2*cm
#                     icon.drawWidth = 2*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     print(f"Error loading DisplayModel image: {e}")
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

#             # Add Student Name, Index Number, and Class Name as Centered Paragraphs
#             elements.append(Paragraph(f"Student Name: {student['fullName'] or 'Unnamed Student'}", bold_style))
#             elements.append(Spacer(1, 6))
#             elements.append(Paragraph(f"Index Number: {student['indexNumber'] or '-'}", bold_style))
#             elements.append(Spacer(1, 6))
#             elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#             elements.append(Spacer(1, 10))

#             # Academic Results
#             elements.append(Paragraph("Academic Performance", body_style))
#             marks_header = ['Subject', 'Final Mark', 'Grade', 'Remarks']
#             marks_table_data = [marks_header]
#             for mark_info in student['marks']:
#                 marks_table_data.append([mark_info['subject_name'], f"{mark_info['mark']:.2f}", mark_info['grade'], ''])
#             marks_table = Table(marks_table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 2.5*inch], repeatRows=1)
#             marks_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ]))
#             elements.append(marks_table)
#             elements.append(Spacer(1, 24))
#             summary_data = [
#                 [f"Total Marks: {student['total_marks']:.2f}", f"Average: {student['average_marks']:.2f}", f"Overall Grade: {student['grade']}"],
#                 [f"Division: {student['division']}", f"Total Points: {student['total_points'] if student['total_points'] > 0 else '-'}", f"Position in Class: {student['position']}"]
#             ]
#             summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
#             summary_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
#             ]))
#             elements.append(summary_table)
#             elements.append(Spacer(1, 10))

#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#     messages.success(request, 'Annual final marks report generated successfully!')
#     return response

# @login_required
# def merge_term_marks_pdfs(request, class_id=None):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user,academicclassyear__active_year=True).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         # Determine level based on is_advance
#         level = 'Alevel' if grading.is_advance else 'Olevel'
        
#         # Fetch filtered subjects using RequiredSubject
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subject_ids = required_subjects.values_list('subject_id', flat=True)
#         subjects_db = Subject.objects.filter(id__in=subject_ids, user=request.user)
#         subjects_db_dict = {s.nameSubject.lower(): s for s in subjects_db}

#         pdf_uploads = TermMarksUpload.objects.filter(
#             user=request.user, 
#             teacherclass=teacherclass,
#             for_merging_pdf=True
#         )
#         if not pdf_uploads.exists():
#             messages.error(request, "No PDFs selected for merging.")
#             logger.error(f"No TermMarksUpload objects marked for merging found for user {request.user} and class {teacherclass}.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         if grading.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         all_data = []
#         subjects_set = set()
#         student_data_dict = {}

#         for upload in pdf_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file not found at {pdf_path}.")
#                 logger.error(f"PDF not found: {pdf_path}")
#                 continue
                
#             try:
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in PDF at {pdf_path}.")
#                     logger.error(f"No tables in PDF: {pdf_path}")
#                     continue

#                 pdf_dfs = []
#                 for i, df in enumerate(dfs):
#                     df = df.dropna(how='all')
#                     if df.empty:
#                         logger.warning(f"Table {i} in PDF {pdf_path} is empty after dropping NA.")
#                         continue
#                     df.columns = df.columns.str.strip().str.lower()
#                     df = df.rename(columns={'s/no': 's_no', 'student name': 'fullname', 'sex': 'sex', 'index no': 'indexnumber'})
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Columns: {list(df.columns)}")
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Number of students: {len(df)}")
#                     pdf_dfs.append(df)

#                 if not pdf_dfs:
#                     messages.error(request, f"No valid tables found in PDF at {pdf_path}.")
#                     logger.error(f"No valid tables in PDF: {pdf_path}")
#                     continue

#                 df = pd.concat(pdf_dfs, ignore_index=True)
#                 logger.debug(f"PDF {pdf_path} - Total students after concatenation: {len(df)}")
#                 subjects_set.update([col for col in df.columns if col not in ['s_no', 'fullname', 'sex', 'indexnumber', 'total', 'avg', 'grade', 'pos', 'div', 'pts']])
#                 all_data.append(df)

#             except Exception as e:
#                 messages.error(request, f"Error processing PDF at {pdf_path}: {str(e)}")
#                 logger.error(f"Error processing PDF {pdf_path}: {str(e)}", exc_info=True)
#                 continue

#         subjects_set = {s for s in subjects_set if s.lower() in subjects_db_dict}  # Filter subjects_set
#         if not all_data:
#             messages.error(request, "No valid data extracted from selected PDFs.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         def get_grade(mark):
#             if mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         for df in all_data:
#             logger.debug(f"Processing DataFrame with {len(df)} students")
#             for _, row in df.iterrows():
#                 indexnumber = str(row['indexnumber']).strip()
#                 if indexnumber.lower() == 'nan' or not indexnumber:
#                     logger.warning(f"Skipping row with invalid indexnumber: {row.to_dict()}")
#                     continue

#                 if indexnumber not in student_data_dict:
#                     student_data_dict[indexnumber] = {
#                         'fullname': row['fullname'],
#                         'sex': row['sex'],
#                         'indexnumber': indexnumber,
#                         'marks': {},
#                         'total_marks': 0,
#                         'subject_count': 0
#                     }

#                 student = student_data_dict[indexnumber]
                
#                 for subj_name, subject in subjects_db_dict.items():
#                     if subj_name in df.columns:
#                         mark_raw = str(row[subj_name]).strip()
#                         logger.debug(f"Student {row['indexnumber']} - Raw mark for {subj_name}: {mark_raw}")
#                         if mark_raw in ['-', ''] or pd.isna(mark_raw):
#                             mark = 0
#                             grade = '-'
#                         else:
#                             mark_match = re.match(r'(\d+\.?\d*)\s*([A-FS-])?', mark_raw)
#                             if mark_match:
#                                 mark = float(mark_match.group(1)) if mark_match.group(1) else 0
#                                 grade = mark_match.group(2) if mark_match.group(2) else get_grade(mark)
#                                 logger.debug(f"Student {row['indexnumber']} - Parsed mark for {subj_name}: {mark}, Grade: {grade}")
#                             else:
#                                 mark = 0
#                                 grade = '-'
#                                 logger.debug(f"Student {row['indexnumber']} - Failed to parse mark for {subj_name}: {mark_raw}")

#                         if subject.id not in student['marks']:
#                             student['marks'][subject.id] = {
#                                 'subject_id': subject.id,
#                                 'subject_name': subject.nameSubject,
#                                 'mark': mark,
#                                 'grade': grade,
#                                 'is_excluded': subject.id in exclude_subjects,
#                                 'count': 1
#                             }
#                         else:
#                             existing = student['marks'][subject.id]
#                             if mark > 0:
#                                 existing['mark'] = (existing['mark'] * existing['count'] + mark) / (existing['count'] + 1)
#                                 existing['grade'] = get_grade(existing['mark'])
#                                 existing['count'] += 1
#                             else:
#                                 existing['grade'] = '-' if existing['mark'] == 0 else get_grade(existing['mark'])

#         logger.debug(f"Total unique students after processing all PDFs: {len(student_data_dict)}")

#         student_data = []
#         for student in student_data_dict.values():
#             total_marks = 0
#             subject_count = 0
#             marks_list = []
            
#             for mark_info in student['marks'].values():
#                 marks_list.append(mark_info)
#                 if mark_info['mark'] > 0:
#                     total_marks += mark_info['mark']
#                     subject_count += 1

#             student['marks'] = marks_list
#             student['total_marks'] = total_marks
#             student['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student['grade'] = get_grade(student['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student['division'] = division
#             student['total_points'] = total_points
            
#             student_data.append(student)

#         logger.debug(f"Total students in final student_data: {len(student_data)}")

#         student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         response = HttpResponse(content_type='application/pdf')
#         filename = f"merged_pdfs_{teacherclass.ClassName}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style = styles['Heading1']
#         subheader_style = styles['Heading2']
#         body_style = styles['BodyText']
#         header_style.alignment = 1
#         subheader_style.alignment = 1
#         body_style.alignment = 1
#         body_style.fontSize = 7

#         elements.append(Paragraph(f"Merged PDFs for {teacherclass.ClassName}", header_style))
#         elements.append(Spacer(1, 8))

#         if not student_data:
#             elements.append(Paragraph("No data available to merge.", body_style))
#         else:
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                            [s.nameSubject for s in subjects_db] + 
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]
            
#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullname'] or '-', student['sex'] or '-', student['indexnumber'] or '-']
#                 for subject in subjects_db:
#                     mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                     if mark_info:
#                         mark_display = f"{mark_info['mark']:.2f}" if mark_info['mark'] > 0 else '-'
#                         grade_display = mark_info['grade']
#                         sub_table = Table([[mark_display, grade_display]],
#                                         colWidths=[10, 12], hAlign='CENTER')
#                         sub_table.setStyle(TableStyle([
#                             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                             ('FONTSIZE', (0, 0), (-1, -1), 4),
#                             ('LEADING', (0, 0), (-1, -1), 8),
#                             ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                         ]))
#                         row.append(sub_table)
#                     else:
#                         row.append('-')
                
#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len(subjects_db) + [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#             # Individual student reports
#             for i, student in enumerate(student_data):
#                 if i > 0:
#                     elements.append(PageBreak())
                
#                 elements.append(Paragraph(f"Student: {student['fullname'] or 'Unnamed Student'}", subheader_style))
#                 elements.append(Spacer(1, 6))

#                 student_data_table = [['Subject', 'Marks', 'Grade', 'Teacher', 'Signature', 'Status']]
#                 grades_for_division = []

#                 for mark in student['marks']:
#                     if mark['mark'] > 0:
#                         student_data_table.append([
#                             mark['subject_name'] or 'Unnamed',
#                             f"{mark['mark']:.2f}",
#                             mark['grade'],
#                             '',  # Placeholder for Teacher
#                             '',  # Placeholder for Signature
#                             ''   # Placeholder for Status
#                         ])
#                         if not mark['is_excluded']:
#                             grades_for_division.append(mark['grade'])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '', '', ''])

#                 student_table = Table(student_data_table, colWidths=[120, 40, 40, 60, 60, 60], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(summary, body_style))

#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", body_style))
#         doc.build(elements)
#         return response

#     if class_id:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         context['teacherclass'] = teacherclass
#         context['uploads'] = TermMarksUpload.objects.filter(teacherclass=teacherclass, user=request.user)

#     return render(request, 'upload_term_marks.html', context)


# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .models import TermMarksUpload

# @login_required
# def update_merge_selection(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             upload_id = data.get('upload_id')
#             for_merging_pdf = data.get('for_merging_pdf')
            
#             # Ensure the upload belongs to the user
#             upload = get_object_or_404(TermMarksUpload, id=upload_id, user=request.user)
#             upload.for_merging_pdf = for_merging_pdf
#             upload.save()
            
#             return JsonResponse({'success': True})
#         except Exception as e:
#             logger.error(f"Error updating merge selection: {str(e)}")
#             return JsonResponse({'success': False, 'error': str(e)}, status=400)
#     return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

    
    
# @login_required
# def subject_grade_distribution(request):
#     # Initial data for the selection form
#     grades = GradingModel.objects.filter(user=request.user)
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     examinations = ExaminationName.objects.filter(user=request.user)
#     context = {'grades': grades, 'classes': classes, 'examinations': examinations}

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')
#         examination_id = request.POST.get('examination_id')

#         # --- Input Validation ---
#         if not all([class_id, grade_id, examination_id]):
#             messages.error(request, "You must select a class, a grading system, and an examination.")
#             return render(request, 'select_grade_distribution.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading_required = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         examination = get_object_or_404(ExaminationName, id=examination_id, user=request.user)

#         # --- Grade Setup ---
#         if grading_required.is_advance:
#             grade_thresholds = {
#                 'A': grading_required.grade_a, 'B': grading_required.grade_b, 'C': grading_required.grade_c,
#                 'D': grading_required.grade_d, 'E': grading_required.grade_e, 'S': grading_required.grade_s,
#                 'F': grading_required.grade_f
#             }
#             level = 'A-Level'
#         else:
#             grade_thresholds = {
#                 'A': grading_required.grade_a, 'B': grading_required.grade_b, 'C': grading_required.grade_c,
#                 'D': grading_required.grade_d, 'F': grading_required.grade_f
#             }
#             level = 'O-Level'
        
#         sorted_grades = sorted(grade_thresholds.items(), key=lambda item: item[1], reverse=True)
#         grade_list = [grade[0] for grade in sorted_grades]

#         # --- **CORRECTED** Data Fetching and Processing ---
        
#         # 1. Get all marks for the selected class and examination. This is our single source of truth.
#         marks_in_class = Mark.objects.filter(teacherclass=teacherclass, examinationname=examination)

#         if not marks_in_class.exists():
#             messages.warning(request, f"No marks have been registered for the class '{teacherclass.ClassName}' in the examination '{examination.exam_name}'.")
#             context.update({'selected_class': teacherclass, 'selected_examination': examination})
#             return render(request, 'select_grade_distribution.html', context)

#         # 2. Get the actual subjects taught in this class by looking at the marks.
#         subject_ids = marks_in_class.values_list('subject_id', flat=True).distinct()
#         subjects = Subject.objects.filter(id__in=subject_ids)

#         # 3. Calculate Grade Distribution (Efficiently)
#         subject_grade_counts = []
#         for subject in subjects:
#             # Filter from the already fetched marks, no new DB query
#             subject_marks = marks_in_class.filter(subject=subject)
#             total_students = subject_marks.count()
            
#             grade_count = {'subject': subject.nameSubject or "Unnamed Subject", 'total_students': total_students}
#             for grade in grade_list:
#                 grade_count[grade] = 0

#             # Loop through marks in memory, not in the database
#             for mark in subject_marks:
#                 for grade_letter, min_score in sorted_grades:
#                     if mark.marks >= min_score:
#                         grade_count[grade_letter] += 1
#                         break # Grade assigned, move to next mark
            
#             subject_grade_counts.append(grade_count)

#         # 4. Calculate Summary
#         total_distinct_students = marks_in_class.values('student').distinct().count()
#         summary_grade_counts = {'subject': f'Summary for {teacherclass.ClassName}', 'total_students': total_distinct_students}
#         for grade in grade_list:
#             # Sum the counts already calculated above
#             summary_grade_counts[grade] = sum(s.get(grade, 0) for s in subject_grade_counts)
            
#         # --- Prepare final context for rendering the results ---
#         context.update({
#             'subject_grade_counts': subject_grade_counts,
#             'summary_grade_counts': summary_grade_counts,
#             'grade_list': grade_list,
#             'grading_system': grading_required,
#             'selected_class': teacherclass,
#             'selected_examination': examination,
#             'level': level
#         })
        
#         return render(request, 'subject_grade_distribution.html', context)

#     # Render the initial selection form
#     return render(request, 'select_grade_distribution.html', context)

# @login_required
# def download_grade_distribution_pdf(request, class_id, grade_id, examination_id):
#     """
#     Generates and downloads a PDF file showing the grade distribution for a specific class and examination.
#     """
#     # 1. Fetch primary objects safely
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     examination = get_object_or_404(ExaminationName, id=examination_id, user=request.user)

#     # 2. Define grade thresholds based on the grading model
#     if grading.is_advance:
#         grade_thresholds = {
#             'A': grading.grade_a, 'B': grading.grade_b, 'C': grading.grade_c,
#             'D': grading.grade_d, 'E': grading.grade_e, 'S': grading.grade_s,
#             'F': grading.grade_f
#         }
#         level = 'A-Level'
#     else:
#         grade_thresholds = {
#             'A': grading.grade_a, 'B': grading.grade_b, 'C': grading.grade_c,
#             'D': grading.grade_d, 'F': grading.grade_f
#         }
#         level = 'O-Level'

#     # Sort thresholds from highest to lowest score for correct grade assignment
#     sorted_grades = sorted(grade_thresholds.items(), key=lambda item: item[1], reverse=True)
#     grade_list = [grade[0] for grade in sorted_grades]

#     # 3. **Correctly fetch subjects and marks for the given class and examination**
#     marks_in_class = Mark.objects.filter(teacherclass=teacherclass, examinationname=examination)

#     # Get the list of subjects that have marks recorded in this class
#     subject_ids = marks_in_class.values_list('subject_id', flat=True).distinct()
#     subjects = Subject.objects.filter(id__in=subject_ids)

#     # 4. Calculate grade distribution for each subject
#     subject_grade_counts = []
#     for subject in subjects:
#         subject_marks = marks_in_class.filter(subject=subject)
#         total_students = subject_marks.count()

#         if total_students > 0:
#             grade_count = {'subject': subject.nameSubject or "Unnamed Subject", 'total_students': total_students}
#             for grade in grade_list:
#                 grade_count[grade] = 0

#             for mark in subject_marks:
#                 for grade_letter, min_score in sorted_grades:
#                     if mark.marks >= min_score:
#                         grade_count[grade_letter] += 1
#                         break

#             subject_grade_counts.append(grade_count)

#     # 5. Prepare data for the PDF table
#     table_data = [['Subject'] + grade_list + ['Total Students']]
#     for data in subject_grade_counts:
#         row = [data['subject']] + [data.get(grade, 0) for grade in grade_list] + [data['total_students']]
#         table_data.append(row)

#     # 6. Create a summary row for all subjects combined
#     total_students_in_class = marks_in_class.values('student').distinct().count()
#     if total_students_in_class > 0:
#         summary_row = [f'Summary for {teacherclass.ClassName}']
#         for grade in grade_list:
#             total_grade = sum(s.get(grade, 0) for s in subject_grade_counts)
#             summary_row.append(total_grade)
#         summary_row.append(total_students_in_class)
#         table_data.append(summary_row)

#     # 7. Build the PDF document
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="grade_distribution_{teacherclass.ClassName}_{examination.exam_name}.pdf"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()

#     # Header
#     elements.append(Paragraph(f"Grade Distribution for {teacherclass.ClassName} ({level})", styles['Heading1']))
#     elements.append(Paragraph(f"Examination: {examination.exam_name}", styles['Heading2']))
#     elements.append(Paragraph(f"Using Grading System: {grading}", styles['Heading3']))
#     elements.append(Spacer(1, 12))

#     # Table
#     if table_data:
#         available_width = A4[0] - 30
#         col_widths = [available_width * 0.3] + [available_width * 0.5 / len(grade_list)] * len(grade_list) + [available_width * 0.2]
#         table = Table(table_data, colWidths=col_widths)
        
#         table_style = TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ])
        
#         if total_students_in_class > 0:
#             table_style.add('BACKGROUND', (0, -1), (-1, -1), colors.lightblue)
#             table_style.add('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')

#         table.setStyle(table_style)
#         elements.append(table)

#     # Footer
#     elements.append(Spacer(1, 24))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))

#     doc.build(elements)
#     return response
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.enums import TA_CENTER  # Import TA_CENTER for alignment
# from reportlab.graphics.shapes import Drawing
# from reportlab.graphics.charts.barcharts import VerticalBarChart
# from reportlab.graphics.charts.textlabels import Label
# from datetime import datetime

# from .models import GradingModel, ExaminationName, TeacherClass, Teacher, Subject, Mark, RequiredSubject


# @login_required
# def download_top_ten_subjects_pdf(request, grade_id, examination_id, class_id):
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     examination = get_object_or_404(ExaminationName, id=examination_id, user=request.user)
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#     level = 'Alevel' if grading.is_advance else 'Olevel'

#     def determine_grade(mark, grading_system):
#         if grading_system.is_advance:
#             if mark >= grading_system.grade_a: return 'A'
#             elif mark >= grading_system.grade_b: return 'B'
#             elif mark >= grading_system.grade_c: return 'C'
#             elif mark >= grading_system.grade_d: return 'D'
#             elif mark >= grading_system.grade_e: return 'E'
#             elif mark >= grading_system.grade_s: return 'S'
#             else: return 'F'
#         else:
#             if mark >= grading_system.grade_a: return 'A'
#             elif mark >= grading_system.grade_b: return 'B'
#             elif mark >= grading_system.grade_c: return 'C'
#             elif mark >= grading_system.grade_d: return 'D'
#             else: return 'F'

#     grade_points = {
#         'A': 1.0, 'B': 2.0, 'C': 3.0, 'D': 4.0,
#         **({'E': 5.0, 'S': 6.0, 'F': 7.0} if grading.is_advance else {'F': 5.0})
#     }

#     subordinate_teacher_user_ids = Teacher.objects.filter(created_by=request.user).values_list('user_id', flat=True)
#     all_user_ids = list(subordinate_teacher_user_ids) + [request.user.id]

#     subjects_data = []

#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subjects = Subject.objects.filter(id__in=required_subjects.values('subject_id'), user=request.user)

#     for subject in subjects:
#         marks = Mark.objects.filter(
#             subject=subject,
#             user_id__in=all_user_ids,
#             teacherclass=teacherclass,
#             examinationname=examination
#         )

#         if marks.exists():
#             total_points = sum(grade_points.get(determine_grade(mark.marks, grading), 0) for mark in marks)
#             student_count = marks.count()
#             gpa = round(total_points / student_count, 2) if student_count > 0 else 0.00

#             # Convert GPA to percentage
#             min_gp = min(grade_points.values())
#             max_gp = max(grade_points.values())
#             gpa_percentage = round(((max_gp - gpa) / (max_gp - min_gp)) * 100, 2) if max_gp != min_gp else 0.00

#             # The 'pass_percentage' calculation has been removed.
#             subjects_data.append({
#                 'subject': subject,
#                 'gpa': gpa,
#                 'gpa_percentage': gpa_percentage
#             })

#     sorted_subjects = sorted(subjects_data, key=lambda x: x['gpa'])[:10]

#     # Create PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="top_subjects_{teacherclass.ClassName}_{examination.exam_name}.pdf"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()

#     # --- MODIFICATION: Center the title style ---
#     title_style = styles['Title']
#     title_style.alignment = TA_CENTER

#     # Header
#     elements.append(Paragraph(f"Top 10 Subjects Performance ({level})", title_style))
#     elements.append(Paragraph(f"Class: {teacherclass.ClassName or 'Unnamed Class'}", styles['Normal']))
#     elements.append(Paragraph(f"Examination: {examination.exam_name}", styles['Normal']))
#     elements.append(Spacer(1, 12))

#     # Table
#     if sorted_subjects:
#         # --- MODIFICATION: Removed 'Pass %' from the header ---
#         table_data = [["Rank", "Subject", "GPA", "GPA %"]]
#         for i, data in enumerate(sorted_subjects, 1):
#             # --- MODIFICATION: Removed pass percentage from the data row ---
#             row = [
#                 str(i),
#                 data['subject'].nameSubject or "Unnamed",
#                 f"{data['gpa']:.2f}",
#                 f"{data['gpa_percentage']:.2f}%"
#             ]
#             table_data.append(row)

#         # --- MODIFICATION: Adjusted column widths for 4 columns ---
#         table = Table(table_data, colWidths=[40, 180, 80, 80])
#         table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 1, colors.black),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
#             ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ]))
#         elements.append(table)
#         elements.append(Spacer(1, 24))

#         # Chart Drawing
#         drawing = Drawing(400, 200)
#         chart = VerticalBarChart()
#         chart.x = 50
#         chart.y = 30
#         chart.height = 150
#         chart.width = 300

#         chart.data = [[data['gpa_percentage'] for data in sorted_subjects]]
        
#         # Using a simplified name for chart labels to prevent overflow
#         chart.categoryAxis.categoryNames = [
#             (s['subject'].nameSubject[:10] + '..') if len(s['subject'].nameSubject) > 12 else s['subject'].nameSubject 
#             for s in sorted_subjects
#         ]
#         chart.categoryAxis.labels.boxAnchor = 'n' # Anchor labels to the top

#         chart.bars[0].fillColor = colors.green
#         chart.valueAxis.valueMin = 0
#         chart.valueAxis.valueMax = 100
#         chart.valueAxis.valueStep = 10

#         label = Label()
#         label.setOrigin(200, 180)
#         label.boxAnchor = 'n'
#         label.setText("Performance Score (%) per Subject")
#         drawing.add(chart)
#         drawing.add(label)
#         elements.append(drawing)

#     else:
#         elements.append(Paragraph("No subject performance data found.", styles['Normal']))

#     elements.append(Spacer(1, 12))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
#     doc.build(elements)
#     return response
    

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.contrib import messages
# from django.db.models import Avg
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from .models import Teacher, TeacherClass, ExaminationName, Mark, DisplayModel, RequiredSubject
# import logging
# from datetime import datetime
# import os

# logger = logging.getLogger(__name__)

# @login_required
# def top_and_bottom_students(request):
#     """
#     Displays the top and bottom 10 students, either for a selected class or for all classes
#     managed by the user and their subordinates, with actual class positions, based on RequiredSubject.
#     """
#     current_user = request.user

#     # Fetch all relevant user IDs
#     subordinate_user_ids = Teacher.objects.filter(created_by=current_user).values_list('user_id', flat=True)
#     all_user_ids = list(subordinate_user_ids) + [current_user.id]

#     # Fetch classes, examinations, and display model
#     teacher_classes = TeacherClass.objects.filter(user_id__in=all_user_ids, academicclassyear__active_year=True)
#     examinations = ExaminationName.objects.filter(user_id__in=all_user_ids)
#     display = DisplayModel.objects.filter(user=current_user).first()

#     # Get required subjects for the current user
#     required_subjects = RequiredSubject.objects.filter(user=current_user)
#     required_subject_ids = required_subjects.values_list('subject__id', flat=True)

#     # Get user selections from query parameters
#     selected_class_id = request.GET.get('class_id')
#     selected_exam_id = request.GET.get('examination_id')

#     context = {
#         'teacher_classes': teacher_classes,
#         'examinations': examinations,
#         'selected_class': None,
#         'selected_examination': None,
#         'top_students': [],
#         'bottom_students': [],
#         'class_data': {},
#         'display': display,
#         'no_subjects_configured': False,
#     }

#     # Check if required subjects exist
#     if not required_subjects:
#         context['no_subjects_configured'] = True
#         logger.info(f"No required subjects configured for user {current_user.username}")
#         return render(request, 'top_bottom_students.html', context)

#     # Base query for marks, filtered by required subjects
#     marks_query = Mark.objects.filter(
#         user_id__in=all_user_ids,
#         subject__id__in=required_subject_ids
#     ).select_related('student', 'teacherclass', 'examinationname')

#     # Apply examination filter if selected
#     if selected_exam_id:
#         marks_query = marks_query.filter(examinationname_id=selected_exam_id)
#         context['selected_examination'] = examinations.filter(id=selected_exam_id).first()

#     if selected_class_id:
#         # Single Class View
#         selected_class = teacher_classes.filter(id=selected_class_id).first()
#         context['selected_class'] = selected_class
        
#         if selected_class:
#             class_marks = marks_query.filter(teacherclass=selected_class)
            
#             # Calculate average marks for each student and sort by average
#             student_averages = class_marks.values(
#                 'student__id',
#                 'student__fullName',
#                 'student__sex',
#                 'student__indexNumber'
#             ).annotate(
#                 avg_mark=Avg('marks')
#             ).order_by('-avg_mark')

#             # Assign actual positions
#             ranked_students = []
#             for position, student in enumerate(student_averages, 1):
#                 ranked_students.append({
#                     'position': position,
#                     'student__id': student['student__id'],
#                     'student__fullName': student['student__fullName'],
#                     'student__sex': student['student__sex'],
#                     'student__indexNumber': student['student__indexNumber'],
#                     'avg_mark': student['avg_mark']
#                 })

#             context['top_students'] = ranked_students[:10]
#             # Bottom students: Take last 10, sort by avg_mark descending to have lowest at the top
#             context['bottom_students'] = sorted(ranked_students[-10:], key=lambda x: x['avg_mark'], reverse=True)
#             logger.debug(f"Processed {len(ranked_students)} students for class {selected_class.ClassName}")
#     else:
#         # All Classes View
#         class_data = {}
#         for teacher_class in teacher_classes:
#             class_marks = marks_query.filter(teacherclass=teacher_class)
            
#             student_averages = class_marks.values(
#                 'student__id',
#                 'student__fullName',
#                 'student__sex',
#                 'student__indexNumber'
#             ).annotate(
#                 avg_mark=Avg('marks')
#             ).order_by('-avg_mark')

#             ranked_students = []
#             for position, student in enumerate(student_averages, 1):
#                 ranked_students.append({
#                     'position': position,
#                     'student__id': student['student__id'],
#                     'student__fullName': student['student__fullName'],
#                     'student__sex': student['student__sex'],
#                     'student__indexNumber': student['student__indexNumber'],
#                     'avg_mark': student['avg_mark']
#                 })

#             top = ranked_students[:10]
#             bottom = sorted(ranked_students[-10:], key=lambda x: x['avg_mark'], reverse=True)
            
#             if top or bottom:
#                 class_data[teacher_class] = {
#                     'top_students': top,
#                     'bottom_students': bottom
#                 }
#                 logger.debug(f"Processed {len(ranked_students)} students for class {teacher_class.ClassName}")
#         context['class_data'] = class_data
        
#     return render(request, 'top_bottom_students.html', context)

# @login_required
# def download_top_and_bottom_students_pdf(request, class_id=None, examination_id=None):
#     current_user = request.user

#     # Fetch all relevant user IDs
#     subordinate_user_ids = Teacher.objects.filter(created_by=current_user).values_list('user_id', flat=True)
#     all_user_ids = list(subordinate_user_ids) + [current_user.id]

#     # Fetch DisplayModel for header and styling
#     display = DisplayModel.objects.filter(user=current_user).first()

#     # Fetch required subjects for the current user
#     required_subjects = RequiredSubject.objects.filter(user=current_user)
#     required_subject_ids = required_subjects.values_list('subject__id', flat=True)

#     # Set up PDF response
#     response = HttpResponse(content_type='application/pdf')
#     filename = "top_and_bottom_students_report.pdf"
#     if class_id and examination_id:
#         selected_class = get_object_or_404(TeacherClass, id=class_id, user_id__in=all_user_ids, academicclassyear__active_year=True)
#         examination = get_object_or_404(ExaminationName, id=examination_id, user_id__in=all_user_ids)
#         filename = f"top_bottom_{selected_class.ClassName or 'Unnamed_Class'}_{examination.exam_name.replace(' ', '_')}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'

#     # Set up styles
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#     body_style.fontSize = 7

#     # Define header elements
#     def create_header_table():
#         header_data = []
#         header_text = display.header if display else "Top and Bottom Students Report"
#         if class_id and examination_id:
#             header_text = display.header if display else f"Top and Bottom Students for {selected_class.ClassName or 'Unnamed Class'} - {examination.exam_name}"
#         if display and display.image:
#             try:
#                 image_path = display.image.path
#                 if os.path.exists(image_path):
#                     logger.debug(f"Loading image from: {image_path}")
#                     icon = Image(image_path, width=2*cm, height=2*cm)
#                     icon.drawHeight = 2*cm
#                     icon.drawWidth = 2*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([
#                         icon,
#                         [
#                             Paragraph(header_text, header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Academic Summary - {datetime.now().year}", subheader_style)
#                         ]
#                     ])
#                 else:
#                     logger.error(f"Image file does not exist: {image_path}")
#                     header_data.append([
#                         Paragraph("Image not found", body_style),
#                         [
#                             Paragraph(header_text, header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Academic Summary - {datetime.now().year}", subheader_style)
#                         ]
#                     ])
#             except Exception as e:
#                 logger.error(f"Error loading DisplayModel image: {str(e)}")
#                 header_data.append([
#                     Paragraph(f"Error loading image: {str(e)}", body_style),
#                     [
#                         Paragraph(header_text, header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Academic Summary - {datetime.now().year}", subheader_style)
#                     ]
#                 ])
#         else:
#             header_data.append([
#                 '',
#                 [
#                     Paragraph(header_text, header_style),
#                     Spacer(1, 4),
#                     Paragraph(display.body if display else f"Academic Summary - {datetime.now().year}", subheader_style)
#                 ]
#             ])

#         header_table = Table(header_data, colWidths=[3*cm, A4[0]-45-3*cm])
#         header_table.setStyle(TableStyle([
#             ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#             ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#             ('LEFTPADDING', (0, 0), (0, 0), 10),
#             ('RIGHTPADDING', (1, 0), (1, 0), 10),
#         ]))
#         return header_table

#     # Define page number function
#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     # Set up document
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []

#     # Check if required subjects exist
#     if not required_subjects:
#         logger.info(f"No required subjects configured for user {current_user.username}")
#         elements.append(create_header_table())
#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph("No subject Configured", body_style))
#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         return response

#     # Base query for marks, filtered by required subjects
#     marks_query = Mark.objects.filter(
#         user_id__in=all_user_ids,
#         subject__id__in=required_subject_ids
#     ).select_related('student', 'teacherclass', 'examinationname')

#     if examination_id:
#         marks_query = marks_query.filter(examinationname_id=examination_id)

#     if class_id:
#         # Single class PDF
#         selected_class = get_object_or_404(TeacherClass, id=class_id, user_id__in=all_user_ids, academicclassyear__active_year=True)
#         class_marks = marks_query.filter(teacherclass=selected_class)
#         student_averages = class_marks.values(
#             'student__id',
#             'student__fullName',
#             'student__sex',
#             'student__indexNumber'
#         ).annotate(
#             avg_mark=Avg('marks')
#         ).order_by('-avg_mark')

#         # Assign actual positions
#         ranked_students = []
#         for position, student in enumerate(student_averages, 1):
#             ranked_students.append({
#                 'position': position,
#                 'student__id': student['student__id'],
#                 'student__fullName': student['student__fullName'],
#                 'student__sex': student['student__sex'],
#                 'student__indexNumber': student['student__indexNumber'],
#                 'avg_mark': student['avg_mark']
#             })

#         top_students = ranked_students[:10]
#         bottom_students = sorted(ranked_students[-10:], key=lambda x: x['avg_mark'], reverse=True)

#         elements.append(create_header_table())
#         elements.append(Spacer(1, 10))
#         if not top_students and not bottom_students:
#             elements.append(Paragraph("No subject Configured or no data available for this class.", body_style))
#         else:
#             elements.append(Paragraph(f"Class: {selected_class.ClassName or 'Unnamed Class'}", subheader_style))
#             elements.append(Spacer(1, 10))

#             # Top Students Table
#             if top_students:
#                 elements.append(Paragraph("Top 10 Students", body_style))
#                 header = ['Position', 'Student Name', 'Sex', 'Index No.', 'Average Mark']
#                 table_data = [header]
#                 for student in top_students:
#                     avg_mark = student['avg_mark']
#                     table_data.append([
#                         str(student['position']),
#                         student['student__fullName'] or 'Unnamed',
#                         student['student__sex'] or '-',
#                         str(student['student__indexNumber']) or '-',
#                         f"{avg_mark:.2f}" if avg_mark is not None else '-'
#                     ])

#                 available_width = A4[0] - 30
#                 col_widths = [available_width * 0.1, available_width * 0.35, available_width * 0.1, available_width * 0.3, available_width * 0.15]
#                 top_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#                 top_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 7),
#                 ]))
#                 elements.append(KeepTogether(top_table))
#                 elements.append(Spacer(1, 10))

#             # Bottom Students Table
#             if bottom_students:
#                 elements.append(Paragraph("Bottom 10 Students", body_style))
#                 header = ['Position', 'Student Name', 'Sex', 'Index No.', 'Average Mark']
#                 table_data = [header]
#                 for student in bottom_students:
#                     avg_mark = student['avg_mark']
#                     table_data.append([
#                         str(student['position']),
#                         student['student__fullName'] or 'Unnamed',
#                         student['student__sex'] or '-',
#                         str(student['student__indexNumber']) or '-',
#                         f"{avg_mark:.2f}" if avg_mark is not None else '-'
#                     ])

#                 bottom_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#                 bottom_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 7),
#                 ]))
#                 elements.append(KeepTogether(bottom_table))
#                 elements.append(Spacer(1, 10))
#     else:
#         # All classes PDF
#         teacher_classes = TeacherClass.objects.filter(user_id__in=all_user_ids, academicclassyear__active_year=True).order_by('ClassName')
#         has_data = False
#         for teacher_class in teacher_classes:
#             class_marks = marks_query.filter(teacherclass=teacher_class)
#             student_averages = class_marks.values(
#                 'student__id',
#                 'student__fullName',
#                 'student__sex',
#                 'student__indexNumber'
#             ).annotate(
#                 avg_mark=Avg('marks')
#             ).order_by('-avg_mark')

#             ranked_students = []
#             for position, student in enumerate(student_averages, 1):
#                 ranked_students.append({
#                     'position': position,
#                     'student__id': student['student__id'],
#                     'student__fullName': student['student__fullName'],
#                     'student__sex': student['student__sex'],
#                     'student__indexNumber': student['student__indexNumber'],
#                     'avg_mark': student['avg_mark']
#                 })

#             top_students = ranked_students[:10]
#             bottom_students = sorted(ranked_students[-10:], key=lambda x: x['avg_mark'], reverse=True)

#             if top_students or bottom_students:
#                 has_data = True
#                 elements.append(PageBreak())
#                 elements.append(create_header_table())
#                 elements.append(Spacer(1, 10))
#                 elements.append(Paragraph(f"Class: {teacher_class.ClassName or 'Unnamed Class'}", subheader_style))
#                 elements.append(Spacer(1, 10))

#                 # Top Students Table
#                 if top_students:
#                     elements.append(Paragraph("Top 10 Students", body_style))
#                     header = ['Position', 'Student Name', 'Sex', 'Index No.', 'Average Mark']
#                     table_data = [header]
#                     for student in top_students:
#                         avg_mark = student['avg_mark']
#                         table_data.append([
#                             str(student['position']),
#                             student['student__fullName'] or 'Unnamed',
#                             student['student__sex'] or '-',
#                             str(student['student__indexNumber']) or '-',
#                             f"{avg_mark:.2f}" if avg_mark is not None else '-'
#                         ])

#                     available_width = A4[0] - 30
#                     col_widths = [available_width * 0.1, available_width * 0.35, available_width * 0.1, available_width * 0.3, available_width * 0.15]
#                     top_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#                     top_table.setStyle(TableStyle([
#                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTSIZE', (0, 0), (-1, -1), 7),
#                     ]))
#                     elements.append(KeepTogether(top_table))
#                     elements.append(Spacer(1, 10))

#                 # Bottom Students Table
#                 if bottom_students:
#                     elements.append(Paragraph("Bottom 10 Students", body_style))
#                     header = ['Position', 'Student Name', 'Sex', 'Index No.', 'Average Mark']
#                     table_data = [header]
#                     for student in bottom_students:
#                         avg_mark = student['avg_mark']
#                         table_data.append([
#                             str(student['position']),
#                             student['student__fullName'] or 'Unnamed',
#                             student['student__sex'] or '-',
#                             str(student['student__indexNumber']) or '-',
#                             f"{avg_mark:.2f}" if avg_mark is not None else '-'
#                         ])

#                     bottom_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#                     bottom_table.setStyle(TableStyle([
#                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTSIZE', (0, 0), (-1, -1), 7),
#                     ]))
#                     elements.append(KeepTogether(bottom_table))
#                     elements.append(Spacer(1, 10))

#         if not has_data:
#             elements.append(create_header_table())
#             elements.append(Spacer(1, 10))
#             elements.append(Paragraph("No subject Configured or no data available for any classes.", body_style))

#     elements.append(Spacer(1, 10))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#     return response
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import render, get_object_or_404
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageTemplate, Frame
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import render, get_object_or_404
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from django.db.models import Avg
# from .models import Teacher, TeacherClass, ExaminationName, Mark, Student, DisplayModel
# import datetime
# import os
# import logging

# def dash(request):
#     return render(request,'dashboard/index.html')



# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import cm
# from reportlab.lib.enums import TA_CENTER
# from decimal import Decimal
# from datetime import datetime
# import json

# from finance.models import Fee





# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import cm
# from decimal import Decimal
# from datetime import datetime
# import json
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect
# from django.http import HttpResponse
# from django.contrib import messages
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
# from reportlab.lib import colors
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.units import cm
# from reportlab.lib.enums import TA_CENTER
# from decimal import Decimal
# from datetime import datetime



# @login_required
# def ca_based_result_with_financial(request, class_id=None, grade_id=None):
#     # Prefetch related data
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True).prefetch_related('student_set')
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user,academicclassyear__active_year=True).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'ca_based_result.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         # Verify teacher authorization
#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by
#         except Teacher.DoesNotExist:
#             messages.error(request, "Your account is not linked to a valid teacher profile.")
#             return redirect('teacher_dashboard')

#         if not creator:
#             messages.error(request, "You are not authorized to generate reports.")
#             return redirect('teacher_dashboard')

#         # Determine level
#         level = 'Alevel' if grading.is_advance else 'Olevel'
        
#         # Fetch required subjects
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subject_ids = required_subjects.values_list('subject_id', flat=True)
#         subjects_db = Subject.objects.filter(id__in=subject_ids, user=request.user)
#         subjects_map = {s.nameSubject: s for s in subjects_db}

#         # Grading setup
#         if grading.is_advance:
#             exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True))
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_e: 'E', grading.grade_s: 'S',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = set()
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         # Fetch term uploads
#         term_uploads = TermMarksUpload.objects.filter(
#             user=request.user,
#             teacherclass=teacherclass,
#             for_merging_pdf=False
#         ).select_related('teacherclass')
#         if not term_uploads.exists():
#             messages.error(request, "No unchecked term marks PDFs available for generating CA-based results.")
#             return render(request, 'ca_based_result.html', context)

#         # Process PDFs
#         term_data = {}
#         subjects_set = set()
#         for upload in term_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file for {upload.term_name} not found at {pdf_path}.")
#                 return render(request, 'ca_based_result.html', context)

#             try:
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, stream=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in {upload.term_name} PDF.")
#                     return render(request, 'ca_based_result.html', context)

#                 df = pd.concat([df.dropna(how='all') for df in dfs], ignore_index=True)
#                 df.columns = df.columns.str.strip()
#                 if all(col not in df.columns for col in ['S/No', 'Student Name', 'Sex', 'Index No']):
#                     messages.error(request, f"Missing required headers in {upload.term_name} PDF.")
#                     return render(request, 'ca_based_result.html', context)

#                 df = df.rename(columns={'S/No': 'S/No', 'Student Name': 'fullName', 'Sex': 'sex', 'Index No': 'indexNumber'})
#                 term_data[upload.term_name] = df
#                 excluded_cols = ['S/No', 'fullName', 'sex', 'indexNumber', 'Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']
#                 subjects_set.update([col for col in df.columns if col not in excluded_cols and col in subjects_map])
#             except Exception as e:
#                 messages.error(request, f"Error processing PDF for {upload.term_name}: {str(e)}.")
#                 return render(request, 'ca_based_result.html', context)

#         students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#             Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects_db).select_related('subject', 'user'))
#         )
#         student_data = []

#         def get_grade(mark):
#             if pd.isna(mark) or mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_remark(grade):
#             remark_map = {
#                 'A': 'Excellent',
#                 'B': 'Very Good',
#                 'C': 'Good',
#                 'D': 'Pass',
#                 'E': 'Poor',
#                 'S': 'Subsidiary',
#                 'F': 'Fail',
#                 '-': '-'
#             }
#             return remark_map.get(grade, '-')

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         # Process students
#         for student in students:
#             student_dict = {'id': student.id, 'fullName': student.fullName, 'sex': student.sex, 'indexNumber': student.indexNumber}
#             marks_list = []
#             total_marks = 0
#             subject_count = 0

#             for subject_name in subjects_set:
#                 if subject_name not in subjects_map:
#                     continue
#                 subject = subjects_map[subject_name]
#                 marks = []
#                 for term_name, term_df in term_data.items():
#                     student_row = term_df[term_df['indexNumber'] == str(student.indexNumber)]
#                     if not student_row.empty and subject_name in student_row.columns:
#                         mark = student_row[subject_name].iloc[0]
#                         try:
#                             if isinstance(mark, str):
#                                 numeric_part = re.search(r'^\d+\.?\d*', mark)
#                                 mark = float(numeric_part.group()) if numeric_part else 0
#                             else:
#                                 mark = float(mark) if pd.notna(mark) else 0
#                             marks.append(mark)
#                         except:
#                             marks.append(0)
#                     else:
#                         marks.append(0)

#                 annual_mark = sum(marks)
#                 if annual_mark > 0:
#                     grade = get_grade(annual_mark)
#                     # Fetch teacher name from Mark model
#                     mark_obj = student.marks.filter(subject=subject).first()
#                     teacher_name = mark_obj.user.teacher_profile.first().teacherName or mark_obj.user.username if mark_obj and mark_obj.user else '-'
#                     marks_list.append({
#                         'subject_id': subject.id,
#                         'subject_name': subject_name,
#                         'mark': annual_mark,
#                         'grade': grade,
#                         'teacher': teacher_name,
#                         'is_excluded': subject.id in exclude_subjects
#                     })
#                     total_marks += annual_mark
#                     subject_count += 1

#             student_dict['marks'] = marks_list
#             student_dict['total_marks'] = total_marks
#             student_dict['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student_dict['grade'] = get_grade(student_dict['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student_dict['division'] = division
#             student_dict['total_points'] = total_points

#             student_data.append(student_dict)

#         student_data.sort(key=lambda x: x['total_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         # Generate PDF
#         response = HttpResponse(content_type='application/pdf')
#         filename = f"CABasedResultsFinancial_{teacherclass.ClassName.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style = styles['Heading1']
#         subheader_style = styles['Heading2']
#         body_style = styles['BodyText']
#         footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#         bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#         discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=10, textColor=colors.red, spaceAfter=6)
#         header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#         body_style.fontSize = 7

#         def add_page_number(canvas, doc):
#             page_num = canvas.getPageNumber()
#             text = f"Page {page_num}"
#             canvas.saveState()
#             canvas.setFont("Helvetica", 8)
#             canvas.setFillColor(colors.grey)
#             canvas.drawCentredString(A4[0]/2, 15, text)
#             canvas.restoreState()

#         display = DisplayModel.objects.filter(user=request.user).first()
#         header_text = display.header if display else f"CA-Based Results and Financial Report for {teacherclass.ClassName}"
#         elements.append(Paragraph(header_text, header_style))
#         elements.append(Spacer(1, 4))
#         elements.append(Paragraph(display.body if display else f"Continuous Assessment Summary - {teacherclass.ClassName}", subheader_style))
#         elements.append(Spacer(1, 8))

#         if display and display.image:
#             try:
#                 icon = Image(display.image.path, width=2*cm, height=2*cm)
#                 icon.hAlign = 'CENTER'
#                 elements.append(icon)
#                 elements.append(Spacer(1, 0.5*cm))
#             except Exception as e:
#                 print(f"Error loading DisplayModel image: {e}")

#         if not student_data:
#             elements.append(Paragraph("No data available for this class from unchecked PDFs.", body_style))
#         else:
#             elements.append(Paragraph("Continuous Assessment and Final Result Examination", subheader_style))
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] +
#                            [s.nameSubject for s in subjects_db if s.nameSubject in subjects_set] +
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullName'] or '-', student['sex'] or '-', student['indexNumber'] or '-']
#                 subject_marks = {m['subject_name']: m['mark'] for m in student['marks']}
#                 for subject in subjects_db:
#                     if subject.nameSubject in subjects_set:
#                         mark = subject_marks.get(subject.nameSubject, 0)
#                         grade = next((m['grade'] for m in student['marks'] if m['subject_name'] == subject.nameSubject), '-')
#                         if mark > 0:
#                             sub_table = Table([[f"{mark:.2f}", grade]], colWidths=[10, 12], hAlign='CENTER')
#                             sub_table.setStyle(TableStyle([
#                                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                                 ('FONTSIZE', (0, 0), (-1, -1), 4),
#                                 ('LEADING', (0, 0), (-1, -1), 8),
#                                 ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                             ]))
#                             row.append(sub_table)
#                         else:
#                             row.append('-')

#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len([s for s in subjects_db if s.nameSubject in subjects_set]) +
#                           [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#             # Individual Student Reports
#             for student in student_data:
#                 elements.append(PageBreak())
#                 header_data = []
#                 if display and display.image:
#                     try:
#                         icon = Image(display.image.path, width=2*cm, height=2*cm)
#                         icon.drawHeight = 2*cm
#                         icon.drawWidth = 2*cm
#                         icon.hAlign = 'LEFT'
#                         header_data.append([icon, [
#                             Paragraph(display.header if display else f"CA-Based Report for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                     except Exception as e:
#                         print(f"Error loading DisplayModel image: {e}")
#                         header_data.append(['', [
#                             Paragraph(display.header if display else f"CA-Based Report for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                 else:
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"CA-Based Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])

#                 header_table = Table(header_data, colWidths=[3*cm, A4[0]-45-3*cm])
#                 header_table.setStyle(TableStyle([
#                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                     ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                     ('LEFTPADDING', (0, 0), (0, 0), 10),
#                     ('RIGHTPADDING', (1, 0), (1, 0), 10),
#                 ]))
#                 elements.append(header_table)
#                 elements.append(Spacer(1, 10))

#                 # Add Student Name and Index Number as Centered Paragraphs
#                 elements.append(Paragraph(f"Student Name: {student['fullName'] or 'Unnamed Student'}", bold_style))
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(f"Index Number: {student['indexNumber'] or '-'}", bold_style))
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#                 elements.append(Spacer(1, 10))

#                 # Academic Results
#                 elements.append(Paragraph("Final Academic Results", body_style))
#                 student_data_table = [['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']]
#                 grades_for_division = []
#                 for mark in student['marks']:
#                     remark = get_remark(mark['grade'])
#                     student_data_table.append([
#                         mark['subject_name'] or 'Unnamed',
#                         f"{mark['mark']:.2f}" if mark['mark'] > 0 else '-',
#                         mark['grade'],
#                         mark['teacher'],
#                         remark
#                     ])
#                     if not mark['is_excluded']:
#                         grades_for_division.append(mark['grade'])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '-', '-'])

#                 student_table = Table(student_data_table, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(summary, body_style))
#                 elements.append(Spacer(1, 10))

#                 # Fee Report
#                 elements.append(Paragraph("Fee Report", body_style))
#                 student_obj = Student.objects.get(id=student['id'])
#                 student_fees = StudentFee.objects.filter(student=student_obj, teacherclass=teacherclass).select_related('fee')
#                 if not student_fees.exists():
#                     elements.append(Paragraph("No fees assigned.", body_style))
#                 else:
#                     table_data = [['Fee Name', 'Required', 'Paid', 'Balance']]
#                     total_required = Decimal('0.00')
#                     total_paid_all = Decimal('0.00')
#                     total_discounted = Decimal('0.00')

#                     for sf in student_fees:
#                         fee = sf.fee
#                         discount = Discount.objects.filter(student=student_obj, fee=fee, user=creator).first()
#                         discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                         adjusted_required = fee.amount - discount_amount
#                         total_discounted += discount_amount
#                         total_paid_result = PayFee.objects.filter(student=student_obj, fee=fee).aggregate(total=Sum('amount_paid'))
#                         total_paid = total_paid_result['total'] if total_paid_result['total'] is not None else Decimal('0.00')
#                         balance = adjusted_required - total_paid
#                         total_required += adjusted_required
#                         total_paid_all += total_paid
#                         fee_display = f"{fee.fee_name} (Discounted: {discount_amount:.2f})" if discount else fee.fee_name
#                         table_data.append([
#                             Paragraph(fee_display, body_style),
#                             Paragraph(f"{adjusted_required:.2f}", body_style),
#                             Paragraph(f"{total_paid:.2f}", body_style),
#                             Paragraph(f"{balance:.2f}", body_style)
#                         ])

#                     table_data.append([
#                         Paragraph('TOTAL', bold_style),
#                         Paragraph(f"{total_required:.2f}", bold_style),
#                         Paragraph(f"{total_paid_all:.2f}", bold_style),
#                         Paragraph(f"{total_required - total_paid_all:.2f}", bold_style)
#                     ])

#                     page_width = A4[0] - 30
#                     col_widths = [0.40 * page_width, 0.20 * page_width, 0.20 * page_width, 0.20 * page_width]
#                     table = Table(table_data, colWidths=col_widths)
#                     table.setStyle(TableStyle([
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                         ('FONTSIZE', (0, 0), (-1, 0), 10),
#                         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                         ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                         ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                         ('FONTSIZE', (0, 1), (-1, -1), 9),
#                         ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                         ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                     ]))
#                     elements.append(table)
#                     if total_discounted > 0:
#                         elements.append(Paragraph(f"Total Discount Applied: {total_discounted:.2f}", discount_style))

#                 elements.append(Spacer(1, 12))
#                 elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", footer_style))
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'CA-based results with financial report generated successfully!')
#         return response

#     return render(request, 'ca_based_result.html', context)
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib import messages
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from reportlab.lib.units import cm
# from django.db.models import Sum, Avg
# from django.db.models import Prefetch
# from decimal import Decimal
# from datetime import datetime
# import pandas as pd

# @login_required
# def generate_annual_final_marks_with_financial(request, class_id=None, grade_id=None, examination_name_id=None):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)
#     examination_names = ExaminationName.objects.filter(user=request.user)
#     context = {
#         'classes': classes, 'grades': grades, 'examination_names': examination_names,
#     }
#     if request.method != 'POST':
#         return render(request, 'generate_annual_final_marks.html', context)

#     class_id = request.POST.get('class_id', class_id)
#     grade_id = request.POST.get('grade_id', grade_id)
#     examination_name_id = request.POST.get('examination_name_id', examination_name_id)

#     try:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     except:
#         messages.error(request, "Invalid class or grading system selection.")
#         return render(request, 'generate_annual_final_marks.html', context)

#     # Verify teacher authorization
#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#         creator = teacher_profile.created_by
#     except Teacher.DoesNotExist:
#         messages.error(request, "Your account is not linked to a valid teacher profile.")
#         return redirect('teacher_dashboard')

#     if not creator:
#         messages.error(request, "You are not authorized to generate reports.")
#         return redirect('teacher_dashboard')

#     examination_name = None
#     if examination_name_id:
#         examination_name = get_object_or_404(ExaminationName, id=examination_name_id, user=request.user)
#     context.update({
#         'teacherclass': teacherclass, 'selected_grade_id': grade_id, 'selected_examination': examination_name,
#     })

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subject_ids = RequiredSubject.objects.filter(user=request.user, level=level).values_list('subject_id', flat=True)
#     subjects_db = Subject.objects.filter(id__in=required_subject_ids, user=request.user)
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(teacherclass=teacherclass).select_related('subject', 'user'))
#     )
#     if not students.exists():
#         messages.error(request, f"No students found for {teacherclass.ClassName}.")
#         return render(request, 'generate_annual_final_marks.html', context)

#     exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject_id', flat=True))
#     grade_thresholds = {
#         grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#         grading.grade_d: 'D', grading.grade_f: 'F'
#     }
#     grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}
#     if grading.is_advance:
#         grade_thresholds.update({grading.grade_e: 'E', grading.grade_s: 'S'})
#         grade_points.update({'E': 5, 'S': 6, 'F': 7})
#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'}, {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'}, {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

#     def get_grade(mark):
#         if pd.isna(mark) or mark is None or mark <= 0:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_division(grades):
#         valid_grades = [g for g in grades if g != '-']
#         req_subs = 3 if grading.is_advance else 7
#         if len(valid_grades) < req_subs:
#             return "Inc", 0
#         sorted_points = sorted([grade_points[g] for g in valid_grades])[:req_subs]
#         total_points = sum(sorted_points)
#         if total_points > grading.division_4:
#             return '0', total_points
#         for d in division_thresholds:
#             if total_points <= d['max']:
#                 return d['label'], total_points
#         return 'IV', total_points

#     student_data = []
#     for student in students:
#         final_marks_list = []
#         total_final_marks = 0
#         for subject in subjects_db:
#             marks_for_subject = student.marks.filter(subject=subject)
#             final_mark = 0
#             if examination_name:
#                 mark_obj = marks_for_subject.filter(examinationname=examination_name).first()
#                 final_mark = mark_obj.marks if mark_obj else 0
#             else:
#                 if marks_for_subject.exists():
#                     aggregation = marks_for_subject.aggregate(average=Avg('marks'))
#                     final_mark = aggregation['average'] or 0
#             if final_mark > 0:
#                 teacher_name = mark_obj.user.teacher_profile.first().teacherName or mark_obj.user.username if mark_obj and mark_obj.user else '-'
#                 final_marks_list.append({
#                     'subject_name': subject.nameSubject, 'mark': final_mark,
#                     'grade': get_grade(final_mark), 'teacher': teacher_name,
#                     'is_excluded': subject.id in exclude_subjects,
#                 })
#                 total_final_marks += final_mark
#         if not final_marks_list:
#             continue
#         avg_marks = total_final_marks / len(final_marks_list) if final_marks_list else 0
#         grades_for_div = [m['grade'] for m in final_marks_list if not m['is_excluded']]
#         division, total_points = get_division(grades_for_div)
#         student_data.append({
#             'id': student.id,
#             'fullName': student.fullName, 'sex': student.sex, 'indexNumber': student.indexNumber,
#             'marks': final_marks_list, 'total_marks': total_final_marks,
#             'average_marks': avg_marks, 'grade': get_grade(avg_marks),
#             'division': division, 'total_points': total_points,
#         })
#     student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#     for i, data in enumerate(student_data, 1):
#         data['position'] = i

#     # Generate PDF
#     response = HttpResponse(content_type='application/pdf')
#     report_type = examination_name.exam_name.replace(' ', '_') if examination_name else "AnnualReport"
#     filename = f"FinalMarksFinancial_{teacherclass.ClassName.replace(' ', '_')}_{report_type}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#     discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=10, textColor=colors.red, spaceAfter=6)
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

#     display = DisplayModel.objects.filter(user=request.user).first()
#     header_text = display.header if display else f"Final Marks and Financial Report for {teacherclass.ClassName}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(display.body if display else f"Academic and Financial Summary - {teacherclass.ClassName}", subheader_style))
#     elements.append(Spacer(1, 8))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.5*cm))
#         except Exception as e:
#             print(f"Error loading DisplayModel image: {e}")

#     if not student_data:
#         elements.append(Paragraph("No data available to generate a report.", body_style))
#     else:
#         elements.append(Paragraph("Academic Results", subheader_style))
#         header = ['Pos', 'Student Name', 'Index No.'] + [s.nameSubject for s in subjects_db] + ['Total', 'Avg', 'Grade', 'Div', 'Pts']
#         table_data = [header]
#         for student in student_data:
#             row = [student['position'], student['fullName'], student['indexNumber']]
#             marks_map = {m['subject_name']: f"{m['mark']:.1f}" for m in student['marks']}
#             for s in subjects_db:
#                 row.append(marks_map.get(s.nameSubject, '-'))
#             row.extend([
#                 f"{student['total_marks']:.2f}", f"{student['average_marks']:.2f}",
#                 student['grade'], student['division'], student['total_points'] or '-',
#             ])
#             table_data.append(row)

#         available_width = A4[0] - 30
#         num_subjects = len(subjects_db)
#         fixed_col_widths = {'pos': 25, 'name': 95, 'index': 60, 'total': 38, 'avg': 38, 'grade': 32, 'div': 25, 'pts': 25}
#         total_fixed_width = sum(fixed_col_widths.values())
#         subject_col_width = (available_width - total_fixed_width) / num_subjects if num_subjects > 0 else 0
#         col_widths = ([fixed_col_widths['pos'], fixed_col_widths['name'], fixed_col_widths['index']] +
#                       [subject_col_width] * num_subjects +
#                       [fixed_col_widths['total'], fixed_col_widths['avg'], fixed_col_widths['grade'], fixed_col_widths['div'], fixed_col_widths['pts']])

#         summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#         summary_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTSIZE', (0, 0), (-1, -1), 7),
#         ]))
#         elements.append(summary_table)
#         elements.append(Spacer(1, 10))

#         # Individual Student Reports
#         for i, student in enumerate(student_data):
#             student_elements = []
#             if i > 0:
#                 student_elements.append(Spacer(1, 10))
#                 student_elements.append(PageBreak())
#             header_data = []
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=2*cm, height=2*cm)
#                     icon.drawHeight = 2*cm
#                     icon.drawWidth = 2*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     print(f"Error loading DisplayModel image: {e}")
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
#             student_elements.append(header_table)
#             student_elements.append(Spacer(1, 10))

#             # Add Student Details
#             student_elements.append(Paragraph(f"Student Name: {student['fullName'] or 'Unnamed Student'}", bold_style))
#             student_elements.append(Spacer(1, 6))
#             student_elements.append(Paragraph(f"Index Number: {student['indexNumber'] or '-'}", bold_style))
#             student_elements.append(Spacer(1, 6))
#             student_elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#             student_elements.append(Spacer(1, 10))

#             # Academic Results
#             student_elements.append(Paragraph("Academic Performance", body_style))
#             marks_header = ['Subject', 'Final Mark', 'Grade', 'Teacher', 'Remarks']
#             marks_table_data = [marks_header]
#             for mark_info in student['marks']:
#                 marks_table_data.append([
#                     mark_info['subject_name'],
#                     f"{mark_info['mark']:.2f}",
#                     mark_info['grade'],
#                     mark_info['teacher'],
#                     '-'
#                 ])
#             marks_table = Table(marks_table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], repeatRows=1)
#             marks_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#             ]))
#             student_elements.append(marks_table)
#             student_elements.append(Spacer(1, 6))
#             summary_data = [
#                 [f"Total Marks: {student['total_marks']:.2f}", f"Average: {student['average_marks']:.2f}", f"Overall Grade: {student['grade']}"],
#                 [f"Division: {student['division']}", f"Total Points: {student['total_points'] if student['total_points'] > 0 else '-'}", f"Position in Class: {student['position']}"]
#             ]
#             summary_table = Table(summary_data, colWidths=[2.5*inch, 2.5*inch, 2*inch])
#             summary_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
#                 ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                 ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
#             ]))
#             student_elements.append(summary_table)
#             student_elements.append(Spacer(1, 10))

#             # Fee Report
#             student_elements.append(Paragraph("Fee Report", body_style))
#             student_obj = Student.objects.get(id=student['id'])
#             student_fees = StudentFee.objects.filter(student=student_obj, teacherclass=teacherclass).select_related('fee')
#             if not student_fees.exists():
#                 student_elements.append(Paragraph("No fees assigned.", body_style))
#             else:
#                 table_data = [['Fee Name', 'Required', 'Paid', 'Balance']]
#                 total_required = Decimal('0.00')
#                 total_paid_all = Decimal('0.00')
#                 total_discounted = Decimal('0.00')

#                 for sf in student_fees:
#                     fee = sf.fee
#                     discount = Discount.objects.filter(student=student_obj, fee=fee, user=creator).first()
#                     discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                     adjusted_required = fee.amount - discount_amount
#                     total_discounted += discount_amount
#                     total_paid_result = PayFee.objects.filter(student=student_obj, fee=fee).aggregate(total=Sum('amount_paid'))
#                     total_paid = total_paid_result['total'] if total_paid_result['total'] is not None else Decimal('0.00')
#                     balance = adjusted_required - total_paid
#                     total_required += adjusted_required
#                     total_paid_all += total_paid
#                     fee_display = f"{fee.fee_name} (Discounted: {discount_amount:.2f})" if discount else fee.fee_name
#                     table_data.append([
#                         Paragraph(fee_display, body_style),
#                         Paragraph(f"{adjusted_required:.2f}", body_style),
#                         Paragraph(f"{total_paid:.2f}", body_style),
#                         Paragraph(f"{balance:.2f}", body_style)
#                     ])

#                 table_data.append([
#                     Paragraph('TOTAL', bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_paid_all:.2f}", bold_style),
#                     Paragraph(f"{total_required - total_paid_all:.2f}", bold_style)
#                 ])

#                 page_width = A4[0] - 30
#                 col_widths = [0.40 * page_width, 0.20 * page_width, 0.20 * page_width, 0.20 * page_width]
#                 table = Table(table_data, colWidths=col_widths)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 10),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                     ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                     ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('FONTSIZE', (0, 1), (-1, -1), 9),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(table)
#                 if total_discounted > 0:
#                     student_elements.append(Paragraph(f"Total Discount Applied: {total_discounted:.2f}", discount_style))

#             student_elements.append(Spacer(1, 12))
#             student_elements.append(Paragraph("Principal's Signature: _____________________", bold_style))
#             elements.extend(student_elements)

#     elements.append(Spacer(1, 12))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#     messages.success(request, 'Annual final marks with financial report generated successfully!')
#     return response



# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib import messages
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from reportlab.lib.units import cm, inch
# from django.db.models import Sum
# from datetime import datetime
# from decimal import Decimal
# import os
# import tabula
# import pandas as pd
# import re
# import logging

# logger = logging.getLogger(__name__)

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.contrib import messages
# from .models import TeacherClass, GradingModel, RequiredSubject, Subject, TermMarksUpload, Student, ExcludeSubject, DisplayModel, Mark, TeacherSubject
# import tabula
# import pandas as pd
# import re
# import os
# from datetime import datetime
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import logging
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.contrib import messages
# from .models import TeacherClass, GradingModel, RequiredSubject, Subject, TermMarksUpload, Student, ExcludeSubject, DisplayModel, Mark, TeacherSubject, ExaminationName
# import tabula
# import pandas as pd
# import re
# import os
# from datetime import datetime
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import logging

# logger = logging.getLogger(__name__)

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.contrib import messages
# from .models import TeacherClass, GradingModel, RequiredSubject, Subject, TermMarksUpload, Student, ExcludeSubject, DisplayModel, Mark, TeacherSubject, ExaminationName
# import tabula
# import pandas as pd
# import re
# import os
# from datetime import datetime
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import logging

# logger = logging.getLogger(__name__)
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.contrib import messages
# from .models import TeacherClass, GradingModel, RequiredSubject, Subject, TermMarksUpload, Student, ExcludeSubject, DisplayModel, Mark, ExaminationName
# import tabula
# import pandas as pd
# import re
# import os
# from datetime import datetime
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import logging

# logger = logging.getLogger(__name__)

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from django.contrib import messages
# from .models import TeacherClass, GradingModel, RequiredSubject, Subject, TermMarksUpload, Student, ExcludeSubject, DisplayModel, Mark, ExaminationName
# import tabula
# import pandas as pd
# import re
# import os
# from datetime import datetime
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import logging

# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import tabula
# import pandas as pd
# import os
# import re
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import tabula
# import pandas as pd
# import os
# import re
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import tabula
# import pandas as pd
# import os
# import re
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# from django.contrib import messages
# from django.shortcuts import render, get_object_or_404
# from django.http import HttpResponse
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# import tabula
# import pandas as pd
# import os
# import re
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# @login_required
# def merge_term_marks_pdfs(request, class_id=None):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user,academicclassyear__active_year=True).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user,academicclassyear__active_year=True)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         level = 'Alevel' if grading.is_advance else 'Olevel'
        
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subject_ids = required_subjects.values_list('subject_id', flat=True)
#         subjects_db = Subject.objects.filter(id__in=subject_ids, user=request.user)
#         subjects_db_dict = {s.nameSubject.lower(): s for s in subjects_db}

#         pdf_uploads = TermMarksUpload.objects.filter(
#             user=request.user, 
#             teacherclass=teacherclass,
#             for_merging_pdf=True
#         )
#         if not pdf_uploads.exists():
#             messages.error(request, "No PDFs selected for merging.")
#             logger.error(f"No TermMarksUpload objects marked for merging found for user {request.user} and class {teacherclass}.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         if grading.is_advance:
#             exclude_subjects = ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True)
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = []
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         all_data = []
#         subjects_set = set()
#         student_data_dict = {}

#         students_db = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#             'marks__subject', 'marks__user__teacher_profile'
#         )

#         for upload in pdf_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file not found at {pdf_path}.")
#                 logger.error(f"PDF not found: {pdf_path}")
#                 continue
                
#             try:
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in PDF at {pdf_path}.")
#                     logger.error(f"No tables in PDF: {pdf_path}")
#                     continue

#                 pdf_dfs = []
#                 for i, df in enumerate(dfs):
#                     df = df.dropna(how='all')
#                     if df.empty:
#                         logger.warning(f"Table {i} in PDF {pdf_path} is empty after dropping NA.")
#                         continue
#                     df.columns = df.columns.str.strip().str.lower()
#                     df = df.rename(columns={'s/no': 's_no', 'student name': 'fullname', 'sex': 'sex', 'index no': 'indexnumber'})
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Columns: {list(df.columns)}")
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Number of students: {len(df)}")
#                     pdf_dfs.append(df)

#                 if not pdf_dfs:
#                     messages.error(request, f"No valid tables found in PDF at {pdf_path}.")
#                     logger.error(f"No valid tables in PDF: {pdf_path}")
#                     continue

#                 df = pd.concat(pdf_dfs, ignore_index=True)
#                 logger.debug(f"PDF {pdf_path} - Total students after concatenation: {len(df)}")
#                 subjects_set.update([col for col in df.columns if col not in ['s_no', 'fullname', 'sex', 'indexnumber', 'total', 'avg', 'grade', 'pos', 'div', 'pts']])
#                 all_data.append(df)

#             except Exception as e:
#                 messages.error(request, f"Error processing PDF at {pdf_path}: {str(e)}")
#                 logger.error(f"Error processing PDF {pdf_path}: {str(e)}", exc_info=True)
#                 continue

#         subjects_set = {s for s in subjects_set if s.lower() in subjects_db_dict}
#         if not all_data:
#             messages.error(request, "No valid data extracted from selected PDFs.")
#             return render(request, 'merge_term_marks_pdfs.html', context)

#         def get_grade(mark):
#             if mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_remark(grade):
#             remark_map = {
#                 'A': 'Excellent',
#                 'B': 'Very Good',
#                 'C': 'Good',
#                 'D': 'Pass',
#                 'E': 'Poor',
#                 'S': 'Subsidiary',
#                 'F': 'Fail',
#                 '-': '-'
#             }
#             return remark_map.get(grade, '-')

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         for df in all_data:
#             for _, row in df.iterrows():
#                 indexnumber = str(row['indexnumber']).strip()
#                 if indexnumber.lower() == 'nan' or not indexnumber:
#                     logger.warning(f"Skipping row with invalid indexnumber: {row.to_dict()}")
#                     continue

#                 if indexnumber not in student_data_dict:
#                     student_data_dict[indexnumber] = {
#                         'fullname': row['fullname'],
#                         'sex': row['sex'],
#                         'indexnumber': indexnumber,
#                         'marks': {},
#                         'total_marks': 0,
#                         'subject_count': 0
#                     }

#                 student = student_data_dict[indexnumber]
                
#                 for subj_name, subject in subjects_db_dict.items():
#                     if subj_name in df.columns:
#                         mark_raw = str(row[subj_name]).strip()
#                         logger.debug(f"Student {row['indexnumber']} - Raw mark for {subj_name}: {mark_raw}")
#                         if mark_raw in ['-', ''] or pd.isna(mark_raw):
#                             mark = 0
#                             grade = '-'
#                         else:
#                             mark_match = re.match(r'(\d+\.?\d*)\s*([A-FS-])?', mark_raw)
#                             if mark_match:
#                                 mark = float(mark_match.group(1)) if mark_match.group(1) else 0
#                                 grade = mark_match.group(2) if mark_match.group(2) else get_grade(mark)
#                                 logger.debug(f"Student {row['indexnumber']} - Parsed mark for {subj_name}: {mark}, Grade: {grade}")
#                             else:
#                                 mark = 0
#                                 grade = '-'
#                                 logger.debug(f"Student {row['indexnumber']} - Failed to parse mark for {subj_name}: {mark_raw}")

#                         db_student = students_db.filter(indexNumber=indexnumber).first()
#                         teacher_names = []
#                         if db_student:
#                             mark_objs = db_student.marks.filter(subject=subject)
#                             if mark_objs.exists():
#                                 for mark_obj in mark_objs:
#                                     if mark_obj.user:
#                                         try:
#                                             teacher_name = mark_obj.user.teacher_profile.first().teacherName or mark_obj.user.username if mark_obj.user.teacher_profile.exists() else mark_obj.user.username
#                                             if teacher_name and teacher_name not in teacher_names:
#                                                 teacher_names.append(teacher_name)
#                                         except Exception as e:
#                                             logger.warning(f"Error fetching teacher name for mark {mark_obj.id}, student {indexnumber}, subject {subj_name}: {str(e)}")
#                             else:
#                                 logger.debug(f"No Mark objects found for student {indexnumber}, subject {subj_name}")
#                         else:
#                             logger.debug(f"No student found in database for indexnumber {indexnumber}")
#                         teachers_display = ', '.join(teacher_names) if teacher_names else '-'
#                         if mark > 0 and teachers_display == '-':
#                             logger.warning(f"No teachers found for student {indexnumber}, subject {subj_name} with mark {mark}")

#                         if subject.id not in student['marks']:
#                             student['marks'][subject.id] = {
#                                 'subject_id': subject.id,
#                                 'subject_name': subject.nameSubject,
#                                 'mark': mark,
#                                 'grade': grade,
#                                 'teachers': teachers_display,
#                                 'is_excluded': subject.id in exclude_subjects,
#                                 'count': 1
#                             }
#                         else:
#                             existing = student['marks'][subject.id]
#                             if mark > 0:
#                                 existing['mark'] = (existing['mark'] * existing['count'] + mark) / (existing['count'] + 1)
#                                 existing['grade'] = get_grade(existing['mark'])
#                                 existing['count'] += 1
#                                 if teachers_display != '-' and teachers_display not in existing['teachers'].split(', '):
#                                     existing_teachers = existing['teachers'].split(', ') if existing['teachers'] != '-' else []
#                                     existing_teachers.extend([t for t in teacher_names if t not in existing_teachers])
#                                     existing['teachers'] = ', '.join(existing_teachers) if existing_teachers else '-'
#                             else:
#                                 existing['grade'] = '-' if existing['mark'] == 0 else get_grade(existing['mark'])

#         logger.debug(f"Total unique students after processing all PDFs: {len(student_data_dict)}")

#         student_data = []
#         for student in student_data_dict.values():
#             total_marks = 0
#             subject_count = 0
#             marks_list = []
            
#             for mark_info in student['marks'].values():
#                 marks_list.append(mark_info)
#                 if mark_info['mark'] > 0:
#                     total_marks += mark_info['mark']
#                     subject_count += 1

#             student['marks'] = marks_list
#             student['total_marks'] = total_marks
#             student['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student['grade'] = get_grade(student['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student['division'] = division
#             student['total_points'] = total_points
            
#             student_data.append(student)

#         logger.debug(f"Total students in final student_data: {len(student_data)}")

#         student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         response = HttpResponse(content_type='application/pdf')
#         filename = f"merged_pdfs_{teacherclass.ClassName}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style = styles['Heading1']
#         subheader_style = styles['Heading2']
#         body_style = styles['BodyText']
#         footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#         bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#         header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#         body_style.fontSize = 7

#         def add_page_number(canvas, doc):
#             page_num = canvas.getPageNumber()
#             text = f"Page {page_num}"
#             canvas.saveState()
#             canvas.setFont("Helvetica", 8)
#             canvas.setFillColor(colors.grey)
#             canvas.drawCentredString(A4[0]/2, 15, text)
#             canvas.restoreState()

#         display = DisplayModel.objects.filter(user=request.user).first()
#         header_text = display.header if display else f"Merged Term Marks for {teacherclass.ClassName}"
#         elements.append(Paragraph(header_text, header_style))
#         elements.append(Spacer(1, 4))
#         elements.append(Paragraph(display.body if display else f"Summary - {teacherclass.ClassName}", subheader_style))
#         elements.append(Spacer(1, 8))

#         if display and display.image:
#             try:
#                 icon = Image(display.image.path, width=2*cm, height=2*cm)
#                 icon.hAlign = 'CENTER'
#                 elements.append(icon)
#                 elements.append(Spacer(1, 0.5*cm))
#             except Exception as e:
#                 print(f"Error loading DisplayModel image: {e}")

#         if not student_data:
#             elements.append(Paragraph("No data available to merge.", body_style))
#         else:
#             elements.append(Paragraph("Merged Term Marks", subheader_style))
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                            [s.nameSubject for s in subjects_db] + 
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]
            
#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullname'] or '-', student['sex'] or '-', student['indexnumber'] or '-']
#                 for subject in subjects_db:
#                     mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                     if mark_info and mark_info['mark'] > 0:
#                         sub_table = Table([[f"{mark_info['mark']:.2f}", mark_info['grade']]],
#                                         colWidths=[10, 12], hAlign='CENTER')
#                         sub_table.setStyle(TableStyle([
#                             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                             ('FONTSIZE', (0, 0), (-1, -1), 4),
#                             ('LEADING', (0, 0), (-1, -1), 8),
#                             ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                         ]))
#                         row.append(sub_table)
#                     else:
#                         row.append('-')
                
#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len(subjects_db) + [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#             for i, student in enumerate(student_data):
#                 if i > 0:
#                     elements.append(PageBreak())
                
#                 header_data = []
#                 if display and display.image:
#                     try:
#                         icon = Image(display.image.path, width=2*cm, height=2*cm)
#                         icon.drawHeight = 2*cm
#                         icon.drawWidth = 2*cm
#                         icon.hAlign = 'LEFT'
#                         header_data.append([icon, [
#                             Paragraph(display.header if display else f"Merged Term Marks for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                     except Exception as e:
#                         print(f"Error loading DisplayModel image: {e}")
#                         header_data.append(['', [
#                             Paragraph(display.header if display else f"Merged Term Marks for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                 else:
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Merged Term Marks for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])

#                 header_table = Table(header_data, colWidths=[3*cm, A4[0]-45-3*cm])
#                 header_table.setStyle(TableStyle([
#                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                     ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                     ('LEFTPADDING', (0, 0), (0, 0), 10),
#                     ('RIGHTPADDING', (1, 0), (1, 0), 10),
#                 ]))
#                 elements.append(header_table)
#                 elements.append(Spacer(1, 10))

#                 elements.append(Paragraph(f"Student Name: {student['fullname'] or 'Unnamed Student'}", bold_style))
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(f"Index Number: {student['indexnumber'] or '-'}", bold_style))
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#                 elements.append(Spacer(1, 10))

#                 elements.append(Paragraph("Merged Academic Results", body_style))
#                 student_data_table = [['Subject', 'Marks', 'Grade', 'Teacher', 'Remarks']]
#                 grades_for_division = []

#                 for mark in student['marks']:
#                     remark = get_remark(mark['grade'])
#                     if mark['mark'] > 0:
#                         student_data_table.append([
#                             mark['subject_name'] or 'Unnamed',
#                             f"{mark['mark']:.2f}",
#                             mark['grade'],
#                             mark['teachers'],
#                             remark
#                         ])
#                         if not mark['is_excluded']:
#                             grades_for_division.append(mark['grade'])
#                     else:
#                         student_data_table.append([
#                             mark['subject_name'] or 'Unnamed',
#                             '-',
#                             mark['grade'],
#                             mark['teachers'],
#                             remark
#                         ])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '-', '-'])

#                 student_table = Table(student_data_table, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(summary, body_style))
#                 elements.append(Spacer(1, 12))
#                 elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#         elements.append(Spacer(1, 10))
#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", footer_style))
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'Merged term marks generated successfully!')
#         return response

#     if class_id:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['uploads'] = TermMarksUpload.objects.filter(teacherclass=teacherclass, user=request.user)

#     return render(request, 'merge_term_marks_pdfs.html', context)
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib import messages
# from django.db.models import Sum
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from datetime import datetime
# from decimal import Decimal
# import os
# import tabula
# import pandas as pd
# import re
# import logging

# logger = logging.getLogger(__name__)

# @login_required
# def merge_term_marks_with_financial(request, class_id=None, grade_id=None):
#     classes = TeacherClass.objects.filter(user=request.user,academicclassyear__active_year=True)
#     grades = GradingModel.objects.filter(user=request.user)

#     context = {
#         'classes': classes,
#         'grades': grades,
#     }

#     if request.method == 'POST':
#         class_id = request.POST.get('class_id')
#         grade_id = request.POST.get('grade_id')

#         if not class_id or not grade_id or not TeacherClass.objects.filter(id=class_id, user=request.user).exists() or not GradingModel.objects.filter(id=grade_id, user=request.user).exists():
#             messages.error(request, f"Invalid selection: Class ID {class_id} or Grade ID {grade_id}.")
#             return render(request, 'upload_term_marks.html', context)

#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['selected_grade_id'] = grade_id

#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by
#         except Teacher.DoesNotExist:
#             messages.error(request, "Your account is not linked to a valid teacher profile.")
#             return redirect('teacher_dashboard')

#         if not creator:
#             messages.error(request, "You are not authorized to generate reports.")
#             return redirect('teacher_dashboard')

#         level = 'Alevel' if grading.is_advance else 'Olevel'
        
#         required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#         subject_ids = required_subjects.values_list('subject_id', flat=True)
#         subjects_db = Subject.objects.filter(id__in=subject_ids, user=request.user)
#         subjects_db_dict = {s.nameSubject.lower(): s for s in subjects_db}

#         if grading.is_advance:
#             exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True))
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_e: 'E', grading.grade_s: 'S',
#                 grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#         else:
#             exclude_subjects = set()
#             grade_thresholds = {
#                 grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C',
#                 grading.grade_d: 'D', grading.grade_f: 'F'
#             }
#             grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#         division_thresholds = [
#             {'max': grading.division_1, 'label': 'I'},
#             {'max': grading.division_2, 'label': 'II'},
#             {'max': grading.division_3, 'label': 'III'},
#             {'max': grading.division_4, 'label': 'IV'},
#             {'max': float('inf'), 'label': '0'}
#         ]

#         pdf_uploads = TermMarksUpload.objects.filter(
#             user=request.user,
#             teacherclass=teacherclass,
#             for_merging_pdf=True
#         )
#         if not pdf_uploads.exists():
#             messages.error(request, "No PDFs selected for merging.")
#             logger.error(f"No TermMarksUpload objects marked for merging found for user {request.user} and class {teacherclass}.")
#             return render(request, 'upload_term_marks.html', context)

#         students_db = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#             'marks__subject', 'marks__user__teacher_profile'
#         )

#         all_data = []
#         subjects_set = set()
#         student_data_dict = {}

#         for upload in pdf_uploads:
#             pdf_path = upload.pdf_file.path
#             if not os.path.exists(pdf_path):
#                 messages.error(request, f"PDF file not found at {pdf_path}.")
#                 logger.error(f"PDF not found: {pdf_path}")
#                 continue

#             try:
#                 dfs = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True, guess=False)
#                 if not dfs:
#                     messages.error(request, f"No tables found in PDF at {pdf_path}.")
#                     logger.error(f"No tables in PDF: {pdf_path}")
#                     continue

#                 pdf_dfs = []
#                 for i, df in enumerate(dfs):
#                     df = df.dropna(how='all')
#                     if df.empty:
#                         logger.warning(f"Table {i} in PDF {pdf_path} is empty after dropping NA.")
#                         continue
#                     df.columns = df.columns.str.strip().str.lower()
#                     df = df.rename(columns={'s/no': 's_no', 'student name': 'fullname', 'sex': 'sex', 'index no': 'indexnumber'})
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Columns: {list(df.columns)}")
#                     logger.debug(f"Table {i} in PDF {pdf_path} - Number of students: {len(df)}")
#                     pdf_dfs.append(df)

#                 if not pdf_dfs:
#                     messages.error(request, f"No valid tables found in PDF at {pdf_path}.")
#                     logger.error(f"No valid tables in PDF: {pdf_path}")
#                     continue

#                 df = pd.concat(pdf_dfs, ignore_index=True)
#                 logger.debug(f"PDF {pdf_path} - Total students after concatenation: {len(df)}")
#                 subjects_set.update([col for col in df.columns if col not in ['s_no', 'fullname', 'sex', 'indexnumber', 'total', 'avg', 'grade', 'pos', 'div', 'pts']])
#                 all_data.append(df)

#             except Exception as e:
#                 messages.error(request, f"Error processing PDF at {pdf_path}: {str(e)}")
#                 logger.error(f"Error processing PDF {pdf_path}: {str(e)}", exc_info=True)
#                 continue

#         subjects_set = {s for s in subjects_set if s.lower() in subjects_db_dict}
#         if not all_data:
#             messages.error(request, "No valid data extracted from selected PDFs.")
#             return render(request, 'upload_term_marks.html', context)

#         def get_grade(mark):
#             if mark is None or mark == 0:
#                 return '-'
#             for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#                 if mark >= threshold:
#                     return grade
#             return 'F'

#         def get_remark(grade):
#             remark_map = {
#                 'A': 'Excellent',
#                 'B': 'Very Good',
#                 'C': 'Good',
#                 'D': 'Pass',
#                 'E': 'Poor',
#                 'S': 'Subsidiary',
#                 'F': 'Fail',
#                 '-': '-'
#             }
#             return remark_map.get(grade, '-')

#         def get_division(grades_for_division):
#             filtered_grades = [g for g in grades_for_division if g != '-']
#             num_valid_subjects = len(filtered_grades)
#             if grading.is_advance and num_valid_subjects < 3:
#                 return "Inc", 0
#             elif not grading.is_advance and num_valid_subjects < 7:
#                 return "Inc", 0
#             sorted_grades = sorted(filtered_grades, key=lambda x: grade_points[x])[:3 if grading.is_advance else 7]
#             total_points = sum(grade_points[g] for g in sorted_grades)
#             division = 'IV'
#             for threshold in division_thresholds:
#                 if total_points <= threshold['max']:
#                     division = threshold['label']
#                     break
#             return division, total_points

#         for df in all_data:
#             for _, row in df.iterrows():
#                 indexnumber = str(row['indexnumber']).strip()
#                 if indexnumber.lower() == 'nan' or not indexnumber:
#                     logger.warning(f"Skipping row with invalid indexnumber: {row.to_dict()}")
#                     continue

#                 if indexnumber not in student_data_dict:
#                     student_data_dict[indexnumber] = {
#                         'id': None,
#                         'fullname': row['fullname'],
#                         'sex': row['sex'],
#                         'indexnumber': indexnumber,
#                         'marks': {},
#                         'total_marks': 0,
#                         'subject_count': 0
#                     }

#                 student = student_data_dict[indexnumber]
                
#                 for subj_name, subject in subjects_db_dict.items():
#                     if subj_name in df.columns:
#                         mark_raw = str(row[subj_name]).strip()
#                         if mark_raw in ['-', ''] or pd.isna(mark_raw):
#                             mark = 0
#                             grade = '-'
#                         else:
#                             mark_match = re.match(r'(\d+\.?\d*)\s*([A-FS-])?', mark_raw)
#                             if mark_match:
#                                 mark = float(mark_match.group(1)) if mark_match.group(1) else 0
#                                 grade = mark_match.group(2) if mark_match.group(2) else get_grade(mark)
#                             else:
#                                 mark = 0
#                                 grade = '-'

#                         db_student = students_db.filter(indexNumber=indexnumber).first()
#                         teacher_name = '-'
#                         if db_student:
#                             mark_obj = db_student.marks.filter(subject=subject).first()
#                             if mark_obj and mark_obj.user:
#                                 teacher_name = mark_obj.user.teacher_profile.first().teacherName or mark_obj.user.username if mark_obj.user.teacher_profile.exists() else mark_obj.user.username

#                         if subject.id not in student['marks']:
#                             student['marks'][subject.id] = {
#                                 'subject_id': subject.id,
#                                 'subject_name': subject.nameSubject,
#                                 'mark': mark,
#                                 'grade': grade,
#                                 'teacher': teacher_name,
#                                 'is_excluded': subject.id in exclude_subjects,
#                                 'count': 1
#                             }
#                         else:
#                             existing = student['marks'][subject.id]
#                             if mark > 0:
#                                 existing['mark'] = (existing['mark'] * existing['count'] + mark) / (existing['count'] + 1)
#                                 existing['grade'] = get_grade(existing['mark'])
#                                 existing['count'] += 1
#                             else:
#                                 existing['grade'] = '-' if existing['mark'] == 0 else get_grade(existing['mark'])

#         for student in student_data_dict.values():
#             try:
#                 db_student = students_db.get(indexNumber=student['indexnumber'])
#                 student['id'] = db_student.id
#             except Student.DoesNotExist:
#                 logger.warning(f"No matching student found for indexnumber: {student['indexnumber']}")

#         student_data = []
#         for student in student_data_dict.values():
#             total_marks = 0
#             subject_count = 0
#             marks_list = []
            
#             for mark_info in student['marks'].values():
#                 marks_list.append(mark_info)
#                 if mark_info['mark'] > 0:
#                     total_marks += mark_info['mark']
#                     subject_count += 1

#             student['marks'] = marks_list
#             student['total_marks'] = total_marks
#             student['average_marks'] = total_marks / subject_count if subject_count > 0 else 0
#             student['grade'] = get_grade(student['average_marks'])

#             grades_for_division = [m['grade'] for m in marks_list if not m['is_excluded']]
#             division, total_points = get_division(grades_for_division)
#             student['division'] = division
#             student['total_points'] = total_points
            
#             student_data.append(student)

#         student_data.sort(key=lambda x: x['average_marks'], reverse=True)
#         for i, student in enumerate(student_data, 1):
#             student['position'] = i

#         response = HttpResponse(content_type='application/pdf')
#         filename = f"MergedTermMarksFinancial_{teacherclass.ClassName.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#         elements = []
#         styles = getSampleStyleSheet()
#         header_style = styles['Heading1']
#         subheader_style = styles['Heading2']
#         body_style = styles['BodyText']
#         footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#         bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9)
#         discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=10, textColor=colors.red, spaceAfter=6)
#         header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#         body_style.fontSize = 7

#         def add_page_number(canvas, doc):
#             page_num = canvas.getPageNumber()
#             text = f"Page {page_num}"
#             canvas.saveState()
#             canvas.setFont("Helvetica", 8)
#             canvas.setFillColor(colors.grey)
#             canvas.drawCentredString(A4[0]/2, 15, text)
#             canvas.restoreState()

#         display = DisplayModel.objects.filter(user=request.user).first()
#         header_text = display.header if display else f"Merged Term Marks and Financial Report for {teacherclass.ClassName}"
#         elements.append(Paragraph(header_text, header_style))
#         elements.append(Spacer(1, 4))
#         elements.append(Paragraph(display.body if display else f"Summary - {teacherclass.ClassName}", subheader_style))
#         elements.append(Spacer(1, 8))

#         if display and display.image:
#             try:
#                 icon = Image(display.image.path, width=2*cm, height=2*cm)
#                 icon.hAlign = 'CENTER'
#                 elements.append(icon)
#                 elements.append(Spacer(1, 0.5*cm))
#             except Exception as e:
#                 print(f"Error loading DisplayModel image: {e}")

#         if not student_data:
#             elements.append(Paragraph("No data available for this class from selected PDFs.", body_style))
#         else:
#             elements.append(Paragraph("Merged Term Marks", subheader_style))
#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] +
#                            [s.nameSubject for s in subjects_db if s.nameSubject.lower() in subjects_set] +
#                            ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#             for i, student in enumerate(student_data, 1):
#                 row = [str(i), student['fullname'] or '-', student['sex'] or '-', student['indexnumber'] or '-']
#                 for subject in subjects_db:
#                     if subject.nameSubject.lower() in subjects_set:
#                         mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                         if mark_info and mark_info['mark'] > 0:
#                             sub_table = Table(
#                                 [[f"{mark_info['mark']:.2f}", mark_info['grade']]],
#                                 colWidths=[10, 12],
#                                 hAlign='CENTER'
#                             )
#                             sub_table.setStyle(TableStyle([
#                                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                                 ('FONTSIZE', (0, 0), (-1, -1), 4),
#                                 ('LEADING', (0, 0), (-1, -1), 8),
#                                 ('TEXTCOLOR', (1, 0), (1, 0), colors.red if mark_info['grade'] == 'F' else colors.black),
#                             ]))
#                             row.append(sub_table)
#                         else:
#                             row.append('-')

#                 row.extend([
#                     f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-',
#                     f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-',
#                     student['grade'],
#                     str(student['position']),
#                     student['division'],
#                     student['total_points'] if student['total_points'] > 0 else '-'
#                 ])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             base_width = (A4[0] - 30) / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 3.0] + [base_width * 0.5] + [base_width * 2.0] +
#                           [base_width * 1.0] * len([s for s in subjects_db if s.nameSubject.lower() in subjects_set]) +
#                           [base_width * 0.8] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 6),
#                 ('LEADING', (0, 0), (-1, -1), 8),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.extend([KeepTogether(overall_table), Spacer(1, 10)])

#             for student in student_data:
#                 if not student['id']:
#                     continue
#                 elements.append(PageBreak())
#                 header_data = []
#                 if display and display.image:
#                     try:
#                         icon = Image(display.image.path, width=2*cm, height=2*cm)
#                         icon.drawHeight = 2*cm
#                         icon.drawWidth = 2*cm
#                         icon.hAlign = 'LEFT'
#                         header_data.append([icon, [
#                             Paragraph(display.header if display else f"Merged Report for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                     except Exception as e:
#                         print(f"Error loading DisplayModel image: {e}")
#                         header_data.append(['', [
#                             Paragraph(display.header if display else f"Merged Report for {teacherclass.ClassName}", header_style),
#                             Spacer(1, 4),
#                             Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                         ]])
#                 else:
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Merged Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])

#                 header_table = Table(header_data, colWidths=[3*cm, A4[0]-45-3*cm])
#                 header_table.setStyle(TableStyle([
#                     ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                     ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                     ('LEFTPADDING', (0, 0), (0, 0), 10),
#                     ('RIGHTPADDING', (1, 0), (1, 0), 10),
#                 ]))
#                 elements.append(header_table)
#                 elements.append(Spacer(1, 10))

#                 elements.append(Paragraph(f"Student Name: {student['fullname'] or 'Unnamed Student'}", bold_style))
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(f"Index Number: {student['indexnumber'] or '-'}", bold_style))
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(f"Class: {teacherclass.ClassName}", bold_style))
#                 elements.append(Spacer(1, 10))

#                 elements.append(Paragraph("Merged Academic Results", body_style))
#                 student_data_table = [['Subject', 'Marks', 'Grade', 'Teacher', 'Remarks']]
#                 grades_for_division = []
#                 for mark in student['marks']:
#                     remark = get_remark(mark['grade'])
#                     if mark['mark'] > 0:
#                         student_data_table.append([
#                             mark['subject_name'] or 'Unnamed',
#                             f"{mark['mark']:.2f}",
#                             mark['grade'],
#                             mark['teacher'],
#                             remark
#                         ])
#                         if not mark['is_excluded']:
#                             grades_for_division.append(mark['grade'])
#                     else:
#                         student_data_table.append([
#                             mark['subject_name'] or 'Unnamed',
#                             '-',
#                             mark['grade'],
#                             mark['teacher'],
#                             remark
#                         ])

#                 if len(student_data_table) == 1:
#                     student_data_table.append(['No subjects with marks available', '-', '-', '-', '-'])

#                 student_table = Table(student_data_table, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 6),
#                     ('LEADING', (0, 0), (-1, -1), 8),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 elements.append(student_table)

#                 overall_grade = student['grade']
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{student['average_marks']:.2f}" if student['average_marks'] > 0 else '-'
#                 total_display = f"{student['total_marks']:.2f}" if student['total_marks'] > 0 else '-'
#                 points_display = str(total_points) if total_points > 0 else '-'
#                 summary = f"Position: {student['position']} | Avg: {avg_display} | Total: {total_display} | Division: {division} | Points: {points_display}"
#                 elements.append(Spacer(1, 6))
#                 elements.append(Paragraph(summary, body_style))
#                 elements.append(Spacer(1, 10))

#                 elements.append(Paragraph("Fee Report", body_style))
#                 student_obj = Student.objects.get(id=student['id'])
#                 student_fees = StudentFee.objects.filter(student=student_obj, teacherclass=teacherclass).select_related('fee')
#                 if not student_fees.exists():
#                     elements.append(Paragraph("No fees assigned.", body_style))
#                 else:
#                     table_data = [['Fee Name', 'Required', 'Paid', 'Balance']]
#                     total_required = Decimal('0.00')
#                     total_paid_all = Decimal('0.00')
#                     total_discounted = Decimal('0.00')

#                     for sf in student_fees:
#                         fee = sf.fee
#                         discount = Discount.objects.filter(student=student_obj, fee=fee, user=creator).first()
#                         discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                         adjusted_required = fee.amount - discount_amount
#                         total_discounted += discount_amount
#                         total_paid_result = PayFee.objects.filter(student=student_obj, fee=fee).aggregate(total=Sum('amount_paid'))
#                         total_paid = total_paid_result['total'] if total_paid_result['total'] is not None else Decimal('0.00')
#                         balance = adjusted_required - total_paid
#                         total_required += adjusted_required
#                         total_paid_all += total_paid
#                         fee_display = f"{fee.fee_name} (Discounted: {discount_amount:.2f})" if discount else fee.fee_name
#                         table_data.append([
#                             Paragraph(fee_display, body_style),
#                             Paragraph(f"{adjusted_required:.2f}", body_style),
#                             Paragraph(f"{total_paid:.2f}", body_style),
#                             Paragraph(f"{balance:.2f}", body_style)
#                         ])

#                     table_data.append([
#                         Paragraph('TOTAL', bold_style),
#                         Paragraph(f"{total_required:.2f}", bold_style),
#                         Paragraph(f"{total_paid_all:.2f}", bold_style),
#                         Paragraph(f"{total_required - total_paid_all:.2f}", bold_style)
#                     ])

#                     page_width = A4[0] - 30
#                     col_widths = [0.40 * page_width, 0.20 * page_width, 0.20 * page_width, 0.20 * page_width]
#                     table = Table(table_data, colWidths=col_widths)
#                     table.setStyle(TableStyle([
#                         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                         ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                         ('FONTSIZE', (0, 0), (-1, 0), 10),
#                         ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                         ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                         ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                         ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                         ('FONTSIZE', (0, 1), (-1, -1), 9),
#                         ('LEFTPADDING', (0, 0), (-1, -1), 6),
#                         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#                         ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                     ]))
#                     elements.append(table)
#                     if total_discounted > 0:
#                         elements.append(Paragraph(f"Total Discount Applied: {total_discounted:.2f}", discount_style))

#                 elements.append(Spacer(1, 12))
#                 elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#         elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d')}", footer_style))
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'Merged term marks with financial report generated successfully!')
#         return response

#     if class_id:
#         teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user)
#         context['teacherclass'] = teacherclass
#         context['uploads'] = TermMarksUpload.objects.filter(teacherclass=teacherclass, user=request.user)

#     return render(request, 'upload_term_marks.html', context)

# from django.contrib.auth.decorators import login_required
# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib import messages
# from django.http import HttpResponse
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from reportlab.lib.units import cm, inch
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from decimal import Decimal
# from datetime import datetime


# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.db.models import Sum, Avg
# from django.db.models import Q as models_Q
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from datetime import datetime
# from django.db.models import Prefetch
# from decimal import Decimal

# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.db.models import Sum, Avg
# from django.db.models import Q as models_Q
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm, inch
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from datetime import datetime
# from django.db.models import Prefetch
# from decimal import Decimal
# import logging

# logger = logging.getLogger(__name__)

# @login_required
# def download_full_report(request, class_id, grade_id, report_id=''):
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id else DisplayModel.objects.filter(user=request.user).first()

#     # Get selected examination IDs from POST data
#     examination_ids = request.POST.getlist('exams')
#     if not examination_ids:
#         messages.error(request, "No examinations selected.")
#         return redirect('all_student_marks')

#     examination_names = ExaminationName.objects.filter(id__in=examination_ids, user=request.user)
#     if not examination_names.exists():
#         messages.error(request, "No valid examinations found for the selected IDs.")
#         return redirect('all_student_marks')

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subject_ids = required_subjects.values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=subject_ids, user=request.user).order_by('nameSubject')

#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects, examinationname__in=examination_names).select_related('subject', 'examinationname', 'user')),
#         Prefetch('assigned_fees', queryset=StudentFee.objects.filter(teacherclass=teacherclass).select_related('fee')),
#         Prefetch('payfee', queryset=PayFee.objects.select_related('fee')),
#         Prefetch('student_focus', queryset=StudentFocus.objects.prefetch_related('student_fcs'))
#     )

#     try:
#         teacher_profile = Teacher.objects.get(user=request.user)
#         creator = teacher_profile.created_by or request.user
#     except Teacher.DoesNotExist:
#         messages.error(request, "Your account is not linked to a valid teacher profile.")
#         return redirect('teacher_dashboard')

#     if not creator:
#         messages.error(request, "You are not authorized to download reports.")
#         return redirect('teacher_dashboard')

#     all_marks = Mark.objects.filter(teacherclass=teacherclass, subject__in=subjects, examinationname__in=examination_names).select_related('user')
#     user_ids = {mark.user_id for mark in all_marks if mark.user_id}
#     teacher_map = {teacher.user_id: teacher.teacherName for teacher in Teacher.objects.filter(user__in=user_ids)}

#     response = HttpResponse(content_type='application/pdf')
#     exam_suffix = "_selected_exams" if examination_names.count() > 1 else examination_names.first().exam_name.replace(' ', '_')
#     filename = f"full_report_{teacherclass.ClassName.class_name or 'Unnamed_Class'}_{exam_suffix}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=8)
#     discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=9, textColor=colors.red, spaceAfter=4)
#     summary_style = ParagraphStyle(name='Summary', parent=styles['BodyText'], fontSize=9, fontName='Helvetica-Bold', spaceAfter=4)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#     body_style.fontSize = 6

#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     if grading.is_advance:
#         exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True))
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D',
#             grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#     else:
#         exclude_subjects = set()
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#     def get_grade(mark):
#         if mark is None:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_remark(grade):
#         remark_map = {
#             'A': 'Excellent', 'B': 'Very Good', 'C': 'Good', 'D': 'Pass',
#             'E': 'Poor', 'S': 'Subsidiary', 'F': 'Fail', '-': '-'
#         }
#         return remark_map.get(grade, '-')

#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

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

#     header_text = display.header if display else f"Full Academic and Financial Report for {teacherclass.ClassName.class_name or 'Unnamed Class'}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 2))
#     academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#     exam_names = ", ".join([exam.exam_name for exam in examination_names])
#     elements.append(Paragraph(display.body if display else f"Comprehensive Summary for {exam_names} - {teacherclass.ClassName.class_name} ({academic_year})", subheader_style))
#     elements.append(Spacer(1, 2))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=1.8*cm, height=1.8*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.2*cm))
#         except Exception as e:
#             logger.error(f"Error loading DisplayModel image: {e}")

#     if not students.exists() or not subjects.exists() or not examination_names.exists():
#         elements.append(Paragraph("No data available for this class or examinations.", body_style))
#     else:
#         for exam_idx, examination_name in enumerate(examination_names):
#             if exam_idx > 0:
#                 elements.append(Spacer(1, 4))
#             elements.append(Paragraph(f"Academic Results - {examination_name.exam_name}", subheader_style))
#             mark_filter = models_Q(marks__subject__in=subjects, marks__examinationname=examination_name)
#             students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#                 total_marks=Sum('marks__marks', filter=mark_filter),
#                 average_marks=Avg('marks__marks', filter=mark_filter)
#             )
#             student_totals = []
#             for student in students_marks_evaluation:
#                 total_marks = student.total_marks or 0
#                 average_marks = student.average_marks or 0
#                 grades = []
#                 for subject in subjects:
#                     mark = student.marks.filter(subject=subject, examinationname=examination_name).first()
#                     grade = get_grade(mark.marks if mark else None)
#                     grades.append(grade)
#                 has_valid_marks = any(grade != '-' for grade in grades)
#                 student_totals.append((student, total_marks, average_marks, has_valid_marks))

#             student_totals.sort(key=lambda x: (-x[3], -x[2]))

#             overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                             [s.nameSubject for s in subjects] + 
#                             ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#             for i, (student, total_marks, average_marks, _) in enumerate(student_totals, 1):
#                 row = [str(i), student.fullName or 'Unnamed', student.sex or '-', student.indexNumber or '-']
#                 grades_for_division = []
#                 for subject in subjects:
#                     mark = student.marks.filter(subject=subject, examinationname=examination_name).first()
#                     mark_value = mark.marks if mark else None
#                     grade = get_grade(mark_value)
#                     sub_table = Table([[str(mark_value) if mark_value is not None else '-', grade]], colWidths=[14, 14], hAlign='CENTER')
#                     sub_table.setStyle(TableStyle([
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTSIZE', (0, 0), (-1, -1), 5),
#                         ('LEADING', (0, 0), (-1, -1), 6),
#                         ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                     ]))
#                     row.append(sub_table)
#                     if not grading.is_advance or subject.id not in exclude_subjects:
#                         grades_for_division.append(grade)

#                 overall_grade = get_grade(average_marks)
#                 division, total_points = get_division(grades_for_division)
#                 row.extend([total_marks if total_marks > 0 else '-', f"{average_marks:.2f}" if average_marks > 0 else '-',
#                             overall_grade, str(i), division, total_points if total_points > 0 else '-'])
#                 overall_data.append(row)

#             total_columns = len(overall_data[0])
#             available_width = A4[0] - 30
#             base_width = available_width / total_columns
#             col_widths = ([base_width * 0.5] + [base_width * 2.5] + [base_width * 0.5] + [base_width * 1.8] + 
#                           [base_width * 0.9] * len(subjects) + [base_width * 0.6] * 6)

#             overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#             overall_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             elements.append(KeepTogether(overall_table))
#             elements.append(Spacer(1, 4))

#         for i, student in enumerate(students):
#             student_elements = []
#             if i > 0:
#                 student_elements.append(Spacer(1, 4))
            
#             header_data = []
#             academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=1.8*cm, height=1.8*cm)
#                     icon.drawHeight = 1.8*cm
#                     icon.drawWidth = 1.8*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     logger.error(f"Error loading DisplayModel image for student {student.fullName}: {e}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                     Spacer(1, 2),
#                     Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                 ]])

#             header_table = Table(header_data, colWidths=[2.8*cm, A4[0]-45-2.8*cm])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                 ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                 ('LEFTPADDING', (0, 0), (0, 0), 8),
#                 ('RIGHTPADDING', (1, 0), (1, 0), 8),
#             ]))
#             student_elements.append(header_table)
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph(f"Student Name: {student.fullName or 'Unnamed'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Index Number: {student.indexNumber or '-'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Class: {teacherclass.ClassName.class_name}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph(f"Academic and financial report for selected examinations: {exam_names}", body_style))
#             for exam_idx, examination_name in enumerate(examination_names):
#                 if exam_idx > 0:
#                     student_elements.append(Spacer(1, 2))
#                 student_marks = Mark.objects.filter(student=student, teacherclass=teacherclass, subject__in=subjects, examinationname=examination_name)
#                 teacher_names = set()
#                 for mark in student_marks:
#                     if mark.user:
#                         teacher_name = teacher_map.get(mark.user_id, mark.user.username)
#                         teacher_names.add(teacher_name)
#                 teachers_display = ', '.join(sorted(teacher_names)) if teacher_names else '-'
#                 student_elements.append(Paragraph(f"Data Entered/Modified By ({examination_name.exam_name}): {teachers_display}", bold_style))
#                 student_elements.append(Spacer(1, 2))

#                 student_elements.append(Paragraph(f"Examination: {examination_name.exam_name}", body_style))
#                 student_data = [['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']]
#                 grades_for_division = []
#                 for mark in student_marks:
#                     subject = mark.subject
#                     mark_value = mark.marks
#                     grade = get_grade(mark_value)
#                     remark = get_remark(grade)
#                     teacher_name = teacher_map.get(mark.user_id, mark.user.username if mark.user else '-')
#                     student_data.append([subject.nameSubject or 'Unnamed', f"{mark_value:.2f}" if mark_value is not None else '-', grade, teacher_name, remark])
#                     if not grading.is_advance or subject.id not in exclude_subjects:
#                         grades_for_division.append(grade)

#                 if len(student_data) == 1:
#                     student_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#                 student_table = Table(student_data, colWidths=[2.3*inch, 0.9*inch, 0.9*inch, 1.4*inch, 0.9*inch], splitByRow=True, repeatRows=1)
#                 student_table.setStyle(TableStyle([
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ]))
#                 student_elements.append(student_table)

#                 total_marks = Mark.objects.filter(student=student, teacherclass=teacherclass, subject__in=subjects, examinationname=examination_name).aggregate(Sum('marks'))['marks__sum'] or 0
#                 average_marks = Mark.objects.filter(student=student, teacherclass=teacherclass, subject__in=subjects, examinationname=examination_name).aggregate(Avg('marks'))['marks__avg'] or 0
#                 overall_grade = get_grade(average_marks)
#                 division, total_points = get_division(grades_for_division)
#                 avg_display = f"{average_marks:.2f}" if average_marks > 0 else '-'
#                 summary = f"Avg: {avg_display} | Total: {total_marks if total_marks > 0 else '-'} | Division: {division} | Points: {total_points if total_points > 0 else '-'}" 
#                 student_elements.append(Spacer(1, 2))
#                 student_elements.append(Paragraph(summary, body_style))
#                 student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph("Fee Report", body_style))
#             student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#             discounts = Discount.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#             payments = PayFee.objects.filter(student=student, fee__in=student_fees.values('fee')).select_related('fee').order_by('-date_paid')
#             student_focus = StudentFocus.objects.filter(student=student).first()
#             initial_payment = Decimal('0.00')
#             if student_focus:
#                 student_registration = StudentRegistration.objects.filter(studentfocus=student_focus).first()
#                 if student_registration and student_registration.initial_payment:
#                     initial_payment = student_registration.initial_payment

#             if not student_fees.exists():
#                 student_elements.append(Paragraph("No fees assigned.", body_style))
#             else:
#                 page_width = A4[0] - 30
#                 col_widths_fees = [0.25 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.15 * page_width]
#                 table_data = [['Fee Name', 'Required', 'Discount', 'Adjusted', 'Paid', 'Balance', 'Status']]
#                 total_required = Decimal('0.00')
#                 total_paid_all = Decimal('0.00')
#                 total_discounted = Decimal('0.00')
#                 total_balance = Decimal('0.00')

#                 for sf in student_fees:
#                     fee = sf.fee
#                     discount = discounts.filter(fee=fee).first()
#                     discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                     adjusted_required = sf.amount_required - discount_amount
#                     total_discounted += discount_amount
#                     total_paid = payments.filter(fee=fee).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#                     balance = adjusted_required - total_paid
#                     status = 'Paid' if balance <= 0 else 'Pending'
#                     payment_timing = "No Payment"
#                     if payments.filter(fee=fee).exists():
#                         latest_payment = payments.filter(fee=fee).order_by('-date_paid').first()
#                         if latest_payment and latest_payment.date_paid:
#                             if latest_payment.date_paid < sf.start_date:
#                                 payment_timing = "In Advance"
#                             elif sf.start_date <= latest_payment.date_paid <= sf.end_date:
#                                 payment_timing = "On Time"
#                             elif latest_payment.date_paid > sf.end_date:
#                                 payment_timing = "After Deadline"
#                     table_data.append([
#                         Paragraph(fee.fee_name, body_style),
#                         Paragraph(f"{sf.amount_required:.2f}", body_style),
#                         Paragraph(f"{discount_amount:.2f}", body_style),
#                         Paragraph(f"{adjusted_required:.2f}", body_style),
#                         Paragraph(f"{total_paid:.2f}", body_style),
#                         Paragraph(f"{balance:.2f}", body_style),
#                         Paragraph(status, body_style)
#                     ])
#                     total_required += adjusted_required
#                     total_paid_all += total_paid
#                     total_balance += balance
#                     total_discounted += discount_amount

#                 table_data.append([
#                     Paragraph('TOTAL', bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_discounted:.2f}", bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_paid_all:.2f}", bold_style),
#                     Paragraph(f"{total_balance:.2f}", bold_style),
#                     Paragraph('', bold_style)
#                 ])

#                 table = Table(table_data, colWidths=col_widths_fees)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                     ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(table)
#                 summary = f"Total Required: {total_required:.2f} | Total Discount: {total_discounted:.2f} | Total Paid: {total_paid_all:.2f} | Total Balance: {total_balance:.2f} | Initial Payment: {initial_payment:.2f}"
#                 student_elements.append(Paragraph(summary, discount_style if total_discounted > 0 else summary_style))

#                 student_elements.append(Spacer(1, 2))
#                 student_elements.append(Paragraph("Payment Records", body_style))
#                 col_widths_payments = [0.25 * page_width, 0.15 * page_width, 0.15 * page_width, 0.25 * page_width, 0.25 * page_width]
#                 payment_data = [['Fee Name', 'Date', 'Amount', 'Payer Account', 'Description']]
#                 for payment in payments:
#                     payment_data.append([
#                         Paragraph(payment.fee.fee_name, body_style),
#                         Paragraph(payment.date_paid.strftime('%Y-%m-%d') if payment.date_paid else '-', body_style),
#                         Paragraph(f"{payment.amount_paid:.2f}", body_style),
#                         Paragraph(payment.payer_account_no or '-', body_style),
#                         Paragraph(payment.description or '-', body_style)
#                     ])
#                 if not payments.exists():
#                     payment_data.append(['No payment records found', '-', '-', '-', '-'])

#                 payment_table = Table(payment_data, colWidths=col_widths_payments)
#                 payment_table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(payment_table)

#             student_elements.append(Spacer(1, 4))
#             student_elements.append(Paragraph("Principal's Signature: _____________________", bold_style))
#             elements.append(KeepTogether(student_elements))

#         has_fees = any(StudentFee.objects.filter(student=student, teacherclass=teacherclass).exists() for student in students)
#         if has_fees:
#             elements.append(Spacer(1, 4))
#             elements.append(Paragraph("General Fee Report", subheader_style))
#             elements.append(Spacer(1, 2))
#             for i, student in enumerate(students):
#                 student_elements = []
#                 if i > 0:
#                     student_elements.append(Spacer(1, 4))
#                 has_discount = Discount.objects.filter(student=student, teacherclass=teacherclass).exists()
#                 student_label = f"Student: {student.fullName or 'Unnamed'} (Index: {student.indexNumber or '-'})" + (f" <font color='red'>*Discounted*</font>" if has_discount else "")
#                 student_elements.append(Paragraph(student_label, subheader_style))
#                 student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#                 discounts = Discount.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#                 payments = PayFee.objects.filter(student=student, fee__in=student_fees.values('fee')).select_related('fee').order_by('-date_paid')
#                 student_focus = StudentFocus.objects.filter(student=student).first()
#                 initial_payment = Decimal('0.00')
#                 if student_focus:
#                     student_registration = StudentRegistration.objects.filter(studentfocus=student_focus).first()
#                     if student_registration and student_registration.initial_payment:
#                         initial_payment = student_registration.initial_payment

#                 if not student_fees.exists():
#                     student_elements.append(Paragraph("No fees assigned.", body_style))
#                     student_elements.append(Spacer(1, 4))
#                     elements.append(KeepTogether(student_elements))
#                     continue

#                 page_width = A4[0] - 30
#                 col_widths_fees = [0.25 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.15 * page_width]
#                 table_data = [['Fee Name', 'Required', 'Discount', 'Adjusted', 'Paid', 'Balance', 'Status']]
#                 total_required = Decimal('0.00')
#                 total_paid_all = Decimal('0.00')
#                 total_discounted = Decimal('0.00')
#                 total_balance = Decimal('0.00')

#                 for sf in student_fees:
#                     fee = sf.fee
#                     discount = discounts.filter(fee=fee).first()
#                     discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                     adjusted_required = sf.amount_required - discount_amount
#                     total_discounted += discount_amount
#                     total_paid = payments.filter(fee=fee).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#                     balance = adjusted_required - total_paid
#                     status = 'Paid' if balance <= 0 else 'Pending'
#                     payment_timing = "No Payment"
#                     if payments.filter(fee=fee).exists():
#                         latest_payment = payments.filter(fee=fee).order_by('-date_paid').first()
#                         if latest_payment and latest_payment.date_paid:
#                             if latest_payment.date_paid < sf.start_date:
#                                 payment_timing = "In Advance"
#                             elif sf.start_date <= latest_payment.date_paid <= sf.end_date:
#                                 payment_timing = "On Time"
#                             elif latest_payment.date_paid > sf.end_date:
#                                 payment_timing = "After Deadline"
#                     table_data.append([
#                         Paragraph(fee.fee_name, body_style),
#                         Paragraph(f"{sf.amount_required:.2f}", body_style),
#                         Paragraph(f"{discount_amount:.2f}", body_style),
#                         Paragraph(f"{adjusted_required:.2f}", body_style),
#                         Paragraph(f"{total_paid:.2f}", body_style),
#                         Paragraph(f"{balance:.2f}", body_style),
#                         Paragraph(status, body_style)
#                     ])
#                     total_required += adjusted_required
#                     total_paid_all += total_paid
#                     total_balance += balance
#                     total_discounted += discount_amount

#                 table_data.append([
#                     Paragraph('TOTAL', bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_discounted:.2f}", bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_paid_all:.2f}", bold_style),
#                     Paragraph(f"{total_balance:.2f}", bold_style),
#                     Paragraph('', bold_style)
#                 ])

#                 table = Table(table_data, colWidths=col_widths_fees)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                     ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(table)
#                 summary = f"Total Required: {total_required:.2f} | Total Discount: {total_discounted:.2f} | Total Paid: {total_paid_all:.2f} | Total Balance: {total_balance:.2f} | Initial Payment: {initial_payment:.2f}"
#                 student_elements.append(Paragraph(summary, discount_style if total_discounted > 0 else summary_style))

#                 student_elements.append(Spacer(1, 2))
#                 student_elements.append(Paragraph("Payment Records", body_style))
#                 col_widths_payments = [0.25 * page_width, 0.15 * page_width, 0.15 * page_width, 0.25 * page_width, 0.25 * page_width]
#                 payment_data = [['Fee Name', 'Date', 'Amount', 'Payer Account', 'Description']]
#                 for payment in payments:
#                     payment_data.append([
#                         Paragraph(payment.fee.fee_name, body_style),
#                         Paragraph(payment.date_paid.strftime('%Y-%m-%d') if payment.date_paid else '-', body_style),
#                         Paragraph(f"{payment.amount_paid:.2f}", body_style),
#                         Paragraph(payment.payer_account_no or '-', body_style),
#                         Paragraph(payment.description or '-', body_style)
#                     ])
#                 if not payments.exists():
#                     payment_data.append(['No payment records found', '-', '-', '-', '-'])

#                 payment_table = Table(payment_data, colWidths=col_widths_payments)
#                 payment_table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(payment_table)
#                 student_elements.append(Spacer(1, 4))
#                 elements.append(KeepTogether(student_elements))

#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     try:
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'Full report generated successfully!')
#         return response
#     except Exception as e:
#         logger.error(f"Error generating PDF: {str(e)}")
#         messages.error(request, f"Error generating PDF: {str(e)}")
#         return redirect('all_student_marks')

# @login_required
# def download_combined_pdf(request, class_id, grade_id, report_id='', examination_name_id=None):
#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id else DisplayModel.objects.filter(user=request.user).first()
    
#     examination_name_id = request.POST.get('examination_id', examination_name_id or request.session.get('selected_examination_id'))
#     if not examination_name_id:
#         messages.error(request, "No examination selected.")
#         return redirect('all_student_marks')
    
#     examination_name = get_object_or_404(ExaminationName, id=examination_name_id, user=request.user)
    
#     if not hasattr(request, 'creator') or not request.creator:
#         logger.warning(f"Creator not set for user {request.user.username} in download_combined_pdf, defaulting to user")
#         creator = request.user
#     else:
#         creator = request.creator
#         logger.debug(f"Generating PDF for user {request.user.username}, creator {creator.username}")

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subject_ids = required_subjects.values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=subject_ids, user=request.user).order_by('nameSubject')
#     mark_filter = models_Q(subject__in=subjects, examinationname=examination_name)
    
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(mark_filter).select_related('subject', 'examinationname', 'user')),
#         Prefetch('assigned_fees', queryset=StudentFee.objects.filter(teacherclass=teacherclass).select_related('fee')),
#         Prefetch('payfee', queryset=PayFee.objects.select_related('fee')),
#         Prefetch('student_focus', queryset=StudentFocus.objects.prefetch_related('student_fcs'))
#     )

#     all_marks = Mark.objects.filter(teacherclass=teacherclass, subject__in=subjects, examinationname=examination_name).select_related('user')
#     user_ids = {mark.user_id for mark in all_marks if mark.user_id}
#     teacher_map = {teacher.user_id: teacher.teacherName for teacher in Teacher.objects.filter(user__in=user_ids)}
    
#     response = HttpResponse(content_type='application/pdf')
#     exam_suffix = f"_{examination_name.exam_name.replace(' ', '_')}"
#     filename = f"combined_report_{teacherclass.ClassName.class_name or 'Unnamed_Class'}{exam_suffix}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=8)
#     discount_style = ParagraphStyle(name='Discount', parent=styles['BodyText'], fontSize=9, textColor=colors.red, spaceAfter=4)
#     summary_style = ParagraphStyle(name='Summary', parent=styles['BodyText'], fontSize=9, fontName='Helvetica-Bold', spaceAfter=4)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#     body_style.fontSize = 6

#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     if grading.is_advance:
#         exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject', flat=True))
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D',
#             grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#     else:
#         exclude_subjects = set()
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#     def get_grade(mark):
#         if mark is None:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_remark(grade):
#         remark_map = {
#             'A': 'Excellent', 'B': 'Very Good', 'C': 'Good', 'D': 'Pass',
#             'E': 'Poor', 'S': 'Subsidiary', 'F': 'Fail', '-': '-'
#         }
#         return remark_map.get(grade, '-')

#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

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

#     header_text = display.header if display else f"Combined Report for {teacherclass.ClassName.class_name or 'Unnamed Class'} - {examination_name.exam_name}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 2))
#     academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#     elements.append(Paragraph(display.body if display else f"Academic and Financial Summary - {teacherclass.ClassName.class_name} ({academic_year})", subheader_style))
#     elements.append(Spacer(1, 2))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.2*cm))
#         except Exception as e:
#             logger.error(f"Error loading DisplayModel image: {e}")

#     if not students.exists() or not subjects.exists():
#         elements.append(Paragraph("No data available for this class.", body_style))
#     else:
#         elements.append(Paragraph("Academic Results", subheader_style))
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination_name)),
#             average_marks=Avg('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname=examination_name))
#         )
#         student_totals = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             grades = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname=examination_name).first()
#                 grade = get_grade(mark.marks if mark else None)
#                 grades.append(grade)
#             has_valid_marks = any(grade != '-' for grade in grades)
#             student_totals.append((student, total_marks, average_marks, has_valid_marks))

#         student_totals.sort(key=lambda x: (-x[3], -x[2]))

#         overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] + 
#                         [s.nameSubject for s in subjects] + 
#                         ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals, 1):
#             row = [str(i), student.fullName or 'Unnamed', student.sex or '-', student.indexNumber or '-']
#             grades_for_division = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname=examination_name).first()
#                 mark_value = mark.marks if mark else None
#                 grade = get_grade(mark_value)
#                 sub_table = Table([[str(mark_value) if mark_value is not None else '-', grade]], colWidths=[14, 14], hAlign='CENTER')
#                 sub_table.setStyle(TableStyle([
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                 ]))
#                 row.append(sub_table)
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             overall_grade = get_grade(average_marks)
#             division, total_points = get_division(grades_for_division)
#             row.extend([total_marks if total_marks > 0 else '-', f"{average_marks:.2f}" if average_marks > 0 else '-',
#                         overall_grade, str(i), division, total_points if total_points > 0 else '-'])
#             overall_data.append(row)

#         total_columns = len(overall_data[0])
#         available_width = A4[0] - 30
#         base_width = available_width / total_columns
#         col_widths = ([base_width * 0.5] + [base_width * 2.5] + [base_width * 0.5] + [base_width * 1.8] + 
#                       [base_width * 0.9] * len(subjects) + [base_width * 0.6] * 6)

#         overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#         overall_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 5),
#             ('LEADING', (0, 0), (-1, -1), 6),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ]))
#         elements.append(KeepTogether(overall_table))
#         elements.append(Spacer(1, 4))

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals):
#             student_elements = []
            
#             header_data = []
#             academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=1.8*cm, height=1.8*cm)
#                     icon.drawHeight = 1.8*cm
#                     icon.drawWidth = 1.8*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Report for {student.fullName or 'Unnamed Student'} - {examination_name.exam_name}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     logger.error(f"Error loading DisplayModel image for student {student.fullName}: {e}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Report for {student.fullName or 'Unnamed Student'} - {examination_name.exam_name}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"Report for {student.fullName or 'Unnamed Student'} - {examination_name.exam_name}", header_style),
#                     Spacer(1, 2),
#                     Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                 ]])

#             header_table = Table(header_data, colWidths=[2.8*cm, A4[0]-45-2.8*cm])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                 ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                 ('LEFTPADDING', (0, 0), (0, 0), 8),
#                 ('RIGHTPADDING', (1, 0), (1, 0), 8),
#             ]))
#             student_elements.append(header_table)
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph(f"Student Name: {student.fullName or 'Unnamed'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Index Number: {student.indexNumber or '-'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Class: {teacherclass.ClassName.class_name}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_marks = student.marks.filter(teacherclass=teacherclass, subject__in=subjects, examinationname=examination_name)
#             teacher_names = set()
#             for mark in student_marks:
#                 if mark.user:
#                     teacher_name = teacher_map.get(mark.user_id, mark.user.username)
#                     teacher_names.add(teacher_name)
#             teachers_display = ', '.join(sorted(teacher_names)) if teacher_names else '-'
#             student_elements.append(Paragraph(f"Data Entered/Modified By: {teachers_display}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph("Academic Performance", body_style))
#             student_data = [['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']]
#             grades_for_division = []
#             for mark in student_marks:
#                 subject = mark.subject
#                 mark_value = mark.marks
#                 grade = get_grade(mark_value)
#                 remark = get_remark(grade)
#                 teacher_name = teacher_map.get(mark.user_id, mark.user.username if mark.user else '-')
#                 student_data.append([subject.nameSubject or 'Unnamed', f"{mark_value:.2f}" if mark_value is not None else '-', grade, teacher_name, remark])
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             if len(student_data) == 1:
#                 student_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#             student_table = Table(student_data, colWidths=[2.3*inch, 0.9*inch, 0.9*inch, 1.4*inch, 0.9*inch], splitByRow=True, repeatRows=1)
#             student_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             student_elements.append(student_table)

#             overall_grade = get_grade(average_marks)
#             division, total_points = get_division(grades_for_division)
#             avg_display = f"{average_marks:.2f}" if average_marks > 0 else '-'
#             summary = f"Position: {i + 1} | Avg: {avg_display} | Total: {total_marks if total_marks > 0 else '-'} | Division: {division} | Points: {total_points if total_points > 0 else '-'}" 
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(summary, body_style))
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph("Fee Report", body_style))
#             student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#             discounts = Discount.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#             payments = PayFee.objects.filter(student=student, fee__in=student_fees.values('fee')).select_related('fee').order_by('-date_paid')
#             student_focus = StudentFocus.objects.filter(student=student).first()
#             initial_payment = Decimal('0.00')
#             if student_focus:
#                 student_registration = StudentRegistration.objects.filter(studentfocus=student_focus).first()
#                 if student_registration and student_registration.initial_payment:
#                     initial_payment = student_registration.initial_payment

#             if not student_fees.exists():
#                 student_elements.append(Paragraph("No fees assigned.", body_style))
#             else:
#                 page_width = A4[0] - 30
#                 col_widths_fees = [0.25 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.15 * page_width]
#                 table_data = [['Fee Name', 'Required', 'Discount', 'Adjusted', 'Paid', 'Balance', 'Status']]
#                 total_required = Decimal('0.00')
#                 total_paid_all = Decimal('0.00')
#                 total_discounted = Decimal('0.00')
#                 total_balance = Decimal('0.00')

#                 for sf in student_fees:
#                     fee = sf.fee
#                     discount = discounts.filter(fee=fee).first()
#                     discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                     adjusted_required = sf.amount_required - discount_amount
#                     total_discounted += discount_amount
#                     total_paid = payments.filter(fee=fee).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#                     balance = adjusted_required - total_paid
#                     status = 'Paid' if balance <= 0 else 'Pending'
#                     payment_timing = "No Payment"
#                     if payments.filter(fee=fee).exists():
#                         latest_payment = payments.filter(fee=fee).order_by('-date_paid').first()
#                         if latest_payment and latest_payment.date_paid:
#                             if latest_payment.date_paid < sf.start_date:
#                                 payment_timing = "In Advance"
#                             elif sf.start_date <= latest_payment.date_paid <= sf.end_date:
#                                 payment_timing = "On Time"
#                             elif latest_payment.date_paid > sf.end_date:
#                                 payment_timing = "After Deadline"
#                     table_data.append([
#                         Paragraph(fee.fee_name, body_style),
#                         Paragraph(f"{sf.amount_required:.2f}", body_style),
#                         Paragraph(f"{discount_amount:.2f}", body_style),
#                         Paragraph(f"{adjusted_required:.2f}", body_style),
#                         Paragraph(f"{total_paid:.2f}", body_style),
#                         Paragraph(f"{balance:.2f}", body_style),
#                         Paragraph(status, body_style)
#                     ])
#                     total_required += adjusted_required
#                     total_paid_all += total_paid
#                     total_balance += balance
#                     total_discounted += discount_amount

#                 table_data.append([
#                     Paragraph('TOTAL', bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_discounted:.2f}", bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_paid_all:.2f}", bold_style),
#                     Paragraph(f"{total_balance:.2f}", bold_style),
#                     Paragraph('', bold_style)
#                 ])

#                 table = Table(table_data, colWidths=col_widths_fees)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                     ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(table)
#                 summary = f"Total Required: {total_required:.2f} | Total Discount: {total_discounted:.2f} | Total Paid: {total_paid_all:.2f} | Total Balance: {total_balance:.2f} | Initial Payment: {initial_payment:.2f}"
#                 student_elements.append(Paragraph(summary, discount_style if total_discounted > 0 else summary_style))

#                 student_elements.append(Spacer(1, 2))
#                 student_elements.append(Paragraph("Payment Records", body_style))
#                 col_widths_payments = [0.25 * page_width, 0.15 * page_width, 0.15 * page_width, 0.25 * page_width, 0.25 * page_width]
#                 payment_data = [['Fee Name', 'Date', 'Amount', 'Payer Account', 'Description']]
#                 for payment in payments:
#                     payment_data.append([
#                         Paragraph(payment.fee.fee_name, body_style),
#                         Paragraph(payment.date_paid.strftime('%Y-%m-%d') if payment.date_paid else '-', body_style),
#                         Paragraph(f"{payment.amount_paid:.2f}", body_style),
#                         Paragraph(payment.payer_account_no or '-', body_style),
#                         Paragraph(payment.description or '-', body_style)
#                     ])
#                 if not payments.exists():
#                     payment_data.append(['No payment records found', '-', '-', '-', '-'])

#                 payment_table = Table(payment_data, colWidths=col_widths_payments)
#                 payment_table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(payment_table)

#             student_elements.append(Spacer(1, 4))
#             student_elements.append(Paragraph("Principal's Signature: _____________________", bold_style))
#             elements.append(KeepTogether(student_elements))
#             elements.append(PageBreak())

#         has_fees = any(StudentFee.objects.filter(student=student, teacherclass=teacherclass).exists() for student in students)
#         if has_fees:
#             elements.append(Spacer(1, 4))
#             elements.append(Paragraph("General Fee Report", subheader_style))
#             elements.append(Spacer(1, 2))
#             for i, student in enumerate(students):
#                 student_elements = []
#                 if i > 0:
#                     student_elements.append(Spacer(1, 4))
#                 has_discount = Discount.objects.filter(student=student, teacherclass=teacherclass).exists()
#                 student_label = f"Student: {student.fullName or 'Unnamed'} (Index: {student.indexNumber or '-'})" + (f" <font color='red'>*Discounted*</font>" if has_discount else "")
#                 student_elements.append(Paragraph(student_label, subheader_style))
#                 student_fees = StudentFee.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#                 discounts = Discount.objects.filter(student=student, teacherclass=teacherclass).select_related('fee')
#                 payments = PayFee.objects.filter(student=student, fee__in=student_fees.values('fee')).select_related('fee').order_by('-date_paid')
#                 student_focus = StudentFocus.objects.filter(student=student).first()
#                 initial_payment = Decimal('0.00')
#                 if student_focus:
#                     student_registration = StudentRegistration.objects.filter(studentfocus=student_focus).first()
#                     if student_registration and student_registration.initial_payment:
#                         initial_payment = student_registration.initial_payment

#                 if not student_fees.exists():
#                     student_elements.append(Paragraph("No fees assigned.", body_style))
#                     student_elements.append(Spacer(1, 4))
#                     elements.append(KeepTogether(student_elements))
#                     continue

#                 page_width = A4[0] - 30
#                 col_widths_fees = [0.25 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.12 * page_width, 0.15 * page_width]
#                 table_data = [['Fee Name', 'Required', 'Discount', 'Adjusted', 'Paid', 'Balance', 'Status']]
#                 total_required = Decimal('0.00')
#                 total_paid_all = Decimal('0.00')
#                 total_discounted = Decimal('0.00')
#                 total_balance = Decimal('0.00')

#                 for sf in student_fees:
#                     fee = sf.fee
#                     discount = discounts.filter(fee=fee).first()
#                     discount_amount = discount.discount_amount if discount else Decimal('0.00')
#                     adjusted_required = sf.amount_required - discount_amount
#                     total_discounted += discount_amount
#                     total_paid = payments.filter(fee=fee).aggregate(total=Sum('amount_paid'))['total'] or Decimal('0.00')
#                     balance = adjusted_required - total_paid
#                     status = 'Paid' if balance <= 0 else 'Pending'
#                     payment_timing = "No Payment"
#                     if payments.filter(fee=fee).exists():
#                         latest_payment = payments.filter(fee=fee).order_by('-date_paid').first()
#                         if latest_payment and latest_payment.date_paid:
#                             if latest_payment.date_paid < sf.start_date:
#                                 payment_timing = "In Advance"
#                             elif sf.start_date <= latest_payment.date_paid <= sf.end_date:
#                                 payment_timing = "On Time"
#                             elif latest_payment.date_paid > sf.end_date:
#                                 payment_timing = "After Deadline"
#                     table_data.append([
#                         Paragraph(fee.fee_name, body_style),
#                         Paragraph(f"{sf.amount_required:.2f}", body_style),
#                         Paragraph(f"{discount_amount:.2f}", body_style),
#                         Paragraph(f"{adjusted_required:.2f}", body_style),
#                         Paragraph(f"{total_paid:.2f}", body_style),
#                         Paragraph(f"{balance:.2f}", body_style),
#                         Paragraph(status, body_style)
#                     ])
#                     total_required += adjusted_required
#                     total_paid_all += total_paid
#                     total_balance += balance
#                     total_discounted += discount_amount

#                 table_data.append([
#                     Paragraph('TOTAL', bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_discounted:.2f}", bold_style),
#                     Paragraph(f"{total_required:.2f}", bold_style),
#                     Paragraph(f"{total_paid_all:.2f}", bold_style),
#                     Paragraph(f"{total_balance:.2f}", bold_style),
#                     Paragraph('', bold_style)
#                 ])

#                 table = Table(table_data, colWidths=col_widths_fees)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor('#f0f4f8')),
#                     ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
#                     ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d0d9e5')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(table)
#                 summary = f"Total Required: {total_required:.2f} | Total Discount: {total_discounted:.2f} | Total Paid: {total_paid_all:.2f} | Total Balance: {total_balance:.2f} | Initial Payment: {initial_payment:.2f}"
#                 student_elements.append(Paragraph(summary, discount_style if total_discounted > 0 else summary_style))

#                 student_elements.append(Spacer(1, 2))
#                 student_elements.append(Paragraph("Payment Records", body_style))
#                 col_widths_payments = [0.25 * page_width, 0.15 * page_width, 0.15 * page_width, 0.25 * page_width, 0.25 * page_width]
#                 payment_data = [['Fee Name', 'Date', 'Amount', 'Payer Account', 'Description']]
#                 for payment in payments:
#                     payment_data.append([
#                         Paragraph(payment.fee.fee_name, body_style),
#                         Paragraph(payment.date_paid.strftime('%Y-%m-%d') if payment.date_paid else '-', body_style),
#                         Paragraph(f"{payment.amount_paid:.2f}", body_style),
#                         Paragraph(payment.payer_account_no or '-', body_style),
#                         Paragraph(payment.description or '-', body_style)
#                     ])
#                 if not payments.exists():
#                     payment_data.append(['No payment records found', '-', '-', '-', '-'])

#                 payment_table = Table(payment_data, colWidths=col_widths_payments)
#                 payment_table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a69bd')),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 9),
#                     ('FONTSIZE', (0, 1), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f4f8')),
#                     ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                     ('LEFTPADDING', (0, 0), (-1, -1), 5),
#                     ('RIGHTPADDING', (0, 0), (-1, -1), 5),
#                     ('WORDWRAP', (0, 1), (-1, -1), 'CJK')
#                 ]))
#                 student_elements.append(payment_table)
#                 student_elements.append(Spacer(1, 4))
#                 elements.append(KeepTogether(student_elements))

#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     try:
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'Combined report generated successfully!')
#         return response
#     except Exception as e:
#         logger.error(f"Error generating PDF: {str(e)}")
#         messages.error(request, f"Error generating PDF: {str(e)}")
#         return redirect('all_student_marks')




# @csrf_exempt
# @login_required
# def download_ca_result_pdf(request, class_id, grade_id, report_id=None):
#     exams = request.POST.getlist('exams')
#     if not exams:
#         messages.error(request, "No examinations selected.")
#         return redirect('all_student_marks')

#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id else DisplayModel.objects.filter(user=request.user).first()
#     subjects = Subject.objects.filter(id__in=RequiredSubject.objects.filter(user=request.user, level='Alevel' if grading.is_advance else 'Olevel').values_list('subject_id', flat=True), user=request.user).order_by('nameSubject')
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related('marks')
#     examination_names = ExaminationName.objects.filter(id__in=exams, user=request.user)

#     # Define grading thresholds
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
#     exam_suffix = "_".join(examination_names.values_list('exam_name', flat=True)).replace(' ', '_')
#     filename = f"ca_result_{teacherclass.ClassName or 'Unnamed_Class'}_{exam_suffix}.pdf"
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
#     header_text = display.header if display else f"CA Based Results for {teacherclass.ClassName or 'Unnamed Class'} - {', '.join(examination_names.values_list('exam_name', flat=True))}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(display.body if display else f"Continuous Assessment Summary - {teacherclass.ClassName}", subheader_style))
#     elements.append(Spacer(1, 8))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.5*cm))
#         except Exception as e:
#             print(f"Error loading DisplayModel image: {e}")

#     if not students.exists() or not subjects.exists() or not examination_names.exists():
#         elements.append(Paragraph("No data available for this class or examinations.", body_style))
#     else:
#         # Aggregate student data
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname__in=examination_names)),
#             average_marks=Avg('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname__in=examination_names))
#         ).select_related('teacherclass')
#         student_data = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             marks_list = []
#             grades_for_division = []
#             for subject in subjects:
#                 total = Mark.objects.filter(student=student, subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total'] or 0
#                 grade = get_grade(total)
#                 teacher_names = []
#                 marks = Mark.objects.filter(student=student, subject=subject, examinationname__in=examination_names)
#                 for mark in marks:
#                     if mark.user:
#                         try:
#                             teacher_name = mark.user.teacher_profile.first().teacherName or mark.user.username if mark.user.teacher_profile.exists() else mark.user.username
#                             teacher_names.append(teacher_name)
#                         except Exception:
#                             teacher_names.append('-')
#                 teachers_display = ', '.join(set(teacher_names)) if teacher_names else '-'
#                 marks_list.append({
#                     'subject_id': subject.id,
#                     'subject_name': subject.nameSubject,
#                     'mark': total,
#                     'grade': grade,
#                     'is_excluded': subject.id in exclude_subjects,
#                     'teacher_name': teachers_display
#                 })
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
#         elements.append(Paragraph("CA Based Academic Results", subheader_style))
#         header = ['Pos', 'Student Name', 'Sex', 'Index Number'] + [s.nameSubject for s in subjects] + ['Total', 'Avg', 'Grade', 'Div', 'Pts']
#         table_data = [header]
#         for i, student in enumerate(student_data, 1):
#             row = [str(i), student['fullName'], student['sex'], student['indexNumber']]
#             for subject in subjects:
#                 mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                 if mark_info:
#                     sub_table = Table([[str(mark_info['mark']) if mark_info['mark'] is not None else '-', mark_info['grade']]],
#                                      colWidths=[15, 15], hAlign='CENTER')
#                     sub_table.setStyle(TableStyle([
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTSIZE', (0, 0), (-1, -1), 6),
#                         ('LEADING', (0, 0), (-1, -1), 8),
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
#         num_subjects = len(subjects)
#         fixed_col_widths = {'pos': 25, 'name': 95, 'sex': 25, 'index': 60, 'total': 38, 'avg': 38, 'grade': 32, 'div': 25, 'pts': 25}
#         total_fixed_width = sum(fixed_col_widths.values())
#         subject_col_width = (available_width - total_fixed_width) / num_subjects if num_subjects > 0 else 0
#         col_widths = ([fixed_col_widths['pos'], fixed_col_widths['name'], fixed_col_widths['sex'], fixed_col_widths['index']] +
#                       [subject_col_width] * num_subjects +
#                       [fixed_col_widths['total'], fixed_col_widths['avg'], fixed_col_widths['grade'], fixed_col_widths['div'], fixed_col_widths['pts']])

#         summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#         summary_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTSIZE', (0, 0), (-1, -1), 7),
#         ]))
#         elements.append(KeepTogether(summary_table))
#         elements.append(Spacer(1, 10))

#         # Individual Student Reports
#         for student in student_data:
#             elements.append(PageBreak())
#             header_data = []
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=2*cm, height=2*cm)
#                     icon.drawHeight = 2*cm
#                     icon.drawWidth = 2*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"CA Based Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     print(f"Error loading DisplayModel image: {e}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"CA Based Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"CA Based Student Report for {teacherclass.ClassName}", header_style),
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

#             elements.append(Paragraph("CA Based Academic Performance", body_style))
#             marks_header = ['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']
#             marks_table_data = [marks_header]
#             for mark_info in student['marks']:
#                 remark = get_remark(mark_info['grade'])
#                 marks_table_data.append([
#                     mark_info['subject_name'],
#                     f"{mark_info['mark']:.2f}" if mark_info['mark'] is not None else '-',
#                     mark_info['grade'],
#                     mark_info['teacher_name'],
#                     remark
#                 ])
#             if len(marks_table_data) == 1:
#                 marks_table_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#             marks_table = Table(marks_table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], repeatRows=1)
#             marks_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 7),
#             ]))
#             elements.append(marks_table)
#             elements.append(Spacer(1, 12))

#             summary_data = [
#                 [f"Total Marks: {student['total_marks']:.2f}" if student['total_marks'] > 0 else 'Total Marks: -',
#                  f"Average: {student['average_marks']:.2f}" if student['average_marks'] > 0 else 'Average: -',
#                  f"Overall Grade: {student['grade']}"],
#                 [f"Division: {student['division']}",
#                  f"Total Points: {student['total_points'] if student['total_points'] > 0 else '-'}",
#                  f"Position in Class: {i}"]
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

#             elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#     messages.success(request, 'CA based results report generated successfully!')
#     return response

# @csrf_exempt
# @login_required
# def download_final_result_pdf(request, class_id, grade_id, report_id=None):
#     exams = request.POST.getlist('exams')
#     if not exams:
#         messages.error(request, "No examinations selected.")
#         return redirect('all_student_marks')

#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     display = DisplayModel.objects.filter(id=report_id, user=request.user).first() if report_id else DisplayModel.objects.filter(user=request.user).first()
#     subjects = Subject.objects.filter(id__in=RequiredSubject.objects.filter(user=request.user, level='Alevel' if grading.is_advance else 'Olevel').values_list('subject_id', flat=True), user=request.user).order_by('nameSubject')
#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related('marks')
#     examination_names = ExaminationName.objects.filter(id__in=exams, user=request.user)

#     # Define grading thresholds
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
#     exam_suffix = "_".join(examination_names.values_list('exam_name', flat=True)).replace(' ', '_')
#     filename = f"final_result_{teacherclass.ClassName or 'Unnamed_Class'}_{exam_suffix}.pdf"
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
#     header_text = display.header if display else f"Final Results for {teacherclass.ClassName or 'Unnamed Class'} - {', '.join(examination_names.values_list('exam_name', flat=True))}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(display.body if display else f"Final Assessment Summary - {teacherclass.ClassName}", subheader_style))
#     elements.append(Spacer(1, 8))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.5*cm))
#         except Exception as e:
#             print(f"Error loading DisplayModel image: {e}")

#     if not students.exists() or not subjects.exists() or not examination_names.exists():
#         elements.append(Paragraph("No data available for this class or examinations.", body_style))
#     else:
#         # Aggregate student data
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname__in=examination_names)),
#             average_marks=Avg('marks__marks', filter=models_Q(marks__subject__in=subjects, marks__examinationname__in=examination_names))
#         ).select_related('teacherclass')
#         student_data = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             marks_list = []
#             grades_for_division = []
#             for subject in subjects:
#                 avg = Mark.objects.filter(student=student, subject=subject, examinationname__in=examination_names).aggregate(avg=Avg('marks'))['avg'] or 0
#                 avg = round(avg, 2)
#                 grade = get_grade(avg)
#                 teacher_names = []
#                 marks = Mark.objects.filter(student=student, subject=subject, examinationname__in=examination_names)
#                 for mark in marks:
#                     if mark.user:
#                         try:
#                             teacher_name = mark.user.teacher_profile.first().teacherName or mark.user.username if mark.user.teacher_profile.exists() else mark.user.username
#                             teacher_names.append(teacher_name)
#                         except Exception:
#                             teacher_names.append('-')
#                 teachers_display = ', '.join(set(teacher_names)) if teacher_names else '-'
#                 marks_list.append({
#                     'subject_id': subject.id,
#                     'subject_name': subject.nameSubject,
#                     'mark': avg,
#                     'grade': grade,
#                     'is_excluded': subject.id in exclude_subjects,
#                     'teacher_name': teachers_display
#                 })
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
#         elements.append(Paragraph("Final Academic Results (Average)", subheader_style))
#         header = ['Pos', 'Student Name', 'Sex', 'Index Number'] + [s.nameSubject for s in subjects] + ['Total', 'Avg', 'Grade', 'Div', 'Pts']
#         table_data = [header]
#         for i, student in enumerate(student_data, 1):
#             row = [str(i), student['fullName'], student['sex'], student['indexNumber']]
#             for subject in subjects:
#                 mark_info = next((m for m in student['marks'] if m['subject_id'] == subject.id), None)
#                 if mark_info:
#                     sub_table = Table([[str(mark_info['mark']) if mark_info['mark'] is not None else '-', mark_info['grade']]],
#                                      colWidths=[15, 15], hAlign='CENTER')
#                     sub_table.setStyle(TableStyle([
#                         ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                         ('FONTSIZE', (0, 0), (-1, -1), 6),
#                         ('LEADING', (0, 0), (-1, -1), 8),
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
#         num_subjects = len(subjects)
#         fixed_col_widths = {'pos': 25, 'name': 95, 'sex': 25, 'index': 60, 'total': 38, 'avg': 38, 'grade': 32, 'div': 25, 'pts': 25}
#         total_fixed_width = sum(fixed_col_widths.values())
#         subject_col_width = (available_width - total_fixed_width) / num_subjects if num_subjects > 0 else 0
#         col_widths = ([fixed_col_widths['pos'], fixed_col_widths['name'], fixed_col_widths['sex'], fixed_col_widths['index']] +
#                       [subject_col_width] * num_subjects +
#                       [fixed_col_widths['total'], fixed_col_widths['avg'], fixed_col_widths['grade'], fixed_col_widths['div'], fixed_col_widths['pts']])

#         summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
#         summary_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTSIZE', (0, 0), (-1, -1), 7),
#         ]))
#         elements.append(KeepTogether(summary_table))
#         elements.append(Spacer(1, 10))

#         # Individual Student Reports
#         for student in student_data:
#             elements.append(PageBreak())
#             header_data = []
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=2*cm, height=2*cm)
#                     icon.drawHeight = 2*cm
#                     icon.drawWidth = 2*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Final Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     print(f"Error loading DisplayModel image: {e}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Final Student Report for {teacherclass.ClassName}", header_style),
#                         Spacer(1, 4),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName} | Academic Year: {datetime.now().year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"Final Student Report for {teacherclass.ClassName}", header_style),
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

#             elements.append(Paragraph("Final Academic Performance (Average)", body_style))
#             marks_header = ['Subject', 'Mark', 'Grade', 'Teacher', 'Remarks']
#             marks_table_data = [marks_header]
#             for mark_info in student['marks']:
#                 remark = get_remark(mark_info['grade'])
#                 marks_table_data.append([
#                     mark_info['subject_name'],
#                     f"{mark_info['mark']:.2f}" if mark_info['mark'] is not None else '-',
#                     mark_info['grade'],
#                     mark_info['teacher_name'],
#                     remark
#                 ])
#             if len(marks_table_data) == 1:
#                 marks_table_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#             marks_table = Table(marks_table_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1.5*inch, 1*inch], repeatRows=1)
#             marks_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 7),
#             ]))
#             elements.append(marks_table)
#             elements.append(Spacer(1, 12))

#             summary_data = [
#                 [f"Total Marks: {student['total_marks']:.2f}" if student['total_marks'] > 0 else 'Total Marks: -',
#                  f"Average: {student['average_marks']:.2f}" if student['average_marks'] > 0 else 'Average: -',
#                  f"Overall Grade: {student['grade']}"],
#                 [f"Division: {student['division']}",
#                  f"Total Points: {student['total_points'] if student['total_points'] > 0 else '-'}",
#                  f"Position in Class: {i}"]
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

#             elements.append(Paragraph("Principal's Signature: _____________________", bold_style))

#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#     messages.success(request, 'Final results report generated successfully!')
#     return response


    
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import get_object_or_404, redirect
# from django.contrib import messages
# from django.views.decorators.csrf import csrf_exempt
# from reportlab.lib.pagesizes import A4
# from reportlab.lib import colors
# from reportlab.lib.units import cm
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from django.db.models import Sum, Avg, Q as models_Q
# from django.db.models import Prefetch
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# @csrf_exempt
# @login_required
# def download_ca_result_financial_pdf(request, class_id, grade_id):
#     exam_ids = request.POST.getlist('exams')
#     if not exam_ids:
#         messages.error(request, "No examinations selected.")
#         return redirect('all_student_marks')

#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     examination_names = ExaminationName.objects.filter(id__in=exam_ids, user=request.user)
#     if not examination_names.exists():
#         messages.error(request, "No examinations found for the selected IDs.")
#         return redirect('all_student_marks')

#     display = DisplayModel.objects.filter(user=request.user).first()
#     creator = getattr(request, 'creator', request.user)
#     if not creator:
#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by or request.user
#         except Teacher.DoesNotExist:
#             messages.error(request, "Your account is not linked to a valid teacher profile.")
#             return redirect('teacher_dashboard')

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subject_ids = required_subjects.values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=subject_ids, user=request.user).order_by('nameSubject')
#     mark_filter = models_Q(marks__subject__in=subjects, marks__examinationname__in=examination_names)

#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects, examinationname__in=examination_names).select_related('subject', 'examinationname', 'user')),
#         Prefetch('assigned_fees', queryset=StudentFee.objects.filter(teacherclass=teacherclass).select_related('fee')),
#         Prefetch('payfee', queryset=PayFee.objects.filter(fee__teacherclass=teacherclass).select_related('fee')),
#         Prefetch('discount_set', queryset=Discount.objects.filter(teacherclass=teacherclass).select_related('fee'))
#     )

#     all_marks = Mark.objects.filter(teacherclass=teacherclass, subject__in=subjects, examinationname__in=examination_names).select_related('user')
#     user_ids = {mark.user_id for mark in all_marks if mark.user_id}
#     teacher_map = {teacher.user_id: teacher.teacherName for teacher in Teacher.objects.filter(user__in=user_ids)}

#     response = HttpResponse(content_type='application/pdf')
#     exam_suffix = "_".join(examination_names.values_list('exam_name', flat=True)).replace(' ', '_')
#     filename = f"ca_result_financial_{teacherclass.ClassName.class_name or 'Unnamed_Class'}_{exam_suffix}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=8)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#     body_style.fontSize = 6

#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     if grading.is_advance:
#         exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject_id', flat=True))
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D',
#             grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#     else:
#         exclude_subjects = set()
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#     def get_grade(mark):
#         if mark is None:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_remark(grade):
#         remark_map = {
#             'A': 'Excellent', 'B': 'Very Good', 'C': 'Good', 'D': 'Pass',
#             'E': 'Poor', 'S': 'Subsidiary', 'F': 'Fail', '-': '-'
#         }
#         return remark_map.get(grade, '-')

#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

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

#     header_text = display.header if display else f"CA-Based Academic and Financial Report for {teacherclass.ClassName.class_name or 'Unnamed Class'}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 2))
#     academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#     elements.append(Paragraph(display.body if display else f"Combined CA Marks and Financial Report - {teacherclass.ClassName.class_name} ({academic_year})", subheader_style))
#     elements.append(Spacer(1, 2))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.2*cm))
#         except Exception as e:
#             logger.error(f"Error loading DisplayModel image: {e}")

#     if not students.exists() or not subjects.exists() or not examination_names.exists():
#         elements.append(Paragraph("No data available for this class or examinations.", body_style))
#     else:
#         elements.append(Paragraph("CA-Based Academic Results", subheader_style))
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=mark_filter),
#             average_marks=Avg('marks__marks', filter=mark_filter)
#         )
#         student_totals = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             grades = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total']
#                 grade = get_grade(mark)
#                 grades.append(grade)
#             has_valid_marks = any(grade != '-' for grade in grades)
#             student_totals.append((student, total_marks, average_marks, has_valid_marks))

#         student_totals.sort(key=lambda x: (-x[3], -x[2]))

#         overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] +
#                         [s.nameSubject for s in subjects] +
#                         ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals, 1):
#             row = [str(i), student.fullName or 'Unnamed', student.sex or '-', student.indexNumber or '-']
#             grades_for_division = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total']
#                 grade = get_grade(mark)
#                 sub_table = Table([[str(mark) if mark is not None else '-', grade]], colWidths=[14, 14], hAlign='CENTER')
#                 sub_table.setStyle(TableStyle([
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                 ]))
#                 row.append(sub_table)
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             overall_grade = get_grade(total_marks)
#             division, total_points = get_division(grades_for_division)
#             row.extend([total_marks if total_marks > 0 else '-', f"{average_marks:.2f}" if average_marks > 0 else '-',
#                         overall_grade, str(i), division, total_points if total_points > 0 else '-'])
#             overall_data.append(row)

#         total_columns = len(overall_data[0])
#         available_width = A4[0] - 30
#         base_width = available_width / total_columns
#         col_widths = ([base_width * 0.5] + [base_width * 2.5] + [base_width * 0.5] + [base_width * 1.8] +
#                       [base_width * 0.9] * len(subjects) + [base_width * 0.6] * 6)

#         overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#         overall_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 5),
#             ('LEADING', (0, 0), (-1, -1), 6),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ]))
#         elements.append(KeepTogether(overall_table))
#         elements.append(Spacer(1, 4))

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals):
#             student_elements = []
#             header_data = []
#             academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=1.8*cm, height=1.8*cm)
#                     icon.drawHeight = 1.8*cm
#                     icon.drawWidth = 1.8*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"CA-Based Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     logger.error(f"Error loading DisplayModel image for student {student.fullName}: {e}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"CA-Based Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"CA-Based Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                     Spacer(1, 2),
#                     Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                 ]])

#             header_table = Table(header_data, colWidths=[2.8*cm, A4[0]-45-2.8*cm])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                 ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                 ('LEFTPADDING', (0, 0), (0, 0), 8),
#                 ('RIGHTPADDING', (1, 0), (1, 0), 8),
#             ]))
#             student_elements.append(header_table)
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph(f"Student Name: {student.fullName or 'Unnamed'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Index Number: {student.indexNumber or '-'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Class: {teacherclass.ClassName.class_name}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_marks = student.marks.filter(teacherclass=teacherclass, subject__in=subjects, examinationname__in=examination_names)
#             teacher_names = set()
#             for mark in student_marks:
#                 if mark.user:
#                     teacher_name = teacher_map.get(mark.user_id, mark.user.username)
#                     teacher_names.add(teacher_name)
#             teachers_display = ', '.join(sorted(teacher_names)) if teacher_names else '-'
#             student_elements.append(Paragraph(f"Data Entered/Modified By: {teachers_display}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph("CA-Based Academic Performance", body_style))
#             student_data = [['Subject', 'Total Marks', 'Grade', 'Teacher', 'Remarks']]
#             grades_for_division = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total']
#                 grade = get_grade(mark)
#                 remark = get_remark(grade)
#                 mark_obj = student.marks.filter(subject=subject, examinationname__in=examination_names).first()
#                 teacher_name = teacher_map.get(mark_obj.user_id, mark_obj.user.username) if mark_obj and mark_obj.user else '-'
#                 student_data.append([
#                     subject.nameSubject or 'Unnamed',
#                     f"{mark:.2f}" if mark is not None else '-',
#                     grade,
#                     teacher_name,
#                     remark
#                 ])
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             if len(student_data) == 1:
#                 student_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#             student_table = Table(student_data, colWidths=[2.3*inch, 0.9*inch, 0.9*inch, 1.4*inch, 0.9*inch], splitByRow=True, repeatRows=1)
#             student_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             student_elements.append(student_table)

#             overall_grade = get_grade(total_marks)
#             division, total_points = get_division(grades_for_division)
#             avg_display = f"{average_marks:.2f}" if average_marks > 0 else '-'
#             summary = f"Position: {i + 1} | Avg: {avg_display} | Total: {total_marks if total_marks > 0 else '-'} | Division: {division} | Points: {total_points if total_points > 0 else '-'}" 
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(summary, body_style))

#             student_elements.append(Spacer(1, 4))
#             student_elements.append(Paragraph("Financial Details", subheader_style))
#             student_elements.append(Spacer(1, 2))
#             fee_data = [['Fee Name', 'Amount Required', 'Amount Paid', 'Balance', 'Discount']]
#             total_required = 0
#             total_paid = 0
#             total_discount = 0
#             for student_fee in student.assigned_fees.all():
#                 amount_required = student_fee.amount_required or 0
#                 fee_payments = student.payfee.filter(fee=student_fee.fee)
#                 amount_paid = sum(payment.amount_paid or 0 for payment in fee_payments)
#                 discounts = student.discount_set.filter(fee=student_fee.fee)
#                 discount_amount = sum(discount.discount_amount or 0 for discount in discounts)
#                 balance = amount_required - amount_paid - discount_amount
#                 total_required += amount_required
#                 total_paid += amount_paid
#                 total_discount += discount_amount
#                 fee_data.append([
#                     student_fee.fee.fee_name or 'Unnamed Fee',
#                     f"{amount_required:.2f}",
#                     f"{amount_paid:.2f}",
#                     f"{balance:.2f}",
#                     f"{discount_amount:.2f}" if discount_amount > 0 else '-'
#                 ])

#             if len(fee_data) == 1:
#                 fee_data.append(['No fees assigned', '-', '-', '-', '-'])
#             else:
#                 fee_data.append([
#                     'Total',
#                     f"{total_required:.2f}",
#                     f"{total_paid:.2f}",
#                     f"{total_required - total_paid - total_discount:.2f}",
#                     f"{total_discount:.2f}" if total_discount > 0 else '-'
#                 ])

#             fee_table = Table(fee_data, colWidths=[2.3*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch], splitByRow=True, repeatRows=1)
#             fee_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             student_elements.append(fee_table)

#             student_elements.append(Spacer(1, 4))
#             student_elements.append(Paragraph("Principal's Signature: _____________________", bold_style))
#             elements.append(KeepTogether(student_elements))
#             elements.append(PageBreak())

#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     try:
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'CA-Based Academic and Financial report generated successfully!')
#         return response
#     except Exception as e:
#         logger.error(f"Error generating PDF: {str(e)}")
#         messages.error(request, f"Error generating PDF: {str(e)}")
#         return redirect('all_student_marks')

# @csrf_exempt
# @login_required
# def download_final_result_financial_pdf(request, class_id, grade_id):
#     exam_ids = request.POST.getlist('exams')
#     if not exam_ids:
#         messages.error(request, "No examinations selected.")
#         return redirect('all_student_marks')

#     teacherclass = get_object_or_404(TeacherClass, id=class_id, user=request.user, academicclassyear__active_year=True)
#     grading = get_object_or_404(GradingModel, id=grade_id, user=request.user)
#     examination_names = ExaminationName.objects.filter(id__in=exam_ids, user=request.user)
#     if not examination_names.exists():
#         messages.error(request, "No examinations found for the selected IDs.")
#         return redirect('all_student_marks')

#     display = DisplayModel.objects.filter(user=request.user).first()
#     creator = getattr(request, 'creator', request.user)
#     if not creator:
#         try:
#             teacher_profile = Teacher.objects.get(user=request.user)
#             creator = teacher_profile.created_by or request.user
#         except Teacher.DoesNotExist:
#             messages.error(request, "Your account is not linked to a valid teacher profile.")
#             return redirect('teacher_dashboard')

#     level = 'Alevel' if grading.is_advance else 'Olevel'
#     required_subjects = RequiredSubject.objects.filter(user=request.user, level=level)
#     subject_ids = required_subjects.values_list('subject_id', flat=True)
#     subjects = Subject.objects.filter(id__in=subject_ids, user=request.user).order_by('nameSubject')
#     mark_filter = models_Q(marks__subject__in=subjects, marks__examinationname__in=examination_names)

#     students = Student.objects.filter(teacherclass=teacherclass).prefetch_related(
#         Prefetch('marks', queryset=Mark.objects.filter(subject__in=subjects, examinationname__in=examination_names).select_related('subject', 'examinationname', 'user')),
#         Prefetch('assigned_fees', queryset=StudentFee.objects.filter(teacherclass=teacherclass).select_related('fee')),
#         Prefetch('payfee', queryset=PayFee.objects.filter(fee__teacherclass=teacherclass).select_related('fee')),
#         Prefetch('discount_set', queryset=Discount.objects.filter(teacherclass=teacherclass).select_related('fee'))
#     )

#     all_marks = Mark.objects.filter(teacherclass=teacherclass, subject__in=subjects, examinationname__in=examination_names).select_related('user')
#     user_ids = {mark.user_id for mark in all_marks if mark.user_id}
#     teacher_map = {teacher.user_id: teacher.teacherName for teacher in Teacher.objects.filter(user__in=user_ids)}

#     response = HttpResponse(content_type='application/pdf')
#     exam_suffix = "_".join(examination_names.values_list('exam_name', flat=True)).replace(' ', '_')
#     filename = f"final_result_financial_{teacherclass.ClassName.class_name or 'Unnamed_Class'}_{exam_suffix}.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{filename}"'
#     doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=15, leftMargin=15, topMargin=20, bottomMargin=20)
#     elements = []
#     styles = getSampleStyleSheet()
#     header_style = styles['Heading1']
#     subheader_style = styles['Heading2']
#     body_style = styles['BodyText']
#     footer_style = ParagraphStyle(name='Footer', parent=styles['BodyText'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey)
#     bold_style = ParagraphStyle(name='Bold', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=8)
#     header_style.alignment = subheader_style.alignment = body_style.alignment = bold_style.alignment = TA_CENTER
#     body_style.fontSize = 6

#     def add_page_number(canvas, doc):
#         page_num = canvas.getPageNumber()
#         text = f"Page {page_num}"
#         canvas.saveState()
#         canvas.setFont("Helvetica", 8)
#         canvas.setFillColor(colors.grey)
#         canvas.drawCentredString(A4[0]/2, 15, text)
#         canvas.restoreState()

#     if grading.is_advance:
#         exclude_subjects = set(ExcludeSubject.objects.filter(user=request.user).values_list('exclude_subject_id', flat=True))
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D',
#             grading.grade_e: 'E', grading.grade_s: 'S', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'S': 6, 'F': 7, '-': 9}
#     else:
#         exclude_subjects = set()
#         grade_thresholds = {
#             grading.grade_a: 'A', grading.grade_b: 'B', grading.grade_c: 'C', grading.grade_d: 'D', grading.grade_f: 'F'
#         }
#         grade_points = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'F': 5, '-': 9}

#     def get_grade(mark):
#         if mark is None:
#             return '-'
#         for threshold, grade in sorted(grade_thresholds.items(), reverse=True):
#             if mark >= threshold:
#                 return grade
#         return 'F'

#     def get_remark(grade):
#         remark_map = {
#             'A': 'Excellent', 'B': 'Very Good', 'C': 'Good', 'D': 'Pass',
#             'E': 'Poor', 'S': 'Subsidiary', 'F': 'Fail', '-': '-'
#         }
#         return remark_map.get(grade, '-')

#     division_thresholds = [
#         {'max': grading.division_1, 'label': 'I'},
#         {'max': grading.division_2, 'label': 'II'},
#         {'max': grading.division_3, 'label': 'III'},
#         {'max': grading.division_4, 'label': 'IV'},
#         {'max': float('inf'), 'label': '0'}
#     ]

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

#     header_text = display.header if display else f"Final Academic and Financial Report for {teacherclass.ClassName.class_name or 'Unnamed Class'}"
#     elements.append(Paragraph(header_text, header_style))
#     elements.append(Spacer(1, 2))
#     academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#     elements.append(Paragraph(display.body if display else f"Final Results and Financial Report - {teacherclass.ClassName.class_name} ({academic_year})", subheader_style))
#     elements.append(Spacer(1, 2))

#     if display and display.image:
#         try:
#             icon = Image(display.image.path, width=2*cm, height=2*cm)
#             icon.hAlign = 'CENTER'
#             elements.append(icon)
#             elements.append(Spacer(1, 0.2*cm))
#         except Exception as e:
#             logger.error(f"Error loading DisplayModel image: {e}")

#     if not students.exists() or not subjects.exists() or not examination_names.exists():
#         elements.append(Paragraph("No data available for this class or examinations.", body_style))
#     else:
#         elements.append(Paragraph("Final Academic Results", subheader_style))
#         students_marks_evaluation = Student.objects.filter(teacherclass=teacherclass).annotate(
#             total_marks=Sum('marks__marks', filter=mark_filter),
#             average_marks=Avg('marks__marks', filter=mark_filter)
#         )
#         student_totals = []
#         for student in students_marks_evaluation:
#             total_marks = student.total_marks or 0
#             average_marks = student.average_marks or 0
#             grades = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total']
#                 grade = get_grade(mark)
#                 grades.append(grade)
#             has_valid_marks = any(grade != '-' for grade in grades)
#             student_totals.append((student, total_marks, average_marks, has_valid_marks))

#         student_totals.sort(key=lambda x: (-x[3], -x[2]))

#         overall_data = [['S/No', 'Student Name', 'Sex', 'Index No'] +
#                         [s.nameSubject for s in subjects] +
#                         ['Total', 'Avg', 'Grade', 'Pos', 'Div', 'Pts']]

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals, 1):
#             row = [str(i), student.fullName or 'Unnamed', student.sex or '-', student.indexNumber or '-']
#             grades_for_division = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total']
#                 grade = get_grade(mark)
#                 sub_table = Table([[str(mark) if mark is not None else '-', grade]], colWidths=[14, 14], hAlign='CENTER')
#                 sub_table.setStyle(TableStyle([
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                     ('FONTSIZE', (0, 0), (-1, -1), 5),
#                     ('LEADING', (0, 0), (-1, -1), 6),
#                     ('TEXTCOLOR', (1, 0), (1, 0), colors.red if grade == 'F' else colors.black),
#                 ]))
#                 row.append(sub_table)
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             overall_grade = get_grade(total_marks)
#             division, total_points = get_division(grades_for_division)
#             row.extend([total_marks if total_marks > 0 else '-', f"{average_marks:.2f}" if average_marks > 0 else '-',
#                         overall_grade, str(i), division, total_points if total_points > 0 else '-'])
#             overall_data.append(row)

#         total_columns = len(overall_data[0])
#         available_width = A4[0] - 30
#         base_width = available_width / total_columns
#         col_widths = ([base_width * 0.5] + [base_width * 2.5] + [base_width * 0.5] + [base_width * 1.8] +
#                       [base_width * 0.9] * len(subjects) + [base_width * 0.6] * 6)

#         overall_table = Table(overall_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
#         overall_table.setStyle(TableStyle([
#             ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#             ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#             ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#             ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#             ('FONTSIZE', (0, 0), (-1, -1), 5),
#             ('LEADING', (0, 0), (-1, -1), 6),
#             ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#         ]))
#         elements.append(KeepTogether(overall_table))
#         elements.append(Spacer(1, 4))

#         for i, (student, total_marks, average_marks, _) in enumerate(student_totals):
#             student_elements = []
#             header_data = []
#             academic_year = teacherclass.academicclassyear.academic_year_name if teacherclass.academicclassyear else 'N/A'
#             if display and display.image:
#                 try:
#                     icon = Image(display.image.path, width=1.8*cm, height=1.8*cm)
#                     icon.drawHeight = 1.8*cm
#                     icon.drawWidth = 1.8*cm
#                     icon.hAlign = 'LEFT'
#                     header_data.append([icon, [
#                         Paragraph(display.header if display else f"Final Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#                 except Exception as e:
#                     logger.error(f"Error loading DisplayModel image for student {student.fullName}: {e}")
#                     header_data.append(['', [
#                         Paragraph(display.header if display else f"Final Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                         Spacer(1, 2),
#                         Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                     ]])
#             else:
#                 header_data.append(['', [
#                     Paragraph(display.header if display else f"Final Academic and Financial Report for {student.fullName or 'Unnamed Student'}", header_style),
#                     Spacer(1, 2),
#                     Paragraph(display.body if display else f"Class: {teacherclass.ClassName.class_name} | Academic Year: {academic_year}", subheader_style)
#                 ]])

#             header_table = Table(header_data, colWidths=[2.8*cm, A4[0]-45-2.8*cm])
#             header_table.setStyle(TableStyle([
#                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#                 ('ALIGN', (1, 0), (1, 0), 'CENTER'),
#                 ('LEFTPADDING', (0, 0), (0, 0), 8),
#                 ('RIGHTPADDING', (1, 0), (1, 0), 8),
#             ]))
#             student_elements.append(header_table)
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph(f"Student Name: {student.fullName or 'Unnamed'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Index Number: {student.indexNumber or '-'}", bold_style))
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(f"Class: {teacherclass.ClassName.class_name}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_marks = student.marks.filter(teacherclass=teacherclass, subject__in=subjects, examinationname__in=examination_names)
#             teacher_names = set()
#             for mark in student_marks:
#                 if mark.user:
#                     teacher_name = teacher_map.get(mark.user_id, mark.user.username)
#                     teacher_names.add(teacher_name)
#             teachers_display = ', '.join(sorted(teacher_names)) if teacher_names else '-'
#             student_elements.append(Paragraph(f"Data Entered/Modified By: {teachers_display}", bold_style))
#             student_elements.append(Spacer(1, 2))

#             student_elements.append(Paragraph("Final Academic Performance", body_style))
#             student_data = [['Subject', 'Total Marks', 'Grade', 'Teacher', 'Remarks']]
#             grades_for_division = []
#             for subject in subjects:
#                 mark = student.marks.filter(subject=subject, examinationname__in=examination_names).aggregate(total=Sum('marks'))['total']
#                 grade = get_grade(mark)
#                 remark = get_remark(grade)
#                 mark_obj = student.marks.filter(subject=subject, examinationname__in=examination_names).first()
#                 teacher_name = teacher_map.get(mark_obj.user_id, mark_obj.user.username) if mark_obj and mark_obj.user else '-'
#                 student_data.append([
#                     subject.nameSubject or 'Unnamed',
#                     f"{mark:.2f}" if mark is not None else '-',
#                     grade,
#                     teacher_name,
#                     remark
#                 ])
#                 if not grading.is_advance or subject.id not in exclude_subjects:
#                     grades_for_division.append(grade)

#             if len(student_data) == 1:
#                 student_data.append(['No subjects with marks available', '-', '-', '-', '-'])

#             student_table = Table(student_data, colWidths=[2.3*inch, 0.9*inch, 0.9*inch, 1.4*inch, 0.9*inch], splitByRow=True, repeatRows=1)
#             student_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             student_elements.append(student_table)

#             overall_grade = get_grade(total_marks)
#             division, total_points = get_division(grades_for_division)
#             avg_display = f"{average_marks:.2f}" if average_marks > 0 else '-'
#             summary = f"Position: {i + 1} | Avg: {avg_display} | Total: {total_marks if total_marks > 0 else '-'} | Division: {division} | Points: {total_points if total_points > 0 else '-'}" 
#             student_elements.append(Spacer(1, 2))
#             student_elements.append(Paragraph(summary, body_style))

#             student_elements.append(Spacer(1, 4))
#             student_elements.append(Paragraph("Financial Details", subheader_style))
#             student_elements.append(Spacer(1, 2))
#             fee_data = [['Fee Name', 'Amount Required', 'Amount Paid', 'Balance', 'Discount']]
#             total_required = 0
#             total_paid = 0
#             total_discount = 0
#             for student_fee in student.assigned_fees.all():
#                 amount_required = student_fee.amount_required or 0
#                 fee_payments = student.payfee.filter(fee=student_fee.fee)
#                 amount_paid = sum(payment.amount_paid or 0 for payment in fee_payments)
#                 discounts = student.discount_set.filter(fee=student_fee.fee)
#                 discount_amount = sum(discount.discount_amount or 0 for discount in discounts)
#                 balance = amount_required - amount_paid - discount_amount
#                 total_required += amount_required
#                 total_paid += amount_paid
#                 total_discount += discount_amount
#                 fee_data.append([
#                     student_fee.fee.fee_name or 'Unnamed Fee',
#                     f"{amount_required:.2f}",
#                     f"{amount_paid:.2f}",
#                     f"{balance:.2f}",
#                     f"{discount_amount:.2f}" if discount_amount > 0 else '-'
#                 ])

#             if len(fee_data) == 1:
#                 fee_data.append(['No fees assigned', '-', '-', '-', '-'])
#             else:
#                 fee_data.append([
#                     'Total',
#                     f"{total_required:.2f}",
#                     f"{total_paid:.2f}",
#                     f"{total_required - total_paid - total_discount:.2f}",
#                     f"{total_discount:.2f}" if total_discount > 0 else '-'
#                 ])

#             fee_table = Table(fee_data, colWidths=[2.3*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch], splitByRow=True, repeatRows=1)
#             fee_table.setStyle(TableStyle([
#                 ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
#                 ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                 ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                 ('FONTSIZE', (0, 0), (-1, -1), 5),
#                 ('LEADING', (0, 0), (-1, -1), 6),
#                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
#             ]))
#             student_elements.append(fee_table)

#             student_elements.append(Spacer(1, 4))
#             student_elements.append(Paragraph("Principal's Signature: _____________________", bold_style))
#             elements.append(KeepTogether(student_elements))
#             elements.append(PageBreak())

#     elements.append(Spacer(1, 4))
#     elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
#     try:
#         doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
#         messages.success(request, 'Final Academic and Financial report generated successfully!')
#         return response
#     except Exception as e:
#         logger.error(f"Error generating PDF: {str(e)}")
#         messages.error(request, f"Error generating PDF: {str(e)}")
#         return redirect('all_student_marks')

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from .models import TeacherSubject, Student, Mark, ExaminationName, Teacher, StudentSubject
# import pandas as pd
# from django.http import HttpResponse
# from io import BytesIO

# @login_required
# def upload_marks(request, teacher_subject_id):
#     try:
#         teacher_profile = request.user.teacher_profile.get()
#     except Teacher.DoesNotExist:
#         messages.error(request, "Teacher profile not found. Contact your administrator.")
#         return redirect('teacher_dashboard')

#     teacher_subject = get_object_or_404(
#         TeacherSubject,
#         id=teacher_subject_id,
#         teacher=teacher_profile
#     )

#     examination_name_id = request.session.get('selected_examination_id')
#     if not examination_name_id:
#         messages.error(request, "Please select an examination first.")
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     try:
#         examination_name = ExaminationName.objects.get(
#             id=examination_name_id,
#             user=teacher_profile.created_by
#         )
#     except ExaminationName.DoesNotExist:
#         messages.error(request, "Selected examination name is invalid.")
#         if 'selected_examination_id' in request.session:
#             del request.session['selected_examination_id']
#         return redirect('select_examination_name', teacher_subject_id=teacher_subject_id)

#     current_teacher_class = teacher_subject.teacherclass
#     try:
#         academic_class_year = current_teacher_class.academicclassyear
#         if not academic_class_year.active_year:
#             messages.error(request, f"The academic year '{academic_class_year.academic_year_name}' for this class is not active.")
#             return redirect('teacher_dashboard')
#     except AttributeError:
#         messages.error(request, "No academic year associated with this class.")
#         return redirect('teacher_dashboard')

#     student_subjects = StudentSubject.objects.filter(
#         teacherclass=current_teacher_class,
#         subject=teacher_subject.subject,
#         teacherclass__academicclassyear__active_year=True
#     )

#     if student_subjects.exists():
#         student_ids = set()
#         for student_subject in student_subjects:
#             student_ids.update(student_subject.student.values_list('id', flat=True))
#         students = Student.objects.filter(
#             id__in=student_ids,
#             teacherclass=current_teacher_class,
#             teacherclass__academicclassyear__active_year=True
#         ).select_related('user').order_by('fullName')
#     else:
#         students = Student.objects.none()

#     student_marks = {
#         mark.student_id: mark.marks for mark in Mark.objects.filter(
#             teacherclass=current_teacher_class,
#             subject=teacher_subject.subject,
#             examinationname=examination_name,
#             student__in=students,
#             teacherclass__academicclassyear__active_year=True
#         )
#     }

#     saved_marks = Mark.objects.filter(
#         teacherclass=current_teacher_class,
#         subject=teacher_subject.subject,
#         examinationname=examination_name,
#         student__in=students,
#         teacherclass__academicclassyear__active_year=True
#     ).select_related('student').order_by('student__fullName')

#     if request.GET.get('download_template'):
#         # Generate Excel template
#         data = {
#             'Student Name': [student.fullName or 'Unnamed Student' for student in students],
#             'Index Number': [student.indexNumber or 'N/A' for student in students],
#             'Mark': [''] * len(students)  # Empty column for marks
#         }
#         df = pd.DataFrame(data)
        
#         # Create Excel file in memory
#         output = BytesIO()
#         with pd.ExcelWriter(output, engine='openpyxl') as writer:
#             df.to_excel(writer, index=False, sheet_name='Marks')
        
#         # Prepare response
#         output.seek(0)
#         response = HttpResponse(
#             content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#             content=output.read()
#         )
#         filename = f"marks_template_{teacher_subject.subject.nameSubject}_{examination_name.exam_name}.xlsx"
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         return response

#     if request.method == 'POST':
#         if teacher_subject.is_restricted:
#             messages.error(request, "Marks for this subject are restricted.")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         if 'excel_file' not in request.FILES:
#             messages.error(request, "No file uploaded.")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         excel_file = request.FILES['excel_file']
#         if not excel_file.name.endswith(('.xlsx', '.xls')):
#             messages.error(request, "Please upload a valid Excel file (.xlsx or .xls).")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         try:
#             df = pd.read_excel(excel_file)
#             required_columns = ['Student Name', 'Index Number', 'Mark']
#             if not all(col in df.columns for col in required_columns):
#                 messages.error(request, "Excel file must contain 'Student Name', 'Index Number', and 'Mark' columns.")
#                 return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#             # Validate and process marks
#             student_index_map = {student.indexNumber: student for student in students if student.indexNumber}
#             for index, row in df.iterrows():
#                 index_number = str(row['Index Number']).strip()
#                 mark_value = row['Mark']

#                 if pd.isna(mark_value):
#                     continue  # Skip rows with empty marks

#                 try:
#                     mark_value = float(mark_value)
#                     if not (0 <= mark_value <= 100):
#                         raise ValueError("Marks must be between 0 and 100.")
#                 except (ValueError, TypeError):
#                     messages.error(request, f"Invalid mark for Index Number {index_number}: Must be a number between 0 and 100.")
#                     continue

#                 student = student_index_map.get(index_number)
#                 if not student:
#                     messages.error(request, f"No student found with Index Number {index_number}.")
#                     continue

#                 Mark.objects.update_or_create(
#                     teacherclass=current_teacher_class,
#                     subject=teacher_subject.subject,
#                     examinationname=examination_name,
#                     student=student,
#                     defaults={
#                         'marks': mark_value,
#                         'user': request.user
#                     }
#                 )

#             messages.success(request, "Marks uploaded successfully!")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#         except Exception as e:
#             messages.error(request, f"Error processing Excel file: {str(e)}")
#             return redirect('fill_marks', teacher_subject_id=teacher_subject_id)

#     context = {
#         'teacher_subject': teacher_subject,
#         'students': students,
#         'student_marks': student_marks,
#         'saved_marks': saved_marks,
#         'examination_name': examination_name,
#         'academic_class_year': academic_class_year,
#         'current_teacher_class': current_teacher_class,
#     }
#     return render(request, 'fill_marks.html', context)




# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import HttpResponseForbidden
# from .models import Teacher, TeacherSubject, TeacherClass, Subject, Student, Mark, DisplayModel, ExaminationName, EmailVerificationOTP, StudentSubject,  GradingModel
# from django.db.models import Count, Avg
# from .forms import TeacherSubjectForm
# import json
# from collections import defaultdict, Counter
# from datetime import datetime
# from attendance.models import StaffAttendance
# def determine_grade(mark, grading):
#     if grading.is_advance:
#         if mark >= grading.grade_a: return 'A'
#         elif mark >= grading.grade_b: return 'B'
#         elif mark >= grading.grade_c: return 'C'
#         elif mark >= grading.grade_d: return 'D'
#         elif mark >= grading.grade_e: return 'E'
#         elif mark >= grading.grade_s: return 'S'
#         else: return 'F'
#     else:
#         if mark >= grading.grade_a: return 'A'
#         elif mark >= grading.grade_b: return 'B'
#         elif mark >= grading.grade_c: return 'C'
#         elif mark >= grading.grade_d: return 'D'
#         else: return 'F'
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import HttpResponseForbidden
# from .models import Teacher, TeacherSubject, TeacherClass, Subject, Student, Mark, DisplayModel, ExaminationName, EmailVerificationOTP, StudentSubject, GradingModel
# from django.db.models import Count, Avg
# from .forms import TeacherSubjectForm
# import json
# from collections import defaultdict, Counter
# from datetime import datetime, date, timedelta
# import calendar  # Added for monthrange
# from attendance.models import StaffAttendance
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import HttpResponseForbidden
# from .models import Teacher, TeacherSubject, TeacherClass, Subject, Student, Mark, DisplayModel, ExaminationName, EmailVerificationOTP, StudentSubject, GradingModel
# from django.db.models import Count, Avg
# from .forms import TeacherSubjectForm
# import json
# from collections import defaultdict, Counter
# from datetime import datetime, date, timedelta
# import calendar
# from attendance.models import StaffAttendance
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import HttpResponseForbidden
# from .models import Teacher, TeacherSubject, TeacherClass, Subject, Student, Mark, DisplayModel, ExaminationName, EmailVerificationOTP, StudentSubject, GradingModel
# from django.db.models import Count, Avg
# from .forms import TeacherSubjectForm
# import json
# from collections import defaultdict, Counter
# from datetime import datetime, date, timedelta
# import calendar
# from attendance.models import StaffAttendance

# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import JsonResponse
# from .models import Teacher, TeacherSubject, TeacherClass, Subject, Student, Mark, DisplayModel, ExaminationName, EmailVerificationOTP, StudentSubject, GradingModel
# from django.db.models import Count, Avg
# from .forms import TeacherSubjectForm
# import json
# from collections import defaultdict, Counter
# from datetime import datetime, date, timedelta
# import calendar
# from attendance.models import StaffAttendance
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.core.exceptions import ObjectDoesNotExist
# from django.http import HttpResponseForbidden
# from .models import Teacher, TeacherSubject, TeacherClass, Subject, Student, Mark, DisplayModel, ExaminationName, EmailVerificationOTP, StudentSubject, GradingModel
# from django.db.models import Count, Avg
# from .forms import TeacherSubjectForm
# import json
# from collections import defaultdict, Counter
# from datetime import datetime, date, timedelta
# import calendar
# from attendance.models import StaffAttendance

# @login_required
# def teacher_profile(request):
#     # Fetch the current teacher
#     login_teacher = Teacher.objects.get(user=request.user)
#     creator = login_teacher.created_by if login_teacher.created_by else request.user
#     try:
#         teacher = Teacher.objects.get(user=request.user)
#     except ObjectDoesNotExist:
#         messages.error(request, "Teacher profile not found.")
#         return redirect('home')

#     # Check if the user has any verified OTP
#     is_email_verified = EmailVerificationOTP.objects.filter(
#         user=request.user, is_verified=True, purpose='verification'
#     ).exists()

#     # Fetch all ExaminationName for the creator
#     exams = ExaminationName.objects.filter(user=creator).order_by('-id')

#     # Get selected exam from GET parameter, default to latest if exists
#     selected_exam_id = request.GET.get('exam_id')
#     if not selected_exam_id and exams.exists():
#         selected_exam_id = exams.first().id
#     selected_exam = ExaminationName.objects.get(id=selected_exam_id) if selected_exam_id else None

#     # Fetch all TeacherSubject instances for the teacher
#     teacher_subjects = TeacherSubject.objects.filter(
#         teacher=teacher
#     ).select_related('subject', 'teacherclass', 'teacherclass__academicclassyear', 'teacherclass__ClassName')

#     # Get distinct subjects assigned to the teacher
#     subjects = Subject.objects.filter(
#         teachersubject__teacher=teacher
#     ).distinct()

#     # Get assigned classes (using TeacherClass)
#     assigned_classes = TeacherClass.objects.filter(
#         teachersubject__teacher=teacher
#     ).distinct()

#     # Calculate total students using the correct related_name 'subject_enrollments'
#     total_students = Student.objects.filter(
#         subject_enrollments__subject__in=subjects,
#         subject_enrollments__teacherclass__in=assigned_classes
#     ).distinct().count()

#     # Fetch grading for calculations
#     grading = GradingModel.objects.filter(user=creator).last()

#     # Calculate GPA, grade distribution, and student count for each teacher subject (for selected exam)
#     for ts in teacher_subjects:
#         ts.grade_counts = {}
#         ts.gpa = 0.0
#         # Enrolled student count (independent of exam)
#         ts.enrolled_count = Student.objects.filter(
#             subject_enrollments__subject=ts.subject,
#             subject_enrollments__teacherclass=ts.teacherclass
#         ).distinct().count()
#         ts.student_count = 0  # Will be set to marked students for the exam
#         if grading and selected_exam:
#             grade_points = {'A': 1.0, 'B': 2.0, 'C': 3.0, 'D': 4.0, **({'E': 5.0, 'S': 6.0, 'F': 7.0} if grading.is_advance else {'F': 5.0})}
#             marks_qs = Mark.objects.filter(
#                 subject=ts.subject,
#                 teacherclass=ts.teacherclass,
#                 user=request.user,
#                 examinationname=selected_exam
#             )
#             if marks_qs.exists():
#                 marks = marks_qs.values_list('marks', flat=True)
#                 student_ids = marks_qs.values_list('student', flat=True).distinct()
#                 ts.student_count = len(student_ids)
#                 if marks:
#                     grades = [determine_grade(m, grading) for m in marks]
#                     points = [grade_points.get(g, grade_points['F']) for g in grades]
#                     ts.gpa = round(sum(points) / len(points), 2) if points else 0.0
#                     ts.grade_counts = dict(Counter(grades))
#                     # Ensure all grades are present with 0 if missing
#                     all_grades = ['A', 'B', 'C', 'D', 'F'] if not grading.is_advance else ['A', 'B', 'C', 'D', 'E', 'S', 'F']
#                     for g in all_grades:
#                         if g not in ts.grade_counts:
#                             ts.grade_counts[g] = 0
#                     # Sort grade_counts by grade order
#                     ts.grade_counts = {g: ts.grade_counts.get(g, 0) for g in all_grades}
#             else:
#                 all_grades = ['A', 'B', 'C', 'D', 'F'] if not grading.is_advance else ['A', 'B', 'C', 'D', 'E', 'S', 'F']
#                 ts.grade_counts = {g: 0 for g in all_grades}
#         else:
#             ts.gpa = 0.0
#             all_grades = ['A', 'B', 'C', 'D', 'F'] if grading and not grading.is_advance else ['A', 'B', 'C', 'D', 'E', 'S', 'F'] if grading else []
#             ts.grade_counts = {g: 0 for g in all_grades}

#     # Calculate average GPA for the selected exam across all teacher subjects
#     exam_gpa_sum = sum(ts.gpa for ts in teacher_subjects)
#     exam_average_gpa = round(exam_gpa_sum / len(teacher_subjects), 2) if teacher_subjects else 0.0

#     # Calculate average GPA across all exams
#     all_exams_average_gpa = 0.0
#     if exams.exists() and grading:
#         total_gpa_sum = 0.0
#         num_exams_with_data = 0
#         for exam in exams:
#             exam_gpa_sum = 0.0
#             num_subjects_with_data = 0
#             for ts in teacher_subjects:
#                 marks_qs = Mark.objects.filter(
#                     subject=ts.subject,
#                     teacherclass=ts.teacherclass,
#                     user=request.user,
#                     examinationname=exam
#                 )
#                 if marks_qs.exists():
#                     marks = marks_qs.values_list('marks', flat=True)
#                     grades = [determine_grade(m, grading) for m in marks]
#                     points = [grade_points.get(g, grade_points['F']) for g in grades]
#                     exam_subject_gpa = round(sum(points) / len(points), 2) if points else 0.0
#                     exam_gpa_sum += exam_subject_gpa
#                     num_subjects_with_data += 1
#             if num_subjects_with_data > 0:
#                 exam_avg_gpa = exam_gpa_sum / num_subjects_with_data
#                 total_gpa_sum += exam_avg_gpa
#                 num_exams_with_data += 1
#         all_exams_average_gpa = round(total_gpa_sum / num_exams_with_data, 2) if num_exams_with_data > 0 else 0.0

#     # Prepare GPA chart data for selected exam
#     gpa_chart = {
#         'labels': [f"{ts.subject.nameSubject} ({ts.teacherclass.ClassName.class_name})" for ts in teacher_subjects],
#         'data': [float(ts.gpa) for ts in teacher_subjects]
#     }

#     # Get attendance data
#     attendance_records = StaffAttendance.objects.filter(teacher=teacher).order_by('-date')

#     # Create a dict for quick lookup by date
#     attendance_by_date = {att.date: att for att in attendance_records}

#     # Determine date range
#     today = date.today()
#     if attendance_records.exists():
#         min_date = min(att.date for att in attendance_records)
#         max_date = max(att.date for att in attendance_records)
#     else:
#         min_date = today.replace(day=1)  # Start of current month
#         max_date = today

#     # Generate all months in the range (including gaps)
#     current_date = min_date.replace(day=1)
#     monthly_details = []
#     while current_date <= max_date:
#         year = current_date.year
#         month_num = current_date.month
#         month_str = current_date.strftime('%B %Y')
#         _, num_days = calendar.monthrange(year, month_num)

#         days = []
#         present_count = 0
#         absent_count = 0
#         for day_num in range(1, num_days + 1):
#             day_date = date(year, month_num, day_num)
#             att = attendance_by_date.get(day_date)
#             if att:
#                 status = att.status
#                 check_in = att.check_in_time
#                 check_out = att.check_out_time
#                 if status == 'present':
#                     present_count += 1
#                 elif status == 'absent':
#                     absent_count += 1
#             else:
#                 if day_date <= today:
#                     status = 'absent'
#                     check_in = None
#                     check_out = None
#                     absent_count += 1
#                 else:
#                     status = '-'
#                     check_in = None
#                     check_out = None
#             days.append({
#                 'day': day_num,
#                 'date': day_date,
#                 'status': status,
#                 'check_in': check_in,
#                 'check_out': check_out,
#             })

#         monthly_details.append({
#             'month_str': month_str,
#             'year': year,
#             'month_num': month_num,
#             'days': days,
#             'present': present_count,
#             'absent': absent_count,
#             'total': present_count + absent_count,
#         })

#         # Move to next month
#         next_month = month_num + 1
#         next_year = year
#         if next_month > 12:
#             next_month = 1
#             next_year += 1
#         current_date = date(next_year, next_month, 1)

#     # Sort by month descending
#     monthly_details.sort(key=lambda m: datetime.strptime(m['month_str'], '%B %Y'), reverse=True)

#     # Overall counts (from actual records only)
#     overall_present = sum(1 for att in attendance_records if att.status == 'present')
#     overall_absent = sum(1 for att in attendance_records if att.status == 'absent')
#     overall_total = len(attendance_records)

#     attendance = {
#         'present_count': overall_present,
#         'absent_count': overall_absent,
#         'total_days': overall_total,
#         'attendance_data': attendance_records,
#     }

#     # Get latest display (using DisplayModel)
#     display = DisplayModel.objects.filter(user=request.user).last()

#     # Handle POST request for marks
#     if request.method == 'POST':
#         active_teacher_subjects = TeacherSubject.objects.filter(
#             teacher=teacher,
#             teacherclass__academicclassyear__active_year=True
#         ).select_related('subject', 'teacherclass', 'teacherclass__academicclassyear')

#         active_subjects = Subject.objects.filter(
#             teachersubject__teacher=teacher,
#             teachersubject__teacherclass__academicclassyear__active_year=True
#         ).distinct()

#         students = Student.objects.filter(
#             subject_enrollments__subject__in=active_subjects,
#             subject_enrollments__teacherclass__academicclassyear__active_year=True
#         ).distinct().select_related('user').order_by('fullName')

#         student_subject_enrollment = {
#             student.id: {
#                 subject.id: StudentSubject.objects.filter(
#                     student=student,
#                     subject__id=subject.id,
#                     teacherclass__academicclassyear__active_year=True
#                 ).exists()
#                 for subject in active_subjects
#             }
#             for student in students
#         }

#         teacher_subjects_dict = {
#             subject.id: TeacherSubject.objects.filter(
#                 teacher=teacher,
#                 subject=subject,
#                 teacherclass__academicclassyear__active_year=True
#             ).first()
#             for subject in active_subjects
#         }

#         student_marks = {
#             student.id: {
#                 subject.id: Mark.objects.filter(
#                     student=student,
#                     subject=subject,
#                     user=teacher.user,
#                     teacherclass__academicclassyear__active_year=True
#                 ).first()
#                 for subject in active_subjects
#             }
#             for student in students
#         }

#         examination_name_id = request.session.get('selected_examination_id')
#         if not examination_name_id:
#             messages.error(request, "Please select an examination first.")
#             return redirect('select_examination_name', teacher_subject_id=active_teacher_subjects.first().id if active_teacher_subjects.exists() else 0)

#         try:
#             examination_name = ExaminationName.objects.get(
#                 id=examination_name_id,
#                 user=teacher.user
#             )
#         except ExaminationName.DoesNotExist:
#             messages.error(request, "Selected examination name is invalid.")
#             if 'selected_examination_id' in request.session:
#                 del request.session['selected_examination_id']
#             return redirect('select_examination_name', teacher_subject_id=active_teacher_subjects.first().id if active_teacher_subjects.exists() else 0)

#         marks_saved = False
#         for student in students:
#             for subject in active_subjects:
#                 mark_value = request.POST.get(f'marks_{student.id}_{subject.id}')
#                 if mark_value and mark_value.strip():
#                     teacher_subject = teacher_subjects_dict.get(subject.id)
#                     if teacher_subject and not teacher_subject.is_restricted:
#                         try:
#                             mark_value = float(mark_value)
#                             if not (0 <= mark_value <= 100):
#                                 raise ValueError("Marks must be between 0 and 100.")
#                             Mark.objects.update_or_create(
#                                 user=teacher.user,
#                                 student=student,
#                                 subject=subject,
#                                 teacherclass=teacher_subject.teacherclass,
#                                 examinationname=examination_name,
#                                 defaults={'marks': mark_value}
#                             )
#                             marks_saved = True
#                         except ValueError as e:
#                             messages.error(request, f"Invalid mark for {student.fullName or student.user.username} in {subject.nameSubject}: {e}")
#                             return redirect('teacher_dashboard')

#         if marks_saved:
#             messages.success(request, "Marks have been saved successfully!")
#         elif not active_subjects.exists():
#             messages.info(request, "No subjects assigned to you for an active academic year.")

#         context = {
#             'teacher': teacher,
#             'teacher_subjects': active_teacher_subjects,
#             'subjects': active_subjects,
#             'assigned_classes': assigned_classes,
#             'total_students': total_students,
#             'exam_average_gpa': exam_average_gpa,
#             'all_exams_average_gpa': all_exams_average_gpa,
#             'gpa_chart': {
#                 'labels': json.dumps(gpa_chart['labels']),
#                 'data': json.dumps(gpa_chart['data'])
#             },
#             'attendance': attendance,
#             'monthly_attendance': monthly_details,
#             'display': display,
#             'is_verified': is_email_verified,
#             'students': students,
#             'student_subject_enrollment': student_subject_enrollment,
#             'teacher_subjects_dict': teacher_subjects_dict,
#             'student_marks': student_marks,
#             'examination_name': examination_name,
#             'exams': exams,
#             'selected_exam': selected_exam,
#         }
#         return render(request, 'teacher_profile.html', context)

#     # GET request
#     context = {
#         'teacher': teacher,
#         'teacher_subjects': teacher_subjects,
#         'subjects': subjects,
#         'assigned_classes': assigned_classes,
#         'total_students': total_students,
#         'exam_average_gpa': exam_average_gpa,
#         'all_exams_average_gpa': all_exams_average_gpa,
#         'gpa_chart': {
#             'labels': json.dumps(gpa_chart['labels']),
#             'data': json.dumps(gpa_chart['data'])
#         },
#         'attendance': attendance,
#         'monthly_attendance': monthly_details,
#         'display': display,
#         'is_verified': is_email_verified,
#         'exams': exams,
#         'selected_exam': selected_exam,
#     }
#     return render(request, 'teacher_profile.html', context)

# def determine_grade(mark, grading):
#     thresholds = grading.get_thresholds()
#     sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[0], reverse=True)
#     for threshold, grade in sorted_thresholds:
#         if mark >= threshold:
#             return grade
#     return 'F'

# @login_required
# def change_teacher_photo(request):
#     if request.method == 'POST':
#         try:
#             teacher = Teacher.objects.get(user=request.user)
#             if 'photo' in request.FILES:
#                 teacher.photo = request.FILES['photo']
#                 teacher.save()
#                 # Optionally save face encoding if needed
#                 if teacher.photo:
#                     teacher.save_face_encoding()
#                 messages.success(request, "Profile photo updated successfully.")
#             else:
#                 messages.error(request, "No photo selected.")
#         except ObjectDoesNotExist:
#             messages.error(request, "Teacher profile not found.")
#         return redirect('teacher_profile')  # Redirect to profile after POST
#     # For GET: Redirect to profile (avoids 403)
#     return redirect('teacher_profile')