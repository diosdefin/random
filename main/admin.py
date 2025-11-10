from django.contrib import admin
from .models import Giveaway, Participant, Winner

@admin.register(Giveaway)
class GiveawayAdmin(admin.ModelAdmin):
    list_display = ['title', 'join_code', 'draw_time', 'is_active', 'created_by']
    list_filter = ['is_active', 'draw_time']
    search_fields = ['title', 'join_code']

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'giveaway', 'joined_at']
    list_filter = ['giveaway', 'joined_at']

@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ['participant', 'giveaway', 'won_at']
    list_filter = ['giveaway', 'won_at']