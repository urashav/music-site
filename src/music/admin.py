from django.contrib import admin
from .models import Playlist, Track
from django.conf import settings


class PlaylistAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'full_url',
        'original_id',
        'created_at',
        'status',
    )


admin.site.register(Playlist, PlaylistAdmin)


class TrackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'slug',
        'original_id',
        'title',
        'permalink_url',
        'genre',
        'created_at',
        'updated_at',
        'playlist_id'
    )
    search_fields = ['id', 'title', 'original_id']
    # list_filter = ('created_at', 'updated_at', 'playlist_id')

    def has_add_permission(self, request):
        return settings.DEBUG

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Track, TrackAdmin)
