from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from user.serializers import UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer, UserChangePasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer, UserUpdateSerializer
from user.models import User
from user.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from user.utils import Util
from .models import NonClinicalDetection, AdvancedDetection, Period
from .serializers import NonClinicalDetectionResultSerializer, AdvancedDetectionResultSerializer, TrackPeriodSerializer, TrackPeriodHistorySerializer
from user.serializers import NonClinicalDetectionSerializer, AdvancedDetectionSerializer
from drf_yasg.utils import swagger_auto_schema
import requests
import logging
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from datetime import timedelta
from django.utils import timezone
from .models import SymptomCategory, Symptom
from .models import SymptomTrack
from .serializers import SymptomCategorySerializer, SymptomSerializer
from .serializers import SymptomTrackSerializer
from rest_framework import status, generics
from rest_framework import serializers
from django.db import transaction


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

# class SendPasswordResetEmailView(APIView):
#     renderer_classes_classes = [UserRenderer]
#     def post(self, request, format=None):
#         seriallizer = SendPasswordResetEmailSerializer(data=request.data)
#         if seriallizer.is_valid(raise_exception=True):
#             return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)
#         return Response(seriallizer.errors, status=status.HTTP_400_BAD_REQUEST)


class SendPasswordResetEmailView(APIView):
    renderer_classes = [UserRenderer]
    
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            
            # Generate reset token and uidb64 for the user
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
            
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            
            # Construct the password reset URL (use your frontend's domain here)
            frontend_url = f"http://localhost:3000/reset-password/{uidb64}/{token}"
            
            # Send email with the reset URL
            body = f"Click the link below to reset your password:\n\n{frontend_url}"
            data = {
                'subject': 'Password Reset Request',
                'body': body,
                'to_email': email
            }
            Util.send_email(data)
            
            return Response({'msg': 'Password reset link sent. Please check your email'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


# logger = logging.getLogger(__name__)

# class NonClinicalDetectionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, format=None):
#         # Deserialize the input data
#         serializer = NonClinicalDetectionSerializer(data=request.data)
#         if serializer.is_valid():
#             # Prepare the input data to send to the ML model
#             detection_data = serializer.validated_data
#             model_input = {
#                 "skin_darkening": detection_data["skin_darkening"],
#                 "hair_growth": detection_data["hair_growth"],
#                 "weight_gain": detection_data["weight_gain"],
#                 "cycle_length": detection_data["cycle_length"],  # Ensure this is added here
#                 "fast_food": detection_data["fast_food"],
#                 "pimples": detection_data["pimples"],
#                 "age": detection_data["age"],
#                 "bmi": detection_data["bmi"]
#             }

#             # Define the URL for the ML model API
#             url = "https://appledog00-nonclinical-prediction.hf.space/predict"
#             headers = {
#                 'Content-Type': 'application/json'
#             }

#             try:
#                 # Make the request to the model API
#                 response = requests.post(url, json=model_input, headers=headers)

#                 # Log the response status code and content for debugging
#                 logger.info(f"Model API response: {response.status_code}, {response.text}")

#                 # Check if the response is successful
#                 if response.status_code == 200:
#                     prediction = response.json()

#                     # Ensure the prediction contains the required fields
#                     predicted_class = prediction.get('predicted_class')
#                     prediction_probability = prediction.get('prediction_probability_for_class_1')

#                     if predicted_class is None or prediction_probability is None:
#                         logger.error(f"Missing prediction data in response: {response.text}")
#                         return Response({
#                             'error': 'Prediction data is missing from the model response'
#                         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#                     # Save the detection result in the database
#                     detection = NonClinicalDetection.objects.create(
#                         user=request.user,
#                         skin_darkening=detection_data["skin_darkening"],
#                         hair_growth=detection_data["hair_growth"],
#                         weight_gain=detection_data["weight_gain"],
#                         cycle_length=detection_data["cycle_length"],  # Ensure cycle_length is included here
#                         fast_food=detection_data["fast_food"],
#                         pimples=detection_data["pimples"],
#                         age=detection_data["age"],
#                         bmi=detection_data["bmi"],
#                         prediction="PCOS Detected" if predicted_class == 1 else "No PCOS Detected",
#                         prediction_probability=prediction_probability
#                     )

#                     # Return the successful response with prediction and probability
#                     return Response({
#                         'msg': 'Non-Clinical Detection successful',
#                         'prediction': detection.prediction,
#                         'probability': detection.prediction_probability
#                     }, status=status.HTTP_201_CREATED)

#                 else:
#                     # If the model API returns an error, log it and return a 500 response
#                     logger.error(f"Error from ML model: {response.status_code} - {response.text}")
#                     return Response({
#                         'error': 'Error communicating with the ML model'
#                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             except requests.exceptions.Timeout:
#                 # Handle timeout exception specifically
#                 logger.error("Request to the ML model timed out")
#                 return Response({
#                     'error': 'The request to the ML model timed out'
#                 }, status=status.HTTP_504_GATEWAY_TIMEOUT)

#             except requests.exceptions.ConnectionError:
#                 # Handle connection error specifically
#                 logger.error("Connection error while trying to reach the ML model")
#                 return Response({
#                     'error': 'Unable to connect to the ML model'
#                 }, status=status.HTTP_502_BAD_GATEWAY)

#             except requests.exceptions.RequestException as e:
#                 # General request exception handling
#                 logger.error(f"RequestException occurred: {str(e)}")
#                 return Response({
#                     'error': f'An error occurred while contacting the ML model: {str(e)}'
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # If serializer is invalid, return a 400 response with errors
#         logger.error(f"Invalid input data: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger(__name__)

class NonClinicalDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = NonClinicalDetectionSerializer(data=request.data)
        if serializer.is_valid():
            detection_data = serializer.validated_data
            model_input = {
                "skin_darkening": detection_data["skin_darkening"],
                "hair_growth": detection_data["hair_growth"],
                "weight_gain": detection_data["weight_gain"],
                "cycle_length": detection_data["cycle_length"],
                "fast_food": detection_data["fast_food"],
                "pimples": detection_data["pimples"],
                "age": detection_data["age"],
                "bmi": detection_data["bmi"]
            }

            url = "https://appledog00-nonclinical-prediction.hf.space/predict"
            headers = {'Content-Type': 'application/json'}

            try:
                response = requests.post(url, json=model_input, headers=headers)
                logger.info(f"Model API response: {response.status_code}, {response.text}")

                if response.status_code == 200:
                    prediction = response.json()
                    predicted_class = prediction.get('predicted_class')
                    prediction_probability = prediction.get('prediction_probability_for_class_1')

                    if predicted_class is None or prediction_probability is None:
                        logger.error(f"Missing prediction data in response: {response.text}")
                        return Response({'error': 'Prediction data is missing from the model response'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    detection = NonClinicalDetection.objects.create(
                        user=request.user,
                        skin_darkening=detection_data["skin_darkening"],
                        hair_growth=detection_data["hair_growth"],
                        weight_gain=detection_data["weight_gain"],
                        cycle_length=detection_data["cycle_length"],
                        fast_food=detection_data["fast_food"],
                        pimples=detection_data["pimples"],
                        age=detection_data["age"],
                        bmi=detection_data["bmi"],
                        prediction="PCOS Detected" if predicted_class == 1 else "No PCOS Detected",
                        prediction_probability=prediction_probability
                    )

                    message = "Please consult with the nearest gynecologist or hospital." if predicted_class == 1 else "Congratulations! You are not prone to PCOS. Maintain a healthy lifestyle and stay aware."

                    return Response({
                        'msg': 'Non-Clinical Detection successful',
                        'prediction': detection.prediction,
                        'probability': detection.prediction_probability,
                        'advice': message
                    }, status=status.HTTP_201_CREATED)

                else:
                    logger.error(f"Error from ML model: {response.status_code} - {response.text}")
                    return Response({'error': 'Error communicating with the ML model'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except requests.exceptions.Timeout:
                logger.error("Request to the ML model timed out")
                return Response({'error': 'The request to the ML model timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)

            except requests.exceptions.ConnectionError:
                logger.error("Connection error while trying to reach the ML model")
                return Response({'error': 'Unable to connect to the ML model'}, status=status.HTTP_502_BAD_GATEWAY)

            except requests.exceptions.RequestException as e:
                logger.error(f"RequestException occurred: {str(e)}")
                return Response({'error': f'An error occurred while contacting the ML model: {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.error(f"Invalid input data: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# logger = logging.getLogger(__name__)

# class AdvancedDetectionView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, format=None):
#         serializer = AdvancedDetectionSerializer(data=request.data)
#         if serializer.is_valid():
#             # Prepare the input data to send to the ML model
#             detection_data = serializer.validated_data
#             model_input = {
#                 "Follicle_No_R": detection_data["follicle_no_r"],
#                 "Follicle_No_L": detection_data["follicle_no_l"],
#                 "Skin_darkening": detection_data["skin_darkening"],
#                 "hair_growth": detection_data["hair_growth"],
#                 "Weight_gain": detection_data["weight_gain"],
#                 "Cycle_length": detection_data["cycle_length"],
#                 "AMH": detection_data["amh"],
#                 "Fast_food": detection_data["fast_food"],
#                 "Cycle_R_I": detection_data["cycle_r_i"],
#                 "FSH_LH": detection_data["fsh_lh"],
#                 "PRL": detection_data["prl"],
#                 "Pimples": detection_data["pimples"],
#                 "Age": detection_data["age"],
#                 "BMI": detection_data["bmi"]
#             }

#             # Define the URL for the ML model API
#             url = "https://appledog00-Project-Sakhii.hf.space/predict/"
#             headers = {'Content-Type': 'application/json'}

#             try:
#                 # Make the request to the model API
#                 response = requests.post(url, json=model_input, headers=headers)
#                 logger.info(f"Model API response: {response.status_code}, {response.text}")

#                 if response.status_code == 200:
#                     prediction = response.json()

#                     # Extract the prediction data from the API response
#                     predicted_class = prediction.get('prediction')  # Now use 'prediction' instead of 'predicted_class'
#                     prediction_probability = prediction.get('probability')  # Now use 'probability' instead of 'prediction_probability'

#                     if predicted_class is None or prediction_probability is None:
#                         logger.error(f"Missing prediction data in response: {response.text}")
#                         return Response({
#                             'error': 'Prediction data is missing from the model response'
#                         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#                     # Save the detection result in the database
#                     detection = AdvancedDetection.objects.create(
#                         user=request.user,
#                         follicle_no_r=detection_data["follicle_no_r"],
#                         follicle_no_l=detection_data["follicle_no_l"],
#                         skin_darkening=detection_data["skin_darkening"],
#                         hair_growth=detection_data["hair_growth"],
#                         weight_gain=detection_data["weight_gain"],
#                         cycle_length=detection_data["cycle_length"],
#                         amh=detection_data["amh"],
#                         fast_food=detection_data["fast_food"],
#                         cycle_r_i=detection_data["cycle_r_i"],
#                         fsh_lh=detection_data["fsh_lh"],
#                         prl=detection_data["prl"],
#                         pimples=detection_data["pimples"],
#                         age=detection_data["age"],
#                         bmi=detection_data["bmi"],
#                         prediction="PCOS Detected" if predicted_class == 1 else "No PCOS Detected",
#                     )

#                     # Return the successful response with prediction and probability
#                     return Response({
#                         'msg': 'Advanced Detection successful',
#                         'prediction': detection.prediction,
#                         'probability': prediction_probability
#                     }, status=status.HTTP_201_CREATED)

#                 else:
#                     # If the model API returns an error, log it and return a 500 response
#                     logger.error(f"Error from ML model: {response.status_code} - {response.text}")
#                     return Response({
#                         'error': 'Error communicating with the ML model'
#                     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             except requests.exceptions.Timeout:
#                 logger.error("Request to the ML model timed out")
#                 return Response({
#                     'error': 'The request to the ML model timed out'
#                 }, status=status.HTTP_504_GATEWAY_TIMEOUT)

#             except requests.exceptions.ConnectionError:
#                 logger.error("Connection error while trying to reach the ML model")
#                 return Response({
#                     'error': 'Unable to connect to the ML model'
#                 }, status=status.HTTP_502_BAD_GATEWAY)

#             except requests.exceptions.RequestException as e:
#                 logger.error(f"RequestException occurred: {str(e)}")
#                 return Response({
#                     'error': f'An error occurred while contacting the ML model: {str(e)}'
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         # If serializer is invalid, return a 400 response with errors
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


logger = logging.getLogger(__name__)


class AdvancedDetectionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = AdvancedDetectionSerializer(data=request.data)
        if serializer.is_valid():
            detection_data = serializer.validated_data
            model_input = {
                "Follicle_No_R": detection_data["follicle_no_r"],
                "Follicle_No_L": detection_data["follicle_no_l"],
                "Skin_darkening": detection_data["skin_darkening"],
                "hair_growth": detection_data["hair_growth"],
                "Weight_gain": detection_data["weight_gain"],
                "Cycle_length": detection_data["cycle_length"],
                "AMH": detection_data["amh"],
                "Fast_food": detection_data["fast_food"],
                "Cycle_R_I": detection_data["cycle_r_i"],
                "FSH_LH": detection_data["fsh_lh"],
                "PRL": detection_data["prl"],
                "Pimples": detection_data["pimples"],
                "Age": detection_data["age"],
                "BMI": detection_data["bmi"]
            }

            url = "https://appledog00-Project-Sakhii.hf.space/predict/"
            headers = {'Content-Type': 'application/json'}

            try:
                response = requests.post(url, json=model_input, headers=headers)
                logger.info(f"Model API response: {response.status_code}, {response.text}")

                if response.status_code == 200:
                    prediction = response.json()
                    predicted_class = prediction.get('prediction')
                    prediction_probability = prediction.get('probability')

                    if predicted_class is None or prediction_probability is None:
                        logger.error(f"Missing prediction data in response: {response.text}")
                        return Response({'error': 'Prediction data is missing from the model response'},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    detection = AdvancedDetection.objects.create(
                        user=request.user,
                        follicle_no_r=detection_data["follicle_no_r"],
                        follicle_no_l=detection_data["follicle_no_l"],
                        skin_darkening=detection_data["skin_darkening"],
                        hair_growth=detection_data["hair_growth"],
                        weight_gain=detection_data["weight_gain"],
                        cycle_length=detection_data["cycle_length"],
                        amh=detection_data["amh"],
                        fast_food=detection_data["fast_food"],
                        cycle_r_i=detection_data["cycle_r_i"],
                        fsh_lh=detection_data["fsh_lh"],
                        prl=detection_data["prl"],
                        pimples=detection_data["pimples"],
                        age=detection_data["age"],
                        bmi=detection_data["bmi"],
                        prediction="PCOS Detected" if predicted_class == 1 else "No PCOS Detected",
                    )

                    message = "Please consult with the nearest gynecologist or hospital." if predicted_class == 1 else "Congratulations! You are not prone to PCOS. Maintain a healthy lifestyle and stay aware."

                    return Response({
                        'msg': 'Advanced Detection successful',
                        'prediction': detection.prediction,
                        'probability': prediction_probability,
                        'advice': message
                    }, status=status.HTTP_201_CREATED)

                else:
                    logger.error(f"Error from ML model: {response.status_code} - {response.text}")
                    return Response({'error': 'Error communicating with the ML model'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except requests.exceptions.Timeout:
                logger.error("Request to the ML model timed out")
                return Response({'error': 'The request to the ML model timed out'}, status=status.HTTP_504_GATEWAY_TIMEOUT)

            except requests.exceptions.ConnectionError:
                logger.error("Connection error while trying to reach the ML model")
                return Response({'error': 'Unable to connect to the ML model'}, status=status.HTTP_502_BAD_GATEWAY)

            except requests.exceptions.RequestException as e:
                logger.error(f"RequestException occurred: {str(e)}")
                return Response({'error': f'An error occurred while contacting the ML model: {str(e)}'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    

class TrackPeriodCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Automatically get the current authenticated user
        user = request.user
        
        # Add the user to the request data (this avoids the need to pass 'user' in the body)
        request.data['user'] = user.id

        # Serialize the data
        serializer = TrackPeriodSerializer(data=request.data)

        if serializer.is_valid():
            # Save the period data
            serializer.save()

            # After saving, predict the next period (you can adjust this logic as needed)
            periods = Period.objects.filter(user=user).order_by('period_date')
            
            if periods.count() > 1:
                # Calculate the average cycle length from multiple periods
                cycle_lengths = []
                for i in range(1, len(periods)):
                    cycle_length = (periods[i].period_date - periods[i-1].period_date).days
                    cycle_lengths.append(cycle_length)
                average_cycle_length = sum(cycle_lengths) // len(cycle_lengths)
            else:
                # Use a default cycle length for new users
                average_cycle_length = 28  # Default 28 days
            
            # Predict the next period date
            last_period_date = periods.last().period_date
            next_period_date = last_period_date + timedelta(days=average_cycle_length)

            return Response({'next_period_date': next_period_date}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class TrackPeriodRetrieveView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    def get(self, request):
        user = request.user  # The authenticated user

        # Fetch the periods for the authenticated user
        periods = Period.objects.filter(user=user).order_by('period_date')

        # Check if there are any periods
        if not periods.exists():
            return Response({"detail": "No period data found for the user."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the period data using the TrackPeriodHistorySerializer
        serializer = TrackPeriodHistorySerializer(periods, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class SymptomCategoryListView(generics.ListAPIView):
    """API to get the list of symptom categories."""
    queryset = SymptomCategory.objects.all()
    serializer_class = SymptomCategorySerializer


class SymptomListView(generics.ListAPIView):
    """API to get symptoms by category."""
    serializer_class = SymptomSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Symptom.objects.filter(category_id=category_id)  # Now valid because category exists






class SymptomTrackCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        period_date = request.data.get('period_date')  # Assuming period_date is provided in request
        symptoms = request.data.get('symptoms', [])  # List of symptom IDs

        if not period_date or not symptoms:
            return Response({"detail": "Period date and symptoms are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the first matching Period object for the user and period_date
        period = Period.objects.filter(user=user, period_date=period_date).first()

        if not period:
            return Response({"detail": "Period not found for the user."}, status=status.HTTP_404_NOT_FOUND)

        # Use a transaction to ensure all or nothing is saved
        with transaction.atomic():
            symptom_tracks = []  # Collect objects to bulk create
            for symptom_id in symptoms:
                try:
                    symptom = Symptom.objects.get(id=symptom_id)
                    symptom_tracks.append(SymptomTrack(user=user, period=period, symptom=symptom))
                except Symptom.DoesNotExist:
                    return Response({"detail": f"Symptom with ID {symptom_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            # Bulk create for efficiency
            SymptomTrack.objects.bulk_create(symptom_tracks)

        return Response({"detail": "Symptoms logged successfully."}, status=status.HTTP_201_CREATED)
    




class SymptomTrackListView(generics.ListAPIView):
    """API to list all tracked symptoms of a user."""
    permission_classes = [IsAuthenticated]
    serializer_class = SymptomTrackSerializer

    def get_queryset(self):
        # Fetch symptoms tracked by the current authenticated user, ordered by the related period's period_date
        return SymptomTrack.objects.filter(user=self.request.user).order_by('-period__period_date')