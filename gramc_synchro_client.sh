#!/usr/bin/bash

cd /root/scripts.git/sync_users/ &&
	(
	flock --nonblock 9 &&
	thisdate=$(date +%FT%HH%M) &&
	ansible-playbook --limit 'localhost:all:!juliet3' gramc_synchro_client.ansible.yaml >"local/log/${thisdate}.out" 2>"local/log/${thisdate}.err"
	) 9>./gramc_synchro_client.lock
