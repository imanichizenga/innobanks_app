from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse,HttpResponse
from django.db import transaction
from rps_app.models import TeacherClass, Student
from .models import StudentAttendance
from django.utils import timezone
from datetime import date, timedelta
import calendar
import face_recognition
import numpy as np
import cv2
import base64
import logging
from django.contrib import messages
from django.urls import reverse
import pickle
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time  # Added missing import
import os
from playsound import playsound

logger = logging.getLogger(__name__)
from reportlab.lib.units import inch
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from rps_app.models import TeacherClass, Student
from .models import StudentAttendance
from django.utils import timezone
from datetime import date, timedelta, datetime
import calendar
import face_recognition
import numpy as np
import cv2
import base64
import logging
from django.contrib import messages
from django.urls import reverse
import pickle
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import pdfkit

import calendar
import face_recognition
import numpy as np
import cv2
import base64
import logging
from django.contrib import messages
from django.urls import reverse
import pickle
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import os
from django.template.loader import render_to_string
import pdfkit
from rps_app.models import Teacher
from .models import StaffAttendance
from .decorators import effective_user_decorator

@effective_user_decorator
@require_POST
@login_required
@csrf_exempt
def process_face_recognition(request, class_id):
    logger.debug(f"Received POST request for /attendance/face-recognition/{class_id}/, user: {request.user}")

    if not request.effective_user.is_teacher:
        logger.error("Unauthorized access attempt by non-teacher")
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    start_time = time.time()
    channel_layer = None

    try:
        try:
            channel_layer = get_channel_layer()
            logger.debug("Channel layer initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize channel layer: {str(e)}")

        # Get form data
        data = request.POST.get('image')
        sign_in = request.POST.get('sign_in') == 'on'
        sign_out = request.POST.get('sign_out') == 'on'

        if not data:
            return JsonResponse({'status': 'error', 'message': 'No image provided'}, status=400)

        # Validate checkbox inputs
        if sign_in and sign_out:
            return JsonResponse({'status': 'error', 'message': 'Cannot select both Sign In and Sign Out'}, status=400)
        if not sign_in and not sign_out:
            return JsonResponse({'status': 'error', 'message': 'Please select either Sign In or Sign Out'}, status=400)

        # Decode base64 image
        if not data.startswith('data:image/jpeg;base64,'):
            return JsonResponse({'status': 'error', 'message': 'Invalid image format'}, status=400)

        _, encoded_data = data.split(',', 1)
        img_data = base64.b64decode(encoded_data)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid image data'}, status=400)

        # Resize for performance
        scale_percent = 50
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        # Get students
        students = Student.objects.filter(
            teacherclass_id=class_id,
            manager=request.effective_user,
            face_encoding__isnull=False
        ).select_related('user')

        known_encodings = []
        known_ids = []

        for student in students:
            try:
                encoding = pickle.loads(student.face_encoding)
                known_encodings.append(encoding)
                known_ids.append(student.id)
            except Exception as e:
                logger.warning(f"Error loading encoding for student {student.id}: {str(e)}")

        # Detect faces
        face_locations = face_recognition.face_locations(img, model="hog", number_of_times_to_upsample=1)[:1]
        face_encodings = face_recognition.face_encodings(img, face_locations, num_jitters=1)[:1]

        processing_time = time.time() - start_time

        if not face_encodings:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"attendance_{class_id}",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': 'No face detected',
                        'processing_time': processing_time
                    }
                )
            return JsonResponse({'status': 'error', 'message': 'No face detected', 'processing_time': processing_time}, status=200)

        face_encoding = face_encodings[0]

        # Check if we have any known encodings to compare against
        if not known_encodings:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"attendance_{class_id}",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': 'No known encodings',
                        'processing_time': processing_time
                    }
                )
            return JsonResponse({'status': 'error', 'message': 'No known encodings', 'processing_time': processing_time}, status=200)

        # Compare with known encodings
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        min_distance = face_distances[best_match_index]

        # Stricter tolerance to reduce false positives (lowered from 0.5 to 0.45)
        tolerance = 0.45
        
        # Additional safeguard: if the best match is still relatively high (e.g., >0.6), treat as stranger
        if min_distance <= tolerance and min_distance <= 0.6:
            student_id = known_ids[best_match_index]
            student = students.get(id=student_id)

            today = date.today()
            attendance, created = StudentAttendance.objects.get_or_create(
                user=request.effective_user,
                student=student,
                date=today,
                defaults={'status': 'present', 'check_in_time': timezone.now().time() if sign_in else None}
            )

            if sign_in:
                # Record check-in time
                attendance.status = 'present'
                attendance.check_in_time = timezone.now().time()
                attendance.save()
                action = 'signed in'
            elif sign_out:
                # Only allow check-out if check-in exists
                if attendance.check_in_time is None:
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f"attendance_{class_id}",
                            {
                                'type': 'attendance_update',
                                'status': 'error',
                                'message': f'No check-in recorded for {student.fullName} today',
                                'processing_time': processing_time
                            }
                        )
                    return JsonResponse({
                        'status': 'error',
                        'message': f'No check-in recorded for {student.fullName} today',
                        'processing_time': processing_time
                    }, status=200)
                attendance.check_out_time = timezone.now().time()
                attendance.save()
                action = 'signed out'

            processing_time = time.time() - start_time

            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"attendance_{class_id}",
                    {
                        'type': 'attendance_update',
                        'status': 'success',
                        'student_name': student.fullName,
                        'student_id': student.id,
                        'date': today.day,
                        'action': action,
                        'processing_time': processing_time
                    }
                )

            return JsonResponse({
                'status': 'success',
                'student_name': student.fullName,
                'student_id': student.id,
                'date': today.day,
                'action': action,
                'processing_time': processing_time
            }, status=200)
        else:
            # Unknown face - distance above threshold or weak match
            processing_time = time.time() - start_time
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"attendance_{class_id}",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': 'No match found - stranger detected',
                        'processing_time': processing_time
                    }
                )
            return JsonResponse({'status': 'error', 'message': 'No match found - stranger detected', 'processing_time': processing_time}, status=200)

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error in face recognition: {str(e)}")
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"attendance_{class_id}",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': f'Processing error: {str(e)}',
                        'processing_time': processing_time
                    }
                )
            except Exception as ws_error:
                logger.error(f"Failed to send WebSocket error message: {str(ws_error)}")
        return JsonResponse({'status': 'error', 'message': f'Processing error: {str(e)}', 'processing_time': processing_time}, status=500)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import base64
