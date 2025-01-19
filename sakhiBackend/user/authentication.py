from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user_id = validated_token.get('user_id')

        if user_id is None:
            raise AuthenticationFailed('User ID is missing from token.')

        try:
            # If user_id is an integer, Django will automatically handle it
            user = User.objects.get(id=user_id)  # Query by integer ID
            return user
        except (User.DoesNotExist, ValueError, TypeError) as e:
            raise AuthenticationFailed(f'Error fetching user: {str(e)}')
