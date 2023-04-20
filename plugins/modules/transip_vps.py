#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: transip_vps
short_description: Create and delete a TransIP VPS
description:
- Create and delete a VPS in TransIP.
author: "Roald Nefs (@yo-han)"
options:
  state:
    description:
    - Indicate desired state of the target.
    choices: ['present', 'absent']
    type: str
  name:
    description:
    - The unique name of the VPS as provided by TransIP.
    type: str
  description:
    description:
    - The name of the VPS that can be set by the customer.
    type: str
  unique_description:
    description:
    - Require an unique description of the VPS. By default TransIP allows multiple hosts with the
      same description. Setting this to "yes" allows only unique descriptions to be used. Useful for
      idempotence, as the unique name of the VPS will be generated by TransIP.
    default: False
    type: bool
  product_name:
    description:
    - Name of the product, e.g. vps-bladevps-x1.
    type: str
  operating_system:
    description:
    - The name of the operating system to install, e.g. ubuntu-18.04.
    type: str
  availability_zone:
    description:
    - The transip availability zone
    type: str
    default: ams0
  username:
    description:
    - Username used for account creating during cloudinit installation (max 32 chars)
    type: str
  ssh_key:
    description:
    - Public ssh key to use for account creating during installation
    type: str
  end_time:
    description:
    - Indicate when the VPS will be terminated.
    - On 'end', the VPS will be terminated on the end date of the agreement.
    - On 'immediately', the VPS will be terminated immediately.
    default: end
    choices: ['end', 'immediately']
    type: str
extends_documentation_fragment:
- yo_han.transip.transip.documentation
'''

EXAMPLES = r'''
---
- name: Create a new VPS
  yo_han.transip.transip_vps:
    state: present
    description: "example vps description"
    unique_description: true
    product_name: vps-bladevps-x1
    operating_system: ubuntu-18.04
    availability_zone: ams0
    username: test
    ssh_key: "ssh-rsa AAAAB3NzaC1yc2EAAA..."
    access_token: REDACTED
  register: result

# - name: Get VPS
#   yo_han.transip.transip_vps:
#   name: "vps-name"
#   access_token: REDACTED
#   register: vps
#   ignore_errors: true
#   until: result.changed == True
#   retries: 10
#   delay: 5

# - debug:
#     msg: "Created new VPS with name {{ vps.data.vps.name }}."

# - name: Delete a VPS
#   yo_han.transip.transip_vps:
#     state: absent
#     name: transipdemo-vps
#     end_time: immediately
#     access_token: REDACTED
'''

RETURN = r'''
---
data:
  description: a TransIP VPS
  returned: changed
  type: dict
  sample: {
    "vps": {
        "availabilityZone": "ams0",
        "cpus": 3,
        "currentSnapshots": 1,
        "description": "",
        "diskSize": 52428800,
        "ipAddress": "141.138.136.129",
        "isBlocked": false,
        "isCustomerLocked": false,
        "isLocked": false,
        "macAddress": "52:54:00:19:a7:20",
        "maxSnapshots": 1,
        "memorySize": 1048576,
        "name": "transipdemo-vps",
        "operatingSystem": "FreeBSD 10.0-RELEASE",
        "productName": "vps-bladevps-x1",
        "status": "running",
        "tags": [
            "customTag",
            "anotherTag"
        ]
    }
  }
