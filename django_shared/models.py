from datetime import datetime
from django.contrib.contenttypes.models import ContentType

from django.core import serializers
from django.db import models
from django.utils import simplejson


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
    SERIALIZATION_FORMATS = (SERIALIZATION_FORMAT_JSON, SERIALIZATION_FORMAT_XML,)

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

    def to_json(self):
        return {
            'create_ts': '%s' % self.create_ts,
            'modify_ts': '%s' % self.modify_ts,
        }

    def __unicode__(self):
        return u"%s" % self.id


class MyJSONEncoder(simplejson.JSONEncoder):
    """JSON encoder which understands datetimes."""

    def default(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))


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
            u'%s' % simplejson.dumps(
                data, cls=MyJSONEncoder, encoding='UTF-8'))

    def get_data(self):
        return simplejson.loads(super(ModelJsonBase, self).get_data())

    data = property(get_data, set_data)

    class Meta:
        abstract = True

    def pretty_data(self):
        return simplejson.dumps(self.data, indent=4)
