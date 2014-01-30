#!/usr/bin/env python

from gzip import GzipFile
import mimetypes
from optparse import make_option
import os
import re
from StringIO import StringIO
import time
from datetime import datetime, timedelta

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME

# set a far futures expire header (1 year is enough)
_expire_datetime = datetime.now() + timedelta(days=365)
EXPIRES_HEADER = time.strftime("%a, %d %b %Y %H:%M:%S GMT", _expire_datetime.timetuple())
STALE_STATIC_ASSET_SECONDS = 12 * 60 * 60       # 12 hours

__CSS_URL_RE = re.compile('url\(([\./\w-]*)\)')


class Command(BaseCommand):
    """
    Uploads static files to S3.
    """
    help = 'Uploads static files to S3'

    option_list = BaseCommand.option_list + (
        make_option('-x', '--exclude', action='store', dest='exclude',
            default=None,
            help='A comma separated list of extensions to exclude '
                 '(eg. --exclude=scss,sass,txt)'),
    )

    def handle(self, *args, **options):
        """
        """
        self.CONN = S3Connection(
            settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

        base_dir = (getattr(settings, 'BASE_DIR', None) or
                    getattr(settings, 'ROOT_DIR', None))

        for file in self.listFiles(options.get('exclude')):
            filename = os.path.normpath(file)
            filekey = re.sub(base_dir + '/', '', filename)

            # don't send to S3 if not updated in the last 12 hours.
            stat = os.stat(filename)
            if time.time() - stat.st_mtime < STALE_STATIC_ASSET_SECONDS:
                self.file_to_s3(filekey, filename)

    def file_to_s3(self, filekey, filename):
        """
        Uploads a filename to s3 and checks if file on disk is newer or not.
        """
        k = Key(self.CONN.get_bucket(BUCKET_NAME))
        k.key = filekey

        if k.exists():
            k.open_read()
            last_modified_time_on_s3 = datetime.strptime(
                k.last_modified[5:], '%d %b %Y %H:%M:%S GMT')
            last_modified_time_on_disk = datetime.fromtimestamp(
                os.path.getmtime(filename))

            if last_modified_time_on_s3 > last_modified_time_on_disk:
                print 'Skipping %s' % filename
                return

        print "Uploading %s to bucket %s" % (filename, BUCKET_NAME)

        f = open(filename, 'rb')
        filedata = f.read()
        f.close()
        self.save_key_value(filekey, filedata, True)

    def listFiles(self, exclude):
        """
        Creates a list of all files in the STATIC_ROOT directory. The values in the
        list will be the absolute path.
        """
        excluded_extensions = exclude.split(',') if exclude else None
        all_files = []

        # walk the static root directory
        for root, dirs, files in os.walk(settings.STATIC_ROOT):
            # iterate over the files in each directory
            for file in files:
                # if there are no excluded extensions or if the extension is
                # not in the excluded list, then add it to the file list
                if (not excluded_extensions or os.path.splitext(file)[1][1:]
                    not in excluded_extensions):
                    all_files.append('%s/%s' % (root, file))

        return all_files

    def save_key_value(self, filename, filedata, gzip_flag = False):
        """key being filename and value is the data. Sets the headers based on content type and far futures expires headers"""
        headers = {}

        if gzip_flag:
            print 'Gziping %s' % filename
            filedata = self.gzip_media(filedata)
            headers.update({'Content-Encoding':'gzip'})

        content_type = mimetypes.guess_type(filename)[0]
        if not content_type:
            content_type = 'text/plain'

        print 'Sending %s to S3' % filename
        k = Key(self.CONN.get_bucket(BUCKET_NAME))
        k.key = filename
        headers.update({
            'Expires': EXPIRES_HEADER,
            'Content-Type': content_type,
            'Cache-Control': 'public, max-age=31536000',
            })
        k.set_contents_from_string(filedata, headers)
        k.set_acl('public-read')

    def gzip_media(self, filedata):
        """gzip encodes a given stream of data."""
        gzip_data = StringIO()
        gzf = GzipFile(fileobj=gzip_data, mode='wb')
        gzf.write(filedata)
        gzf.close()
        return gzip_data.getvalue()