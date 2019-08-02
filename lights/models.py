from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models


class Lamp(models.Model):

    name = models.CharField(max_length=80, unique=True)
    is_on = models.BooleanField(default=False)
    # brightness %. 0% is not allowed.
    brightness = models.SmallIntegerField(
        'brightness %',
        default=100,
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)])

    def __str__(self):
        return self.name
