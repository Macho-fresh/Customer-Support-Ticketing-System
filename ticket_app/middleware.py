from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = parse_qs(scope["query_string"].decode())

        token = query_string.get("token")

        if token:
            token = token[0]

            try:
                access_token = AccessToken(token)

                user = await self.get_user(access_token["user_id"])

                scope["user"] = user

            except Exception:
                scope["user"] = None

        else:
            scope["user"] = None

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)