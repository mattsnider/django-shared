from django import forms
from validators import validate_format

class FormMixin(object):

    def as_dl(self):
        """
        Returns this form rendered as HTML <p>s.
        """
        return self._html_output(
            normal_row = u'<dt%(html_class_attr)s>%(label)s%(help_text)s</dt><dd%(html_class_attr)s>%(field)s%(errors)s</dd>',
            error_row = u'<dd>%s</dd>',
            row_ender = '</dd>',
            help_text_html = u' <div class="helptext">%s</div>',
            errors_on_separate_row = False)

    def pickle_for_request(self):
        """
        Returns a pickleable version of the form.
        """
        return self.__class__, self.data

    @staticmethod
    def unpickle_from_request(form_class, data, form_args=()):
        """
        Returns an instance of the form with initial data form the pickled tuple.
        """
        form = form_class(*form_args, data=data)
        form.is_valid()
        return form

class FormBase(forms.Form, FormMixin):
    """
        The base form for this project. Fixes the following:
            -makes ids unique, by using the form name as well as the field name
    """
    def __init__(self, *args, **kwargs):
        if not kwargs.get('auto_id', ''):
            kwargs['auto_id'] = 'id_%s%s' % (self.__class__.__name__,'_%s')

        super(FormBase, self).__init__(*args, **kwargs)

    def _save(self, *args, **kwargs):
        raise NotImplementedError('_save should be overwritten by subclass')

    def validate_and_save(self, *args, **kwargs):
        is_valid = self.is_valid()
        if is_valid:
            self._save(self.cleaned_data, *args, **kwargs)
        return is_valid

class FormFormat(forms.Form):
    format = forms.CharField(max_length=4, validators=[validate_format])