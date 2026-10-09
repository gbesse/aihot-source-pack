# AIHOT Source Pack

**Inicie una instancia AIHOT con fuentes públicas inspeccionables e importables.**

[English](README.md) · [Français](README.fr.md) · [Español](README.es.md)

## Proyectos relacionados

- [AIHOT](https://github.com/KKKKhazix/AIHOT) — Importa ese formato JSON al iniciarse por primera vez; este paquete es independiente.
- [Source request #13](https://github.com/KKKKhazix/AIHOT/issues/13) — Solicita fuentes útiles además de la lista de demostración.
- [AIHOT source format](https://github.com/KKKKhazix/AIHOT/blob/main/industry/sources.json) — Esquema de ejemplo que respeta el exportador.

Estos enlaces describen proyectos relacionados, sin afiliación.

Ejecute `python3 source_pack.py preview --topic memory` para ver los identificadores, temas y URL Atom exactas antes de exportar. La vista previa solo lee el manifiesto incluido, sin solicitudes de red.

## Probar

```sh
python3 source_pack.py validate --lang es
```

## Qué comprueba esta herramienta

Exporta diez feeds Atom oficiales de versiones GitHub en el formato `industry/sources.json` de AIHOT. Filtra por `agents`, `memory`, `retrieval` o `protocols`; `check-live` comprueba TLS y XML.

## Usar con sus datos

```sh
python3 source_pack.py export --topic memory > sources.generated.json
python3 source_pack.py check-live --topic memory
```

Revise `sources.generated.json`, combine las entradas deseadas en `industry/sources.json` de una instancia nueva y ejecute el proceso de carga de AIHOT. Se verificó el formato, pero no la importación en una instancia activa.

## Alcance y límites

Solo diez feeds de versiones GitHub. No es la lista privada de producción de AIHOT. La disponibilidad cambia; `check-live` es una verificación puntual. No se copian artículos.

## Pruebas

```sh
python3 -m unittest discover -s tests -v
```

MIT · v0.1.2

## Varios temas

Una fuente puede declarar varios temas en `sources.json`; `export` los conserva todos en los `tags` de AIHOT. Ejecute `python3 source_pack.py export` para revisar el JSON sin conexión.

## Comprobación de adopción

[Pruebe un caso concreto y compruebe sus límites](examples/adoption-check.md).