import numpy as np
import cv2
import face_recognition
import pickle
from datetime import date
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
import time
import base64
import numpy as np
import cv2
import face_recognition
import pickle
from datetime import date
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import StaffAttendance
from rps_app.models import Teacher
logger = logging.getLogger(__name__)
@effective_user_decorator
@require_POST
@login_required
@csrf_exempt
def process_staff_face_recognition(request):
    logger.debug(f"Received POST request for /attendance/staff-face-recognition/, user: {request.user}")

    if not request.effective_user.is_teacher:
        logger.error("Unauthorized access attempt by non-teacher")
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    start_time = time.time()
    channel_layer = None

    try:
        try:
            channel_layer = get_channel_layer()
            logger.debug("Channel layer initialized successfully")
        except Exception as e:
            logger.warning(f"Could not initialize channel layer: {str(e)}")

        # Get form data
        data = request.POST.get('image')
        sign_in = request.POST.get('sign_in') == 'on'
        sign_out = request.POST.get('sign_out') == 'on'

        if not data:
            return JsonResponse({'status': 'error', 'message': 'No image provided'}, status=400)

        # Validate checkbox inputs
        if sign_in and sign_out:
            return JsonResponse({'status': 'error', 'message': 'Cannot select both Sign In and Sign Out'}, status=400)
        if not sign_in and not sign_out:
            return JsonResponse({'status': 'error', 'message': 'Please select either Sign In or Sign Out'}, status=400)

        # Decode base64 image
        if not data.startswith('data:image/jpeg;base64,'):
            return JsonResponse({'status': 'error', 'message': 'Invalid image format'}, status=400)

        _, encoded_data = data.split(',', 1)
        img_data = base64.b64decode(encoded_data)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid image data'}, status=400)

        # Resize for performance
        scale_percent = 50
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        # Get teachers
        teachers = Teacher.objects.filter(
            created_by=request.effective_user,
            face_encoding__isnull=False
        ).select_related('user')

        known_encodings = []
        known_ids = []

        for teacher in teachers:
            try:
                encoding = pickle.loads(teacher.face_encoding)
                known_encodings.append(encoding)
                known_ids.append(teacher.id)
            except Exception as e:
                logger.warning(f"Error loading encoding for teacher {teacher.id}: {str(e)}")

        # Detect faces
        face_locations = face_recognition.face_locations(img, model="hog", number_of_times_to_upsample=1)[:1]
        face_encodings = face_recognition.face_encodings(img, face_locations, num_jitters=1)[:1]

        processing_time = time.time() - start_time

        if not face_encodings:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "attendance_staff",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': 'No face detected',
                        'processing_time': processing_time
                    }
                )
            return JsonResponse({'status': 'error', 'message': 'No face detected', 'processing_time': processing_time}, status=200)

        face_encoding = face_encodings[0]

        # Check if we have any known encodings to compare against
        if not known_encodings:
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "attendance_staff",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': 'No known encodings',
                        'processing_time': processing_time
                    }
                )
            return JsonResponse({'status': 'error', 'message': 'No known encodings', 'processing_time': processing_time}, status=200)

        # Compare with known encodings
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        min_distance = face_distances[best_match_index]

        # Stricter tolerance to reduce false positives
        tolerance = 0.45

        # Additional safeguard: if the best match is still relatively high (e.g., >0.6), treat as stranger
        if min_distance <= tolerance and min_distance <= 0.6:
            teacher_id = known_ids[best_match_index]
            teacher = teachers.get(id=teacher_id)

            today = date.today()
            attendance, created = StaffAttendance.objects.get_or_create(
                user=request.effective_user,
                teacher=teacher,
                date=today,
                defaults={'status': 'present', 'check_in_time': timezone.now().time() if sign_in else None}
            )

            if sign_in:
                # Record check-in time
                attendance.status = 'present'
                attendance.check_in_time = timezone.now().time()
                attendance.save()
                action = 'signed in'
            elif sign_out:
                # Only allow check-out if check-in exists
                if attendance.check_in_time is None:
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            "attendance_staff",
                            {
                                'type': 'attendance_update',
                                'status': 'error',
                                'message': f'No check-in recorded for {teacher.teacherName} today',
                                'processing_time': processing_time
                            }
                        )
                    return JsonResponse({
                        'status': 'error',
                        'message': f'No check-in recorded for {teacher.teacherName} today',
                        'processing_time': processing_time
                    }, status=200)
                attendance.check_out_time = timezone.now().time()
                attendance.save()
                action = 'signed out'

            processing_time = time.time() - start_time

            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "attendance_staff",
                    {
                        'type': 'attendance_update',
                        'status': 'success',
                        'teacher_name': teacher.teacherName,
                        'teacher_id': teacher.id,
                        'date': today.day,
                        'action': action,
                        'processing_time': processing_time
                    }
                )

            return JsonResponse({
                'status': 'success',
                'teacher_name': teacher.teacherName,
                'teacher_id': teacher.id,
                'date': today.day,
                'action': action,
                'processing_time': processing_time
            }, status=200)
        else:
            # Unknown face - distance above threshold or weak match
            processing_time = time.time() - start_time
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    "attendance_staff",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': 'No match found - stranger detected',
                        'processing_time': processing_time
                    }
                )
            return JsonResponse({'status': 'error', 'message': 'No match found - stranger detected', 'processing_time': processing_time}, status=200)

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Error in staff face recognition: {str(e)}")
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    "attendance_staff",
                    {
                        'type': 'attendance_update',
                        'status': 'error',
                        'message': f'Processing error: {str(e)}',
                        'processing_time': processing_time
                    }
                )
            except Exception as ws_error:
                logger.error(f"Failed to send WebSocket error message: {str(ws_error)}")
        return JsonResponse({'status': 'error', 'message': f'Processing error: {str(e)}', 'processing_time': processing_time})

@effective_user_decorator
@require_POST
@login_required
def upload_student_photo(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id, manager=request.effective_user)
    except Exception as e:
        logger.error(f"Error fetching student {student_id}: {str(e)}")
        raise

    if 'photo' in request.FILES:
        try:
            student.photo = request.FILES['photo']
            student.save()
            
            # Save face encoding after saving the photo
            if student.photo:
                success = student.save_face_encoding()
                if success:
                    messages.success(request, f"Photo and face encoding for {student.fullName} updated successfully.")
                else:
                    messages.warning(request, f"Photo saved for {student.fullName}, but could not extract face encoding. Please use a clearer photo with a visible face.")
            else:
                messages.success(request, f"Photo for {student.fullName} updated successfully.")
                
        except Exception as e:
            logger.error(f"Error uploading photo for student {student.id}: {str(e)}")
            messages.error(request, "Failed to upload photo. Please try again.")
    else:
        messages.error(request, "No photo provided.")
    
    view_type = request.GET.get('view', 'monthly')
    week_number = request.GET.get('week', '1')
    return redirect(f"{reverse('attendance:student_attendance_with_class', args=[student.teacherclass.id])}?view={view_type}&week={week_number}")

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from rps_app.models import TeacherClass, Student
from .models import StudentAttendance
from django.utils import timezone
from datetime import date, timedelta, datetime
import calendar
import face_recognition
import numpy as np
import cv2
import base64
import logging
from django.contrib import messages
from django.urls import reverse
import pickle
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages

import logging
from datetime import date, timedelta
import calendar
from django.utils import timezone

