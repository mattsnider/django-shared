import re

from classytags.arguments import Argument
from classytags.core import Options, Tag
from django import template
from django.conf import settings
from django.utils.encoding import smart_unicode, smart_str
from django.utils.timesince import timesince

register = template.Library()
defer_html_queue = []


class AsyncScript(Tag):
    name = "async_script"

    options = Options(
        Argument("path"),
        Argument("appendStatic", default=True, required=False),
    )

    def render_tag(self, context, **kwargs):
        """
        Renders HTML to include a JavaScript file asynchronously.
        The content of the file is downloaded immediately, but it isn't
        processed until the UI thread is idle.
        """
        path = kwargs["path"]

        if kwargs["appendStatic"]:
            path = "%s%s" % (settings.STATIC_URL, path)

        return ("<script>(function(d) {"
                "var el = d.createElement('script'),"
                "elScript = d.getElementsByTagName('script')[0];"
                "el.type = 'text/javascript';"
                "el.async = true;"
                "el.src = '%s';"
                "elScript.parentNode.insertBefore(el, elScript);" +
                "}(document));</script>") % path
register.tag(AsyncScript)


class DeferHTML(Tag):
    name = "defer_html"

    options = Options(
        blocks=[('end_defer_html', 'nodelist')]
    )

    def render_tag(self, context, **kwargs):
        """
        Any HTML inside this tag will be queued and rendered at the
        end of the document. This is particularly useful for JavaScript tags.
        The HTML stored here will need to be rendered by call
        RenderDeferredHTML. This is done automatically in base.html.
        """
        global defer_html_queue
        defer_html_queue.append(
            "".join([o.render(context) for o in kwargs.get('nodelist')]))
        return ""
register.tag(DeferHTML)


def improved_timesince(date):
    """
    Returns the django timesince, but with better handling for times
    that happened less than a minute ago.
    """
    t = timesince(date)

    if '0' == t[0:1]:
        return 'just now'
    else:
        return '%s ago' % t

register.filter('improved_timesince', improved_timesince)


class IndexNode(template.Node):

    def __init__(self, var_list, var_index, var_name):
        self.var_list = var_list
        self.var_index = var_index
        self.var_name = var_name or (u'%s_%s' % (
            self.var_list, self.var_index)).replace('.', '_')

    def render(self, context):
        index = template.Variable(self.var_index).resolve(context)
        list = template.Variable(self.var_list).resolve(context)

        try:
            value = list[index]
        except IndexError:
            value = None

        context[self.var_name] = value
        return u""


def index(parser, token):
    """
    Creates a template variable from the element in the list at the index.
    The created variable name will be <var_list>_<var_index>. If the name
    has dots ('.') in it, the will be replaced with underscore.
    Optionally, a third argument may be passed, which will be used as the
    name of the new argument, instead of the default.
    Will set the new variable to None, if the index doesn't exist.
    {% index <var_list> <var_index> %}
    """
    parts = token.split_contents()
    if len(parts) < 3:
        raise template.TemplateSyntaxError(
            "'set' tag must be of the form: "
            "{% index <var_list> <var_index> %}")
    try:
        varname = parts[3]
    except IndexError:
        varname = ''
    return IndexNode(parts[1], parts[2], varname)
register.tag('index', index)


class LinelessNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return re.sub('\s+', ' ', self.nodelist.render(context).strip('\n'))


def lineless(parser, token):
    """
    Removes newline characters
    """
    nodelist = parser.parse(('endlineless',))
    parser.delete_first_token()
    return LinelessNode(nodelist)
lineless = register.tag(lineless)


@register.simple_tag
def regex(regex, replace, value):
    """
    Use re.sub from templates.
    """
    return smart_unicode(
        re.sub(regex, replace, smart_str(value), flags=re.UNICODE)
    )


class RenderDeferredHTML(Tag):
    name = "render_deferred_html"

    def render_tag(self, context, **kwargs):
        """
        Render all HTML that has been deferred by DeferHTML.
        """
        global defer_html_queue
        tmp = "".join(defer_html_queue)
        defer_html_queue = []
        return tmp
register.tag(RenderDeferredHTML)


class SetVarNode(template.Node):

    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value

    def render(self, context):
        try:
            value = template.Variable(self.var_value).resolve(context)
        except template.VariableDoesNotExist:
            value = ""
        context[self.var_name] = value
        return u""


def set_var(parser, token):
    """
        {% set <var_name>  = <var_value> %}
    """
    parts = token.split_contents()
    if len(parts) < 4:
        raise template.TemplateSyntaxError("'set' tag must be of the form:  {% set <var_name>  = <var_value> %}")
    return SetVarNode(parts[1], parts[3])
register.tag('set', set_var)
