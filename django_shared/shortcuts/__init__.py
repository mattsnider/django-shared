from django.core.urlresolvers import reverse
from django_shared.form.forms import FormBase

__author__ = 'mattesnider'
import logging

from django.shortcuts import redirect
logger = logging.getLogger()

def redirect_with_form(request, view_name, form, url=u'%s',
                       reverse_args=None, reverse_kwargs=None):
    """
    Sets a form to the session and then returns the redirect response.
    """
    if hasattr(form, '__contains__'):
        request.session['form'] = [f.pickle_for_request() for f in form]
    else:
        request.session['form'] = form.pickle_for_request()

    if view_name:
        view_url = url % reverse(view_name, args=reverse_args,
            kwargs=reverse_kwargs)
    else:
        view_url = url
    return redirect(view_url)

def get_or_create_form(request, form_class, pop=True, args=(), kwargs=None):
    """
    Fetches the form from the request or creates a new one.
    """
    form_data = request.session.get('form')

    if form_data:
        if pop:
            del request.session['form']

        if isinstance(form_data, list):
            forms = []
            for form_tuple in form_data:
                if form_tuple[0] == form_class:
                    form = FormBase.unpickle_from_request(*form_tuple, form_args=args)
                    forms.append(form)
            return forms
        elif isinstance(form_data, tuple):
            form_tuple = form_data
            if form_tuple[0] == form_class:
                form = FormBase.unpickle_from_request(*form_tuple, form_args=args)
                return form
        else:
            raise ValueError('Invalid data stored in form session')

    return form_class(*args, **(kwargs or {}))