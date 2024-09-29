from rest_framework import serializers
from user.models import User

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







    
    

