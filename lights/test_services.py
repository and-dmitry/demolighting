from unittest import mock

from django.test import TestCase

from .models import Lamp
from .services import ExternalError, LampService
from .switch import Switch, SwitchError


class LampServiceTests(TestCase):

    def setUp(self):
        self.mock_switch = mock.create_autospec(Switch,
                                                spec_set=True,
                                                instance=True)
        self.service = LampService(self.mock_switch)

    def test_return(self):
        lamp = Lamp.objects.create(name='the lamp')

        instance = self.service.set_lamp_mode(lamp.pk, on=True)
        self.assertEqual(instance, lamp)

    def test_turn_on(self):
        lamp = Lamp.objects.create(name='the lamp')

        self.service.set_lamp_mode(lamp.pk, on=True)

        self.mock_switch.turn_on.assert_called_once_with(lamp.pk)
        self.mock_switch.set_brightness.assert_not_called()
        lamp.refresh_from_db()
        self.assertEqual(lamp.is_on, True)
        self.assertIsNotNone(lamp.last_switch)

    def test_turn_off(self):
        lamp = Lamp.objects.create(name='the lamp', is_on=True)

        self.service.set_lamp_mode(lamp.pk, on=False)

        self.mock_switch.turn_off.assert_called_once_with(lamp.pk)
        lamp.refresh_from_db()
        self.assertEqual(lamp.is_on, False)
        self.assertIsNotNone(lamp.last_switch)

    def test_change_brightness(self):
        lamp = Lamp.objects.create(name='the lamp', brightness=50)
        new_brightness = lamp.brightness + 10
        self.service.set_lamp_mode(lamp.pk, brightness=new_brightness)

        self.mock_switch.set_brightness.assert_called_once_with(
            lamp_id=lamp.pk,
            brightness=new_brightness)
        self.mock_switch.turn_on.assert_not_called()
        self.mock_switch.turn_off.assert_not_called()
        lamp.refresh_from_db()
        self.assertEqual(lamp.brightness, new_brightness)
        self.assertIsNone(lamp.last_switch)

    def test_period_on_off(self):
        """Turn on, off, check period."""
        brightness = 77
        lamp = Lamp.objects.create(name='the lamp',
                                   is_on=False,
                                   brightness=brightness)

        self.service.set_lamp_mode(lamp.pk, on=True)

        lamp.refresh_from_db()
        period = lamp.periods.latest('start')
        self.assertEqual(period.brightness, brightness)
        self.assertEqual(period.start, lamp.last_switch)
        self.assertIsNone(period.end)

        self.service.set_lamp_mode(lamp.pk, on=False)

        lamp.refresh_from_db()
        period.refresh_from_db()
        self.assertEqual(period.end, lamp.last_switch)

    def test_change_brightness_when_off(self):
        """Test change of brightness when lamp is off.

        Should not affect periods.
        """
        lamp = Lamp.objects.create(name='the lamp', brightness=50)
        new_brightness = lamp.brightness + 10
        self.service.set_lamp_mode(lamp.pk, brightness=new_brightness)

        lamp.refresh_from_db()
        self.assertEqual(lamp.periods.count(), 0)

    def test_change_brightness_when_on(self):
        """Test change of brightness when lamp is on.

        Should reset period.
        """
        lamp = Lamp.objects.create(name='the lamp', brightness=50)
        self.service.set_lamp_mode(lamp.pk, on=True)
        first_period = lamp.periods.latest('start')

        new_brightness = lamp.brightness + 10
        self.service.set_lamp_mode(lamp.pk, brightness=new_brightness)

        second_period = lamp.periods.latest('start')
        self.assertNotEqual(second_period.pk, first_period.pk)

    def test_switch_error(self):
        lamp = Lamp.objects.create(name='the lamp')

        self.mock_switch.turn_on.side_effect = SwitchError('switch error')
        with self.assertRaises(ExternalError):
            self.service.set_lamp_mode(lamp.pk, on=True)

        lamp.refresh_from_db()
        self.assertEqual(lamp.is_on, False)


# TODO: no change - switch on, switch on
# TODO: no lamp
# TODO: return instance?
# TODO: turn on, change brightness;
# TODO: turn off, change brightness
