# models.py
from django.contrib.auth.models import User
from django.db import models

class Giveaway(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    join_code = models.CharField(max_length=20, unique=True)  # Код для входа
    max_participants = models.PositiveIntegerField(null=True, blank=True)  # Ограничение участников
    draw_time = models.DateTimeField()  # Время розыгрыша
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_giveaways')
    created_at = models.DateTimeField(auto_now_add=True)
    winners_count = models.PositiveIntegerField(default=1)  # Количество победителей
    
    def __str__(self):
        return self.title

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE, related_name='participants')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'giveaway']  # Один пользователь - одна запись

class Winner(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='wins')
    giveaway = models.ForeignKey(Giveaway, on_delete=models.CASCADE, related_name='winners')
    won_at = models.DateTimeField(auto_now_add=True)
    prize_description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['participant', 'giveaway']