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
from django.db import transaction
from django.core.cache import cache
from .tasks import *

class CreateTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        agent = User.objects.filter(role='Agent').annotate(open_tickets=Count('agent')).order_by('open_tickets').first()
        
        with transaction.atomic():
            ticket =  Ticket.objects.create(
                customer = request.user,
                title = title,
                description = description,
                agent = agent
            )

            AuditLog.objects.create(
                ticket = ticket,
                action = f'{request.user} created a ticket assigned to {agent}',
                user = request.user
            )

            cache.set(
                f"ticket_{ticket.id}",
                ticket,
                timeout=300
            )
            create_ticket_email.delay(
            ticket.agent.email,
            ticket.agent.username,
            ticket.title
            )
        
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

        with transaction.atomic():
            ticket.description = description
            ticket.save()

            AuditLog.objects.create(
                ticket = ticket,
                action = f'{request.user} updated this ticket',
                user = request.user
            )

            cache.delete(
                f"ticket_{ticket.id}"
            )

            cache.set(
                f"ticket_{ticket.id}",
                ticket,
                timeout=300
            )
        
            create_updated_ticket(
                ticket.agent.email,
                ticket.agent.username,
                ticket.title
            )
      
        serializer = TicketSerializer(ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)  

class DeleteTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def delete(self, request, id):

        with transaction.atomic():
            ticket = Ticket.objects.get(id=id).delete()

            AuditLog.objects.create(
                ticket = ticket,
                action = f'{request.user} deleted this ticket',
                user = request.user
            )

            cache.delete(
                f"ticket_{ticket.id}"
            )
        
            delete_ticket.delay(
            ticket.agent.email,
            ticket.agent.username,
            ticket.title
            ) 
            

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
        cache_key = f"agent_tickets_{request.user.id}"

        data = cache.get(cache_key)

        if data:

            return Response(data)
        
        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewOneAgentTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAgent]

    def post(self, request, id):
        ticket = Ticket.objects.get(agent=request.user, id=id)  
        serializer = TicketSerializer(ticket) 
        cache_key = f"agent_ticket_{request.user.id}"

        data = cache.get(cache_key)

        if data:

            return Response(data)
        
        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        ) 
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ChangeTicketStatus(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsAgent]

    def patch(self, request, id):
        s = request.data.get('status')
        ticket = Ticket.objects.get(agent=request.user, id=id) 
        old_status = ticket.status
        if ticket: 
            with transaction.atomic():
                ticket.status = s
                ticket.save()

                AuditLog.objects.create(
                    ticket = ticket,
                    action = f'{request.user} changed ticket status from {old_status} to {s}',
                    user = request.user
                )

                
            serializer = TicketSerializer(ticket) 
            cache.delete(
                f"ticket_{ticket.id}"
                )

            cache.set(
            f"ticket_{ticket.id}",
            serializer.data,
            timeout=300
            )  
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
        with transaction.atomic():  
            ticket.priority = priority
            ticket.save()

            AuditLog.objects.create(
                ticket = ticket,
                action = f'{request.user} changed ticket priority to {priority}',
                user = request.user
            )
        serializer = TicketSerializer(ticket)
        cache.delete(
                f"ticket_{ticket.id}"
                )

        cache.set(
        f"ticket_{ticket.id}",
        serializer.data,
        timeout=300
        )   
        return Response(serializer.data, status=status.HTTP_200_OK)          
    
class ViewUserTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def post(self, request, id):
        ticket = Ticket.objects.get(customer=request.user, id=id)  
        serializer = TicketSerializer(ticket)  
        cache_key = f"user_ticket_{request.user.id}"

        data = cache.get(cache_key)

        if data:

            return Response(data)
        
        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

class ViewAllUserTicket(generics.GenericAPIView):
    serializer_class = TicketSerializer
    permission_classes = [IsCustomer]

    def post(self, request):
        ticket = Ticket.objects.filter(customer=request.user)  
        serializer = TicketSerializer(ticket, many=True)  
        cache_key = f"user_tickets_{request.user.id}"

        data = cache.get(cache_key)

        if data:

            return Response(data)
        
        cache.set(
            cache_key,
            serializer.data,
            timeout=300
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# add statistics