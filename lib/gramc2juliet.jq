[
    [
        # Filtering non-juliet users
        . | to_entries[] | select(.value.projets | any(.loginnames.Juliet.login or .loginnames.Juliet.nom != "nologin")) |

        # Converting users object to users list by putting the email inside the users objects
        .value + { "email": .key } |

        # Filtering non-juliet projects
        . + { "projets":
        ([
            .projets | to_entries[] | select(.value.loginnames.Juliet.login or .value.loginnames.Juliet.nom != "nologin") |
            .value.loginnames.Juliet + { "projectname": .key }
        ]) }
    ] |

    # Combining users list (from input) and sshkeys list (from variable)
    . + [$sshkeys | group_by(.idindividu) | .[] | { "idIndividu": .[0].idindividu, "sshkeys": . }] |
        group_by(.idIndividu) | .[] | add | select(has("email")) |

    # Formatting the actual users objects
    {
        "email": .email,
        "id": .idIndividu,
        "username": .projets[0].nom,
        "preferred": null,
        "report": (.projets | any(.login and .nom == "nologin")),
        "delete": (.projets | any(.login | not)),
        "projects":
        ([
            .projets[] | { "id": null, "name": .projectname }
        ]),
        "sshkeys":
        ([
            .sshkeys[] |
            # Must filter non-juliet users in ssh keys user lists
            . + { "users": [.users[] | select(.loginname | endswith("@Juliet"))] } |
            {
                "name": .nom,
                "id": .idCle,
                # Key must be considered revoked if not associated with juliet
                "rvk": (.rvk or .users == []),
                "report": (.users | any(.deploy | not)),
                "pub": .pub
            }
        ])
    }
]
