# AntennaDesk — Development Blueprint
## Aplicación de diseño, simulación y construcción de antenas para radioaficionados

**Versión:** 1.0 · **Estado:** blueprint inicial para OpenCode · **Nombre provisional:** AntennaDesk  
**Plataformas objetivo:** Linux y Windows · **Idioma inicial:** español, preparado para inglés  
**Tipo:** aplicación de escritorio, local-first, con motor electromagnético externo

---

## 1. Resumen ejecutivo

AntennaDesk busca hacer accesible el diseño de antenas sin sacrificar rigor técnico. El usuario debe poder partir de una intención —por ejemplo, «un dipolo para 40 metros, con una altura máxima de 8 m y un espacio disponible de 18 m»—, generar un modelo, simularlo, explorar sus resultados y producir una ficha construible.

La ventaja competitiva no será reimplementar toda la física electromagnética, sino ofrecer un flujo guiado, modelos paramétricos, diagnósticos claros, optimización con restricciones prácticas y trazabilidad entre diseño, simulación y medición.

### Principios

1. **Modelo de dominio propio:** geometría e intención de diseño no dependen de la GUI ni de NEC.
2. **Separación por dominios:** dominio, casos de uso, solver, persistencia, visualización e intercambio son módulos independientes.
3. **Motor existente al principio:** evaluar NEC-2/nec2c y opciones relacionadas; no escribir un solver propio en el MVP.
4. **Diseño guiado primero:** el usuario no debe conocer tarjetas NEC ni segmentación para crear un dipolo.
5. **Rigor y limitaciones visibles:** toda simulación guarda condiciones, versión del motor, advertencias y datos de origen.
6. **Construibilidad:** permitir restricciones físicas y explicar los compromisos.
7. **Local-first:** sin cuentas, nube ni telemetría obligatoria.
8. **Incremental:** cada fase debe dejar una aplicación funcional, probada y documentada.

### No objetivos del MVP

- Reemplazar herramientas electromagnéticas generales para toda geometría y frecuencia.
- Crear un motor electromagnético propio.
- Simular con precisión edificios, árboles, mástiles, cables de alimentación y cualquier entorno real sin modelarlos.
- Incluir control directo de NanoVNA u otros instrumentos.
- Optimizar exclusivamente por ROE.
- Incluir antenas dieléctricas complejas, arrays masivos o análisis full-wave 3D avanzado.
- Crear cuentas, sincronización cloud o colaboración multiusuario.

---

## 2. Usuarios y alcance

### Usuarios

- Radioaficionados que construyen dipolos, verticales, loops y antenas de hilo.
- Constructores que quieren comparar variantes antes de cortar material.
- Clubes que enseñan antenas y electromagnetismo aplicado.
- Usuarios avanzados que necesitan un editor geométrico, sin que sea la puerta de entrada obligatoria.

### MVP

- Asistente de diseño para dipolo de media onda.
- Modelo paramétrico de conductores rectos.
- Frecuencia objetivo, longitud, altura, orientación y diámetro.
- Modelo básico de suelo compatible con el solver elegido.
- Simulación mediante un motor NEC-2 integrado por adaptador.
- Impedancia de entrada, ROE respecto de una impedancia de referencia explícita, barrido de frecuencia, corriente y patrón de campo lejano cuando el motor lo permita.
- Vista geométrica básica.
- Guardar/abrir proyecto nativo versionado.
- Exportar archivo de entrada NEC, resultados CSV y reporte.
- Diagnósticos antes y después de simular.
- Pruebas automatizadas y CI en Linux/Windows.

### Evolución funcional

| Etapa | Funcionalidad |
|---|---|
| 0.1 | Dipolo guiado, motor NEC, resultados y proyecto nativo |
| 0.2 | Comparación de variantes, exportación e informes |
| 0.3 | Optimización de longitud y restricciones físicas |
| 0.4 | Dipolo plegado, vertical simple, loop y cargas admitidas |
| 0.5 | Importación de modelos NEC y mediciones CSV de VNA |
| 0.6+ | Yagi, editor avanzado, optimización multiobjetivo y nuevos motores |

No incorporar un tipo de antena hasta contar con pruebas de referencia y una explicación de sus limitaciones.

