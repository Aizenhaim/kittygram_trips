from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .views import CatViewSet

router = DefaultRouter()
router.register('cats', CatViewSet, basename='cat')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def achievements_list(request):
    return Response([])


urlpatterns = [
    path('', include(router.urls)),
    path('achievements/', achievements_list),
]
