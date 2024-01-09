#!/usr/bin/bash

if [[ "$1" == "" || "$2" == "" || "$1" == "-h" || "$1" == "--help" ]]
then
    echo 'Checks all ids between MINID and MAXID comprized on all juliet[0-4] servers and on LDAP, then prints a new free id.'
    exit 1
fi

min_id=$(($1 - 1))
max_id=$2

id=$({
    ldapsearch -x "(objectClass=posixAccount)" uidNumber |
        grep -E '^uidNumber: ' |
        sed 's/^uidNumber: //' |
        awk '{if ('$min_id' < $1 && $1 <= '$max_id') {print}}' |
        sort --numeric-sort --reverse |
        head -n1
    ldapsearch -x "(objectClass=posixGroup)" gidNumber |
        grep -E '^gidNumber: ' |
        sed 's/^gidNumber: //' |
        awk '{if ('$min_id' < $1 && $1 <= '$max_id') {print}}' |
        sort --numeric-sort --reverse |
        head -n1
    clush -Nqw juliet[1-4] '
        cat /etc/passwd /etc/group |
        awk '"'"'BEGIN {a='$min_id'} {if (a < $3 && $3 <= '$max_id') {a=$3}} END {print a}'"'"' FS=: |
        sort --numeric-sort --reverse |
        head -n1'
} | sort --numeric-sort --reverse | head -n1)
id=$((id + 1))
if [[ "$id" -gt "$max_id" ]]
then
    echo 'ERROR: Max id reached' >&2
    exit $1
fi
echo $id