logger = logging.getLogger(__name__)
@effective_user_decorator
@login_required
@transaction.atomic
def student_attendance(request, class_id=None):
    if not request.effective_user.is_teacher:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('teacher_dashboard')

    try:
        classes = TeacherClass.objects.filter(
            user=request.effective_user,
            academicclassyear__active_year=True
        ).order_by('ClassName')
    except Exception as e:
        logger.error(f"Error fetching classes: {str(e)}")
        raise

    view_type = request.GET.get('view', 'monthly')
    try:
        week_number = int(request.GET.get('week', 1))
    except ValueError:
        logger.warning(f"Invalid week_number: {request.GET.get('week')}")
        week_number = 1
    detected_only = request.GET.get('detected_only', 'false') == 'true'
    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year
    month_name = calendar.month_name[current_date.month]

    if class_id is None:
        context = {
            'classes': classes,
            'selected_class': None,
            'students': Student.objects.none(),
            'attendance_data': {},
            'month_name': '',
            'date_headers': [],
            'current_date': current_date,
            'view_type': view_type,
            'week_number': week_number,
            'detected_students': Student.objects.none(),
        }
        return render(request, 'attendance/student_attendance.html', context)

    try:
        selected_class = get_object_or_404(TeacherClass, id=class_id, user=request.effective_user)
        logger.debug(f"Rendering student_attendance with class_id={class_id}, selected_class.id={selected_class.id}")
    except Exception as e:
        logger.error(f"Error fetching class {class_id}: {str(e)}")
        raise

    try:
        students = Student.objects.filter(
            teacherclass=selected_class,
            manager=request.effective_user
        ).order_by('fullName').select_related('user')
    except Exception as e:
        logger.error(f"Error fetching students for class {class_id}: {str(e)}")
        raise

    # Define date range and headers
    if view_type == 'weekly':
        first_day_of_month = date(current_year, current_month, 1)
        first_monday = first_day_of_month + timedelta(days=(7 - first_day_of_month.weekday()) % 7)
        week_start = first_monday + timedelta(days=(week_number - 1) * 7)
        date_headers = [week_start + timedelta(days=i) for i in range(7)]
        date_range = date_headers
        display_name = f"Week {week_number} of {month_name} {current_year}"
    else:
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        date_headers = [date(current_year, current_month, i + 1) for i in range(days_in_month)]
        date_range = date_headers
        display_name = f"{month_name} {current_year}"

    # Initialize attendance records for all past and current days
    try:
        for student in students:
            for day in date_range:
                if day <= current_date:
                    StudentAttendance.objects.get_or_create(
                        user=request.effective_user,
                        student=student,
                        date=day,
                        defaults={'status': 'absent', 'check_in_time': None}
                    )
    except Exception as e:
        logger.error(f"Error initializing attendance for class {class_id}: {str(e)}")

    attendance_data = {}
    for student in students:
        try:
            attendance_records = StudentAttendance.objects.filter(
                student=student,
                date__in=date_range
            ).values('date', 'status', 'check_in_time')
            attendance_data[student.id] = {
                record['date'].day: {
                    'status': 'P' if record['status'] == 'present' else 'A',
                    'check_in_time': record['check_in_time'].strftime('%H:%M:%S') if record['check_in_time'] else '-'
                } for record in attendance_records
            }
            logger.debug(f"Attendance data for student {student.id}: {attendance_data[student.id]}")
        except Exception as e:
            logger.error(f"Error fetching attendance for student {student.id}: {str(e)}")
            attendance_data[student.id] = {}

    detected_students = Student.objects.filter(
        teacherclass=selected_class,
        manager=request.effective_user,
        attendances__date=current_date,
        attendances__status='present'
    ).order_by('fullName').select_related('user')

    context = {
        'classes': classes,
        'selected_class': selected_class,
        'students': students,
        'attendance_data': attendance_data,
        'month_name': display_name,
        'date_headers': date_headers,
        'current_date': current_date,
        'view_type': view_type,
        'week_number': week_number,
        'detected_students': detected_students,
        'channel_name': f"attendance_{class_id}",
        'students_with_encodings': students.filter(face_encoding__isnull=False),
        'students_without_encodings': students.filter(face_encoding__isnull=True),
    }

    if detected_only:
        if class_id is None:
            logger.error("No class_id provided for detected_only partial render")
            return render(request, 'attendance/detected_students_partial.html', {
                'detected_students': Student.objects.none(),
                'current_date': current_date,
                'class_id': None,
                'view_type': view_type,
                'week_number': week_number,
                'error': 'No class selected'
            })

        return render(request, 'attendance/detected_students_partial.html', {
            'detected_students': detected_students,
            'current_date': current_date,
            'class_id': class_id,
            'view_type': view_type,
            'week_number': week_number,
        })

    return render(request, 'attendance/student_attendance.html', context)




from django.shortcuts import render
from django.utils import timezone
from datetime import date
# ... other imports ...
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rps_app.models import Teacher
from attendance.models import StaffAttendance
from datetime import date, timedelta
import calendar
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rps_app.models import Teacher
from attendance.models import StaffAttendance
from datetime import date, timedelta
import calendar
from django.utils import timezone

@effective_user_decorator
@login_required
def staff_attendance(request):
    if not request.effective_user.is_teacher:
        return redirect('homepage')

    # Filter teachers: only those created by the logged-in user
    teachers = Teacher.objects.filter(created_by=request.effective_user)

    # Face encoding status
    teachers_with_encodings = teachers.filter(face_encoding__isnull=False)
    teachers_without_encodings = teachers.exclude(face_encoding__isnull=False)

    # View type (monthly/weekly)
    view_type = request.GET.get('view', 'monthly')
    week_number = int(request.GET.get('week', 1)) if view_type == 'weekly' else None
    current_date = date.today()
    month_name = current_date.strftime('%B')
    year, month = current_date.year, current_date.month

    # Generate date headers
    if view_type == 'weekly':
        start_date = current_date - timedelta(days=current_date.weekday() + 7 * (week_number - 1))
        date_headers = [start_date + timedelta(days=i) for i in range(7)]
    else:
        _, last_day = calendar.monthrange(year, month)
        date_headers = [date(year, month, d) for d in range(1, last_day + 1)]

    # Detected teachers (present today)
    detected_teachers = [t for t in teachers if StaffAttendance.objects.filter(teacher=t, date=current_date, status='present').exists()]

    context = {
        'teachers': teachers,
        'teachers_with_encodings': teachers_with_encodings,
        'teachers_without_encodings': teachers_without_encodings,
        'detected_teachers': detected_teachers,
        'view_type': view_type,
        'week_number': week_number,
        'month_name': month_name,
        'date_headers': date_headers,
        'current_date': current_date,
        'csrf_token': request.COOKIES['csrftoken'],
    }
    return render(request, 'attendance/staff_attendance.html', context)

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Teacher
@effective_user_decorator
@login_required
def upload_teacher_photo(request, teacher_id):
    teacher = Teacher.objects.get(id=teacher_id, created_by=request.effective_user)
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        if photo:
            teacher.photo = photo
            teacher.save()
            teacher.save_face_encoding()  # Generate encoding
            messages.success(request, f"Photo uploaded for {teacher.teacherName}")
        else:
            messages.error(request, "No photo provided")
        return redirect('attendance:staff_attendance')
    return render(request, 'upload_teacher_photo.html', {'teacher': teacher})

@effective_user_decorator
@login_required
@transaction.atomic
def attendance_table_partial(request, class_id):
    try:
        selected_class = get_object_or_404(TeacherClass, id=class_id, user=request.effective_user)
        logger.debug(f"Rendering attendance_table_partial with class_id={class_id}, selected_class.id={selected_class.id}")
    except Exception as e:
        logger.error(f"Error fetching class {class_id}: {str(e)}")
        raise

    view_type = request.GET.get('view', 'monthly')
    try:
        week_number = int(request.GET.get('week', 1))
    except ValueError:
        logger.warning(f"Invalid week_number: {request.GET.get('week')}")
        week_number = 1
    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year
    month_name = calendar.month_name[current_date.month]

    try:
        students = Student.objects.filter(
            teacherclass=selected_class,
            manager=request.effective_user
        ).order_by('fullName').select_related('user')
    except Exception as e:
        logger.error(f"Error fetching students for class {class_id}: {str(e)}")
        raise

    # Define date range and headers
    if view_type == 'weekly':
        first_day_of_month = date(current_year, current_month, 1)
        first_monday = first_day_of_month + timedelta(days=(7 - first_day_of_month.weekday()) % 7)
        week_start = first_monday + timedelta(days=(week_number - 1) * 7)
        date_headers = [week_start + timedelta(days=i) for i in range(7)]
        date_range = date_headers
        display_name = f"Week {week_number} of {month_name} {current_year}"
    else:
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        date_headers = [date(current_year, current_month, i + 1) for i in range(days_in_month)]
        date_range = date_headers
        display_name = f"{month_name} {current_year}"

    # Initialize attendance records for all past and current days
    try:
        for student in students:
            for day in date_range:
                if day <= current_date:
                    StudentAttendance.objects.get_or_create(
                        user=request.effective_user,
                        student=student,
                        date=day,
                        defaults={'status': 'absent', 'check_in_time': None}
                    )
    except Exception as e:
        logger.error(f"Error initializing attendance for class {class_id}: {str(e)}")

    attendance_data = {}
    for student in students:
        try:
            attendance_records = StudentAttendance.objects.filter(
                student=student,
                date__in=date_range
            ).values('date', 'status', 'check_in_time')
            attendance_data[student.id] = {
                record['date'].day: {
                    'status': 'P' if record['status'] == 'present' else 'A',
                    'check_in_time': record['check_in_time'].strftime('%H:%M:%S') if record['check_in_time'] else '-'
                } for record in attendance_records
            }
            logger.debug(f"Attendance data for student {student.id}: {attendance_data[student.id]}")
        except Exception as e:
            logger.error(f"Error fetching attendance for student {student.id}: {str(e)}")
            attendance_data[student.id] = {}

    context = {
        'selected_class': selected_class,
        'students': students,
        'attendance_data': attendance_data,
        'month_name': display_name,
        'date_headers': date_headers,
        'current_date': current_date,
        'view_type': view_type,
        'week_number': week_number,
    }

    return render(request, 'attendance/attendance_table_partial.html', context)


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rps_app.models import DisplayModel
from rps_app import templatetags
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

