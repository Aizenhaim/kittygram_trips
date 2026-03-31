from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Cat
from .serializers import CatSerializer
from .permissions import IsOwnerOrReadOnly


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.select_related('owner').all()
    serializer_class = CatSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