---

## 3. Arquitectura

Aplicar una arquitectura modular inspirada en **Hexagonal Architecture / Ports and Adapters**. No usar microservicios: es una aplicación de escritorio local.

```text
┌────────────────────────────────────────────────────────┐
│ Presentación: PySide6                                  │
│ Wizard · editor geométrico · gráficos · diagnósticos   │
└─────────────────────────┬──────────────────────────────┘
                          │ comandos / consultas
┌─────────────────────────▼──────────────────────────────┐
│ Aplicación: casos de uso                                │
│ CreateProject · EditAntenna · RunSimulation · Optimize │
│ CompareVariants · ImportMeasurement · ExportReport     │
└───────────────┬─────────────────────────┬───────────────┘
                │                         │
┌───────────────▼────────────┐  ┌─────────▼──────────────┐
│ Dominio                    │  │ Puertos / interfaces   │
│ Project, Antenna, Geometry │  │ Solver, Repository,    │
│ Feed, Ground, Results      │  │ Importer, Exporter     │
└────────────────────────────┘  └─────────┬──────────────┘
                                          │
                              ┌───────────▼──────────────┐
                              │ Adaptadores              │
                              │ NEC-2 · JSON · CSV · PDF │
                              └──────────────────────────┘
```

### Reglas de dependencia

- `domain/` no importa PySide6, SciPy ni bibliotecas concretas del solver.
- La GUI no ejecuta cálculos electromagnéticos ni conoce la sintaxis NEC.
- La aplicación depende de interfaces, no de implementaciones concretas.
- El adaptador traduce el modelo canónico a NEC y normaliza su salida.
- Los datos crudos del solver se conservan para diagnóstico; la aplicación consume resultados normalizados.
- La simulación nunca se ejecuta en el hilo principal de Qt.
- Una simulación representa una instantánea inmutable del modelo, no una referencia a un objeto que luego cambia.
- La persistencia se versiona y migra explícitamente.
- No introducir abstracciones sin una frontera de cambio real.

### Estructura sugerida

```text
antennadesk/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── AGENTS.md
├── CHANGELOG.md
├── src/antennadesk/
│   ├── __main__.py
│   ├── bootstrap.py
│   ├── config/
│   ├── domain/
│   │   ├── common/          # unidades, IDs, validación
│   │   ├── projects/        # proyecto, variantes, revisiones
│   │   ├── antennas/        # geometría, conductores, fuentes, cargas
│   │   ├── environment/     # suelo y condiciones ambientales
│   │   ├── simulation/      # especificación, resultados, diagnósticos
│   │   ├── optimization/    # objetivos y restricciones
│   │   └── measurements/    # registros y contexto de medición
│   ├── application/
│   │   ├── ports/           # interfaces de solver, repositorio, import/export
│   │   ├── use_cases/
│   │   ├── commands/
│   │   ├── queries/
│   │   └── dto/
│   ├── geometry/            # transformaciones y validación geométrica
│   ├── simulation/
│   │   ├── solver_registry.py
│   │   ├── discretization.py
│   │   ├── normalization.py
│   │   └── nec2/            # adapter, input writer, parser, capabilities
│   ├── optimization/
│   ├── persistence/         # JSON, schema, migraciones
│   ├── interchange/         # NEC, CSV, datos VNA
│   ├── reporting/           # modelo de informe, HTML/PDF
│   ├── ui/
│   │   ├── viewmodels/
│   │   ├── wizard/
│   │   ├── geometry_view/
│   │   ├── results_view/
│   │   └── widgets/
│   └── resources/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── acceptance/
│   ├── reference_cases/
│   ├── fixtures/
│   └── ui/
├── examples/
├── docs/
│   ├── DEVELOPMENT_BLUEPRINT.md
│   ├── ARCHITECTURE.md
│   ├── DOMAIN_MODEL.md
│   ├── SOLVER_ADAPTER.md
│   ├── VALIDATION_PLAN.md
│   ├── USER_GUIDE.md
│   └── ADR/
├── scripts/
└── packaging/
```

No crear todos los archivos vacíos al inicio. Incorporar módulos al implementar funcionalidad real.

