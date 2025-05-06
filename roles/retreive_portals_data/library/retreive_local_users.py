#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: retreive_local_users

short_description: Retrieve data from the local portal and format it with basic filtering.

version_added: "1.0.0"

description: Retrieve data from the local portal and format it with basic filtering.

options:

author:
    - Yolain ERRE
'''

EXAMPLES = r'''
# Retreive users list
- name: Retreive users and projects lists
  retreive_local_users:
  register: local_users
'''

RETURN = r'''
users:
    description: The detailed users list.
    type: list
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

import json
import subprocess
from urllib import request

def run_module():
    module_args = dict(
    )
    result = dict(
        changed=False,
        users=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        result['users'] = retreive_data()
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def retreive_data():
    with open('./local/localdb.json', 'r') as file:
        users = json.loads(file.read())
    return users


def main():
    run_module()


if __name__ == '__main__':
    main()
