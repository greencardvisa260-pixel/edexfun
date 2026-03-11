from django.contrib import admin
from .models import Game, Question

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'grid_size', 'visibility', 'question_count', 'created_at']
    list_filter = ['visibility', 'grid_size']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['tile_number', 'game', 'question_type', 'points', 'special']
    list_filter = ['question_type', 'special']