from datetime import date, timedelta
import calendar
import logging
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak, KeepTogether

from datetime import date, timedelta
import calendar
import logging
@effective_user_decorator
@login_required
def generate_attendance_pdf(request, class_id):
    try:
        selected_class = get_object_or_404(TeacherClass, id=class_id, user=request.effective_user)
    except Exception as e:
        logger.error(f"Error fetching class {class_id}: {str(e)}")
        messages.error(request, "Failed to generate PDF: Invalid class")
        return redirect('attendance:student_attendance_with_class', class_id=class_id)

    view_type = request.GET.get('view', 'monthly')
    try:
        week_number = int(request.GET.get('week', 1))
    except ValueError:
        logger.warning(f"Invalid week_number: {request.GET.get('week')}")
        week_number = 1

    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year
    month_name = calendar.month_name[current_date.month]

    if view_type == 'weekly':
        first_day_of_month = date(current_year, current_month, 1)
        first_monday = first_day_of_month + timedelta(days=(7 - first_day_of_month.weekday()) % 7)
        week_start = first_monday + timedelta(days=(week_number - 1) * 7)
        date_headers = [week_start + timedelta(days=i) for i in range(7)]
        date_range = date_headers
        display_name = f"Week {week_number} of {month_name} {current_year}"
        pagesize = A4
    else:
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        date_headers = [date(current_year, current_month, i + 1) for i in range(days_in_month)]
        date_range = date_headers
        display_name = f"{month_name} {current_year}"
        pagesize = landscape(A4)

    try:
        students = Student.objects.filter(
            teacherclass=selected_class,
            manager=request.effective_user
        ).order_by('fullName').select_related('user')
    except Exception as e:
        logger.error(f"Error fetching students for class {class_id}: {str(e)}")
        messages.error(request, "Failed to generate PDF: Error fetching student data")
        return redirect('attendance:student_attendance_with_class', class_id=class_id)

    # Initialize attendance records for past days
    try:
        for student in students:
            for day in date_range:
                if day <= current_date:
                    StudentAttendance.objects.get_or_create(
                        user=request.effective_user,
                        student=student,
                        date=day,
                        defaults={'status': 'absent', 'check_in_time': None, 'check_out_time': None}
                    )
    except Exception as e:
        logger.error(f"Error initializing attendance for class {class_id}: {str(e)}")

    response = HttpResponse(content_type='application/pdf')
    filename = f"attendance_{selected_class.ClassName}_{display_name.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    doc = SimpleDocTemplate(
        response,
        pagesize=pagesize,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(name='Header', fontName='Times-Bold', fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=6)
    subheader_style = ParagraphStyle(name='Subheader', fontName='Times-Roman', fontSize=12, leading=14, alignment=TA_CENTER, spaceAfter=6)
    body_style = ParagraphStyle(name='Body', fontName='Times-Roman', fontSize=8, leading=10, alignment=TA_CENTER)
    footer_style = ParagraphStyle(name='Footer', fontName='Times-Roman', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.grey)
    present_style = ParagraphStyle(name='Present', fontName='Times-Bold', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.green)
    absent_style = ParagraphStyle(name='Absent', fontName='Times-Bold', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.red)
    time_style = ParagraphStyle(name='Time', fontName='Times-Roman', fontSize=7, leading=8, alignment=TA_CENTER)

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num} | Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas.saveState()
        canvas.setFont("Times-Roman", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(pagesize[0]/2, 0.5*cm, text)
        canvas.restoreState()

    # Header with Centered Logo
    display = DisplayModel.objects.filter(user=request.user).first()
    academic_year = selected_class.academicclassyear.academic_year_name if selected_class.academicclassyear else 'N/A'
    header_text = display.header if display else f"Attendance Report for {selected_class.ClassName or 'Unnamed Class'}"
    subheader_text = f"Class: {selected_class.ClassName} | Academic Year: {academic_year} | {display_name}"

    # Add centered logo
    if display and display.image:
        try:
            icon = Image(display.image.path, width=2*cm, height=2*cm)
            icon.hAlign = 'CENTER'
            icon.vAlign = 'TOP'
            elements.append(icon)
        except Exception as e:
            logger.error(f"Error loading DisplayModel image: {e}")
            elements.append(Spacer(1, 2*cm))  # Reserve space if image fails
    else:
        elements.append(Spacer(1, 2*cm))  # Reserve space if no image

    # Centered header and subheader
    elements.append(Paragraph(header_text, header_style))
    elements.append(Paragraph(subheader_text, subheader_style))
    elements.append(Spacer(1, 0.3*cm))

    if not students.exists():
        elements.append(Paragraph("No students available for this class.", body_style))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        try:
            doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
            messages.success(request, 'Attendance report generated successfully!')
            return response
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect('attendance:student_attendance_with_class', class_id=class_id)

    # First Summary Table (Attendance Summary with Check-In/Check-Out)
    elements.append(Paragraph("Attendance Summary", subheader_style))
    elements.append(Spacer(1, 0.3*cm))  # Top margin

    fixed_headers = ['S/No', 'Student Name', 'Index No', 'Sex']
    fixed_col_widths = [0.5*inch, 1.4*inch, 0.9*inch, 0.4*inch]

    # Date column width
    date_col_width = 0.5*inch  # Increased for times

    # Check if need to split
    split_threshold = 15
    if view_type == 'monthly' and len(date_headers) > split_threshold:
        # Split into two parts
        mid = len(date_headers) // 2
        date_parts = [date_headers[:mid], date_headers[mid:]]
        part_labels = [f"Days 1-{mid}", f"Days {mid+1}-{len(date_headers)}"]
    else:
        date_parts = [date_headers]
        part_labels = [""]

    for part_idx, date_part in enumerate(date_parts):
        if part_labels[part_idx]:
            elements.append(Paragraph(f"{part_labels[part_idx]}", subheader_style))
            elements.append(Spacer(1, 0.2*cm))

        summary_data = [fixed_headers + [f"{day.strftime('%d')}\nIn | Out" for day in date_part]]
        for i, student in enumerate(students, 1):
            row = [
                str(i),
                student.fullName[:30] or 'Unnamed',
                student.indexNumber or '-',
                student.sex or '-'
            ]
            for day in date_part:
                try:
                    attendance = StudentAttendance.objects.get(student=student, date=day)
                    status = 'P' if attendance.status == 'present' else 'A' if day <= current_date else '-'
                    check_in = attendance.check_in_time.strftime('%H:%M') if attendance.check_in_time else '-'
                    check_out = attendance.check_out_time.strftime('%H:%M') if attendance.check_out_time else '-'
                    cell_content = f"{status}\n{check_in} | {check_out}"
                    style = present_style if status == 'P' else absent_style if status == 'A' else body_style
                    row.append(Paragraph(cell_content, style))
                except StudentAttendance.DoesNotExist:
                    status = 'A' if day <= current_date else '-'
                    cell_content = f"{status}\n- | -"
                    row.append(Paragraph(cell_content, absent_style if status == 'A' else body_style))
            summary_data.append(row)

        col_widths = fixed_col_widths + [date_col_width] * len(date_part)

        summary_table = Table(summary_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D8DE')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*cm))
        if part_idx < len(date_parts) - 1:
            elements.append(PageBreak())

    elements.append(PageBreak())

    # Second Summary Table (Overall Attendance Summary)
    elements.append(Paragraph("Overall Attendance Summary", subheader_style))
    elements.append(Spacer(1, 0.3*cm))  # Top margin

    second_summary_data = [['Student Name', 'Index Number', 'Present Days', 'Absent Days']]
    from rps_app.templatetags.custom_filters import count_present, count_absent
    for student in students:
        row = [
            student.fullName[:30] or 'Unnamed',
            student.indexNumber or '-',
            str(count_present(student, date_headers)),
            str(count_absent(student, date_headers))
        ]
        second_summary_data.append(row)

    total_columns = len(second_summary_data[0])
    available_width = pagesize[0] - 2.5*cm  # Reduced to ensure right margin
    col_widths = [1.8*inch, 1.3*inch, 0.9*inch, 0.9*inch]  # Adjusted to fit with margin

    logger.debug(f"Second summary table columns: {total_columns}, Total width: {sum(col_widths):.2f}pt, Available width: {available_width:.2f}pt")
    logger.debug(f"Second summary table rows: {len(second_summary_data)}")

    second_summary_table = Table(second_summary_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
    second_summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Thicker grid lines
        ('BOX', (0, 0), (-1, -1), 2, colors.black),   # Thicker outer border
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D8DE')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),  # Consistent padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ]))
    elements.append(second_summary_table)
    elements.append(Spacer(1, 0.3*cm))  # Bottom margin
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    try:
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        messages.success(request, 'Attendance report generated successfully!')
        return response
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('attendance:student_attendance_with_class', class_id=class_id)



@effective_user_decorator
@login_required
def generate_staff_attendance_pdf(request):
    if not request.effective_user.is_teacher:
        logger.error("Unauthorized access attempt by non-teacher")
        messages.error(request, "Unauthorized")
        return redirect('attendance:staff_attendance')

    view_type = request.GET.get('view', 'monthly')
    try:
        week_number = int(request.GET.get('week', 1))
    except ValueError:
        logger.warning(f"Invalid week_number: {request.GET.get('week')}")
        week_number = 1

    current_date = timezone.now().date()
    current_month = current_date.month
    current_year = current_date.year
    month_name = calendar.month_name[current_date.month]

    if view_type == 'weekly':
        first_day_of_month = date(current_year, current_month, 1)
        first_monday = first_day_of_month + timedelta(days=(7 - first_day_of_month.weekday()) % 7)
        week_start = first_monday + timedelta(days=(week_number - 1) * 7)
        date_headers = [week_start + timedelta(days=i) for i in range(7)]
        date_range = date_headers
        display_name = f"Week {week_number} of {month_name} {current_year}"
        pagesize = A4
    else:
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        date_headers = [date(current_year, current_month, i + 1) for i in range(days_in_month)]
        date_range = date_headers
        display_name = f"{month_name} {current_year}"
        pagesize = landscape(A4)

    # Get teachers created by or accessible to the authenticated user
    try:
        teachers = Teacher.objects.filter(
            created_by=request.effective_user
        ).select_related('user')
    except Exception as e:
        logger.error(f"Error fetching teachers: {str(e)}")
        messages.error(request, "Failed to generate PDF: Error fetching teacher data")
        return redirect('attendance:staff_attendance')

    # Initialize attendance records for past days
    try:
        for teacher in teachers:
            for day in date_range:
                if day <= current_date:
                    StaffAttendance.objects.get_or_create(
                        user=request.effective_user,
                        teacher=teacher,
                        date=day,
                        defaults={'status': 'absent', 'check_in_time': None, 'check_out_time': None}
                    )
    except Exception as e:
        logger.error(f"Error initializing attendance for teachers: {str(e)}")

    response = HttpResponse(content_type='application/pdf')
    filename = f"staff_attendance_{display_name.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    doc = SimpleDocTemplate(
        response,
        pagesize=pagesize,
        rightMargin=1*cm,
        leftMargin=1*cm,
        topMargin=1*cm,
        bottomMargin=1*cm
    )
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(name='Header', fontName='Times-Bold', fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=6)
    subheader_style = ParagraphStyle(name='Subheader', fontName='Times-Roman', fontSize=12, leading=14, alignment=TA_CENTER, spaceAfter=6)
    body_style = ParagraphStyle(name='Body', fontName='Times-Roman', fontSize=8, leading=10, alignment=TA_CENTER)
    footer_style = ParagraphStyle(name='Footer', fontName='Times-Roman', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.grey)
    present_style = ParagraphStyle(name='Present', fontName='Times-Bold', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.green)
    absent_style = ParagraphStyle(name='Absent', fontName='Times-Bold', fontSize=8, leading=10, alignment=TA_CENTER, textColor=colors.red)
    time_style = ParagraphStyle(name='Time', fontName='Times-Roman', fontSize=7, leading=8, alignment=TA_CENTER)

    def add_page_number(canvas, doc):
        page_num = canvas.getPageNumber()
        text = f"Page {page_num} | Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        canvas.saveState()
        canvas.setFont("Times-Roman", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(pagesize[0]/2, 0.5*cm, text)
        canvas.restoreState()

    # Header with Centered Logo
    display = DisplayModel.objects.filter(user=request.effective_user).first()
    header_text = display.header if display else "Staff Attendance Report"
    subheader_text = f"Period: {display_name}"

    # Add centered logo
    if display and display.image:
        try:
            icon = Image(display.image.path, width=2*cm, height=2*cm)
            icon.hAlign = 'CENTER'
            icon.vAlign = 'TOP'
            elements.append(icon)
        except Exception as e:
            logger.error(f"Error loading DisplayModel image: {e}")
            elements.append(Spacer(1, 2*cm))  # Reserve space if image fails
    else:
        elements.append(Spacer(1, 2*cm))  # Reserve space if no image

    # Centered header and subheader
    elements.append(Paragraph(header_text, header_style))
    elements.append(Paragraph(subheader_text, subheader_style))
    elements.append(Spacer(1, 0.3*cm))

    if not teachers.exists():
        elements.append(Paragraph("No teachers available.", body_style))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        try:
            doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
            messages.success(request, 'Staff attendance report generated successfully!')
            return response
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            messages.error(request, f"Error generating PDF: {str(e)}")
            return redirect('attendance:staff_attendance')

    # First Summary Table (Attendance Summary with Check-In/Check-Out)
    elements.append(Paragraph("Attendance Summary", subheader_style))
    elements.append(Spacer(1, 0.3*cm))  # Top margin

    fixed_headers = ['S/No', 'Teacher Name', 'Teacher Key']
    fixed_col_widths = [0.5*inch, 1.4*inch, 0.9*inch]

    # Date column width
    date_col_width = 0.5*inch  # Increased for times

    # Check if need to split
    split_threshold = 15
    if view_type == 'monthly' and len(date_headers) > split_threshold:
        # Split into two parts
        mid = len(date_headers) // 2
        date_parts = [date_headers[:mid], date_headers[mid:]]
        part_labels = [f"Days 1-{mid}", f"Days {mid+1}-{len(date_headers)}"]
    else:
        date_parts = [date_headers]
        part_labels = [""]

    for part_idx, date_part in enumerate(date_parts):
        if part_labels[part_idx]:
            elements.append(Paragraph(f"{part_labels[part_idx]}", subheader_style))
            elements.append(Spacer(1, 0.2*cm))

        summary_data = [fixed_headers + [f"{day.strftime('%d')}\nIn | Out" for day in date_part]]
        for i, teacher in enumerate(teachers, 1):
            row = [
                str(i),
                teacher.teacherName[:30] or 'Unnamed',
                teacher.teacher_key or '-'
            ]
            for day in date_part:
                try:
                    attendance = StaffAttendance.objects.get(teacher=teacher, date=day)
                    status = 'P' if attendance.status == 'present' else 'A' if day <= current_date else '-'
                    check_in = attendance.check_in_time.strftime('%H:%M') if attendance.check_in_time else '-'
                    check_out = attendance.check_out_time.strftime('%H:%M') if attendance.check_out_time else '-'
                    cell_content = f"{status}\n{check_in} | {check_out}"
                    style = present_style if status == 'P' else absent_style if status == 'A' else body_style
                    row.append(Paragraph(cell_content, style))
                except StaffAttendance.DoesNotExist:
                    status = 'A' if day <= current_date else '-'
                    cell_content = f"{status}\n- | -"
                    row.append(Paragraph(cell_content, absent_style if status == 'A' else body_style))
            summary_data.append(row)

        col_widths = fixed_col_widths + [date_col_width] * len(date_part)

        summary_table = Table(summary_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D8DE')),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*cm))
        if part_idx < len(date_parts) - 1:
            elements.append(PageBreak())

    elements.append(PageBreak())

    # Second Summary Table (Overall Attendance Summary)
    elements.append(Paragraph("Overall Attendance Summary", subheader_style))
    elements.append(Spacer(1, 0.3*cm))  # Top margin

    second_summary_data = [['Teacher Name', 'Teacher Key', 'Present Days', 'Absent Days']]
    for teacher in teachers:
        try:
            present_count = StaffAttendance.objects.filter(teacher=teacher, date__in=date_headers, status='present').count()
            absent_count = StaffAttendance.objects.filter(teacher=teacher, date__in=date_headers, status='absent').count()
        except Exception as e:
            logger.error(f"Error counting attendance for teacher {teacher.id}: {str(e)}")
            present_count = 0
            absent_count = len(date_headers)
        row = [
            teacher.teacherName[:30] or 'Unnamed',
            teacher.teacher_key or '-',
            str(present_count),
            str(absent_count)
        ]
        second_summary_data.append(row)

    total_columns = len(second_summary_data[0])
    available_width = pagesize[0] - 2.5*cm  # Reduced to ensure right margin
    col_widths = [1.8*inch, 1.3*inch, 0.9*inch, 0.9*inch]

    logger.debug(f"Second summary table columns: {total_columns}, Total width: {sum(col_widths):.2f}pt, Available width: {available_width:.2f}pt")
    logger.debug(f"Second summary table rows: {len(second_summary_data)}")

    second_summary_table = Table(second_summary_data, colWidths=col_widths, splitByRow=True, repeatRows=1)
    second_summary_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('LEADING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D8DE')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ]))
    elements.append(second_summary_table)
    elements.append(Spacer(1, 0.3*cm))  # Bottom margin
    elements.append(Paragraph(f"Generated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    try:
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        messages.success(request, 'Staff attendance report generated successfully!')
        return response
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        messages.error(request, f"Error generating PDF: {str(e)}")
        return redirect('attendance:staff_attendance')
from django.db.models import Count, Q
from datetime import datetime
from .forms import ManualAttendanceFilterForm
from .models import ManualStudentAttendance, ManualStaffAttendance


def _get_period_dates(target_date, view_type):
    if view_type == "weekly":
        start = target_date - timedelta(days=target_date.weekday())
        end = start + timedelta(days=6)
    elif view_type == "monthly":
        start = target_date.replace(day=1)
        end_day = calendar.monthrange(target_date.year, target_date.month)[1]
        end = target_date.replace(day=end_day)
    else:
        start = target_date
        end = target_date
    return start, end


@effective_user_decorator
@login_required
def manual_student_attendance(request):
    classes = TeacherClass.objects.filter(
        user=request.effective_user,
        academicclassyear__active_year=True,
    ).select_related("ClassName").order_by("ClassName__class_name")

    selected_class_id = request.GET.get("class_id") or request.POST.get("class_id")
    selected_date_str = request.GET.get("date") or request.POST.get("date")
    selected_date = timezone.localdate()
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "Invalid date selected. Showing today.")

    selected_class = None
    students = Student.objects.none()
    existing_map = {}

    if selected_class_id:
        selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=request.effective_user)
        students = Student.objects.filter(
            teacherclass=selected_class,
            manager=request.effective_user,
        ).select_related("user").order_by("fullName", "indexNumber")
        existing_map = {
            item["student_id"]: item["status"]
            for item in ManualStudentAttendance.objects.filter(
                student__in=students,
                date=selected_date,
            ).values("student_id", "status")
        }

    if request.method == "POST" and selected_class:
        present_ids = {int(pk) for pk in request.POST.getlist("present_students") if pk.isdigit()}
        with transaction.atomic():
            for student in students:
                ManualStudentAttendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={
                        "user": request.effective_user,
                        "status": "present" if student.id in present_ids else "absent",
                    },
                )

        messages.success(request, "Student attendance saved successfully.")
        return redirect(
            f"{reverse('attendance:manual_student_attendance')}?class_id={selected_class.id}&date={selected_date.isoformat()}"
        )

    total_students = students.count()
    present_count = sum(1 for status in existing_map.values() if status == "present")
    absent_count = total_students - present_count

    context = {
        "classes": classes,
        "students": students,
        "selected_class": selected_class,
        "selected_date": selected_date,
        "existing_map": existing_map,
        "total_students": total_students,
        "present_count": present_count,
        "absent_count": absent_count,
    }
    return render(request, "attendance/manual_student_attendance.html", context)


