from django.conf.urls import patterns


urlpatterns = patterns('django_shared.views',
    (r'^404/$', 'page_not_found'),
    (r'^500/$', 'server_error'),
)