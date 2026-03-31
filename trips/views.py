from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Trip, Stop, STATUS_PLANNED, STATUS_ACTIVE, STATUS_COMPLETED
from .serializers import TripSerializer, TripDetailSerializer, StopSerializer
from .permissions import IsTripOwnerOrReadOnly
from .filters import TripFilter


class TripViewSet(viewsets.ModelViewSet):
    """
    Управление поездками котиков.

    list   -- список всех поездок (фильтрация: cat, status, title; пагинация)
    create -- создать поездку (только авторизованный, только для своего кота)
    retrieve -- детали поездки с полным списком остановок
    update/partial_update -- редактировать (только владелец)
    destroy -- удалить (только владелец)
    start   -- начать поездку POST /api/trips/{id}/start/
    complete -- завершить поездку POST /api/trips/{id}/complete/
    """

    queryset = Trip.objects.select_related('owner', 'cat').prefetch_related('stops')
    permission_classes = [IsAuthenticatedOrReadOnly, IsTripOwnerOrReadOnly]
    filterset_class = TripFilter
    search_fields = ['title', 'description', 'cat__name']
    ordering_fields = ['created_at', 'started_at', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TripDetailSerializer
        return TripSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start(self, request, pk=None):
        """Начать поездку. Статус меняется с planned на active."""
        trip = self.get_object()
        if trip.owner != request.user:
            return Response(
                {'detail': 'Только владелец может начать поездку.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if trip.status != STATUS_PLANNED:
            return Response(
                {'detail': f'Нельзя начать поездку со статусом "{trip.get_status_display()}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        trip.status = STATUS_ACTIVE
        trip.started_at = timezone.now()
        trip.save()
        return Response(TripSerializer(trip, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Завершить поездку. Требуется статус active и хотя бы одна остановка."""
        trip = self.get_object()
        if trip.owner != request.user:
            return Response(
                {'detail': 'Только владелец может завершить поездку.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        if trip.status != STATUS_ACTIVE:
            return Response(
                {'detail': f'Нельзя завершить поездку со статусом "{trip.get_status_display()}".'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not trip.stops.exists():
            return Response(
                {'detail': 'Нельзя завершить поездку без остановок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        trip.status = STATUS_COMPLETED
        trip.completed_at = timezone.now()
        trip.save()
        return Response(TripSerializer(trip, context={'request': request}).data)


class StopViewSet(viewsets.ModelViewSet):
    """
    Управление остановками поездки.
    Вложенный ресурс: /api/trips/{trip_pk}/stops/
    """

    serializer_class = StopSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsTripOwnerOrReadOnly]

    def _get_trip(self):
        return Trip.objects.get(pk=self.kwargs['trip_pk'])

    def get_queryset(self):
        return Stop.objects.filter(trip_id=self.kwargs['trip_pk']).order_by('order')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        try:
            context['trip'] = self._get_trip()
        except Trip.DoesNotExist:
            pass
        return context

    def perform_create(self, serializer):
        trip = self._get_trip()
        if trip.owner != self.request.user:
            raise PermissionDenied('Только владелец может добавлять остановки.')
        if trip.status == STATUS_COMPLETED:
            raise ValidationError('Нельзя добавлять остановки к завершённой поездке.')
        serializer.save(trip=trip)
