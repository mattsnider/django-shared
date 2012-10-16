#!/usr/bin/env python

import os
import sys
import codecs

from setuptools import setup, Command, find_packages

src_dir = "django_kissmetrics"


class RunTests(Command):
    description = "Run the django test suite from the tests dir."
    user_options = []
    extra_env = {}
    extra_args = []

    def run(self):
        for env_name, env_value in self.extra_env.items():
            os.environ[env_name] = str(env_value)

        this_dir = os.getcwd()
        testproj_dir = os.path.join(this_dir, "tests")
        os.chdir(testproj_dir)
        sys.path.append(testproj_dir)
        from django.core.management import execute_manager
        os.environ["DJANGO_SETTINGS_MODULE"] = os.environ.get(
            "DJANGO_SETTINGS_MODULE", "settings")
        settings_file = os.environ["DJANGO_SETTINGS_MODULE"]
        settings_mod = __import__(settings_file, {}, {}, [''])
        prev_argv = list(sys.argv)
        try:
            sys.argv = [__file__, "test"] + self.extra_args
            execute_manager(settings_mod, argv=sys.argv)
        finally:
            sys.argv = prev_argv

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


class QuickRunTests(RunTests):
    extra_env = dict(SKIP_RLIMITS=1, QUICKTEST=1)


if os.path.exists("README.md"):
    long_description = codecs.open("README.md", "r", "utf-8").read()
else:
    long_description = "See https://github.com/mattesnider/django-shared"

setup(
    name = 'django-shared',
    packages=find_packages(),
    version='.'.join(map(str, __import__('django_shared').__version__)),
    description = 'Common tools for working with Django and Python.',
    long_description = long_description,
    url = 'http://github.com/votizen/django-shared',
    author = 'Matt Snider',
    author_email = 'admin@mattsnider.com',
    maintainer = 'Matt Snider',
    maintainer_email = 'admin@mattsnider.com',
    keywords = ['python', 'django'],
    license = 'MIT',
    cmdclass={
        "test": RunTests,
        "quicktest": QuickRunTests
    },
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
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
      ]
)