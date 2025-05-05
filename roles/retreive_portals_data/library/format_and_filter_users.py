#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: format_and_filter_users

short_description: Filter valid and invalid users and extract projects from the user list obtained through the portals modules.

version_added: "1.0.0"

description: Filter valid and invalid users and extract projects from the user list obtained through the portals modules.

options:
    users:
        description: Correctly formated dictionnary listing users and their informations.
        required: true
        type: list
    min_uid:
        description: Minimum UID of the range managed by this module.
        required: true
        type: int
    max_uid:
        description: Maximum UID of the range managed by this module.
        required: true
        type: int
    min_gid:
        description: Minimum GID of the range managed by this module.
        required: true
        type: int
    max_gid:
        description: Maximum GID of the range managed by this module.
        required: true
        type: int
    cluster_users_file:
        description: File where are read and saved the associations username/uid/portal_id/portal_name.
        required: true
        type: int

author:
    - Yolain ERRE
'''

EXAMPLES = r'''
- name: Filter users and retreive users and projects lists
  format_and_filter_users:
    users: "{{users_portal.users}}"
  register: users_and_projects
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

import sys
import re
import json
import subprocess
import hashlib


def run_module():
    module_args = dict(
        users=dict(type='list', required=True),
        min_uid=dict(type='int', required=True),
        max_uid=dict(type='int', required=True),
        min_gid=dict(type='int', required=True),
        max_gid=dict(type='int', required=True),
        cluster_users_file=dict(type='str', required=True)
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
        result['users'], result['projects'] = filter_users(
            module.params['users'],
            module.params['min_uid'],
            module.params['max_uid'],
            module.params['min_gid'],
            module.params['max_gid'],
            module.params['cluster_users_file'])
    except:
        module.fail_json(msg=traceback.format_exc(), **result)

    module.exit_json(**result)


def search_user_database(portalid, portalname, cluster_users_file):
    nameresult = subprocess.run(
        [
            'awk',
            '$3=="{}" && $4=="{}" {{print $1,$2}}'.format(portalid, portalname),
            'FS=:',
            'OFS=:',
            cluster_users_file
        ],
        stdout=subprocess.PIPE
    )
    if nameresult.returncode != 0:
        exit(1)
    namedata = nameresult.stdout.decode().split(':')

    if len(namedata) == 2:
        return (namedata[0], int(namedata[1]))
    else:
        return None


def init_default_uid(min_uid, max_uid, cluster_users_file):
    newuidresult = subprocess.run(
        ['./roles/retreive_portals_data/files/get_new_id.sh', str(min_uid), str(max_uid)],
        stdout=subprocess.PIPE
    )
    newuidresult.check_returncode()
    default_uid = int(newuidresult.stdout)
    with open(cluster_users_file, 'r') as f:
        lines = f.readlines()
        default_uid = max(max([int(x.split(':')[1]) for x in lines] + [0]), default_uid)
    return default_uid


def get_new_username(email, preferred):
    if preferred is not None and len(preferred) > 3:
        if re.match(r'^[a-z][a-z0-9_]{5,31}$', preferred.lower()):
            basename = preferred.lower()
        else:
            return None
    else:
        names = re.sub(r'(@.*)|([^a-z.])', '', email.lower()).split('.')
        if len(names) == 0:
            return None
        if len(names) == 1:
            names.insert(0, '')
        basename = (names[0][:max(8 - len(names[1]), 2)] + names[1]).ljust(8, '0')
    name = basename
    idresult = subprocess.run(
        ['id', '-u', name],
        stdout=subprocess.PIPE
    )
    appened_number = 1
    while idresult.returncode == 0:
        name = basename + str(appened_number)
        idresult = subprocess.run(
            ['id', '-u', name],
            stdout=subprocess.PIPE
        )
    return name


def give_id_and_username_to_user(user, default_uid, min_uid, max_uid, cluster_users_file):
    user['username'] = user['username'].lower()

    # First, search if the mesonet account id is present in local users database
    tmp = search_user_database(user['id'], user['portal'], cluster_users_file)
    if tmp is not None:
        user['username'] = tmp[0]
        user['uid'] = tmp[1]

    # Else, checks other solutions
    else:

        # If the user has no login, generate one that doesn't exist alongside a new uid
        if user['username'] == "nologin":
            if default_uid > max_uid:
                raise Exception("Fatal error: uid overflow.")
            name = get_new_username(user['email'], user['preferred'])
            if name is None:
                return False, default_uid
            # Creates a new user with a uid between 10⁹ and 2×10⁹ excluded
            user['username'] = name
            user['uid'] = default_uid
            default_uid += 1

        # If the user has a login, we retrieve the uid
        else:
            # Search if the username exists
            idresult = subprocess.run(
                ['id', '-u', user['username']],
                stdout=subprocess.PIPE
            )

            # If it doesn't exist, there is a problem
            if idresult.returncode != 0:
                print("Warning: User " + user['username'] + " doesn't exist.", file=sys.stderr)
                return False, default_uid
            # Else, take the uid
            user['uid'] = int(idresult.stdout)

        # Adding user to local database
        if not (user['uid'] < min_uid or max_uid < user['uid']):
            with open(cluster_users_file, 'a') as myfile:
                myfile.write('{}:{}:{}:{}\n'.format(user['username'], user['uid'], user['id'], user['portal']))

    # We double check if uid is not outside 10⁹ and 2×10⁹ excluded
    if user['uid'] < min_uid or max_uid < user['uid']:
        return False, default_uid
    # We check if username is UNIX compatible
    if re.match(r'^[a-z_][-a-z0-9_]*$', user['username']) is None:
        return False, default_uid
    return True, default_uid


def give_id_to_project(project, default_gid, tmp_projects, min_gid, max_gid):
    project['name'] = project['name'].lower()

    if project['name'] in tmp_projects:
        project['gid'] = tmp_projects[project['name']]

    else:

        # TODO Change getent, it bugs if there is too many users in ldap, may be safer to directly use ldap commands
        # Second, search if the groupname given by the mesonet portal exists
        idresult = subprocess.run(['getent', 'group', project['name']], stdout=subprocess.PIPE)

        # If it exists, takes the group id linked to this groupname
        if idresult.returncode == 0:
            project['gid'] = int(str.encode(str(idresult.stdout).split(':')[2]))

        # else, creates a new project id between 2×10⁹ and 3×10⁹ excluded
        else:
            if default_gid == 0:
                newgidresult = subprocess.run(['./roles/retreive_portals_data/files/get_new_id.sh', str(min_gid), str(max_gid)], stdout=subprocess.PIPE)
                newgidresult.check_returncode()
                default_gid = int(newgidresult.stdout)
            project['gid'] = default_gid
            default_gid += 1

    if project['gid'] < min_gid or max_gid < project['gid']:
        return False, default_gid
    if re.match(r'^[a-z_][-a-z0-9_]*$', project['name']) is None:
        return False, default_gid

    tmp_projects[project['name']] = project['gid']
    return True, default_gid


def filter_users(users, min_uid, max_uid, min_gid, max_gid, cluster_users_file):
    default_uid = init_default_uid(min_uid, max_uid, cluster_users_file)
    default_gid = 0
    tmp_projects = {}
    users_to_remove = []
    for user in users:
        isidgiven, default_uid = give_id_and_username_to_user(user, default_uid, min_uid, max_uid, cluster_users_file)
        if not isidgiven:
            users_to_remove.append(user)
            continue

        # Search the groups ids or give them a new id if they have no id
        projects_to_remove = []
        for project in user['projects']:
            isidgiven, default_gid = give_id_to_project(project, default_gid, tmp_projects, min_gid, max_gid)
            if not isidgiven:
                projects_to_remove.append(project)

        # Removing all groups with wrong or no gid
        for project in projects_to_remove:
            user['projects'].remove(project)

    # Removing all users with wrong or no uid
    for user in users_to_remove:
        users.remove(user)

    # Extract projects from users data
    jqresult_projects = subprocess.run(
        [
            'jq',
            '--compact-output',
            '--from-file',
            'roles/retreive_portals_data/files/extract_projects.jq'
        ], input=json.dumps(users).encode('utf-8'), stdout=subprocess.PIPE)
    jqresult_projects.check_returncode()

    projects = json.loads(jqresult_projects.stdout)

    for user in users:
        user["hash"] = hashlib.sha256(json.dumps(user).encode()).hexdigest()
    for project in projects:
        project["hash"] = hashlib.sha256(json.dumps(project).encode()).hexdigest()

    return users, projects


def main():
    run_module()


if __name__ == '__main__':
    main()
