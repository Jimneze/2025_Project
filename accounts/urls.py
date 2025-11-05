from django.urls import path
from .views import (
    CustomLoginView, logout_view, register_view,
    verify_2fa_view, setup_2fa_view, manage_2fa_view, disable_2fa_view
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('2fa/verify/', verify_2fa_view, name='verify_2fa'),
    path('2fa/setup/', setup_2fa_view, name='setup_2fa'),
    path('2fa/manage/', manage_2fa_view, name='manage_2fa'),
    path('2fa/disable/', disable_2fa_view, name='disable_2fa'),
]