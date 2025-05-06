Client de synchronisation des utilisateurs avec le portail Gramc pour Mesonet
=============================================================================

**ATTENTION :** Ce projet est techniquement utilisable en modifiant certains fichiers, mais est toujours un travail en cours et non utilisable sans modification.

**ATTENTION :** Cette dernière version ajoute un filtrage des « logins préférés ». Si vous les utilisez, penser à modifier la ligne 148 du fichier `roles/retreive_portals_data/library/format_and_filter_users.py` pour l'adapter à vos besoins.

Description
-----------

Ce client de synchronisation est un ensemble de scripts construits autour de Ansible. Il est utilisé pour automatiquement synchroniser les utilisateurs, leurs clés ssh et leurs projets depuis le portail Gramc vers un cluster local. Les projets sont synchronisés en tant que groupes locals au serveur et en tant qu'account Slurm.

- Par défaut, la portée des uid gérés par ce client va de 100000 à 199999
- Par défaut, la portée des gid gérés par ce client va de 200000 à 299999
- Le nom de compte des nouveaux utilisateurs sont générés par son adresse courriel, en prenant au moins deux caractères du prénom suivi du nom, et en complétant en prenant d'autres caractères du prénom ou en ajoutant des 0 pour atteindre 8 caractères
    - Pour changer ce comportement, il faut changer la fonction `get_new_username` du fichier `roles/retreive_portals_data/library/format_and_filter_users.py`
