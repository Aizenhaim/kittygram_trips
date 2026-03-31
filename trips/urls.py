from django.urls import path, include
from rest_framework_nested import routers as nested_routers
from rest_framework.routers import DefaultRouter
from .views import TripViewSet, StopViewSet

router = DefaultRouter()
router.register('trips', TripViewSet, basename='trip')

trips_router = nested_routers.NestedDefaultRouter(router, 'trips', lookup='trip')
trips_router.register('stops', StopViewSet, basename='trip-stops')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(trips_router.urls)),
]
