#!/usr/bin/bash

set -e

for i in "$@"
do
	if [[ $i == '-h' || $i == '--help' ]]
	then
		echo "\
Add a user to slurm. Projects can be added after the user to add the user to these projects. This script check for the presence of the user before adding them to slurm or to a project.

Usage: $0 USERNAME [PROJECT1 PROJECT2 ...]

Options:
	-h,--help	Prints this help and exit."
		exit
	fi
done

if [[ $1 == '' ]]
then
	echo 'Error: no argument'
	exit 1
fi

user=$1
shift

if [[ $(sacctmgr --noheader --parsable2 list associations account=default user=$user) == '' ]]
then
	sacctmgr --immediate add user name=$user account=default adminlevel=none defaultaccount=default
fi

if [[ $# -gt 0 ]]
then
	for project in "$@"
	do
		if [[ $(sacctmgr --noheader --parsable2 list associations account=$project) == '' ]]
		then
			sacctmgr --immediate add account name=$project parent=projects
		fi
		if [[ $(sacctmgr --noheader --parsable2 list associations account=$project user=$user) == '' ]]
		then
			sacctmgr --immediate add user name=$user account=$project adminlevel=none
		fi
#		if [[ $(sacctmgr --noheader --parsable2 list user name=$user | cut -d'|' -f2) == 'default' ]]
#		then
#			sacctmgr --immediate modify user name=$user set defaultaccount=$project
#		fi
	done
fi
