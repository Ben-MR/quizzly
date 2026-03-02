from datetime import timedelta
from django.utils import timezone
import os
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from quiz_app.api import serializer
from quiz_app.api.permissions import IsOwnQuiz
from quiz_app.api.serializer import QuizCreateSerializer, QuizListSerializer
from .service import download_youtube_audio, generate_quiz_from_audio
from quiz_app.models import Question, Quiz



class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()   

    
    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the current action.
        Uses specialized serializers for reading lists, retrieving details, 
        creating new instances, or updating existing ones.
        """
        if self.action in ['create', 'update', 'partial_update']:
            return QuizCreateSerializer
        if self.action in ['list', 'retrieve']:
            return QuizListSerializer
        
    def get_permissions(self):
        """Returns the appropriate permissions based on the current action.
        Allows any user to create a quiz, but
        requires authentication for listing, retrieving, updating, or deleting quizzes.
        Additionally, only the creator of a quiz can update or delete it.
        """
        if self.action in ["partial_update", "destroy", "retrieve"]:
            return [IsAuthenticated(), IsOwnQuiz()]

        return super().get_permissions()


    def create(self, request, *args, **kwargs):
        """
        Main entry point for quiz generation.
        - Validates the YouTube URL.
        - Downloads audio and processes it via Gemini AI.
        - Saves the generated data to the database.
        - Returns a full 201 Created response.
        """
        video_url = request.data.get("url")    
        if not video_url:
            return Response({"error": "URL fehlt"}, status=400)        

        try:
            relative_audio_path = download_youtube_audio(video_url)
            quiz_json = generate_quiz_from_audio(os.path.join("media", relative_audio_path))
            if "error" in quiz_json:
                return Response({"error": f"AI error: {quiz_json['error']}"}, status=500)
            
            if "title" not in quiz_json:
                return Response({"error": "No valid quiz format returned by AI"}, status=500)
        except Exception as e:
             return Response(
                {"error": f"Invalid Video-URL: {str(e)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        current_user = request.user if request.user.is_authenticated else None
        new_quiz = Quiz.objects.create(
            title=quiz_json["title"],
            description=quiz_json["description"],
            creator=current_user,
            video_url=video_url,
        )
        for q in quiz_json['questions']:
            Question.objects.create(
                quiz=new_quiz,
                question_title=q['question_title'], 
                question_options=q['question_options'],
                answer=q['answer']
        )

        serializer = QuizCreateSerializer(new_quiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Updates specific fields of an existing quiz (PATCH).
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save() 
        return Response(serializer.data)
    
    def get_queryset(self):
        """
        Customizes the queryset based on time filters provided in the URL.
        Example: /api/quizzes/?filter=today or /api/quizzes/?filter=week
        """
        user = self.request.user
        queryset = Quiz.objects.filter(creator=user).order_by('-created_at')
        
        time_filter = self.request.query_params.get('filter')
        now = timezone.now()

        if time_filter == 'today':
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            queryset = queryset.filter(created_at__gte=start_of_day)
            
        elif time_filter == 'week':
            last_seven_days = now - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=last_seven_days)

        return queryset
        
