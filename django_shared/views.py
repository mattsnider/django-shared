from django.conf import settings
from django.contrib import messages
from django.shortcuts import render


def maintenance(request):
    """Handle the maintenance view"""
    messages.get_messages(request)
    template_name = getattr(
        settings, 'DS_MAINTENANCE_TEMPLATE', 'django_shared/maintenance.html')
    return render(request, template_name, {
        'settings': settings,
    })


def page_not_found(request):
    """Handle the page_not_found view"""
    messages.get_messages(request)
    template_name = getattr(
        settings, 'DS_404_TEMPLATE', 'django_shared/404.html')
    return render(request, template_name, {
        'settings': settings,
    }, status=404)


def server_error(request):
    """Handle the server_error view"""
    messages.get_messages(request)
    template_name = getattr(
        settings, 'DS_500_TEMPLATE', 'django_shared/500.html')
    return render(request, template_name, {
        'settings': settings,
    }, status=500)