from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def create_ticket_email(email, username, title):
    subject="Ticket Assignment"

    message = (
        f"Hello {username}\n\n"
        f"The ticket titled '{title}' has been assigned to you.\n"
        "Please attend to it as soon as possible.\n\n"
        "Regards,\n"
        "Ticket Team"

    )

    from_email = settings.DEFAULT_FROM_EMAIL

    recipient_list=[
        email
    ]

    fail_silently=False
    
    send_mail(subject, message, from_email, recipient_list, fail_silently)

def create_updated_ticket(email, username, title):
    subject="Ticket Updated"

    message = (
        f"Hello {username}\n\n"
        f"The ticket titled '{title}' was just updated.\n"
        "Please attend to it as soon as possible.\n\n"
        "Regards,\n"
        "Ticket Team"

    )

    from_email = settings.DEFAULT_FROM_EMAIL

    recipient_list=[
        email
    ]

    fail_silently=False
    
    send_mail(subject, message, from_email, recipient_list, fail_silently)

def delete_ticket(email, username, title):
    subject="Ticket Deleted"

    message=(
        f"Hello {username},"
        f"The customer of ticket: {title} "
        f"has just deleted their ticket."

        'Regards',
        'Ticket Team'
    )

    from_email=settings.DEFAULT_FROM_EMAIL

    recipient_list=[
        email
    ]

    fail_silently=False
    send_mail(subject, message, from_email, recipient_list, fail_silently)
