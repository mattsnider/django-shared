from optparse import make_option
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.importlib import import_module


class Command(BaseCommand):
    """
    Run Sass against all files. By default it will search in /static/scss/,
    but it can also look into /static/sass/. For more details see:
        http://sass-lang.com/docs/yardoc/file.SASS_REFERENCE.html
    """
    help = 'Run Sass against all related files.'

    option_list = BaseCommand.option_list + (
        make_option('-s', '--style', action='store', dest='style', default='compressed',
            choices = ('nested', 'expanded', 'compact', 'compressed'),
            help='SaSS style options'),
        make_option('--file_ext', action='store', dest='file_ext', default='scss',
            choices = ('scss', 'sass'),
            help='The file extension to use, .scss or .sass'),
        make_option('-a', '--app', action='store', dest='app', default='',
            help='The app to sassify. Default is all apps.'),
        make_option('--site-packages', action='store_true', dest='site-packages', default=False,
            help='Look for sass files in site-packages as well as active project '
                 '(not recommended, packages should ship with compiled CSS and using this '
                 'option has been known to cause CSS discrepancies).'),
        )

    def handle(self, *args, **options):
        """
        Searches each app for static/(scss|sass)/filename.(scss|sass) files
        and executes Sass against them.
        """
        cmd = 'sass --update %%s:%%s --style %s --trace' % options.get('style')
        include_site_packages = options.get('site-packages')
        file_ext = options['file_ext']
        app = options['app']
        root_dir = getattr(settings, 'ROOT_DIR', None)

        if not root_dir:
            raise CommandError('Your project must settings.py file must define a ROOT_DIR, try\n'
                               'ROOT_DIR = path.abspath(path.dirname(__file__))')

        self.stdout.write('Starting sass_to_css\n')
        for app_name in settings.INSTALLED_APPS:
            if not app or app == app_name:
                mod = import_module(app_name)

                try:
                    # test if the scss directory exists
                    sass_path = os.path.join(
                        mod.__path__[0], 'static', file_ext)

                    if not (include_site_packages or root_dir in sass_path):
                        self.stdout.write('Ignoring %s:\n' % app_name)
                        continue

                    self.stdout.write('Processing %s:\n' % app_name)

                    for dirpath, dirnames, filenames in os.walk(sass_path):
                        for filename in filenames:
                            if '.%s' % file_ext not in filename:
                                continue
                                # read data from file
                            from_file = os.path.join(dirpath, filename)

                            # write data to file
                            to_file = os.path.join(
                                dirpath.replace(file_ext, 'css'),
                                filename.replace(file_ext, 'css'))

                            # sassify
                            os.system(cmd % (from_file, to_file,))

                            self.stdout.write('Process %s to %s:\n' % (
                                from_file, to_file,))
                except IOError:
                    pass
        self.stdout.write('Completed sass_to_css!\n')
