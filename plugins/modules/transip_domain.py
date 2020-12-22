#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: transip_domain
short_description:
description:
author: "Roald Nefs (@roaldnefs)"
options:
extends_documentation_fragment:
- roaldnefs.transip.transip.documentation
'''

import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.roaldnefs.transip.plugins.module_utils.transip import TransIPHelper
from ansible.module_utils._text import to_native


def core(module):
    pass


def main():
    argument_spec = TransIPHelper.transip_argument_spec()
    argument_spec.update(
        state=dict(choices=["present"], default="present")
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    try:
        core(module)
    except Exception as exc:
        module.fail_json(msg=to_native(exc), exception=traceback.format_exc())

if __name__ == "__main__":
    main()
