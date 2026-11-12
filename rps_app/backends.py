# # rps_app/backends.py
# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model
# from rps_app.models import Student, Teacher
# import logging

# logger = logging.getLogger(__name__)

# class CombinedAuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         UserModel = get_user_model()  # rps_app.Teacher
#         try:
#             # Try authenticating as a Teacher
#             teacher = UserModel.objects.get(username=username)
#             if teacher.check_password(password) and self.user_can_authenticate(teacher):
#                 logger.debug(f"Authenticated as Teacher: {teacher.username}, id: {teacher.id}")
#                 return teacher
#         except UserModel.DoesNotExist:
#             try:
#                 # Try authenticating as a Student
#                 student = Student.objects.get(indexNumber=username)
#                 if student.check_password(password) and self.user_can_authenticate(student):
#                     logger.debug(f"Authenticated as Student: {student.fullName}, indexNumber={student.indexNumber}, id: {student.id}")
#                     return student
#             except Student.DoesNotExist:
#                 logger.debug(f"No user found for username/indexNumber={username}")
#                 return None

#     def get_user(self, user_id):
#         UserModel = get_user_model()
#         try:
#             # Try retrieving a Teacher
#             teacher = UserModel.objects.get(pk=user_id)
#             logger.debug(f"Retrieved Teacher: {teacher.username}, id: {teacher.id}")
#             return teacher
#         except UserModel.DoesNotExist:
#             try:
#                 # Try retrieving a Student
#                 student = Student.objects.get(pk=user_id)
#                 logger.debug(f"Retrieved Student: {student.fullName}, indexNumber={student.indexNumber}, id: {student.id}")
#                 return student
#             except Student.DoesNotExist:
#                 logger.debug(f"No user found for user_id={user_id}")
#                 return None

#     def user_can_authenticate(self, user):
#         return getattr(user, 'is_active', True)