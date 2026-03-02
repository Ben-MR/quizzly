from django.urls import path, include
from .views import QuizViewSet
from rest_framework import routers

router = routers.DefaultRouter() 
router.register(r'quizzes', QuizViewSet, basename="quizzes")

urlpatterns = [
    path('', include(router.urls)),
]