from django.http import HttpResponse
from django.utils import simplejson

class JsonResponse(HttpResponse):
    """
    Encapsulates a JSON response, to keep code DRY.
    """
    def __init__(self, data=None, errors=[ ], success=True):
        """
        data is a map, errors a list
        """
        if not data:
            data = {}
        json = json_response(data=data, errors=errors, success=success)
        super(JsonResponse, self).__init__(json, mimetype='application/json')

def json_response(data={ }, errors=[ ], success=True):
    data.update({
        'errors': errors,
        'success': bool(len(errors) == 0 and success),
        })
    return simplejson.dumps(data)