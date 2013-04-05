from optparse import make_option

from django.conf import settings
from django.core.cache import get_cache
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils.cache import get_cache_key


class Command(BaseCommand):
    """
    Removes a cached URL from the cache.
    """
    args = '<viewname reverse_arg_1 ...>'
    help = 'Removes a cached URL from the cache.'

    option_list = BaseCommand.option_list + (
        make_option('-u', '--url', dest='url',
            help='The relative URL, instead of viewname'),
        )

    def handle(self, *args, **options):
        """

        """
        url = options.get('url')

        if not url:
            url = reverse(args[0], args=args[1:])

        class TempRequest(object):
            META = {}

            def get_full_path(self):
                return url

        cache_key = get_cache_key(TempRequest(), '', 'GET')

        if cache_key:
            cache = get_cache(settings.CACHE_MIDDLEWARE_ALIAS)
            cache.delete(cache_key)
            self.stdout.write('Purging %s!\n' % url)
        else:
            self.stderr.write('Could not find cache for %s!\n' % url)
