[
    (.[] |
        .projects[] + {"username": .username})?
] |
[
    group_by(.name)[] |
        .[0] + { "usernames": [(.[].username)] } | del(.username)
]

