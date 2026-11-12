from django.apps import apps
from django.conf import settings
import logging

# Set up logging
logger = logging.getLogger(__name__)

def get_email_settings(user):
    """
    Retrieve email settings for a given user. For non-superusers, use the creator's email configuration.
    
    Args:
        user: The authenticated user instance.
    
    Returns:
        dict: A dictionary containing email configuration settings.
    """
    try:
        EmailConfiguration = apps.get_model('rps_app', 'EmailConfiguration')
        
        # Check if the user is a superuser
        if user.is_superuser:
            try:
                config = EmailConfiguration.objects.get(user=user)
                logger.info(f"Retrieved email configuration for superuser: {user.username}")
                return {
                    'EMAIL_BACKEND': config.email_backend,
                    'EMAIL_HOST': config.email_host,
                    'EMAIL_PORT': config.email_port,
                    'EMAIL_USE_TLS': config.email_use_tls,
                    'EMAIL_HOST_USER': config.email_host_user,
                    'EMAIL_HOST_PASSWORD': config.email_host_password,
                    'DEFAULT_FROM_EMAIL': config.default_from_email,
                }
            except EmailConfiguration.DoesNotExist:
                logger.warning(f"No email configuration found for superuser: {user.username}. Using default settings.")
                pass
        else:
            # For non-superusers, check if they are a teacher or student
            Teacher = apps.get_model('rps_app', 'Teacher')
            Student = apps.get_model('rps_app', 'Student')
            
            creator = None
            try:
                # Check if the user has a Teacher profile
                teacher = Teacher.objects.get(user=user)
                creator = teacher.created_by
            except Teacher.DoesNotExist:
                try:
                    # Check if the user has a Student profile
                    student = Student.objects.get(user=user)
                    creator = student.manager
                except Student.DoesNotExist:
                    logger.warning(f"No teacher or student profile found for user: {user.username}")
            
            if creator:
                try:
                    config = EmailConfiguration.objects.get(user=creator)
                    logger.info(f"Retrieved email configuration for creator: {creator.username}")
                    return {
                        'EMAIL_BACKEND': config.email_backend,
                        'EMAIL_HOST': config.email_host,
                        'EMAIL_PORT': config.email_port,
                        'EMAIL_USE_TLS': config.email_use_tls,
                        'EMAIL_HOST_USER': config.email_host_user,
                        'EMAIL_HOST_PASSWORD': config.email_host_password,
                        'DEFAULT_FROM_EMAIL': config.default_from_email,
                    }
                except EmailConfiguration.DoesNotExist:
                    logger.warning(f"No email configuration found for creator: {creator.username}. Using default settings.")
            
        # Fallback to default settings if no configuration is found
        logger.info("Using default email settings.")
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': 587,
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST_USER': 'britishschooltz9@gmail.com',
            'EMAIL_HOST_PASSWORD': 'asck jcua lrxe yshb',
            'DEFAULT_FROM_EMAIL': 'britishschooltz9@gmail.com',
        }
    except Exception as e:
        logger.error(f"Error retrieving email settings for user {user.username}: {str(e)}")
        # Fallback to default settings on any error
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
            'EMAIL_HOST': 'smtp.gmail.com',
            'EMAIL_PORT': 587,
            'EMAIL_USE_TLS': True,
            'EMAIL_HOST_USER': 'britishschooltz9@gmail.com',
            'EMAIL_HOST_PASSWORD': 'asck jcua lrxe yshb',
            'DEFAULT_FROM_EMAIL': 'britishschooltz9@gmail.com',
        }


def get_sms_configuration(user):
    """
    Retrieve SMS configuration for a given user. For non-superusers, use the creator's SMS configuration.

    Args:
        user: The authenticated user instance.

    Returns:
        SmsConfiguration instance or None if not found.
    """
    try:
        SmsConfiguration = apps.get_model('rps_app', 'SmsConfiguration')

        if user.is_superuser:
            try:
                config = SmsConfiguration.objects.get(user=user)
                logger.info("Retrieved SMS configuration for superuser: %s", user.username)
                return config
            except SmsConfiguration.DoesNotExist:
                logger.warning("No SMS configuration found for superuser: %s", user.username)
                return None

        Teacher = apps.get_model('rps_app', 'Teacher')
        Student = apps.get_model('rps_app', 'Student')

        creator = None
        try:
            teacher = Teacher.objects.get(user=user)
            creator = teacher.created_by
        except Teacher.DoesNotExist:
            try:
                student = Student.objects.get(user=user)
                creator = student.manager
            except Student.DoesNotExist:
                logger.warning("No teacher or student profile found for user: %s", user.username)

        if creator:
            try:
                config = SmsConfiguration.objects.get(user=creator)
                logger.info("Retrieved SMS configuration for creator: %s", creator.username)
                return config
            except SmsConfiguration.DoesNotExist:
                logger.warning("No SMS configuration found for creator: %s", creator.username)
                return None
    except Exception as exc:
        logger.error("Error retrieving SMS configuration for user %s: %s", user.username, exc)

    return None
