#!/usr/bin/env python
import os, sys
from setuptools import setup, find_packages

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# README is required for distribution, but README.md is required for github,
#   so create README temporarily
os.system('cp %s/README.md %s/README.txt' % (ROOT_DIR, ROOT_DIR))

sdict = dict(
    name = 'django-shared',
    packages = find_packages(),
    version='.'.join(map(str, __import__('django_shared').__version__)),
    description = 'Common tools for working with Django and Python.',
    long_description=open('README.md').read(),
    url = 'https://github.com/mattsnider/django-shared',
    author = 'Matt Snider',
    author_email = 'admin@mattsnider.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'admin@mattsnider.com',
    keywords = ['python', 'django'],
    license = 'MIT',
    include_package_data=True,
    install_requires=[
        'django>=1.3',
        'django-classy-tags>=0.3.4',
    ],
    platforms=["any"],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)

from distutils.core import setup
setup(**sdict)

# cleanup README
os.remove('%s/README.txt' % ROOT_DIR)