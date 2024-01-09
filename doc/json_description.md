Structures json des données reçues et utilisées
===============================================

GramC
-----

### Utilisateurs

```
{
	(email): {
		"nom" : str,
		"prenom" : str,
		"idIndividu": int,
		"projets" : {
			(nom_projet) : {
				"loginnames" : {
					"BOREALE": {...},
					"Juliet": {
						"nom": str,
						"login": bool,
						"clessh": {
							"idCle": int,
							"nom": str,
							"pub": str,
							"rvk": bool,
							"deploy": bool
						},
						"userid": int
					},
					"TURPAN": {...}
				},
				"derniere": {...+"version": str, "deleted": bool},
				"active": {...+"version": str, "deleted": bool}
			}
		}
	}
}
```

### Clés ssh

```
[
	{
		"idCle": 1,
		"nom": str,
		"pub": str,
		"rvk": bool,
		"idindividu": int,
		"empreinte": str,
		"users": [{
			"individu": str,
			"idIndividu": int,
			"mail": str,
			"loginname": str, # "loginname@server"
			"deploy": bool,
			"projet": str
		}]
	}
}
```

### 

Local intermédiaire
-------------------

```
{
	"email": str,
	"username": str,
	"preffered": str,
	"id": int,
	"report": bool,
	"delete": bool,
	"sshkeys": [{
		"name": str,
		"id": int,
		"pub": str,
		"rvk": bool,
		"report": bool
	}],
	"projects": [{
		"id": int,
		"name": str
	}]
}
```

Local ansible
-------------

```
{
	"users": [{
		"email": str,
		"username": str,
		"preffered": str,
		"uid": int,
		"id": int,
		"report": bool,
		"delete": bool,
		"sshkeys": [{
			"name": str,
			"id": int,
			"pub": str,
			"rvk": bool,
			"report": bool
		}],
		"projects": [{
			"id": int,
			"name": str
		}]
	}],
	"projects": [{
		"name": str,
		"id": int,
		"gid": int,
		"usernames": [ str ]
	}]
}
```
