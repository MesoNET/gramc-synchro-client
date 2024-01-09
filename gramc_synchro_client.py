#!/usr/bin/python3

# Retreive accounting data from the mesonet server and add the local information (or create it if inexistant).
# Follows these rules:
# — Creates users ids between 1000000000 and 2000000000 excluded
# — Creates groups ids between 2000000000 and 3000000000 excluded, except for user groups which use the the same id as their corresponding users
# For information, from the file /etc/login.defs:
# — Defaults SYS_UID_MIN and SYS_UID_MAX used by useradd are 201 to 999 included, same for groups
# — Defaults UID_MIN and UID_MAX used by useradd are 1000 to 60000 included, same for groups
# — Defaults SUB_UID_MIN and SUB_UID_MAX used by useradd are 100000 to 600100000 included, same for groups
# So the range 1000000000 to 3000000000 will never collide with these.

# ——————— #
#  BEGIN  #
# ——————— #

import sys
import re
import json
import subprocess
import requests

# —————————————————————————————————————————————— #
#  Step 1/3: Retrieve data from mesonet portals  #
# —————————————————————————————————————————————— #

#  Retrieving data
# -----------------

# Retrieving data from the gramc mesonet server
users_gramc_json = json.dumps(
    requests.post(
        'https://acces.mesonet.fr/gramc-meso/adminux/utilisateurs/get',
        data=json.dumps({}),
        headers={'content-type': 'application/json'}
    ).json()
)
sshkeys_gramc_json = json.dumps(
    requests.post(
        'https://acces.mesonet.fr/gramc-meso/adminux/clessh/get',
        data=json.dumps({}),
        headers={'content-type': 'application/json'}
    ).json()
)

#  Filtering & formatting data
# -----------------------------

# Filter and format the gramc data for further use
jqresult_gramc = subprocess.run(
    [
        'jq',
        '--compact-output',
        '--from-file', 'lib/gramc2juliet.jq',
        '--argjson', 'sshkeys',
        sshkeys_gramc_json
    ],
    input=users_gramc_json.encode('utf-8'), stdout=subprocess.PIPE
)
jqresult_gramc.check_returncode()
users = json.loads(jqresult_gramc.stdout)

# ———————————————————————————————————————————————— #
#  Step 2/3: Create or find local accounting data  #
# ———————————————————————————————————————————————— #


def get_new_username(email, preferred):
    if preferred is not None:
        basename = preferred
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


# Returns True if successful, else False
def give_id_and_username_to_user(user):
    global new_uid
    user['username'] = user['username'].lower()

    # If the user has no login, generate one that doesn't exist alongside a new uid
    if user['username'] == "nologin":
        name = get_new_username(user['email'], user['preferred'])
        if name is None:
            return False
        # Creates a new user with a uid between 10⁹ and 2×10⁹ excluded
        if new_uid == 0:
            newuidresult = subprocess.run(
                ['./lib/get_new_id.sh', '1000000000', '1999999999'],
                stdout=subprocess.PIPE
            )
            newuidresult.check_returncode()
            new_uid = int(newuidresult.stdout)
        user['uid'] = new_uid
        new_uid += 1

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
            return False
        # Else, take the uid
        user['uid'] = int(idresult.stdout)

    # We double check if uid is not outside 10⁹ and 2×10⁹ excluded
    if user['uid'] < 1000000000 or 1999999999 < user['uid']:
        return False
    return True


def give_id_to_project(project):
    global new_gid
    project['name'] = project['name'].lower()

    # TODO Change getent, it bugs if there is too many users in ldap, may be safer to directly use ldap commands
    # Second, search if the groupname given by the mesonet portal exists
    idresult = subprocess.run(['getent', 'group', project['name']], stdout=subprocess.PIPE)

    # If it exists, takes the group id linked to this groupname
    if idresult.returncode == 0:
        project['gid'] = int(str.encode(str(idresult.stdout).split(':')[2]))

    # else, creates a new project id between 2×10⁹ and 3×10⁹ excluded
    else:
        if new_gid == 0:
            newgidresult = subprocess.run(['./lib/get_new_id.sh', '2000000000', '2999999999'], stdout=subprocess.PIPE)
            newgidresult.check_returncode()
            new_gid = int(newgidresult.stdout)
        project['gid'] = new_gid
        new_gid += 1

    if project['gid'] < 2000000000 or 2999999999 < project['gid']:
        return False
    return True


