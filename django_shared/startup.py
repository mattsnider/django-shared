"""
If you want to use DS_AUTO_LOAD and DS_AUTO_DISCOVER, you need to call
startup from two places ``manage.py`` and ``wsgi.py``, or ``urls.py`` if
you are not using a ``wsgi.py``. To call, add the following line:

from django_shared.startup import run; run()

It already contains code to prevent double loading.

Additionally, you will need to include two new settings properties to make
use of the startup system: ``DS_AUTO_LOAD`` and ``DS_AUTO_DISCOVER``. They
should both be tuples or lists. The ``DS_AUTO_LOAD`` are modules that need
to be imported on starup, such as listeners. The ``DS_AUTO_DISCOVER`` are
modules that have an ``autodiscover`` function, like ``django.contrib.admin``.
Here are examples:

DS_AUTO_LOAD = ('listeners',)
DS_AUTO_DISCOVER = ('django_simple_social', 'django.contrib.admin',)
"""
from django.conf import settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule

do_load = True


def auto_load(submodules):
    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        for submodule in submodules:
            try:
                import_module("{0}.{1}".format(app, submodule))
            except:
                if module_has_submodule(mod, submodule):
                    raise


def run():
    global do_load

    if do_load:
        items_to_auto_load = getattr(settings, 'DS_AUTO_LOAD', None)

        if items_to_auto_load:
            auto_load(items_to_auto_load)

        items_to_auto_discover = getattr(settings, 'DS_AUTO_DISCOVER', None)

        if items_to_auto_discover:
            for item in items_to_auto_discover:
                try:
                    mod = import_module(item)
                    mod.autodiscover()
                except Exception as e:
                    print e
        do_load = False
