#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: transip_sshkey
short_description: Manage TransIP SSH keys
description:
- Manage TransIP SSH keys.
author: "Roald Nefs (@roaldnefs)"
options:
  state:
    description:
    - Indicate desired state of the target.
    default: present
    choices: ['present', 'absent']
    type: str
  description:
    description:
    - The SSH key description.
    type: str
  fingerprint:
    description:
    - The MD5 fingerprint of the SSH key.
    type: str
  ssh_pub_key:
    description:
    - The SSH key.
    type: str
extends_documentation_fragment:
- yo_han.transip.transip.documentation
'''

EXAMPLES = r'''
- name: Create a new SSH key
  yo_han.transip.transip_sshkey:
    state: present
    ssh_pub_key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDf2pxWX/yhUBDyk2LPhvRtI0LnVO8PyR5Zt6AHrnhtLGqK+8YG9EMlWbCCWrASR+Q1hFQG example
    description: example
  register: result

- debug:
    msg: "Added SSH-key with fingerprint {{ result.data.sshKey.fingerprint }}"

- name: Delete a SSH key
  yo_han.transip.transip_sshkey:
    state: absent
    ssh_pub_key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDf2pxWX/yhUBDyk2LPhvRtI0LnVO8PyR5Zt6AHrnhtLGqK+8YG9EMlWbCCWrASR+Q1hFQG example
'''

RETURN = r'''
data:
  description: a TransIP SSH key
  returned: changed
  type: dict
  sample: {
    "sshKey": {
        "creationDate": "2020-12-27 15:24:59",
        "description": "example",
        "fingerprint": "79:07:8c:7c:6c:00:b1:e9:44:4a:bf:e4:1a:fa:88:0d",
        "id": 10163,
        "key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDf2pxWX/yhUBDyk2LPhvRtI0LnVO8PyR5Zt6AHrnhtLGqK+8YG9EMlWbCCWrASR+Q1hFQG example"
    }
  }
'''

from __future__ import absolute_import, division, print_function
from ansible_collections.yo_han.transip.plugins.module_utils.transip import TransIPHelper
from ansible.module_utils.basic import AnsibleModule
import traceback


class TransIPSSHKeyException(Exception):
    pass


class TransIPSSHKey(object):
    def __init__(self, module):
        self.module = module
        self.rest = TransIPHelper(module)

    def list(self):
        """Returns a list of all SSH-keys."""
        path = "ssh-keys"
        response = self.rest.get(path)

        if response.status_code == 200:
            return response.json.get("sshKeys", [])

        return []

    def get(self):
        """Get information of a specific SSH-key."""
        fingerprint = self.module.params.get("fingerprint")
        ssh_pub_key = self.module.params.get("ssh_pub_key")

        for ssh_key in self.list():
            if fingerprint:
                if fingerprint == ssh_key["fingerprint"]:
                    return {"sshKey": ssh_key}
            else:
                if ssh_pub_key == ssh_key["key"]:
                    return {"sshKey": ssh_key}
        return None

    def create(self):
        """Create a new SSH-key if it doesn't exists yet."""
        json_data = self.get()
        if json_data:
            self.module.exit_json(changed=False)
        if self.module.check_mode:
            self.module.exit_json(changed=True)

        path = "ssh-keys"

        # Set the required request attributes
        data = {
            "sshKey": self.module.params.get("ssh_pub_key"),
            "description": self.module.params.get("description")
        }

        response = self.rest.post(path, data=data)

        if response.status_code == 201:
            # Retrieve data about the newly created SSH-key, as the TransIP API
            # doesn't provide any information on the creation of the SSH-key
            json_data = self.get()
            if json_data and "sshKey" in json_data:
                ssh_key_data = json_data
            else:
                # When using the demo access token, the API doesn't actually
                # create the SSH-key so the json_data might be empty
                ssh_key_data = {"sshKey": {}}
            self.module.exit_json(changed=True, data=ssh_key_data)
        else:
            json_data = response.json
            error_msg = "Failed to create SSH-key"
            if json_data and "error" in json_data:
                error_msg = json_data["error"]
            self.module.fail_json(change=False, msg=error_msg)

    def delete(self):
        """Delete an existing SSH-key."""
        json_data = self.get()
        if not json_data:
            self.module.exit_json(changed=False, msg="SSH-key not found")

        if self.module.check_mode:
            self.module.exit_json(changed=True)

        ssh_key_id = json_data["sshKey"]["id"]
        path = "sshKeys/{0}".format(ssh_key_id)

        response = self.rest.delete(path)

        if response.status_code == 204:
            self.module.exit_json(changed=True, msg="SSH-key deleted")
        else:
            self.module.fail_json(
                changed=False, msg="Failed to delete SSH-key")


def handle_request(module):
    sshkey = TransIPSSHKey(module)
    state = module.params["state"]
    if state == "present":
        sshkey.create()
    elif state == "absent":
        sshkey.delete()


def main():
    argument_spec = TransIPHelper.transip_argument_spec()
    argument_spec.update(
        state=dict(choices=["present", "absent"], default="present"),
        ssh_pub_key=dict(type="str"),
        description=dict(type="str"),
        fingerprint=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=(
            ("ssh_pub_key", "fingerprint"),
        ),
        required_if=(
            ("state", "present", ["ssh_pub_key", "description"]),
        ),
    )

    try:
        handle_request(module)
    except TransIPSSHKeyException as exc:
        module.fail_json(msg=str(exc), exception=traceback.format_exc())
    except KeyError as exc:
        module.fail_json(msg='Unable to load {0}'.format(
            str(exc)), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
