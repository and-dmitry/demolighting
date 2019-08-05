from datetime import timedelta

from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import ExpressionWrapper, F, Sum
from django.utils import timezone


class Lamp(models.Model):

    name = models.CharField(max_length=80, unique=True)
    is_on = models.BooleanField(default=False)
    # Time of last switch on/off. Change of brightness is not
    # considered a switch.
    last_switch = models.DateTimeField(null=True, blank=True)
    # brightness %. 0% is not allowed.
    brightness = models.SmallIntegerField(
        'brightness %',
        default=100,
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)])

    def __str__(self):
        return self.name

    @property
    def total_working_time(self):
        # Calcute total duration of closed periods for this lamp.
        result = (
            self.periods
            .filter(end__isnull=False)
            .annotate(period_length=ExpressionWrapper(
                F('end') - F('start'),
                output_field=models.DurationField()))
            .aggregate(total=Sum('period_length'))
        )
        # TODO: this can be cached
        total = result['total'] or timedelta(0)

        # Add duration of active period. Simple "where end not null
        # order by start desc" wouldn't work - there may be some
        # abandoned periods in the table (see WorkingPeriod
        # docstring). This can be done with a query but I doubt it
        # would be faster because of subquery.
        try:
            # TODO: add only('start')?
            last_period = self.periods.latest('start')
        except WorkingPeriod.DoesNotExist:
            pass
        else:
            if not last_period.end:
                total += last_period.duration
        return total


class WorkingPeriod(models.Model):
    """Working period of a lamp.

    An instance of this model represents a period when a lamp was on
    with a certain level of brightness.

    Types of periods for a lamp:

    - Closed period - end is not null
    - Open period - end is null
    - Last period - period with maximum start (open or closed)
    - Active period - last period if it's open, else none
    - Abandoned period - open period but not last (so not active)
    """

    lamp = models.ForeignKey(Lamp,
                             on_delete=models.CASCADE,
                             related_name='periods',
                             related_query_name='period')
    brightness = models.SmallIntegerField(
        'brightness %',
        validators=[MinValueValidator(1),
                    MaxValueValidator(100)])
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.lamp.name} ({self.start:%Y:%m:%d %H:%M:%S})'

    @property
    def duration(self):
        end = self.end or timezone.now()
        return end - self.start

    # TODO: add is_open() ?
