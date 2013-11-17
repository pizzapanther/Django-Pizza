import sys

from setuptools import setup, find_packages

setup(
    name = "Django-Pizza",
    version = '13.11.6',
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
      'pizza.blog',
      'pizza.blog.migrations',
      'pizza.blog.templatetags',
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
      "sorl-thumbnail>=11.01"
    ]
)