---

## 4. Dominios y responsabilidades

### 4.1 Projects

Entidades: `Project`, `DesignVariant`, `ProjectMetadata`, `ProjectRevision`.

Responsabilidades:
- Crear, renombrar, guardar y duplicar proyectos.
- Mantener variantes comparables.
- Guardar instantáneas exactas de modelos y simulaciones.
- Registrar versión de esquema y aplicación.

Regla crítica: editar un diseño no modifica los resultados de simulaciones anteriores.

### 4.2 Antenna Model

Entidades/objetos: `AntennaModel`, `Wire`, `Point3D`, `ConductorMaterial`, `FeedPoint`, `LumpedLoad`, `GroundModel`, `Environment`, `FrequencyPlan`, `AntennaTemplate`, `DesignConstraint`.

Unidades canónicas:
- Longitud: metros.
- Frecuencia: Hz.
- Impedancia: ohmios.
- Conductividad: S/m cuando aplique.
- Convención angular única, convertida en los límites del sistema.
- La UI muestra siempre la unidad y convierte explícitamente.

Los parámetros de diseño (p. ej. longitud total) deben estar separados de la geometría derivada (coordenadas), de la discretización numérica del solver y de los resultados.

### 4.3 Geometry

Funciones:
- Transformar, rotar y trasladar geometrías.
- Calcular longitudes y límites.
- Detectar coordenadas no finitas, conductores de longitud cero, duplicados, uniones y cruces problemáticos.
- Generar una vista previa.
- Proponer discretización, sin confundir segmentos numéricos con conductores físicos.

### 4.4 Simulation

`SimulationSpec` contiene frecuencia o barrido, suelo, configuración de cálculo, discretización y solver/version.

`SimulationResult` normalizado contiene:
- Estado: completado, cancelado, parcial o error.
- Frecuencias calculadas.
- Impedancia compleja de alimentación.
- ROE con impedancia de referencia explícita.
- Corrientes por elemento/segmento si están disponibles.
- Patrón, polarización y resultados de campo lejano según capacidades del motor.
- Convenciones de ganancia/directividad claramente documentadas.
- Advertencias, versión del solver, huella del modelo y duración.
- Referencias a entrada/salida cruda.

No usar un único campo ambiguo `gain`: distinguir ganancia, ganancia realizada y directividad cuando corresponda.

### 4.5 Solver Adapter

Interfaz conceptual:

```python
class AntennaSolver(Protocol):
    def capabilities(self) -> SolverCapabilities: ...
    def validate(self, model, spec) -> list[Diagnostic]: ...
    def run(self, model, spec, progress_callback=None, cancel_token=None) -> RawSolverResult: ...
    def version(self) -> SolverVersion: ...
```

El adaptador debe:
1. Validar capacidades y entradas.
2. Traducir geometría y condiciones al formato del motor.
3. Generar entrada reproducible.
4. Ejecutar el proceso de forma controlada.
5. Capturar stdout, stderr y código de salida.
6. Parsear la salida con reglas explícitas.
7. Normalizar unidades, signos y convenciones.
8. Conservar archivos crudos.
9. Emitir diagnósticos con contexto.
10. Cancelar sin dejar procesos huérfanos.

### 4.6 Optimization

Primera función: ajustar longitud de un dipolo dentro de límites físicos para aproximar una resonancia o reactancia objetivo.

Requisitos:
- Intervalo y límites explícitos.
- Registro de evaluaciones y función objetivo.
- Límites de tiempo/iteraciones.
- Explicación de los parámetros modificados.
- Re-simular y validar la solución final.
- No usar ROE mínima como objetivo universal: la ROE no prueba eficiencia ni un patrón útil.

Más adelante: ancho de banda, ganancia en dirección objetivo, restricciones de espacio, coste/complejidad de construcción y optimización multiobjetivo.

### 4.7 Measurements

Registrar instrumento, fecha, archivo original/hash, rango de frecuencia, tipo de dato, estado de calibración informado, plano de referencia, coaxial/accesorios, antena/variante, altura, orientación, entorno y notas.

