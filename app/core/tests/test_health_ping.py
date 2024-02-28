"""Tests for health ping"""
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


class HealthPingTests(TestCase):
    """Test the health ping API."""

    def test_health_check(self):
        """Test health check API."""
        client = APIClient()
        url = reverse('health-ping')
        res = client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
