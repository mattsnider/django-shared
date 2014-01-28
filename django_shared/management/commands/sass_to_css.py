from optparse import make_option
import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.importlib import import_module


class Command(BaseCommand):
    """
    Run Sass against all files. It will search the static directory of each
    app from Sass files and copy them into CSS files in a 'css' directory
    at the same level, so if Sass files are located at:

    /static/%(app_name)s/scss/

    Then the CSS files will be created at:

    /static/%(app_name)s/css/

    For more details on SASS see:
        http://sass-lang.com/docs/yardoc/file.SASS_REFERENCE.html
    """
    help = 'Run Sass against all related files.'

    DEFAULT_SASS_PATHS = (
        os.path.join('%(mod_path)s', 'static', '%(file_ext)s'),
        os.path.join('%(mod_path)s', 'static', '%(app_name)s', '%(file_ext)s'))

    option_list = BaseCommand.option_list + (
        make_option('-s', '--style', action='store', dest='style',
            default='compressed',
            choices = ('nested', 'expanded', 'compact', 'compressed'),
            help='SaSS style options'),
        make_option('--file_ext', action='store', dest='file_ext',
            default='scss',
            choices = ('scss', 'sass'),
            help='The file extension to use, .scss or .sass'),
        make_option('-a', '--app', action='store', dest='app', default='',
            help='The app to sassify. Default is all apps.'),
        make_option('--site-packages', action='store_true',
            dest='site-packages', default=False,
            help='Look for sass files in site-packages as well as active '
                 'project (not recommended, packages should ship with compiled '
                 'CSS and using this option has been known to cause CSS '
                 'discrepancies).'),
        )

    def _get_base_dir(self):
        """
        Fetches the BASE_DIR. Also looks for the ROOT_DIR, as that is the
        deprecated settings variable that has been replaced.
        """
        base_dir = (getattr(settings, 'BASE_DIR', None) or
                    getattr(settings, 'ROOT_DIR', None))

        if not base_dir:
            raise CommandError(
                'Your project must settings.py file must define a BASE_DIR,'
                'try: BASE_DIR = os.path.dirname(os.path.dirname(__file__))')
        return base_dir

    def handle(self, *args, **options):
        """
        Searches each app for static/(scss|sass)/filename.(scss|sass) files
        and executes Sass against them.
        """
        self.stdout.write('Starting sass_to_css\n')
        self.run_sass(options)
        self.stdout.write('Completed sass_to_css!\n')

    def _find_sass_files(self, app_path, file_ext):
        """
        Searches the app for sass files and returns the list of them.
        """
        sass_files = []

        # find all the matching SaSS files (default extension is .scss)
        for root, dirs, files in os.walk(os.path.join(
                app_path, settings.STATIC_ROOT)):
            for file in files:
                if file.endswith(file_ext):
                    sass_files.append(os.path.join(root, file))
        return sass_files

    def run_sass(self, options):
        """
        Iterate through the apps and process the sass files.
        """
        base_dir = self._get_base_dir()

        cmd = 'sass --update %%s:%%s --style %s --trace' % options.get('style')
        include_site_packages = options.get('site-packages')
        file_ext = '.%s' % options['file_ext']
        app = options['app']

        for app_name in settings.INSTALLED_APPS:
            # do all apps, or just the one specified
            if not app or app == app_name:
                # get the path of the app
                mod = import_module(app_name)
                app_path = mod.__path__[0]

                # only search site-packages apps if the option is true
                if not (include_site_packages or base_dir in app_path):
                    self.stdout.write('Invalid - Ignoring %s:\n' % app_name)

                sass_files = self._find_sass_files(app_path, file_ext)

                # did not find any sass files, skip this app
                if not sass_files:
                    self.stdout.write('No SaSS - Skipping app: %s\n' % app_name)
                    continue

                try:
                    self.stdout.write('Processing %s:\n' % app_name)

                    # iterate over the sass files and process them.
                    for from_file in sass_files:
                        # replacing extension and last directory name
                        t = os.path.split(from_file)
                        l = [None, 'css', None]
                        l[2] = t[1].replace(file_ext, '.css')
                        l[0] = os.path.split(t[0])[0]

                        # write data to file
                        to_file = os.path.join(*l)

                        # sassify
                        os.system(cmd % (from_file, to_file,))

                        self.stdout.write('Process %s to %s:\n' % (
                            from_file, to_file,))
                except IOError:
                    pass
