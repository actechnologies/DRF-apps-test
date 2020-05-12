from uuid import uuid4
from django.db import models
from rest_framework_api_key.models import APIKey

# Create your models here.


class APPModel(models.Model):
    """
    Simple APP model
    """
    id = models.UUIDField(default=uuid4,
                          editable=False,
                          primary_key=True,
                          help_text='UUID primary key')
    appname = models.CharField(max_length=64,
                               unique=True,
                               help_text='App name')
    api_key = models.OneToOneField(APIKey,
                                   on_delete=models.CASCADE,
                                   help_text='App API key')
    last_access = models.DateTimeField(null=True,
                                       help_text='Datetime of last api request by app')
    requests_count = models.IntegerField(default=0,
                                         help_text='Requests count for app')

    def __str__(self):
        return self.appname
