from django import template
from rps_app.models import GradingModel, StudentSubject, Student, Teacher, EmailVerificationOTP, Subject, RequiredSubject, Subscriber,PaymentNotification
from attendance.models import StudentAttendance, StaffAttendance
from website.models import Top, Host
from django.utils import timezone
import os
from decimal import Decimal
import re
from django.db.utils import DatabaseError
register = template.Library()



@register.filter
def filter_by_subject(marks_list, subject_id):
    return [mark for mark in marks_list if mark['subject'] == subject_id]
# Student attendance filters
@register.filter
def get_attendance_status(student, date_header):
    
    """
    Returns the attendance status for a student on a given date.
    - 'P' if present, 'A' if absent or no record, '-' for future dates.
    """
    today = timezone.now().date()
    if date_header > today:
        return "-"
    try:
        attendance = StudentAttendance.objects.get(
            student=student,
            date=date_header
        )
        return "P" if attendance.status == "present" else "A"
    except StudentAttendance.DoesNotExist:
        return "A" if date_header <= today else "-"

@register.filter
def count_present(student, date_headers):
    """
    Returns the number of days the student was marked present within the date range.
    Only counts days up to the current date.
    """
    today = timezone.now().date()
    date_range = [d for d in date_headers if d <= today]
    if not date_range:
        return 0
    return StudentAttendance.objects.filter(
        student=student,
        date__in=date_range,
        status='present'
    ).count()

@register.filter
def count_absent(student, date_headers):
    """
    Returns the number of days the student was marked absent or had no record
    within the date range, up to the current date.
    """
    today = timezone.now().date()
    date_range = [d for d in date_headers if d <= today]
    if not date_range:
        return 0
    present_count = StudentAttendance.objects.filter(
        student=student,
        date__in=date_range,
        status='present'
    ).count()
    total_days = len(date_range)
    absent_count = total_days - present_count
    return absent_count


@register.filter
def get_teacher_status(teacher, date_header):
    """
    Returns the attendance status for a teacher on a given date.
    - 'P' if present, 'A' if absent (or no record for past days), '-' for future days.
    """
    today = timezone.now().date()
    if date_header > today:
        return "-"
    try:
        attendance = StaffAttendance.objects.get(
            teacher=teacher,
            date=date_header
        )
        return "P" if attendance.status.lower() == "present" else "A"
    except StaffAttendance.DoesNotExist:
        return "A" if date_header <= today else "-"

@register.filter
def count_teacher_present(teacher, date_headers):
    """
    Returns the number of days the teacher was marked present within the date range.
    Only counts days up to the current date.
    """
    today = timezone.now().date()
    date_range = [d for d in date_headers if d <= today]
    if not date_range:
        return 0
    return StaffAttendance.objects.filter(
        teacher=teacher,
        date__in=date_range,
        status='present'
    ).count()


@register.filter
def attendance_rate(present_count, total_days):
    try:
        if total_days == 0:
            return 0  # Avoid division by zero
        return round((present_count / total_days) * 100, 2)  # Calculate percentage
    except (TypeError, ValueError):
        return 0  # Return 0 if there's an error (e.g., non-numeric input)



@register.filter
def count_teacher_absent(teacher, date_headers):
    """
    Returns the number of days the teacher was marked absent or had no record
    within the date range, up to the current date.
    """
    today = timezone.now().date()
    date_range = [d for d in date_headers if d <= today]
    if not date_range:
        return 0
    present_count = StaffAttendance.objects.filter(
        teacher=teacher,
        date__in=date_range,
        status='present'
    ).count()
    total_days = len(date_range)
    absent_count = total_days - present_count
    return absent_count

# Existing filters (unchanged)
@register.filter
def safedict(value, key):
    try:
        return value.get(key, {})
    except (AttributeError, TypeError):
        return {}

