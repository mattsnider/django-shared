from django.http import HttpResponseBadRequest


def ajax_only(view_func):
    """
    Decorator for requests that are only supposed to handle AJAX requests.
    """
    def inner(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return view_func(request, *args, **kwargs)
    return inner
