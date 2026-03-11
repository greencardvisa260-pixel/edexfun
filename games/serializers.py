from rest_framework import serializers
from .models import Game, Question


class QuestionSerializer(serializers.ModelSerializer):
    image_src = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'tile_number', 'question_type', 'question_text',
            'correct_answer', 'points', 'special',
            'option_a', 'option_b', 'option_c', 'option_d',
            'image_src', 'time_limit', 'hint'
        ]

    def get_image_src(self, obj):
        return obj.get_image()


class GameSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    owner_name = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'owner', 'owner_name',
            'grid_size', 'visibility', 'subject', 'grade_level', 'cover_image_url',
            'created_at', 'updated_at', 'questions', 'question_count'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username

    def get_question_count(self, obj):
        return obj.question_count()


class GameListSerializer(serializers.ModelSerializer):
    owner_name = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'owner_name',
            'grid_size', 'visibility', 'subject', 'grade_level', 'cover_image_url',
            'created_at', 'question_count'
        ]

    def get_owner_name(self, obj):
        return f"{obj.owner.first_name} {obj.owner.last_name}".strip() or obj.owner.username

    def get_question_count(self, obj):
        return obj.question_count()
