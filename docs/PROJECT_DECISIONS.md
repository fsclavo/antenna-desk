# Decisiones de proyecto confirmadas

**Fecha:** 2026-10-28  
**Responsable:** Fernando Sclavo  
**Estado:** decisiones iniciales confirmadas para arrancar el proyecto

Este registro conserva las respuestas dadas antes de la Fase 0. No sustituye
a los ADR: cuando una decisión tenga alternativas técnicas y consecuencias
arquitectónicas, se documentará en `docs/ADR/`.

## Licencia y propiedad

- Licencia del proyecto: **GPL-3.0-or-later**.
- Copyright: **2026 Fernando Sclavo**.
- Cabeceras SPDX breves en archivos fuente.
- Documentación bajo la misma licencia GPL-3.0-or-later.
- Distribución de binarios con fuentes y scripts de empaquetado.
- Contribuciones con **DCO** (`Signed-off-by`), sin CLA.
- Dependencias permitidas: solo licencias compatibles con GPLv3 (MIT, BSD,
  Apache-2.0, LGPLv3, GPLv3); nada propietario ni GPLv2-only.

## Motor y validación

- Motor del MVP: **nec2c 1.3.3** como proceso externo, con versión fijada por
  commit y parche Windows mantenido. Ver `docs/ADR/0001-solver-selection.md`.
- Alternativa de contraste: **NEC2++/PyNEC**, no como dependencia de runtime.
- **xnec2c** se usa solo como referencia técnica y de UX.
- Fuentes independientes disponibles: samples de **MMANA-GAL** y el
  **ARRL Antenna Book**; se usarán para ampliar la validación en Fase 2.

## Plataformas y entorno

- Linux y Windows.
- Validación local en Linux; Windows en GitHub Actions.
- Python `>=3.11`; CI con matriz 3.11–3.13.
- Entorno y dependencias con `uv` + `uv.lock`.
- CI en GitHub Actions desde el inicio.

## Arquitectura y dominio

- Arquitectura hexagonal / ports and adapters.
- Dominio sin PySide6, SciPy ni bibliotecas concretas del solver.
- Persistencia: **dataclasses** en dominio; **Pydantic v2** solo en el borde de
  persistencia/validación de esquema.
- Convención geométrica interna: ejes derecho, **Z arriba**, azimut desde el
  Norte, elevación sobre el horizonte; mapeo explícito a theta/phi de NEC.
- Unidades: **métrico e imperial seleccionable en preferencias**; el dominio
  usa unidades canónicas (metros, Hz, ohmios).
- Paquete Python: `antennadesk`.
- Formato de proyecto: `.antennadesk` (JSON versionado).
- Bandas: **HF, VHF y UHF desde el inicio**, sin prometer precisión fuera del
  modelo admitido por el motor.

## Producto y UX

- UI en **español e inglés**; identificadores y código en inglés.
- Documentación en español.
- i18n con `tr()` desde el inicio.
- Local-first, sin cuentas, nube ni telemetría obligatoria.

## Calidad y flujo de trabajo

- `mypy` estricto en dominio y aplicación.
- `Ruff` para lint/format.
- `pytest` para unitarias, integración y aceptación.
- Cobertura como señal auxiliar, no como prueba de validez electromagnética.
- Ramas cortas + pull request.
- **Conventional Commits**.
- Fase 0 antes de la GUI; no scaffoldear todo el roadmap.

## Próximas decisiones que requerirán ADR

- Arquitectura y límites definitivos.
- Unidades y convenciones angulares (implementación concreta).
- Formato de proyecto y migraciones.
- Ejecución/cancelación de simulaciones.
- Estrategia de visualización 3D.
- Formatos de importación/exportación.
- Empaquetado Linux/Windows.
