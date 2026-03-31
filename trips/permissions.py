from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsTripOwnerOrReadOnly(BasePermission):
    """Редактировать и удалять поездку может только её владелец."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        trip = obj if hasattr(obj, 'owner') else obj.trip
        return trip.owner == request.user
