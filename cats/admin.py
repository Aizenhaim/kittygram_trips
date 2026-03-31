from django.contrib import admin
from .models import Cat


@admin.register(Cat)
class CatAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'birth_year', 'owner')
    list_filter = ('color',)
    search_fields = ('name', 'owner__username')
