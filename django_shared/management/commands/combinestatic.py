from optparse import make_option
from compressor.filters.yui import YUICSSFilter, YUIJSFilter

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    """
    Combines static files like CSS and JS as specified in the STATIC_FILE_COMBINATIONS setting.
    """
    help = 'Combines static files like CSS and JS as specified in the STATIC_FILE_COMBINATIONS setting'

    option_list = BaseCommand.option_list + (
        make_option('-c', '--compress', action='store_true', dest='compress', default=False,
            help='Compression can be turned on via your settings, or set to True by this option'),
    )

    def handle(self, *args, **options):
        """
        Combines all JS files in the STATIC_FILE_COMBINATIONS dict:
            The dict should be:
                {
                    'path/output_file_name1.js', ['path/file1_to_compress.js', 'path/file2_to_compress.js', ],
                    'path/output_file_name2.js', ['path/file3_to_compress.js', 'path/file4_to_compress.js', ],
                    'path/output_file_name3.css', ['path/file5_to_compress.css', 'path/file6_to_compress.css', ],
                }
        """

        if not getattr(settings, 'STATIC_FILE_COMBINATIONS'):
            raise CommandError('settings value STATIC_FILE_COMBINATIONS is required')

        self.stdout.write('Starting concatenation:\n')
        for output_file, files_or_dict in settings.STATIC_FILE_COMBINATIONS.items():
            self.stdout.write('Compressing %s:\n' % output_file)
            do_compression = options.get('compress') or False

            if isinstance(files_or_dict, dict):
                files = files_or_dict.get('files') or []
                do_compression = files_or_dict.get('compress') or False
            else:
                files = files_or_dict

            file_count = self._create_concatenated_file(files, output_file, do_compression)
            self.stdout.write('Concatenated %d files into %s:\n' % (file_count, output_file))
        self.stdout.write('Concatenation Completed!\n')

    def _create_concatenated_file(self, sources, output, do_compression=False):
        """
        Reads files, concatenates them, and writes them out. Returns the number of concatenated files.
        """
        inferred_file_type = output.split('.')[1]

        # read in all the files
        data_for_file = []
        for file_name in sources:
            f = open(file_name, 'rb')
            data_for_file.append(f.read())
            f.close()

        # create a concatenated file
        f = open(output, 'w')
        filedata = "".join(data_for_file)
        f.write(filedata)

        # compress the concatenated file
        if do_compression:
            if 'js' == inferred_file_type:
                compressed_filedata = YUIJSFilter(content=filedata).output()
            elif 'css' == inferred_file_type:
                compressed_filedata = YUICSSFilter(content=filedata).output()
            else:
                raise CommandError('Unsupported filetype; %s' % inferred_file_type)
            f = open(output.replace('.%s' % inferred_file_type, '-min.%s' % inferred_file_type), 'w')
            f.write(compressed_filedata)

        return len(data_for_file)
