This package is a collection of tools, templates, and more that I find useful in most of my Django projects. If you find them useful, feel free to include it in your projects as well.

The template 'django_shared/base.html' is intended to be extended by all templates in your app. It uses the html5boilerplate project (http://http://html5boilerplate.com/) and automatically sets up HTML 5 support using modernizr. In addition, jQuery is available by default and some basic CSS.

Installation
============

Code is found at::

> https://github.com/mattsnider/django-shared

The easiest way to install is using pip::

> pip install git+https://github.com/mattsnider/django-shared.git#egg=django_shared

You can also install by downloading the source file and running::

> python setup.py install

Requirements
============

I have tried to keep requirements to a minimum. Obviously, Django (>=1.3) is required, and I like to use class-based template tags, so django-classy-tags (>=0.3.4) is also required. If you use pip to install, then these dependencies will be taken care of automatically.

This library has been tested on python >2.6.

Roadmap
=======

Here is a list of a few things I will be working on over the next couple months:

* Test coverage
* Improvements to management command sass_to_css
* Upgrading boilerplate
* SaSS/CSS review

Issues
======

https://github.com/mattsnider/django-shared/issues

Licensing
=========

Apache 2.0; see LICENSE file