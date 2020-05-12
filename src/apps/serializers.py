from rest_framework import serializers
from rest_framework_api_key.models import APIKey

from apps.models import APPModel


class APPSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="appmodel-detail", lookup_field='appname', read_only=True)

    def create(self, validated_data):
        """
        Creating APPModel instance by appname and api_key \n
        :param validated_data: users data
        :return: APPModel instance or None
        """
        if 'appname' in validated_data:
            api_key = APIKey.objects.get(name=validated_data['api_key'])
            app = APPModel.objects.create(appname=validated_data['appname'], api_key=api_key)
            api_key.name = validated_data['appname']
            api_key.save()
            return app
        else:
            return None

    def update(self, instance, validated_data):
        """
        Updating APPModel instance
        :param instance: APPModel instance for update
        :param validated_data: users data
        :return: updated APPModel instance
        """
        if 'appname' in validated_data:
            instance.appname = validated_data.get('appname')
            instance.api_key.name = validated_data.get('appname', instance.appname)
            instance.api_key.save()
        if 'last_access' in validated_data:
            instance.last_access = validated_data.get('last_access', instance.last_access)
        if 'requests_count' in validated_data:
            instance.requests_count = validated_data.get('requests_count', instance.requests_count)
        instance.save()
        return instance

    class Meta:
        model = APPModel
        fields = ['url', 'appname', 'last_access', 'requests_count']