- Ce client garde une association des uid locaux avec les id des portails distants, par défaut dans le fichier `./local/usersdata.csv`
- Les utilisateurs sans projet actifs sont bloqués via les valeurs du fichier `/etc/shadow` et leurs fichier `authorized_keys` est changé en `authorized_keys.locked` pour empêcher la connexion
- **IMPORTANT :** Le script risque de ne pas arriver à son terme si un ou plusieurs nœuds sont injoignables ou bloquants
    - Pour contourner ce problème, il faut préciser l'option `--limit='localhost:all:!nœudbloqué1'` (pour plusieurs nœuds : `localhost:all:!nœudbloqué1:!nœudbloqué2'`, remplacer `nœudbloquéX` par les nœuds injoignables) pour que le script ne tente pas de déployer les utilisateurs dessus
    - Après avoir utilisé le script en ignorant des nœuds, il peut être nécessaire de le relancer après avoir supprimé les fichiers `./local/users_hashes.csv` et `./local/projects_hashes.csv` (des variables `already_deployed_users_file` et `already_deployed_projects_file` du playbook principal), pour qu'il fasse un redéploiement complet (Suivant le nombre d'utilisateurs, cela peut prendre beaucoup de temps)
- **IMPORTANT :** Ce client défini précisémment les groupes des utilisateurs gérés, **ils sont donc automatiquement retirés de tout autre groupe**
    - Pour changer ce comportement, mettre la variable `no_remove_from_groups` dans `gramc_synchro_client.ansible.yaml` à `true`, il faudra alors retirer manuellement des groupes les utilisateurs qui ne sont plus dans les projets

Dépendances et contraintes
--------------------------

- jq
- awk
- Ansible, avec les modules « Community »
- Python avec les modules json, subprocess and requests
- Le nœud lançant ce client doit pouvoir se connecter en root par une clé sans mot de passe (ou par un compte sudo sans mot de passe en utilisant --become)
- Le nœud lançant ce client doit avoir accès au stockage partagé où sont présents les dossiers des utilisateurs et les dossiers des projets
- Le nœud lançant ce client doit être l'un des nœuds gérés par ce client (notamment pour qu'il puisse récupérer le uid d'un utilisateur et le gid d'un groupe/projet via la commande `id`)
- Le playbook `gramc_synchro_client.ansible.yaml` doit être lancé avec `ansible_playbook` **dans le dossier de ce client, où se trouve le fichier `gramc_synchro_client.ansible.yaml`**
- Lors de l'exécution du client par le script `gramc_synchro_client.sh`, si l'exécution se retrouve bloquée et que le script est relancé, il ne relancera pas le playbook

Installation
------------

1. Clonez le dépôt (Il est conseillé de cloner l'une des versions released, plus stables)
2. Configurez la liste des nœuds dans l'inventaire
3. Configurez les variables de `gramc_synchro_client.ansible.yaml` pour les adapter à votre cluster
    1. Notamment, mettre le bon nom du cluster correspondant à celui dans la base de données de gramc
4. Adapter les rôles à votre cas d'utilisation, par exemple changer comment les dossiers des projets sont générés dans `roles/users_folders/tasks/main.yaml`
5. Vérifier que la liste d'utilisateurs récupérée est correcte avec les tags `all_portals,debug_filtered`
6. Lancer la recette ansible pour vérifier son bon fonctionnement
7. Éventuellement :
    1. Modifier le contenu de `gramc_synchro_client.sh` pour l'adapter à votre cluster
    2. Ajouter `gramc_synchro_client.sh` au cron

Ce que ce client fait
---------------------

1. Ce client commence par récupérer les données des portails, seuls certains fichiers dans le dossier du client de synchronisation sont modifiés
    1. Les uid et gid sont associés aux ids des utilisateurs des portails pendant cette étape mais aucun groupe ni utilisateur n'est créé sur le cluster
2. Ce client se connecte sur chaque nœud pour y créer les utilisateurs et les groupes correspondant aux projets, et les associe, mais ne crée aucun dossier
3. Ce client crée les dossiers utilisateurs et les dossiers des projets dans les dossiers indiqués
    1. Les dossiers des utilisateurs sont remplis avec le contenu de `/etc/skel`
    2. Ce client crée automatiquement les clés ssh pour que l'utilisateur puisse se connecter entre les nœuds du cluster
    3. Ce client ajoute automatiquement les clés ssh publiques du portail dans `.ssh/authorized_keys` et en retire les clés révoquées
4. Ce client crée les utilisateurs et projets dans la base de données Slurm
    1. **BUG À CORRIGER :** Ce client ne retire pas les associations Slurm utilisateur/account qui ne sont plus dans le projet correspondant
        1. Pour une correction temporaire, modifier le fichier `roles/populate_slurm/files/set_slurm_user.sh`
5. Ce client envoie finalement les confirmations de créations aux portails

Déboguage
---------

- Il est possible de lancer la recette ansible avec les tags `all_portals,debug_retreive`, `all_portals,debug_formated` ou `all_portals, debug_filtered` pour récupérer la liste des utilisateurs et de leurs clés et projets dans un fichier sous le dossier `local/`, afin de vérifier la liste des utilisateurs utilisée par la recette ansible
    - L'utilisation de ces tags arrête le script avant la propagation des utilisateurs (mais peut modifier `local/usersdata.csv` en cas de nouvel utilisateur)

Configuration optionnelle mais recommandée
------------------------------------------

- Configure Ansible to run the playbook faster, for example in "ansible.cfg" in "\[ssh\_connection\]" section:
  - Enable pipelining with "pipelining=True"
  - Enable ssh persistance with "ssh\_args=-o ControlMaster=yes -o ControlPersist=60s"

Trucs & astuces (non testés)
----------------------------

You can run the "gramc\_synchro\_client.py" script with some environment variables to have a custom "ansible.cfg" file and a custom ".netrc" file

- Custom ansible configuration file: "ANSIBLE\_CONFIG=$custom\_path"
  - See [https://docs.ansible.com/ansible/latest/cli/ansible-playbook.html#environment]
- Custom .netrc file: "NETRC=$custom\_path"
  - See [https://docs.python-requests.org/en/latest/user/quickstart/#custom-headers]

Ajouter un autre portail
------------------------

1. Créer un nouveau module dans le rôle `retreive_portals_data` renvoyant la liste des utilisateurs associés à leurs projets et clés correctement formatée
2. Ajouter au fichier `roles/retreive_portals_data/tasks/main.yaml` les tâches nécessaires pour récupérer la liste, et modifier la tâche `filter_and_format_data` pour l'y ajouter

Gestion des utilisateurs via le LDAP
------------------------------------

Il est possible de créer les utilisateurs et groupes représentant les projets sur un LDAP plutôt que directement sur chaque nœud. Pour cela, il faut décommenter le bloc responsable de la création des utilisateurs et groupes sur le LDAP et commenter le play créant les utilisateurs sur les nœuds, puis configurer les variables utilisées par le rôle faisant les créations sur le LDAP. Il est possible de changer les fichiers du rôle pour personnaliser les détails de la création des utilisateurs et groupes sur le LDAP.

À faire
-------

- Corriger le retrait des associations Slurm
- Corriger l'appel aux scripts non-python pour qu'ils puissent être appelés de n'importe où
- Rendre plus robuste la récupération des uid et gid sur le cluster
    - Faire un nouveau play pour récupérer les uid/gid sur les nœuds ?

