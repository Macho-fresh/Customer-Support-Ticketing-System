from django.db import models
from accounts.models import User

class Ticket(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer')
    title = models.CharField(max_length=100, db_index=True)
    description = models.CharField()
    PRIORITY = (
        (1, 'Critical'),
        (2, 'High'),
        (3, "Medium"),
        (4, "Low")
    )
    priority = models.IntegerField(choices = PRIORITY, default=3, db_index=True)
    STATUS = (
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
        ('Reopened', 'Reopened')
    ) 
    status = models.CharField(max_length=20, choices = STATUS, default='Open', db_index=True)
    agent = models.ForeignKey(User, on_delete = models.SET_NULL, null=True, related_name='agent')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['priority', 'created_at']

class Comment(models. Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class AuditLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
