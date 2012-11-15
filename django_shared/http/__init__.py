from StringIO import StringIO
import gzip
import httplib
import string
import urllib
import urllib2
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils import simplejson


def dict_lower(d):
    return dict(zip(map(string.lower, d.keys()), map(
        string.lower, d.values())))


class JsonResponse(HttpResponse):
    """
    Encapsulates a JSON response, to keep code DRY.
    """
    def __init__(self, data=None, errors=None, success=True):
        """
        data is a map, errors a list
        """
        if not data:
            data = {}
        json = json_response(data=data, errors=errors, success=success)
        super(JsonResponse, self).__init__(json, mimetype='application/json')


def json_response(data=None, errors=None, success=True):
    data.update({
        'errors': errors,
        'success': not errors and success,
    })
    return simplejson.dumps(data)


def _gzip_open(handler, req, cls):
    """
    Adapted from: https://derrickpetzold.com/index.php/python-gzip-http/
    """
    req.add_header('Accept-Encoding', 'gzip')
    r = handler.do_open(cls, req)
    headers = dict_lower(r.headers)
    if 'content-encoding' in headers and headers['content-encoding'] == 'gzip':
        fp = gzip.GzipFile(fileobj=StringIO(r.read()))
    else:
        fp = r
    resp = urllib.addinfourl(fp, r.headers, r.url, r.code)
    resp.msg = r.msg
    return resp


class GzipHttpHandler(urllib2.HTTPHandler):
    def http_open(self, req):
        return _gzip_open(self, req, httplib.HTTPConnection)


class GzipHttpsHandler(urllib2.HTTPSHandler):
    def https_open(self, req):
        return _gzip_open(self, req, httplib.HTTPSConnection)


def gzip_urlopen(url, data=None, timeout=30):
    """
    Extend urllib2.urlopen() to support gzip encoding.
    """
    request = urllib2.Request(url)
    opener = urllib2.build_opener(GzipHttpHandler, GzipHttpsHandler)
    return opener.open(request, data, timeout)
