import sys

from setuptools import setup, find_packages

setup(
    name = "Django-Pizza",
    version = '16.10.1',
    description = "Yet another Django CMS.",
    url = "https://github.com/pizzapanther/Django-Pizza",
    author = "Paul Bailey",
    author_email = "paul.m.bailey@gmail.com",
    license = "BSD",
    packages = [
      'pizza',
      'pizza.kitchen_sink',
      'pizza.kitchen_sink.migrations',
      'pizza.kitchen_sink.templatetags',
      'pizza.kitchen_sink.management',
      'pizza.kitchen_sink.management.commands',
      'pizza.blog',
      'pizza.blog.migrations',
      'pizza.blog.templatetags',
      'pizza.calendar',
      'pizza.calendar.migrations',
    ],
    include_package_data = True,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = [
      "sorl-thumbnail>=11.01",
      "Django-Next-Please>=13.12",
    ]
)
