from django.test import TestCase, Client
from django.urls import reverse

class SimpleTests(TestCase):
    def test_homepage_status_code(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_page_status_code(self):
        client = Client()
        response = client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)
