from django.urls import path
from .views import RegisterView, LoginView, PhoneVerificationRequestView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('send-verification/', PhoneVerificationRequestView.as_view(), name='send_verification'),
]
