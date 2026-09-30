# AIHOT Source Pack

**Démarrez une instance AIHOT avec des flux publics inspectables et importables.**

[English](README.md) · [Français](README.fr.md) · [Español](README.es.md)

## Projets voisins

- [AIHOT](https://github.com/KKKKhazix/AIHOT) — Importe ce format JSON au premier démarrage ; ce pack est indépendant.
- [Source request #13](https://github.com/KKKKhazix/AIHOT/issues/13) — Demande des sources utilisables au-delà de la liste de démonstration.
- [AIHOT source format](https://github.com/KKKKhazix/AIHOT/blob/main/industry/sources.json) — Schéma d’exemple exact que l’export respecte.

Ces liens décrivent des projets voisins, sans affiliation.

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

MIT · v0.1.0-alpha.1
