from django.test import TestCase, Client
from django.urls import reverse

class SystemIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_status(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_donor_search_accessible(self):
        response = self.client.get(reverse('donors:search'))
        self.assertEqual(response.status_code, 200)
