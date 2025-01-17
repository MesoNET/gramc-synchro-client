#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: failsafe_check

short_description: Check for some inconsistencies in the users and projects lists.

version_added: "1.0.0"

description: Check for some inconsistencies in the users and projects lists.

options:
    users:
        description:
        required: true
        type: list
    projects:
        description:
        required: true
        type: list

author:
    - Yolain ERRE
'''

EXAMPLES = r'''
- name: Failsafe check
  failsafe_check:
    users: "{{users_and_projects.users}}"
    projects: "{{users_and_projects.projects}}"
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

import sys

def run_module():
    module_args = dict(
        users=dict(type='list', required='true'),
        projects=dict(type='list', required='true')
    )
    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        failsafe_check(module.params['users'], module.params['projects'])
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def failsafe_check(users, projects):
    # Warn if number of users is too high. Must not go above 15257 because of subuid and subgid numbers.
    if len(users) > 10000:
        with open('/root/WARNING.sync_users.txt','w') as f:
            print('WARNING: Number of users is {} and must not go above 15257.'.format(len(users)), file=f)

    # Verify no user or project have same id
    error = False
    ids = []
    for user in users:
        if user['uid'] in ids:
            print("Fatal Error: ID " + str(user['uid']) + " is duplicate.", file=sys.stderr)
            raise Exception("Fatal Error: ID " + str(user['uid']) + " is duplicate.")
        elif user['username'] == 'nologin':
            print("Fatal Error: User " + str(user['email']) + " has no login.", file=sys.stderr)
            raise Exception("Fatal Error: User " + str(user['email']) + " has no login.")
        else:
            ids.append(user['uid'])
    for project in projects:
        if project['gid'] in ids:
            print("Fatal Error: ID " + str(project['gid']) + " is duplicate.", file=sys.stderr)
            raise Exception("Fatal Error: ID " + str(project['gid']) + " is duplicate.")
        else:
            ids.append(project['gid'])
    return


def main():
    run_module()


if __name__ == '__main__':
    main()
