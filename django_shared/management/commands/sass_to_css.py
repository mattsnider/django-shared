from optparse import make_option
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.importlib import import_module


class Command(BaseCommand):
    """
    Run Sass against all files. By default it will search in /static/scss/ and
    /static/%(app_name)s/scss/, but it can also look into /static/sass/ and
    /static/%(app_name)s/sass/.

    For more details on SASS see:
        http://sass-lang.com/docs/yardoc/file.SASS_REFERENCE.html

    You can set a custom SASS_TO_CSS_PATH in your settings files that will
    determine where the application will look for your sass files. The
    command will attempt to replace string variables:

        '%(mod_path)s' - the module root directory
        '%(app_name)s' - the application name
        '%(file_ext)s' - the file extension (scss or sass)

        The two default sass_path strings are:
        os.path.join('%(mod_path)s', 'static', '%(file_ext)s')
        os.path.join('%(mod_path)s', 'static', '%(app_name)s', '%(file_ext)s')

        If you define SASS_TO_CSS_PATH, then this command will only search
        in that directory and will not check the default two paths.
    """
    help = 'Run Sass against all related files.'

    DEFAULT_SASS_PATHS = (
        os.path.join('%(mod_path)s', 'static', '%(file_ext)s'),
        os.path.join('%(mod_path)s', 'static', '%(app_name)s', '%(file_ext)s'))

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
        root_dir = getattr(settings, 'ROOT_DIR', None)

        if not root_dir:
            raise CommandError(
                'Your project must settings.py file must define a ROOT_DIR,'
                'try\nROOT_DIR = path.abspath(path.dirname(__file__))')

        self.stdout.write('Starting sass_to_css\n')
        self.run_sass(options)
        self.stdout.write('Completed sass_to_css!\n')

    def get_sass_path(self, sass_path, app_name, mod_path, file_ext):
        """
        Creates the sass_path and checks that the directory exists.
        """
        sass_path = sass_path % {
            'mod_path': mod_path,
            'app_name': app_name,
            'file_ext': file_ext,}

        return sass_path if os.path.exists(sass_path) else None

    def run_sass(self, options):
        """
        Iterate through the apps and process the sass files.
        """
        root_dir = getattr(settings, 'ROOT_DIR', None)
        settings_sass_path = getattr(settings, 'SASS_TO_CSS_PATH', None)

        cmd = 'sass --update %%s:%%s --style %s --trace' % options.get('style')
        include_site_packages = options.get('site-packages')
        file_ext = options['file_ext']
        app = options['app']

        for app_name in settings.INSTALLED_APPS:
            if not app or app == app_name:
                mod = import_module(app_name)
                mod_path = mod.__path__[0]
                real_app_name = app_name.split('.')[-1]

                if not (include_site_packages or root_dir in mod_path):
                    self.stdout.write('Invalid - Ignoring %s:\n' % app_name)

                if settings_sass_path:
                    sass_path = self.get_sass_path(
                        settings_sass_path, real_app_name, mod_path, file_ext)
                else:
                    for path in Command.DEFAULT_SASS_PATHS:
                        sass_path = self.get_sass_path(
                            path, real_app_name, mod_path, file_ext)

                        if sass_path:
                            break

                # did not find an available directory for sass, skip this app
                if not sass_path:
                    self.stdout.write('No SaSS - Skipping %s:\n' % app_name)
                    continue

                try:
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
