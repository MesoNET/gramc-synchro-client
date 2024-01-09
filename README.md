Mesonet synchroclient
=====================

Warning: This project is usable with modifications but still a WiP.

Description
-----------

Mesonet synchroclient is a group of scripts and playbooks used to automaticly synchronize users, projects and ssh keys from a gramc portal to a local cluster of servers. It also synchronise projects as local groups and local Slurm accounts.

Requirements
------------

- Ansible, with the community modules
- Python with the json, subprocess and requests modules
- Nodes in the cluster needs to be accessible from the script's server without human intervention (ex. private key method).

Installation
------------

1. Clone the repo
2. Configure ansible hosts
3. Configure ansible to return json formated format (In "ansible.cfg", section "\[defaults\]", set "callbacks\_enabled=json" and "stdout\_callback=json")
4. Make sure in the "./lib/\*" files that everything corresponds to your cluster's configuration (ansible playbook for propagation, ldap ids for new id computing, etc...)
5. Add "0 1 \* \* \*  cd /path/to/cloned/dir/ && ./gramc\_synchro\_client.py >.gramc\_synchro\_client.log 2>.gramc\_synchro\_client.err" to cron

### Optional but recommended

- Configure Ansible to run the playbook faster, for example in "ansible.cfg" in "\[ssh\_connection\]" section:
  - Enable pipelining with "pipelining=True"
  - Enable ssh persistance with "ssh\_args=-o ControlMaster=yes -o ControlPersist=60s"

### Tips & tricks (not tested)

You can run the "gramc\_synchro\_client.py" script with some environment variables to have a custom "ansible.cfg" file and a custom ".netrc" file

- Custom ansible configuration file: "ANSIBLE\_CONFIG=$custom\_path"
  - See [https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html#environment]
- Custom .netrc file: "NETRC=$custom\_path"
  - See [https://docs.python-requests.org/en/latest/user/quickstart/#custom-headers]

Project files
-------------

gramc\_synchro\_client/
├── doc/
│   └── json\_description.md
├── lib/
│   ├── account\_propag.ansible.yaml
│   ├── extract\_projects.jq
│   ├── get\_new\_id.sh
│   ├── gramc2juliet.jq
│   └── set\_slurm\_user.sh
├── readme.md
└── gramc\_synchro\_client.py

