#!/usr/bin/bash

cd ${GRAMC_SYNCHRO_CLIENT_DIR} &&
	(
	flock --nonblock 9 &&
	thisdate=$(date +%FT%HH%M) &&
	ansible-playbook gramc_synchro_client.ansible.yaml >"local/log/${thisdate}.out" 2>"local/log/${thisdate}.err"
	) 9>./gramc_synchro_client.lock
