# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from .models import User  # Adjust the import based on your project structure

# class CustomJWTAuthentication(JWTAuthentication):
#     def get_user(self, validated_token):
#         user_id = validated_token.get('user_id')

#         if user_id is None:
#             raise AuthenticationFailed('User ID is missing from token.')

#         try:
#             return User.objects.get(id=user_id)  # Ensure `id` matches the type
#         except User.DoesNotExist:
#             raise AuthenticationFailed('User not found')


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from bson.objectid import ObjectId  # Import ObjectId

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')

        if user_id is None:
            raise AuthenticationFailed('User ID is missing from token.')

        try:
            user = User.objects.get(id=ObjectId(user_id))  # Convert to ObjectId
            return user
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
