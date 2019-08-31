from django.urls import include, path
from rest_framework import routers

from . import views
from .api_views import LampViewSet


rest_router = routers.DefaultRouter()
rest_router.register('lamps', LampViewSet)

app_name = 'lights'
urlpatterns = [
    path('api/', include(rest_router.urls)),
    path('', views.root_view),
    path('lamps/', views.LampListView.as_view(), name='lamp-site-list'),
    path('lamps/<int:pk>',
         views.LampDetailView.as_view(),
         name='lamp-site-detail'),
    path('lamps/<int:pk>/control',
         views.LampControlView.as_view(),
         name='lamp-site-control'),
]
