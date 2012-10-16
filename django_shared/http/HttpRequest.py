from django.http import Http404

from contrib.form.forms import FormFormat

def get_mime_type(sFormat):
    """Returns the appropriate format for the response"""
    if 'xml' == sFormat:
        return 'application/xml'
    elif 'xml' == sFormat:
        return 'application/json'
    else:
        return 'text/plain'

def get_request_format(request):
    """Determines the request format from the `format` parameter"""
    if 'GET' == request.method:
        form = FormFormat(request.GET)
        if form.is_valid():
            return form.cleaned_data.get('format')

    raise Http404