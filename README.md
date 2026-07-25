# Customer Support Ticketing System API

A backend REST API for managing customer support tickets, automated agent assignment, ticket status workflows, audit logging, email notifications, and real-time communication between customers and assigned support agents.

The system is built with Django and Django REST Framework and includes PostgreSQL, Docker, Redis, Celery-ready architecture, and Django Channels for real-time ticket conversations.

---

## Table of Contents

* [Features](#features)
* [Technologies Used](#technologies-used)
* [System Architecture](#system-architecture)
* [Project Structure](#project-structure)
* [Ticket Workflow](#ticket-workflow)
* [Authentication and Authorization](#authentication-and-authorization)
* [Ticket Assignment](#ticket-assignment)
* [Ticket Status Management](#ticket-status-management)
* [Real-Time Communication](#real-time-communication)
* [Audit Logging](#audit-logging)
* [Email Notifications](#email-notifications)
* [Database](#database)
* [Docker Setup](#docker-setup)
* [Environment Variables](#environment-variables)
* [Installation and Local Development](#installation-and-local-development)
* [Running with Docker](#running-with-docker)
* [Database Migrations](#database-migrations)
* [API Endpoints](#api-endpoints)
* [WebSocket Connection](#websocket-connection)
* [Testing](#testing)
* [Pagination](#pagination)
* [Filtering & Search](#filtering-and-search)
* [Rate Limiting](#rate-limiting)
* [License](#license)

---

## Features

* Customer registration and authentication
* JWT authentication
* Role-based access control
* Customer ticket creation
* Automatic support agent assignment
* Ticket status management
* Ticket reopening and closing
* Customer and agent ticket access control
* Real-time communication using WebSockets
* Ticket-specific chat rooms
* Audit logging for important ticket actions
* Email notifications
* PostgreSQL database support
* Redis channel layer for WebSockets
* Docker containerization
* Docker Compose development environment
* Environment variable configuration
* Celery for background tasks

---

## Technologies Used

### Backend

* Python
* Django
* Django REST Framework

### Authentication

* JSON Web Tokens (JWT)
* `djangorestframework-simplejwt`

### Real-Time Communication

* Django Channels
* Daphne
* Redis
* `channels-redis`

### Database

* PostgreSQL

### DevOps

* Docker
* Docker Compose

### Email

* SMTP
* Gmail SMTP 

---

## System Architecture

The application consists of several major components:

```text
                         ┌────────────────────┐
                         │      Customer      │
                         └──────────┬─────────┘
                                    │
                                    │ REST API
                                    ▼
                         ┌────────────────────┐
                         │   Django API       │
                         │                    │
                         │ Authentication     │
                         │ Ticket Management  │
                         │ Business Logic     │
                         └──────┬─────┬───────┘
                                │     │
                    ┌───────────┘     └──────────────┐
                    ▼                                ▼
             ┌─────────────┐                  ┌─────────────┐
             │ PostgreSQL  │                  │    Redis    │
             │  Database   │                  │Channel Layer│
             └─────────────┘                  └──────┬──────┘
                                                     │
                                                     ▼
                                             ┌──────────────┐
                                             │ WebSockets   │
                                             │ Django       │
                                             │ Channels     │
                                             └──────────────┘
```

---

## Project Structure

The  project structure looks like:

```text
Ticketing_System/
│
├── ticket_project/
│   │
│   ├── manage.py
│   │
│   ├── ticket_project/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   ├── ticket_app/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── consumers.py
│   │   ├── middleware.py
│   │   
│   │
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── compose.yml
│   ├── .env
│   └── .gitignore
```

---

# Ticket Workflow

The workflow is:

```text
Customer
   │
   ▼
Creates Ticket
   │
   ▼
System Automatically Assigns Agent
   │
   ▼
Agent Receives Notification
   │
   ▼
Agent Reviews Ticket
   │
   ▼
Agent Communicates With Customer
   │
   ▼
Ticket Resolved
   │
   ▼
Ticket Closed
```

Example:

```text
OPEN
  ↓
IN_PROGRESS
  ↓
RESOLVED
  ↓
CLOSED
```

A closed ticket can optionally be reopened if the customer needs additional assistance.

---

# Authentication and Authorization

The system uses JWT authentication.

Users are authenticated using an access token:

```text
Authorization: Bearer <access_token>
```

The system supports different user roles, for example:

```text
CUSTOMER
AGENT
```

Permissions are enforced using custom permission classes.

Example:

```python
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "Customer"
        )
```

Agents and customers have different permissions.

### Customer

A customer can:

* Create tickets
* View their own tickets
* Send messages in their tickets
* View ticket updates

### Agent

An agent can:

* View assigned tickets
* Change ticket status
* Communicate with customers
* Resolve tickets

---

# Ticket Assignment

When a customer creates a ticket, the system automatically assigns the ticket to an available support agent.

Example logic:

```python
agent = (
    User.objects
    .filter(role="Agent")
    .annotate(open_tickets=Count("customer_tickets"))
    .order_by("open_tickets")
    .first()
)
```

This allows the system to assign the ticket to the agent with the lowest number of active tickets.

This is a simple load-balancing strategy.


---

# Ticket Status Management

Tickets can have different states.

Example:

```text
OPEN
IN_PROGRESS
RESOLVED
CLOSED
```

The ticket status can be updated by an authorized agent.

Example:

```http
PATCH /api/change-ticket-status/<int:id>/
```

Only the agent assigned to the ticket should be allowed to modify its status.

Example:

```python
if request.user != ticket.agent:
    return Response(
        {
            "error": "You are not the agent assigned to this ticket"
        },
        status=status.HTTP_401_UNAUTHORIZED
    )
```

---

# Real-Time Communication

The system uses Django Channels and WebSockets for real-time communication.

Each ticket has its own WebSocket room.

For example:

```text
Ticket ID: 1

WebSocket Room:
ticket_1
```

The customer and assigned agent can join the same ticket room.

```text
Customer
    │
    │
    ▼
┌─────────────┐
│  ticket_1   │
│ WebSocket   │
│    Room     │
└─────────────┘
    ▲
    │
    │
   Agent
```

Only the customer who created the ticket and the agent assigned to it are allowed to connect.

Example WebSocket URL:

```text
ws://127.0.0.1:8000/chat/1/
```

With JWT authentication:

```text
ws://127.0.0.1:8000/chat/1/?token=<access_token>
```

---

## WebSocket Authentication

Since Django's default `AuthMiddlewareStack` uses session authentication, JWT authentication requires custom middleware.

The middleware:

1. Reads the token from the WebSocket URL.
2. Validates the JWT.
3. Extracts the user ID.
4. Retrieves the user from the database.
5. Adds the user to the WebSocket scope.

Example:

```python
class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = parse_qs(
            scope["query_string"].decode()
        )

        token = query_string.get("token")

        if token:
            token = token[0]

            try:
                access_token = AccessToken(token)

                user = await self.get_user(
                    access_token["user_id"]
                )

                scope["user"] = user

            except Exception:
                scope["user"] = None

        else:
            scope["user"] = None

        return await super().__call__(
            scope,
            receive,
            send
        )
```

The WebSocket consumer then accesses the authenticated user using:

```python
self.scope["user"]
```

---

# Audit Logging

Important ticket actions are recorded in an audit log.

Example actions:

```text
Customer created a ticket
Agent was assigned to a ticket
Agent changed ticket status
Ticket was reopened
Ticket was closed
```

Example:

```python
AuditLog.objects.create(
    ticket=ticket,
    action=f"{request.user} created a ticket",
    user=request.user
)
```

Audit logging provides:

* Accountability
* Debugging
* Security monitoring
* Historical records
* Better customer support management

Example audit history:

```text
15:00 - Customer created ticket
15:02 - System assigned ticket to Agent A
15:15 - Agent changed status to IN_PROGRESS
15:45 - Agent changed status to RESOLVED
16:00 - Customer closed ticket
```

---

# Email Notifications

The system can send emails when important events occur.

Examples:

* Ticket assigned to an agent
* Ticket status changed
* Ticket resolved
* Ticket closed
* Ticket reopened

Example:

```python
send_mail(
    subject,
    message,
    from_email,
    recipient_list,
    fail_silently=False
)
```

email sending is moved to a background task queue such as Celery.

---

# Database

The application uses PostgreSQL.

Example database configuration:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get(
            "POSTGRES_PORT",
            "5432"
        ),
    }
}
```

---

# Docker Setup

The project uses Docker to containerize the application.

The main services are:

```text
web
 │
 ├── Django
 ├── Django REST Framework
 └── Django Channels

db
 │
 └── PostgreSQL

```

---

# Environment Variables

Sensitive values are not hardcoded into the source code.

Example `.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True

POSTGRES_DB=ticketing_db
POSTGRES_USER=ticketing_user
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=email@gmail.com
EMAIL_HOST_PASSWORD=email_password
```

The `.env` file should is not committed to Git.

Add it to `.gitignore`:

```text
.env
```

---

# Installation and Local Development

## 1. Clone the Repository

```bash
git clone <repository-url>
```

```bash
cd Ticketing_System
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

### Linux/macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

Add the database and email variables required by the project.

---

## 5. Run Migrations

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

---

## 6. Create a Superuser

```bash
python manage.py createsuperuser
```

---

## 7. Run the Development Server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

# Running with Docker

Build and start the services:

```bash
docker compose up --build
```

Run in detached mode:

```bash
docker compose up -d
```

Stop the services:

```bash
docker compose down
```

View logs:

```bash
docker compose logs -f web
```

View database logs:

```bash
docker compose logs -f db
```

---

# Database Migrations with Docker

Run migrations inside the web container:

```bash
docker compose exec web python manage.py migrate
```

Create migrations:

```bash
docker compose exec web python manage.py makemigrations
```

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

---

# API Endpoints

The exact endpoint names may vary depending on your URL configuration.

## Authentication

```text
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/token/refresh/
POST /api/auth/register-agent/
```

---

## Tickets

```text
POST /api/create-ticket/
```

Creates a new support ticket.

```text
GET /api/view-tickets-customer/
```

Returns tickets belonging to the authenticated customer.

```text
GET /api/view-tickets-agent/
```

Returns tickets assigned to the authenticated agent.

```text
PATCH /api/change-ticket-status/<ticket_id>/
```

Updates the status of a ticket.

---

## Example Ticket Creation

```json
{
    "title": "Login not working",
    "description": "I cannot log into my account."
}
```

The system then:

1. Creates the ticket.
2. Automatically assigns an available agent.
3. Creates an audit log.
4. Sends an agent notification.
5. Makes the ticket available for real-time communication.

---

# WebSocket Connection

Example:

```javascript
const socket = new WebSocket(
    "ws://127.0.0.1:8000/chat/1/?token=ACCESS_TOKEN"
);

socket.onopen = () => {
    console.log("Connected");
};

socket.onmessage = (event) => {
    console.log(event.data);
};

socket.onclose = () => {
    console.log("Connection closed");
};
```

Sending a message:

```javascript
socket.send(JSON.stringify({
    message: "Hello, I need help with my account."
}));
```

Messages are broadcast to the WebSocket group associated with the ticket:

```text
ticket_1
```

---

# Redis Channel Layer

Django Channels uses Redis to enable communication between WebSocket connections.

Example configuration:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                ("redis", 6379)
            ],
        },
    },
}
```

When running Django locally with Redis installed directly:

```python
"hosts": [
    ("127.0.0.1", 6379)
]
```

When running inside Docker:

```python
"hosts": [
    ("redis", 6379)
]
```

The hostname is the Docker Compose service name.

---

# Testing

Run the test suite using:

```bash
python manage.py test
```

Inside Docker:

```bash
docker compose exec web python manage.py test
```

---

## Pagination

Implemented pagination for large ticket lists.

```text
GET /api/tickets/?page=2
```

This prevents the API from returning thousands of tickets at once.

---

## Filtering and Search

Added support for:

```text
/status
/agent
/customer
/created_at
```

Example:

```text
GET /api/tickets/?status=OPEN
```

---

## Rate Limiting

Protected the API from abuse by limiting requests.

Examples:

```text
100 requests per minute
```

This can be implemented using Django REST Framework throttling.

---

## Author

Developed as a backend engineering project focused on:

* REST API development
* Authentication
* Authorization
* Database design
* Real-time communication
* Background processing
* Docker containerization
* PostgreSQL
* Redis
* Scalable backend architecture

### By Macho