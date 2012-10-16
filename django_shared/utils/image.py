import StringIO
from datetime import datetime
from random import randint
import Image
import os

from django.conf import settings
from django_shared.utils.file import read_file_chunks
from django_shared.utils.s3 import upload_to_s3


def scale_to(width, height, desired_width=0, desired_height=0):
    """
    Scaling function for system. Will either scale to the width
    or if desired_height is provided, will just return desired values.
    """
    if desired_width and desired_height:
        return desired_width, desired_height
    ratio = desired_width * 1. / width
    return int(width * ratio), int(height * ratio)


def upload_image(file, filename, bucket, append_timestamp=False,
    scale_args=None, uploaded_image_buffer=None, do_not_overwrite=False):
    """
    Upload a file directly to S3, should skip saving locally.
    Returns the filename that was created.
    Prefetch the uploaded_image_buffer for performance gain, when resizing
        the same image several times.
    """
    # append a timestamp, so images don't overwrite each other
    if append_timestamp:
        filename = '%s-%s' % (
            filename, datetime.now().strftime("%Y%m%d%H%M%S%f"))

    # this is a cheat, just appending a random, but should be pretty good
    #   for preventing overwriting in one request
    if do_not_overwrite:
        filename += unicode(randint(0, 1000000))

    # update the filename, with the file type
    filename = '%s.%s' % (filename, file.name.split('.')[-1])
    if uploaded_image_buffer:
        uploaded_image_buffer.seek(0)
    else:
        uploaded_image_buffer = read_file_chunks(file)
    uploaded_image = Image.open(uploaded_image_buffer)

    if scale_args and any(scale_args):
        (width, height) = uploaded_image.size
        (width, height) = scale_to(
            width, height, *scale_args)

        resized_image = uploaded_image.resize((width, height))

        image_file = StringIO.StringIO()
        resized_image.save(image_file, 'JPEG')
    else:
        image_file = uploaded_image_buffer

    image_file.seek(0)  # just to make sure

    if getattr(settings, 'IS_DEV', False):
        with open(os.path.join(
            settings.MEDIA_ROOT, filename), 'wb+') as destination_file:
            destination_file.write(image_file.read())

    else:
        upload_to_s3(image_file, os.path.join(
            settings.MEDIA_URL, filename), bucket)

    return filename


def upload_image_and_resize(
    file, name_and_size_tuple, bucket, append_timestamp=False,
    do_not_overwrite=False):
    """
    Uploads multiple files efficiently.
    """
    uploaded_image_buffer = read_file_chunks(file)
    files = []

    for t in name_and_size_tuple:
        file_path = upload_image(file, t[0], bucket,
            append_timestamp=append_timestamp, scale_args=t[1:],
            uploaded_image_buffer=uploaded_image_buffer,
            do_not_overwrite=do_not_overwrite)
        files.append(file_path)

    return files
