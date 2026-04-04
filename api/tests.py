from django.urls import reverse
from rest_framework.test import APITestCase


class ApiSmokeTests(APITestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get(reverse('health-check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

    def test_api_root_contains_endpoints(self):
        response = self.client.get(reverse('api-root'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('endpoints', response.data)
