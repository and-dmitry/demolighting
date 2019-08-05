"""Service layer.

Implementing business logic here to keep models simple.
"""

import logging

from django.db import transaction
from django.utils import timezone

from .models import Lamp, WorkingPeriod
from .switch import Switch, SwitchError


logger = logging.getLogger(__name__)


class ExternalError(Exception):
    """External system error."""


class LampService:

    """Service for controlling lamps."""

    def __init__(self, external_switch):
        self.switch = external_switch

    def set_lamp_mode(self, lamp_id, *, on=None, brightness=None):
        """Set operating mode for a lamp.

        Turn the lamp on/off, set brightness.

        This method does all the required processing: applies
        parameters to the actual lamp through the switch, updates the
        information in the database, etc. These actions are wrapped in
        a transaction. If switch operation fails, the model changes
        are rolled back.

        Turning lamp on starts (creates) new active working
        period. Active period is the last (order by start desc)
        period. It should not have "end" timestamp set. Turning lamp
        off closes active period (sets "end").

        Changing brightness when lamp is on closes active period and
        starts a new one.

        :returns: Lamp instance
        :raises ExternalError:

        """
        with transaction.atomic():
            instance = self._persist_mode(lamp_id, on, brightness)
            self._call_switch(lamp_id, on, brightness)
        return instance

    def _persist_mode(self, lamp_id, on, brightness):
        """Save mode change to db.

        :returns: Lamp instance
        """
        # TODO: check for changes
        now = timezone.now()
        lamp = Lamp.objects.get(pk=lamp_id)
        if on is not None:
            lamp.is_on = on
            lamp.last_switch = now
        if brightness is not None:
            lamp.brightness = brightness
        lamp.save()

        if on:
            _open_period(lamp, now, brightness)
        elif on is False:
            _close_period(lamp, now)
        elif lamp.is_on and brightness is not None:
            # brightness changed when light was on, splitting period
            _close_period(lamp, now)
            _open_period(lamp, now, brightness)
        return lamp

    def _call_switch(self, lamp_id, on, brightness):
        """Perform calls to the switch.

        This is supposed to control the actual lamps.

        :raises ExternalError:
        """
        # TODO: set brightness only when turning on (regardless of
        # actual brightness change)?
        try:
            if brightness is not None:
                self.switch.set_brightness(
                    lamp_id=lamp_id,
                    brightness=brightness)
            if on is True:
                self.switch.turn_on(lamp_id)
            elif on is False:
                self.switch.turn_off(lamp_id)
        except SwitchError as e:
            logger.error('Failed to set mode for lamp %d: ' + str(e))
            raise ExternalError('light switch error')


def _open_period(lamp, timestamp, brightness):
    WorkingPeriod.objects.create(lamp=lamp,
                                 brightness=lamp.brightness,
                                 start=timestamp)


def _close_period(lamp, timestamp):
    """Close current working period."""
    try:
        last_period = lamp.periods.latest('start')
        # TODO: check if active
        last_period.end = timestamp
        last_period.save()
    except WorkingPeriod.DoesNotExist:
        logger.warning('No period to close for lamp_id=%d', lamp.id)


lamp_service = LampService(Switch())
