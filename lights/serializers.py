from rest_framework import serializers

from .models import Lamp


class LampSerializer(serializers.HyperlinkedModelSerializer):

    # Namespace has to be set manually
    url = serializers.HyperlinkedIdentityField(view_name="lights:lamp-detail")
    total_working_time = serializers.DurationField(read_only=True)

    class Meta:
        model = Lamp
        # TODO: add id?
        fields = [
            'url',
            'name',
            'is_on',
            'brightness',
            'last_switch',
            'total_working_time',
        ]
        read_only_fields = ['name', 'last_switch']
