#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: transip_vps_os
short_description: Re-install the operating system
description:
- Re-install the operating system of a VPS in TransIP.
author: "Johan Kuijt (@yo-han)"
options:
  name:
    description:
    - The name of the VPS
    type: str
  operating_system:
    description:
    - The name of the operating system to install, e.g. ubuntu-18.04.
    type: str
  username:
    description:
    - Username used for the first user account on the VPS.
    type: str
  ssh_key:
    description:
    - Public ssh key to use for account creating during installation
    type: str
extends_documentation_fragment:
- yo_han.transip.transip.documentation
'''

EXAMPLES = r'''
---
- name: Install new OS
  yo_han.transip.transip_vps_os:
    name: "vps-123"
    operating_system: "ubuntu-22.04"
    username: "john"
    ssh_key: "ssh-rsa ..."
    access_token: "secret-token"
  register: vps
'''

RETURN = r'''
data:
  description: Re-install the operating system of a VPS in TransIP.
  returned: changed
  type: dict
  sample: [
    {
        "changed": true,
        "failed": false
    }
  ]
'''

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.yo_han.transip.plugins.module_utils.transip import TransIPHelper


class TransIPVPSOSException(Exception):
    pass


class TransIPVPSOS(object):

    def __init__(self, module):
        self.module = module
        self.rest = TransIPHelper(module)

    def install(self):

        path = "vps/" + self.module.params["name"] + "/operating-systems"

        # Set the required request attributes
        data = {
            "operatingSystemName": self.module.params["operating_system"],
            "username": self.module.params.get("username"),
            "sshKeys": [self.module.params.get("ssh_key")],
        }

        response = self.rest.post(path, data=data)

        if response.status_code == 201:

            self.module.exit_json(changed=True)
        else:
            json_data = response.json

            error_msg = "Failed to re-install VPS OS"
            if json_data and "error" in json_data:
                error_msg = json_data["error"]
            self.module.fail_json(changed=False, msg=error_msg)


def handle_request(module):
    vps = TransIPVPSOS(module)

    vps.install()


def main():
    argument_spec = TransIPHelper.transip_argument_spec()
    argument_spec.update(
        name=dict(type="str"),
        operating_system=dict(type="str"),
        ssh_key=dict(type="str", no_log=True),
        username=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        handle_request(module)
    except TransIPVPSOSException as exc:
        module.fail_json(msg=str(exc), exception=traceback.format_exc())
    except KeyError as exc:
        module.fail_json(msg='Unable to load {0}'.format(
            str(exc)), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
