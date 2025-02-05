[
    [
        # Filtering non-cluster users
        . | to_entries[] | select(.value.projets | any((.loginnames | .[$cluster_name].login) or (.loginnames | .[$cluster_name].nom != "nologin"))) |

        # Converting users object to users list by putting the email inside the users objects
        .value + { "email": .key } |

        # Filtering non-cluster projects
        . + { "projets":
        ([
            .projets | to_entries[] | select((.value | (has("active") and (.active.deleted | not))) and ((.value.loginnames | .[$cluster_name].login) or (.value.loginnames | .[$cluster_name].nom != "nologin"))) |
            (.value.loginnames | .[$cluster_name]) + { "projectname": .key }
        ]) } |

        # Filtering users without projects
        select(.projets | any)
    ] |

    # Combining users list (from input) and sshkeys list (from variable)
    . + [$sshkeys | group_by(.idindividu) | .[] | { "idIndividu": .[0].idindividu, "sshkeys": . }] |
        group_by(.idIndividu) | .[] | add | select(has("email")) |

    # Formatting the actual users objects
    {
        "portal": "mesonet",
        "email": .email,
        "id": .idIndividu,
        "username": (.projets | map(select(.nom != "nologin")) | if has(0) then .[0].nom else "nologin" end),
        "preferred": null,
	"password": null,
        "report": (.projets | any(.login and .nom == "nologin")),
        "delete": (.projets | any(.login | not)),
        "projects":
        ([
            .projets[] |
		{
			"id": null,
			"name": .projectname,
			"report": (.login and .nom == "nologin")
		}
        ]),
        "sshkeys":
        ([
            .sshkeys[]? |
            # Must filter non-cluster users in ssh keys user lists
            . + { "users": [.users[] | select(.loginname | endswith("@" + $cluster_name))] } |
            {
                "name": .nom,
                "id": .idCle,
                # Key must be considered revoked if not associated with the cluster
                "rvk": (.rvk or .users == []),
                "report": (.users | any(.deploy | not)),
                "pub": .pub
            }
        ])
    }
]
