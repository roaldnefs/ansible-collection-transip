# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text


class Response(object):

    def __init__(self, resp, info):
        self.body = None
        if resp:
            self.body = resp.read()
        self.info = info

    @property
    def json(self):
        if not self.body:
            return None
        try:
            return json.loads(to_text(self.body))
        except ValueError:
            return None

    @property
    def status_code(self):
        return self.info["status"]

    @property
    def debug(self):
        return to_text(self.info)


class TransIPHelper(object):

    def __init__(self, module):
        self.module = module
        self.baseurl = "https://api.transip.nl/v6"
        self.timeout = module.params.get("timeout")
        self.access_token = module.params.get("access_token")
        self.test_mode = module.params.get("test_mode")
        self.headers = {"Authorization": f"Bearer {self.access_token}",
                        "Content-type": "application/json"}

        # Call the simple test resource on the TransIP API to make sure
        # everything is working
        response = self.get("api-test")
        if response.status_code == 401:
            self.module.fail_json(
                msg="Failed to login using API token, please verify validity of the API token.")

    @staticmethod
    def transip_argument_spec():
        return dict(
            access_token=dict(
                no_log=True,
                required=False,
                aliases=["api_token"]
            ),
            test_mode=dict(type='bool', default=False, aliases=[
                           'dry_run', 'dryrun', 'test-modus']),
            timeout=dict(type='int', default=30),
        )

    def send(self, method, path, data=None):
        url = f"{self.baseurl}/{path}"
        data = self.module.jsonify(data)

        if (self.test_mode):
            url = f"{url}?test=1"

        resp, info = fetch_url(
            self.module,
            url,
            data=data,
            headers=self.headers,
            method=method,
            timeout=self.timeout
        )

        return Response(resp, info)

    def get(self, path, data=None):
        return self.send("GET", path, data)

    def post(self, path, data=None):
        return self.send("POST", path, data)

    def put(self, path, data=None):
        return self.send("PUT", path, data)

    def patch(self, path, data=None):
        return self.send("PATCH", path, data)

    def delete(self, path, data=None):
        return self.send("DELETE", path, data)
