from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Giveaway, Participant
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Создание тестовых данных для розыгрышей'

    def handle(self, *args, **options):
        # Создаем тестовых пользователей
        organizer, _ = User.objects.get_or_create(
            username='organizer',
            defaults={'email': 'organizer@example.com', 'is_staff': True}
        )
        organizer.set_password('password123')
        organizer.save()

        participant1, _ = User.objects.get_or_create(
            username='participant1',
            defaults={'email': 'participant1@example.com'}
        )
        participant1.set_password('password123')
        participant1.save()

        participant2, _ = User.objects.get_or_create(
            username='participant2',
            defaults={'email': 'participant2@example.com'}
        )
        participant2.set_password('password123')
        participant2.save()

        # Создаем тестовые розыгрыши
        giveaway1 = Giveaway.objects.create(
            title='Тестовый розыгрыш iPhone 15',
            description='Выиграй новый iPhone 15!',
            join_code='IPHONE2024',
            max_participants=100,
            draw_time=timezone.now() + timedelta(days=7),
            created_by=organizer,
            winners_count=1
        )

        giveaway2 = Giveaway.objects.create(
            title='Розыгрыш MacBook Pro',
            description='Шанс выиграть MacBook Pro M3',
            join_code='MACBOOK2024',
            max_participants=50,
            draw_time=timezone.now() + timedelta(days=3),
            created_by=organizer,
            winners_count=2
        )

        # Регистрируем участников
        Participant.objects.create(user=participant1, giveaway=giveaway1)
        Participant.objects.create(user=participant2, giveaway=giveaway1)
        Participant.objects.create(user=participant1, giveaway=giveaway2)

        self.stdout.write(
            self.style.SUCCESS('✅ Тестовые данные успешно созданы!')
        )
        self.stdout.write('👥 Пользователи: organizer/password123, participant1/password123, participant2/password123')
        self.stdout.write('🎪 Розыгрыши: IPHONE2024, MACBOOK2024')