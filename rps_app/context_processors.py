# website/context_processors.py
from urllib.parse import urlparse
from django.conf import settings
from website.models import Host, Top
import logging

logger = logging.getLogger(__name__)

def top_icon_context(request):
    icon_url = ''
    host = None
    top = None
    # footer = None
    host_name = ''
    
    try:
        full_host = request.get_host()  # e.g., 'localhost:9000'
        host_name = full_host.split(':')[0]  # Strip port
        logger.debug(f"Processing hostname: {host_name}")
        
        # Fetch Host by hostname
        try:
            host = Host.objects.get(host_name=host_name)
            logger.info(f"Retrieved host for hostname: {host_name}")
        except Host.DoesNotExist:
            logger.warning(f"No host found for hostname: {host_name}")
        
        # Fetch Top and Footer objects
        if host:
            top = Top.objects.filter(host_required=host).last()
            # footer = Footer.objects.filter(host_required=host).last()
            if top and top.icon_required:
                icon_url = top.icon_required.url
                logger.debug(f"Icon URL set to: {icon_url}")
        
    except Exception as e:
        logger.error(f"Error in top_icon_context: {str(e)}")
    
    return {
        'global_host': host,
        'global_top_icon': icon_url,
        'top': top,
        'host_name': host_name,
        # 'footer': footer,
    }


# rps_app/context_processors.py
from .models import Teacher  # Import your Teacher model
import logging

logger = logging.getLogger(__name__)

def global_context(request):
    """
    Adds the current user's Teacher profile to the global template context
    if they are an authenticated teacher and a profile exists.
    Does NOT create a profile if one is missing (e.g., for students).
    """
    context = {}
    if request.user.is_authenticated and getattr(request.user, 'is_teacher', False):
        try:
            # Fetch existing Teacher profile only (no creation)
            teacher = Teacher.objects.filter(user=request.user).first()
            if teacher:
                context['teacher'] = teacher
                logger.debug(f"Retrieved Teacher profile for user {request.user.username}")
            else:
                logger.debug(f"No Teacher profile found for teacher user {request.user.username}")
        except Exception as e:
            logger.error(f"Error fetching Teacher profile for {request.user.username}: {e}")
            # Fallback: Don't add 'teacher' to context if error
    return context


# context_processors.py
# context_processors.py
from rps_app.models import ChatMessage, Student, Teacher

def chat_notifications(request):
    """
    Context processor for global chat notifications.
    Returns unread count and recent messages with proper sender details.
    """
    if not request.user.is_authenticated:
        return {
            'unread_count': 0,
            'recent_messages': [],
            'global_top_icon': '/static/innobanks.png'  # Default icon
        }

    # Count only UNREAD messages (status < 2 means not seen)
    unread_count = ChatMessage.objects.filter(
        receiver=request.user,
        is_read=False  # Use is_read field for accuracy
    ).count()

    # Get recent messages with sender details
    recent_messages_qs = ChatMessage.objects.filter(
        receiver=request.user
    ).select_related('sender').order_by('-timestamp')[:5]

    # Enhance recent messages with sender profile data
    recent_messages = []
    for msg in recent_messages_qs:
        # Get sender's profile photo
        sender_photo = None
        
        # Check if sender is a student
        student_profile = Student.objects.filter(user=msg.sender).first()
        if student_profile and student_profile.photo:
            sender_photo = student_profile.photo.url
        else:
            # Check if sender is a teacher
            teacher_profile = Teacher.objects.filter(user=msg.sender).first()
            if teacher_profile and teacher_profile.photo:
                sender_photo = teacher_profile.photo.url
        
        # Add enhanced message data
        msg.sender_photo = sender_photo
        msg.sender_fullname = msg.sender.get_full_name() or msg.sender.username
        recent_messages.append(msg)

    # Get current user's profile icon for global display
    global_top_icon = '/static/innobanks.png'  # Default
    
    # Try to get user's own profile photo
    user_student = Student.objects.filter(user=request.user).first()
    if user_student and user_student.photo:
        global_top_icon = user_student.photo.url
    else:
        user_teacher = Teacher.objects.filter(user=request.user).first()
        if user_teacher and user_teacher.photo:
            global_top_icon = user_teacher.photo.url

    return {
        'unread_count': unread_count,
        'recent_messages': recent_messages,
        'global_top_icon': global_top_icon,
    }