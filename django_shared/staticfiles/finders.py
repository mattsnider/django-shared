import warnings

from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class RootDirectoryFinder(BaseFinder):
    """
    A static files finder that looks in STATIC_ROOT. Will serve files
    in STATIC_ROOT. Should only be used when Django is running in debug mode.

    Because of a hack used for the ``list`` method, this finder must come
    after the built-in AppDirectoriesFinder in STATICFILES_FINDERS.
    """
    storage_class = FileSystemStorage

    def __init__(self, *args, **kwargs):
        # The list of apps that are handled
        super(RootDirectoryFinder, self).__init__(*args, **kwargs)
        self.storage = self.storage_class(location=settings.STATIC_ROOT)

    def list(self, ignore_patterns):
        """
        List is used by several internal Django apps, most notably
        the collectstatic command in the staticfiles app. We
        only want this finder to return a the contents of STATIC_ROOT
        when called by staticfiles_urlpatterns, and not list the files in
        STATIC_ROOT for collectstatic and other similar features.

        Since ``list`` has to return a file and a storage class instance
        (otherwise it errors), we have to hack it to work correctly.
        We accomplish this by having a special static file that will
        already be included by the ``list`` of AppDirectoriesFinder.
        This is the only way I could make it do nothing.
        """
        yield u'forRootDirectoryFinder.txt', self.storage

    def find(self, path, all=False):
        """
        Looks for files in the app directories.
        """
        if not settings.DEBUG:
            warnings.warn(
                'RootDirectoryFinder should only be run in debug mode.',
                RuntimeWarning
            )

        if self.storage.exists(path):
            matched_path = self.storage.path(path)
            if matched_path:
                return matched_path
        return None
