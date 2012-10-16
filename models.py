from datetime import datetime
from django.contrib.contenttypes.models import ContentType

from django.core import serializers
from django.db import models

class ModelBase(models.Model):
    create_ts = models.DateTimeField(default=datetime.now)
    modify_ts = models.DateTimeField(default=datetime.now)

    SERIALIZATION_FORMAT_JSON = 'json'
    SERIALIZATION_FORMAT_XML = 'xml'
    SERIALIZATION_FORMATS = (SERIALIZATION_FORMAT_JSON, SERIALIZATION_FORMAT_XML,)

    class Meta:
        abstract = True

    def content_type(self):
        """
        Helper function to quickly get the content type for any instance.
        """
        return ContentType.objects.get_for_model(self)

    def reload(self):
        """
        Gets the latest instance from the DB. Be careful, this returns a
        new instance, instead of updating the current one.
        """
        return self.__class__.objects.get(pk=self.pk)

    def save(self, *args, **kwargs):
        """Handle some special conditions, such as `update_ts`"""
        self.modify_ts = datetime.now()
        super(ModelBase, self).save(*args, **kwargs)

    def serialize(self, format='json'):
        return serializers.serialize(format, [self])
