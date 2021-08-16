from django.contrib import admin

from main.models import Audio

@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'file',
        'created_at'
    ]
    list_select_related = ['user']