@effective_user_decorator
@login_required
def manual_staff_attendance(request):
    selected_date_str = request.GET.get("date") or request.POST.get("date")
    selected_date = timezone.localdate()
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "Invalid date selected. Showing today.")

    teachers = Teacher.objects.filter(created_by=request.effective_user).select_related("user").order_by("teacherName", "teacher_key")
    existing_map = {
        item["teacher_id"]: item["status"]
        for item in ManualStaffAttendance.objects.filter(
            teacher__in=teachers,
            date=selected_date,
        ).values("teacher_id", "status")
    }

    if request.method == "POST":
        present_ids = {int(pk) for pk in request.POST.getlist("present_teachers") if pk.isdigit()}
        with transaction.atomic():
            for teacher in teachers:
                ManualStaffAttendance.objects.update_or_create(
                    teacher=teacher,
                    date=selected_date,
                    defaults={
                        "user": request.effective_user,
                        "status": "present" if teacher.id in present_ids else "absent",
                    },
                )
        messages.success(request, "Staff attendance saved successfully.")
        return redirect(f"{reverse('attendance:manual_staff_attendance')}?date={selected_date.isoformat()}")

    total_staff = teachers.count()
    present_count = sum(1 for status in existing_map.values() if status == "present")
    absent_count = total_staff - present_count

    return render(
        request,
        "attendance/manual_staff_attendance.html",
        {
            "teachers": teachers,
            "selected_date": selected_date,
            "existing_map": existing_map,
            "total_staff": total_staff,
            "present_count": present_count,
            "absent_count": absent_count,
        },
    )


