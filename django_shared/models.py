from datetime import datetime
import json

from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.db import models


def keyify(content_type_pk, pk):
    """
    Creates a key from class name and primary key
    """
    return '%s:%s' % (content_type_pk, pk)


def keyify_obj(o):
    """
    Creates a key from class name and primary key
    """
    return keyify(o.content_type.pk, o.pk)


class memoized_property(object):
    """
    A read-only @property that is only evaluated once.

    From: http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result


class ModelBase(models.Model):
    """
    An abstract model to be the foundation for all other models. Adds
    helper functions and automatically tracks record creation and modify times.
    """
    create_ts = models.DateTimeField(default=datetime.now)
    modify_ts = models.DateTimeField(default=datetime.now)

    SERIALIZATION_FORMAT_JSON = 'json'
    SERIALIZATION_FORMAT_XML = 'xml'
    SERIALIZATION_FORMATS = (
        SERIALIZATION_FORMAT_JSON, SERIALIZATION_FORMAT_XML,)

    class Meta:
        abstract = True

    @property
    def content_type(self):
        """
        Helper function to quickly get the content type for any instance.
        """
        return ContentType.objects.get_for_model(self)

    def keyify(self):
        """
        Creates a key from class name and primary key
        """
        return keyify_obj(self)

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

    def to_json(self, exclude=None, include=None, manytomany=False):
        """
        Returns a JSON representation of this model.
        This may not be the best way to do this, and could potentially
        have security issues with passwords and stuff, so use with care.
        """
        field_names = include or self._meta.get_all_field_names()
        # filter the list of fields names to only the include set
        if exclude:
            field_names = set(field_names).difference(exclude)

        ret = {}

        for field_name in field_names:
            val = getattr(self, field_name, None)

            # get the ManyToMany relationships as well
            if manytomany and 'ManyRelatedManager' in str(val.__class__):
                l = []

                for o in getattr(self, field_name).all():
                    l.append(o.to_json(exclude=exclude, include=include))

                if len(l):
                    ret[field_name] = l
            # only return non-None values
            elif val is not None:
                ret[field_name] = unicode(val)

        return ret

    def __unicode__(self):
        return u"%s" % self.id


class ModelDataBase(ModelBase):
    """
    This is the model to extend for storing blobs of data.
    """
    _data = models.TextField(db_column='data', blank=True)

    def set_data(self, data):
        self._data = data
        self._cached_data = data

    def get_data(self):
        cached_data = getattr(self, '_cached_data', None)

        if not cached_data:
            cached_data = self._data
            self._cached_data = cached_data
        return cached_data

    data = property(get_data, set_data)

    class Meta:
        abstract = True


class ModelJsonBase(ModelDataBase):
    """
    The raw source that is used to encode JSON objects.
    """
    def set_data(self, data):
        super(ModelJsonBase, self).set_data(
            u'%s' % json.dumps(
                data, cls=DateTimeAwareJSONEncoder, encoding='UTF-8'))

    def get_data(self):
        return json.loads(super(ModelJsonBase, self).get_data())

    data = property(get_data, set_data)

    class Meta:
        abstract = True

    def pretty_data(self):
        return json.dumps(self.data, indent=4)
