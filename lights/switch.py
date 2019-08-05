"""Light switch interface.

This module provides an interface for controlling imaginary light
sources. Let's assume it uses some sort of hardware controller.
"""


import logging


logger = logging.getLogger(__name__)


class SwitchError(Exception):
    pass


class Switch:
    """Light switch for multiple lamps.

    This interface is synchronous. Methods apply changes immediately or
    raise exception.
    """

    def turn_on(self, lamp_id):
        logger.info('Turned on lamp %d', lamp_id)

    def turn_off(self, lamp_id):
        logger.info('Turned off lamp %d', lamp_id)

    def set_brightness(self, *, lamp_id, brightness):
        logger.info('Set brightness to %d%% for lamp %d',
                    brightness, lamp_id)