El MVP importa CSV documentado. No asumir que todos los CSV de VNA tienen el mismo formato ni que una medición en un plano de referencia es directamente comparable con la impedancia de una fuente ideal en otro plano.

### 4.8 Reporting

El informe incluye:
- Proyecto/variante y dimensiones.
- Frecuencia y condiciones del entorno.
- Motor, versión y configuración.
- Resultados y gráficos con unidades.
- Advertencias y limitaciones.
- Parámetros de optimización.
- Datos de medición asociados.
- Fecha y huella de simulación.

Usar un modelo de reporte común. HTML puede ser la base; PDF se añade cuando la salida sea reproducible.

---

## 5. Modelo de dominio e invariantes

```text
Project
 ├── DesignVariant
 │    └── AntennaModel
 │         ├── Geometry / Wires
 │         ├── FeedPoint
 │         ├── ConductorMaterial
 │         ├── Loads
 │         └── Environment / GroundModel
 ├── SimulationRun
 │    ├── SimulationSpec
 │    ├── SolverMetadata
 │    ├── SimulationResult
 │    └── Diagnostics
 ├── MeasurementRecord
 └── ReportReference
```

Invariantes:
- Todas las magnitudes numéricas son finitas.
- Ningún conductor tiene longitud cero.
- La fuente referencia una ubicación válida y compatible con el solver.
- Frecuencias positivas y barridos válidos, acotados en tamaño.
- El archivo guardado se valida al abrirse.
- Los resultados se vinculan a una instantánea inmutable.
- La conversión al solver produce diagnósticos ante elementos no representables.
- Las aproximaciones y simplificaciones nunca se ocultan.

Las plantillas (dipolo, vertical, loop) generan el mismo `AntennaModel` canónico; no deben crear caminos de simulación independientes.

---

## 6. Motor electromagnético y riesgos numéricos

### Decisión inicial

Evaluar NEC-2/nec2c y opciones como NEC2++/PyNEC. Realizar un spike técnico antes de comprometer arquitectura:
- Licencia y obligaciones de redistribución.
- Integración como biblioteca o proceso externo.
- Funcionamiento en Linux y Windows.
- Dependencias nativas y empaquetado.
- Disponibilidad de impedancia, corriente, patrón y barridos.
- Calidad del mantenimiento y formatos de salida.
- Limitaciones de geometría, suelo y cargas.
- Caso de referencia ejecutable.

No asumir que una biblioteca GPL puede distribuirse sin consecuencias para la licencia final del producto. Documentar la decisión en un ADR. Xnec2c puede servir como referencia técnica y de UX, aunque no necesariamente como dependencia embebida.

### Discretización

La discretización es una fuente importante de errores. El usuario define conductores físicos; el adaptador crea segmentos numéricos para el motor.

Debe haber:
- Política de segmentación documentada.
- Diagnóstico de segmentos demasiado cortos/largos según recomendaciones del motor.
- Validación de fuentes, uniones y cruces.
- Visualización de segmentos en modo avanzado.
- Persistencia de la configuración numérica.
- Advertencias si la geometría cae fuera de las recomendaciones conocidas.

No convertir una regla de segmentación en verdad universal: basarse en la documentación del solver y validarla con casos concretos.

### Limitaciones físicas

La aplicación debe explicar que:
- Una ROE baja no demuestra alta eficiencia.
- El suelo real puede diferir del modelo.
- La alimentación física puede introducir modo común.
- Edificios, árboles, mástiles y cables no modelados pueden alterar resultados.
- Los diámetros, materiales y dimensiones reales tienen tolerancias.
- La ganancia, ganancia realizada y directividad no son intercambiables.
- La simulación es una predicción condicionada por el modelo, no una garantía de rendimiento real.

---

## 7. UX: diseño guiado y modo avanzado

### Ventana principal

- Barra superior: proyecto, variante, guardar, deshacer/rehacer y simular.
- Panel de diseño: parámetros de antena y restricciones.
- Centro: geometría 2D/3D.
- Panel de resumen: advertencias y estado.
- Resultados en pestañas: impedancia/ROE, patrón, corrientes, diagnósticos y datos crudos.

Evitar saturar el MVP. Mostrar funciones avanzadas progresivamente.

### Asistente de dipolo

