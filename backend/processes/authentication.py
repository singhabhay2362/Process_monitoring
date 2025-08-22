from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.headers.get('Authorization', '').replace('Bearer ', '')
        if api_key != '': 
            raise AuthenticationFailed('Invalid API key')
        return (None, None)