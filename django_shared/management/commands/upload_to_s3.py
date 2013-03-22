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
#        make_option('-c', '--compress', action='store_true', dest='compress', default=False,
#            help='Compression can be turned on via your settings, or set to True by this option'),
        )

    def handle(self, *args, **options):
        self.CONN = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        files = self.listFiles(settings.STATIC_ROOT)

        for filename in files:
            filename = os.path.normpath(filename)
            if filename == '.' or not os.path.isfile(filename):
                continue

            # don't send to S3 if not updated in the last 12 hours.
            stat = os.stat(filename)
            if time.time() - stat.st_mtime < STALE_STATIC_ASSET_SECONDS:
                self.file_to_s3(filename)

    def file_to_s3(self, filename):
        """
        Uploads a filename to s3, making sure it really is a file etc. Also checks if file on disk is newer or not.
        YUI files must be manually uploaded
        """
        if filename == '.' or not os.path.isfile(filename) or '/yui/' in filename:
            return # Skip this, because it's not a file.

        k = Key(self.CONN.get_bucket(BUCKET_NAME))
        k.key = '/static%s' % filename
        if k.exists():
            k.open_read()
            last_modified_time_on_s3 = datetime.strptime(k.last_modified[5:], '%d %b %Y %H:%M:%S GMT')
            last_modified_time_on_disk = datetime.fromtimestamp(os.path.getmtime(filename))

            if last_modified_time_on_s3 > last_modified_time_on_disk:
                print 'Skipping %s' % filename
                return

        print "Uploading %s to bucket %s" % (filename, BUCKET_NAME)

        f = open(filename, 'rb')
        filedata = f.read()
        f.close()
        self.save_key_value(filename, filedata, True)

    def listFiles(self, dir):
        basedir = dir
        files = []
        subdirlist = []

        for item in os.listdir(dir):
            item = os.path.join(basedir, item)

            if os.path.isfile(item):
                files.append(item)
            else:
                subdirlist.append(item)

        for subdir in subdirlist:
            files.extend(self.listFiles(subdir))

        return files

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