1. Elegir banda o introducir frecuencia.
2. Indicar orientación y espacio disponible.
3. Introducir altura.
4. Elegir conductor/diámetro.
5. Revisar condiciones de suelo y supuestos.
6. Generar modelo inicial.
7. Simular.
8. Interpretar resonancia, impedancia, ROE y patrón.
9. Ajustar longitud con control guiado.
10. Exportar ficha de construcción.

La longitud inicial debe presentarse como aproximación, no como longitud final universal.

### Principios UX

- Mostrar primero la intención, después los detalles numéricos.
- Unidades visibles, tooltips y explicaciones breves.
- Errores accionables.
- Separar claramente estimaciones analíticas, simulaciones y mediciones.
- Advertir antes de simular si el modelo es dudoso.
- Accesibilidad por teclado.
- Idioma inicial español, preparado para inglés.

---

## 8. Stack tecnológico

| Área | Elección propuesta | Uso |
|---|---|---|
| Lenguaje | Python 3.11+ | Lógica, integración y ecosistema científico |
| GUI | PySide6 / Qt Widgets | Escritorio multiplataforma |
| Entorno/dependencias | `uv` + `uv.lock` | Reproducibilidad |
| Tipado | type hints + mypy | Contratos y mantenimiento |
| Lint/format | Ruff | Calidad y estilo |
| Tests | pytest | Unitarios, integración, aceptación |
| Cálculo | NumPy, SciPy | Optimización y cálculos auxiliares |
| Gráficos interactivos | PyQtGraph | Barridos y curvas |
| Informes | Matplotlib opcional + HTML/PDF | Gráficos estáticos e informes |
| Solver | NEC-2 por adaptador | Simulación electromagnética |
| Proyecto nativo | JSON versionado | Portabilidad y transparencia |
| Medidas | CSV documentado | Importación inicial |
| Linux | AppImage tras validación | Distribución |
| Windows | PyInstaller inicialmente | Ejecutable |
| CI | GitHub Actions | Tests y builds |

### Decisiones que no hay que anticipar

- No usar scikit-rf como modelo de dominio: puede ayudar a manejar datos de redes en una fase futura, pero no representa la geometría de una antena.
- No añadir PyVista/VTK hasta demostrar que una vista 3D ligera es insuficiente.
- No introducir una base de datos en el MVP si JSON satisface el caso de uso.
- No usar `pickle` para archivos de proyecto.
- No ejecutar el solver desde widgets.
- No añadir servicios cloud ni telemetría por defecto.
- No agregar dependencias sin justificar coste, licencia y beneficio.

---

## 9. Persistencia e interoperabilidad

### Formato nativo

Usar JSON con `schema_version`, validación y migraciones. Guardado atómico mediante archivo temporal y reemplazo tras confirmar éxito. No ejecutar contenido del archivo ni aceptar deserialización arbitraria.

Ejemplo ilustrativo:

```json
{
  "format": "antennadesk-project",
  "schema_version": 1,
  "project": {"id": "uuid", "name": "Dipolo 40 m", "units": "metric"},
  "designs": [{
    "id": "uuid",
    "name": "Inicial",
    "antenna_type": "wire_dipole",
    "parameters": {
      "target_frequency_hz": 7100000,
      "total_length_m": 20.0,
      "height_m": 8.0
    }
  }],
  "simulation_runs": []
}
```

### NEC

- Exportar entrada NEC reproducible.
- Importar sólo un subconjunto documentado al comienzo.
- Advertir por elementos ignorados/no soportados.
- No descartar tarjetas desconocidas en silencio.
- No prometer round-trip perfecto hasta tener pruebas.

### CSV y VNA

Documentar columnas, unidades, separadores, decimales, convención de fase y datos faltantes. Implementar adaptadores por formato de archivo; no tratar todos los CSV como iguales. En primera instancia, importar archivos; control directo del instrumento queda fuera del MVP.

---

## 10. Validación científica y pruebas

### Tres niveles que no deben confundirse

1. **Prueba de software:** la implementación hace lo previsto.
2. **Validación numérica:** coincide con referencias independientes dentro de tolerancias documentadas.
3. **Validación experimental:** se compara con mediciones reales considerando incertidumbre y entorno.

