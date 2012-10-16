from django import template
from django.conf import settings

register = template.Library()

class MediaUrlNode(template.Node):
    """Template node that renders the media_url tag."""
    def __init__(self, path_params):
        self.path_param_vars = map(lambda x: template.Variable(x), path_params)

    def render(self, context):
        final_path = ''.join(map(lambda x: x.resolve(context), self.path_param_vars))

        return '%s%s?v=%s' % (settings.STATIC_URL,
                            final_path,
                            settings.MEDIA_HASH)

@register.tag
def media_url(parser, token):
    """Tag for cache static resource urls. Usage is simply {% media 'css/base.css' %} or for any other similar static
    resource; js/images and such."""
    try:
        path_params = token.split_contents()[1:]
    except ValueError:
        raise template.TemplateSyntaxError, \
            "%r tag requires exactly at least one argument" % token.contents.split()[0]
    return MediaUrlNode(path_params)
