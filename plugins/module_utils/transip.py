#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.urls import fetch_url


class TransIPHelper(object):
    def __init__(self, module):
        self.module = module
        self.baseurl = "https://api.transip.nl/v6/"
        self.timeout = module.params.get("timeout", 30)
        self.oauth_token = module.params.get('oauth_token')
        self.headers = {'Authorization': 'Bearer {0}'.format(self.oauth_token),
                        'Content-type': 'application/json'}

    @staticmethod
    def transip_argument_spec():
        return dict()

    def send(self, method, path, data=None):
        url = "{}/{}".format(self.baseurl, path)
        data = self.module.jsonify(data)

        response, infomation = fetch_url(self.module, url, data=data,headers=self.headers, method=method, timeout=self.timeout)
