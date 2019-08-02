from rest_framework import serializers

from .models import Lamp


class LampSerializer(serializers.HyperlinkedModelSerializer):

    # Namespace has to be set manually
    url = serializers.HyperlinkedIdentityField(view_name="lights:lamp-detail")

    class Meta:
        model = Lamp
        # TODO: add id?
        fields = ['url', 'name', 'is_on', 'brightness']
        read_only_fields = ['name']