### Casos de referencia iniciales

- Dipolo recto en espacio libre.
- Dipolo con barrido de frecuencia.
- Dipolo horizontal sobre suelo a distintas alturas.
- Vertical con modelo de tierra/radiales que admita el motor.
- Loop y cargas cuando se implementen.
- Modelos inválidos para probar diagnósticos.

Las referencias deben proceder de una fuente técnica trazable, una herramienta independiente o cálculo contrastado. No crear valores esperados usando la misma implementación que se prueba.

### Pruebas

**Unitarias:** unidades, geometría, validaciones, ROE a partir de impedancia compleja, serialización, migraciones y normalización.

**Integración:** adaptador del solver, parseo de salida real, errores, cancelación, importación CSV, reportes y reapertura de proyectos.

**Aceptación:** crear dipolo sin coordenadas; simular; modificar longitud sin alterar resultados previos; guardar/reabrir; exportar informe; recibir error accionable ante un modelo inválido.

**Regresión numérica:** fixtures versionados, tolerancias explícitas, metadatos de versión/configuración y revisión manual de cambios de resultados. No actualizar snapshots automáticamente sin análisis.

---

## 11. Ejecución, robustez y seguridad

- Ejecutar simulaciones fuera del hilo principal usando `QProcess`, `QThreadPool` u opción validada en el spike.
- Mantener UI responsiva.
- Mostrar progreso sólo si el motor proporciona datos reales.
- Permitir cancelar y limpiar procesos temporales.
- Limitar concurrencia, duración e iteraciones de optimización.
- Registrar logs por simulación.
- Cachear sólo con una clave que incluya modelo, configuración y versión del solver.
- Tratar archivos importados como datos no confiables.
- Evitar comandos de shell construidos concatenando entradas del usuario.
- Validar rutas y tamaños de archivos.
- No ejecutar scripts embebidos.
- No descargar/ejecutar automáticamente motores sin un mecanismo explícito y verificable.
- Fallos del solver no deben cerrar la aplicación.

---

## 12. Reporting y documentación

Informes HTML como base y PDF cuando el formato sea estable. Incluir geometría, dimensiones, condiciones, motor/versión, resultados con unidades, advertencias, parámetros de optimización y datos de medición relacionados.

Documentación inicial:
- Primer proyecto: dipolo HF.
- Cómo interpretar impedancia y ROE.
- Qué puede y qué no puede decir una simulación.
- Cómo comparar variantes.
- Cómo importar mediciones VNA.
- Diagnóstico de errores comunes.

Mantener glosario: resonancia, reactancia, ROE, impedancia, ganancia, directividad, polarización, suelo, segmento, fuente y carga.

---

## 13. OpenCode y disciplina de desarrollo

Crear y mantener:
- `AGENTS.md`
- `docs/DEVELOPMENT_BLUEPRINT.md`
- `docs/ARCHITECTURE.md`
- `docs/DOMAIN_MODEL.md`
- `docs/SOLVER_ADAPTER.md`
- `docs/VALIDATION_PLAN.md`
- `docs/ADR/`

### Contenido sugerido para `AGENTS.md`

```markdown
# Project instructions

- Read docs/DEVELOPMENT_BLUEPRINT.md before implementing features.
- Preserve boundaries between domain, application, solver adapters, persistence and UI.
- Domain code must not import PySide6 or concrete solver libraries.
- Never put electromagnetic calculations in widgets/view models.
- Do not invent numerical reference values.
- New domain rules require unit tests.
- Solver behavior changes require integration/regression tests.
- Keep units and result conventions explicit.
- Do not silently discard unsupported imported model elements.
- Never use pickle for project files.
- Keep the UI responsive during simulations.
- Explain why a new dependency is needed.
- Update docs when behavior or project schema changes.
- Run relevant tests, lint and type checks before declaring a task complete.
- Report assumptions, tests run and remaining limitations.
- Implement one coherent milestone at a time; do not scaffold the whole roadmap.
```

### Flujo de trabajo recomendado

