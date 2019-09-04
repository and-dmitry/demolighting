from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from .models import Lamp
from .views import LampControlForm


class LoginTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_login_view(self):
        response = self.client.get(settings.LOGIN_URL)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Log in')

    # TODO: DRY
    def test_lamp_list_no_auth(self):
        response = self.client.get('/lamps/')
        self.assertRedirects(response, f'{settings.LOGIN_URL}?next=/lamps/')

    def test_lamp_detail_no_auth(self):
        response = self.client.get('/lamps/1')
        self.assertRedirects(response, f'{settings.LOGIN_URL}?next=/lamps/1')

    def test_lamp_control_no_auth(self):
        response = self.client.get('/lamps/1/control')
        self.assertRedirects(response,
                             f'{settings.LOGIN_URL}?next=/lamps/1/control')


class LampsSiteViewsTests(TestCase):

    def setUp(self):
        self.client = Client()
        user = User.objects.create_user('testuser')
        self.client.force_login(user)

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

    def test_control_get(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.get(f'/lamps/{lamp.pk}/control')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lights/lamp_control.html')
        self.assertEqual(lamp, response.context['lamp'])

    def test_control_get_status_off(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.get(f'/lamps/{lamp.pk}/control')
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertEqual(form['status'].value(), LampControlForm.STATUS_OFF)

    def test_control_post_action(self):
        lamp = Lamp.objects.create(name='lamp1')
        new_brightness = 70

        self.client.post(f'/lamps/{lamp.pk}/control', {
            'brightness': str(new_brightness),
            'status': 'on'})

        lamp.refresh_from_db()
        self.assertEqual(lamp.brightness, new_brightness)
        self.assertTrue(lamp.is_on)

    def test_control_post_redirect(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.post(f'/lamps/{lamp.pk}/control',
                                    {'brightness': '20',
                                     'status': 'on'})
        self.assertRedirects(response, f'/lamps/{lamp.pk}')

    @mock.patch('lights.views.lamp_service', autospec=True)
    def test_control_service_call(self, mock_lamp_service):
        lamp = Lamp.objects.create(name='lamp1')
        new_brightness = 75

        self.client.post(f'/lamps/{lamp.pk}/control', {
            'brightness': str(new_brightness),
            'status': 'on'})

        mock_lamp_service.set_lamp_mode.assert_called_once_with(
            lamp,
            on=True,
            brightness=new_brightness)

    def test_control_get_404(self):
        response = self.client.get(f'/lamps/1/control')
        self.assertEqual(response.status_code, 404)

    def test_control_post_404(self):
        response = self.client.post(f'/lamps/1/control')
        self.assertEqual(response.status_code, 404)

    def test_control_validation_error_response(self):
        lamp = Lamp.objects.create(name='lamp1')

        response = self.client.post(f'/lamps/{lamp.pk}/control', {
            'brightness': 101,
            'status': 'on'})

        self.assertEqual(response.status_code, 200)

    @mock.patch('lights.views.lamp_service', autospec=True)
    def test_control_validation_error_action(self, mock_lamp_service):
        lamp = Lamp.objects.create(name='lamp1')

        self.client.post(f'/lamps/{lamp.pk}/control', {
            'brightness': 101,
            'status': 'on'})

        mock_lamp_service.assert_not_called()
