from django.test import Client, TestCase

from .models import Lamp


class LampsSiteViewsTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_root_redirect(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/lamps/')

    def test_list(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.get('/lamps/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lights/lamp_list.html')
        self.assertIn(lamp, response.context['lamp_list'])

    def test_details(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.get(f'/lamps/{lamp.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lights/lamp_detail.html')
        self.assertEqual(lamp, response.context['lamp'])
