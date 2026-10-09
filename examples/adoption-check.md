# aihot-source-pack — contrôle d’adoption · adoption check · comprobación de adopción

## Français

Point de départ local, après la préparation indiquée dans le README :

```sh
python3 source_pack.py preview --topic protocols
```

Avant un import AIHOT, vérifiez les identifiants et URL Atom des flux de protocoles. Une URL inattendue se corrige dans le manifeste avant export ; l’aperçu ne contacte aucun serveur.

## English

Local starting point, after the setup described in the README:

```sh
python3 source_pack.py preview --topic protocols
```

Before an AIHOT import, inspect the IDs and Atom URLs of protocol feeds. Correct an unexpected URL in the manifest before export; preview makes no network request.

## Español

Punto de partida local, después de la preparación descrita en el README:

```sh
python3 source_pack.py preview --topic protocols
```

Antes de importar en AIHOT, revise los ID y las URL Atom de los feeds de protocolos. Corrija una URL inesperada en el manifiesto antes de exportar; la vista previa no usa la red.
## Variante synthétique · Synthetic variation · Variante sintética

```text
topic=protocols; inspect=[id,atom_url]
```

FR : adaptez une copie de la fixture locale à cette situation, puis vérifiez le comportement décrit ci-dessus. Les valeurs sont illustratives, pas des résultats Jev mesurés.

EN: adapt a copy of the local fixture to this situation, then check the behavior described above. Values are illustrative, not measured Jev output.

ES: adapte una copia de la fixture local a esta situación y compruebe el comportamiento descrito arriba. Los valores son ilustrativos, no resultados Jev medidos.
