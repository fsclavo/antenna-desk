# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Spanish translations for Qt-free report labels.

The reporting package builds English documents by default.  ``Translator.report``
uses this catalog to translate report labels, headings, and parameterized
construction-note templates when the UI language is Spanish.  Keys are the
exact English source strings used by the reporting modules; a missing key
falls back to English so a partial translation never breaks an export.
"""

from __future__ import annotations

REPORT_SPANISH: dict[str, str] = {
    # Feed-connection detail.
    "Feed connection": "Conexión de alimentación",
    "Schematic · not to scale": "Esquema · no a escala",
    "Antenna terminal A": "Terminal A de la antena",
    "Antenna terminal B": "Terminal B de la antena",
    "Coax center": "Centro del coaxil",
    "Coax shield": "Malla del coaxil",
    "Common-mode choke": "Choke de modo común",
    "Direct coax": "Coaxil directo",
    "no balun recorded": "sin balún registrado",
    "1:1 current balun": "Balún de corriente 1:1",
    "Transformer / balun": "Transformador / balún",
    "Balanced feed line": "Línea de alimentación balanceada",
    "Multi-port combining network": "Red combinadora multipuerto",
    "Connection not classified": "Conexión sin clasificar",
    "Center conductor": "Conductor central",
    "Shield (braid)": "Malla (trenza)",
    "Coax cross-section": "Sección del coaxil",
    "Coax cable": "Cable coaxil",
    "Recommended, not recorded": "Recomendado, no registrado",
    "Modeled as ideal": "Modelado como ideal",
    "Combining network not modeled": "Red combinadora no modelada",
    "Primary": "Primario",
    "Secondary": "Secundario",
    "Return": "Retorno",
    "The balun location depends on the tuner; it is not modeled.": (
        "La ubicación del balún depende del sintonizador; no está modelada."
    ),
    "Balanced line A": "Línea balanceada A",
    "Balanced line B": "Línea balanceada B",
    "Additional sources": "Fuentes adicionales",
    "Verify the wiring": "Verificar el cableado",
    "Balance: {balance}": "Balance: {balance}",
    "balanced": "equilibrada",
    "unbalanced": "desbalanceada",
    "Construction aid, not a solver result.": (
        "Ayuda de construcción, no un resultado del solver."
    ),
    "Connection table": "Tabla de conexiones",
    "From": "Desde",
    "To": "Hacia",
    "Modeled": "Modelado",
    "Recorded": "Registrado",
    "Recommended": "Recomendado",
    "Not modeled": "No modelado",
    "Assembly steps": "Pasos de armado",
    "Limitations": "Limitaciones",
    "Matching hardware": "Herraje de adaptación",
    "Direct connection": "Conexión directa",
    "Balanced output": "Salida balanceada",
    "Unbalanced input": "Entrada desbalanceada",
    "Balanced line": "Línea balanceada",
    "Primary feed": "Alimentación principal",
    "Return path": "Camino de retorno",
    "Verify before construction": "Verificar antes de construir",
    "Balun balanced A": "Balún, salida balanceada A",
    "Balun balanced B": "Balún, salida balanceada B",
    "Balun input center": "Balún, entrada central",
    "Balun input shield": "Balún, entrada de malla",
    "Transformer secondary A": "Transformador, secundario A",
    "Transformer secondary B": "Transformador, secundario B",
    "Transformer primary center": "Transformador, primario central",
    "Transformer primary shield": "Transformador, primario de malla",
    "Ground / radials": "Tierra / radiales",
    "Primary port": "Puerto principal",
    "Not classified": "Sin clasificar",
    "A and B to a 1:1 current balun; coax center and shield to its input.": (
        "A y B a un balún de corriente 1:1; centro y malla del coaxil a su entrada."
    ),
    "A and B to a transformer/balun; coax center and shield to its input.": (
        "A y B a un transformador/balún; centro y malla del coaxil a su entrada."
    ),
    "A and B to the balanced feed line; the balun location depends on the tuner.": (
        "A y B a la línea de alimentación balanceada; la ubicación del balún "
        "depende del sintonizador."
    ),
    "Primary port plus additional sources; the combining network is not modeled.": (
        "Puerto principal más fuentes adicionales; la red combinadora no está modelada."
    ),
    "Connection not classified; verify the wiring before construction.": (
        "Conexión sin clasificar; verificá el cableado antes de construir."
    ),
    (
        "Direct coax: A to the center conductor and B to the shield; "
        "a current balun/choke is recommended."
    ): (
        "Coaxil directo: A al conductor central y B a la malla; se recomienda un "
        "balún/choke de corriente."
    ),
    "Direct coax: A to the radiator and B to the ground or return.": (
        "Coaxil directo: A al radiador y B a la tierra o al retorno."
    ),
    "Loop gap: A and B across the gap; verify the coupling or matching method.": (
        "Gap del lazo: A y B a través del gap; verificá el método de acople o adaptación."
    ),
    "Apex gap: A and B across the gap; verify the center/shield assignment.": (
        "Gap del vértice: A y B a través del gap; verificá la asignación centro/malla."
    ),
    "Ideal source at the feed point": "Fuente ideal en el punto de alimentación",
    "Ideal feed transformer": "Transformador de alimentación ideal",
    "Current balun/choke installed": "Balún/choke de corriente instalado",
    "Feed line configured": "Línea de alimentación configurada",
    "Balun/unun loss configured": "Pérdida de balún/unun configurada",
    "Install a 1:1 current balun/choke at the feed point": (
        "Instalá un balún/choke de corriente 1:1 en el punto de alimentación"
    ),
    "Use a current balun/transformer at the modeled ratio": (
        "Usá un balún/transformador de corriente con la relación modelada"
    ),
    "A 1:1 current balun/choke is recommended": ("Se recomienda un balún/choke de corriente 1:1"),
    "No current balun is required by this family": (
        "Esta familia no requiere un balún de corriente"
    ),
    "Verify the shield, ground, and return connection": (
        "Verificá la conexión de malla, tierra y retorno"
    ),
    "Verify the feed transition; this family is not classified": (
        "Verificá la transición de alimentación; esta familia no está clasificada"
    ),
    "Common-mode current on the coax shield": ("Corriente de modo común en la malla del coaxil"),
    "Balun balance, frequency response, and power handling": (
        "Balance, respuesta en frecuencia y potencia del balún"
    ),
    "Coax shield radiation and connector loss": (
        "Radiación de la malla del coaxil y pérdida del conector"
    ),
    "Gamma and delta matches are not modeled.": (
        "Las adaptaciones gamma y delta no están modeladas."
    ),
    "The physical center/shield assignment is not classified": (
        "La asignación física de centro/malla no está clasificada"
    ),
    "Cut or prepare the feed gap and leave clearance for the feed hardware.": (
        "Cortá o prepará el gap de alimentación y dejá espacio para el herraje."
    ),
    "Connect terminal A and terminal B to the interface as shown.": (
        "Conectá el terminal A y el terminal B a la interfaz como se muestra."
    ),
    "Seal the connector, provide strain relief, and form a drip loop.": (
        "Sellá el conector, dale alivio de tensión y formá un drip loop."
    ),
    "Connect the coax center and shield to the balun or transformer input.": (
        "Conectá el centro y la malla del coaxil a la entrada del balún o transformador."
    ),
    "Keep the balanced line pair together and verify the tuner-side balun.": (
        "Mantené juntos los conductores de la línea balanceada y verificá el "
        "balún del lado del sintonizador."
    ),
    "Build the combining network separately; it is not part of the antenna model.": (
        "Construí la red combinadora por separado; no es parte del modelo de la antena."
    ),
    "Verify the shield, ground, radial, or counterpoise return path.": (
        "Verificá el camino de retorno de malla, tierra, radiales o contrapeso."
    ),
    "This is a construction aid, not a solver result.": (
        "Esto es una ayuda de construcción, no un resultado del solver."
    ),
    "The app does not model common-mode current or coax shield radiation.": (
        "La app no modela corriente de modo común ni radiación de la malla del coaxil."
    ),
    "The feed gap is not modeled; record it as an as-built dimension.": (
        "El gap de alimentación no está modelado; registralo como dimensión as-built."
    ),
    "The transformer is ideal; verify the real balun ratio and power rating.": (
        "El transformador es ideal; verificá la relación y la potencia del balún real."
    ),
    "The center/shield assignment is not classified; verify it on the build.": (
        "La asignación centro/malla no está clasificada; verificala en la obra."
    ),
    "The hairpin is a matching stub, not a balun.": (
        "El hairpin es un stub de adaptación, no un balún."
    ),
    "Beta/hairpin matching stub; it is not a balun": (
        "Stub de adaptación beta/hairpin; no es un balún"
    ),
    "Conductor B is continuous and connected at both ends; it is not a parasitic": (
        "El conductor B es continuo y está unido en ambos extremos; no es un parásito"
    ),
    "Tapered driven element": "Elemento alimentado con punta cónica",
    "Off-center feed; verify the actual transformer ratio": (
        "Alimentación descentrada; verificá la relación real del transformador"
    ),
    "Loop feed at a gap or matching section": (
        "Alimentación del lazo en un gap o sección de adaptación"
    ),
    "Counterpoise or installation return is required": (
        "Se requiere contrapeso o retorno de instalación"
    ),
    "The stub is a matching section, not a balun": (
        "El stub es una sección de adaptación, no un balún"
    ),
    "Verify the center/shield assignment at the apex": (
        "Verificá la asignación centro/malla en el vértice"
    ),
    "Top-junction feed; matching and ground return are not modeled": (
        "Alimentación en la unión superior; adaptación y retorno de tierra no modelados"
    ),
    "Primary port plus additional sources; the combining network is ideal": (
        "Puerto principal más fuentes adicionales; la red combinadora es ideal"
    ),
    "Balanced feed line; the balun location depends on the tuner": (
        "Línea de alimentación balanceada; la ubicación del balún depende del sintonizador"
    ),
    "Custom or unclassified geometry; verify the center/shield assignment": (
        "Geometría personalizada o sin clasificar; verificá la asignación centro/malla"
    ),
    # Structural headings and captions.
    "Bill of materials": "Lista de materiales",
    "{material} Ø{diameter:.3f} mm": "{material} Ø{diameter:.3f} mm",
    "Unit cost": "Costo unitario",
    "Unit cost / m": "Costo unitario / m",
    "Line total": "Total de la línea",
    "BOM total": "Total del BOM",
    "Construction notes": "Notas de construcción",
    "Construction pre-flight": "Pre-flight de construcción",
    "Ready to build.": "Listo para construir.",
    "Ready to build with warnings.": "Listo para construir con advertencias.",
    "Not ready to build: fix the errors below.": (
        "No listo para construir: corregí los errores indicados."
    ),
    "No pre-flight issues found.": "No se encontraron problemas de pre-flight.",
    "Failure": "Fallo",
    "Warning": "Advertencia",
    "Info": "Información",
    "Category": "Categoría",
    "Finding": "Hallazgo",
    "Where": "Dónde",
    "Geometry": "Geometría",
    "Feedpoint and connections": "Alimentación y conexiones",
    "Site and supports": "Sitio y soportes",
    "Construction data": "Datos de construcción",
    "Solver assumptions": "Supuestos del solver",
    "Dimensions": "Dimensiones",
    "Evidence and limitations": "Evidencia y limitaciones",
    "Simulation": "Simulación",
    "Wire schedule": "Lista de hilos",
    "Construction view": "Vista de construcción",
    "Isometric view": "Vista isométrica",
    "Installation view (front)": "Vista de instalación (frontal)",
    "Installation return": "Retorno de instalación",
    "Installation return (proxy)": "Retorno de instalación (proxy)",
    "Top layout": "Disposición en planta",
    # Title block and table headers.
    "#": "#",
    "Active length": "Longitud activa",
    "Amplitude": "Amplitud",
    "Amplitude taper": "Atenuación de amplitud",
    "Antenna": "Antena",
    "Apex height": "Altura del vértice",
    "At (MHz)": "En (MHz)",
    "Azimuth": "Azimut",
    "Band": "Banda",
    "Band set": "Set de bandas",
    "Bands": "Bandas",
    "published G3TXQ": "G3TXQ publicada",
    "reference-scaled": "escalada desde la referencia",
    "Feed model": "Modelo de alimentación",
    "Base height": "Altura de base",
    "Best SWR": "Mejor ROE",
    "Boom height": "Altura del boom",
    "Levels": "Niveles",
    "Level spacing": "Separación entre niveles",
    "Base Yagi elements": "Elementos del Yagi base",
    "Base boom length": "Longitud del boom base",
    "Base boom height": "Altura del boom base",
    "Top level height": "Altura del nivel superior",
    "Additional-level ratio": "Relación de niveles adicionales",
    "Boom length": "Longitud del boom",
    "Longest element": "Elemento más largo",
    "Phase line Z0": "Z0 de la línea de fase",
    "Phase line velocity factor": "Factor de velocidad de la línea de fase",
    "Phase-line Z0": "Z0 de la línea de fase",
    "Phase-line velocity factor": "Factor de velocidad de la línea de fase",
    "Shortest element": "Elemento más corto",
    "Sigma": "Sigma",
    "Tau": "Tau",
    "Bottom height": "Altura inferior",
    "Capacitor ESR": "ESR del capacitor",
    "Capacitor reactance": "Reactancia del capacitor",
    "Center sag": "Flecha central",
    "Center section": "Sección central",
    "Circumference": "Circunferencia",
    "Code": "Código",
    "Coil Q": "Q de la bobina",
    "Conductor length": "Longitud del conductor",
    "Conductor losses": "Pérdidas en conductores",
    "Conductor spacing": "Separación entre conductores",
    "Cone base radius": "Radio de la base del cono",
    "Cone height": "Altura del cono",
    "Counterpoise": "Contrapeso",
    "Return length": "Longitud del retorno",
    "automatic": "automático",
    "installation proxy": "proxy de instalación",
    "counterpoise": "contrapeso",
    "coax shield": "malla del coaxil",
    "Counterpoise azimuth": "Azimut del contrapeso",
    "Counterpoise height": "Altura del contrapeso",
    "Design": "Diseño",
    "Design band": "Banda de diseño",
    "Diameter": "Diámetro",
    "Director element": "Elemento director",
    "Director side": "Lado del director",
    "Director spacing": "Separación del director",
    "Disc radius": "Radio del disco",
    "Driven element": "Elemento alimentado",
    "Driven element length": "Longitud del elemento alimentado",
    "Driven loop side": "Lado del lazo alimentado",
    "Driven sources": "Fuentes excitadas",
    "Driven tip": "Punta del alimentado",
    "Driver half-length": "Semilongitud del excitador",
    "Efficiency": "Eficiencia",
    "Efficiency (%)": "Eficiencia (%)",
    "Element length": "Longitud del elemento",
    "Element lengths": "Longitudes de elementos",
    "Element spacing": "Separación entre elementos",
    "Element width": "Ancho del elemento",
    "Elements": "Elementos",
    "End (m)": "Fin (m)",
    "End connector length": "Longitud del conector de extremo",
    "End height": "Altura del extremo",
    "Horizontal run": "Tramo horizontal",
    "End heights": "Alturas de extremos",
    "Equivalent diameter": "Diámetro equivalente",
    "Estimated stub impedance": "Impedancia estimada del stub",
    "Evidence level": "Nivel de evidencia",
    "Evidence source": "Fuente de evidencia",
    "Evidence tolerance": "Tolerancia de evidencia",
    "Model confidence": "Confianza del modelo",
    "Absolute SWR is informational. The installation return is a model proxy, not a physical counterpoise; the real coax/mast/earth path dominates SWR.": (  # noqa: E501
        "La ROE absoluta es informativa. El retorno de instalación es un proxy "
        "del modelo, no un contrapeso físico; el camino real del "
        "coaxil/mástil/tierra domina la ROE."
    ),
    "Absolute SWR is informational; the shortened preset is judged by R/X convergence.": (
        "La ROE absoluta es informativa; el preset acortado se evalúa por la convergencia de R/X."
    ),
    "Far field": "Campo lejano",
    "Feed": "Alimentación",
    "Feed network": "Red de alimentación",
    "co-simulated TL network": "Red de líneas co-simulada",
    "Splitter": "Divisor",
    "Phase-line coax": "Coaxil de línea de fase",
    "Ideal N-way splitter": "Divisor ideal de N vías",
    "From the feed network": "De la red de alimentación",
    "Reference line": "Línea de referencia",
    "Line increment": "Incremento de línea",
    "Velocity factor": "Factor de velocidad",
    "Line Z0": "Z0 de línea",
    "Splitter excess loss": "Pérdida extra del divisor",
    "Matched line loss": "Pérdida de línea adaptada",
    "Line losses": "Pérdidas de línea",
    "Feed coordinates": "Coordenadas de alimentación",
    "Feed gap": "Separación de alimentación",
    "Feed height": "Altura de alimentación",
    "Feed section": "Tramo de alimentación",
    "Feed height above ground": "Altura de alimentación sobre el suelo",
    "Feed location": "Ubicación de la alimentación",
    "Feed match": "Adaptación de alimentación",
    "Feed offset": "Desplazamiento de alimentación",
    "Feed offset below top": "Desplazamiento de alimentación bajo la parte superior",
    "Feed offset from start": "Desplazamiento de alimentación desde el inicio",
    "Feed side": "Lado de alimentación",
    "Feed transformer": "Transformador de alimentación",
    "Current balun": "Balún de corriente",
    "recorded; common-mode choking is not modeled": (
        "registrado; el choking de modo común no está modelado"
    ),
    "Balanced antenna: install a current balun/choke at the feed. Common-mode choking is not modeled.": (  # noqa: E501
        "Antena balanceada: instalá un balún/choke de corriente en la alimentación. "
        "El choking de modo común no está modelado."
    ),
    "Balanced antenna: a current balun/choke is recorded in the project. Common-mode choking is not modeled.": (  # noqa: E501
        "Antena balanceada: hay un balún/choke de corriente registrado en el proyecto. "
        "El choking de modo común no está modelado."
    ),
    "Feed wire": "Hilo de alimentación",
    "Feed/base height": "Altura de alimentación/base",
    "First leg (from wire start)": "Primer tramo (desde el inicio del hilo)",
    "Fold spacing": "Separación del plegado",
    "Folded": "Plegado",
    "Folded driven": "Alimentado plegado",
    "Folded driven element": "Elemento alimentado plegado",
    "Frequency": "Frecuencia",
    "Frequency (MHz)": "Frecuencia (MHz)",
    "Frequency plan": "Plan de frecuencia",
    "Full length": "Longitud total",
    "Gain (dBi)": "Ganancia (dBi)",
    "Generator": "Generador",
    "Ground": "Suelo",
    "Hairpin length": "Longitud del hairpin",
    "Hairpin spacing": "Separación del hairpin",
    "Height": "Altura",
    "High band": "Banda alta",
    "Horizontal length": "Longitud horizontal",
    "Horizontal segment": "Segmento horizontal",
    "Horizontal top run": "Tramo horizontal superior",
    "Included angle": "Ángulo incluido",
    "Included angles": "Ángulos incluidos",
    "Input power (W)": "Potencia de entrada (W)",
    "Leg length": "Longitud del tramo",
    "Length": "Longitud",
    "Length (m)": "Longitud (m)",
    "Limitation": "Limitación",
    "Link offset": "Desplazamiento del enlace",
    "Loading coil": "Bobina de carga",
    "Coil position": "Posición de la bobina",
    "Top section": "Tramo superior",
    "Loads": "Cargas",
    "Loop circumference": "Circunferencia del lazo",
    "Loop conductor": "Conductor del lazo",
    "Loop diameter": "Diámetro del lazo",
    "Loop side": "Lado del lazo",
    "Loops": "Lazos",
    "Low band": "Banda baja",
    "Lowest edge": "Borde más bajo",
    "Lowest tip": "Punta más baja",
    "Matching section": "Sección de adaptación",
    "Matching stub length": "Longitud del stub de adaptación",
    "Material": "Material",
    "Materials": "Materiales",
    "Max height": "Altura máxima",
    "Message": "Mensaje",
    "Metal conductor length": "Longitud del conductor metálico",
    "Min height": "Altura mínima",
    "Orientation": "Orientación",
    "Outer section": "Sección exterior",
    "Outer sections": "Secciones exteriores",
    "Overall span": "Envergadura total",
    "Pairs": "Pares",
    "Phase": "Fase",
    "Phase step": "Paso de fase",
    "Plane height": "Altura del plano",
    "Polarization": "Polarización",
    "Polygon sides": "Lados del polígono",
    "Power (W)": "Potencia (W)",
    "Project": "Proyecto",
    "R (Ω)": "R (Ω)",
    "Radial length": "Longitud de radiales",
    "Radial droop": "Inclinación de radiales",
    "Radial tip height": "Altura de las puntas de los radiales",
    "Radial wires": "Hilos radiales",
    "Radials": "Radiales",
    "Radials per element": "Radiales por elemento",
    "Radiator height": "Altura del radiador",
    "Radiator length": "Largo del radiador",
    "Reference impedance": "Impedancia de referencia",
    "Reflector": "Reflector",
    "Reflector element": "Elemento reflector",
    "Reflector half-length": "Semilongitud del reflector",
    "Reflector side": "Lado del reflector",
    "Reflector spacing": "Separación del reflector",
    "Reflector tip": "Punta del reflector",
    "Remaining leg": "Tramo restante",
    "Ring diameter": "Diámetro del anillo",
    "Ring height": "Altura del anillo",
    "Ring sides": "Lados del anillo",
    "SWR": "ROE",
    "Sag": "Flecha",
    "Second leg (from feed)": "Segundo tramo (desde la alimentación)",
    "Segmentation": "Segmentación",
    "Severity": "Severidad",
    "Side length": "Longitud del lado",
    "Sides": "Lados",
    "Simulation configuration": "Configuración de la simulación",
    "Solver executable": "Ejecutable del solver",
    "Source": "Fuente",
    "Spacing": "Separación",
    "Span": "Envergadura",
    "Stack height": "Altura de la pila",
    "Start (m)": "Inicio (m)",
    "State": "Estado",
    "Status": "Estado",
    "Stub length": "Longitud del stub",
    "Stub spacing": "Separación del stub",
    "Takeoff (°)": "Ángulo de salida (°)",
    "Tapered tips": "Puntas cónicas",
    "Termination": "Terminación",
    "Termination resistor": "Resistencia de terminación",
    "Tip gap": "Separación de puntas",
    "Top hat radius": "Radio del sombrero superior",
    "Top hat wires": "Hilos del sombrero superior",
    "Top height": "Altura superior",
    "Total conductor": "Conductor total",
    "Total conductor length": "Longitud total del conductor",
    "Total length": "Longitud total",
    "Total wire length": "Longitud total del hilo",
    "Transformer": "Transformador",
    "Transformer loss": "Pérdida del transformador",
    "Total feed-chain loss": "Pérdida total de la cadena de alimentación",
    "measured 49:1 (Squash Practice)": "49:1 medido (Squash Practice)",
    "retained; design network overrides": "retenida; la red de diseño la anula",
    "Design matching network": "Red de adaptación del diseño",
    "Design series": "Serie del diseño",
    "Design shunt": "Paralelo del diseño",
    "L network (primary side)": "Red L (lado primario)",
    "Pi network (primary side)": "Red Pi (lado primario)",
    "T network (primary side)": "Red T (lado primario)",
    "Input shunt": "Paralelo de entrada",
    "Output shunt": "Paralelo de salida",
    "Input series": "Serie de entrada",
    "Output series": "Serie de salida",
    "{value} ({status})": "{value} ({status})",
    "Matching capacitor": "Capacitor de adaptación",
    "Transformer leakage": "Fuga del transformador",
    "Project matching": "Adaptación del proyecto",
    "{network} · {state} · {position}": "{network} · {state} · {position}",
    "at feedpoint": "en el feedpoint",
    "in shack": "en la estación",
    "Feed line": "Línea de alimentación",
    "As-built record": "Registro as-built",
    "Hardware BOM": "Lista de materiales de herrajes",
    "Coils and traps": "Bobinas y trampas",
    "Construction checklist": "Lista de control de construcción",
    "Dimension": "Dimensión",
    "Actual": "Real",
    "Difference": "Diferencia",
    "Notes": "Notas",
    "Item": "Ítem",
    "Qty": "Cant.",
    "Unit": "Unidad",
    "Position": "Posición",
    "Inductance": "Inductancia",
    "Capacitance": "Capacitancia",
    "Resistance": "Resistencia",
    "Antenna conductor": "Conductor de antena",
    "End insulators": "Aisladores de extremo",
    "Element clamps": "Abrazaderas de elemento",
    "Boom": "Boom",
    "Feedpoint support / insulator": "Soporte / aislador del feedpoint",
    "Mast or support": "Mástil o soporte",
    "Coaxial connector": "Conector coaxial",
    "Balun / unun": "Balun / unun",
    "Radial wire": "Hilo de radial",
    "Ground rod": "Jabalina de tierra",
    "Trap": "Trampa",
    "Guy line / support rope": "Viento / cuerda de soporte",
    "From the conductor BOM": "De la lista de conductores",
    "Starting estimate": "Estimación inicial",
    "Use the transformer or balun in the design": "Usar el transformador o balun del diseño",
    "Radial system": "Sistema de radiales",
    "Verify the local grounding requirement": ("Verificar el requisito local de puesta a tierra"),
    "From the load table": "De la tabla de cargas",
    "Target value; verify with the solver and a measurement": (
        "Valor objetivo; verificar con el solver y una medición"
    ),
    "checklist.prepare_drawings": "Preparar el plano de construcción y la lista de hilos.",
    "checklist.check_dimensions": "Verificar cada dimensión contra el diseño antes de cortar.",
    "checklist.inspect_insulators": "Inspeccionar aisladores, soportes y herrajes.",
    "checklist.check_feedpoint": (
        "Revisar el punto de alimentación, balun/unun y alivio de tensión."
    ),
    "checklist.seal_connectors": "Sellar conectores exteriores y tender el coax de forma segura.",
    "checklist.check_supports": "Revisar mástil, vientos y distancias de seguridad.",
    "checklist.verify_grounding": "Verificar la puesta a tierra de la estación y la antena.",
    "checklist.measure_swr": "Medir ROE y resonancia con la línea instalada.",
    "checklist.record_measurement": "Registrar la sesión de medición en el proyecto.",
    "checklist.update_as_built": "Actualizar las dimensiones y notas as-built.",
    "Prepare the construction drawing and wire schedule.": (
        "Preparar el plano de construcción y la lista de hilos."
    ),
    "Check every dimension against the design before cutting.": (
        "Verificar cada dimensión contra el diseño antes de cortar."
    ),
    "Inspect insulators, supports, and hardware for damage.": (
        "Inspeccionar aisladores, soportes y herrajes."
    ),
    "Check the feedpoint, balun/unun, and strain relief.": (
        "Revisar el punto de alimentación, balun/unun y alivio de tensión."
    ),
    "Seal outdoor connectors and route the coax safely.": (
        "Sellar conectores exteriores y tender el coax de forma segura."
    ),
    "Check mast, guy lines, and clearances.": (
        "Revisar mástil, vientos y distancias de seguridad."
    ),
    "Verify station and antenna grounding.": (
        "Verificar la puesta a tierra de la estación y la antena."
    ),
    "Measure SWR and resonance with the installed feed line.": (
        "Medir ROE y resonancia con la línea instalada."
    ),
    "Record the measurement session in the project.": (
        "Registrar la sesión de medición en el proyecto."
    ),
    "Update the as-built dimensions and notes.": ("Actualizar las dimensiones y notas as-built."),
    "Installation profile": "Perfil de instalación",
    "Available height": "Altura disponible",
    "Available space": "Espacio disponible",
    "Installation orientation": "Orientación de instalación",
    "Support": "Soporte",
    "Profile ground": "Suelo del perfil",
    "Profile notes": "Notas del perfil",
    "mast": "mástil",
    "tree": "árbol",
    "building": "edificio",
    "fence": "cerca",
    "portable": "portátil",
    "other": "otro",
    "Transmission lines": "Líneas de transmisión",
    "Trap capacitance": "Capacitancia de la trampa",
    "Trap frequency": "Frecuencia de la trampa",
    "Trap inductance": "Inductancia de la trampa",
    "Trap inset": "Inserción de la trampa",
    "Trap positions": "Posiciones de las trampas",
    "Tuning capacitance": "Capacitancia de sintonía",
    "Tuning gap": "Separación de sintonía",
    "Turning radius": "Radio de giro",
    "Type": "Tipo",
    "Units": "Unidades",
    "Updated": "Actualizado",
    "Vertical element length": "Largo del elemento",
    "Vertical elements": "Elementos verticales",
    "Vertical height": "Altura vertical",
    "Vertical length": "Largo vertical",
    "Vertical section": "Sección vertical",
    "Verticals": "Verticales",
    "Wire": "Hilo",
    "Wire diameter": "Diámetro del hilo",
    "Wire height": "Altura del hilo",
    "Wire height at start": "Altura del hilo al inicio",
    "Wire height at supports": "Altura del hilo en los soportes",
    "Wire length": "Longitud del hilo",
    "Wires": "Hilos",
    "X (Ω)": "X (Ω)",
    "|Z| (Ω)": "|Z| (Ω)",
    "Ø (mm)": "Ø (mm)",
    # Report section headings.
    "Band patterns": "Patrones por banda",
    "Band summary": "Resumen por banda",
    "Diagnostics": "Diagnósticos",
    "Gain and efficiency": "Ganancia y eficiencia",
    "Impedance": "Impedancia",
    "Resonance": "Resonancia",
    "Wilkinson splitter input (primary); every level is a network port": (
        "Entrada del divisor Wilkinson (principal); cada nivel es un puerto de red"
    ),
    "Wilkinson N-port network": "Red Wilkinson N-port",
    "Divider design frequency": "Frecuencia de diseño del divisor",
    "Branch impedance": "Impedancia de rama",
    "Isolation resistors": "Resistencias de aislación",
    "Divider model": "Modelo del divisor",
    "Level matching": "Matching por nivel",
    "ideal quarter-wave branches and star resistors": (
        "ramas ideales de cuarto de onda y resistencias en estrella"
    ),
    "set by the feed network": "fijado por la red de alimentación",
    # Result-summary rows.
    "Balun/unun loss": "Pérdida del balun/unun",
    "Feed-line loss": "Pérdida de la línea de alimentación",
    "Link metrics at": "Métricas de enlace en",
    "Max directivity": "Directividad máxima",
    "Max power gain": "Ganancia máxima de potencia",
    "Max power gain (NEC)": "Ganancia máxima de potencia (NEC)",
    "2:1 SWR bandwidth": "Ancho de banda ROE 2:1",
    "HPBW azimuth": "HPBW azimut",
    "HPBW elevation": "HPBW elevación",
    "Front-to-back": "Relación delante/atrás",
    "Sidelobe level": "Nivel de lóbulo lateral",
    "Takeoff angle": "Ángulo de salida",
    "Axial ratio": "Relación axial",
    "Polarization sense": "Sentido de polarización",
    "Co-pol CP gain": "Ganancia CP copolar",
    "Cross-pol discrimination": "Discriminación cross-pol",
    "Pattern resolution": "Resolución del patrón",
    "unbracketed (sweep edge)": "sin bordes (límite del barrido)",
    "unavailable": "no disponible",
    "infinite": "infinita",
    "Max realized gain": "Ganancia realizada máxima",
    "Mismatch loss": "Pérdida por desadaptación",
    "Network loss": "Pérdida de la red",
    # Dynamic table labels.
    "Load {index} ({kind})": "Carga {index} ({kind})",
    "Transmission line {index}": "Línea de transmisión {index}",
    # Common values and short status phrases.
    "Aluminum": "Aluminio",
    "Beverage": "Beverage",
    "Bobtail curtain": "Cortina bobtail",
    "Copper": "Cobre",
    "Stainless steel 304": "Acero inoxidable 304",
    "Discone": "Discono",
    "Half square": "Medio cuadrado",
    "Hexbeam": "Hexbeam",
    "J Pole": "J Pole",
    "Moxon rectangle": "Rectángulo Moxon",
    "Phased vertical array": "Arreglo vertical en fase",
    "Quad beam": "Lazo cuádruple",
    "Slim Jim": "Slim Jim",
    "Trapped Yagi": "Yagi con trampas",
    "Yagi": "Yagi",
    "Zepp": "Zepp",
    "custom wires": "hilos personalizados",
    "fan dipole": "dipolo en abanico",
    "folded dipole": "dipolo plegado",
    "free_space": "espacio libre",
    "horizontal": "horizontal",
    "inverted L": "L invertida",
    "inverted-V": "V invertida",
    "loop": "lazo",
    "magnetic loop": "lazo magnético",
    "off-center-fed dipole": "dipolo alimentado descentrado",
    "perfect": "plano perfecto",
    "series": "serie",
    "terminated folded dipole (T2FD)": "dipolo plegado terminado (T2FD)",
    "trap dipole": "dipolo con trampas",
    "vertical": "vertical",
    "wire dipole": "dipolo de hilo",
    "yes": "sí",
    # Report phrases.
    "No band patterns available.": "No hay patrones por banda disponibles.",
    "No diagnostics.": "Sin diagnósticos.",
    "No far-field pattern available.": "No hay patrón de campo lejano disponible.",
    "3D pattern unavailable: the far-field data does not contain a 2D angular grid.": (
        "Patrón 3D no disponible: los datos de campo lejano no contienen una grilla angular 2D."
    ),
    "3D far-field pattern": "Patrón 3D de campo lejano",
    "Static total-gain wireframe at the report pattern frequency. "
    "The separate geometry figure shows the antenna orientation.": (
        "Tramado estático de ganancia total en la frecuencia del patrón del "
        "informe. La figura de geometría separada muestra la orientación de la "
        "antena."
    ),
    "Total-gain pattern at {frequency:.3f} MHz · stored sampling {theta_count}x{phi_count}": (
        "Patrón de ganancia total a {frequency:.3f} MHz · muestreo almacenado "
        "{theta_count}x{phi_count}"
    ),
    "Max {gain:.2f} dBi at θ={theta:.0f}°, φ={phi:.0f}°. The geometry figure shows orientation.": (
        "Máximo {gain:.2f} dBi en θ={theta:.0f}°, φ={phi:.0f}°. La figura de "
        "geometría muestra la orientación."
    ),
    "Max {gain:.2f} dBi at θ={theta:.0f}°, φ={phi:.0f}°": (
        "Máximo {gain:.2f} dBi en θ={theta:.0f}°, φ={phi:.0f}°"
    ),
    "Gain": "Ganancia",
    "dBi": "dBi",
    "No geometry figure available.": "No hay figura de geometría disponible.",
    "No azimuth cut available.": "No hay corte de azimut disponible.",
    "No elevation cut available.": "No hay corte de elevación disponible.",
    "No resonance in the sweep.": "No hay resonancia en el barrido.",
    "No result yet.": "Todavía no hay resultado.",
    "disabled": "deshabilitado",
    "enabled": "habilitado",
    "not recorded": "sin registrar",
    "unknown": "desconocido",
    # Chart axis labels.
    "Elevation θ (°)": "Elevación θ (°)",
    "Azimuth φ (°)": "Azimut φ (°)",
    "Power gain (dBi)": "Ganancia de potencia (dBi)",
    "Azimuth cut at θ = {angle:.0f}°": "Corte de azimut en θ = {angle:.0f}°",
    "Elevation cut at φ = {angle:.0f}°": "Corte de elevación en φ = {angle:.0f}°",
    "{band} pattern": "Patrón de {band}",
    # Construction-note templates.
    " A beta/hairpin stub is connected across the {spacing:.4f} m driven-element gap and shorted {length:.4f} m along the boom.": (  # noqa: E501
        " Un stub beta/hairpin se conecta a través de la separación de "
        "{spacing:.4f} m del elemento alimentado y se cortocircuita a "
        "{length:.4f} m sobre el boom."
    ),
    " Add {count} horizontal top-hat wires of {radius:.4f} m at the radiator top.": (
        " Agregá {count} hilos horizontales de sombrero superior de "
        "{radius:.4f} m en la parte superior del radiador."
    ),
    " The director loop is {side} m per side at {spacing} m in front of the driven loop.": (
        " El lazo director tiene {side} m por lado y está a {spacing} m "
        "delante del lazo alimentado."
    ),
    " The driven element is folded with {spacing:.4f} m spacing and two end connectors. Feed one conductor at its center; the second conductor remains passive.": (  # noqa: E501
        " El elemento alimentado está plegado con una separación de "
        "{spacing:.4f} m y dos conectores de extremo. Alimentá un conductor "
        "en su centro; el segundo conductor queda pasivo."
    ),
    " Feed the folded element through a {ratio}:1 transformer.": (
        " Alimentá el elemento plegado a través de un transformador {ratio}:1."
    ),
    "A wire reflector sits {spacing:.4f} m behind the driven plane.": (
        "Un reflector de hilo está a {spacing:.4f} m detrás del plano alimentado."
    ),
    "AntennaDesk construction sheet · SI units (m, MHz, Ω)": (
        "Hoja de construcción de AntennaDesk · unidades SI (m, MHz, Ω)"
    ),
    "AntennaDesk · GPL-3.0-or-later · Use the browser print dialog to save this sheet as PDF.": (
        "AntennaDesk · GPL-3.0-or-later · Usá el diálogo de impresión del "
        "navegador para guardar esta hoja como PDF."
    ),
    "Build a Moxon rectangle with {width} m elements, {depth} m spacing, and bent tips leaving a {gap} m gap.": (  # noqa: E501
        "Construí un rectángulo Moxon con elementos de {width} m, una separación "
        "de {depth} m y puntas dobladas que dejan una separación de {gap} m."
    ),
    "Build an M-shaped driver with {driver} m half-lengths and a U-shaped reflector with {reflector} m half-lengths on a six-spreader frame with a {turning} m turning radius. Set the tip gap to {tip_gap} m and feed the center of the M. The reflector wraps the rear three sides; the frame, spreader sag, feed balun, and multi-band nesting are not modeled.": (  # noqa: E501
        "Construí un excitador en forma de M con semilongitudes de {driver} m y "
        "un reflector en forma de U con semilongitudes de {reflector} m sobre un "
        "marco de seis separadores con un radio de giro de {turning} m. Ajustá la "
        "separación de puntas a {tip_gap} m y alimentá el centro de la M. El "
        "reflector rodea los tres lados traseros; el marco, la flecha de los "
        "separadores, el balun de alimentación y el anidamiento multibanda no "
        "están modelados."
    ),
    "Build a {length} m vertical radiator with a {diameter} m matching ring at {ring_height} m above ground.": (  # noqa: E501
        "Construí un radiador vertical de {length} m con un anillo de adaptación "
        "de {diameter} m a {ring_height} m sobre el suelo."
    ),
    "Build a {kind} with a {radiator} m radiator and a {stub} m stub spaced {spacing} m.": (
        "Construí un {kind} con un radiador de {radiator} m y un stub de {stub} m "
        "separado {spacing} m."
    ),
    "Build a {kind} with {count} vertical elements joined at the top. {wire_note} Keep the bottom ends insulated from ground and feed {feed_point}. The feed is {feed_offset} m below the top junction at {feed_height} m above ground.": (  # noqa: E501
        "Construí un {kind} con {count} elementos verticales unidos en la parte "
        "superior. {wire_note} Mantené los extremos inferiores aislados del suelo "
        "y alimentá {feed_point}. La alimentación está {feed_offset} m debajo de "
        "la unión superior, a {feed_height} m sobre el suelo."
    ),
    "Build {count} Yagi elements with the driven element at {driven} m and the reflector at {reflector} m. Fit a parallel LC trap on each side of every element at {inset} m from its center, using {inductance} µH and the capacitance for {frequency} MHz. The trap model is ideal; boom mounting, trap loss, feed line, and matching network are not modeled.": (  # noqa: E501
        "Construí {count} elementos Yagi con el elemento alimentado a {driven} m y "
        "el reflector a {reflector} m. Colocá una trampa LC paralela a cada lado "
        "de cada elemento a {inset} m de su centro, usando {inductance} µH y la "
        "capacitancia para {frequency} MHz. El modelo de trampa es ideal; el "
        "montaje en el boom, la pérdida de la trampa, la línea de alimentación y "
        "la red de adaptación no están modelados."
    ),
    "One shared mast runs from ground to the top boom and the guys attach to its top.": (
        "Un mástil compartido va del suelo al boom superior y los vientos se anclan a su punta."
    ),
    "The shared mast and guys are not modeled.": (
        "El mástil compartido y los vientos no están modelados."
    ),
    "Build {count} identical Yagis on one vertical stack with {spacing} m between level booms. The splitter node is a 1 cm numerical feed point above the stack, not an antenna conductor. Feed every level through a {count}-way splitter and a lossless transmission-line network: level 1 is {reference} m, and each higher level adds {increment} m of {velocity} velocity-factor line. Record {loss} dB of splitter excess loss and {line_loss} dB/100 m of matched line loss plus a per-port mismatch correction, applied to realized gain. The solver co-simulates the network and reports every port; the primary SWR is the lossless network input and splitter internal mismatch is not modeled. Fit each level as a complete Yagi from the base element table. {mast_note} Per-level matching is not modeled; verify the combined pattern and match.": (  # noqa: E501
        "Construí {count} Yagis idénticos en una pila vertical con {spacing} m "
        "entre los boms de los niveles. El nodo del divisor es un punto de "
        "alimentación numérico de 1 cm sobre la pila, no un "
        "conductor de antena. Alimentá cada nivel mediante un divisor de {count} "
        "vías y una red de líneas de transmisión sin pérdidas: el nivel 1 tiene "
        "{reference} m y cada nivel superior agrega {increment} m de línea con "
        "factor de velocidad {velocity}. Registrá {loss} dB de pérdida extra del "
        "divisor y {line_loss} dB/100 m de pérdida de línea adaptada más una "
        "corrección por desadapto de cada puerto, aplicada a la ganancia "
        "realizada. El solver co-simula la red e informa cada puerto; "
        "la ROE primaria es la entrada de la red sin pérdidas y no se modela el "
        "desajuste interno del divisor. Armá cada nivel como un Yagi completo a "
        "partir de la tabla de elementos base. {mast_note} El ajuste por nivel no "
        "está modelado; verificá el patrón combinado y el ajuste."
    ),
    "Build {count} identical Yagis on one vertical stack with {spacing} m between level booms. The splitter is an equal {count}-way Wilkinson: {branch} Ω quarter-wave branches and a star of {count} {isolation} Ω isolation resistors, designed at {design} MHz. Feed line lengths are {lengths}, with {velocity} velocity factor and {z0} Ω characteristic impedance. Record {loss} dB of splitter excess loss and {line_loss} dB/100 m of matched line loss plus a per-port mismatch correction, applied to realized gain. The N-port solver combines the divider with the antenna port admittance; the pattern is reconstructed from the solved port voltages. Branches and resistors are ideal; component loss, tolerance, and broadband behavior are not modeled. Fit each level as a complete Yagi from the base element table. {mast_note} Per-level matching is not modeled; verify the combined pattern and match.": (  # noqa: E501
        "Construí {count} Yagis idénticos en una pila vertical con {spacing} m "
        "entre los boms de los niveles. El divisor es un Wilkinson equilibrado de "
        "{count} vías: ramas de cuarto de onda de {branch} Ω y una estrella de "
        "{count} resistencias de aislación de {isolation} Ω, diseñado a "
        "{design} MHz. Los largos de línea son {lengths}, con factor de velocidad "
        "{velocity} e impedancia característica {z0} Ω. Registrá {loss} dB de "
        "pérdida extra del divisor y {line_loss} dB/100 m de pérdida de línea "
        "adaptada más una corrección por desadapto de cada puerto, aplicada a la "
        "ganancia realizada. El solver N-port combina el divisor con la admitancia "
        "de los puertos de la antena; el patrón se reconstruye desde las tensiones "
        "de puerto resueltas. Las ramas y resistencias son ideales; no se modelan "
        "pérdida, tolerancia ni comportamiento de banda ancha. Armá cada nivel como "
        "un Yagi completo a partir de la tabla de elementos base. {mast_note} El "
        "ajuste por nivel no está modelado; verificá el patrón combinado y el ajuste."
    ),
    "Build {count} identical Yagis on one vertical stack with {spacing} m between level booms. Level 1 is the primary feed; drive levels 2 to {last} with a {ratio} relative amplitude. Feed the levels through a {count}-way splitter and phase lines: level 1 is {reference} m, and each higher level adds {increment} m of {velocity} velocity-factor line. Record {loss} dB of splitter excess loss. The line impedance transformation and line loss are not modeled; the solver uses ideal voltage sources. Fit each level as a complete Yagi from the base element table. {mast_note} Per-level matching is not modeled; verify the combined pattern and match.": (  # noqa: E501
        "Construí {count} Yagis idénticos en una pila vertical con {spacing} m "
        "entre los boms de los niveles. El nivel 1 es la alimentación principal; "
        "excitá los niveles 2 a {last} con una amplitud relativa de {ratio}. "
        "Alimentá los niveles mediante un divisor de {count} vías y líneas de "
        "fase: el nivel 1 tiene {reference} m y cada nivel superior agrega "
        "{increment} m de línea con factor de velocidad {velocity}. Registrá "
        "{loss} dB de pérdida extra del divisor. La transformación de "
        "impedancia y la pérdida de línea no están modeladas; el solver usa "
        "fuentes de tensión ideales. Armá cada nivel como un Yagi completo a "
        "partir de la tabla de elementos base. {mast_note} El ajuste por nivel no "
        "está modelado; verificá el patrón combinado y el ajuste."
    ),
    "Build {count} identical Yagis on one vertical stack with {spacing} m "
    "between level booms. Level 1 is the primary feed; drive levels 2 to "
    "{last} as ideal sources with a {phase}° phase step and {ratio} relative "
    "amplitude. Fit each level as a complete Yagi from the base element "
    "table. The power splitter, phase lines, splitter loss, and per-level "
    "matching are not modeled. {mast_note} Verify the combined pattern and "
    "match.": (
        "Construí {count} Yagis idénticos en una pila vertical con {spacing} m "
        "entre los boms de los niveles. El nivel 1 es la alimentación principal; "
        "excitá los niveles 2 a {last} como fuentes ideales con un escalón de fase "
        "de {phase}° y una amplitud relativa de {ratio}. Armá cada nivel como un "
        "Yagi completo a partir de la tabla de elementos base. El divisor de "
        "potencia, las líneas de fase, las pérdidas del divisor y el ajuste por "
        "nivel no están modelados. {mast_note} Verificá el patrón combinado y el "
        "ajuste."
    ),
    "Build {count} cone wires from the apex at {apex} m down to a base ring of {radius} m radius at {base} m. Add {count} disc wires of {disc} m above the apex with a {gap} m feed gap. Feed across that gap. The cone and disc are wire approximations; the coax, mast, and solid surfaces are not modeled.": (  # noqa: E501
        "Construí {count} hilos de cono desde el vértice a {apex} m hasta un "
        "anillo de base de radio {radius} m a {base} m. Agregá {count} hilos de "
        "disco de {disc} m sobre el vértice con una separación de alimentación de "
        "{gap} m. Alimentá a través de esa separación. El cono y el disco son "
        "aproximaciones de hilos; el coaxil, el mástil y las superficies sólidas "
        "no están modelados."
    ),
    "Build {count} parallel elements on a {boom} m boom. Feed the center of element {driven}.{folded_note}{match_note}": (  # noqa: E501
        "Construí {count} elementos paralelos en un boom de {boom} m. Alimentá el "
        "centro del elemento {driven}.{folded_note}{match_note}"
    ),
    "Cut {count} straight elements with the longest at {longest} m and the shortest at {shortest} m. Space them along the boom using the generated schedule, with the rear element at the back. Run the transposed phase line between adjacent element centers with a crossover between each pair; short the rear element center and feed the front element center through the {ratio}:1 transformer. The phase line is an ideal lossless two-port; the balun, feed-line loss, rear stub, boom, mast, and construction tolerances are not modeled.": (  # noqa: E501
        "Cortá {count} elementos rectos con el más largo en {longest} m y el más "
        "corto en {shortest} m. Sepalos a lo largo del boom usando la tabla "
        "generada, con el elemento trasero atrás. Tendé la línea de fase "
        "transpuesta entre los centros de elementos adyacentes con un cruce "
        "entre cada par; cortocircuitá el centro del elemento trasero y "
        "alimentá el centro del elemento frontal a través del transformador "
        "{ratio}:1. La línea de fase es un cuadripolo ideal sin pérdidas; no se "
        "modelan el balun, la pérdida de línea, el stub trasero, el boom, el "
        "mástil ni las tolerancias de construcción."
    ),
    "Build {count} square loops with the driven loop at {side} m per side and the reflector at {reflector} m per side. Set the reflector {spacing} m behind the driven loop.{director_note} Feed the midpoint of the driven loop's left vertical side and keep the loops square. The boom, spreaders, mast, and any additional matching network are not modeled; the feed transformer is ideal. Tune the match for the installed antenna.{transformer_note}": (  # noqa: E501
        "Construí {count} lazos cuadrados con el lazo alimentado de {side} m por "
        "lado y el reflector de {reflector} m por lado. Colocá el reflector a "
        "{spacing} m detrás del lazo alimentado.{director_note} Alimentá el punto "
        "medio del lado vertical izquierdo del lazo alimentado y mantené los lazos "
        "cuadrados. El boom, los separadores, el mástil y cualquier red de "
        "adaptación adicional no están modelados; el transformador de alimentación "
        "es ideal. Ajustá la adaptación para la antena instalada.{transformer_note}"
    ),
    "Build {count} square loops with {side} m sides. Join them at the shared horizontal rails, starting at {base} m above ground, and feed the midpoint of the central rail at {feed_height} m. {reflector_note} The quarter-wave side and eighth-wave reflector spacing are starting dimensions; tune them for the installation.{transformer_note}": (  # noqa: E501
        "Construí {count} lazos cuadrados de {side} m por lado. Unilos en los "
        "rieles horizontales compartidos, comenzando a {base} m sobre el suelo, y "
        "alimentá el punto medio del riel central a {feed_height} m. "
        "{reflector_note} El lado de cuarto de onda y la separación de reflector "
        "de octavo de onda son dimensiones de partida; ajustalos para la "
        "instalación.{transformer_note}"
    ),
    " Feed the midpoint through a {ratio}:1 transformer.": (
        " Alimentá el punto medio a través de un transformador {ratio}:1."
    ),
    " Feed the midpoint directly; no transformer is modeled.": (
        " Alimentá el punto medio directamente; no se modela transformador."
    ),
    "Build {count} vertical radiators of {length} m, spaced {spacing} m along one line, with their bases at {base} m above ground. Fit {radials} radials of {radial_length} m to each base. Drive the first vertical as the primary feed and the remaining verticals with the listed phase and amplitude steps. The combining network is ideal and is not included; use an explicit feed network and verify the match.": (  # noqa: E501
        "Construí {count} radiadores verticales de {length} m, separados "
        "{spacing} m a lo largo de una línea, con sus bases a {base} m sobre el "
        "suelo. Colocá {radials} radiales de {radial_length} m en cada base. "
        "Alimentá la primera vertical como alimentación principal y las verticales "
        "restantes con los pasos de fase y amplitud indicados. La red combinadora "
        "es ideal y no está incluida; usá una red de alimentación explícita y "
        "verificá la adaptación."
    ),
    "Custom geometry: use the wire table and feed point above. Verify every connection and the feed gap before construction.": (  # noqa: E501
        "Geometría personalizada: usá la tabla de hilos y el punto de "
        "alimentación de arriba. Verificá cada conexión y la separación de "
        "alimentación antes de construir."
    ),
    "Cut one conductor to {circumference} m and close it into {sides} equal sides of {side} m in a {plane} plane. Feed the midpoint of the first side.": (  # noqa: E501
        "Cortá un conductor de {circumference} m y cerralo en {sides} lados "
        "iguales de {side} m en un plano {plane}. Alimentá el punto medio del "
        "primer lado."
    ),
    "Cut one conductor to {conductor_length} m. Support the ends at {height} m and let the center sag by {sag} m; the feed is at the lowest point, {feed_height} m above ground. The sagged shape is approximated by straight NEC segments between the sampled points.": (  # noqa: E501
        "Cortá un conductor de {conductor_length} m. Sostené los extremos a "
        "{height} m y dejá que el centro cuelgue {sag} m; la alimentación queda en "
        "el punto más bajo, a {feed_height} m sobre el suelo. La forma con flecha "
        "se aproxima con segmentos NEC rectos entre los puntos muestreados."
    ),
    "Cut one conductor to {total} m. Feed it {offset} m from the start ({percent}% of its length).": (  # noqa: E501
        "Cortá un conductor de {total} m. Alimentalo a {offset} m desde el inicio "
        "({percent}% de su longitud)."
    ),
    "Cut one conductor to {total} m. Install {vertical} m vertically with the base {base} m above ground, then run the remaining {horizontal} m horizontally at {top} m. Feed the base of the vertical section.": (  # noqa: E501
        "Cortá un conductor de {total} m. Instalá {vertical} m en vertical con la "
        "base a {base} m sobre el suelo, luego tendé los {horizontal} m restantes "
        "en horizontal a {top} m. Alimentá la base de la sección vertical."
    ),
    "Cut one conductor to {total} m. Mark the trap positions at {left} m and {right} m from the start, leaving a {inner} m center section. Install parallel LC traps tuned to {frequency} MHz ({inductance} µH, {capacitance} pF). Feed the center of the element.": (  # noqa: E501
        "Cortá un conductor de {total} m. Marcá las posiciones de las trampas a "
        "{left} m y {right} m desde el inicio, dejando una sección central de "
        "{inner} m. Instalá trampas LC paralelas sintonizadas a {frequency} MHz "
        "({inductance} µH, {capacitance} pF). Alimentá el centro del elemento."
    ),
    "Cut one dipole conductor to {length} m and install it at {height} m. Add a short source stub at the center and a {line_length} m, {impedance} Ω matching line. The line velocity factor is {velocity}; the published dimensions are starting points.": (  # noqa: E501
        "Cortá un conductor de dipolo de {length} m e instalalo a {height} m. "
        "Agregá un stub corto de fuente en el centro y una línea de adaptación de "
        "{line_length} m y {impedance} Ω. El factor de velocidad de la línea es "
        "{velocity}; las dimensiones publicadas son puntos de partida."
    ),
    "Cut one wire to {length} m and feed it at one end. The feed is at {feed_height} m and the far end at {end_height} m. Use a {ratio}:1 transformer; the counterpoise is {counterpoise}.": (  # noqa: E501
        "Cortá un hilo de {length} m y alimentalo en un extremo. La alimentación "
        "está a {feed_height} m y el extremo lejano a {end_height} m. Usá un "
        "transformador {ratio}:1; el contrapeso es {counterpoise}."
    ),
    "Cut one wire to {length} m. Fit the {inductance} µH loading coil at {offset} m from the feed; the remaining {top} m is the top section. Use a {ratio}:1 transformer and the matching unit described below; the counterpoise is {counterpoise}.": (  # noqa: E501
        "Cortá un hilo de {length} m. Colocá la bobina de carga de {inductance} µH "
        "a {offset} m de la alimentación; los {top} m restantes son el tramo "
        "superior. Usá un transformador {ratio}:1 y la unidad de adaptación "
        "descrita abajo; el contrapeso es {counterpoise}."
    ),
    "The first {length} m is a fixed feed section of the same wire; do not cut a separate conductor.": (  # noqa: E501
        "Los primeros {length} m son un tramo de alimentación fijo del mismo hilo; "
        "no cortes un conductor separado."
    ),
    "The {length} m installation return is a model proxy for the coax/mast/earth path, not a physical radial.": (  # noqa: E501
        "El retorno de instalación de {length} m es un proxy de modelo para el camino "
        "del coaxil/mástil/tierra, no una radial física."
    ),
    "The {capacitance} pF capacitor is an ideal shunt across the transformer primary. The {leakage} µH leakage is a starting estimate; measure your transformer. Core loss, capacitor ESR, and winding capacitance are not modeled.": (  # noqa: E501
        "El capacitor de {capacitance} pF es un shunt ideal en el primario del "
        "transformador. La fuga de {leakage} µH es una estimación inicial; medí tu "
        "transformador. Las pérdidas del núcleo, el ESR del capacitor y la capacidad "
        "de los bobinados no están modelados."
    ),
    "Cut the full {total} m wire and mark the link positions at {offset} m either side of the center. Feed the center. {coil_note} The coil model is an ideal series R-L load; tune it for the installed height and ground.": (  # noqa: E501
        "Cortá el hilo completo de {total} m y marcá las posiciones de enlace a "
        "{offset} m a cada lado del centro. Alimentá el centro. {coil_note} El "
        "modelo de bobina es una carga R-L serie ideal; sintonizala para la altura "
        "y el suelo instalados."
    ),
    "Cut the radiator to {radiator} m and two matching-stub conductors to {stub} m, spaced {spacing} m. Join the stub conductors at the base and feed the center of that connector; leave the antenna end of the second conductor open. The estimated stub impedance is {impedance} Ω. The 1:1 common-mode choke is a construction requirement and is not part of the NEC model.": (  # noqa: E501
        "Cortá el radiador a {radiator} m y dos conductores de stub de adaptación "
        "a {stub} m, separados {spacing} m. Uní los conductores del stub en la "
        "base y alimentá el centro de ese conector; dejá abierto el extremo de "
        "antena del segundo conductor. La impedancia estimada del stub es "
        "{impedance} Ω. El choke de modo común 1:1 es un requisito de construcción "
        "y no forma parte del modelo NEC."
    ),
    "Cut the radiator to {radiator} m and two matching-stub conductors to {stub} m. Join one stub conductor to the radiator, leave the second open at the antenna end, and join both at the base connector. Feed the middle of the base connector through a 1:1 common-mode choke. The choke and coaxial feed are not modeled.": (  # noqa: E501
        "Cortá el radiador a {radiator} m y dos conductores de stub de adaptación "
        "a {stub} m. Uní un conductor del stub al radiador, dejá el segundo "
        "abierto en el extremo de antena y uní ambos en el conector de base. "
        "Alimentá el centro del conector de base a través de un choke de modo "
        "común 1:1. El choke y la alimentación coaxil no están modelados."
    ),
    "Cut the two legs to the dimensions above, leaving a small feed gap at the center. The feed point is {feed_offset} m from the start of the wire and {other_leg} m from the end.": (  # noqa: E501
        "Cortá los dos tramos a las dimensiones de arriba, dejando una pequeña "
        "separación de alimentación en el centro. El punto de alimentación está a "
        "{feed_offset} m desde el inicio del hilo y a {other_leg} m desde el "
        "extremo."
    ),
    "Cut three vertical wires of {height:.4f} m and two top wires of {segment:.4f} m each.": (
        "Cortá tres hilos verticales de {height:.4f} m y dos hilos superiores de "
        "{segment:.4f} m cada uno."
    ),
    "Cut two equal conductors of {length} m and two end connectors of {spacing} m. Join them at both ends to form a folded loop. Feed the midpoint of one conductor through a {ratio}:1 transformer. Install a {resistance} Ω non-inductive resistor at the midpoint of the other conductor, opposite the feed point. The total conductor length is {total} m.": (  # noqa: E501
        "Cortá dos conductores iguales de {length} m y dos conectores de extremo "
        "de {spacing} m. Unilos en ambos extremos para formar un lazo plegado. "
        "Alimentá el punto medio de un conductor a través de un transformador "
        "{ratio}:1. Instalá una resistencia no inductiva de {resistance} Ω en el "
        "punto medio del otro conductor, opuesta al punto de alimentación. La "
        "longitud total del conductor es {total} m."
    ),
    "Cut two equal driven elements of {total} m and two end connectors of {spacing} m. Join them at both ends and feed the center of one element. The total conductor length is {conductor} m.": (  # noqa: E501
        "Cortá dos elementos alimentados iguales de {total} m y dos conectores de "
        "extremo de {spacing} m. Unilos en ambos extremos y alimentá el centro de "
        "un elemento. La longitud total del conductor es {conductor} m."
    ),
    "Cut two equal driven elements of {total} m and two end connectors of {spacing} m. Join them at both ends and feed the center of one element through a {ratio}:1 transformer. The total conductor length is {conductor} m.": (  # noqa: E501
        "Cortá dos elementos alimentados iguales de {total} m y dos conectores de "
        "extremo de {spacing} m. Unilos en ambos extremos y alimentá el centro de "
        "un elemento a través de un transformador {ratio}:1. La longitud total del "
        "conductor es {conductor} m."
    ),
    "Cut one conductor to {circumference} m and close it into {sides} equal sides of {side} m in a {plane} plane. Feed the midpoint of the first side through a {ratio}:1 transformer.": (  # noqa: E501
        "Cortá un conductor de {circumference} m y cerralo en {sides} lados iguales "
        "de {side} m en un plano {plane}. Alimentá el punto medio del primer lado a "
        "través de un transformador {ratio}:1."
    ),
    "Cut two legs of {leg} m and join them at the apex with an included angle of {angle}°. The apex is {apex} m above ground.": (  # noqa: E501
        "Cortá dos tramos de {leg} m y unilos en el vértice con un ángulo incluido "
        "de {angle}°. El vértice está a {apex} m sobre el suelo."
    ),
    "Cut two vertical wires of {height:.4f} m and one top wire of {horizontal:.4f} m.": (
        "Cortá dos hilos verticales de {height:.4f} m y un hilo superior de {horizontal:.4f} m."
    ),
    "Cut {count} dipole pairs with lengths {lengths} at included angles {angles}. Join all pairs at the common apex and feed there. The ends sit at {end_heights} above ground.": (  # noqa: E501
        "Cortá {count} pares de dipolos con longitudes {lengths} en ángulos "
        "incluidos {angles}. Uní todos los pares en el vértice común y alimentá "
        "allí. Los extremos quedan a {end_heights} sobre el suelo."
    ),
    "Fit a {resistance:.1f} Ω resistor from the far end to a ground rod.": (
        "Colocá una resistencia de {resistance:.1f} Ω desde el extremo lejano a una jabalina."
    ),
    "Fit two {inductance:.3f} µH loading coils at {offset:.4f} m either side of the feed; each coil has {resistance:.3f} Ω series resistance.": (  # noqa: E501
        "Colocá dos bobinas de carga de {inductance:.3f} µH a {offset:.4f} m a "
        "cada lado de la alimentación; cada bobina tiene {resistance:.3f} Ω de "
        "resistencia serie."
    ),
    "Form a {diameter} m loop with {sides} sides. Leave a {gap} m gap at the top and install a {capacitance} pF capacitor with about {esr} Ω ESR. Feed the midpoint of the bottom side. Conductor loss comes from the selected material and wire radius; a coupling loop and the capacitor voltage are not modeled.": (  # noqa: E501
        "Formá un lazo de {diameter} m con {sides} lados. Dejá una separación de "
        "{gap} m en la parte superior e instalá un capacitor de {capacitance} pF "
        "con aproximadamente {esr} Ω de ESR. Alimentá el punto medio del lado "
        "inferior. La pérdida del conductor proviene del material y el radio de "
        "hilo seleccionados; un lazo de acoplamiento y la tensión del capacitor no "
        "están modelados."
    ),
    "Install a {length} m vertical radiator with its base {base} m above ground. Add {radials} radials of {radial_length} m.{radial_droop_note}{top_hat_note}": (  # noqa: E501
        "Instalá un radiador vertical de {length} m con su base a {base} m sobre "
        "el suelo. Agregá {radials} radiales de {radial_length} m."
        "{radial_droop_note}{top_hat_note}"
    ),
    " Slope them {droop}° downward; the tips are {tip} m above ground.": (
        " Inclinálos {droop}° hacia abajo; las puntas quedan a {tip} m sobre el suelo."
    ),
    " Keep them horizontal at the base plane.": (" Mantenelos horizontales en el plano de base."),
    "Leave the far end open for a bidirectional receiving pattern.": (
        "Dejá el extremo lejano abierto para un patrón de recepción bidireccional."
    ),
    "Leave the links open and use only the center section.": (
        "Dejá los enlaces abiertos y usá solo la sección central."
    ),
    "No loading coils are fitted.": "No se instalan bobinas de carga.",
    "Run one horizontal wire of {length} m at {height} m above ground. Connect a short vertical feed stub from the near end to ground and feed it through a {ratio:.1f}:1 transformer. Keep the wire straight. {termination_note} The one-wavelength starting length, termination value, and transformer ratio are assumptions; the pattern and receiving performance are not independently validated.": (  # noqa: E501
        "Tendé un hilo horizontal de {length} m a {height} m sobre el suelo. "
        "Conectá un tramo vertical corto de alimentación desde el extremo "
        "cercano a tierra y alimentalo a través de un transformador "
        "{ratio:.1f}:1. Mantené el hilo recto. {termination_note} La longitud "
        "inicial de una longitud de onda, el valor de terminación y la relación "
        "del transformador son supuestos; el patrón y el rendimiento de "
        "recepción no están validados independientemente."
    ),
    "SWR ({impedance:g} Ω)": "ROE ({impedance:g} Ω)",
    "SWR ≤ 2 bandwidth": "Ancho de banda ROE ≤ 2",
    "This variant has no reflector.": "Esta variante no tiene reflector.",
    "Trim and re-measure after installation. Real ground, supports, feed line, and nearby objects can shift the result. A low SWR does not prove high efficiency or a useful radiation pattern.": (  # noqa: E501
        "Recortá y volvé a medir después de la instalación. El suelo real, los "
        "soportes, la línea de alimentación y los objetos cercanos pueden "
        "modificar el resultado. Una ROE baja no garantiza alta eficiencia ni un "
        "patrón de radiación útil."
    ),
    "beta / hairpin": "beta / hairpin",
    "center of driven element": "centro del elemento alimentado",
    "center of the M driver": "centro del excitador en M",
    "across the apex gap": "a través de la separación del vértice",
    "driven element center": "centro del elemento alimentado",
    "driven loop side midpoint": "punto medio del lado del lazo alimentado",
    "first vertical (primary)": "primera vertical (principal)",
    "near end": "extremo cercano",
    "near end, ground-referenced stub": "extremo cercano, tramo referido a tierra",
    "construction sheet": "hoja de construcción",
    "midpoint of the first side": "punto medio del primer lado",
    "none": "ninguno",
    "the top corner of one outer vertical": "la esquina superior de una vertical exterior",
    "the top junction of the center vertical and the top wires": (
        "la unión superior de la vertical central y los hilos superiores"
    ),
    "{length:.4f} m each": "{length:.4f} m cada uno",
    "{length} each": "{length} cada uno",
    "{offset:.4f} m from feed": "{offset:.4f} m desde la alimentación",
    "{left:.4f} m, {right:.4f} m from wire start": (
        "{left:.4f} m, {right:.4f} m desde el inicio del hilo"
    ),
    "{left}, {right} from wire start": "{left}, {right} desde el inicio del hilo",
    "{material} ({conductivity:.3g} S/m)": ("{material} ({conductivity:.3g} S/m)"),
    "{offset:.4f} m from the wire start": "{offset:.4f} m desde el inicio del hilo",
    "{offset} from the wire start": "{offset} desde el inicio del hilo",
    "{resistance:.1f} Ω to ground": "{resistance:.1f} Ω a tierra",
    "{spacing:.4f} m behind": "{spacing:.4f} m detrás",
    "{spacing} behind": "{spacing} detrás",
    # HTML report phrases and templates.
    "<strong>Reproducibility.</strong> Model/spec fingerprint <code>{fingerprint}</code> · solver <strong>{solver} {version}</strong> · status <strong>{status}</strong>.": (  # noqa: E501
        "<strong>Reproducibilidad.</strong> Huella del modelo/spec "
        "<code>{fingerprint}</code> · solver <strong>{solver} {version}</strong> · "
        "estado <strong>{status}</strong>."
    ),
    "AntennaDesk report": "Informe de AntennaDesk",
    "AntennaDesk simulation report · generated from an immutable result snapshot · {finished}": (
        "Informe de simulación de AntennaDesk · generado a partir de una "
        "instantánea inmutable del resultado · {finished}"
    ),
    "AntennaDesk · GPL-3.0-or-later · This report reflects the model and conditions above. Use the browser print dialog to save it as PDF.": (  # noqa: E501
        "AntennaDesk · GPL-3.0-or-later · Este informe refleja el modelo y las "
        "condiciones anteriores. Usá el diálogo de impresión del navegador para "
        "guardarlo como PDF."
    ),
    "Ideal source inputs; negative power means that source absorbs power. The primary feed remains the impedance/SWR reference.": (  # noqa: E501
        "Entradas ideales de las fuentes; una potencia negativa significa que esa "
        "fuente absorbe potencia. La alimentación principal sigue siendo la "
        "referencia de impedancia/ROE."
    ),
    "Impedance (Ω)": "Impedancia (Ω)",
    "Power gain pattern at {frequency:g} MHz": (
        "Patrón de ganancia de potencia a {frequency:g} MHz"
    ),
    "Total gain": "Ganancia total",
    "target λ/{ratio:.0f} per segment": "objetivo λ/{ratio:.0f} por segmento",
    "{band} power gain at {frequency:g} MHz": (
        "Ganancia de potencia de {band} a {frequency:g} MHz"
    ),
    "{count} segments per wire": "{count} segmentos por hilo",
    "{start:g}-{stop:g} MHz, {count} points": ("{start:g}-{stop:g} MHz, {count} puntos"),
    # Native PDF wire schedule.
    "Feed: {wire} @ {offset} · ({x}, {y}, {z}) · height {height}": (
        "Alimentación: {wire} @ {offset} · ({x}, {y}, {z}) · altura {height}"
    ),
    "W{index} {wire}: ({start_x}, {start_y}, {start_z}) -> ({end_x}, {end_y}, {end_z}) · {length} {unit} · Ø{diameter} mm · {material}": (  # noqa: E501
        "W{index} {wire}: ({start_x}, {start_y}, {start_z}) -> ({end_x}, "
        "{end_y}, {end_z}) · {length} {unit} · Ø{diameter} mm · {material}"
    ),
    # Additional values.
    "A (reference)": "A (referencia)",
    "B (published)": "B (publicada)",
    "C (experimental)": "C (experimental)",
    "cancelled": "cancelada",
    "completed": "completada",
    "empirical": "empírica",
    "error": "error",
    "experimental": "experimental",
    "failed": "fallida",
    "finite": "suelo finito",
    "heuristic": "heurística",
    "info": "información",
    "parallel": "paralelo",
    "partial": "parcial",
    "physical": "física",
    "published": "publicada",
    "reference": "referencia",
    "reference_scaled": "referencia escalada",
    "running": "en ejecución",
    "warning": "advertencia",
    "Biquad": "Biquad",
    "Double biquad": "Biquad doble",
    "G5RV": "G5RV",
    "Linked dipole": "Dipolo con enlaces",
    "Loaded dipole": "Dipolo cargado",
    "T2FD": "T2FD",
    "ZS6BKW": "ZS6BKW",
    "beta_hairpin": "beta / hairpin",
    "copper": "cobre",
    "aluminum": "aluminio",
    "stainless_steel_304": "acero inoxidable 304",
    "custom": "personalizado",
    "end-fed wire": "hilo alimentado en un extremo",
    "shortened EFHW 80-10 m": "EFHW acortada 80-10 m",
    "shortened EFHW 40-20-10 m": "EFHW acortada 40-20-10 m",
    "loaded vertical": "vertical cargada",
    "random wire": "hilo aleatorio",
    "sloper": "sloper",
    "top-loaded vertical": "vertical con carga superior",
    "{kind} (eps_r={permittivity:g}, sigma={conductivity:g} S/m)": (
        "{kind} (eps_r={permittivity:g}, sigma={conductivity:g} S/m)"
    ),
    # Feed and matching presentation.
    "active": "activa",
    "inactive": "inactiva",
    "input": "entrada",
    "output": "salida",
    "retained; project network overrides": "retenida; la red del proyecto la reemplaza",
    "{value:g} µH": "{value:g} µH",
    "{value:g} pF": "{value:g} pF",
    "{value:.1f} pF (primary shunt, {status})": (
        "{value:.1f} pF (paralelo en el primario, {status})"
    ),
    "{value:.4f} µH ({status})": "{value:.4f} µH ({status})",
    "L network (series {series}, {side} shunt {shunt})": (
        "Red L (serie {series}, paralelo de {side} {shunt})"
    ),
    "Measured transformer (series {series}, input shunt {input_shunt})": (
        "Transformador medido (serie {series}, paralelo de entrada {input_shunt})"
    ),
    "Pi network (input shunt {input_shunt}, series {series}, output shunt {output_shunt})": (
        "Red Pi (paralelo de entrada {input_shunt}, serie {series}, "
        "paralelo de salida {output_shunt})"
    ),
    "T network (input series {input_series}, shunt {shunt}, output series {output_series})": (
        "Red T (serie de entrada {input_series}, paralelo {shunt}, serie de salida {output_series})"
    ),
    ", Q {q:g}": ", Q {q:g}",
    "{network} · {state}": "{network} · {state}",
    "{impedance:g} Ω, {length}, velocity factor {velocity:g}": (
        "{impedance:g} Ω, {length}, factor de velocidad {velocity:g}"
    ),
    "{loss:.3f} dB at {frequency:.6f} MHz (exponent {exponent:g})": (
        "{loss:.3f} dB a {frequency:.6f} MHz (exponente {exponent:g})"
    ),
    "The project matching network replaces the internal EFHW matching unit. The {capacitance} pF capacitor and {leakage} µH leakage are retained in the design but are not installed or applied; do not cascade both networks. The {ratio}:1 transformer ratio still applies.": (  # noqa: E501
        "La red de adaptación del proyecto reemplaza la unidad de adaptación "
        "interna del EFHW. El capacitor de {capacitance} pF y la fuga de {leakage} "
        "µH se retienen en el diseño pero no se instalan ni se aplican; no "
        "conectes ambas redes en cascada. La relación del transformador {ratio}:1 "
        "sigue aplicando."
    ),
    "Cut one wire to {length} m. Run {vertical} m vertically from the feed, bend 90°, then run {horizontal} m horizontally at {top} m. Use a {ratio}:1 transformer; the counterpoise is {counterpoise}.": (  # noqa: E501
        "Cortá un hilo de {length} m. Subí {vertical} m en vertical desde la "
        "alimentación, hacé un codo de 90° y luego corré {horizontal} m en "
        "horizontal a {top} m. Usá un transformador {ratio}:1; el contrapeso es "
        "{counterpoise}."
    ),
    "Cut one wire to {length} m. Run {vertical} m vertically from the feed, bend 90°, then run {horizontal} m horizontally at {top} m. Fit the {inductance} µH loading coil at {offset} m from the feed; the remaining {top_section} m is the top section. Use a {ratio}:1 transformer; the counterpoise is {counterpoise}.": (  # noqa: E501
        "Cortá un hilo de {length} m. Subí {vertical} m en vertical desde la "
        "alimentación, hacé un codo de 90° y luego corré {horizontal} m en "
        "horizontal a {top} m. Colocá la bobina de carga de {inductance} µH a "
        "{offset} m de la alimentación; los {top_section} m restantes son el tramo "
        "superior. Usá un transformador {ratio}:1; el contrapeso es {counterpoise}."
    ),
    "The bend is a 90° corner at {vertical} m from the feed. Use one continuous conductor and keep the corner mechanically supported; the model uses a sharp corner.": (  # noqa: E501
        "El codo es una esquina de 90° a {vertical} m de la alimentación. Usá un "
        "conductor continuo y mantené la esquina soportada mecánicamente; el modelo "
        "usa una esquina recta."
    ),
}