@effective_user_decorator
@login_required
def student_attendance_report(request):
    form = ManualAttendanceFilterForm(request.GET or None)
    classes = TeacherClass.objects.filter(
        user=request.effective_user,
        academicclassyear__active_year=True,
    ).select_related("ClassName").order_by("ClassName__class_name")

    selected_class_id = request.GET.get("class_id")
    selected_class = None
    rows = []
    summary = {"total": 0, "present": 0, "absent": 0, "percentage": 0}

    if form.is_valid() and selected_class_id:
        selected_date = form.cleaned_data["date"]
        view_type = form.cleaned_data["view"]
        search = form.cleaned_data.get("search", "").strip()
        period_start, period_end = _get_period_dates(selected_date, view_type)

        selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=request.effective_user)
        students = Student.objects.filter(
            teacherclass=selected_class,
            manager=request.effective_user,
        ).select_related("user").order_by("fullName", "indexNumber")

        if search:
            students = students.filter(Q(fullName__icontains=search) | Q(indexNumber__icontains=search))

        student_ids = list(students.values_list("id", flat=True))
        attendance_stats = {
            item["student_id"]: item
            for item in ManualStudentAttendance.objects.filter(
                student_id__in=student_ids,
                date__range=(period_start, period_end),
            ).values("student_id").annotate(
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
            )
        }

        for student in students:
            stat = attendance_stats.get(student.id, {})
            present = stat.get("present", 0)
            absent = stat.get("absent", 0)
            total = present + absent
            percentage = round((present / total) * 100, 2) if total else 0
            rows.append(
                {
                    "student": student,
                    "present": present,
                    "absent": absent,
                    "percentage": percentage,
                }
            )

        summary["total"] = len(rows)
        summary["present"] = sum(row["present"] for row in rows)
        summary["absent"] = sum(row["absent"] for row in rows)
        total_records = summary["present"] + summary["absent"]
        summary["percentage"] = round((summary["present"] / total_records) * 100, 2) if total_records else 0
    else:
        selected_date = timezone.localdate()
        view_type = "daily"
        period_start, period_end = selected_date, selected_date

    return render(
        request,
        "attendance/student_attendance_report.html",
        {
            "form": form,
            "classes": classes,
            "selected_class_id": selected_class_id,
            "selected_class": selected_class,
            "rows": rows,
            "summary": summary,
            "period_start": period_start,
            "period_end": period_end,
            "view_type": view_type,
        },
    )


