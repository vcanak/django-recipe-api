"""Tests for ingredients"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """return a ingredient detail url to user"""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create a user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsApiTests(TestCase):
    """Test unauthenticated API requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredient"""

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Tests for authenticated API requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving list of ingredients"""

        Ingredient.objects.create(user=self.user, name='Lemon')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')

        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_list_by_user(self):
        """Test ingredient list by user"""
        other_user = create_user(
            email='other@example.com',
            password='password123'
        )
        Ingredient.objects.create(user=other_user, name='Lemon')
        ingredient = Ingredient.objects.create(user=self.user, name='Tomato')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating a ingredient"""
        ingredient = Ingredient.objects.create(user=self.user,
                                               name='Lemon')
        payload = {'name': 'Tomato'}

        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test for deleting a Ingredient"""

        ingredient = Ingredient.objects.create(user=self.user, name='Piper')
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredient_assigned_to_recipes(self):
        """Test listing ingredients assigned to recipes"""
        ingredient_1 = Ingredient.objects.create(user=self.user, name='Lemon')
        ingredient_2 = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = Recipe.objects.create(
            title='Chicken',
            time_minutes=5,
            price=Decimal('5.50'),
            user=self.user,
        )
        recipe.ingredients.add(ingredient_1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer_1 = IngredientSerializer(ingredient_1)
        serializer_2 = IngredientSerializer(ingredient_2)
        self.assertIn(serializer_1.data, res.data)
        self.assertNotIn(serializer_2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns unique results"""
        ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
        Ingredient.objects.create(user=self.user, name='Salt')
        recipe_1 = Recipe.objects.create(
            title='Chicken',
            time_minutes=5,
            price=Decimal('5.50'),
            user=self.user,
        )
        recipe_2 = Recipe.objects.create(
            title='Meetball',
            time_minutes=5,
            price=Decimal('5.50'),
            user=self.user,
        )
        recipe_1.ingredients.add(ingredient)
        recipe_2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