Para cada tarea, OpenCode debe:
1. Leer blueprint y código existente.
2. Identificar dominios afectados y dependencias.
3. Proponer plan corto y archivos a modificar.
4. Implementar alcance mínimo.
5. Añadir pruebas.
6. Ejecutar tests, lint y type checking relevantes.
7. Revisar límites arquitectónicos.
8. Actualizar documentación.
9. Informar cambios, decisiones, pruebas y limitaciones.

No pedirle que implemente todo el producto de una vez.

---

## 14. CI/CD y distribución

### CI

En cada PR:
- Instalar dependencias desde `uv.lock`.
- Ruff.
- mypy sobre módulos definidos.
- pytest.
- Tests de dominio sin depender del solver.
- Integración del solver donde esté disponible.
- Construcción del paquete.
- Validación de ejemplos y proyectos de referencia.

### Linux y Windows

Linux: probar primero ejecución reproducible; empaquetar AppImage sólo tras verificar bibliotecas nativas, licencia y dependencias; probar en distribuciones representativas.

Windows: PyInstaller como primera opción, tras validar integración con el solver; probar en instalación limpia sin Python; documentar dependencias y avisos de seguridad habituales sin recomendar desactivar protecciones.

La distribución del motor puede ser el principal riesgo de empaquetado. Resolverlo en Fase 0, no al final.

---

## 15. Riesgos principales

| Riesgo | Mitigación |
|---|---|
| Licencia del solver no compatible | Spike temprano y ADR antes de integrarlo |
| Resultados erróneos o mal interpretados | Casos de referencia independientes y validación física |
| Geometría/discretización inadecuada | Diagnósticos y validación previa |
| Alcance excesivo | MVP limitado a dipolo y conductores rectos |
| UX que oculta supuestos físicos | Mostrar condiciones, advertencias y glosario |
| Dependencia externa sin mantenimiento | Adaptador propio y alternativa evaluada |
| Diferencias Linux/Windows | CI y prueba de paquete limpio |
| Comparación incorrecta con VNA | Guardar calibración, plano de referencia y accesorios |
| Optimización poco construible | Restricciones físicas y objetivos explícitos |
| Pérdida de proyectos antiguos | Esquema versionado y migraciones probadas |

---

## 16. Roadmap con criterios de salida

### Fase 0 — Spike técnico (P0)

- Comparar NEC-2/nec2c, NEC2++/PyNEC y opciones pertinentes.
- Revisar licencia, redistribución, integración Python/proceso externo y portabilidad.
- Ejecutar un caso simple en Linux y Windows.
- Inspeccionar entrada/salida y disponibilidad de resultados.
- Crear ADR con decisión y riesgos.

**Salida:** motor elegido con evidencia y caso reproducible. No iniciar la GUI antes de resolver el riesgo de distribución.

### Fase 1 — Dominio y persistencia (P0)

- Estructura, tooling y `AGENTS.md`.
- Unidades, geometría, conductor, fuente y entorno mínimos.
- Validaciones.
- JSON versionado y guardado atómico.
- Tests de dominio y migraciones.

**Salida:** crear, validar, guardar y reabrir un dipolo sin GUI ni solver.

### Fase 2 — Adaptador y referencias (P0)

- Generación de entrada.
- Ejecución, captura de errores y cancelación.
- Parseo y normalización.
- Casos de referencia con tolerancias.
- Logs y advertencias.

**Salida:** dipolo de referencia simulado reproduciblemente y comparado con fuente independiente.

### Fase 3 — MVP guiado (P0)

- Ventana principal y wizard.
- Parámetros de frecuencia, longitud, altura y diámetro.
- Geometría generada automáticamente.
- Simulación asíncrona.
- Impedancia, ROE, barrido y patrón básico.
- Guardar/abrir proyectos.

**Salida:** un usuario simula un dipolo sin editar coordenadas ni archivos NEC.

### Fase 4 — Comparación e informes (P1)

- Vista geométrica mejorada.
- Comparación A/B.
- Corrientes si el motor las soporta.
- CSV y reportes HTML/PDF.
- Marcadores de resonancia.

**Salida:** variantes comparables e informe reproducible.

### Fase 5 — Optimización y construcción (P1)

