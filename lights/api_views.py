from rest_framework import mixins, viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from .models import Lamp
from .serializers import LampSerializer
from .services import lamp_service, ExternalError


class ServiceUnavailableError(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class LampViewSet(mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """Viewset for Lamp.

    Creating and deleting resources is not allowed.

    PUT is not necessary for this API - creation is handled by POST
    and replacement is not allowed. Partial update is handled by
    PATCH, like it supposed to be.
    """
    queryset = Lamp.objects.all().order_by('id')
    serializer_class = LampSerializer

    def partial_update(self, request, pk=None):
        lamp = self.get_object()
        request_serializer = self.get_serializer(lamp,
                                                 data=request.data,
                                                 partial=True)
        request_serializer.is_valid(raise_exception=True)

        try:
            lamp_service.set_lamp_mode(
                lamp,
                on=request_serializer.validated_data.get('is_on'),
                brightness=request_serializer.validated_data.get('brightness'))
        except ExternalError:
            raise ServiceUnavailableError(
                detail='Failed to switch the lamp, try again later')

        response_serializer = self.get_serializer(lamp)
        return Response(response_serializer.data)
