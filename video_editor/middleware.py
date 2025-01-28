from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class StaticTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')
        if not token or token != "Bearer STATIC_API_TOKEN":
            raise AuthenticationFailed("Invalid or missing token.")
        return (None, None)
