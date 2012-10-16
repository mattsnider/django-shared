import StringIO

def read_file_chunks(f):
    """
    Read the file chunks into a StringIO.
    """
    uploaded_image_buffer  = StringIO.StringIO()

    # read all file chunks to support larger files
    for chunk in f.chunks():
        uploaded_image_buffer.write(chunk)
    uploaded_image_buffer.seek(0)  # point back to beginning of buffer for read

    return uploaded_image_buffer