'''

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.yo_han.transip.plugins.module_utils.transip import TransIPHelper


class TransIPVPSException(Exception):
    pass


class TransIPVPS(object):

    def __init__(self, module):
        self.module = module
        self.rest = TransIPHelper(module)

    def list(self):
        """Returns a list of all VPSs."""
        path = "vps"
        response = self.rest.get(path)

        if response.status_code == 200:
            return response.json.get("vpss", [])

        return []

    def get(self):
        """Get information of a specific VPS."""
        name = self.module.params.get("name")
        description = self.module.params.get("description")
        unique_description = self.module.params.get("unique_description")

        json_data = self.get_by_name(name)
        if not json_data and unique_description:
            json_data = self.get_by_description(description)
        return json_data

    def get_by_name(self, name):
        """Get information of a specific VPS by name."""
        path = "vps/{0}".format(name)
        response = self.rest.get(path)

        if response.status_code == 200:
            return response.json

        return None

    def get_by_description(self, description):
        """Get information of a specific VPS by description."""
        for vps in self.list():
            if vps["description"] == description:
                return {"vps": vps}
        return None

    def create(self):
        """Order a new VPS if it doesn't already exists."""
        json_data = self.get()
        if json_data:
            self.module.exit_json(changed=False)
        if self.module.check_mode:
            self.module.exit_json(changed=True)

        path = "vps"

        # Set the required request attributes
        data = {
            "productName": self.module.params["product_name"],
            "operatingSystem": self.module.params["operating_system"],
        }

        # Add the optional request attributes
        description = self.module.params.get("description")
        if description:
            data["description"] = description

        sshKey = self.module.params.get("ssh_key")
        if sshKey:
            data["sshKeys"] = [sshKey]

        username = self.module.params.get("username")
        if username:
            data["username"] = username

        availabilityZone = self.module.params.get("availability_zone")
        if availabilityZone:
            data["availabilityZone"] = availabilityZone
        else:
            data["availabilityZone"] = "ams0"

        response = self.rest.post(path, data=data)

        if response.status_code == 201:
            # Retrieve data about the newly created VPS, as the TransIP API
            # doesn't provide any information on the creation of the VPS
            json_data = self.get()
            # When using the demo access token, the API doesn't actually create
            # the VPS so the json_data might be empty
            vps_data = {"vps": {}}
            if json_data and "vps" in json_data:
                vps_data["vps"] = json_data["vps"]
            self.module.exit_json(changed=True, data=vps_data)
        else:
            json_data = response.json
            error_msg = "Failed to order VPS"
            if json_data and "error" in json_data:
                error_msg = json_data["error"]
            self.module.fail_json(changed=False, msg=error_msg)

    def cancel(self):
        """Cancel a VPS using the specified end time attribute, on 'end' will
        terminate the VPS on the end date of the agreement while 'immediately'
        will terminate the VPS immediately.
        """
        name = self.module.params.get("name")
        end_time = self.module.params.get("end_time")

        json_data = self.get_by_name(name)
        if json_data:
            if self.module.check_mode:
                self.module.exit_json(change=True)
            path = "vps/{0}".format(name)
            data = {"endTime": end_time}
            response = self.rest.delete(path, data=data)

            if response.status_code == 204:
                self.module.exit_json(changed=True, msg="VPS canceled")
            self.module.fail_json(changed=False, msg="Failed to cancel VPS")
        else:
            self.module.fail_json(changed=False, msg="VPS not found")

    def get_vps(self):
        """Retrieve vps information."""
        json_data = self.get()
        if json_data:
            self.module.exit_json(changed=True, data=json_data)
        else:
            self.module.fail_json(changed=False, msg="VPS not found")

    def get_list(self):
        """Retrieve vps information."""
        json_data = self.list()
        if json_data:
            self.module.exit_json(changed=True, data=json_data)
        else:
            self.module.fail_json(changed=False, msg="VPS not found")


def handle_request(module):
    vps = TransIPVPS(module)
    state = module.params["state"]
    name = module.params.get("name")
    description = module.params.get("description")

    if state == "present":
        vps.create()
    elif state == "absent":
        vps.cancel()
    elif not state and (name or description):
        vps.get_vps()


def main():
    argument_spec = TransIPHelper.transip_argument_spec()
    argument_spec.update(
        state=dict(choices=["present", "absent"]),
        name=dict(type="str"),
        product_name=dict(type="str"),
        operating_system=dict(type="str"),
        availability_zone=dict(type="str", default="ams0"),
        ssh_key=dict(type="str", no_log=True),
        username=dict(type="str"),
        end_time=dict(choices=["end", "immediately"], default="end"),
        description=dict(type="str"),
        unique_description=dict(type="bool", default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=([
            ("state", "present", ["product_name", "operating_system"]),
            ("state", "absent", ["end_time"]),
            ("unique_description", True, ["description"]),
        ]),
        supports_check_mode=True,
    )

    try:
        handle_request(module)
    except TransIPVPSException as exc:
        module.fail_json(msg=str(exc), exception=traceback.format_exc())
    except KeyError as exc:
        module.fail_json(msg='Unable to load {0}'.format(
            str(exc)), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
