from rest_framework import serializers
from .models import User, ReceiveImageModel
from apps.api import models
from django.contrib.auth import authenticate
from django.core.validators import EmailValidator
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "email",
            "password",
            "is_admin",
        ]
        extra_kwargs = {'password': {'write_only': True,
                                     'validators': [validate_password]}}

    def create(self, validated_data):
        user = models.User(
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = models.User
        fields = [
            "password",
            "password2",
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "email",
            "password",
            "is_admin"
        ]
        extra_kwargs = {'password': {'write_only': True,
                                     'validators': [validate_password]}}

    def validate(self, data):
        if 'is_admin' not in data:
            raise serializers.ValidationError("Must include is_admin field")
        return data

    def create(self, validated_data):
        user = models.User(
            email=validated_data['email'],
            is_admin=validated_data['is_admin']
        )
        user.set_password(validated_data['password'])
        if (validated_data['is_admin'] == "True"):
            user.is_superuser = True
            user.is_staff = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if 'is_admin' not in data:
            is_admin = False
        else:
            is_admin = data.get('is_admin')

        if not email or not password:
            raise serializers.ValidationError("Please provide both email and password")

        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email does not exist")

        user = authenticate(request=self.context.get('request'), email=email, password=password, is_admin=is_admin)

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserProfileModel
        fields = ('__all__')


class ReceiveImageModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReceiveImageModel
        fields = ('user_email', 'image')


class UserDetectedImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserDetectedImageModel
        # field = ('user_email', 'origin_image_url', 'detect_image_url', 'counted_number', 'uploaded_time')
        fields = '__all__'