from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from account.serializers import RegistrationSerializer
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import login
from account.backends import TokenAuthenticationBackend
from rest_framework.authtoken.views import ObtainAuthToken

@api_view(['POST', ])
def registration_view(request):

    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            account = serializer.save()
            data['response'] = 'successfully registered new user.'
            data['email'] = account.email
            data['username'] = account.username
            token = Token.objects.get(user=account).key
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)

class CustomObtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomObtainAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'id': token.user_id})


@api_view(['POST', ])
def qrcode_authentication_view(request):
    id = request.data.get("id")
    token = request.data.get("token")

    token_authentication_backend = TokenAuthenticationBackend()
    user = token_authentication_backend.authenticate(request=request, id=id, auth_token=token)
    if user is not None:
        user.backend = 'account.backends.TokenAuthenticationBackend'
        login(request, user)
        return Response({'response': 'Authentication successful'}, status=status.HTTP_200_OK)
        
    else:
        return Response({'response': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def test_permission_view(request):
    return Response(status=status.HTTP_200_OK)