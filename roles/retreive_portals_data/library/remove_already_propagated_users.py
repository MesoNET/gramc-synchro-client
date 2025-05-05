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
        projects=dict(type='list', required=True),
        already_deployed_users_file=dict(type='str', required=True),
        already_deployed_projects_file=dict(type='str', required=True)

    )
    result = dict(
        changed=False,
        users=[],
        projects=[]
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        result['users'], result['projects'] = filter_users(module.params['users'], module.params['projects'],
                                                           module.params['already_deployed_users_file'], module.params['already_deployed_projects_file'])
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def filter_users(users, projects, users_hashes_file, projects_hashes_file):
    if pathlib.Path(users_hashes_file).is_file():
        with open(users_hashes_file, 'r') as f:
            for line in f:
                [portal, user_id, user_hash] = line.split(':')
                for user in users:
                    if user["report"] or user["portal"] != portal or str(user["id"]) != user_id or user["hash"] != user_hash:
                        users.remove(user)
                        break
    if pathlib.Path(projects_hashes_file).is_file():
        with open(projects_hashes_file, 'r') as f:
            for line in f:
                [portal, project_name, project_hash] = line.split(':')
                for project in projects:
                    if project["report"] or project["name"] != project_name or project["hash"] != project_hash:
                        projects.remove(project)
                        break

    return users, projects


def main():
    run_module()


if __name__ == '__main__':
    main()
