from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from user.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer, UserUpdateSerializer
from user.models import User
from user.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from user.utils import Util
from .models import NonClinicalDetection, AdvancedDetection
from .serializers import NonClinicalDetectionResultSerializer, AdvancedDetectionResultSerializer
from user.serializers import NonClinicalDetectionSerializer, AdvancedDetectionSerializer
from drf_yasg.utils import swagger_auto_schema

# from allauth.socialaccount.models import SocialAccount

# Generate Token Manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    print(f"Generated refresh token: {str(refresh)}")  
    print(f"Generated access token: {str(refresh.access_token)}")  
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

            # Generate token
            token = get_tokens_for_user(user)

            # Send Welcome Email
            body = f"Welcome to Sakhi! You have successfully signed up with us, {user.name}."
            data = {
                'subject': 'Welcome to Sakhi!',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)

            return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            print(f"Trying to login with email: {email}")
            
            # Corrected query to filter users by email
            user = User.objects.filter(email=email).first()
            
            if user:
                print("User found.")
                if user.check_password(password):
                    token = get_tokens_for_user(user)
                    return Response({'token': token, 'msg': 'Login Success'}, status=status.HTTP_200_OK)
                else:
                    print("Invalid password.")
            else:
                print("User not found.")
            return Response({'errors': {'non_field_error': ['Email or Password is not Valid']}}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({'msg':'Password Changed Sucessfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendPasswordResetEmailView(APIView):
    renderer_classes_classes = [UserRenderer]
    def post(self, request, format=None):
        seriallizer = SendPasswordResetEmailSerializer(data=request.data)
        if seriallizer.is_valid(raise_exception=True):
            return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)
        return Response(seriallizer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordResetView(APIView):
    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = UserPasswordResetSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save(uidb64, token)
                return Response({'success': 'Password reset successful.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class GoogleLoginCallbackView(APIView):
#     permission_classes = [IsAuthenticated]  # Only authenticated users can hit this endpoint

#     def get(self, request, *args, **kwargs):
#         try:
#             # Retrieve the social account (Google account) associated with the logged-in user
#             social_account = SocialAccount.objects.get(user=request.user, provider='google')
            
#             # You can now create or retrieve the user from the SocialAccount
#             user = social_account.user
            
#             # Generate tokens for the user
#             refresh = RefreshToken.for_user(user)
            
#             # Return the JWT tokens
#             return Response({
#                 'access_token': str(refresh.access_token),
#                 'refresh_token': str(refresh),
#             }, status=200)
#         except SocialAccount.DoesNotExist:
#             return Response({'error': 'Google account is not linked'}, status=400)


# Non-Clinical Detection API
class NonClinicalDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = NonClinicalDetectionSerializer(data=request.data)
        if serializer.is_valid():
            # Save the detection result with the logged-in user
            detection = serializer.save(user=request.user, prediction="PCOS Detected")
            return Response({'msg': 'Non-Clinical Detection successful', 'prediction': detection.prediction}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Advanced Detection API
class AdvancedDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = AdvancedDetectionSerializer(data=request.data)
        if serializer.is_valid():
            # Save the detection result with the logged-in user
            detection = serializer.save(user=request.user, prediction="PCOS Detected")
            return Response({'msg': 'Advanced Detection successful', 'prediction': detection.prediction}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View to get Non-Clinical Detection Results
class NonClinicalDetectionResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Get the latest non-clinical detection result for the user
        non_clinical_result = NonClinicalDetection.objects.filter(user=request.user).last()

        if non_clinical_result:
            # Return the non-clinical results in response
            serializer = NonClinicalDetectionResultSerializer(non_clinical_result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No non-clinical detection result found'}, status=status.HTTP_404_NOT_FOUND)

# View to get Advanced Detection Results
class AdvancedDetectionResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # Get the latest advanced detection result for the user
        advanced_result = AdvancedDetection.objects.filter(user=request.user).last()

        if advanced_result:
            # Return the advanced results in response
            serializer = AdvancedDetectionResultSerializer(advanced_result)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'msg': 'No advanced detection result found'}, status=status.HTTP_404_NOT_FOUND)


class UserUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, format=None):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)  # Only update the fields provided

        if serializer.is_valid():
            serializer.save()  # Save the updated user information
            return Response({'msg': 'User name updated successfully'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API for Deleting User Account and Related Data
class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None):
        user = request.user

        # Delete related data
        NonClinicalDetection.objects.filter(user=user).delete()
        AdvancedDetection.objects.filter(user=user).delete()

        # Finally, delete the user account
        user.delete()

        return Response({'msg': 'User account and all related data deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)