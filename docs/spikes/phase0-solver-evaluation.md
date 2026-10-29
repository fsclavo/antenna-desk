# Fase 0 — Evaluación de motores NEC

**Fecha:** 2026-10-28  
**Estado:** spike completado, decisión aceptada (ADR-0001)  
**Alcance:** evaluar motores NEC-2 para el MVP de AntennaDesk en Linux y
Windows, con licencia compatible con GPL-3.0-or-later, integración como
proceso o biblioteca, portabilidad, resultados disponibles y coste de
empaquetado. No se evaluó la GUI ni el modelo de dominio.

## 1. Candidatos

| Candidato | Versión evaluada | Lenguaje | Licencia | Integración | Mantenimiento |
|---|---|---|---|---|---|
| **nec2c** (upstream 5B4AZ) | 1.3.1 | C | Dominio público | CLI / proceso | Autor retirado; código estable |
| **nec2c** (fork KJ7LNW) | 1.3.3 (`55be1e0`) | C | GPL-3.0 | CLI / proceso | Activo (2026) |
| **NEC2++ / necpp** | 2.3.4 | C++ | GPL-2.0-or-later | CLI, biblioteca C++, SWIG | Activo (2026) |
| **PyNEC** | 2.3.4 | Python + SWIG | GPL-2.0-or-later | Extensión Python in-process | Activo, pero sin wheels Windows |
| **xnec2c** | 4.4.12 | C + GTK | GPL-3.0 | Aplicación GUI | Activo; referencia de UX |
| **NEC-2 Fortran original** | 1981 | Fortran | Dominio público | CLI / proceso | Histórico; requiere gfortran |

No se evaluaron como motores 4nec2, MMANA-GAL, EZNEC ni herramientas
comerciales. MMANA-GAL y el ARRL Antenna Book se reservan como fuentes de
contraste independiente para fases posteriores.

## 2. Licencia y compatibilidad

AntennaDesk es **GPL-3.0-or-later**. Eso permite combinar el trabajo con
licencias compatibles con GPLv3, pero **no** con GPL-2.0-only.

| Componente | Licencia verificada | ¿Compatible con GPL-3.0-or-later? | Evidencia |
|---|---|---|---|
| nec2c upstream 1.3.1 | Dominio público | Sí | `README` §7: “nec2c is Public Domain”; copyright de Debian |
| nec2c fork KJ7LNW 1.3.3 | GPL-3.0 | Sí | `COPYING` GPLv3; metadatos del repositorio |
| NEC2++ 2.3.4 | GPL-2.0-or-later | Sí | Cabeceras: “either version 2 … or (at your option) any later version” |
| PyNEC 2.3.4 | GPL-2.0-or-later | Sí | Derivado de NEC2++; misma cabecera |
| xnec2c 4.4.12 | GPL-3.0 | Sí | Metadatos del repositorio |
| NEC-2 Fortran | Dominio público | Sí | Aviso del gobierno de EE. UU. |

**Riesgo principal:** la licencia del fork `nec2c` es GPL-3.0 aunque las
cabeceras originales son de dominio público. Para evitar ambigüedad se puede
usar el upstream 1.3.1 (dominio público) o el fork 1.3.3 (GPL-3.0). Como
AntennaDesk ya es GPLv3, el fork es la opción práctica.

**Obligación de distribución:** al distribuir un binario de nec2c hay que
ofrecer el código fuente correspondiente y los avisos de licencia. El
instalador debe incluir `LICENSE`, `COPYING` del motor y la fuente o una
oferta válida de fuente. Esto debe revisarse legalmente antes del release.

## 3. Integración y resultados

### nec2c

- Entrada: deck NEC-2 en texto.
- Salida: texto con secciones estables dentro de una versión.
- Disponible: impedancia de entrada, corrientes por segmento, presupuesto de
  potencia, campo cercano, patrón de campo lejano, suelo perfecto/finito y
  Sommerfeld, barridos de frecuencia.
- Integración recomendada: **proceso externo** con `QProcess` o
  `subprocess`/`QThreadPool`.
- Ventajas: binario pequeño, sin dependencias de runtime, aislamiento ante
  crashes, fácil de cancelar, licencia compatible.
- Costes: parser de texto propio, gestión de procesos, parche Windows.

### NEC2++ / PyNEC

- NEC2++ ofrece API C++ y CLI; PyNEC expone la API a Python.
- Disponible: los mismos resultados NEC-2, con acceso estructurado.
- Integración como biblioteca: acopla el proceso al motor; un fallo nativo
  puede tumbar la aplicación. Como proceso: conserva el aislamiento, pero
  añade una dependencia C++ más pesada.
- PyNEC: cómodo para prototipos y validación, pero **no publica wheels para
  Windows** en 2.3.4 (solo Linux x86-64 y macOS ARM). Empaquetarlo en Windows
  exige compilar SWIG/C++ o mantener un build propio.
- Ventaja: API rica y mantenimiento activo; útil como segundo motor de
  contraste.

### xnec2c

- GUI GTK sobre nec2c. No es una biblioteca.
- Sirve como referencia técnica y de UX; no se propone como dependencia.

## 4. Portabilidad

| Plataforma | nec2c | NEC2++ | PyNEC |
|---|---|---|---|
| Linux x86-64 | Compila con `cc`; paquete `nec2c` disponible | Compila con CMake | Wheel disponible |
| Windows x86-64 | Requiere parche POSIX; compila con MinGW/Zig; PE verificado | CI oficial en `windows-latest` | Sin wheel; requiere build propio |
| macOS | Compila con `cc` | CMake | Wheel ARM |

