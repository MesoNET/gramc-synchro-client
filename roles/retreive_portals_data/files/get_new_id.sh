#!/usr/bin/bash

if [[ "$1" == "" || "$2" == "" || "$1" == "-h" || "$1" == "--help" ]]
then
    echo 'Checks all ids between MINID and MAXID, then prints a new free id.'
    exit 1
fi

min_id=$(($1 - 1))
max_id=$2

id=$({
    cat /etc/passwd /etc/group |
        awk 'BEGIN {a='$min_id'} {if (a < $3 && $3 <= '$max_id') {a=$3}} END {print a}' FS=: |
        sort --numeric-sort --reverse |
        head -n1
} | sort --numeric-sort --reverse | head -n1)
id=$((id + 1))
if [[ "$id" -gt "$max_id" ]]
then
    echo 'ERROR: Max id reached' >&2
    exit $1
fi
echo $id
