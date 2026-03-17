from django.contrib.auth.models import User
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer
from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

def login_page(request):
    return render(request, "login.html")

def register_page(request):
    return render(request, "register.html")
