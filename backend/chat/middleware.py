from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
import jwt


@database_sync_to_async
def get_user(user_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except (User.DoesNotExist, ValueError, TypeError):
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token = params.get('token', [None])[0]

        if token:
            try:
                payload = jwt.decode(
                    token,
                    settings.SECRET_KEY,
                    algorithms=['HS256']
                )
                user_id = payload.get('user_id')
                print(f'WS auth OK: user_id={user_id}')
                if user_id:
                    scope['user'] = await get_user(user_id)
                else:
                    print('WS auth error: no user_id in payload')
                    scope['user'] = AnonymousUser()
            except jwt.ExpiredSignatureError:
                print('WS auth error: token expired')
                scope['user'] = AnonymousUser()
            except jwt.InvalidTokenError as e:
                print(f'WS auth error: {e}')
                scope['user'] = AnonymousUser()
            except Exception as e:
                print(f'WS auth unexpected error: {e}')
                scope['user'] = AnonymousUser()
        else:
            print('WS auth error: no token provided')
            scope['user'] = AnonymousUser()

        return await self.app(scope, receive, send)
