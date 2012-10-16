from optparse import make_option
from os import path, system

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    """
    Run sass against all files SCSS files specified as `SASS_TO_CSS` in your settings.
        See SaSS documentation for more details http://sass-lang.com/docs/yardoc/file.SASS_REFERENCE.html
    """
    help = 'Run sass against all files SCSS files specified as `SASS_TO_CSS` in your settings.'

    option_list = BaseCommand.option_list + (
        make_option('-s', '--style', action='store', dest='style', default='compressed',
            choices = ('nested', 'expanded', 'compact', 'compressed'),
            help='SaSS style options'
        ),
        make_option('--file_ext', action='store', dest='file_ext', default='scss',
            choices = ('scss', 'sass'),
            help='The file extension to use, .scss or .sass',
        ),
    )

    def handle(self, *args, **options):
        """
        Combines all SaSS files in the SASS_TO_CSS list:
            Expects files to be in {APP_NAME}/static/scss/{FILE_NAME}.scss
            You can specify on file per app or an list of files per app
            You can the name of the outputted CSS by specifying an optional third argument to your tuple
            If a list is specified for the SCSS files, and you want to rename the file,
                then a list of the same length must be specified for CSS names
            The list should be a tuple:
                [
                    ('app_name', 'file_name'), # single file
                    ('app_name', ['file_name1', 'file_name2', ...]), # collection of files
                    ('app_name', 'file_name', 'css_file_name'), # single file, renaming the CSS file
                    ('app_name', ['file_name1', 'file_name2', ...], ['css_file_name1', 'css_file_name2', ...]), # collection of files, renaming the CSS files
                ]
        """
        if not getattr(settings, 'SASS_TO_CSS'):
            raise CommandError('settings value SASS_TO_CSS is required')

        root_dir = path.join(path.dirname(path.realpath(__file__)),
            '..', '..', '..')

        cmd = 'sass --update %%s:%%s --style %s --trace' % options.get('style')
        file_ext = options.get('file_ext')

        self.stdout.write('Starting sass_to_css\n')
        for app_name, file_or_files in settings.SASS_TO_CSS:
            self.stdout.write('Processing %s:\n' % app_name)

            for filename in [file_or_files] if isinstance(file_or_files, (str, unicode,)) else file_or_files:
                # read data from file
                from_file = path.join(root_dir, app_name, 'static/scss',
                    '%s.%s' % (filename, file_ext))

                # write data to file
                to_file = path.join(root_dir, app_name, 'static/css',
                    '%s.css' % filename)

                # sassify
                system(cmd % (from_file, to_file,))

                self.stdout.write('Process %s to %s:\n' % (from_file, to_file,))
        self.stdout.write('Completed sass_to_css!\n')
