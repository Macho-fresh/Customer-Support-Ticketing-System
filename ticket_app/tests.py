from django.test import TestCase
from rest_framework.test import APITestCase
from accounts.models import User
from rest_framework import status

# also create an agent so it has someone to assign ticket to

class TicketTest(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username = 'stella',
            email = 'macho@gmail.com',
            password = 'Macholina911#',
            role = 'Customer'
            )

        User.objects.create_user(
                    username = 'macho',
                    email = 'chycyber13@gmail.com',
                    password = 'Macholina911#',
                    role = 'Agent'
                    )
 
        data = {
                    'username': 'stella',
                    'email': 'macho@gmail.com',
                    'password': 'Macholina911#'
                }

        login = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(
            login.status_code,
            status.HTTP_200_OK
        )
        # print(login.data)
        self.client.credentials(
            HTTP_AUTHORIZATION = f'Bearer {login.data["access"]}'
        )
    def test_ticket(self):
        data = {
                    'title': 'Login error',
                    'description': 'The login page keeps loading after I click login'
                }

        response = self.client.post('/api/create-ticket/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

# Recommended areas to test include:

# * Customer registration ----- done
# * Agent authentication 
# * Ticket creation ---------- done
# * Automatic agent assignment ---------- done
# * Unauthorized ticket access
# * Status changes
# * Audit logging
# * WebSocket authentication
# * WebSocket room access
# * Email notifications
