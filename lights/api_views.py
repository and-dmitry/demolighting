from rest_framework import mixins, viewsets
from rest_framework.response import Response

from . import services
from .models import Lamp
from .serializers import LampSerializer


class LampViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Viewset for Lamp.

    Creating and deleting resources is not allowed through this
    API. That's why this class inherits specific mixins instead of
    ModelViewSet.

    PUT is not necessary for this API - creation is handled by POST
    and replacement is not allowed. Partial update is handled by
    PATCH, like it supposed to be.
    """
    queryset = Lamp.objects.all().order_by('id')
    serializer_class = LampSerializer

    def partial_update(self, request, pk=None):
        # TODO: avoid getting instance from db here? Service does this
        # again in transaction.
        instance = self.get_object()
        request_serializer = self.get_serializer(instance,
                                                 data=request.data,
                                                 partial=True)
        request_serializer.is_valid(raise_exception=True)
        instance = services.lamp_service.set_lamp_mode(
            instance.pk,
            on=request_serializer.validated_data.get('is_on'),
            brightness=request_serializer.validated_data.get('brightness'))
        response_serializer = self.get_serializer(instance)
        return Response(response_serializer.data)
