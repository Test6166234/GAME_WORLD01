from rest_framework import serializers

from django.core.validators import MaxValueValidator
from .models import *

class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Player
        fields = ['id', 'score', 'last_seen', 'created_at', 'username']

class SnakeScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SnakeScore
        fields = ['id', 'score', 'created_at']

class ClickerScoreSerializer(serializers.ModelSerializer):
    player = serializers.PrimaryKeyRelatedField(read_only=True)
    score = serializers.IntegerField(validators=[MaxValueValidator(999999)]) # Поправил лимит, чтобы не мешал играть
    cps = serializers.FloatField(validators=[MaxValueValidator(999)])

    class Meta:
        model = ClickerScore
        fields = ['id', 'score', 'cps', 'mode', 'player', 'date']

class TaskSerializer(serializers.ModelSerializer):
    player_id = serializers.IntegerField(source='player.id', read_only=True)
    player_name = serializers.CharField(source='player.user.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'player_id', 'player_name', 'created_at']
        read_only_fields = ['created_at']







class NeTankScoreSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(validators=[MaxValueValidator(999999)])
    class Meta:
        model = NeTankScore
        fields = ['id', 'player', 'score', 'created_at']
        read_only_fields = ['player', 'created_at']
