#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: retreive_mesonet_users

short_description: Retrieve data from the mesonet portal and format it with basic filtering.

version_added: "1.0.0"

description: Retrieve data from the mesonet portal and format it with basic filtering.

options:

author:
    - Yolain ERRE
'''

EXAMPLES = r'''
# Retreive users list
- name: Retreive users and projects lists
  retreive_mesonet_users:
  register: mesonet_users
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
import requests
import tempfile

def run_module():
    module_args = dict(
        cluster_name=dict(type='str', required=True)
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
        result['users'] = retreive_data(module.params['cluster_name'])
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def retreive_data(cluster_name):
    users_gramc_json = json.dumps(
        requests.post(
            'https://acces.mesonet.fr/gramc-meso/adminux/utilisateurs/get',
            data=json.dumps({}),
            headers={'content-type': 'application/json'}
        ).json()
    )
    with tempfile.NamedTemporaryFile() as tmp_sshkeys_gramc_file:
        with open(tmp_sshkeys_gramc_file.name, 'w') as f:
            f.write(
                json.dumps(
                    requests.post(
                        'https://acces.mesonet.fr/gramc-meso/adminux/clessh/get',
                        data=json.dumps({}),
                        headers={'content-type': 'application/json'}
                    ).json()
                )
            )
        jqresult_gramc = subprocess.run(
            [
                'jq',
                '--compact-output',
                '--from-file', 'roles/retreive_portals_data/files/from_mesonet_portal.jq',
                '--arg', 'cluster_name', cluster_name,
                '--slurpfile', 'sshkeys', tmp_sshkeys_gramc_file.name
            ],
            input=users_gramc_json.encode('utf-8'), stdout=subprocess.PIPE
        )
    jqresult_gramc.check_returncode()
    users_gramc = json.loads(jqresult_gramc.stdout)
    return users_gramc


def main():
    run_module()


if __name__ == '__main__':
    main()
