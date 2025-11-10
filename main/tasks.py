from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Giveaway, Participant, Winner
import random

@shared_task
def schedule_giveaway_draw(giveaway_id):
    """Фоновая задача для проведения розыгрыша"""
    try:
        giveaway = Giveaway.objects.get(id=giveaway_id)
        
        with transaction.atomic():
            participants = list(giveaway.participants.all())
            
            if not participants:
                return "Нет участников для розыгрыша"
            
            # Безопасный случайный выбор
            winners_count = min(giveaway.winners_count, len(participants))
            winners = random.sample(participants, winners_count)
            
            # Создание записей победителей
            for participant in winners:
                Winner.objects.create(
                    participant=participant,
                    giveaway=giveaway
                )
            
            # Деактивируем розыгрыш после проведения
            giveaway.is_active = False
            giveaway.save()
        
        return f"Определено {len(winners)} победителей"
    
    except Giveaway.DoesNotExist:
        return "Розыгрыш не найден"

@shared_task
def check_scheduled_giveaways():
    """Периодическая проверка розыгрышей по расписанию"""
    now = timezone.now()
    active_giveaways = Giveaway.objects.filter(
        is_active=True,
        draw_time__lte=now
    )
    
    for giveaway in active_giveaways:
        schedule_giveaway_draw.delay(giveaway.id)