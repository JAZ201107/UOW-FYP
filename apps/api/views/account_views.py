from apps.api.models import User
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import Http404
from rest_framework.decorators import permission_classes
from knox import views as knox_views
from apps.api.serializers import LoginSerializer
from django.contrib.auth import login
from rest_framework.decorators import api_view
from rest_framework import views
from django.http import JsonResponse
from apps.api import serializers
from apps.api import models


class LoginView(knox_views.LoginView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            response = super(LoginView, self).post(request, format=None)
            response.data['admin'] = user.is_admin
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(response.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return JsonResponse({"user": "Authenticated"}, status=status.HTTP_200_OK)


class GetAllUserAndImages(views.APIView):
    """This class used to get all user's uploaded images, for admin"""
    serializer_class = serializers.UserDetectedImageSerializer
    queryset = models.UserDetectedImageModel.objects.all()

    def get(self, request):
        user_images = list(models.UserDetectedImageModel.objects.filter().values())
        return JsonResponse(user_images, safe=False)
