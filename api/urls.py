from django.urls import path, include

from . import views

app_name = 'api'

urlpatterns = [
    
    # login
    path('login/', views.LoginAPIView.as_view()),
    path('signup/', views.AccountSignUpAPIView.as_view()),
    path('account/<int:pk>/', views.AccountRetrieveUpdateDestroyAPIView.as_view()),
    path('account/<int:pk>/geo', views.HomeOfficeGeoAPIView.as_view()),
    path('account/within-radius/', views.AccountWithinRadiusAPIView.as_view()),
]