from rest_framework import serializers
from .models import User

class UserSerializer(serializers.Serializer):  # Keep this as Serializer
    user_id = serializers.CharField(read_only = True)  # Explicitly define ID
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    created_at = serializers.DateTimeField(read_only=True)  # Explicitly define timestamps
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        # Assuming your User model is not Django ORM based
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])  # Hash password if supported
        # breakpoint()
        user.save()  # Save using your custom ORM
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
