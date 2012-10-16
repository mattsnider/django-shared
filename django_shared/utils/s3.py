import mimetypes

from boto import connect_s3
from boto.s3.key import Key
from django.conf import settings


def upload_to_s3(file, filename, bucket):
    """
    Upload a file directly to S3, should skip saving locally.
    Returns the filename that was created.
    Prefetch the uploaded_image_buffer for performance gain, when resizing
        the same image several times.
    """
    conn = connect_s3(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.create_bucket(bucket)

    k = Key(bucket)
    k.key = filename
    k.content_type = mimetypes.guess_type(filename)[0]
    k.set_contents_from_string(file.read())
    k.set_acl('public-read')
