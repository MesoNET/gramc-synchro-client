#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: slurm_user

short_description: Set the user in the slurm database with exactly the given accounts.

version_added: "1.0.0"

description: Set the user in the slurm database with exactly the given accounts.

options:
    user:
        description:
        required: true
        type: str
    accounts:
        description:
        required: true
        type: list
        elements: str

author:
    - Yolain ERRE
'''

EXAMPLES = r'''
- name: Set slurm users
  set_slurm_users:
    user:
    accounts:
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
import traceback

import subprocess

def run_module():
    module_args = dict(
        username=dict(type='str', required=True),
        accounts=dict(type='list', elements='str', required=True)
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
        result['changed'] = set_slurm_users(module.params['username'], module.params['accounts'])
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def set_slurm_users(username, accounts):
    slurmresult = subprocess.run(['./roles/populate_slurm/files/set_slurm_user.sh', username] + accounts, stdout=subprocess.PIPE)
    slurmresult.check_returncode()
    return bool(slurmresult.stdout.decode())


def main():
    run_module()


if __name__ == '__main__':
    main()
