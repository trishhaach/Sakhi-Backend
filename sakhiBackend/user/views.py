from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from user.serializers import UserRegistrationSerializer, UserLoginSerializer
from user.models import User
from user.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken

# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'errors': {'non_field_error': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
            
            if user.check_password(password):
                token = get_tokens_for_user(user)  
                return Response({'token': token, 'msg': 'Login Success'},status=status.HTTP_200_OK
                )
            else:
                return Response({'errors': {'non_field_error': ['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)
           
