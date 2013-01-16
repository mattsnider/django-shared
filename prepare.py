"""
This is a helper command to ensure that everything is compiled.
"""
import os

dir = os.path.abspath(os.path.dirname(__file__))

sass_cmd = 'sass --update %(path)s/django_shared/static/scss:%(path)s/django_shared/static/css --style compressed --trace'
print sass_cmd % {'path': dir}
os.system(sass_cmd % {'path': dir})