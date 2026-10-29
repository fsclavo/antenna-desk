# ADR-0001 — Motor electromagnético del MVP

- **Estado:** Aceptado
- **Fecha:** 2026-10-28
- **Aprobado:** 2026-10-29 por Fernando Sclavo
- **Decisores:** Fernando Sclavo, desarrollo
- **Fase:** 0 — Spike técnico

## Contexto

AntennaDesk es una aplicación de escritorio local-first, GPL-3.0-or-later,
para Linux y Windows. El MVP necesita simular un dipolo de media onda y
obtener impedancia de entrada, ROE, barrido de frecuencia, corrientes y patrón
de campo lejano. El blueprint prohíbe escribir un solver propio en el MVP y
exige resolver el riesgo de licencia y distribución antes de empezar la GUI.

La Fase 0 debía comparar NEC-2/nec2c, NEC2++/PyNEC y alternativas en cuanto a
licencia, integración, portabilidad, resultados, mantenimiento y empaquetado,
con un caso reproducible en Linux y Windows.

## Decisión

Se adopta **nec2c 1.3.3** (fork `KJ7LNW/nec2c`, commit
`55be1e0e3fe5ee9dad4ce6050711450d19c562fd`) como motor del MVP, integrado
como **proceso externo** mediante un adaptador propio. La versión del motor
se fija por commit y se incluye un parche de portabilidad Windows mantenido
en `spikes/phase0/patches/nec2c-windows.patch`.

NEC2++/PyNEC no se usan como dependencia de runtime. Se reservan como segundo
motor de contraste para la validación de la Fase 2. xnec2c se usa solo como
referencia técnica y de UX.

## Motivos

1. **Licencia compatible:** el nec2c original es de dominio público; el fork
   declara GPL-3.0, compatible con la licencia del proyecto.
2. **Portabilidad:** compila en Linux con `cc` y en Windows con MinGW/Zig tras
   un parche acotado de `getopt`, `sigaction` y `times()`.
3. **Aislamiento:** al ejecutarse como proceso, un fallo del solver no cierra
   la aplicación y la cancelación es controlable.
4. **Resultados:** entrega impedancia, corrientes, potencia y patrón de campo
   lejano; el barrido de 21 frecuencias con patrón tardó ~6 ms.
5. **Validación:** reproduce los valores impresos del NEC-2 User's Guide
   (Ejemplos 1 y 3) con diferencias menores a `0.01 Ω`.
6. **Empaquetado:** un solo ejecutable C, sin runtime adicional; menor coste
   que una biblioteca C++ o una extensión Python.

## Consecuencias

### Positivas

- El motor queda desacoplado del dominio, la GUI y el formato de proyecto.
- Se puede cancelar, limitar y registrar cada ejecución.
- El adaptador puede normalizar la salida sin depender de una API nativa.
- El proyecto conserva la posibilidad de cambiar de motor sin tocar el dominio.

### Negativas

- Hay que escribir y mantener un parser de texto.
- Hay que mantener un parche Windows al actualizar nec2c.
- La distribución GPL exige incluir fuente, COPYING y avisos del motor.
- El formato de salida no es un contrato formal; hay que fijar la versión.

### Neutras

- NEC2++ ofrece una API más rica, pero añade una dependencia C++ más pesada.
- PyNEC es cómodo para prototipos, pero no publica wheels Windows en 2.3.4.

## Alternativas consideradas

| Alternativa | Motivo de descarte |
|---|---|
| NEC2++ como biblioteca | Acopla la app a una biblioteca C++; mayor coste de empaquetado y riesgo de crash nativo |
| PyNEC in-process | Sin wheels Windows; acopla la app a la versión de Python y a la ABI de la extensión |
| xnec2c | Es una GUI GTK, no una biblioteca; útil solo como referencia |
| NEC-2 Fortran original | Requiere gfortran y mantenimiento de código histórico; sin ventaja para el MVP |
| Escribir un solver propio | Fuera de alcance y del principio de reutilizar un motor existente |

## Evidencia

- `spikes/phase0/README.md`: reproducción, casos y resultados.
- `docs/spikes/phase0-solver-evaluation.md`: comparación completa.
- `spikes/phase0/expected/reference_values.json`: valores del manual y
  tolerancias.
- `spikes/phase0/scripts/run_reference.py`: 19 checks, todos pasan en Linux y
  en el binario Windows.
- `.github/workflows/solver-spike.yml`: CI Linux/Windows.

Resultado del spike:

```text
nec2_manual_example1          Z=82.6980+46.3060j  (manual 82.6979+46.3060j)
nec2_manual_example3_perfect  Z=106.4400+9.9055j  (manual 106.437+9.90578j)
nec2_manual_example3_finite   Z=111.1200+11.0080j (manual 111.117+11.0075j)
19/19 checks passed
```

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Cambios de formato en nec2c | Fijar commit; parser con fixtures; tests de regresión |
| Parche Windows obsoleto | CI Windows; build reproducible; revisar al actualizar |
| Rutas largas rechazadas por nec2c | Directorio temporal corto y nombres relativos en el adaptador |
| Incumplimiento GPL en el instalador | Incluir fuente, COPYING y avisos; revisión legal |
| Validación limitada a dos ejemplos | Ampliar casos de referencia en Fase 2 |
| Fork sin mantenimiento futuro | Upstream es dominio público; se puede volver a 1.3.1 o mantener el parche |

## Seguimiento

1. Aprobar este ADR.
2. Mantener el commit y el SHA-256 de la fuente fijados en el build.
3. En Fase 2, implementar el adaptador real con parser probado, cancelación,
   límites de tiempo, logs y captura de stderr.
4. Añadir casos de referencia de suelo, cargas, verticales y loops antes de
   incorporar esas geometrías.
5. Revisar la licencia y el texto de distribución con asesoría legal antes
   del primer release público.