El PE Windows se compiló con Zig 0.13 (clang) y con MinGW-w64 GCC 13; ambos
builds pasaron los 19 checks bajo Wine. La validación nativa se ejecutó en
GitHub Actions: Linux y Windows, `19/19` checks.

El parche Windows de nec2c reemplaza:

- `sys/times.h` y `times()` por `clock()`.
- `sigaction()` por `signal()`.
- `getopt()` por un parser mínimo de `-i`, `-o`, `-h`, `-v`.

El parche está en `spikes/phase0/patches/nec2c-windows.patch` y se aplica
automáticamente en el build de Windows.

## 5. Validación numérica del spike

Los valores esperados se transcribieron del **NEC-2 User's Guide, Part III**
(Burke y Poggio), no se generaron con el motor bajo prueba.

| Caso | Esperado (manual) | nec2c 1.3.3 Linux | nec2c 1.3.3 Windows (Wine) | NEC2++ 2.3.4 | PyNEC 2.3.4 |
|---|---:|---:|---:|---:|---:|
| Ejemplo 1, espacio libre, 299.8 MHz | `82.6979 + j46.3060` | `82.6980 + j46.3060` | `82.6980 + j46.3060` | `82.6980 + j46.3060` | `82.6979 + j46.3060` |
| Ejemplo 3, suelo perfecto, 30 MHz | `106.437 + j9.90578` | `106.4400 + j9.9055` | `106.4400 + j9.9055` | `106.4400 + j9.9072` | `106.4415 + j9.9072` |
| Ejemplo 3, suelo finito, 30 MHz | `111.117 + j11.0075` | `111.1200 + j11.0080` | `111.1200 + j11.0080` | `111.1200 + j11.0090` | `111.1228 + j11.0094` |
| Ejemplo 1 escalado a 7.1 MHz | `82.6979 + j46.3060` (±0.1) | `82.6920 + j46.2820` | `82.6920 + j46.2820` | — | — |

Unidades: ohmios. La diferencia entre motores es menor a `0.02 %` en estos
casos. No son resultados bit-a-bit idénticos; por eso el motor y la versión
deben quedar fijados en cada simulación.

Smoke test: un dipolo de 40 m con 21 segmentos, 21 frecuencias, patrón de
elevación y corrientes produjo 21 bloques de impedancia, 21 de patrón y 21 de
corrientes. Tiempo de ejecución: ~6 ms en el equipo de prueba.

## 6. Empaquetado

- **nec2c:** un ejecutable C, sin runtime adicional. Se puede incluir en el
  instalador junto con su código fuente/avisos. Es la opción de menor coste.
- **NEC2++:** biblioteca C++ y CLI; añade runtime C++ y aumenta el tamaño.
- **PyNEC:** extensión compilada por versión de Python y plataforma; sin wheel
  Windows, el empaquetado es el mayor riesgo.
- **xnec2c:** GUI GTK; no aplica.

## 7. Matriz de decisión

Criterios ponderados para el MVP:

| Criterio | Peso | nec2c | NEC2++ | PyNEC |
|---|---:|---:|---:|---:|
| Licencia compatible | Alto | Sí | Sí | Sí |
| Portabilidad Linux/Windows | Alto | Sí, con parche pequeño | Sí | Windows sin wheel |
| Aislamiento de fallos | Alto | Sí (proceso) | Depende de integración | No (in-process) |
| Resultados disponibles | Alto | Sí | Sí | Sí |
| Coste de empaquetado | Medio | Bajo | Medio | Alto |
| Mantenimiento | Medio | Fork activo | Activo | Activo |
| API estructurada | Bajo | No (texto) | Sí | Sí |
| Madurez de validación | Medio | Alta (NEC-2) | Alta (NEC-2) | Alta (NEC-2) |

## 8. Recomendación

Adoptar **nec2c 1.3.3** como motor del MVP, integrado como **proceso externo**
a través de un adaptador propio. Mantener el fork fijado por commit y el
parche Windows en el repositorio. Usar **NEC2++/PyNEC** como segundo motor de
contraste en la Fase 2, no como dependencia de runtime.

Motivos:

1. Licencia compatible y sin ambigüedad práctica para el proyecto GPLv3.
2. Binario pequeño, rápido y sin dependencias de runtime.
3. Aislamiento de crashes y cancelación sencilla.
4. Resultados NEC-2 completos y validados contra el manual.
5. Portabilidad Windows demostrada con un parche acotado.

## 9. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| El formato de texto cambia entre versiones | Fijar versión/commit; parser con fixtures y tests de regresión |
| El parche Windows se desactualiza | Build reproducible; CI Windows; revisar al actualizar |
| Nombres de archivo largos en nec2c | Ejecutar en directorio temporal corto con nombres relativos |
| Distribución GPL incorrecta | Incluir fuente, COPYING y avisos; revisión legal previa |
| Validación insuficiente de suelo/cargas | Ampliar casos de referencia en Fase 2 |
| Dependencia de un fork | El upstream es dominio público; se puede volver a 1.3.1 o mantener el parche |

## 10. Evidencia reproducible

```bash
bash spikes/phase0/scripts/build_nec2c.sh
python3 spikes/phase0/scripts/run_reference.py --nec2c spikes/phase0/build/nec2c
```

Resultado: `19/19 checks passed`.

Para Windows:

```bash
CC="zig cc -target x86_64-windows-gnu" \
  bash spikes/phase0/scripts/build_nec2c_windows.sh
python3 spikes/phase0/scripts/run_reference.py \
  --nec2c spikes/phase0/build/nec2c.exe
```

El binario Windows también se ejecutó mediante Wine en Linux y pasó los 19
checks. La validación nativa se ejecuta en
`.github/workflows/solver-spike.yml`.
