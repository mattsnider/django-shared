__author__ = 'mattesnider'

from django.conf import settings
from django.core import signals

from django_shared.redis.utils import ConnectionHandler

connections = ConnectionHandler(settings.REDISES)

# Register an event that closes the redis connection
# when a Django request is finished.
def close_connection(**kwargs):
    connections.close_all()
signals.request_finished.connect(close_connection)

