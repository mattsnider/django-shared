from django.forms.widgets import Input, TextInput, ClearableFileInput, \
    CheckboxInput, DateInput, MultiWidget
from django.utils.encoding import force_unicode
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy

class EmailInput(Input):
    input_type = 'email'


class ClearableImageInput(ClearableFileInput):

    clear_checkbox_label = ugettext_lazy('remove image')
    input_text = ugettext_lazy('or change')
    template_with_initial = u'<div class="clearable">%(initial)s <br/> %(clear_template)s <br/> <strong>%(input_text)s:</strong> %(input)s</div>'
    template_with_clear = u'%(clear)s <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label>'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            }
        template = u'%(input)s'
        substitutions['input'] = super(ClearableFileInput, self).render(
            name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = (u'<a href="%s">%s</a>'
                                        % (escape(value.url),
                                           force_unicode(value)))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(
                    checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(
                    checkbox_id)
                substitutions['clear'] = CheckboxInput().render(
                    checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = (
                    self.template_with_clear % substitutions)

        return mark_safe(template % substitutions)


def as_email(self, attrs=None, **kwargs):
    """
    Returns a string of HTML for representing this as an <input type="email">.
    """
    return self.as_widget(EmailInput(), attrs, **kwargs)


def as_disabled(self, attrs=None, **kwargs):
    """
    Returns a string of HTML for representing this as an
    <input type="text" disabled="disabled">.
    """
    if not attrs:
        attrs = {
            'disabled': 'disabled'
        }

    elif not hasattr(attrs, 'disabled'):
        attrs['disabled'] = 'disabled'

    return self.as_widget(TextInput(), attrs, **kwargs)


class YearInput(DateInput):
    ignore_values = (1900,)

    def __init__(self, attrs=None):
        super(YearInput, self).__init__(format='%Y', attrs=attrs)

    def _format_value(self, value):
        value = super(YearInput, self)._format_value(value)
        if value in self.ignore_values:
            return ''
        return value


class MonthInput(DateInput):
    def __init__(self, attrs=None):
        super(MonthInput, self).__init__(format='%m', attrs=attrs)


class DayInput(DateInput):
    def __init__(self, attrs=None):
        super(DayInput, self).__init__(format='%d', attrs=attrs)


class SplitMDYDateWidget(MultiWidget):
    """
    Multi-widget for splitting dates into three fields.
    """
    def __init__(self, attrs=None):
        widgets = (
            MonthInput(attrs=attrs),
            DayInput(attrs=attrs),
            YearInput(attrs=attrs),
            )
        super(SplitMDYDateWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.month, value.day, value.year
        return None, None, None

    def format_output(self, rendered_widgets):
        return '<span class="slash">/</span>'.join(rendered_widgets)