@register.filter
def lookup_dict(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(str(key), '-')
    return '-'

@register.filter
def date_from_header(header):
    # Convert header to string if it's an integer, then extract day number
    header_str = str(header)
    day = int(re.sub(r'[^0-9]', '', header_str))
    return day

@register.filter
def escape_latex(text):
    """Escape special LaTeX characters in a string."""
    if not isinstance(text, str):
        text = str(text)
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    return ''.join(latex_special_chars.get(c, c) for c in text)

@register.filter
def multiply(value, arg):
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def get_item(dictionary, key):
    """Retrieve an item from a dictionary by key, returning None if not found."""
    return dictionary.get(key) if dictionary else None

@register.filter
def student_subjects(student_id):
    """Return a list of subject IDs for a given student."""
    return list(StudentSubject.objects.filter(student__id=student_id).values_list('subject__id', flat=True))

@register.filter
def get_grade(value):
    """Convert a numeric mark to a letter grade based on the first GradingModel."""
    if value == '-' or value is None:
        return '-'
    grading = GradingModel.objects.first()
    if not grading:
        return '-'
    try:
        value = float(value)
        if grading.is_advance:
            if value >= grading.grade_a: return 'A'
            elif value >= grading.grade_b: return 'B'
            elif value >= grading.grade_c: return 'C'
            elif value >= grading.grade_d: return 'D'
            elif value >= grading.grade_e: return 'E'
            elif value >= grading.grade_s: return 'S'
            else: return 'F'
        else:
            if value >= grading.grade_a: return 'A'
            elif value >= grading.grade_b: return 'B'
            elif value >= grading.grade_c: return 'C'
            elif value >= grading.grade_d: return 'D'
            else: return 'F'
    except (ValueError, TypeError):
        return '-'

@register.filter
def is_student(user):
    """Check if the user is an instance of the Student model."""
    return isinstance(user, Student)

@register.filter
def basename(value):
    return os.path.basename(value)


@register.filter
def has_verified_email(user):
    try:
        return EmailVerificationOTP.objects.filter(
            user=user,
            is_verified=True,
            purpose='verification'
        ).exists()
    except DatabaseError:
        return False

@register.filter
def is_user_subscribed(user):
    return PaymentNotification.objects.filter(
        user=user,
        success_payment=True
    ).exists()

@register.filter
def is_verified_student(user):
    """
    Check if the user is a Student (not a Teacher) and their email is verified.
    """
    if not user.is_authenticated or not isinstance(user, Student) or hasattr(user, 'teacher'):
        return False
    return EmailVerificationOTP.objects.filter(
        user=user,
        purpose='verification',
        is_verified=True
    ).exists()

@register.filter
def filter_by_level(queryset, level):
    """
    Filter RequiredSubject queryset by level (Olevel or Alevel).
    If level is empty, return the entire queryset.
    """
    if level:
        return queryset.filter(level=level)
    return queryset

@register.filter
def filter_subject_by_level(subject, level):
    """
    Check if a Subject instance has a corresponding RequiredSubject entry with the specified level.
    """
    if not level:
        return True
    if isinstance(subject, Subject):
        return RequiredSubject.objects.filter(subject=subject, level=level, user=subject.user).exists()
    return False

@register.filter(name='subtract')
def subtract(value, arg):
    """Subtracts the argument from the value."""
    try:
        return Decimal(value) - Decimal(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except (ValueError, TypeError):
            return ''

@register.filter
def icon_for_host(host):
    """
    Given a host instance, return the URL of the icon_required
    from the Top object related to that host.
    """
    try:
        top = Top.objects.filter(host_required=host).first()
        if top and top.icon_required:
            return top.icon_required.url
    except Exception:
        pass
    return ''

@register.filter
def bootstrap_message_class(message_tags):
    """
    Maps Django message tags to Bootstrap toast contextual classes.
    """
    tag_map = {
        'success': 'text-bg-success',
        'error': 'text-bg-danger',
        'warning': 'text-bg-warning',
        'info': 'text-bg-info',
        'debug': 'text-bg-secondary',
    }
    return tag_map.get(message_tags, 'text-bg-secondary')




@register.filter
def basename(value):
    """Extract the file name from a file path."""
    return os.path.basename(value)



@register.filter
def has_permission(teacher, permission_name):
    """
    Custom template filter to check if a teacher has a specific permission.
    
    Usage in template: {% if teacher|has_permission:"can_view_attendance" %}
    Returns True if the teacher has the permission set to True, False otherwise.
    Handles cases where no UserPermission exists for the teacher.
    """
    if not hasattr(teacher, 'userpermission') or not teacher.userpermission:
        return False
    permission_value = getattr(teacher.userpermission, permission_name, False)
    return bool(permission_value)



@register.filter
def replace(value, args):
    """
    Replace substring in a string.
    Usage: {{ value|replace:"old:new" }}
    Example: {{ "Hello & World"|replace:" & :-" }} → "Hello-World"
    """
    if not value:
        return value
    old, new = args.split(':')
    return value.replace(old, new)