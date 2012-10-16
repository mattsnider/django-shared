from pyexpat import ParserCreate, ExpatError

from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.core.cache import get_cache
from django.test import RequestFactory, TestCase
from django.utils.importlib import import_module
from django.utils.simplejson import loads

__all__ = ('DjangoSharedTestCase', )


class DjangoSharedTestCase(TestCase):
    """Things common to all test cases"""

    # Flags for mocking things that get mocked frequently.  Flags set to 'True'
    # are opt-out, flags set to 'False' are opt-in.  Individual tests can also
    # use the context managers directly in situations where they don't apply to
    # all tests in a class.

    def setUp(self):
        """Flush cache and redis, and run patchers."""
        super(DjangoSharedTestCase, self).setUp()

        self.reset_cache()
        self.reset_redis()
        self._user_counter = 1
        self.factory = RequestFactory()

        # Assemble the list of context managers we want to patch with.  This
        # list is assembled based on the class variable mocking flags.
        context_managers = []

        # Set a class variable so this can be used by both setUp() and
        # tearDown().  Use a tuple so subclasses can't manipulate the list.
        # (They should use the class variable flags to signal which context
        # managers this method should add.
        self.context_managers = tuple(context_managers)

        # Enable any requested mocking.
        for context_manager in self.context_managers:
            context_manager.__enter__()

    def tearDown(self):
        # Exit any context managers requested for mocking.  Do so in the
        # reverse order in case it matters.
        for context_manager in reversed(self.context_managers):
            context_manager.__exit__(None, None, None)
        super(DjangoSharedTestCase, self).tearDown()

    def create_client_session(self):
        """
        The test client doesn't always include an actual session. This helper
        ensures that a session really exists for the purpose of mutating and
        saving it directly.
        """
        if not isinstance(self.client.session, dict):
            return  # a session already exists

        session_engine = import_module(settings.SESSION_ENGINE)
        session = session_engine.SessionStore()
        session.save()
        session_cookie = settings.SESSION_COOKIE_NAME
        self.client.cookies[session_cookie] = session.session_key
        cookie_data = {
            'max-age': None,
            'path': '/',
            'domain': settings.SESSION_COOKIE_DOMAIN,
            'secure': settings.SESSION_COOKIE_SECURE or None,
            'expires': None,
        }
        self.client.cookies[session_cookie].update(cookie_data)

    def assert_anonymous(self, request=None):
        """
        A helper method which asserts that the client is not an
        authenticated user.
        """
        if not request:
            request = self.client
        self.assertFalse(BACKEND_SESSION_KEY in request.session)
        self.assertFalse(SESSION_KEY in request.session)

    def assert_login_required(self, url):
        """
        Logged out user redirects to login.
        """
        response = self.client.post(url)
        self.assertEquals(302, response.status_code)
        signin_url = '%s?next=%s' % (settings.LOGIN_URL, url)
        self.assertRedirects(response, signin_url)

    def assert_unicode_no_queries(self, manager=None, factory_class=None,
        instance=None):
        manager = manager or factory_class._associated_class._default_manager
        instance = instance or factory_class()
        for using in settings.DATABASES.keys():
            instance = manager.get(pk=instance.pk)
            self.assertNumQueries(0, lambda: unicode(instance), using=using)

    def assert_url_must_be_post(self, url):
        """
        A non-post requests get 404.
        """
        response = self.client.get(url)
        self.assertEquals(405, response.status_code)

    def assert_valid_json(self, response, success, data=None, errors=None):
        json = loads(response.content)
        expected_json = {'success': success, 'errors': errors or []}

        if data:
            expected_json['data'] = data

        self.assertEquals(expected_json, json)

    def assert_valid_xml(self, response):
        """
        Evaluates if the XML in the response is valid or not.
        """
        try:
            parser = ParserCreate()
            parser.Parse(response.content, True)
        except ExpatError:
            self.fail("Invalid XML being used")

    def _authenticate(self, auth_user, password='testpw'):
        """
        Authenticates the provided user.
        """
        auth_user.set_password(password)
        auth_user.save()

        if not self.client.login(
            username=auth_user.username, password=password):
            raise Exception('Failed to authenticate')

    def reset_cache(self):
        for alias in settings.CACHES.keys():
            cache = get_cache(alias)
            cache.clear()

    def reset_redis(self):
        from django_shared.redis import connections
        for alias in connections.redises.keys():
            redis = connections[alias]
            redis.flushdb()
