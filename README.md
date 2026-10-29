# AntennaDesk

Aplicación de escritorio para el diseño, simulación y construcción de antenas,
orientada a radioaficionados. Local-first, Linux y Windows, con motor
electromagnético NEC-2.

**Estado:** Fase 0 completada (selección y validación del motor). La GUI y el
modelo de dominio todavía no están implementados.

## Documentación

- [Blueprint de desarrollo](docs/antennadesk-development-blueprint.md)
- [Decisiones de proyecto confirmadas](docs/PROJECT_DECISIONS.md)
- [ADR-0001 — Motor del MVP](docs/ADR/0001-solver-selection.md)
- [Evaluación de motores NEC](docs/spikes/phase0-solver-evaluation.md)
- [Spike reproducible de Fase 0](spikes/phase0/README.md)

## Motor

El MVP usará **nec2c 1.3.3** como proceso externo, con versión fijada por
commit y un parche de portabilidad Windows. La validación reproduce los
ejemplos del NEC-2 User's Guide y se ejecuta en Linux y Windows (CI: 19/19).

## Reproducir el spike

```bash
bash spikes/phase0/scripts/build_nec2c.sh
python3 spikes/phase0/scripts/run_reference.py --nec2c spikes/phase0/build/nec2c
```

Resultado esperado: `19/19 checks passed`.

## Licencia

GPL-3.0-or-later. Ver [LICENSE](LICENSE).
