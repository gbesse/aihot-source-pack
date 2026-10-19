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

MIT · v0.3.1

## Varios temas

Una fuente puede declarar varios temas en `sources.json`; `export` los conserva todos en los `tags` de AIHOT. Ejecute `python3 source_pack.py export` para revisar el JSON sin conexión.

## Comprobación de adopción

[Pruebe un caso concreto y compruebe sus límites](examples/adoption-check.md).

## Comprobaciones de fuentes inspeccionables

`python3 source_pack.py check-live --topic memory --json --lang es` genera un recibo por fuente: fecha de observación, validación exacta del espacio de nombres Atom, número de entradas y SHA256 de los bytes recibidos. Una fuente vacía sigue siendo válida con cero entradas. El hash identifica la captura; no es firma, prueba de calidad de versiones ni adopción humana. Rechaza XML con un sufijo engañoso `*feed`. Solicitudes y redirecciones requieren HTTPS. Los fallos contienen códigos genéricos sin stderr del transporte. Campos de texto estrictos evitan también fallos con manifiestos incorrectos.


Exporte un archivo completo sin sobrescribir configuración: `python3 source_pack.py export --topic memory --lang es --output sources-export.json`. El archivo UTF8 se publica en un paso con permisos 600; un destino existente o no disponible falla con código 2 sin cambiarlo. Sin `--output` se conserva la salida estándar. La opción solo pertenece a `export` y no realiza importación remota.

## Un flujo válido no implica actividad reciente

`check-live --max-age-days 90` añade una política de edad de entradas Atom. Por defecto `--timestamp-field updated` mide modificaciones, no necesariamente publicaciones nuevas; elegir `published` para exigir ese campo sin alternativa silenciosa. Distingue reciente, antiguo, fecha desconocida, flujo vacío y fecha futura incoherente. Las fechas necesitan zona; la fecha global del flujo nunca sustituye las de entradas. Fechas más de cinco minutos futuras fallan. XML válido que incumple la política sale con 1. Sin límite de edad conserva la validación estructural anterior. Las fechas declaradas por el editor no prueban calidad ni adopción humana.

```sh
python3 source_pack.py check-live --topic memory --max-age-days 90 --timestamp-field updated --lang es --json
python3 examples/feed-freshness.py
```

El segundo comando compara una publicación antigua editada recientemente con flujo y reloj sintéticos sin red. Las pruebas nuevas no hacen peticiones remotas.
