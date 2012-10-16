from logging import getLogger
from re import compile, IGNORECASE

from django.core.validators import RegexValidator
from django.forms.fields import RegexField
from django.forms.widgets import Input
from django.utils.translation import ugettext_lazy as _

email_proxy_re = compile(
    r'^((?!@proxymail\.facebook\.com).)*$', IGNORECASE)  # domain

logger = getLogger('contrib.form.fields')

validate_proxy_email = RegexValidator(email_proxy_re, _(u'Enter a valid e-mail address.'), 'invalid')


class HTML5RegexField(RegexField):
    def __init__(
        self, regex, regex_str=None, *args, **kwargs):
        """
        regex can be either a string or a compiled regular expression object.
        error_message is an optional error message to use, if
        'Enter a valid value' is too generic for you. To get client-side
        validation, the regex must be a string, or if it is compiled,
        provide the string representation as regex_str.
        """
        if isinstance(regex, basestring):
            self._orig_regex = regex
        elif regex_str:
            self._orig_regex = regex_str
        else:
            self._orig_regex = None
            logger.warn('No regex string provided to HTML5RegexField, '
                        'client-side validation will not be enabled')
        super(HTML5RegexField, self).__init__(regex, *args, **kwargs)

    def widget_attrs(self, widget):
        attrs = super(HTML5RegexField, self).widget_attrs(widget)
        # set the pattern attribute, if _orig_regex is a string
        if self._orig_regex is not None and isinstance(widget, Input):
            attrs.update({'pattern': str(self._orig_regex)})
        return attrs
