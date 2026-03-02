from rest_framework import permissions

class IsOwnQuiz(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (obj.creator_id == user.id)
                