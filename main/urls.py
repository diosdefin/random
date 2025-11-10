from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GiveawayViewSet, MyParticipationsViewSet, CustomAuthToken, UserRegistrationView
from django.http import JsonResponse

def api_root(request):
    """Простая корневая страница API"""
    return JsonResponse({
        'message': 'Giveaway Service API',
        'endpoints': {
            'register': '/api/auth/register/',
            'login': '/api/auth/token/',
            'giveaways': '/api/giveaways/',
            'my_participations': '/api/my-participations/',
            'admin': '/admin/'
        }
    })

router = DefaultRouter()
router.register(r'giveaways', GiveawayViewSet, basename='giveaway')
router.register(r'my-participations', MyParticipationsViewSet, basename='myparticipations')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/token/', CustomAuthToken.as_view(), name='api_token_auth'),
]