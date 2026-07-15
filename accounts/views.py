from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from .models import User

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Customer'
    
class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Agent'
    
class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'User already exists'
            }, status = status.HTTP_409_CONFLICT)
        
        User.objects.create_user(
            username = username,
            email = email,
            password = password,
            role = 'Customer'
        )
        return Response({
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)


class RegisterAgentView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'User already exists'
            }, status = status.HTTP_409_CONFLICT)
        
        User.objects.create_user(
            username = username,
            email = email,
            password = password,
            role = 'Agent'
        )
        return Response({
            'message': 'Agent created successfully'
        }, status=status.HTTP_201_CREATED)