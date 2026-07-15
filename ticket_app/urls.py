from .views import *
from django.urls import path

urlpatterns = [
    path('create-ticket/', CreateTicket.as_view()),
    path('update-ticket/<int:id>/', UpdateTicket.as_view()),
    path('delete-ticket/<int:id>/', DeleteTicket.as_view()),
    path('view-tickets-agent/', ViewAllAgentTickets.as_view()),
    path('view-ticket-agent/<int:id>/', ViewOneAgentTicket.as_view()),
    path('change-ticket-status/<int:id>/', ChangeTicketStatus.as_view()),
    path('change-ticket-priority/<int:id>/', ChangeTicketPriority.as_view()),
    path('view-tickets-customer/', ViewAllUserTicket.as_view()),
    path('view-ticket-customer/<int:id>/', ViewUserTicket.as_view())
]
