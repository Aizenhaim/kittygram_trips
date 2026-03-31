from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CatViewSet

router = DefaultRouter()
router.register('cats', CatViewSet, basename='cat')

urlpatterns = [path('', include(router.urls))]
