from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Lamp


class LampTests(TestCase):

    def test_minimal(self):
        lamp = Lamp(name='some lamp')
        lamp.full_clean()
        lamp.save()

    def test_defaults(self):
        lamp = Lamp(name='some lamp')
        lamp.full_clean()
        lamp.save()
        self.assertEqual(lamp.is_on, False)
        self.assertEqual(lamp.brightness, 100)

    def test_full(self):
        lamp = Lamp(name='some lamp',
                    is_on=True,
                    brightness=50)
        lamp.full_clean()
        lamp.save()

    def test_brightness_too_low(self):
        lamp = Lamp(name='some lamp', brightness=0)
        with self.assertRaises(ValidationError) as cm:
            lamp.full_clean()
        self.assertIn('brightness', cm.exception.message_dict)

    def test_brightness_too_high(self):
        lamp = Lamp(name='some lamp', brightness=101)
        with self.assertRaises(ValidationError) as cm:
            lamp.full_clean()
        self.assertIn('brightness', cm.exception.message_dict)
