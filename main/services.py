import random
import logging
from django.utils import timezone
from django.db import transaction
from .models import Giveaway, Winner

logger = logging.getLogger(__name__)

def perform_giveaway_draw(giveaway_id):
    """
    Синхронное проведение розыгрыша
    Для использования на PythonAnywhere вместо Celery
    """
    try:
        giveaway = Giveaway.objects.get(id=giveaway_id)
        
        # Проверки
        if not giveaway.is_active:
            return False, "Розыгрыш уже завершен"
        
        if giveaway.draw_time > timezone.now():
            return False, "Время розыгрыша еще не наступило"
        
        participants = list(giveaway.participants.all())
        
        if not participants:
            return False, "Нет участников для розыгрыша"
        
        # Проверяем, нет ли уже победителей
        if giveaway.winners.exists():
            return False, "Розыгрыш уже проведен"
        
        # Определяем количество победителей
        winners_count = min(giveaway.winners_count, len(participants))
        
        # Выбираем случайных победителей
        selected_winners = random.sample(participants, winners_count)
        
        # Создаем записи победителей в транзакции
        with transaction.atomic():
            winners_list = []
            for participant in selected_winners:
                winner = Winner.objects.create(
                    participant=participant,
                    giveaway=giveaway,
                    prize_description=f"Победитель розыгрыша '{giveaway.title}'"
                )
                winners_list.append({
                    'id': participant.user.id,
                    'username': participant.user.username,
                    'email': participant.user.email
                })
            
            # Деактивируем розыгрыш после проведения
            giveaway.is_active = False
            giveaway.save()
        
        logger.info(f"Розыгрыш {giveaway_id} завершен. Выбрано {winners_count} победителей")
        return True, {
            'message': f'Розыгрыш завершен! Выбрано {winners_count} победителей',
            'winners': winners_list,
            'winners_count': winners_count
        }
        
    except Giveaway.DoesNotExist:
        error_msg = f"Розыгрыш {giveaway_id} не найден"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Ошибка при проведении розыгрыша: {str(e)}"
        logger.error(error_msg)
        return False, error_msg