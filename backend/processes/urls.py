from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessViewSet, SystemInfoViewSet

router = DefaultRouter()
router.register(r'processes', ProcessViewSet, basename='process')
router.register(r'system-info', SystemInfoViewSet, basename='system-info')

urlpatterns = [
    path('', include(router.urls)),
]
