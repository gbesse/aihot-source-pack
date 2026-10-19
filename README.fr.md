# AIHOT Source Pack

**Démarrez une instance AIHOT avec des flux publics inspectables et importables.**

[English](README.md) · [Français](README.fr.md) · [Español](README.es.md)

## Projets voisins

- [AIHOT](https://github.com/KKKKhazix/AIHOT) — Importe ce format JSON au premier démarrage ; ce pack est indépendant.
- [Source request #13](https://github.com/KKKKhazix/AIHOT/issues/13) — Demande des sources utilisables au-delà de la liste de démonstration.
- [AIHOT source format](https://github.com/KKKKhazix/AIHOT/blob/main/industry/sources.json) — Schéma d’exemple exact que l’export respecte.

Ces liens décrivent des projets voisins, sans affiliation.

Exécutez `python3 source_pack.py preview --topic memory` pour voir les identifiants, thèmes et URL Atom exactes avant export. L’aperçu lit uniquement le manifeste fourni, sans requête réseau.

## Essayer

```sh
python3 source_pack.py validate --lang fr
```

## Ce que cet outil vérifie

Exporte dix flux Atom officiels de releases GitHub au format `industry/sources.json` d’AIHOT. Filtrage par `agents`, `memory`, `retrieval` ou `protocols` ; `check-live` vérifie TLS et XML.

## Utiliser avec vos données

```sh
python3 source_pack.py export --topic memory > sources.generated.json
python3 source_pack.py check-live --topic memory
```

Relisez `sources.generated.json`, fusionnez les entrées souhaitées dans `industry/sources.json` d’une nouvelle instance, puis lancez le seed AIHOT. Le format a été vérifié, pas l’import dans une instance AIHOT démarrée.

## Périmètre et limites

Dix flux de releases GitHub uniquement. Il ne s’agit pas des sources privées de production d’AIHOT. La disponibilité change ; `check-live` est ponctuel. Aucun article n’est copié.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

MIT · v0.3.1

## Plusieurs thèmes

Une source peut déclarer plusieurs thèmes dans `sources.json` ; `export` les conserve tous dans les `tags` AIHOT. Exécutez `python3 source_pack.py export` pour examiner le JSON hors ligne.

## Contrôle d’adoption

[Essayer un cas concret et vérifier ses limites](examples/adoption-check.md).

## Contrôles de flux inspectables

`python3 source_pack.py check-live --topic memory --json --lang fr` produit un reçu par flux : date d’observation, validation exacte de l’espace de noms Atom, nombre d’entrées et SHA256 des octets reçus. Un flux vide reste valide avec zéro entrée. Le hash identifie cette capture ; il ne constitue ni signature, ni preuve de qualité des releases, ni adoption humaine. Un XML dont le suffixe `*feed` trompeur ressemble à Atom est refusé. La requête et ses redirections exigent HTTPS. Les échecs utilisent des codes génériques sans stderr du transport. Des champs textuels stricts évitent aussi les plantages sur manifestes mal formés.


Exportez un fichier complet sans écraser une configuration existante : `python3 source_pack.py export --topic memory --lang fr --output sources-export.json`. Le fichier UTF-8 est publié en une seule étape avec permissions 600 ; une destination existante ou indisponible échoue avec le code 2 et reste inchangée. Sans `--output`, la sortie standard historique reste disponible. Cette option appartient uniquement à `export` et n’effectue aucun import distant.

## Flux valide ne signifie pas activité récente

`check-live --max-age-days 90` ajoute une politique d’âge sur les entrées Atom. Par défaut `--timestamp-field updated` mesure une activité de modification, pas nécessairement une nouvelle publication ; choisir `published` pour exiger cette date, sans repli silencieux. Le reçu distingue récent, ancien, date inconnue, flux vide et date future incohérente. Les dates doivent préciser leur fuseau ; la date globale du flux ne remplace jamais celles des entrées. Une date située plus de cinq minutes dans le futur échoue. Un flux XML valide mais ne satisfaisant pas la politique donne une sortie 1. Sans limite d’âge, la validation structurelle précédente reste identique. Les dates déclarées par l’éditeur ne prouvent ni qualité, ni adoption humaine.

```sh
python3 source_pack.py check-live --topic memory --max-age-days 90 --timestamp-field updated --lang fr --json
python3 examples/feed-freshness.py
```

La seconde commande compare hors ligne une publication ancienne modifiée récemment, avec une horloge et un flux synthétiques. Les nouveaux tests n’effectuent aucune requête distante.