# Search the users ids or give them a new id if they have no id
new_uid = 0
users_to_remove = []
for user in users:

    if not give_id_and_username_to_user(user):
        users_to_remove.append(user)
        continue

    # Search the groups ids or give them a new id if they have no id
    new_gid = 0
    projects_to_remove = []
    for project in user['projects']:
        if not give_id_to_project(project):
            projects_to_remove.append(project)

    # Removing all groups with wrong or no gid
    for project in projects_to_remove:
        user['projects'].remove(project)


# Removing all users with wrong or no uid
for user in users_to_remove:
    users.remove(user)

# Extract projects from users data
jqresult_projects = subprocess.run(['jq', '--compact-output', '--from-file', 'lib/extract_projects.jq'], input=json.dumps(users).encode('utf-8'), stdout=subprocess.PIPE)
jqresult_projects.check_returncode()

projects = json.loads(jqresult_projects.stdout)

# TODO: Reverify ldap works to be sure

# —————————————————————————————————————————————————————————— #
#  Step 3/3: Apply and propagate accounting data to servers  #
# —————————————————————————————————————————————————————————— #

# Create the result object
res = json.loads('{}')
res['users'] = users
res['projects'] = projects

# Update slurm database
for user in users:
    user_projects_names = []
    for project in user['projects']:
        user_projects_names.append(project['name'])
    slurmresult = subprocess.run(['./lib/set_slurm_user.sh', user['username']] + user_projects_names)
    slurmresult.check_returncode()

# Apply the changes on servers
ansibleresult = subprocess.run(['ansible-playbook', '--extra-vars', json.dumps(res), './lib/account_propag.ansible.yaml'], capture_output=True)
print(ansibleresult.stderr.decode('utf-8'), file=sys.stderr)
result = json.loads(ansibleresult.stdout)
print(json.dumps(result['stats'], indent=4))
checkreturncode = False
for (host, stat) in result['stats'].items():
    checkreturncode = checkreturncode or not (stat['changed'] + stat['ok'] + stat['skipped'] > 0 or stat['unreachable'] > 0)
    checkreturncode = checkreturncode or not (stat['failures'] == 0)
if checkreturncode:
    ansibleresult.check_returncode()

# Send to portal if an account is created
for user_result in result['plays'][1]['tasks'][0]['hosts']['localhost']['results']:
    user = user_result['item']
    if user['report'] and not user_result['failed']:
        for project in user['projects']:
            requests.post(
                'https://acces.mesonet.fr/gramc-meso/adminux/utilisateurs/setloginname',
                data=json.dumps(
                    {
                        "loginname": user['username'] + "@Juliet",
                        "idIndividu": user['id'],
                        "projet": project['name']
                    }),
                headers={'content-type': 'application/json'}
            )

# Send to portal if an ssh key is deployed
for key_result in result['plays'][2]['tasks'][0]['hosts']['localhost']['results']:
    user = key_result['item'][0]
    sshkey = key_result['item'][1]
    if sshkey['report'] and 'failed' in key_result and not key_result['failed']:
        for project in user['projects']:
            requests.post(
                'https://acces.mesonet.fr/gramc-meso/adminux/clessh/deployer',
                data=json.dumps(
                    {
                        "loginname": user['username'] + "@Juliet",
                        "idIndividu": user['id'],
                        "projet": project['name']
                    }),
                headers={'content-type': 'application/json'}
            )

# ————— #
#  END  #
# ————— #
