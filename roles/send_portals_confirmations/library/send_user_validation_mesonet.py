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
projects:
    description: The detailed projects list.
    type: list
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

import requests
import json

def run_module():
    module_args = dict(
        user=dict(type='dict', required=True),
        cluster_name=dict(type='str', required=True)
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
        send_validation(module.params['user'], module.params['cluster_name'])
        result['changed'] = True
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def send_validation(user, cluster_name):
    for project in user['projects']:
        if project['report']:
            r = requests.post(
                'https://acces.mesonet.fr/gramc-meso/adminux/utilisateurs/setloginname',
                data=json.dumps(
                    {
                        "loginname": user['username'] + "@" + cluster_name,
                        "idIndividu": user['id'],
                        "projet": project['name']
                    }),
                headers={'content-type': 'application/json'}
            )
    return


def main():
    run_module()


if __name__ == '__main__':
    main()
