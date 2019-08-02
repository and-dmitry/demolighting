from rest_framework import mixins, viewsets

from .models import Lamp
from .serializers import LampSerializer


class LampViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Viewset for Lamp.

    Creating and deleting resources is not allowed through this
    API. That's why this class inherits specific mixins instead of
    ModelViewSet.

    PUT is not actually necessary for this API - creation is handled
    by POST and replacement is not allowed. But PUT works just like
    PATCH for model viewsets and serializers. Let's follow the
    robustness principle and be liberal in what we accept. Same goes
    for DRF silently ignoring read-only fields instead of returning
    error.

    """
    queryset = Lamp.objects.all().order_by('id')
    serializer_class = LampSerializer
