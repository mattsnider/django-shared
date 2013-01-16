from django.conf.urls import patterns, url


urlpatterns = patterns('django_shared.views',
    url(r'^maintenance/$', 'maintenance', name='maintenance'),
    url(r'^404/$', 'page_not_found', name='page_not_found'),
    url(r'^500/$', 'server_error', name='server_error'),
)