# Phase 0 — Solver spike

Este directorio contiene el spike reproducible de la Fase 0 del
[blueprint](../../docs/antennadesk-development-blueprint.md). Su objetivo es
demostrar que un motor NEC-2 puede integrarse, ejecutarse y validarse en Linux
y Windows antes de comprometer la arquitectura de AntennaDesk.

## Resultado corto

- Motor recomendado para el MVP: **nec2c 1.3.3** como **proceso externo**.
- Fuente fijada: commit `55be1e0e3fe5ee9dad4ce6050711450d19c562fd` de
  [`KJ7LNW/nec2c`](https://github.com/KJ7LNW/nec2c).
- Licencia: el `nec2c` original es de dominio público; el fork declara
  GPL-3.0. AntennaDesk es GPL-3.0-or-later, por lo que es compatible.
- Se reproduce el valor impreso del **NEC-2 User's Guide, Ejemplo 1**
  (`82.6979 + j46.3060 Ω` a 299.8 MHz) con diferencia menor a `0.001 Ω`.
- Se reproducen los ejemplos de suelo perfecto y finito del **Ejemplo 3**
  con diferencia menor a `0.01 Ω`.
- El binario Windows x86-64 se compiló y ejecutó correctamente; los 19 checks
  pasan también a través del binario PE (probado con Wine en Linux).

La decisión y sus consecuencias están en
[`docs/ADR/0001-solver-selection.md`](../../docs/ADR/0001-solver-selection.md).
La comparación completa está en
[`docs/spikes/phase0-solver-evaluation.md`](../../docs/spikes/phase0-solver-evaluation.md).

## Estructura

```text
spikes/phase0/
├── cases/       # Decks NEC de entrada
├── expected/    # Valores publicados y tolerancias
├── patches/     # Parche de portabilidad Windows para nec2c
├── scripts/     # Build, ejecución y parseo
├── .cache/      # Fuente descargada (ignorada por git)
└── build/       # Binarios compilados (ignorados por git)
```

## Requisitos

- Linux/macOS: `bash`, `curl`, `sha256sum`, compilador C (`cc`/`gcc`), Python 3.11+.
- Windows nativo con MSYS2/MinGW64: `gcc`, `make`, `patch`, `curl`, Python.
- Alternativa de cross-build desde Linux: `zig` o `x86_64-w64-mingw32-gcc`.

No se necesita Fortran ni NumPy/SciPy para este spike.

## Reproducir en Linux

```bash
bash spikes/phase0/scripts/build_nec2c.sh
python3 spikes/phase0/scripts/run_reference.py --nec2c spikes/phase0/build/nec2c
```

Salida esperada: `19/19 checks passed`.

## Reproducir en Windows

En MSYS2/MinGW64:

```bash
bash spikes/phase0/scripts/build_nec2c_windows.sh
python spikes/phase0/scripts/run_reference.py --nec2c spikes/phase0/build/nec2c.exe
```

Cross-build desde Linux con Zig:

```bash
CC="zig cc -target x86_64-windows-gnu" \
  bash spikes/phase0/scripts/build_nec2c_windows.sh
```

El `.exe` resultante es un PE32+ x86-64. En Linux se puede ejecutar con Wine
para una verificación adicional; la validación nativa se ejecutó en GitHub
Actions (`.github/workflows/solver-spike.yml`): Linux y Windows, `19/19` checks.

## Casos de referencia

Los valores esperados se transcribieron del **NEC-2 User's Guide, Part III**
(Burke y Poggio), no se generaron con nec2c:

| Caso | Frecuencia | Valor esperado | Fuente |
|---|---:|---:|---|
| `nec2_manual_example1` | 299.8 MHz | `82.6979 + j46.3060 Ω` | Ejemplo 1, espacio libre |
| `nec2_manual_example3_perfect` | 30 MHz | `106.437 + j9.90578 Ω` | Ejemplo 3, suelo perfecto |
| `nec2_manual_example3_finite` | 30 MHz | `111.117 + j11.0075 Ω` | Ejemplo 3, suelo finito (`εr=6`, `σ=1e-3 S/m`) |
| `scaled_example1_7mhz` | 7.1 MHz | mismo que Ejemplo 1, tolerancia `0.1 Ω` | Escalado en frecuencia |

Tolerancia global: `0.05 Ω` absolutos por componente. El caso escalado usa
`0.1 Ω` por el redondeo de coordenadas y radio.

El caso `dipole_sweep_pattern` no tiene referencia numérica independiente: se
usa como smoke test de 21 frecuencias, 21 cortes de patrón y 21 secciones de
corrientes.

## Hallazgos relevantes

1. **Salida suficiente:** nec2c entrega impedancia de entrada, corrientes por
   segmento, presupuesto de potencia y patrón de campo lejano en texto estable.
2. **Rendimiento:** el barrido de 21 frecuencias con patrón y corrientes se
   ejecutó en aproximadamente 6 ms en el equipo de prueba.
3. **Portabilidad Windows:** nec2c usa `getopt`, `sigaction`, `times()` y
   `sys/times.h`; el parche de `patches/nec2c-windows.patch` reemplaza esas
   dependencias. Es pequeño y mantenible, pero debe reaplicarse al actualizar
   la versión.
4. **Nombres de archivo:** nec2c limita el nombre de entrada a ~80 caracteres.
   El adaptador debe ejecutar en un directorio de trabajo corto y usar nombres
   relativos, no rutas absolutas largas.
5. **Formato de texto:** es estable dentro de una versión, pero no es un
   contrato formal. Hay que fijar la versión del motor y cubrir el parser con
   fixtures.
6. **Diferencias entre motores:** `nec2c` y `nec2++` coinciden dentro de
   ~0.02 % en los casos probados. No son bit-a-bit idénticos.

## Limitaciones de este spike

- No se probó una instalación limpia de Windows sin MSYS2; eso queda para el
  pipeline de empaquetado.
- No se validaron aún antenas con cargas, redes, radiales ni geometrías
  complejas.
- No se implementó cancelación, límites de tiempo ni captura de stderr en un
  adaptador de producción.
- Los valores de referencia cubren solo dos ejemplos del manual y un caso
  escalado. La validación científica completa pertenece a la Fase 2.

## Próximos pasos

1. Aprobar el ADR y fijar `nec2c` como motor del MVP.
2. Pasar a Fase 1 (dominio, persistencia, tooling) sin introducir GUI todavía.
3. En Fase 2, convertir estos scripts en el adaptador real, con parser probado,
   cancelación, logs y casos de regresión numérica.
