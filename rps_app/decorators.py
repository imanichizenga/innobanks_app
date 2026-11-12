from functools import wraps
from django.shortcuts import render
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Teacher  # Adjust import based on your app structure

def effective_user_decorator(view_func):
    """
    A custom decorator that sets request.effective_user based on the current user.
    - If the user is a superuser, effective_user = request.user
    - Otherwise, effective_user = teacher_profile.created_by (fetches Teacher profile), fallback to request.user if None
    
    Usage:
    @effective_user_decorator
    def my_view(request):
        # In the view, use request.effective_user in filters instead of request.user
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.user.is_superuser:
                request.effective_user = request.user
            else:
                try:
                    teacher_profile = Teacher.objects.get(user=request.user)
                    creator = teacher_profile.created_by
                    request.effective_user = creator or request.user  # Fallback to self if no creator
                except Teacher.DoesNotExist:
                    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
                    if is_ajax:
                        return JsonResponse({'error': 'Teacher profile not found. Access denied.'}, status=403)
                    else:
                        messages.error(request, "Teacher profile not found. Access denied.")
                        return render(request, 'error.html', {'message': 'Profile not found'})  # Adjust template as needed
        else:
            # Handle unauthenticated user (though @login_required should prevent this)
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            if is_ajax:
                return JsonResponse({'error': 'Authentication required.'}, status=401)
            else:
                return render(request, 'login.html')  # Adjust as needed
        
        response = view_func(request, *args, **kwargs)
        # Optionally clean up the attribute after the view runs
        if hasattr(request, 'effective_user'):
            delattr(request, 'effective_user')
        return response
    return wrapper