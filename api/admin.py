from django.contrib import admin
from .models import (
    Player,
    SnakeScore,
    ClickerScore,
    Task,
    GameItem,

)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'score', 'last_seen', 'created_at')
    search_fields = ('user__username',)
    ordering = ('-score',)
    readonly_fields = ('score', 'created_at', 'last_seen')
    list_filter = ('created_at',)


@admin.register(SnakeScore)
class SnakeScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'score', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    ordering = ('-score',)
    readonly_fields = ('created_at',)


@admin.register(ClickerScore)
class ClickerScoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'score', 'date')
    list_filter = ('date',)
    ordering = ('-score',)
    readonly_fields = ('date',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'player', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'player__user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_editable = ('status',)



