from rest_framework import serializers
from sympy import re
from quiz_app.models import Quiz, Question
from django.contrib.auth import get_user_model

class QuizQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed Question information.
    Includes technical metadata like ID and timestamps for full transparency.
    Used typically in detail views or for internal processing.
    """
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer', 'created_at', 'updated_at']

class QuizQuestionListSerializer(serializers.ModelSerializer):
    """
    A lightweight Serializer for Question objects.
    Optimized for lists or nested quiz outputs where only core 
    question data (title, options, answer) is required without metadata.
    """
    class Meta:
        model = Question
        fields = ['id', 'question_title', 'question_options', 'answer']

class QuizCreateSerializer(serializers.ModelSerializer):
    """
    Primary Serializer for creating and updating Quiz instances.
    Handles complex nested relationships and secure user attribution.
    """
    creator = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), 
        write_only=True,
        required=False 
    )
    questions = QuizQuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'creator', 'created_at', 'updated_at', 'video_url', 'questions']

    def update(self, instance, validated_data):
        """
        Custom update logic to allow partial modifications of title and description
        while preserving existing data if fields are missing from the request.
        """
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance
    

class QuizListSerializer(serializers.ModelSerializer):
    """
    Optimized Serializer for listing multiple Quizzes.
    Uses QuizQuestionListSerializer to provide a cleaner, 
    less metadata-heavy output for frontend overview components.
    """
    questions = QuizQuestionListSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'video_url', 'questions']

    def get_embed_video_url(self, obj):
        """
        Transforms a standard YouTube URL into an embeddable format.
        Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ 
        becomes: https://www.youtube.com/embed/dQw4w9WgXcQ
        """
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", obj.video_url)
        if video_id_match:
            video_id = video_id_match.group(1)
            return f"https://www.youtube.com/embed/{video_id}"
        return None



