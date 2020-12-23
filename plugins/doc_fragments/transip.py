#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Roald Nefs <info@roaldnefs.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


class ModuleDocFragment(object):

    # Standard TransIP documentation fragment.

    DOCUMENTATION = r'''
options:
  access_token:
    description:
      - TransIP access token
    type: str
    aliases: [ api_token ]
  timeout:
    description:
      - The timeout in seconds used for polling TransIP's API.
    type: int
    default: 30
'''
