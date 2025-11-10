# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Giveaway, Participant, Winner
from .serializers import GiveawaySerializer, ParticipantSerializer, WinnerSerializer
from .tasks import schedule_giveaway_draw
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = []  # Разрешаем доступ без аутентификации
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Создаем токен для нового пользователя
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email
        })
    
    
class GiveawayViewSet(viewsets.ModelViewSet):
    serializer_class = GiveawaySerializer
    permission_classes = [IsAuthenticated]
    
    # ДОБАВЬТЕ ЭТОТ АТРИБУТ:
    queryset = Giveaway.objects.all()
    
    def get_queryset(self):
        # Организаторы видят свои розыгрыши, игроки - активные
        if self.request.query_params.get('my_giveaways'):
            return Giveaway.objects.filter(created_by=self.request.user)
        return Giveaway.objects.filter(is_active=True)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def enter(self, request, pk=None):
        """Участие в розыгрыше по коду"""
        giveaway = self.get_object()
        
        # Проверки
        if giveaway.participants.filter(user=request.user).exists():
            return Response(
                {'error': 'Вы уже участвуете в этом розыгрыше'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if giveaway.max_participants and giveaway.participants.count() >= giveaway.max_participants:
            return Response(
                {'error': 'Достигнуто максимальное количество участников'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if giveaway.draw_time < timezone.now():
            return Response(
                {'error': 'Регистрация на розыгрыш завершена'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Создание участника
        participant = Participant.objects.create(
            user=request.user,
            giveaway=giveaway
        )
        
        return Response(
            {'message': 'Вы успешно зарегистрированы в розыгрыше!'},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def draw_winner(self, request, pk=None):
        """Запуск розыгрыша (только для организатора)"""
        giveaway = self.get_object()
        
        if giveaway.created_by != request.user:
            return Response(
                {'error': 'Только организатор может запустить розыгрыш'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Запускаем фоновую задачу
        schedule_giveaway_draw.delay(giveaway.id)
        
        return Response(
            {'message': 'Розыгрыш запущен, победители будут определены в ближайшее время'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Список участников розыгрыша"""
        giveaway = self.get_object()
        participants = giveaway.participants.all()
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def winners(self, request, pk=None):
        """Список победителей розыгрыша"""
        giveaway = self.get_object()
        winners = giveaway.winners.all()
        serializer = WinnerSerializer(winners, many=True)
        return Response(serializer.data)

class MyParticipationsViewSet(viewsets.ReadOnlyModelViewSet):
    """Розыгрыши, в которых участвует текущий пользователь"""
    serializer_class = GiveawaySerializer
    permission_classes = [IsAuthenticated]
    
    # ДОБАВЬТЕ И ЗДЕСЬ:
    queryset = Giveaway.objects.all()
    
    def get_queryset(self):
        return Giveaway.objects.filter(
            participants__user=self.request.user
        )
    


