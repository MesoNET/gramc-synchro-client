#!/usr/bin/python3

import json
import subprocess
import requests
import re


def get_consomation(account):
    # Faire ce qu'il faut pour retourner la valeur de la consomation pour le projet concerné
    return conso


def do_value(account, value):
    # Faire ce qu'il faut avec la valeur retournée par le portail pour le projet concerné
    dosomething = value

def main():
    # Partie 1 : Récupérer les valeurs attribuées aux projets
    changes_to_do = requests.get(
            'https://acces.mesonet.fr/gramc-meso/adminux/todo/get'
        ).json()
    for attribution in changes_to_do:
        value = attribution['attribution']
        project = attribution['idProjet']
        id_rallonge = attribution['idRallonge'] if 'idRallonge' in attribution else attribution['idProjet']
        # Faire ce qu'il y a à faire avec les valeurs attribuées au projet
        do_value(projet, value)
        # Sauvegarder le changement d'attribution au projet pour garder une trace
        with open('gramc_attributions.csv', 'a') as f:
            f.write('{}:{}:{}\n'.format(project, id_rallonge, value))
        # Confirmer la bonne réception du changement d'attribution
        r = requests.post(
            'https://acces.mesonet.fr/gramc-meso/adminux/todo/done',
            data=json.dumps(
                {
                    "projet": project,
                    "ressource": "MaRessource"
                }),
            headers={'content-type': 'application/json'}
        )
        print('Sent confirmation for consommation quota of project {}.'.format(project))

    # Partie 2 : Renvoyer au portail les consommations des projets
    with open('gramc_attributions.csv', 'r') as f:
        lines = f.readlines()
    for line in lines:
        values = line.split(':')
        project = values[0]
        if project == values[1]:
            # Récupérer la consommation du projet
            conso = get_consomation(project)
            # Renvoyer la consommation du projet pour la ressource concernée
            r = requests.post(
                'https://acces.mesonet.fr/gramc-meso/adminux/projet/setconso',
                data=json.dumps(
                    {
                        "projet": project,
                        "ressource": "MaRessource",
                        "conso": conso
                    }),
                headers={'content-type': 'application/json'}
            )
            print('Sent {} gpu hours for the project {}.'.format(gpu_hours, project))


if __name__ == "__main__":
    main()
