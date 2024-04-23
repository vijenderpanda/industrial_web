from django.urls import include, re_path, path
from .views import *

urlpatterns = [
    path('/', home, name=home),
]
