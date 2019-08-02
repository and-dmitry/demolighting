"""API integration tests."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Lamp


class BasicTests(TestCase):

    def test_no_auth(self):
        client = APIClient()
        response = client.get('/api/')
        self.assertEqual(response.status_code, 403)


class LampsTests(TestCase):

    def setUp(self):
        user = User.objects.create_user('testuser')
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_root(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('application/json', response['Content-Type'])
        self.assertIn('lamps', response.json())

    def test_list_basics(self):
        lamps = [Lamp.objects.create(name=f'lamp{i}') for i in range(3)]

        response = self.client.get('/api/lamps/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['count'], len(lamps))

    def test_list_lamp_repr(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.get('/api/lamps/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        lamp_repr = data['results'][0]
        self.assertEqual(lamp_repr['name'], lamp.name)
        self.assertEqual(lamp_repr['is_on'], lamp.is_on)
        self.assertEqual(lamp_repr['brightness'], lamp.brightness)
        self.assertIn('url', lamp_repr)

    def test_lamp_details(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.get('/api/lamps/')
        self.assertEqual(response.status_code, 200)

        lamp_url = response.json()['results'][0]['url']

        response = self.client.get(lamp_url)
        self.assertEqual(response.status_code, 200)

        lamp_repr = response.json()
        self.assertEqual(lamp_repr['name'], lamp.name)
        self.assertEqual(lamp_repr['is_on'], lamp.is_on)
        self.assertEqual(lamp_repr['brightness'], lamp.brightness)
        self.assertEqual(lamp_repr['url'], lamp_url)

    def test_turn_on(self):
        brightness = 15
        lamp = Lamp.objects.create(name='lamp1',
                                   is_on=False,
                                   brightness=brightness)

        response = self.client.get('/api/lamps/')
        self.assertEqual(response.status_code, 200)

        lamp_url = response.json()['results'][0]['url']
        response = self.client.patch(lamp_url, {'is_on': True})
        self.assertEqual(response.status_code, 200)

        lamp.refresh_from_db()
        self.assertEqual(lamp.is_on, True)
        self.assertEqual(lamp.brightness, brightness,
                         msg='partial update should not change other fields')

    def test_change_brightness(self):
        old_brightness = 50
        new_brightness = 60
        lamp = Lamp.objects.create(name='lamp1', brightness=old_brightness)

        response = self.client.get('/api/lamps/')
        self.assertEqual(response.status_code, 200)

        lamp_url = response.json()['results'][0]['url']
        response = self.client.patch(lamp_url, {'brightness': new_brightness})
        self.assertEqual(response.status_code, 200)

        lamp.refresh_from_db()
        self.assertEqual(lamp.brightness, new_brightness)

    def test_post(self):
        response = self.client.post('/api/lamps/', {'name': 'lamp name'})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete(self):
        lamp = Lamp.objects.create(name='lamp1')
        response = self.client.delete(f'/api/lamps/{lamp.id}/')
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_change_name(self):
        name = 'the lamp'
        lamp = Lamp.objects.create(name=name)
        response = self.client.patch(f'/api/lamps/{lamp.id}/',
                                     {'name': 'new name'})
        # DRF default behaviour is to silently ignore changes to
        # read-only fields. I'm fine with that.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lamp.refresh_from_db()
        self.assertEqual(lamp.name, name)


# TODO: test paging
# TODO: use status.HTTP_*
