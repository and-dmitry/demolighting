from django.urls import include, path
from rest_framework import routers

from .api_views import LampViewSet


rest_router = routers.DefaultRouter()
rest_router.register('lamps', LampViewSet)

app_name = 'lights'
urlpatterns = [
    path('api/', include(rest_router.urls)),
]
