#!/usr/bin/env python

from setuptools import setup

from pysimplesoap import __version__, __author__, __author_email__, __license__

setup(
    name='PySimpleSOAP',
    version=__version__,
    description='Python simple and lightweight SOAP Library',
    author=__author__,
    author_email=__author_email__,
    url='https://github.com/pysimplesoap/pysimplesoap',
    packages=['pysimplesoap'],
    license=__license__,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
