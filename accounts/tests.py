from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User

class RegisterTest(APITestCase):
    def test_register(self):
        data = {
            'username': 'macho',
            'email': 'macho@gmail.com',
            'password': 'Macholina911#'
        }

        response = self.client.post('/api/auth/register/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class LoginTest(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username = 'macho',
            email = 'macho@gmail.com',
            password = 'Macholina911#'
        )
    def test_login(self):
        data = {
                    'username': 'macho',
                    'email': 'macho@gmail.com',
                    'password': 'Macholina911#'
                }
        
        response = self.client.post('/api/auth/login/', data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)  
        self.assertIn('refresh', response.data)  

# add agent register and check role