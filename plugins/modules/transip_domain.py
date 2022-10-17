#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, Johan Kuijt <info@johankuijt.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r'''
---
module: transip_domain
short_description: Create or remove a TransIP domain DNS entry
description:
- Create or remove a TransIP domain DNS entry
author: "Johan Kuijt (@yo-han)"
options:
  state:
    description:
    - Indicate desired state of the target.
    default: present
    choices: ['present', 'absent']
    type: str
  domain:
    description:
    - The domain name of the DNS entry.
    type: str
  name:
    description:
    - The name of the DNS entry. Can be @ for the domain or a subdomain.
    type: str
  expire:
    description:
    - The TTL in seconds
    default: 300
    type: int
  type:
    description:
    - DNS entry type (A, AAAA, CNAME, MX, NS, TXT, SRV, SSHFP, TLSA, CAA, NAPTR)
    default: A
    choices: ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SRV", "SSHFP", "TLSA", "CAA", "NAPTR"]
    type: str
  content:
    description:
    - The content of the DNS entry. (127.0.0.1 for A, or a domainname for CNAME, etc)
    type: str
extends_documentation_fragment:
- yo_han.transip.transip.documentation
'''

EXAMPLES = r'''
---
- name: Create a new DNS entry
  yo_han.transip.transip_domain:
    state: present
    domain: "example.com"
    name: "ansible"
    content: "127.0.0.1"
    access_token: REDACTED
    register: domain

# - name: Remove a DNS entry
#     yo_han.transip.transip_domain:
#     state: absent
#     domain: "example.com"
#     name: "ansible"
#     content: "127.0.0.1"
#     access_token: REDACTED
'''

RETURN = r'''
data:
  description: Create a DNS entry
  returned: changed
  type: dict
  sample: [
    {
        "changed": true,
        "data": "DNS entry created",
        "failed": false
    }
  ]
'''

from email.policy import default
from ansible_collections.yo_han.transip.plugins.module_utils.transip import TransIPHelper
from ansible.module_utils.basic import AnsibleModule
import traceback


class TransIPNetworkException(Exception):
    pass


class TransIPDomain(object):

    def __init__(self, module):
        self.module = module
        self.rest = TransIPHelper(module)

    def list(self):
        """Returns a list of all DNS entries for this domain."""
        domain = self.module.params.get("domain")
        path = "domains/{0}/dns".format(domain)
        response = self.rest.get(path)

        if response.status_code == 200:
            return response.json.get("dnsEntries", [])

        return []

    def get(self):
        """Get information of a specific network."""
        name = self.module.params.get("name")
        content = self.module.params.get("content")

        for entry in self.list():
            if entry["name"] == name and entry["content"] == content:
                return {"dnsEntry": entry}
        return None

    def create(self):
        """Create a new DNS entry for the current domain."""
        json_data = self.get()

        dns_entry = {"dnsEntry":
                     {
                         "name": self.module.params["name"],
                         "expire": self.module.params["expire"],
                         "type": self.module.params["type"],
                         "content": self.module.params["content"],
                     }
                     }

        if json_data and dns_entry == json_data:
            self.module.exit_json(changed=False)
        if self.module.check_mode:
            self.module.exit_json(changed=True)

        domain = self.module.params.get("domain")
        path = "domains/{0}/dns".format(domain)

        if dns_entry == json_data:
            response = self.rest.patch(path, data=dns_entry)
        else:
            response = self.rest.post(path, data=dns_entry)

        if response.status_code == 201:
            self.module.exit_json(changed=True, data="DNS entry created")
        elif response.status_code == 204:
            self.module.exit_json(changed=True, data="DNS entry updated")
        else:
            json_data = response.json
            error_msg = "Failed to create DNS entry"
            if json_data and "error" in json_data:
                error_msg = json_data["error"]
            else:
                error_msg = response.debug
            self.module.fail_json(changed=False, msg=error_msg)

    def remove(self):
        """Remove a DNS entry for the current domain."""
        domain = self.module.params.get("domain")

        path = "domains/{0}/dns".format(domain)

        dns_entry = {"dnsEntry":
                     {
                         "name": self.module.params["name"],
                         "expire": self.module.params["expire"],
                         "type": self.module.params["type"],
                         "content": self.module.params["content"],
                     }
                     }

        response = self.rest.delete(path, data=dns_entry)

        if response.status_code == 204:
            self.module.exit_json(changed=True, msg="DNS entry removed")
        else:
            self.module.fail_json(changed=False, msg="DNS entry not found")


def handle_request(module):
    network = TransIPDomain(module)
    state = module.params["state"]

    if state == "present":
        network.create()
    elif state == "absent":
        network.remove()


def main():
    argument_spec = TransIPHelper.transip_argument_spec()
    argument_spec.update(
        state=dict(choices=["present", "absent"], default="present"),
        domain=dict(type="str"),
        name=dict(type="str"),
        expire=dict(type="int", default=300),
        type=dict(type="str", default="A", choices=[
                  "A", "AAAA", "CNAME", "MX", "NS", "TXT", "SRV", "SSHFP", "TLSA", "CAA", "NAPTR"]),
        content=dict(type="str"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_if=([
            ("state", "present", ["domain", "name", "content"]),
            ("state", "absent", ["domain", "name", "content"]),
        ]),
        supports_check_mode=True,
    )

    try:
        handle_request(module)
    except TransIPNetworkException as exc:
        module.fail_json(msg=str(exc), exception=traceback.format_exc())
    except KeyError as exc:
        module.fail_json(msg='Unable to load {0}'.format(
            str(exc)), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
