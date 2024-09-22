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
    password = serializers.CharField(max_length=255, style= {'input_type':'password'}, write_only=True)
    confirmPassword = serializers.CharField(max_length=255, style= {'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'confirmPassword']

    def validate(self, attrs):
        password = attrs.get('password')
        confirmPassword = attrs.get('confirmPassword')
        user = self.context.get('user')
        if password != confirmPassword:
            raise serializers.ValidationError("Password and confirm password doesn't match")
        user.set_password(password)
        user.save()
        return attrs