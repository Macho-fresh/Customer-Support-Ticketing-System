from django.shortcuts import render
from .models import *
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from .serializer import *
from rest_framework.permissions import IsAuthenticated
from accounts.views import *
from accounts.models import User
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.mail import send_mail
from django.conf import settings

class CreateTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        agent = User.objects.filter(role='Agent').annotate(open_tickets=Count('agent')).order_by('open_tickets').first()

        ticket =  Ticket.objects.create(
            customer = request.user,
            title = title,
            description = description,
            agent = agent
        )

        AuditLog.objects.create(
            ticket = ticket,
            action = f'{request.user} created a ticket',
            user = request.user
        )
        # add later: tell the agent that he or she has been assigned to this ticket
        subject="Ticket Assignment"

        message = (
            f"Hello {ticket.agent.username}\n\n"
            f"The ticket titled '{ticket.title}' has been assigned to you.\n"
            "Please attend to it as soon as possible.\n\n"
            "Regards,\n"
            "Ticket Team"

        )

        from_email = settings.DEFAULT_FROM_EMAIL

        recipient_list=[
            ticket.agent.email
        ]

        fail_silently=False
        
        send_mail(subject, message, from_email, recipient_list, fail_silently)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdateTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def patch(self, request, id):
        title = request.data.get('title')
        description = request.data.get('description')

        ticket =  Ticket.objects.get(id=id)
        ticket.title = title
        ticket.description = description
        ticket.save()

        AuditLog.objects.create(
            ticket = ticket,
            action = f'{request.user} updated this ticket',
            user = request.user
        )
        
        # add later: tell the agent that the user updtated their ticket title and description

        subject="Ticket Updated"

        message = (
            f"Hello {ticket.agent.username}\n\n"
            f"The ticket titled '{ticket.title}' was just updated.\n"
            "Please attend to it as soon as possible.\n\n"
            "Regards,\n"
            "Ticket Team"

        )

        from_email = settings.DEFAULT_FROM_EMAIL

        recipient_list=[
            ticket.agent.email
        ]

        fail_silently=False
        
        send_mail(subject, message, from_email, recipient_list, fail_silently)

        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)  

class DeleteTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def delete(self, request, id):

        ticket = Ticket.objects.get(id=id).delete()

        AuditLog.objects.create(
            ticket = ticket,
            action = f'{request.user} deleted this ticket',
            user = request.user
        )
        
        # add later: tell the agent that the user deleted their ticket 
        subject="Ticket Deleted"

        message=(
            f"Hello {ticket.agent},"
            f"The customer of ticket: {ticket.title} "
            f"has been has deleted their ticket."

            'Regards',
            'Ticket Team'
        )

        from_email=settings.DEFAULT_FROM_EMAIL

        recipient_list=[
            ticket.customer.email
        ]

        fail_silently=False
        send_mail(subject, message, from_email, recipient_list, fail_silently)


        return Response({
            'message': 'Ticket deleted successfully'
        }, status=status.HTTP_200_OK)       
    
class ViewAllAgentTickets(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAgent]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ('status', 'priority')
    search_fields = ['title', 'description']
    # always order by priority when showing agents their tickets


    def post(self, request):
        tickets = Ticket.objects.filter(agent=request.user) 
        serializer = TicketSerializer(tickets, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewOneAgentTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAgent]

    def post(self, request, id):
        ticket = Ticket.objects.get(agent=request.user, id=id)  
        serializer = TicketSerializer(ticket)  
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ChangeTicketStatus(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAgent]

    def patch(self, request, id):
        s = request.data.get('status')
        ticket = Ticket.objects.get(agent=request.user, id=id) 
        old_status = ticket.status
        if ticket: 
            ticket.status = s
            ticket.save()

            AuditLog.objects.create(
                ticket = ticket,
                action = f'{request.user} changed ticket status from {old_status} to {s}',
                user = request.user
            )
            serializer = TicketSerializer(ticket)  
            return Response(serializer.data, status=status.HTTP_200_OK)   
        return Response({
            'error': 'Youre not the agent assigned to this ticket'
        }, status=status.HTTP_401_UNAUTHORIZED) 

class ChangeTicketPriority(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAgent]

    def patch(self, request, id):
        priority = request.data.get('priority')
        ticket = Ticket.objects.get(agent=request.user, id=id)  
        ticket.priority = priority
        ticket.save()

        AuditLog.objects.create(
            ticket = ticket,
            action = f'{request.user} changed ticket priority to {priority}',
            user = request.user
        )
        serializer = TicketSerializer(ticket)  
        return Response(serializer.data, status=status.HTTP_200_OK)          
    
class ViewUserTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def post(self, request, id):
        ticket = Ticket.objects.get(customer=request.user, id=id)  
        serializer = TicketSerializer(ticket)  
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewAllUserTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def post(self, request):
        ticket = Ticket.objects.filter(customer=request.user)  
        serializer = TicketSerializer(ticket, many=True)  
        return Response(serializer.data, status=status.HTTP_200_OK)