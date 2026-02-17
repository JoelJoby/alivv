from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from website.models import Country, Customer, CustomerDetails, State

class SimpleTests(TestCase):
    def test_homepage_status_code(self):
        client = Client()
        response = client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_page_status_code(self):
        client = Client()
        response = client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

class CheckoutTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='Test Country', iso_alpha_2='TC', iso_alpha_3='TCO')

    def test_checkout_context_contains_countries(self):
        client = Client()
        response = client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('countries', response.context)
        self.assertEqual(len(response.context['countries']), 1)
        self.assertEqual(response.context['countries'][0], self.country)


class CheckoutAddressTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test@test.com', email='test@test.com', password='password')
        self.country = Country.objects.create(name='Test Country', iso_alpha_2='TC', iso_alpha_3='TCO')
        self.state = State.objects.create(name='Test State', country=self.country)
        self.customer = Customer.objects.create(email='test@test.com', first_name='John', last_name='Doe', phone='1234567890')
        self.address = CustomerDetails.objects.create(
            customer=self.customer,
            address_line_1='123 Test St',
            city='Test City',
            country=self.country,
            state=self.state,
            postcode='12345'
        )

    def test_checkout_shows_addresses_for_logged_in_user(self):
        self.client.login(username='test@test.com', password='password')
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a saved address:')
        self.assertContains(response, '123 Test St')
        # Check for data attributes (checking just existence of substring is enough mostly)
        self.assertContains(response, f'data-country="{self.country.id}"')
        self.assertContains(response, f'data-state="{self.state.id}"')
