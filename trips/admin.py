from django.contrib import admin
from .models import Trip, Stop


class StopInline(admin.TabularInline):
    model = Stop
    extra = 0
    fields = ('order', 'title', 'latitude', 'longitude', 'visited_at')


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('title', 'cat', 'owner', 'status', 'started_at', 'completed_at')
    list_filter = ('status',)
    search_fields = ('title', 'cat__name', 'owner__username')
    inlines = [StopInline]


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    list_display = ('title', 'trip', 'order', 'visited_at')
    list_filter = ('trip__status',)
    search_fields = ('title', 'trip__title')
