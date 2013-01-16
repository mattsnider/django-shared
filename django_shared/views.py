from django.conf import settings
from django.contrib import messages
from django.shortcuts import render


def page_not_found(request, template_name='django_shared/404.html'):
    """Handle the page_not_found view"""
    messages.get_messages(request)
    return render(request, template_name, {
        'settings': settings,
    }, status=404)


def server_error(request, template_name='django_shared/500.html'):
    """Handle the server_error view"""
    messages.get_messages(request)
    return render(request, template_name, {
        'settings': settings,
    }, status=500)