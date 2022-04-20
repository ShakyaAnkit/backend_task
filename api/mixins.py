from rest_framework.authentication import TokenAuthentication
from rest_framework import permissions

class UserLoginRequiredMixin:
	'''
	Mixin for User Login
	'''
	authentication_classes = [TokenAuthentication]
	permission_classes = [permissions.IsAuthenticated]