#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: portail_retreive_users

short_description: Retrieve data from portals and merge it with basic filtering.

version_added: "1.0.0"

description: Retrieve data from portals and merge it with basic filtering.

options:
    users:
        description:
        required: true
        type: list

author:
    - Yolain ERRE
'''

EXAMPLES = r'''
# Retreive users lists and merge them in a similar format
- name: Retreive users and projects lists
  portail_retreive_users:
  register: users_list
'''

RETURN = r'''
users:
    description: The detailed users list.
    type: list
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

import pathlib
import json

def run_module():
    module_args = dict(
        users=dict(type='list', required=True),
        already_deployed_users_file=dict(type='str', required=True)
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
        result['users'] = filter_users(module.params['users'], module.params['already_deployed_users_file'])
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def filter_users(users, already_deployed_users_file):
    resfile = already_deployed_users_file
    if pathlib.Path(resfile).is_file():
        with open(resfile, 'r') as f:
            oldres = json.load(f)
    else:
        oldres = json.loads('{"users":[], "projects":[]}')

    users_to_remove = []
    for user in users:
        if user in oldres["users"] and not user["report"] and not any(k["report"] for k in user["sshkeys"]):
            users_to_remove.append(user)

    for user in users_to_remove:
        users.remove(user)
    return users


def main():
    run_module()


if __name__ == '__main__':
    main()