@effective_user_decorator
@login_required
def staff_attendance_report(request):
    form = ManualAttendanceFilterForm(request.GET or None)
    rows = []
    summary = {"total": 0, "present": 0, "absent": 0, "percentage": 0}

    if form.is_valid():
        selected_date = form.cleaned_data["date"]
        view_type = form.cleaned_data["view"]
        search = form.cleaned_data.get("search", "").strip()
        period_start, period_end = _get_period_dates(selected_date, view_type)

        teachers = Teacher.objects.filter(created_by=request.effective_user).select_related("user").order_by("teacherName", "teacher_key")
        if search:
            teachers = teachers.filter(Q(teacherName__icontains=search) | Q(teacher_key__icontains=search))

        teacher_ids = list(teachers.values_list("id", flat=True))
        attendance_stats = {
            item["teacher_id"]: item
            for item in ManualStaffAttendance.objects.filter(
                teacher_id__in=teacher_ids,
                date__range=(period_start, period_end),
            ).values("teacher_id").annotate(
                present=Count("id", filter=Q(status="present")),
                absent=Count("id", filter=Q(status="absent")),
            )
        }

        for teacher in teachers:
            stat = attendance_stats.get(teacher.id, {})
            present = stat.get("present", 0)
            absent = stat.get("absent", 0)
            total = present + absent
            percentage = round((present / total) * 100, 2) if total else 0
            rows.append(
                {
                    "teacher": teacher,
                    "present": present,
                    "absent": absent,
                    "percentage": percentage,
                }
            )

        summary["total"] = len(rows)
        summary["present"] = sum(row["present"] for row in rows)
        summary["absent"] = sum(row["absent"] for row in rows)
        total_records = summary["present"] + summary["absent"]
        summary["percentage"] = round((summary["present"] / total_records) * 100, 2) if total_records else 0
    else:
        selected_date = timezone.localdate()
        view_type = "daily"
        period_start, period_end = selected_date, selected_date

    return render(
        request,
        "attendance/staff_attendance_report.html",
        {
            "form": form,
            "rows": rows,
            "summary": summary,
            "period_start": period_start,
            "period_end": period_end,
            "view_type": view_type,
        },
    )

from .utils import determine_attendance_status, apply_common_attendance_filters, status_totals, build_attendance_pdf_response


def _status_badge(status):
    return status or "absent"


def _filters_summary(form, selected_class=None):
    cleaned = form.cleaned_data if form.is_valid() else {}
    bits = []
    if selected_class:
        bits.append(f"Class: {selected_class}")
    bits.append(f"View: {cleaned.get('view', 'daily')}")
    bits.append(f"Date: {cleaned.get('date')}")
    if cleaned.get('date_from') or cleaned.get('date_to'):
        bits.append(f"Date range: {cleaned.get('date_from') or '-'} to {cleaned.get('date_to') or '-'}")
    if cleaned.get('status'):
        bits.append(f"Status: {cleaned['status']}")
    if cleaned.get('from_time') or cleaned.get('to_time'):
        bits.append(f"Time: {cleaned.get('from_time') or '-'} to {cleaned.get('to_time') or '-'}")
    if cleaned.get('arrived_after'):
        bits.append(f"Arrived after: {cleaned['arrived_after']}")
    if cleaned.get('late_only'):
        bits.append("Late only: Yes")
    return " | ".join(bits)


@effective_user_decorator
@login_required
def manual_student_attendance(request):
    classes = TeacherClass.objects.filter(user=request.effective_user, academicclassyear__active_year=True).select_related("ClassName").order_by("ClassName__class_name")
    selected_class_id = request.GET.get("class_id") or request.POST.get("class_id")
    selected_date_str = request.GET.get("date") or request.POST.get("date")
    cutoff_str = request.GET.get("cutoff_time") or request.POST.get("cutoff_time")
    selected_date = timezone.localdate()
    cutoff_time = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "Invalid date selected. Showing today.")
    if cutoff_str:
        try:
            cutoff_time = datetime.strptime(cutoff_str, "%H:%M").time()
        except ValueError:
            messages.warning(request, "Invalid cutoff time ignored.")

    selected_class = None
    students = Student.objects.none()
    existing_map = {}

    if selected_class_id:
        selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=request.effective_user)
        students = Student.objects.filter(teacherclass=selected_class, manager=request.effective_user).select_related("user").order_by("fullName", "indexNumber")
        existing = ManualStudentAttendance.objects.filter(student__in=students, date=selected_date)
        existing_map = {
            item.student_id: {
                "status": item.attendance_status or item.status,
                "check_in_time": item.check_in_time,
                "check_out_time": item.check_out_time,
            }
            for item in existing
        }

    if request.method == "POST" and selected_class:
        student_ids = [int(pk) for pk in request.POST.getlist("student_ids") if pk.isdigit()]
        students_by_id = {student.id: student for student in students}
        selected_students = [students_by_id[student_id] for student_id in student_ids if student_id in students_by_id]

        def _parse_time_value(raw_value):
            if not raw_value:
                return None
            try:
                return datetime.strptime(raw_value, "%H:%M").time()
            except ValueError:
                return None

        now_time = timezone.localtime().time().replace(second=0, microsecond=0)
        with transaction.atomic():
            for student in selected_students:
                is_present = request.POST.get(f"present_{student.id}") == "1"
                check_in_raw = request.POST.get(f"check_in_{student.id}")
                check_out_raw = request.POST.get(f"check_out_{student.id}")
                existing_record = ManualStudentAttendance.objects.filter(student=student, date=selected_date).first()
                existing_check_in = existing_record.check_in_time if existing_record else None
                check_out = _parse_time_value(check_out_raw)

                if is_present:
                    check_in = _parse_time_value(check_in_raw) or existing_check_in or now_time
                    status = "present"
                else:
                    check_in = None
                    status = "absent"

                defaults = {
                    "user": request.effective_user,
                    "status": status,
                    "attendance_status": status,
                    "check_in_time": check_in,
                    "check_out_time": check_out,
                    "late_cutoff_time": cutoff_time,
                    "recorded_at": timezone.now(),
                }
                ManualStudentAttendance.objects.update_or_create(student=student, date=selected_date, defaults=defaults)
        messages.success(request, "Student attendance saved successfully.")
        return redirect(f"{reverse('attendance:manual_student_attendance')}?class_id={selected_class.id}&date={selected_date.isoformat()}&cutoff_time={cutoff_time.strftime('%H:%M') if cutoff_time else ''}")

    total_students = students.count()
    present_count = sum(1 for row in existing_map.values() if row.get("status") == "present")
    late_count = sum(1 for row in existing_map.values() if row.get("status") == "late")
    absent_count = sum(1 for row in existing_map.values() if row.get("status") == "absent")

    return render(request, "attendance/manual_student_attendance.html", {
        "classes": classes,
        "students": students,
        "selected_class": selected_class,
        "selected_date": selected_date,
        "existing_map": existing_map,
        "cutoff_time": cutoff_time,
        "total_students": total_students,
        "present_count": present_count,
        "late_count": late_count,
        "absent_count": absent_count,
    })


