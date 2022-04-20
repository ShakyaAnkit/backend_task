from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians
from django.db.models import F
from django.http import Http404

from accounts.models import Account
from api.mixins import UserLoginRequiredMixin
from api.utils import distanceBetnGPS
from .serializers import AccountSerializer, AccountSignUpSerializer
from api import serializers

class LoginAPIView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        """
            Gets tokens with username and password. Input should be in the format:
            {
                "username": "username", 
                "password": "1234abcd"
            }
        """

        username = self.request.data.get('username')
        password = self.request.data.get('password')

        account = Account.objects.filter(email=username)
        if account.exists():
            # account user login
            user = account.first()
            user = user if user.check_password(password) else None
        else:
            return self.error_response()
        
        # checking user
        if user:
            token, _ = Token.objects.get_or_create(user=user)

            user_data = AccountSerializer(instance=user).data

            return Response({'user': user_data, 'token': token.key}, status=200)
        
        return self.error_response()

    def error_response(self):
        return Response({'error': 'Invalid username or password'}, status=400)

# SignUp
class AccountSignUpAPIView(generics.CreateAPIView):
	model = Account
	serializer_class = AccountSignUpSerializer

# Account CRUD
class AccountRetrieveUpdateDestroyAPIView(UserLoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

class HomeOfficeGeoAPIView(UserLoginRequiredMixin, APIView):
    def get_account(self):
        if not hasattr(self.request.user, 'account'):
            raise Http404
        return self.request.user.account

    def get(self, request, *args, **kwargs):
        account = self.get_account()
        distance = distanceBetnGPS(
            (account.location_of_home.latitude, account.location_of_home.longitude), 
            (account.location_of_office.latitude, account.location_of_office.longitude)
        )
        response = {
            'total_distance': distance
        }
        return Response(response, status=200)


class AccountWithinRadiusAPIView(UserLoginRequiredMixin, APIView):
    def post(self, *args, **kwargs):
        data = self. request.data
        current_lat = data['latitude']
        current_long = data['longitude']

        distance = self.calculate_distance(current_lat, current_long)

        account_qs = Account.objects.all()
        accounts_within_radius = account_qs.annotate(distance=distance).order_by('distance').filter(distance__lt=10)
        response = AccountSerializer(accounts_within_radius, many=True)
        return Response(response.data, status=200)

    def calculate_distance(self, current_lat, current_long):
        dlat = Radians(F('location_of_home__latitude') - current_lat)
        dlong = Radians(F('location_of_home__longitude') - current_long)

        a = (Power(Sin(dlat/2), 2) + Cos(Radians(current_lat)) 
            * Cos(Radians(F('location_of_home__latitude'))) * Power(Sin(dlong/2), 2)
        )

        c = 2 * ATan2(Sqrt(a), Sqrt(1-a))
        d = 6371 * c
        return d