from rest_framework import serializers
from .models import Trip, Stop, STATUS_COMPLETED


class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        fields = ('id', 'title', 'description', 'latitude', 'longitude', 'order', 'visited_at')

    def validate(self, attrs):
        trip = self.context.get('trip')
        if trip and trip.status == STATUS_COMPLETED:
            raise serializers.ValidationError(
                'Нельзя добавлять остановки к завершённой поездке.'
            )
        return attrs


class TripSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    cat_name = serializers.CharField(source='cat.name', read_only=True)
    stops_count = serializers.IntegerField(source='stops.count', read_only=True)

    class Meta:
        model = Trip
        fields = (
            'id', 'owner', 'cat', 'cat_name', 'title', 'description',
            'status', 'started_at', 'completed_at', 'created_at', 'stops_count',
        )
        read_only_fields = ('owner', 'status', 'started_at', 'completed_at', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        cat = attrs.get('cat')
        if cat and request and cat.owner != request.user:
            raise serializers.ValidationError(
                {'cat': 'Можно создавать поездки только для своих котов.'}
            )
        return attrs


class TripDetailSerializer(TripSerializer):
    stops = StopSerializer(many=True, read_only=True)

    class Meta(TripSerializer.Meta):
        fields = TripSerializer.Meta.fields + ('stops',)
