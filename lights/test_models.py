import datetime
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from .models import Lamp, WorkingPeriod


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
                    brightness=50,
                    last_switch=timezone.now())
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

    def test_total_working_time_zero(self):
        lamp = Lamp.objects.create(name='lamp')
        self.assertEqual(lamp.total_working_time, timedelta())

    def test_total_working_time_no_active(self):
        """Test total time when all periods are closed."""
        lamp = Lamp.objects.create(name='the lamp')
        other_lamp = Lamp.objects.create(name='other lamp')
        period1 = lamp.periods.create(
            brightness=1,
            start=datetime.datetime(2019, 1, 1, 10, tzinfo=timezone.utc),
            end=datetime.datetime(2019, 1, 1, 11, tzinfo=timezone.utc))
        period2 = lamp.periods.create(
            brightness=1,
            start=datetime.datetime(2019, 1, 1, 13, tzinfo=timezone.utc),
            end=datetime.datetime(2019, 1, 1, 15, tzinfo=timezone.utc))
        other_lamp.periods.create(
            brightness=1,
            start=datetime.datetime(2019, 1, 1, 2, tzinfo=timezone.utc),
            end=datetime.datetime(2019, 1, 1, 5, tzinfo=timezone.utc))

        expected_duration = period1.duration + period2.duration
        self.assertEqual(lamp.total_working_time, expected_duration)

    def test_total_working_time_with_active(self):
        """Test total time with active period."""
        lamp = Lamp.objects.create(name='the lamp')
        other_lamp = Lamp.objects.create(name='other lamp')
        closed_period = lamp.periods.create(
            brightness=1,
            start=datetime.datetime(2019, 1, 1, 10, tzinfo=timezone.utc),
            end=datetime.datetime(2019, 1, 1, 11, tzinfo=timezone.utc))
        active_period = lamp.periods.create(
            brightness=1,
            start=datetime.datetime(2019, 1, 1, 13, tzinfo=timezone.utc))
        other_lamp.periods.create(
            brightness=1,
            start=datetime.datetime(2019, 1, 1, 2, tzinfo=timezone.utc),
            end=datetime.datetime(2019, 1, 1, 5, tzinfo=timezone.utc))

        expected_duration = closed_period.duration + active_period.duration
        delta = abs(lamp.total_working_time - expected_duration)
        self.assertLess(delta, timedelta(seconds=1))


class WorkingPeriodTests(TestCase):

    def test_minimal(self):
        lamp = Lamp.objects.create(name='lamp')
        period = WorkingPeriod(lamp=lamp, brightness=33, start=timezone.now())
        period.full_clean()
        period.save()

    def test_full(self):
        lamp = Lamp.objects.create(name='lamp')
        period = WorkingPeriod(lamp=lamp, brightness=33, start=timezone.now(),
                               end=timezone.now())
        period.full_clean()
        period.save()

    def test_duration_closed(self):
        lamp = Lamp.objects.create(name='lamp')
        start = datetime.datetime(2019, 1, 1, 10, tzinfo=timezone.utc)
        end = datetime.datetime(2019, 1, 1, 11, tzinfo=timezone.utc)
        period = WorkingPeriod(lamp=lamp, brightness=33, start=start, end=end)
        self.assertEqual(period.duration, end - start)

    def test_duration_open(self):
        lamp = Lamp.objects.create(name='lamp')
        period = WorkingPeriod(
            lamp=lamp,
            brightness=33,
            start=datetime.datetime(2019, 1, 1, 10, tzinfo=timezone.utc))
        self.assertIsInstance(period.duration, timedelta)
