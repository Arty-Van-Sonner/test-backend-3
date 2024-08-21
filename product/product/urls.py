# Savchenko AD 20.08.2024

from django.urls import include, path
from django.contrib import admin

name = 'product'

urlpatterns = [
    path('admin/', admin.site.urls),
]
