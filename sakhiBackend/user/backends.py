# # user/backends.py
# from django.contrib.auth.backends import BaseBackend
# from .models import User

# class MongoEngineBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None, **kwargs):
#         try:
#             # Assuming the user uses the email for login
#             user = User.objects.get(email=username)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return None