- Ajuste de longitud con límites.
- Registro de iteraciones y objetivo.
- Restricciones de espacio.
- Hoja de construcción y análisis de sensibilidad.

**Salida:** el usuario ajusta un dipolo a un objetivo y entiende los cambios.

### Fase 6 — Nuevas antenas y mediciones (P1/P2)

- Incorporar vertical, loop o dipolo plegado según demanda.
- Importación CSV de VNA por adaptadores.
- Registro de condiciones de medición.
- Comparación simulación/medición.
- Validación con antena física.

**Salida:** cada nueva geometría tiene tests de referencia y limitaciones documentadas.

### Fase 7 — Editor avanzado (P2)

- Editor libre de conductores.
- Importación de subconjunto NEC.
- Fuentes/cargas avanzadas.
- Optimización multiobjetivo.
- Otros motores sólo ante necesidad demostrada.

**Salida:** los usuarios avanzados pueden extender diseños sin perjudicar el flujo guiado.

---

## 17. Primer milestone recomendado

No empezar por una interfaz atractiva. Crear primero una prueba vertical:

1. Construir un modelo de dipolo desde parámetros.
2. Validarlo y generar diagnósticos.
3. Convertirlo a entrada NEC.
4. Ejecutar el motor y capturar salida.
5. Normalizar impedancia y patrón.
6. Comparar con referencia independiente.
7. Guardar modelo, configuración y resultado.
8. Reabrir el proyecto y generar un reporte mínimo.

Después de validar esta ruta, implementar el wizard y la GUI.

---

## 18. Definition of Done

Una funcionalidad está terminada cuando:
- Cumple criterios de aceptación.
- Tiene pruebas adecuadas al riesgo.
- Respeta límites de dominio.
- Usa unidades y convenciones explícitas.
- Expone errores y limitaciones.
- Actualiza documentación.
- No bloquea la UI en operaciones largas.
- Pasa tests/lint/type checks pertinentes.
- No introduce dependencias sin justificar.
- Mantiene compatibilidad de proyectos o incluye migración.
- Declara limitaciones pendientes.

Una función de simulación no está terminada porque el motor devuelva un número: necesita validación, interpretación y advertencias.

---

## 19. Métricas de salud

- Casos de referencia que pasan.
- Regresiones numéricas investigadas y resueltas.
- Cobertura de pruebas del dominio y adaptadores.
- Flujos principales con pruebas de aceptación.
- Responsividad de UI durante simulación.
- Proyectos de ejemplo que abren en cada release.
- Builds limpios Linux/Windows.
- Formatos de importación con fixtures y tests.

La cobertura de código es una señal auxiliar, no una prueba de validez electromagnética.

---

## 20. ADRs iniciales

Crear decisiones breves con contexto, alternativas, decisión y consecuencias:
1. Motor y licencia.
2. Arquitectura y límites de dominios.
3. Unidades y convenciones angulares.
4. Formato de proyecto y migraciones.
5. Ejecución/cancelación de simulaciones.
6. Estrategia de visualización 3D.
7. Formatos de importación/exportación.
8. Licencia del producto.
9. Empaquetado Linux/Windows.

---

## 21. Instrucción inicial para OpenCode

Usar este documento como guía, no como orden para implementar todo a la vez.

**Primera tarea:** realizar exclusivamente la Fase 0. Comparar opciones de motor NEC en cuanto a licencia, integración, portabilidad, resultados disponibles, mantenimiento y distribución. Crear una tabla comparativa, un spike reproducible y un ADR recomendado. No implementar aún la GUI ni el modelo completo.

Después de aprobar esa decisión, avanzar a Fase 1. Si una tarea puntual contradice el blueprint, explicar el conflicto antes de modificar la arquitectura.

---

## 22. Referencias técnicas iniciales

- Qt for Python / PySide6: https://doc.qt.io/qtforpython-6/
- PyNEC: https://pypi.org/project/PyNEC/
- Xnec2c, manual: https://www.xnec2c.org/
- Xnec2c, repositorio: https://github.com/KJ7LNW/xnec2c

Son puntos de partida, no una aprobación definitiva. Confirmar versión, mantenimiento, compatibilidad, licencia y condiciones de redistribución al elegir el motor.
