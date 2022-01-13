#!/usr/bin/python
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.

"""Pythonic simple SOAP Client transport"""


import logging
import ssl
import sys


from urllib import request as urllib2
from http.cookiejar import CookieJar

log = logging.getLogger(__name__)

#
# We store metadata about what available transport mechanisms we have available.
#
_http_connectors = {}  # libname: classimpl mapping
_http_facilities = {}  # functionalitylabel: [sequence of libname] mapping


class TransportBase:
    @classmethod
    def supports_feature(cls, feature_name):
        return cls._wrapper_name in _http_facilities[feature_name]

#
# urllib2 support.
#


class urllib2Transport(TransportBase):
    _wrapper_version = "urllib2 %s" % urllib2.__version__
    _wrapper_name = 'urllib2'

    def __init__(self, timeout=None, proxy=None, cacert=None, sessions=False):
        if (timeout is not None) and not self.supports_feature('timeout'):
            raise RuntimeError('timeout is not supported with urllib2 transport')
        if proxy:
            raise RuntimeError('proxy is not supported with urllib2 transport')
        if cacert:
            raise RuntimeError('cacert is not support with urllib2 transport')

        handlers = []

        if ((sys.version_info[0] == 2 and sys.version_info >= (2, 7, 9)) or (sys.version_info[0] == 3 and sys.version_info >= (3, 2, 0))):
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            handlers.append(urllib2.HTTPSHandler(context=context))

        if sessions:
            handlers.append(urllib2.HTTPCookieProcessor(CookieJar()))

        opener = urllib2.build_opener(*handlers)
        self.request_opener = opener.open
        self._timeout = timeout

    def request(self, url, method="GET", body=None, headers={}):
        req = urllib2.Request(url, body, headers)
        try:
            f = self.request_opener(req, timeout=self._timeout)
            return f.info(), f.read()
        except urllib2.HTTPError as f:
            if f.code != 500:
                raise
            return f.info(), f.read()


_http_connectors['urllib2'] = urllib2Transport
_http_facilities.setdefault('sessions', []).append('urllib2')

if sys.version_info >= (2, 6):
    _http_facilities.setdefault('timeout', []).append('urllib2')


class DummyTransport:
    """Testing class to load a xml response"""

    def __init__(self, xml_response):
        self.xml_response = xml_response

    def request(self, location, method, body, headers):
        log.debug("%s %s", method, location)
        log.debug(headers)
        log.debug(body)
        return {}, self.xml_response


def get_http_wrapper(library=None, features=[]):
    # If we are asked for a specific library, return it.
    if library is not None:
        try:
            return _http_connectors[library]
        except KeyError:
            raise RuntimeError('%s transport is not available' % (library,))

    # If we haven't been asked for a specific feature either, then just return our favourite
    # implementation.
    if not features:
        return _http_connectors.get('httplib2', _http_connectors['urllib2'])

    # If we are asked for a connector which supports the given features, then we will
    # try that.
    current_candidates = _http_connectors.keys()
    new_candidates = []
    for feature in features:
        for candidate in current_candidates:
            if candidate in _http_facilities.get(feature, []):
                new_candidates.append(candidate)
        current_candidates = new_candidates
        new_candidates = []

    # Return the first candidate in the list.
    try:
        candidate_name = current_candidates[0]
    except IndexError:
        raise RuntimeError("no transport available which supports these features: %s" % (features,))
    else:
        return _http_connectors[candidate_name]


def set_http_wrapper(library=None, features=[]):
    """Set a suitable HTTP connection wrapper."""
    global Http
    Http = get_http_wrapper(library, features)
    return Http


def get_Http():
    """Return current transport class"""
    global Http
    return Http


# define the default HTTP connection class (it can be changed at runtime!):
set_http_wrapper()
