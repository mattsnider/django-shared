from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _

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


class UserEmailCreationForm(FormBase):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_email': _("A user with that email already exists."),
    }
    email = forms.EmailField(label=_("Email"), max_length=255)
    password = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)

    def clean_email(self):
        # Since User.email is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])

    def save(self):
        cd = self.cleaned_data
        return User.objects.create_user(
            cd['email'].split('@')[0],
            email=cd['email'],
            password=cd["password"],
        )


class EmailAuthenticationForm(AuthenticationForm, FormMixin):
    """
    Base class for authenticating users by email. Extend this to get a
    form that accepts email/password logins.
    """
    email = forms.EmailField(label=_("Email"), max_length=255)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': _("Please enter a correct email and password. "
                           "Note that both fields are case-sensitive."),
        'no_cookies': _("Your Web browser doesn't appear to have cookies "
                        "enabled. Cookies are required for logging in."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
        del self.fields['username']

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'])
            elif not self.user_cache.is_active:
                raise forms.ValidationError(self.error_messages['inactive'])
        self.check_for_test_cookie()
        return self.cleaned_data


class FormFormat(forms.Form):
    format = forms.CharField(max_length=4, validators=[validate_format])
