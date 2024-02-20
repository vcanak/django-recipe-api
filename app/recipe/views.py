""" Views for Recipe API"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from recipe import serializers


class RecipeViewSet(viewsets.ModelViewSet):
    """View for managing recipe API"""

    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for logged in user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        "Return serializer class for request"
        if self.action == 'list':
            return serializers.RecipeSerializer
        return serializers.RecipeDetailSerializer

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
