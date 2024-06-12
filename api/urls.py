from api.views import *
from django.urls import path


__all__ = ['urls']

urls = [
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('profile', profile, name='profile')
]