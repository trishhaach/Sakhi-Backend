from xml.dom import ValidationErr
from rest_framework import serializers
from user.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .models import User
from .utils import Util
from .models import NonClinicalDetection, AdvancedDetection

class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirmPassword = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['password'] != data['confirmPassword']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        if 'email' not in data or 'password' not in data:
            raise serializers.ValidationError({
                'email': 'This field is required.',
                'password': 'This field is required.'
            })
        return data
    
class UserProfileSerializer(serializers.Serializer):
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)


class UserChangePasswordSerializer(serializers.Serializer):
    oldPassword = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    newPassword = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)
    confirmNewPassword = serializers.CharField(max_length=255, style={'input_type': 'password'}, write_only=True)

    class Meta:
        fields = ['oldPassword', 'newPassword', 'confirmNewPassword']

    def validate(self, attrs):
        old_password = attrs.get('oldPassword')
        new_password = attrs.get('newPassword')
        confirm_new_password = attrs.get('confirmNewPassword')
        user = self.context.get('user')

        # Check if the old password is correct
        if not user.check_password(old_password):
            raise serializers.ValidationError("Old password is not correct")

        # Check if the new password matches the confirm password
        if new_password != confirm_new_password:
            raise serializers.ValidationError("New password and confirm new password don't match")

        return attrs

    def save(self, **kwargs):
        user = self.context.get('user')
        new_password = self.validated_data.get('newPassword')
        user.set_password(new_password)
        user.save()
        return user



class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        # Correct query
        user = User.objects.filter(email=email).first()  # Using filter instead of call
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Password Reset Token', token)
            link = f'http://localhost:3000/api/user/reset/{uid}/{token}'
            print('Password Reset Link', link)

            # Send email
            body = 'Click following link to Reset Your Password ' + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email
            }
            Util.send_email(data)

            return attrs
        else:
            raise ValidationError('You are not a Registered User')


class UserPasswordResetSerializer(serializers.Serializer):
    newPassword = serializers.CharField(write_only=True, style={'input_type': 'password'})
    confirmNewPassword = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        fields = ['newPassword', 'confirmNewPassword']

    def validate(self, attrs):
        try:
            password = attrs.get('newPassword')
            confirm_password = attrs.get('confirmNewPassword')
            
            # Check if passwords match
            if password != confirm_password:
                raise serializers.ValidationError("Passwords do not match.")

            # You can also include password validation rules here, such as length, characters, etc.

        except DjangoUnicodeDecodeError as identifier:
            raise serializers.ValidationError("Token is not valid or expired")

        return attrs

    def save(self, uidb64, token):
        # Get the user from uidb64
        user_id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=user_id)

        # Set the new password
        user.set_password(self.validated_data['newPassword'])
        user.save()
        return user

class NonClinicalDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonClinicalDetection
        fields = ['skin_darkening', 'hair_growth', 'weight_gain', 'cycle_length', 'fast_food', 'pimples', 'age', 'bmi']

class AdvancedDetectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedDetection
        fields = ['follicle_no_r', 'follicle_no_l', 'skin_darkening', 'hair_growth', 'weight_gain', 'cycle_length', 
                  'amh', 'fast_food', 'cycle_r_i', 'fsh_lh', 'prl', 'pimples', 'age', 'bmi']

# Serializer to retrieve Non-Clinical Detection Results
class NonClinicalDetectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonClinicalDetection
        fields = ['skin_darkening', 'hair_growth', 'weight_gain', 'cycle_length', 'fast_food', 'pimples', 'age', 'bmi', 'prediction']

# Serializer to retrieve Advanced Detection Results
class AdvancedDetectionResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedDetection
        fields = ['follicle_no_r', 'follicle_no_l', 'skin_darkening', 'hair_growth', 'weight_gain', 'cycle_length', 'amh', 'fast_food', 'cycle_r_i', 'fsh_lh', 'prl', 'pimples', 'age', 'bmi', 'prediction']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name'] 

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance