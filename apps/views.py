import datetime
from uuid import uuid4

from rest_framework import status
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework_api_key.models import APIKey
from rest_framework_api_key.permissions import HasAPIKey

from apps.models import APPModel
from apps.serializers import APPSerializer

# Create your views here.


class APPViewSet(mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):

    queryset = APPModel.objects.all()
    serializer_class = APPSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'appname'

    def create(self, request, *args, **kwargs):
        """
        Creating APP by 'appname', generating API key for app \n
        :param request: user request obj
        :return: 'rest_framework.respons.Response' with 201/400 HTTP code as result of creating app
        """
        api_key, key = APIKey.objects.create_key(name=str(uuid4()))
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(api_key=api_key.name)
            return Response({**serializer.data, 'api_key': key}, status=status.HTTP_201_CREATED)
        else:
            api_key.delete()
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Deleting object by DELETE request
        :param request: user request obj
        :return: 'rest_framework.respons.Response' with 202 HTTP code
        """
        app = self.get_object()
        app.api_key.delete()
        app.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'], detail=True)
    def new_key(self, request, appname=None):
        """
        Update API key for APP instance with deleting previous
        :param request: user request obj
        :param appname: APP name for renewing api key
        :return: 'rest_framework.respons.Response' with 200 HTTP code
        """
        app = APPModel.objects.get(appname=appname)
        app.api_key.delete()
        api_key, key = APIKey.objects.create_key(name=appname)
        app.api_key = api_key
        app.save()
        return Response({'api_key': key}, status=status.HTTP_200_OK)


class APPRetrieveAPIView(RetrieveAPIView):
    """
    Simple api view for check API keys
    """
    serializer_class = APPSerializer
    queryset = None
    permission_classes = [HasAPIKey]

    def get(self, request, *args, **kwargs):
        """
        Get app info by API key checker
        :param request: user request obj
        :return: 'rest_framework.respons.Response' with 200/403 HTTP code
        """
        if "HTTP_AUTHORIZATION" in request.META:
            key = request.META["HTTP_AUTHORIZATION"].replace('Api-Key ', '')
            api_key = APIKey.objects.get_from_key(key)
            app = APPModel.objects.get(api_key=api_key)
            app.requests_count += 1
            app.last_access = datetime.datetime.now(datetime.timezone.utc)
            app.save()
            return Response({**APPSerializer(app, context={'request': request}).data}, status=status.HTTP_200_OK)
        else:
            return Response(data={'detail': 'API key missing'}, status=status.HTTP_403_FORBIDDEN)
