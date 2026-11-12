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
    # Structural headings and captions.
    "Bill of materials": "Lista de materiales",
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
    "Base height": "Altura de base",
    "Best SWR": "Mejor ROE",
    "Boom height": "Altura del boom",
    "Boom length": "Longitud del boom",
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
    "Far field": "Campo lejano",
    "Feed": "Alimentación",
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
    "Radial wires": "Hilos radiales",
    "Radials": "Radiales",
    "Radials per element": "Radiales por elemento",
    "Radiator height": "Altura del radiador",
    "Radiator length": "Longitud del radiador",
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
    "Vertical elements": "Elementos verticales",
    "Vertical height": "Altura vertical",
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
    # Result-summary rows.
    "Balun/unun loss": "Pérdida del balun/unun",
    "Feed-line loss (matched)": "Pérdida de la línea de alimentación (adaptada)",
    "Link metrics at": "Métricas de enlace en",
    "Max directivity": "Directividad máxima",
    "Max power gain": "Ganancia máxima de potencia",
    "Max power gain (NEC)": "Ganancia máxima de potencia (NEC)",
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
    "No resonance in the sweep.": "No hay resonancia en el barrido.",
    "No result yet.": "Todavía no hay resultado.",
    "disabled": "deshabilitado",
    "enabled": "habilitado",
    "not recorded": "sin registrar",
    "unknown": "desconocido",
    # Chart axis labels.
    "Elevation θ (°)": "Elevación θ (°)",
    "Power gain (dBi)": "Ganancia de potencia (dBi)",
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
    "Build a W-shaped driver with {driver} m half-lengths and a U-shaped reflector with {reflector} m half-lengths on a six-spreader frame with a {turning} m turning radius. Set the tip gap to {tip_gap} m and feed the center of the W. The model reconstructs the bent wire path; the frame, spreader sag, feed balun, and multi-band nesting are not modeled.": (  # noqa: E501
        "Construí un excitador en forma de W con semilongitudes de {driver} m y "
        "un reflector en forma de U con semilongitudes de {reflector} m sobre un "
        "marco de seis separadores con un radio de giro de {turning} m. Ajustá la "
        "separación de puntas a {tip_gap} m y alimentá el centro de la W. El "
        "modelo reconstruye el camino de hilo doblado; el marco, la flecha de los "
        "separadores, el balun de alimentación y el anidamiento multibanda no "
        "están modelados."
    ),
    "Build a {height} m vertical radiator with a {diameter} m matching ring at {ring_height} m above ground.": (  # noqa: E501
        "Construí un radiador vertical de {height} m con un anillo de adaptación "
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
    "Build {count} square loops with the driven loop at {side} m per side and the reflector at {reflector} m per side. Set the reflector {spacing} m behind the driven loop.{director_note} Feed the midpoint of the driven loop's left vertical side and keep the loops square. The boom, spreaders, mast, and matching network are not modeled; tune the match for the installed antenna.": (  # noqa: E501
        "Construí {count} lazos cuadrados con el lazo alimentado de {side} m por "
        "lado y el reflector de {reflector} m por lado. Colocá el reflector a "
        "{spacing} m detrás del lazo alimentado.{director_note} Alimentá el punto "
        "medio del lado vertical izquierdo del lazo alimentado y mantené los lazos "
        "cuadrados. El boom, los separadores, el mástil y la red de adaptación no "
        "están modelados; ajustá la adaptación para la antena instalada."
    ),
    "Build {count} square loops with {side} m sides. Join them at the shared horizontal rails, starting at {base} m above ground, and feed the midpoint of the central rail at {feed_height} m. {reflector_note} The quarter-wave side and eighth-wave reflector spacing are starting dimensions; tune them for the installation.": (  # noqa: E501
        "Construí {count} lazos cuadrados de {side} m por lado. Unilos en los "
        "rieles horizontales compartidos, comenzando a {base} m sobre el suelo, y "
        "alimentá el punto medio del riel central a {feed_height} m. "
        "{reflector_note} El lado de cuarto de onda y la separación de reflector "
        "de octavo de onda son dimensiones de partida; ajustalos para la "
        "instalación."
    ),
    "Build {count} vertical radiators of {height} m, spaced {spacing} m along one line, with their bases at {base} m above ground. Fit {radials} radials of {radial_length} m to each base. Drive the first vertical as the primary feed and the remaining verticals with the listed phase and amplitude steps. The combining network is ideal and is not included; use an explicit feed network and verify the match.": (  # noqa: E501
        "Construí {count} radiadores verticales de {height} m, separados "
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
    "Install a {height} m vertical radiator with its base {base} m above ground. Add {radials} radials of {radial_length} m in the base plane.{top_hat_note}": (  # noqa: E501
        "Instalá un radiador vertical de {height} m con su base a {base} m sobre "
        "el suelo. Agregá {radials} radiales de {radial_length} m en el plano de "
        "base.{top_hat_note}"
    ),
    "Leave the far end open for a bidirectional receiving pattern.": (
        "Dejá el extremo lejano abierto para un patrón de recepción bidireccional."
    ),
    "Leave the links open and use only the center section.": (
        "Dejá los enlaces abiertos y usá solo la sección central."
    ),
    "No loading coils are fitted.": "No se instalan bobinas de carga.",
    "Run one horizontal wire of {length} m at {height} m above ground. Feed the near end directly and keep the wire straight. {termination_note} The one-wavelength starting length and termination value are heuristics; the pattern and receiving performance are not independently validated.": (  # noqa: E501
        "Tendé un hilo horizontal de {length} m a {height} m sobre el suelo. "
        "Alimentá el extremo cercano directamente y mantené el hilo recto. "
        "{termination_note} La longitud inicial de una longitud de onda y el "
        "valor de terminación son heurísticas; el patrón y el rendimiento de "
        "recepción no están validados independientemente."
    ),
    "SWR ({impedance:g} Ω)": "ROE ({impedance:g} Ω)",
    "This variant has no reflector.": "Esta variante no tiene reflector.",
    "Trim and re-measure after installation. Real ground, supports, feed line, and nearby objects can shift the result. A low SWR does not prove high efficiency or a useful radiation pattern.": (  # noqa: E501
        "Recortá y volvé a medir después de la instalación. El suelo real, los "
        "soportes, la línea de alimentación y los objetos cercanos pueden "
        "modificar el resultado. Una ROE baja no garantiza alta eficiencia ni un "
        "patrón de radiación útil."
    ),
    "beta / hairpin": "beta / hairpin",
    "center of driven element": "centro del elemento alimentado",
    "center of the W driver": "centro del excitador en W",
    "across the apex gap": "a través de la separación del vértice",
    "driven element center": "centro del elemento alimentado",
    "driven loop side midpoint": "punto medio del lado del lazo alimentado",
    "first vertical (primary)": "primera vertical (principal)",
    "near end": "extremo cercano",
    "construction sheet": "hoja de construcción",
    "midpoint of the first side": "punto medio del primer lado",
    "none": "ninguno",
    "the top corner of one outer vertical": "la esquina superior de una vertical exterior",
    "the top junction of the center vertical and the top wires": (
        "la unión superior de la vertical central y los hilos superiores"
    ),
    "{length:.4f} m each": "{length:.4f} m cada uno",
    "{offset:.4f} m from feed": "{offset:.4f} m desde la alimentación",
    "{left:.4f} m, {right:.4f} m from wire start": (
        "{left:.4f} m, {right:.4f} m desde el inicio del hilo"
    ),
    "{material} ({conductivity:.3g} S/m)": ("{material} ({conductivity:.3g} S/m)"),
    "{offset:.4f} m from the wire start": "{offset:.4f} m desde el inicio del hilo",
    "{resistance:.1f} Ω to ground": "{resistance:.1f} Ω a tierra",
    "{spacing:.4f} m behind": "{spacing:.4f} m detrás",
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
    "Feed: {wire} @ {offset} m · ({x}, {y}, {z}) · height {height} m": (
        "Alimentación: {wire} @ {offset} m · ({x}, {y}, {z}) · altura {height} m"
    ),
    "W{index} {wire}: ({start_x}, {start_y}, {start_z}) -> ({end_x}, {end_y}, {end_z}) · {length} m · Ø{diameter} mm · {material}": (  # noqa: E501
        "W{index} {wire}: ({start_x}, {start_y}, {start_z}) -> ({end_x}, "
        "{end_y}, {end_z}) · {length} m · Ø{diameter} mm · {material}"
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
    "Pi network (input shunt {input_shunt}, series {series}, output shunt {output_shunt})": (
        "Red Pi (paralelo de entrada {input_shunt}, serie {series}, "
        "paralelo de salida {output_shunt})"
    ),
    "T network (input series {input_series}, shunt {shunt}, output series {output_series})": (
        "Red T (serie de entrada {input_series}, paralelo {shunt}, serie de salida {output_series})"
    ),
    ", Q {q:g}": ", Q {q:g}",
    "{network} · {state}": "{network} · {state}",
    "{impedance:g} Ω, {length:.4f} m, velocity factor {velocity:g}": (
        "{impedance:g} Ω, {length:.4f} m, factor de velocidad {velocity:g}"
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