@effective_user_decorator
@login_required
def manual_staff_attendance(request):
    selected_date_str = request.GET.get("date") or request.POST.get("date")
    cutoff_str = request.GET.get("cutoff_time") or request.POST.get("cutoff_time")
    selected_date = timezone.localdate()
    cutoff_time = None
    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            messages.warning(request, "Invalid date selected. Showing today.")
    if cutoff_str:
        try:
            cutoff_time = datetime.strptime(cutoff_str, "%H:%M").time()
        except ValueError:
            messages.warning(request, "Invalid cutoff time ignored.")

    selected_role = (request.GET.get("role") or request.POST.get("role") or '').strip().lower()
    teachers = Teacher.objects.filter(created_by=request.effective_user).select_related("user").order_by("teacher_role", "teacherName", "teacher_key")
    if selected_role:
        teachers = teachers.filter(teacher_role=selected_role)
    existing = ManualStaffAttendance.objects.filter(teacher__in=teachers, date=selected_date).select_related("teacher", "teacher__user")
    existing_map = {
        item.teacher_id: {"status": item.attendance_status or item.status, "check_in_time": item.check_in_time, "check_out_time": item.check_out_time}
        for item in existing
    }

    if request.method == "POST":
        teacher_ids = [int(pk) for pk in request.POST.getlist("teacher_ids") if pk.isdigit()]
        teachers_by_id = {teacher.id: teacher for teacher in teachers}
        selected_teachers = [teachers_by_id[teacher_id] for teacher_id in teacher_ids if teacher_id in teachers_by_id]

        def _parse_time_value(raw_value):
            if not raw_value:
                return None
            try:
                return datetime.strptime(raw_value, "%H:%M").time()
            except ValueError:
                return None

        now_time = timezone.localtime().time().replace(second=0, microsecond=0)
        with transaction.atomic():
            for teacher in selected_teachers:
                is_present = request.POST.get(f"present_{teacher.id}") == "1"
                check_in_raw = request.POST.get(f"check_in_{teacher.id}")
                check_out_raw = request.POST.get(f"check_out_{teacher.id}")
                existing_record = ManualStaffAttendance.objects.filter(teacher=teacher, date=selected_date).first()
                existing_check_in = existing_record.check_in_time if existing_record else None
                check_out = _parse_time_value(check_out_raw)

                if is_present:
                    check_in = _parse_time_value(check_in_raw) or existing_check_in or now_time
                    status = "present"
                else:
                    check_in = None
                    status = "absent"

                defaults = {
                    "user": request.effective_user,
                    "status": status,
                    "attendance_status": status,
                    "check_in_time": check_in,
                    "check_out_time": check_out,
                    "late_cutoff_time": cutoff_time,
                    "recorded_at": timezone.now(),
                }
                ManualStaffAttendance.objects.update_or_create(teacher=teacher, date=selected_date, defaults=defaults)
        messages.success(request, "Staff attendance saved successfully.")
        role_query = f"&role={selected_role}" if selected_role else ''
        return redirect(f"{reverse('attendance:manual_staff_attendance')}?date={selected_date.isoformat()}&cutoff_time={cutoff_time.strftime('%H:%M') if cutoff_time else ''}{role_query}")

    total_staff = teachers.count()
    present_count = sum(1 for row in existing_map.values() if row.get("status") == "present")
    late_count = sum(1 for row in existing_map.values() if row.get("status") == "late")
    absent_count = sum(1 for row in existing_map.values() if row.get("status") == "absent")

    return render(request, "attendance/manual_staff_attendance.html", {
        "teachers": teachers,
        "selected_date": selected_date,
        "cutoff_time": cutoff_time,
        "existing_map": existing_map,
        "total_staff": total_staff,
        "late_count": late_count,
        "absent_count": absent_count,
        "present_count": present_count,
        "selected_role": selected_role,
        "role_choices": [('teacher', 'Teacher'), ('accountant', 'Accountant'), ('driver', 'Driver'), ('admin', 'Admin')],
    })


@effective_user_decorator
@login_required
def student_attendance_report(request):
    form = ManualAttendanceFilterForm(request.GET or None)
    classes = TeacherClass.objects.filter(user=request.effective_user, academicclassyear__active_year=True).select_related("ClassName").order_by("ClassName__class_name")
    selected_class_id = request.GET.get("class_id")
    selected_class = None
    records = ManualStudentAttendance.objects.none()
    if form.is_valid() and selected_class_id:
        selected_date = form.cleaned_data["date"]
        view_type = form.cleaned_data["view"]
        search = form.cleaned_data.get("search", "").strip()
        period_start, period_end = _get_period_dates(selected_date, view_type)
        selected_class = get_object_or_404(TeacherClass, id=selected_class_id, user=request.effective_user)
        records = ManualStudentAttendance.objects.filter(
            student__teacherclass=selected_class,
            student__manager=request.effective_user,
            date__range=(period_start, period_end),
        ).select_related("student", "student__user").order_by("-date", "student__fullName")
        if search:
            records = records.filter(Q(student__fullName__icontains=search) | Q(student__indexNumber__icontains=search))
        records = apply_common_attendance_filters(records, form.cleaned_data)
    else:
        selected_date = timezone.localdate()
        view_type = "daily"
        period_start, period_end = selected_date, selected_date

    summary = status_totals(records)
    if request.GET.get("export") == "pdf" and selected_class_id and form.is_valid():
        rows = [{"obj": obj, "person": obj.student} for obj in records]
        return build_attendance_pdf_response(
            filename="student_attendance_report.pdf",
            title="Student Attendance Report",
            filters_summary=_filters_summary(form, selected_class=selected_class),
            rows=rows,
            summary=summary,
            is_staff=False,
        )

    return render(request, "attendance/student_attendance_report.html", {
        "form": form,
        "classes": classes,
        "selected_class_id": selected_class_id,
        "selected_class": selected_class,
        "records": records,
        "summary": summary,
        "period_start": period_start,
        "period_end": period_end,
        "view_type": view_type,
    })


@effective_user_decorator
@login_required
def staff_attendance_report(request):
    form = ManualAttendanceFilterForm(request.GET or None)
    records = ManualStaffAttendance.objects.none()
    if form.is_valid():
        selected_date = form.cleaned_data["date"]
        view_type = form.cleaned_data["view"]
        search = form.cleaned_data.get("search", "").strip()
        period_start, period_end = _get_period_dates(selected_date, view_type)
        records = ManualStaffAttendance.objects.filter(
            teacher__created_by=request.effective_user,
            date__range=(period_start, period_end),
        ).select_related("teacher", "teacher__user").order_by("-date", "teacher__teacherName")
        if search:
            records = records.filter(Q(teacher__teacherName__icontains=search) | Q(teacher__teacher_key__icontains=search))
        records = apply_common_attendance_filters(records, form.cleaned_data)
    else:
        selected_date = timezone.localdate()
        view_type = "daily"
        period_start, period_end = selected_date, selected_date

    summary = status_totals(records)
    if request.GET.get("export") == "pdf" and form.is_valid():
        rows = [{"obj": obj, "person": obj.teacher} for obj in records]
        return build_attendance_pdf_response(
            filename="staff_attendance_report.pdf",
            title="Staff Attendance Report",
            filters_summary=_filters_summary(form),
            rows=rows,
            summary=summary,
            is_staff=True,
        )

    return render(request, "attendance/staff_attendance_report.html", {
        "form": form,
        "records": records,
        "summary": summary,
        "period_start": period_start,
        "period_end": period_end,
        "view_type": view_type,
    })
