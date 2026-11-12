from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from rps_app.models import Teacher
import logging

logger = logging.getLogger(__name__)

def accountant_role_required(view_func):
    """Decorator to ensure the user is authenticated and has accountant permissions."""
    @login_required
    def wrapper(request, *args, **kwargs):
        try:
            if request.user.is_superuser:
                # Superusers are their own creators
                request.creator = request.user
                logger.debug(f"Superuser {request.user.username} set as creator")
            else:
                # For non-superusers, retrieve creator from Teacher profile
                try:
                    teacher_profile = Teacher.objects.get(user=request.user)
                    creator = teacher_profile.created_by
                    if not creator:
                        logger.warning(f"User {request.user.username} has no creator assigned, defaulting to self")
                        request.creator = request.user  # Fallback to user
                    else:
                        request.creator = creator
                        logger.debug(f"User {request.user.username} assigned creator {creator.username}")
                except Teacher.DoesNotExist:
                    logger.warning(f"Teacher profile not found for user {request.user.username}, defaulting to self")
                    request.creator = request.user  # Fallback to user
            return view_func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in accountant_role_required for user {request.user.username}: {str(e)}", exc_info=True)
            messages.error(request, "An error occurred while verifying your permissions.")
            return redirect('teacher_dashboard')
    return wrapper