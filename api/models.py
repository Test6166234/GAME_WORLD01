from django.db import models
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class SnakeScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='snake_scores')
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class ClickerScore(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='clicker_scores')
    score = models.IntegerField(default=0)
    cps = models.FloatField(default=0)
    mode = models.CharField(max_length=10, default='1s')
    date = models.DateTimeField(auto_now_add=True)

class Task(models.Model):
    STATUS_CHOICES = (('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done'))
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)

class GameItem(models.Model):
    TYPE_CHOICES = (('powerup', 'Power-up'), ('cosmetic', 'Cosmetic'))
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    value = models.IntegerField(default=0)





class NeTankScore(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='netank_scores')
    score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
