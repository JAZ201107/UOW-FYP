from apps.api.models import User
from apps.api.serializers import UserSerializer, CreateUserSerializer, ChangePasswordSerializer
from django.http import Http404, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework import views
from apps.api import serializers
from apps.api import models
import json


# Create your views here.
class UserList(APIView):
    permission_classes = [IsAuthenticated, ]
    """
    List users or create user
    """

    def get(self, request):
        # Check if user is administrator
        if (not request.user.is_admin):
            return Response({"detail": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        get_data = request.query_params
        # Search querying
        if ('email' in get_data):
            users = User.objects.filter(email__contains=get_data['email'])
        else:
            users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Check if user is administrator
        if (not request.user.is_admin):
            return Response({"detail": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validate(request.data):
                serializer.create(request.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRegistration(APIView):
    """This Class Create User and Basic User Info"""
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(request.data)  # create user
            user_email = serializer.validated_data.get('email')
            print(user_email)
            models.UserProfileModel.objects.create(
                user_email=user_email
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve, update or delete a user instance.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # Check if user is administrator
        if (not request.user.is_admin):
            return Response({"detail": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # Change User's Password
    def put(self, request, pk, format=None):
        # Check if user is administrator
        if (not request.user.is_admin):
            return Response({"detail": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        user = self.get_object(pk)
        serializer = ChangePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"password": "Password Updated"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        # Check if user is administrator
        if (not request.user.is_admin):
            return Response({"detail": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(views.APIView):
    """This class handle the REST API of get user basic profile"""
    serializer_class = serializers.UserProfileSerializer
    queryset = models.UserProfileModel.objects.all()

    def get(self, request):
        """Get the User Profile Information"""

        user_email = request.query_params.get('user_email_h')
        user = models.UserProfileModel.objects.filter(user_email=user_email).values()
        content = {}
        if user:  # if use is not None
            content['user_name'] = user[0]['user_name']
            content['user_email'] = user_email
            content['user_address'] = user[0]['user_address']
            content['user_phone_number'] = user[0]['user_phone_number']
            return Response(content, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        """Add the User Profile Information"""
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            content = {}
            if serializer.save():  # success saved
                user_email = serializer.validated_data.get('user_email')
                print(user_email)
                user = models.UserProfileModel.objects.filter(user_email=user_email).values()
                if user:  # if use is not None
                    print(user[0]['user_name'])
                    content['user_name'] = user[0]['user_name']
                    content['user_email'] = user_email
                    content['user_address'] = user[0]['user_address']
                    content['user_phone_number'] = user[0]['user_phone_number']
                    return Response(content)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update User Profile Information"""
        user_email = request.data['user_email']
        user = models.UserProfileModel.objects.get(user_email=user_email)
        serializer = self.serializer_class(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetectedImageView(views.APIView):
    """This Class Handle The History of the user uploaded file"""
    serializer_class = serializers.UserDetectedImageSerializer
    queryset = models.UserDetectedImageModel.objects.all()

    def get(self, request):
        user_email = request.query_params.get('user_email_h')
        print(user_email)
        images = list(models.UserDetectedImageModel.objects.filter(user_email=user_email).values())
        # serializer = self.serializer_class(images)
        print(images)
        return JsonResponse(images, safe=False)
