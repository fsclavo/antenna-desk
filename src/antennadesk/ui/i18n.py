# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small English/Spanish translation layer for the Phase 3 UI."""

from __future__ import annotations

from enum import StrEnum


class Language(StrEnum):
    ENGLISH = "en"
    SPANISH = "es"


_TRANSLATIONS: dict[str, dict[Language, str]] = {
    "app.title": {
        Language.ENGLISH: "AntennaDesk — Antenna Designer",
        Language.SPANISH: "AntennaDesk — Diseñador de antenas",
    },
    "app.untitled": {
        Language.ENGLISH: "Untitled",
        Language.SPANISH: "Sin título",
    },
    "start.title": {
        Language.ENGLISH: "Start an antenna project",
        Language.SPANISH: "Iniciá un proyecto de antena",
    },
    "start.description": {
        Language.ENGLISH: (
            "Create a project from a template, or open an existing .antennadesk file."
        ),
        Language.SPANISH: (
            "Creá un proyecto a partir de una plantilla o abrí un archivo .antennadesk existente."
        ),
    },
    "start.flow": {
        Language.ENGLISH: (
            "Typical flow: choose a template, estimate dimensions if needed, "
            "refine the design, then simulate."
        ),
        Language.SPANISH: (
            "Flujo típico: elegí una plantilla, estimá las dimensiones si hace "
            "falta, refiná el diseño y después simulá."
        ),
    },
    "advanced.title": {
        Language.ENGLISH: "Advanced simulation",
        Language.SPANISH: "Simulación avanzada",
    },
    "sweep.group_title": {
        Language.ENGLISH: "Simulation sweep",
        Language.SPANISH: "Barrido de simulación",
    },
    "sweep.mode": {Language.ENGLISH: "Sweep", Language.SPANISH: "Barrido"},
    "sweep.auto": {
        Language.ENGLISH: "Auto (template)",
        Language.SPANISH: "Automático (plantilla)",
    },
    "sweep.custom": {Language.ENGLISH: "Custom", Language.SPANISH: "Personalizado"},
    "sweep.hint": {
        Language.ENGLISH: (
            "Auto uses the current template's default sweep. Custom overrides "
            "Start/Stop/Points for the next run."
        ),
        Language.SPANISH: (
            "Automático usa el barrido por defecto de la plantilla actual. "
            "Personalizado reemplaza Inicio/Fin/Puntos para la próxima corrida."
        ),
    },
    "app.about": {
        Language.ENGLISH: "AntennaDesk {version} — GPL-3.0-or-later\nLocal-first antenna design and simulation.",
        Language.SPANISH: "AntennaDesk {version} — GPL-3.0-or-later\nDiseño y simulación de antenas local-first.",
    },
    "menu.file": {Language.ENGLISH: "File", Language.SPANISH: "Archivo"},
    "menu.edit": {Language.ENGLISH: "Edit", Language.SPANISH: "Editar"},
    "menu.import": {Language.ENGLISH: "Import", Language.SPANISH: "Importar"},
    "menu.export": {Language.ENGLISH: "Export", Language.SPANISH: "Exportar"},
    "menu.design": {Language.ENGLISH: "Design", Language.SPANISH: "Diseño"},
    "menu.variants": {Language.ENGLISH: "Designs", Language.SPANISH: "Diseños"},
    "menu.custom_wires": {
        Language.ENGLISH: "Custom Wires",
        Language.SPANISH: "Hilos personalizados",
    },
    "menu.simulation": {
        Language.ENGLISH: "Simulation",
        Language.SPANISH: "Simulación",
    },
    "menu.tools": {Language.ENGLISH: "Tools", Language.SPANISH: "Herramientas"},
    "menu.help": {Language.ENGLISH: "Help", Language.SPANISH: "Ayuda"},
    "font_size.small": {Language.ENGLISH: "Small", Language.SPANISH: "Pequeño"},
    "font_size.medium": {Language.ENGLISH: "Normal", Language.SPANISH: "Normal"},
    "font_size.large": {Language.ENGLISH: "Large", Language.SPANISH: "Grande"},
    "preferences.title": {
        Language.ENGLISH: "Preferences",
        Language.SPANISH: "Preferencias",
    },
    "preferences.language": {
        Language.ENGLISH: "Language",
        Language.SPANISH: "Idioma",
    },
    "preferences.language_system": {
        Language.ENGLISH: "System",
        Language.SPANISH: "Sistema",
    },
    "preferences.restore_defaults": {
        Language.ENGLISH: "Restore Defaults",
        Language.SPANISH: "Restaurar valores",
    },
    "preferences.units": {
        Language.ENGLISH: "Units",
        Language.SPANISH: "Unidades",
    },
    "preferences.font_size": {
        Language.ENGLISH: "Font Size",
        Language.SPANISH: "Tamaño de fuente",
    },
    "preferences.hint": {
        Language.ENGLISH: (
            "Language, units, and font size apply after you accept. System "
            "follows the operating system language. Project files always store "
            "metric SI units."
        ),
        Language.SPANISH: (
            "El idioma, las unidades y el tamaño de fuente se aplican al "
            "aceptar. Sistema sigue el idioma del sistema operativo. Los "
            "archivos de proyecto siempre guardan unidades SI métricas."
        ),
    },
    "action.preferences": {
        Language.ENGLISH: "Preferences...",
        Language.SPANISH: "Preferencias...",
    },
    "action.new": {Language.ENGLISH: "New Antenna...", Language.SPANISH: "Nueva antena..."},
    "catalog.title": {
        Language.ENGLISH: "New Antenna",
        Language.SPANISH: "Nueva antena",
    },
    "catalog.type": {
        Language.ENGLISH: "Antenna Type",
        Language.SPANISH: "Tipo de antena",
    },
    "catalog.search": {
        Language.ENGLISH: "Search antenna types...",
        Language.SPANISH: "Buscar tipos de antena...",
    },
    "catalog.evidence": {
        Language.ENGLISH: "Evidence",
        Language.SPANISH: "Evidencia",
    },
    "catalog.family.dipole": {
        Language.ENGLISH: "Dipole",
        Language.SPANISH: "Dipolo",
    },
    "catalog.family.yagi": {
        Language.ENGLISH: "Yagi",
        Language.SPANISH: "Yagi",
    },
    "catalog.family.vertical": {
        Language.ENGLISH: "Vertical",
        Language.SPANISH: "Vertical",
    },
    "catalog.family.loop": {
        Language.ENGLISH: "Loop",
        Language.SPANISH: "Lazo",
    },
    "catalog.family.custom": {
        Language.ENGLISH: "Custom",
        Language.SPANISH: "Personalizada",
    },
    "catalog.wire_dipole.description": {
        Language.ENGLISH: "Center-fed straight wire with horizontal or vertical orientation.",
        Language.SPANISH: "Hilo recto con alimentación central, horizontal o vertical.",
    },
    "catalog.folded_dipole.description": {
        Language.ENGLISH: "Two parallel elements joined at the ends, with adjustable spacing.",
        Language.SPANISH: "Dos elementos paralelos unidos en los extremos, con separación ajustable.",
    },
    "catalog.loop.description": {
        Language.ENGLISH: "Regular-polygon loop in a vertical or horizontal plane.",
        Language.SPANISH: "Lazo poligonal regular en un plano vertical u horizontal.",
    },
    "catalog.yagi": {Language.ENGLISH: "Yagi", Language.SPANISH: "Yagi"},
    "catalog.yagi.description": {
        Language.ENGLISH: (
            "Editable multi-element Yagi with horizontal or vertical "
            "polarization and an NBS starting preset."
        ),
        Language.SPANISH: (
            "Yagi editable de múltiples elementos con polarización horizontal "
            "o vertical y preset inicial NBS."
        ),
    },
    "catalog.inverted_v": {
        Language.ENGLISH: "Inverted-V",
        Language.SPANISH: "V invertida",
    },
    "catalog.ringo": {
        Language.ENGLISH: "Ringo",
        Language.SPANISH: "Ringo",
    },
    "catalog.ringo.description": {
        Language.ENGLISH: "Half-wave vertical with a base matching ring.",
        Language.SPANISH: "Vertical de media onda con anillo de adaptación en la base.",
    },
    "catalog.j_pole": {
        Language.ENGLISH: "J Pole",
        Language.SPANISH: "J Pole",
    },
    "catalog.j_pole.description": {
        Language.ENGLISH: "Vertical radiator with a parallel matching stub.",
        Language.SPANISH: "Radiador vertical con stub de adaptación paralelo.",
    },
    "catalog.half_square": {
        Language.ENGLISH: "Half square",
        Language.SPANISH: "Medio cuadrado",
    },
    "catalog.half_square.description": {
        Language.ENGLISH: (
            "Two quarter-wave verticals joined by a half-wave top wire, fed at a "
            "top corner; broadside and vertically polarized."
        ),
        Language.SPANISH: (
            "Dos verticales de cuarto de onda unidas por un hilo superior de media "
            "onda, alimentadas en una esquina superior; bidireccional y polarización "
            "vertical."
        ),
    },
    "catalog.bobtail_curtain": {
        Language.ENGLISH: "Bobtail curtain",
        Language.SPANISH: "Cortina bobtail",
    },
    "catalog.bobtail_curtain.description": {
        Language.ENGLISH: (
            "Three quarter-wave verticals joined by two half-wave top wires, fed "
            "at the top of the center vertical; broadside and vertically polarized."
        ),
        Language.SPANISH: (
            "Tres verticales de cuarto de onda unidas por dos hilos superiores de "
            "media onda, alimentadas en la parte superior de la vertical central; "
            "bidireccional y polarización vertical."
        ),
    },
    "catalog.slim_jim": {
        Language.ENGLISH: "Slim Jim",
        Language.SPANISH: "Slim Jim",
    },
    "catalog.slim_jim.description": {
        Language.ENGLISH: "Folded rectangle with a gap in one vertical leg.",
        Language.SPANISH: "Rectángulo plegado con una brecha en una pata vertical.",
    },
    "catalog.trap_dipole": {
        Language.ENGLISH: "Trap dipole",
        Language.SPANISH: "Dipolo con trampas",
    },
    "catalog.trap_dipole.description": {
        Language.ENGLISH: ("Center-fed dipole with two parallel LC traps for two-band operation."),
        Language.SPANISH: (
            "Dipolo alimentado en el centro con dos trampas LC paralelas para operar en dos bandas."
        ),
    },
    "catalog.t2fd": {
        Language.ENGLISH: "T2FD",
        Language.SPANISH: "T2FD",
    },
    "catalog.t2fd.description": {
        Language.ENGLISH: (
            "Terminated folded dipole with a broadband non-inductive resistor "
            "and a feed transformer."
        ),
        Language.SPANISH: (
            "Dipolo plegado terminado con resistor no inductivo de banda ancha "
            "y transformador de alimentación."
        ),
    },
    "catalog.evidence.t2fd": {
        Language.ENGLISH: ("Reference-backed starting dimensions; ideal resistor and transformer"),
        Language.SPANISH: (
            "Dimensiones iniciales con referencia; resistor y transformador ideales"
        ),
    },
    "catalog.sloper": {
        Language.ENGLISH: "Sloper",
        Language.SPANISH: "Sloper",
    },
    "catalog.sloper.description": {
        Language.ENGLISH: "End-fed half-wave wire sloping from a high feed point to a lower end.",
        Language.SPANISH: "Hilo de media onda alimentado en el extremo, inclinado desde un punto alto hacia un extremo más bajo.",
    },
    "catalog.random_wire": {
        Language.ENGLISH: "Random wire",
        Language.SPANISH: "Hilo aleatorio",
    },
    "catalog.random_wire.description": {
        Language.ENGLISH: "Non-resonant end-fed wire with a 9:1 transformer and counterpoise.",
        Language.SPANISH: "Hilo no resonante alimentado en el extremo con transformador 9:1 y contrapeso.",
    },
    "catalog.g5rv": {
        Language.ENGLISH: "G5RV",
        Language.SPANISH: "G5RV",
    },
    "catalog.g5rv.description": {
        Language.ENGLISH: ("Published 102 ft dipole with a 300 Ω or 450 Ω matching line."),
        Language.SPANISH: (
            "Dipolo publicado de 102 pies con línea de adaptación de 300 Ω o 450 Ω."
        ),
    },
    "catalog.evidence.g5rv": {
        Language.ENGLISH: "Published G5RV dimensions; lossless TL model",
        Language.SPANISH: "Dimensiones publicadas del G5RV; modelo de línea sin pérdidas",
    },
    "catalog.zs6bkw": {
        Language.ENGLISH: "ZS6BKW",
        Language.SPANISH: "ZS6BKW",
    },
    "catalog.zs6bkw.description": {
        Language.ENGLISH: (
            "Reference-backed multiband doublet with a 400 Ω or 450 Ω matching section."
        ),
        Language.SPANISH: (
            "Doblete multibanda con referencia y sección de adaptación de 400 Ω o 450 Ω."
        ),
    },
    "catalog.evidence.zs6bkw": {
        Language.ENGLISH: "Cebik/W4RNL and commercial dimensions; lossless TL model",
        Language.SPANISH: "Dimensiones de Cebik/W4RNL y comercial; modelo de línea sin pérdidas",
    },
    "catalog.zepp": {
        Language.ENGLISH: "Zepp",
        Language.SPANISH: "Zepp",
    },
    "catalog.zepp.description": {
        Language.ENGLISH: (
            "Classic end-fed half-wave radiator with a real two-conductor "
            "quarter-wave matching stub."
        ),
        Language.SPANISH: (
            "Radiador clásico de media onda alimentado en el extremo, con stub de "
            "adaptación real de dos conductores y cuarto de onda."
        ),
    },
    "catalog.doublet": {
        Language.ENGLISH: "Doublet",
        Language.SPANISH: "Doublet",
    },
    "catalog.doublet.description": {
        Language.ENGLISH: "Center-fed dipole for open-wire feed line and a tuner.",
        Language.SPANISH: "Dipolo alimentado en el centro para línea abierta y sintonizador.",
    },
    "catalog.endfed": {
        Language.ENGLISH: "End-fed wire / EFHW",
        Language.SPANISH: "Hilo alimentado en el extremo / EFHW",
    },
    "catalog.endfed.description": {
        Language.ENGLISH: (
            "Single wire fed at one end; the EFHW preset uses the published "
            "40/20/10 m lengths and a 49:1 transformer."
        ),
        Language.SPANISH: (
            "Hilo único alimentado en un extremo; el preset EFHW usa las "
            "longitudes publicadas de 40/20/10 m y un transformador 49:1."
        ),
    },
    "catalog.fan_dipole": {
        Language.ENGLISH: "Fan dipole",
        Language.SPANISH: "Dipolo ventilador",
    },
    "catalog.fan_dipole.description": {
        Language.ENGLISH: "Multiple center-fed dipoles sharing a common apex feed.",
        Language.SPANISH: "Varios dipolos con alimentación central y vértice común.",
    },
    "catalog.moxon": {
        Language.ENGLISH: "Moxon rectangle",
        Language.SPANISH: "Rectángulo Moxon",
    },
    "catalog.moxon.description": {
        Language.ENGLISH: (
            "Two-element rectangle with bent tips and horizontal or vertical polarization."
        ),
        Language.SPANISH: (
            "Rectángulo de dos elementos con puntas dobladas y polarización horizontal o vertical."
        ),
    },
    "catalog.ocfd": {
        Language.ENGLISH: "Off-center-fed dipole",
        Language.SPANISH: "Dipolo con alimentación descentrada",
    },
    "catalog.ocfd.description": {
        Language.ENGLISH: "Single-wire dipole fed away from the center.",
        Language.SPANISH: "Dipolo de un solo hilo alimentado fuera del centro.",
    },
    "catalog.inverted_v.description": {
        Language.ENGLISH: "Two sloping wires fed at the apex, with adjustable included angle.",
        Language.SPANISH: "Dos hilos inclinados alimentados en el vértice, con ángulo ajustable.",
    },
    "catalog.inverted_l": {
        Language.ENGLISH: "Inverted L",
        Language.SPANISH: "L invertida",
    },
    "catalog.inverted_l.description": {
        Language.ENGLISH: "End-fed vertical section with a horizontal top wire.",
        Language.SPANISH: "Sección vertical alimentada en la base con un tramo horizontal superior.",
    },
    "catalog.delta_loop": {
        Language.ENGLISH: "Delta loop",
        Language.SPANISH: "Lazo delta",
    },
    "catalog.delta_loop.description": {
        Language.ENGLISH: "Three-sided loop preset; the loop editor opens with three sides.",
        Language.SPANISH: "Preset de lazo de tres lados; el editor abre con tres lados.",
    },
    "catalog.quad_loop": {
        Language.ENGLISH: "Quad loop",
        Language.SPANISH: "Lazo cuadrado",
    },
    "catalog.quad_loop.description": {
        Language.ENGLISH: "Four-sided loop preset; the loop editor opens with four sides.",
        Language.SPANISH: "Preset de lazo de cuatro lados; el editor abre con cuatro lados.",
    },
    "catalog.magnetic_loop": {
        Language.ENGLISH: "Magnetic loop",
        Language.SPANISH: "Lazo magnético",
    },
    "catalog.magnetic_loop.description": {
        Language.ENGLISH: (
            "Small tuned loop with a top gap and series capacitor; experimental "
            "loss and matching model."
        ),
        Language.SPANISH: (
            "Lazo pequeño sintonizado con gap superior y capacitor serie; "
            "modelo de pérdidas y adaptación experimental."
        ),
    },
    "catalog.vertical": {
        Language.ENGLISH: "Vertical + radials",
        Language.SPANISH: "Vertical + radiales",
    },
    "catalog.vertical.description": {
        Language.ENGLISH: "Vertical radiator with an optional radial ground plane.",
        Language.SPANISH: "Radiador vertical con plano de radiales opcional.",
    },
    "catalog.loaded_vertical": {
        Language.ENGLISH: "Loaded vertical / mobile whip",
        Language.SPANISH: "Vertical cargada / whip móvil",
    },
    "catalog.loaded_vertical.description": {
        Language.ENGLISH: "Short vertical with a series loading coil for mobile or restricted spaces.",
        Language.SPANISH: "Vertical corta con bobina de carga en serie para móvil o espacios reducidos.",
    },
    "catalog.custom": {
        Language.ENGLISH: "Custom wires",
        Language.SPANISH: "Hilos personalizados",
    },
    "catalog.custom.description": {
        Language.ENGLISH: "Start from an empty wire table and define arbitrary coordinates.",
        Language.SPANISH: "Comenzar con una tabla vacía y definir coordenadas arbitrarias.",
    },
    "catalog.evidence.builtin": {
        Language.ENGLISH: "Built-in template; simulation model",
        Language.SPANISH: "Plantilla integrada; modelo de simulación",
    },
    "catalog.evidence.moxon": {
        Language.ENGLISH: "Reference-backed 20 m wire preset; edited geometry is experimental",
        Language.SPANISH: "Preset de alambre de 20 m con referencia; la geometría editada es experimental",
    },
    "catalog.evidence.yagi": {
        Language.ENGLISH: "Reference-backed NBS preset; edited geometry is experimental",
        Language.SPANISH: "Preset NBS con referencia; la geometría editada es experimental",
    },
    "catalog.evidence.experimental": {
        Language.ENGLISH: "Experimental; no independent numeric reference",
        Language.SPANISH: "Experimental; sin referencia numérica independiente",
    },
    "catalog.evidence.published": {
        Language.ENGLISH: (
            "Published starting dimensions; no independent impedance or pattern validation"
        ),
        Language.SPANISH: (
            "Dimensiones iniciales publicadas; sin validación independiente de impedancia o patrón"
        ),
    },
    "catalog.evidence.custom": {
        Language.ENGLISH: "User-defined geometry",
        Language.SPANISH: "Geometría definida por el usuario",
    },
    "action.open": {Language.ENGLISH: "Open Project...", Language.SPANISH: "Abrir proyecto..."},
    "action.save": {Language.ENGLISH: "Save", Language.SPANISH: "Guardar"},
    "action.save_as": {Language.ENGLISH: "Save As...", Language.SPANISH: "Guardar como..."},
    "action.locate_solver": {
        Language.ENGLISH: "Locate NEC2C...",
        Language.SPANISH: "Ubicar NEC2C...",
    },
    "action.feed_line": {
        Language.ENGLISH: "Feed Line...",
        Language.SPANISH: "Línea de alimentación...",
    },
    "action.matching_network": {
        Language.ENGLISH: "Matching Network...",
        Language.SPANISH: "Red de adaptación...",
    },
    "action.balun_loss": {
        Language.ENGLISH: "Balun/Unun Loss...",
        Language.SPANISH: "Pérdida de balun/unun...",
    },
    "action.exit": {Language.ENGLISH: "Exit", Language.SPANISH: "Salir"},
    "action.about": {
        Language.ENGLISH: "About AntennaDesk",
        Language.SPANISH: "Acerca de AntennaDesk",
    },
    "action.simulate": {Language.ENGLISH: "Simulate", Language.SPANISH: "Simular"},
    "action.ok": {Language.ENGLISH: "OK", Language.SPANISH: "Aceptar"},
    "action.cancel": {Language.ENGLISH: "Cancel", Language.SPANISH: "Cancelar"},
    "action.apply": {Language.ENGLISH: "Apply design", Language.SPANISH: "Aplicar diseño"},
    "action.apply.tooltip": {
        Language.ENGLISH: "Save the current form values without running the solver.",
        Language.SPANISH: "Guardá los valores actuales del formulario sin ejecutar el solver.",
    },
    "action.simulate.tooltip": {
        Language.ENGLISH: "Save the current form values and run the solver.",
        Language.SPANISH: "Guardá los valores actuales del formulario y ejecutá el solver.",
    },
    "action.next": {Language.ENGLISH: "Next", Language.SPANISH: "Siguiente"},
    "action.back": {Language.ENGLISH: "Back", Language.SPANISH: "Atrás"},
    "action.finish": {Language.ENGLISH: "Create", Language.SPANISH: "Crear"},
    "action.change": {Language.ENGLISH: "Change...", Language.SPANISH: "Cambiar..."},
    "action.close": {Language.ENGLISH: "Close", Language.SPANISH: "Cerrar"},
    "action.yes": {Language.ENGLISH: "Yes", Language.SPANISH: "Sí"},
    "action.no": {Language.ENGLISH: "No", Language.SPANISH: "No"},
    "action.english": {Language.ENGLISH: "English", Language.SPANISH: "English"},
    "action.spanish": {Language.ENGLISH: "Español", Language.SPANISH: "Español"},
    "action.metric": {Language.ENGLISH: "Metric", Language.SPANISH: "Métrico"},
    "action.imperial": {Language.ENGLISH: "Imperial", Language.SPANISH: "Imperial"},
    "panel.design": {Language.ENGLISH: "Design", Language.SPANISH: "Diseño"},
    "panel.geometry": {Language.ENGLISH: "Geometry", Language.SPANISH: "Geometría"},
    "geometry.none": {
        Language.ENGLISH: "No project open.",
        Language.SPANISH: "No hay ningún proyecto abierto.",
    },
    "geometry.distance": {
        Language.ENGLISH: "Distance along wire ({unit})",
        Language.SPANISH: "Distancia sobre el hilo ({unit})",
    },
    "geometry.height": {
        Language.ENGLISH: "Height ({unit})",
        Language.SPANISH: "Altura ({unit})",
    },
    "geometry.feed": {Language.ENGLISH: "Feed", Language.SPANISH: "Alimentación"},
    "geometry.end": {Language.ENGLISH: "End", Language.SPANISH: "Extremo"},
    "geometry.center": {Language.ENGLISH: "Center", Language.SPANISH: "Centro"},
    "geometry.scale": {Language.ENGLISH: "Scale", Language.SPANISH: "Escala"},
    "geometry.total_length": {Language.ENGLISH: "Total length", Language.SPANISH: "Longitud total"},
    "geometry.leg_length": {Language.ENGLISH: "Leg", Language.SPANISH: "Rama"},
    "geometry.azimuth": {Language.ENGLISH: "Azimuth", Language.SPANISH: "Azimut"},
    "geometry.vertical": {Language.ENGLISH: "Vertical wire", Language.SPANISH: "Hilo vertical"},
    "geometry.summary": {
        Language.ENGLISH: "Length {length} · Height {height} · Azimuth {azimuth}°",
        Language.SPANISH: "Longitud {length} · Altura {height} · Azimut {azimuth}°",
    },
    "geometry.plan_summary": {
        Language.ENGLISH: "Length {length} · Azimuth {azimuth}°",
        Language.SPANISH: "Longitud {length} · Azimut {azimuth}°",
    },
    "geometry.plan_summary_multi": {
        Language.ENGLISH: "{count} wires · {width} x {depth}",
        Language.SPANISH: "{count} hilos · {width} x {depth}",
    },
    "geometry.plan_summary_folded": {
        Language.ENGLISH: "Folded dipole · element {element} · spacing {spacing} · total conductor {total}",
        Language.SPANISH: "Dipolo plegado · elemento {element} · separación {spacing} · conductor total {total}",
    },
    "geometry.plan_summary_loop": {
        Language.ENGLISH: "Loop · circumference {circumference} · diameter {diameter} · {sides} sides",
        Language.SPANISH: "Lazo · circunferencia {circumference} · diámetro {diameter} · {sides} lados",
    },
    "geometry.multi_wire_elevation": {
        Language.ENGLISH: "{count} wires · span {span} · height {height}",
        Language.SPANISH: "{count} hilos · ancho {span} · altura {height}",
    },
    "geometry.j_pole_elevation": {
        Language.ENGLISH: "{template} · radiator {radiator} · stub {stub} · spacing {spacing}",
        Language.SPANISH: "{template} · radiador {radiator} · stub {stub} · separación {spacing}",
    },
    "geometry.slim_jim_elevation": {
        Language.ENGLISH: "{template} · radiator {radiator} · stub {stub} · gap {gap} · spacing {spacing}",
        Language.SPANISH: "{template} · radiador {radiator} · stub {stub} · brecha {gap} · separación {spacing}",
    },
    "geometry.j_pole_plan": {
        Language.ENGLISH: "{template} top view · spacing {spacing}",
        Language.SPANISH: "Vista superior {template} · separación {spacing}",
    },
    "geometry.zepp_summary": {
        Language.ENGLISH: (
            "{template} · radiator {radiator} · stub {stub} · spacing {spacing} · ≈{impedance} Ω"
        ),
        Language.SPANISH: (
            "{template} · radiador {radiator} · stub {stub} · separación {spacing} · ≈{impedance} Ω"
        ),
    },
    "geometry.zepp_note": {
        Language.ENGLISH: (
            "Two-wire quarter-wave stub; the 1:1 choke and coaxial feed are not drawn"
        ),
        Language.SPANISH: (
            "Stub de cuarto de onda de dos conductores; el choque 1:1 y la "
            "alimentación coaxil no se dibujan"
        ),
    },
    "geometry.zepp_legacy_note": {
        Language.ENGLISH: (
            "Legacy simplified Zepp model; recreate the design to use the two-wire stub"
        ),
        Language.SPANISH: (
            "Modelo Zepp simplificado heredado; recreá el diseño para usar el "
            "stub de dos conductores"
        ),
    },
    "geometry.radiator": {
        Language.ENGLISH: "Radiator",
        Language.SPANISH: "Radiador",
    },
    "geometry.stub": {
        Language.ENGLISH: "Stub",
        Language.SPANISH: "Stub",
    },
    "geometry.elevation_summary": {
        Language.ENGLISH: "Height {height} · feed height {feed}",
        Language.SPANISH: "Altura {height} · altura de alimentación {feed}",
    },
    "geometry.elevation_summary_typed": {
        Language.ENGLISH: "{type} · height {height} · feed height {feed}",
        Language.SPANISH: "{type} · altura {height} · altura de alimentación {feed}",
    },
    "geometry.loop_elevation_summary": {
        Language.ENGLISH: "Loop · bottom {bottom} · diameter {diameter}",
        Language.SPANISH: "Lazo · base {bottom} · diámetro {diameter}",
    },
    "geometry.spacing_exaggerated": {
        Language.ENGLISH: "Spacing exaggerated for clarity",
        Language.SPANISH: "Separación exagerada para mayor claridad",
    },
    "geometry.section": {Language.ENGLISH: "Section", Language.SPANISH: "Sección"},
    "geometry.two_conductors": {
        Language.ENGLISH: "2 conductors",
        Language.SPANISH: "2 conductores",
    },
    "geometry.diameter": {Language.ENGLISH: "Diameter", Language.SPANISH: "Diámetro"},
    "geometry.width": {Language.ENGLISH: "Width", Language.SPANISH: "Ancho"},
    "geometry.depth": {Language.ENGLISH: "Depth", Language.SPANISH: "Profundidad"},
    "geometry.top_view": {
        Language.ENGLISH: "top view",
        Language.SPANISH: "vista superior",
    },
    "geometry.equivalent_diameter": {
        Language.ENGLISH: "equivalent diameter",
        Language.SPANISH: "diámetro equivalente",
    },
    "geometry.total_conductor": {
        Language.ENGLISH: "total conductor",
        Language.SPANISH: "conductor total",
    },
    "geometry.elements": {
        Language.ENGLISH: "elements",
        Language.SPANISH: "elementos",
    },
    "geometry.boom_length": {
        Language.ENGLISH: "boom length",
        Language.SPANISH: "longitud del boom",
    },
    "geometry.gap": {Language.ENGLISH: "gap", Language.SPANISH: "brecha"},
    "geometry.traps": {Language.ENGLISH: "traps", Language.SPANISH: "trampas"},
    "geometry.transmission_lines": {
        Language.ENGLISH: "transmission lines: {count}",
        Language.SPANISH: "líneas de transmisión: {count}",
    },
    "geometry.end_height": {
        Language.ENGLISH: "end height",
        Language.SPANISH: "altura del extremo",
    },
    "geometry.feed_height": {
        Language.ENGLISH: "feed height",
        Language.SPANISH: "altura de alimentación",
    },
    "geometry.feed_offset": {
        Language.ENGLISH: "feed offset",
        Language.SPANISH: "desplazamiento de alimentación",
    },
    "geometry.radials": {Language.ENGLISH: "radials", Language.SPANISH: "radiales"},
    "geometry.wires": {Language.ENGLISH: "wires", Language.SPANISH: "hilos"},
    "geometry.wire_length": {
        Language.ENGLISH: "wire length",
        Language.SPANISH: "longitud del hilo",
    },
    "geometry.arbitrary_geometry": {
        Language.ENGLISH: "arbitrary geometry · overall dimensions only",
        Language.SPANISH: "geometría arbitraria · solo dimensiones generales",
    },
    "geometry.front_overlap": {
        Language.ENGLISH: "front view: elements overlap; use Plan to see the layout",
        Language.SPANISH: "alzado: los elementos se superponen; use Planta para ver la disposición",
    },
    "geometry.edge_on": {
        Language.ENGLISH: "top view is edge-on",
        Language.SPANISH: "la vista superior es de canto",
    },
    "geometry.vertical_plane_edge_on": {
        Language.ENGLISH: "top view: vertical plane is edge-on; use Elevation to see the layout",
        Language.SPANISH: "vista superior: el plano vertical está de canto; usá Alzado para ver la disposición",
    },
    "geometry.horizontal_plane_edge_on": {
        Language.ENGLISH: "elevation: horizontal loop is edge-on; use Plan to see the layout",
        Language.SPANISH: "alzado: el lazo horizontal está de canto; usá Planta para ver la disposición",
    },
    "geometry.top_height": {
        Language.ENGLISH: "top height",
        Language.SPANISH: "altura superior",
    },
    "geometry.sides_note": {
        Language.ENGLISH: "{sides}-sided polygon shown to scale",
        Language.SPANISH: "polígono de {sides} lados a escala",
    },
    "geometry.detail_gap": {
        Language.ENGLISH: "gap detail (not to scale)",
        Language.SPANISH: "detalle de brecha (fuera de escala)",
    },
    "geometry.detail_spacing": {
        Language.ENGLISH: "spacing detail (not to scale)",
        Language.SPANISH: "detalle de separación (fuera de escala)",
    },
    "geometry.dimension_hidden": {
        Language.ENGLISH: "1 dimension hidden for space",
        Language.SPANISH: "1 cota oculta por espacio",
    },
    "geometry.dimensions_hidden": {
        Language.ENGLISH: "{count} dimensions hidden for space",
        Language.SPANISH: "{count} cotas ocultas por espacio",
    },
    "geometry.view": {Language.ENGLISH: "View", Language.SPANISH: "Vista"},
    "geometry.view_elevation": {Language.ENGLISH: "Elevation", Language.SPANISH: "Alzado"},
    "geometry.view_plan": {Language.ENGLISH: "Plan", Language.SPANISH: "Planta"},
    "geometry.view_3d": {Language.ENGLISH: "3D", Language.SPANISH: "3D"},
    "geometry.3d_summary": {
        Language.ENGLISH: "{type} · {count} wires · max height {height}",
        Language.SPANISH: "{type} · {count} hilos · altura máxima {height}",
    },
    "geometry.vertical_scale": {
        Language.ENGLISH: "Vertical scale",
        Language.SPANISH: "Escala vertical",
    },
    "geometry.zoom": {Language.ENGLISH: "Zoom", Language.SPANISH: "Zoom"},
    "geometry.zoom_hint": {
        Language.ENGLISH: "Mouse wheel zooms; drag pans; double-click resets.",
        Language.SPANISH: "La rueda hace zoom; arrastrá para desplazar; doble clic restablece.",
    },
    "geometry.vertical_exaggeration": {
        Language.ENGLISH: "vertical x{factor}",
        Language.SPANISH: "vertical x{factor}",
    },
    "design_from_frequency.title": {
        Language.ENGLISH: "Estimate Dimensions",
        Language.SPANISH: "Estimar dimensiones",
    },
    "design_from_frequency.current_template_hint": {
        Language.ENGLISH: (
            "This estimate refines the current template only; it does not "
            "change the template or antenna type. Use Change Template for a "
            "different family."
        ),
        Language.SPANISH: (
            "Esta estimación solo refina la plantilla actual; no cambia la "
            "plantilla ni el tipo de antena. Usá Cambiar plantilla para otra "
            "familia."
        ),
    },
    "design_from_frequency.template_locked": {
        Language.ENGLISH: "Locked to the current template. Use Change Template instead.",
        Language.SPANISH: "Fijado a la plantilla actual. Usá Cambiar plantilla en su lugar.",
    },
    "design_from_frequency.unsupported": {
        Language.ENGLISH: (
            "This template has no frequency-first estimator. Use the template "
            "editor's own controls or change the template explicitly."
        ),
        Language.SPANISH: (
            "Esta plantilla no tiene estimador desde frecuencia. Usá los "
            "controles del editor de la plantilla o cambiá la plantilla de "
            "forma explícita."
        ),
    },
    "design_from_frequency.unsupported_loaded_vertical": {
        Language.ENGLISH: (
            "A loaded vertical depends on its loading coil, so automatic "
            "frequency-first estimation is not available."
        ),
        Language.SPANISH: (
            "Una vertical cargada depende de su bobina de carga, por lo que no "
            "hay estimación automática desde frecuencia."
        ),
    },
    "design_from_frequency.unsupported_random_wire": {
        Language.ENGLISH: (
            "A random-wire length is deliberately non-resonant; use its "
            "template editor to adjust the length and matching."
        ),
        Language.SPANISH: (
            "La longitud de un hilo aleatorio es deliberadamente no resonante; "
            "usá el editor de la plantilla para ajustar la longitud y la "
            "adaptación."
        ),
    },
    "design_from_frequency.family": {
        Language.ENGLISH: "Antenna family",
        Language.SPANISH: "Familia de antena",
    },
    "design_from_frequency.loop_shape": {
        Language.ENGLISH: "Loop shape",
        Language.SPANISH: "Forma del lazo",
    },
    "design_from_frequency.vertical_form": {
        Language.ENGLISH: "Vertical type",
        Language.SPANISH: "Tipo de vertical",
    },
    "design_from_frequency.fan_bands": {
        Language.ENGLISH: "Band frequencies (MHz, comma-separated)",
        Language.SPANISH: "Frecuencias de banda (MHz, separadas por coma)",
    },
    "design_from_frequency.invalid_bands": {
        Language.ENGLISH: "Enter at least one valid band frequency.",
        Language.SPANISH: "Ingresá al menos una frecuencia de banda válida.",
    },
    "design_from_frequency.dimension": {
        Language.ENGLISH: "Dimension",
        Language.SPANISH: "Dimensión",
    },
    "design_from_frequency.value": {
        Language.ENGLISH: "Value",
        Language.SPANISH: "Valor",
    },
    "design_from_frequency.estimate": {
        Language.ENGLISH: "Estimate",
        Language.SPANISH: "Estimar",
    },
    "design_from_frequency.apply": {
        Language.ENGLISH: "Apply to current design",
        Language.SPANISH: "Aplicar al diseño actual",
    },
    "design_from_frequency.refine_after_apply": {
        Language.ENGLISH: "Open the family optimizer after applying",
        Language.SPANISH: "Abrir el optimizador de familia después de aplicar",
    },
    "design_from_frequency.hint": {
        Language.ENGLISH: "These are starting dimensions, not verified construction values. Apply them and refine with the family optimizer when available.",
        Language.SPANISH: "Son dimensiones iniciales, no valores de construcción verificados. Aplicarlas y refinar con el optimizador de familia cuando esté disponible.",
    },
    "design_from_frequency.confidence": {
        Language.ENGLISH: "Confidence: {value}",
        Language.SPANISH: "Confianza: {value}",
    },
    "design_from_frequency.tolerance": {
        Language.ENGLISH: "Tolerance: {value}",
        Language.SPANISH: "Tolerancia: {value}",
    },
    "confidence.physical": {
        Language.ENGLISH: "physical",
        Language.SPANISH: "física",
    },
    "confidence.empirical": {
        Language.ENGLISH: "empirical",
        Language.SPANISH: "empírica",
    },
    "confidence.reference_scaled": {
        Language.ENGLISH: "reference scaled",
        Language.SPANISH: "referencia escalada",
    },
    "confidence.heuristic": {
        Language.ENGLISH: "heuristic",
        Language.SPANISH: "heurística",
    },
    "design_from_frequency.assumptions": {
        Language.ENGLISH: "Assumptions: {values}",
        Language.SPANISH: "Supuestos: {values}",
    },
    "design_from_frequency.warnings": {
        Language.ENGLISH: "Warnings: {values}",
        Language.SPANISH: "Advertencias: {values}",
    },
    "design_from_frequency.sources": {
        Language.ENGLISH: "Sources: {values}",
        Language.SPANISH: "Fuentes: {values}",
    },
    "source.arrl.antenna_book.dipole.end_effect": {
        Language.ENGLISH: "ARRL Antenna Book — dipole end effect",
        Language.SPANISH: "ARRL Antenna Book — efecto de extremo del dipolo",
    },
    "source.arrl.antenna_book.loop.resonant_circumference": {
        Language.ENGLISH: "ARRL Antenna Book — resonant loop circumference",
        Language.SPANISH: "ARRL Antenna Book — circunferencia resonante del lazo",
    },
    "source.arrl.antenna_book.vertical.quarter_wave": {
        Language.ENGLISH: "ARRL Antenna Book — vertical length factors",
        Language.SPANISH: "ARRL Antenna Book — factores de longitud para verticales",
    },
    "source.nbs.tn688.five_element": {
        Language.ENGLISH: "NBS TN-688 — five-element Yagi",
        Language.SPANISH: "NBS TN-688 — Yagi de cinco elementos",
    },
    "source.cebik.t2fd.wide_long": {
        Language.ENGLISH: "Cebik, W4RNL, “Modeling the T2FD”: wide-long rule",
        Language.SPANISH: "Cebik, W4RNL, “Modeling the T2FD”: regla wide-long",
    },
    "source.cebik.moxon_review.table1": {
        Language.ENGLISH: "Cebik, W4RNL — Moxon review, Table 1",
        Language.SPANISH: "Cebik, W4RNL — revisión Moxon, Tabla 1",
    },
    "source.antennadesk.heuristic.application_preset": {
        Language.ENGLISH: "AntennaDesk application preset (heuristic)",
        Language.SPANISH: "Preset de aplicación de AntennaDesk (heurístico)",
    },
    "estimator.assumption.t2fd_broadband": {
        Language.ENGLISH: "broadband starting dimensions; not a resonant design",
        Language.SPANISH: "dimensiones iniciales de banda ancha; no es un diseño resonante",
    },
    "estimator.assumption.height_and_ground": {
        Language.ENGLISH: "height and ground affect the final resonance and feed impedance",
        Language.SPANISH: "la altura y el ground afectan la resonancia y la impedancia final",
    },
    "estimator.assumption.inverted_v_angle": {
        Language.ENGLISH: "the included angle changes the feed impedance",
        Language.SPANISH: "el ángulo incluido cambia la impedancia de alimentación",
    },
    "estimator.assumption.endfed_matching": {
        Language.ENGLISH: (
            "the transformer ratio and counterpoise are starting values; verify "
            "them for the installation"
        ),
        Language.SPANISH: (
            "la relación del transformador y el contrapeso son valores de "
            "partida; verificarlos para la instalación"
        ),
    },
    "estimator.assumption.yagi_reference": {
        Language.ENGLISH: "dimensions are scaled from the DL6WU trimming reference",
        Language.SPANISH: "las dimensiones se escalan desde la referencia DL6WU",
    },
    "estimator.assumption.yagi_element_diameter": {
        Language.ENGLISH: "the reference assumes 4 mm elements at 432 MHz; element-diameter correction is not applied",
        Language.SPANISH: "la referencia supone elementos de 4 mm a 432 MHz; no se aplica corrección por diámetro",
    },
    "estimator.assumption.reference_scaling": {
        Language.ENGLISH: "dimensions are scaled from a published reference design",
        Language.SPANISH: "las dimensiones se escalan desde un diseño de referencia publicado",
    },
    "estimator.warning.t2fd_broadband": {
        Language.ENGLISH: "T2FD dimensions are broadband starting points; verify termination and transformer",
        Language.SPANISH: "Las dimensiones del T2FD son puntos de partida de banda ancha; verificá terminación y transformador",
    },
    "estimator.warning.starting_point": {
        Language.ENGLISH: "starting point only; verify with simulation or measurement",
        Language.SPANISH: "solo punto de partida; verificar con simulación o medición",
    },
    "estimator.warning.inverted_v_angle_increased": {
        Language.ENGLISH: ("the included angle was widened to keep the leg ends above ground"),
        Language.SPANISH: (
            "el ángulo incluido se amplió para mantener los extremos sobre el suelo"
        ),
    },
    "estimator.warning.fan_angle_increased": {
        Language.ENGLISH: ("one or more element angles were widened to keep the ends above ground"),
        Language.SPANISH: (
            "uno o más ángulos de elemento se ampliaron para mantener los extremos sobre el suelo"
        ),
    },
    "estimator.warning.endfed_end_height_clamped": {
        Language.ENGLISH: ("the end height was clamped to the wire's vertical reach"),
        Language.SPANISH: ("la altura del extremo se limitó al alcance vertical del hilo"),
    },
    "estimator.warning.folded_impedance": {
        Language.ENGLISH: "spacing affects the step-up impedance; a 4:1 balun is typical for a 50 Ω system",
        Language.SPANISH: "la separación afecta la impedancia elevada; un balun 4:1 es lo típico para un sistema de 50 Ω",
    },
    "estimator.warning.vertical_matching": {
        Language.ENGLISH: "5/8-wave verticals need matching and a suitable radial system",
        Language.SPANISH: "las verticales de 5/8 necesitan adaptación y un sistema de radiales adecuado",
    },
    "estimator.warning.loop_matching": {
        Language.ENGLISH: "full-wave loops normally present 100-150 Ω; use a 2:1 balun or matching network for 50 Ω",
        Language.SPANISH: "los lazos de onda completa suelen presentar 100-150 Ω; usá un balun 2:1 o una red de adaptación para 50 Ω",
    },
    "estimator.warning.ocfd_matching": {
        Language.ENGLISH: "off-center feed impedance depends on the offset and height; the preset uses an ideal 4:1 transformer, so verify the real balun",
        Language.SPANISH: "la impedancia del feed descentrado depende del offset y la altura; el preset usa un transformador ideal 4:1, verificá el balún real",
    },
    "estimator.warning.fan_interaction": {
        Language.ENGLISH: (
            "fan elements interact and the V angle shifts resonance, especially "
            "on the highest band; tune with all bands visible"
        ),
        Language.SPANISH: (
            "los elementos del fan interactúan y el ángulo en V desplaza la "
            "resonancia, especialmente en la banda más alta; ajustar con todas "
            "las bandas visibles"
        ),
    },
    "estimator.warning.endfed_matching": {
        Language.ENGLISH: "end-fed matching and counterpoise are installation-specific",
        Language.SPANISH: "la adaptación y el contrapeso del end-fed dependen de la instalación",
    },
    "estimator.warning.j_pole_matching": {
        Language.ENGLISH: "stub and feed offset must be tuned with simulation or measurement",
        Language.SPANISH: "el stub y el offset de alimentación deben ajustarse con simulación o medición",
    },
    "estimator.warning.ringo_heuristic": {
        Language.ENGLISH: "Ringo proportions are an application preset, not a universal formula",
        Language.SPANISH: "las proporciones del Ringo son un preset de la aplicación, no una fórmula universal",
    },
    "estimator.warning.yagi_not_unique": {
        Language.ENGLISH: "a Yagi design is not unique; gain, bandwidth and F/B trade off",
        Language.SPANISH: "un diseño Yagi no es único; ganancia, ancho de banda y F/B se compensan",
    },
    "estimator.warning.moxon_gap": {
        Language.ENGLISH: "the Moxon gap is sensitive; verify the scaled design",
        Language.SPANISH: "el gap del Moxon es sensible; verificar el diseño escalado",
    },
    "source.cebik.dl6wu.32_element_rsgb": {
        Language.ENGLISH: "Cebik DL6WU 32-element reference (RSGB VHF/UHF DX Book)",
        Language.SPANISH: "Referencia DL6WU de 32 elementos de Cebik (RSGB VHF/UHF DX Book)",
    },
    "panel.results": {Language.ENGLISH: "Results", Language.SPANISH: "Resultados"},
    "field.project_name": {
        Language.ENGLISH: "Project name",
        Language.SPANISH: "Nombre del proyecto",
    },
    "field.frequency": {Language.ENGLISH: "Frequency (MHz)", Language.SPANISH: "Frecuencia (MHz)"},
    "field.fundamental_frequency": {
        Language.ENGLISH: "Fundamental design frequency (MHz)",
        Language.SPANISH: "Frecuencia fundamental de diseño (MHz)",
    },
    "field.design_frequency": {
        Language.ENGLISH: "Design frequency (MHz)",
        Language.SPANISH: "Frecuencia de diseño (MHz)",
    },
    "field.length": {Language.ENGLISH: "Total length", Language.SPANISH: "Longitud total"},
    "field.element_length": {
        Language.ENGLISH: "Element length",
        Language.SPANISH: "Longitud del elemento",
    },
    "field.circumference": {
        Language.ENGLISH: "Circumference",
        Language.SPANISH: "Circunferencia",
    },
    "field.antenna_type": {
        Language.ENGLISH: "Antenna type",
        Language.SPANISH: "Tipo de antena",
    },
    "field.family": {
        Language.ENGLISH: "Family",
        Language.SPANISH: "Familia",
    },
    "field.template": {
        Language.ENGLISH: "Template",
        Language.SPANISH: "Plantilla",
    },
    "family.dipole": {
        Language.ENGLISH: "Dipole",
        Language.SPANISH: "Dipolo",
    },
    "family.yagi": {Language.ENGLISH: "Yagi", Language.SPANISH: "Yagi"},
    "family.loop": {Language.ENGLISH: "Loop", Language.SPANISH: "Lazo"},
    "family.vertical": {
        Language.ENGLISH: "Vertical",
        Language.SPANISH: "Vertical",
    },
    "family.custom": {
        Language.ENGLISH: "Custom",
        Language.SPANISH: "Personalizada",
    },
    "custom.family": {
        Language.ENGLISH: "Family: {value}",
        Language.SPANISH: "Familia: {value}",
    },
    "custom.template": {
        Language.ENGLISH: "Template: {value}",
        Language.SPANISH: "Plantilla: {value}",
    },
    "field.spacing": {Language.ENGLISH: "Spacing", Language.SPANISH: "Separación"},
    "field.sides": {Language.ENGLISH: "Sides", Language.SPANISH: "Lados"},
    "field.primary_dimension": {
        Language.ENGLISH: "Main dimension",
        Language.SPANISH: "Dimensión principal",
    },
    "field.secondary_dimension": {
        Language.ENGLISH: "Secondary dimension",
        Language.SPANISH: "Dimensión secundaria",
    },
    "antenna_type.wire_dipole": {
        Language.ENGLISH: "Wire dipole",
        Language.SPANISH: "Dipolo de hilo",
    },
    "antenna_type.folded_dipole": {
        Language.ENGLISH: "Folded dipole",
        Language.SPANISH: "Dipolo plegado",
    },
    "antenna_type.loop": {Language.ENGLISH: "Loop", Language.SPANISH: "Lazo"},
    "antenna_type.magnetic_loop": {
        Language.ENGLISH: "Magnetic loop",
        Language.SPANISH: "Lazo magnético",
    },
    "antenna_type.trap_dipole": {
        Language.ENGLISH: "Trap dipole",
        Language.SPANISH: "Dipolo con trampas",
    },
    "antenna_type.t2fd": {
        Language.ENGLISH: "T2FD",
        Language.SPANISH: "T2FD",
    },
    "wizard.name_wire": {Language.ENGLISH: "dipole", Language.SPANISH: "dipolo"},
    "wizard.name_folded": {
        Language.ENGLISH: "folded dipole",
        Language.SPANISH: "dipolo plegado",
    },
    "wizard.name_loop": {Language.ENGLISH: "loop", Language.SPANISH: "lazo"},
    "field.height": {Language.ENGLISH: "Height", Language.SPANISH: "Altura"},
    "field.base_height": {Language.ENGLISH: "Base height", Language.SPANISH: "Altura de base"},
    "field.orientation": {Language.ENGLISH: "Orientation", Language.SPANISH: "Orientación"},
    "field.polarization": {
        Language.ENGLISH: "Polarization",
        Language.SPANISH: "Polarización",
    },
    "orientation.horizontal": {Language.ENGLISH: "Horizontal", Language.SPANISH: "Horizontal"},
    "orientation.vertical": {Language.ENGLISH: "Vertical", Language.SPANISH: "Vertical"},
    "field.azimuth": {Language.ENGLISH: "Azimuth (°)", Language.SPANISH: "Azimut (°)"},
    "field.diameter": {Language.ENGLISH: "Wire diameter", Language.SPANISH: "Diámetro del hilo"},
    "field.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "field.material": {Language.ENGLISH: "Material", Language.SPANISH: "Material"},
    "field.ground": {Language.ENGLISH: "Ground", Language.SPANISH: "Suelo"},
    "field.permittivity": {
        Language.ENGLISH: "Relative permittivity",
        Language.SPANISH: "Permitividad relativa",
    },
    "field.conductivity": {
        Language.ENGLISH: "Conductivity (S/m)",
        Language.SPANISH: "Conductividad (S/m)",
    },
    "field.soil_preset": {
        Language.ENGLISH: "Soil preset",
        Language.SPANISH: "Tipo de suelo",
    },
    "soil.custom": {
        Language.ENGLISH: "Custom / measured",
        Language.SPANISH: "Personalizado / medido",
    },
    "soil.average": {
        Language.ENGLISH: "Average soil / clay",
        Language.SPANISH: "Suelo promedio / arcilla",
    },
    "soil.rich": {
        Language.ENGLISH: "Rich soil / loam",
        Language.SPANISH: "Suelo rico / limo",
    },
    "soil.dry_sand": {
        Language.ENGLISH: "Dry sand",
        Language.SPANISH: "Arena seca",
    },
    "soil.rocky": {
        Language.ENGLISH: "Rocky soil",
        Language.SPANISH: "Suelo rocoso",
    },
    "soil.fresh_water": {
        Language.ENGLISH: "Fresh water",
        Language.SPANISH: "Agua dulce",
    },
    "soil.salt_water": {
        Language.ENGLISH: "Salt water",
        Language.SPANISH: "Agua salada",
    },
    "soil.hint": {
        Language.ENGLISH: (
            "Typical HF starting values adapted from the ARRL/Terman ground "
            "table. Moisture, frequency, and local geology change the real "
            "values; edit the numbers or choose Custom for measurements."
        ),
        Language.SPANISH: (
            "Valores típicos de partida para HF adaptados de la tabla de suelo "
            "ARRL/Terman. La humedad, la frecuencia y la geología local cambian "
            "los valores reales; editá los números o elegí Personalizado para "
            "usar mediciones."
        ),
    },
    "field.reference_impedance": {
        Language.ENGLISH: "Reference impedance (Ω)",
        Language.SPANISH: "Impedancia de referencia (Ω)",
    },
    "g5rv.title": {
        Language.ENGLISH: "G5RV Generator",
        Language.SPANISH: "Generador G5RV",
    },
    "g5rv.feed_height": {
        Language.ENGLISH: "Feed height",
        Language.SPANISH: "Altura de alimentación",
    },
    "g5rv.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "g5rv.line_option": {
        Language.ENGLISH: "Matching line",
        Language.SPANISH: "Línea de adaptación",
    },
    "g5rv.line_option.0": {
        Language.ENGLISH: "300 Ω / 8.84 m (29 ft)",
        Language.SPANISH: "300 Ω / 8.84 m (29 pies)",
    },
    "g5rv.line_option.1": {
        Language.ENGLISH: "450 Ω / 10.36 m (34 ft)",
        Language.SPANISH: "450 Ω / 10.36 m (34 pies)",
    },
    "g5rv.line_impedance": {
        Language.ENGLISH: "Matching-line impedance",
        Language.SPANISH: "Impedancia de la línea de adaptación",
    },
    "g5rv.line_length": {
        Language.ENGLISH: "Matching-line length",
        Language.SPANISH: "Longitud de la línea de adaptación",
    },
    "g5rv.velocity_factor": {
        Language.ENGLISH: "Line velocity factor",
        Language.SPANISH: "Factor de velocidad de la línea",
    },
    "g5rv.geometry": {
        Language.ENGLISH: (
            "Dipole {dipole} {unit} · matching line {line_impedance} Ω / {line_length} {unit}"
        ),
        Language.SPANISH: (
            "Dipolo {dipole} {unit} · línea de adaptación {line_impedance} Ω / {line_length} {unit}"
        ),
    },
    "g5rv.hint": {
        Language.ENGLISH: (
            "Published G5RV dimensions: 102 ft dipole with a 29 ft 300 Ω or "
            "34 ft 450 Ω matching section. The line is modeled as lossless. "
            "Set the line velocity factor for your hardware; the default "
            "treats the published length as the electrical length. The custom "
            "panel starts with a 41-point 3.5-30 MHz sweep and automatic "
            "pattern resolution. Add the transmitter coax as a Feed Line."
        ),
        Language.SPANISH: (
            "Dimensiones publicadas del G5RV: dipolo de 102 pies con sección "
            "de adaptación de 29 pies y 300 Ω o 34 pies y 450 Ω. La línea se "
            "modela sin pérdidas. Ajustá el factor de velocidad de tu línea; "
            "el valor por defecto trata la longitud publicada como longitud "
            "eléctrica. Agregá el coaxil del transmisor como Feed Line."
        ),
    },
    "g5rv.evidence": {
        Language.ENGLISH: (
            "Reference-backed dimensions from Carr, Practical Antenna Handbook "
            "(via the Wikipedia G5RV article); the transmission-line model is "
            "lossless and simplified."
        ),
        Language.SPANISH: (
            "Dimensiones con referencia de Carr, Practical Antenna Handbook "
            "(vía el artículo de Wikipedia sobre G5RV); el modelo de línea de "
            "transmisión es sin pérdidas y simplificado."
        ),
    },
    "zs6bkw.title": {
        Language.ENGLISH: "ZS6BKW Generator",
        Language.SPANISH: "Generador ZS6BKW",
    },
    "zs6bkw.wire_length": {
        Language.ENGLISH: "Wire length",
        Language.SPANISH: "Longitud del hilo",
    },
    "zs6bkw.line_length": {
        Language.ENGLISH: "Matching line length",
        Language.SPANISH: "Longitud de la línea de adaptación",
    },
    "zs6bkw.variant_label": {
        Language.ENGLISH: "Preset",
        Language.SPANISH: "Preset",
    },
    "zs6bkw.variant.0": {
        Language.ENGLISH: "28.4 m wire · 400 Ω / 13.6 m line (Cebik/W4RNL)",
        Language.SPANISH: "Hilo de 28.4 m · línea de 400 Ω / 13.6 m (Cebik/W4RNL)",
    },
    "zs6bkw.variant.1": {
        Language.ENGLISH: "27.5 m wire · 450 Ω / 12.2 m line (commercial)",
        Language.SPANISH: "Hilo de 27.5 m · línea de 450 Ω / 12.2 m (comercial)",
    },
    "zs6bkw.geometry": {
        Language.ENGLISH: (
            "Wire {dipole} {unit} · matching line {line_impedance} Ω / {line_length} {unit}"
        ),
        Language.SPANISH: (
            "Hilo {dipole} {unit} · línea de adaptación {line_impedance} Ω / {line_length} {unit}"
        ),
    },
    "zs6bkw.hint": {
        Language.ENGLISH: (
            "Reference-backed ZS6BKW dimensions. The 400 Ω / 13.6 m variant "
            "follows Cebik/W4RNL; the 450 Ω / 12.2 m variant records the common "
            "commercial implementation. The matching section is lossless. "
            "Set the line velocity factor for your hardware; the default "
            "treats the published length as the electrical length. Add the "
            "transmitter coax as a Feed Line."
        ),
        Language.SPANISH: (
            "Dimensiones del ZS6BKW con referencia. La variante de 400 Ω / "
            "13.6 m sigue a Cebik/W4RNL; la de 450 Ω / 12.2 m registra la "
            "implementación comercial habitual. La sección de adaptación es "
            "sin pérdidas. Ajustá el factor de velocidad de tu línea; el valor "
            "por defecto trata la longitud publicada como longitud eléctrica. "
            "Agregá el coaxil del transmisor como Feed Line."
        ),
    },
    "zs6bkw.evidence": {
        Language.ENGLISH: (
            "Dimensions from L. B. Cebik, W4RNL, “The G5RV Antenna System "
            "Re-Visited, Part 3: The Almost-No-ATU ZS6BKW”, and the 450 Ω "
            "commercial variant reported by PA0FRI. The transmission-line "
            "model is lossless and simplified."
        ),
        Language.SPANISH: (
            "Dimensiones de L. B. Cebik, W4RNL, “The G5RV Antenna System "
            "Re-Visited, Part 3: The Almost-No-ATU ZS6BKW”, y de la variante "
            "comercial de 450 Ω reportada por PA0FRI. El modelo de línea de "
            "transmisión es sin pérdidas y simplificado."
        ),
    },
    "zepp.title": {
        Language.ENGLISH: "Zepp Generator",
        Language.SPANISH: "Generador Zepp",
    },
    "zepp.radiator_length": {
        Language.ENGLISH: "Radiator length",
        Language.SPANISH: "Longitud del radiador",
    },
    "zepp.matching_length": {
        Language.ENGLISH: "Matching section length",
        Language.SPANISH: "Longitud de la sección de adaptación",
    },
    "zepp.spacing": {
        Language.ENGLISH: "Conductor spacing",
        Language.SPANISH: "Separación entre conductores",
    },
    "zepp.impedance": {
        Language.ENGLISH: "Estimated impedance",
        Language.SPANISH: "Impedancia estimada",
    },
    "zepp.base_height": {
        Language.ENGLISH: "Feed/base height",
        Language.SPANISH: "Altura de alimentación/base",
    },
    "zepp.starting_dimensions": {
        Language.ENGLISH: "Set starting dimensions from frequency",
        Language.SPANISH: "Establecer dimensiones iniciales desde la frecuencia",
    },
    "zepp.geometry": {
        Language.ENGLISH: (
            "Radiator {radiator} {unit} · matching section {matching} {unit} · "
            "spacing {spacing} {unit} · ≈{impedance} Ω · base {base_height} {unit} · "
            "top {top_height} {unit}"
        ),
        Language.SPANISH: (
            "Radiador {radiator} {unit} · sección de adaptación {matching} {unit} · "
            "separación {spacing} {unit} · ≈{impedance} Ω · base {base_height} {unit} · "
            "altura superior {top_height} {unit}"
        ),
    },
    "zepp.hint": {
        Language.ENGLISH: (
            "The matching section is drawn as two real conductors: one connects "
            "to the radiator, the other is open at the antenna end, and both meet "
            "at the base feed connector. A 1:1 common-mode choke at the "
            "transmitter end is required but is not modeled. The coax, "
            "common-mode current, and installation effects are not modeled; tune "
            "the radiator and stub for your height, ground, and hardware."
        ),
        Language.SPANISH: (
            "La sección de adaptación se dibuja como dos conductores reales: uno "
            "se conecta al radiador, el otro queda abierto en el extremo de la "
            "antena y ambos se unen en el conector de alimentación de la base. Se "
            "requiere un choque de modo común 1:1 en el extremo del transmisor, "
            "pero no se modela. No se modelan el coaxil, la corriente de modo "
            "común ni los efectos de la instalación; ajustá el radiador y el stub "
            "para tu altura, terreno y hardware."
        ),
    },
    "zepp.evidence": {
        Language.ENGLISH: (
            "Classic 3/4-wave end-fed Zepp topology: a half-wave radiator with a "
            "quarter-wave parallel-wire stub. The second stub conductor is real "
            "geometry; the 1:1 choke and coaxial feed are not modeled, so the "
            "match and common-mode current are not independently validated."
        ),
        Language.SPANISH: (
            "Topología clásica Zepp alimentada en el extremo de 3/4 de onda: "
            "radiador de media onda con stub de cuarto de onda de dos "
            "conductores. El segundo conductor del stub es geometría real; el "
            "choque 1:1 y la alimentación coaxil no se modelan, por lo que la "
            "adaptación y la corriente de modo común no están validadas de forma "
            "independiente."
        ),
    },
    "doublet.title": {
        Language.ENGLISH: "Doublet Generator",
        Language.SPANISH: "Generador de doublet",
    },
    "doublet.hint": {
        Language.ENGLISH: (
            "A center-fed dipole intended for open-wire feed line and a tuner. "
            "The feed line is project-level; adjust it later in Design → Feed "
            "Line. The dimensions and 450 Ω line are application starting points."
        ),
        Language.SPANISH: (
            "Un dipolo alimentado en el centro pensado para línea abierta y "
            "sintonizador. La línea es del proyecto; ajustala después en "
            "Diseño → Línea de alimentación. Las dimensiones y la línea de "
            "450 Ω son puntos de partida."
        ),
    },
    "doublet.geometry": {
        Language.ENGLISH: (
            "Length {length} {unit} · feed line {line} Ω · adjust the line in Design → Feed Line"
        ),
        Language.SPANISH: (
            "Longitud {length} {unit} · línea de {line} Ω · ajustá la línea en "
            "Diseño → Línea de alimentación"
        ),
    },
    "doublet.evidence": {
        Language.ENGLISH: (
            "Experimental preset: the dipole geometry is standard, but the "
            "open-wire line and tuner are not modeled as a matching network."
        ),
        Language.SPANISH: (
            "Preset experimental: la geometría del dipolo es estándar, pero la "
            "línea abierta y el sintonizador no se modelan como red de adaptación."
        ),
    },
    "feed_line.title": {
        Language.ENGLISH: "Feed Line",
        Language.SPANISH: "Línea de alimentación",
    },
    "feed_line.enabled": {
        Language.ENGLISH: "Enable feed line",
        Language.SPANISH: "Habilitar línea de alimentación",
    },
    "feed_line.characteristic_impedance": {
        Language.ENGLISH: "Characteristic impedance",
        Language.SPANISH: "Impedancia característica",
    },
    "feed_line.length": {
        Language.ENGLISH: "Length",
        Language.SPANISH: "Longitud",
    },
    "feed_line.velocity_factor": {
        Language.ENGLISH: "Velocity factor",
        Language.SPANISH: "Factor de velocidad",
    },
    "feed_line.loss": {
        Language.ENGLISH: "Matched loss",
        Language.SPANISH: "Pérdida adaptada",
    },
    "feed_line.hint": {
        Language.ENGLISH: (
            "The feed line transforms the impedance and SWR to the transmitter. "
            "It does not change the antenna pattern or power gain."
        ),
        Language.SPANISH: (
            "La línea transforma la impedancia y el SWR hacia el transmisor. "
            "No cambia el patrón ni la ganancia de potencia de la antena."
        ),
    },
    "balun_loss.title": {
        Language.ENGLISH: "Balun/Unun Loss",
        Language.SPANISH: "Pérdida de balun/unun",
    },
    "balun_loss.enabled": {
        Language.ENGLISH: "Enable balun/unun loss",
        Language.SPANISH: "Habilitar pérdida de balun/unun",
    },
    "balun_loss.reference_frequency": {
        Language.ENGLISH: "Reference frequency",
        Language.SPANISH: "Frecuencia de referencia",
    },
    "balun_loss.reference_loss": {
        Language.ENGLISH: "Loss at reference",
        Language.SPANISH: "Pérdida en la referencia",
    },
    "balun_loss.exponent": {
        Language.ENGLISH: "Frequency exponent",
        Language.SPANISH: "Exponente de frecuencia",
    },
    "balun_loss.preview": {
        Language.ENGLISH: "{values}",
        Language.SPANISH: "{values}",
    },
    "balun_loss.disabled": {
        Language.ENGLISH: "Disabled.",
        Language.SPANISH: "Deshabilitado.",
    },
    "balun_loss.hint": {
        Language.ENGLISH: (
            "Matched insertion loss fitted as loss = Lref x (f/fref)^n. It "
            "reduces realized gain but does not change geometry, impedance, or "
            "SWR. This is an application model, not a core-loss calculation."
        ),
        Language.SPANISH: (
            "Pérdida de inserción adaptada ajustada como pérdida = Lref x "
            "(f/fref)^n. Reduce la ganancia realizada pero no cambia la "
            "geometría, la impedancia ni la ROE. Es un modelo de aplicación, no "
            "un cálculo de pérdidas del núcleo."
        ),
    },
    "matching_network.title": {
        Language.ENGLISH: "Matching Network",
        Language.SPANISH: "Red de adaptación",
    },
    "matching_network.enabled": {
        Language.ENGLISH: "Enable L matching network",
        Language.SPANISH: "Habilitar red de adaptación L",
    },
    "matching_network.series_l": {
        Language.ENGLISH: "Series inductance",
        Language.SPANISH: "Inductancia serie",
    },
    "matching_network.series_c": {
        Language.ENGLISH: "Series capacitance",
        Language.SPANISH: "Capacitancia serie",
    },
    "matching_network.shunt_l": {
        Language.ENGLISH: "Shunt inductance",
        Language.SPANISH: "Inductancia paralelo",
    },
    "matching_network.shunt_c": {
        Language.ENGLISH: "Shunt capacitance",
        Language.SPANISH: "Capacitancia paralelo",
    },
    "matching_network.q_factor": {
        Language.ENGLISH: "Component Q (0 = lossless)",
        Language.SPANISH: "Q de componentes (0 = sin pérdidas)",
    },
    "matching_network.lossless": {
        Language.ENGLISH: "Lossless",
        Language.SPANISH: "Sin pérdidas",
    },
    "matching_network.topology": {
        Language.ENGLISH: "Topology",
        Language.SPANISH: "Topología",
    },
    "matching_network.input_shunt_l": {
        Language.ENGLISH: "Input shunt inductance",
        Language.SPANISH: "Inductancia paralelo de entrada",
    },
    "matching_network.input_shunt_c": {
        Language.ENGLISH: "Input shunt capacitance",
        Language.SPANISH: "Capacitancia paralelo de entrada",
    },
    "matching_network.output_shunt_l": {
        Language.ENGLISH: "Output shunt inductance",
        Language.SPANISH: "Inductancia paralelo de salida",
    },
    "matching_network.output_shunt_c": {
        Language.ENGLISH: "Output shunt capacitance",
        Language.SPANISH: "Capacitancia paralelo de salida",
    },
    "matching_network.input_series_l": {
        Language.ENGLISH: "Input series inductance",
        Language.SPANISH: "Inductancia serie de entrada",
    },
    "matching_network.input_series_c": {
        Language.ENGLISH: "Input series capacitance",
        Language.SPANISH: "Capacitancia serie de entrada",
    },
    "matching_network.output_series_l": {
        Language.ENGLISH: "Output series inductance",
        Language.SPANISH: "Inductancia serie de salida",
    },
    "matching_network.output_series_c": {
        Language.ENGLISH: "Output series capacitance",
        Language.SPANISH: "Capacitancia serie de salida",
    },
    "matching_network.load_r": {
        Language.ENGLISH: "Load R at design frequency",
        Language.SPANISH: "R de carga en la frecuencia de diseño",
    },
    "matching_network.load_x": {
        Language.ENGLISH: "Load X at design frequency",
        Language.SPANISH: "X de carga en la frecuencia de diseño",
    },
    "matching_network.frequency": {
        Language.ENGLISH: "Design frequency",
        Language.SPANISH: "Frecuencia de diseño",
    },
    "matching_network.auto_design": {
        Language.ENGLISH: "Auto-design L network",
        Language.SPANISH: "Diseñar red L automáticamente",
    },
    "matching_network.auto_unavailable": {
        Language.ENGLISH: "A single L section cannot match this load at the selected frequency.",
        Language.SPANISH: "Una sola sección L no puede adaptar esta carga en la frecuencia elegida.",
    },
    "matching_network.shunt_at_input": {
        Language.ENGLISH: "Shunt element on the transmitter side",
        Language.SPANISH: "Elemento paralelo del lado del transmisor",
    },
    "matching_network.hint": {
        Language.ENGLISH: (
            "Lossless L-network evaluated before the feed line. It changes "
            "impedance and SWR but not the antenna pattern or power gain."
        ),
        Language.SPANISH: (
            "Red L sin pérdidas evaluada antes de la línea. Cambia la impedancia "
            "y el SWR, pero no el patrón ni la ganancia de potencia."
        ),
    },
    "field.sweep": {Language.ENGLISH: "Frequency sweep", Language.SPANISH: "Barrido de frecuencia"},
    "field.sweep_enabled": {
        Language.ENGLISH: "Enable sweep",
        Language.SPANISH: "Habilitar barrido",
    },
    "field.sweep_start": {Language.ENGLISH: "Start (MHz)", Language.SPANISH: "Inicio (MHz)"},
    "field.sweep_stop": {Language.ENGLISH: "Stop (MHz)", Language.SPANISH: "Fin (MHz)"},
    "field.sweep_points": {Language.ENGLISH: "Points", Language.SPANISH: "Puntos"},
    "material.copper": {Language.ENGLISH: "Copper", Language.SPANISH: "Cobre"},
    "material.aluminum": {Language.ENGLISH: "Aluminum", Language.SPANISH: "Aluminio"},
    "ground.free_space": {Language.ENGLISH: "Free space", Language.SPANISH: "Espacio libre"},
    "ground.perfect": {Language.ENGLISH: "Perfect ground", Language.SPANISH: "Suelo perfecto"},
    "ground.finite": {Language.ENGLISH: "Finite ground", Language.SPANISH: "Suelo finito"},
    "units.metric": {Language.ENGLISH: "Metric (m, mm)", Language.SPANISH: "Métrico (m, mm)"},
    "units.imperial": {
        Language.ENGLISH: "Imperial (ft, in)",
        Language.SPANISH: "Imperial (ft, in)",
    },
    "status.ready": {Language.ENGLISH: "Ready", Language.SPANISH: "Listo"},
    "status.simulating": {Language.ENGLISH: "Simulating...", Language.SPANISH: "Simulando..."},
    "status.completed": {
        Language.ENGLISH: "Simulation completed",
        Language.SPANISH: "Simulación completada",
    },
    "status.cancelled": {
        Language.ENGLISH: "Simulation cancelled",
        Language.SPANISH: "Simulación cancelada",
    },
    "status.partial": {
        Language.ENGLISH: "Simulation partially completed",
        Language.SPANISH: "Simulación completada parcialmente",
    },
    "status.error": {Language.ENGLISH: "Simulation failed", Language.SPANISH: "Simulación fallida"},
    "status.solver": {
        Language.ENGLISH: "NEC engine: {name} {version}",
        Language.SPANISH: "Motor NEC: {name} {version}",
    },
    "status.no_solver": {
        Language.ENGLISH: "NEC engine not configured",
        Language.SPANISH: "Motor NEC no configurado",
    },
    "status.solver_missing": {
        Language.ENGLISH: "Solver not found. Build nec2c or set NEC2C.",
        Language.SPANISH: "No se encontró el motor. Compilá nec2c o definí NEC2C.",
    },
    "status.unsaved": {
        Language.ENGLISH: "Unsaved changes",
        Language.SPANISH: "Cambios sin guardar",
    },
    "status.design_changed": {
        Language.ENGLISH: "Design changed. Simulate again.",
        Language.SPANISH: "Diseño modificado. Simulá de nuevo.",
    },
    "status.measurement_updated": {
        Language.ENGLISH: "Measurement details updated.",
        Language.SPANISH: "Detalles de la medición actualizados.",
    },
    "status.measurement_deleted": {
        Language.ENGLISH: "Measurement deleted.",
        Language.SPANISH: "Medición eliminada.",
    },
    "design.provenance": {
        Language.ENGLISH: "Estimated design: {method} · confidence: {confidence} · tolerance: {tolerance}",
        Language.SPANISH: "Diseño estimado: {method} · confianza: {confidence} · tolerancia: {tolerance}",
    },
    "status.design_estimated": {
        Language.ENGLISH: "Estimated dimensions applied. Review them and simulate.",
        Language.SPANISH: "Dimensiones estimadas aplicadas. Revisalas y simulá.",
    },
    "status.estimate_apply_manual_refine": {
        Language.ENGLISH: "Estimated dimensions applied. Open the family optimizer to refine them when available.",
        Language.SPANISH: "Dimensiones estimadas aplicadas. Abrí el optimizador de familia para refinarlas cuando esté disponible.",
    },
    "status.cancelling": {Language.ENGLISH: "Cancelling...", Language.SPANISH: "Cancelando..."},
    "status.preparing_save": {
        Language.ENGLISH: "Preparing project...",
        Language.SPANISH: "Preparando proyecto...",
    },
    "status.saved": {Language.ENGLISH: "Project saved.", Language.SPANISH: "Proyecto guardado."},
    "status.opened": {Language.ENGLISH: "Project opened.", Language.SPANISH: "Proyecto abierto."},
    "status.no_project": {
        Language.ENGLISH: "No project open.",
        Language.SPANISH: "No hay proyecto abierto.",
    },
    "tab.bands": {Language.ENGLISH: "Bands", Language.SPANISH: "Bandas"},
    "band.group_title": {
        Language.ENGLISH: "Band analysis",
        Language.SPANISH: "Análisis por bandas",
    },
    "band.choose": {
        Language.ENGLISH: "Choose analysis bands...",
        Language.SPANISH: "Elegir bandas de análisis...",
    },
    "band.empty": {
        Language.ENGLISH: "Select at least one analysis band.",
        Language.SPANISH: "Seleccioná al menos una banda de análisis.",
    },
    "band.analyze": {
        Language.ENGLISH: "Analyze Bands...",
        Language.SPANISH: "Analizar bandas...",
    },
    "band.dialog_title": {
        Language.ENGLISH: "Band analysis",
        Language.SPANISH: "Análisis por bandas",
    },
    "band.preset": {Language.ENGLISH: "Preset", Language.SPANISH: "Preajuste"},
    "band.preset.default": {
        Language.ENGLISH: "Family default",
        Language.SPANISH: "Predeterminado de la familia",
    },
    "band.preset.current": {
        Language.ENGLISH: "Current band",
        Language.SPANISH: "Banda actual",
    },
    "band.preset.40_20_10": {
        Language.ENGLISH: "40 / 20 / 10 m",
        Language.SPANISH: "40 / 20 / 10 m",
    },
    "band.preset.80_10": {
        Language.ENGLISH: "80-10 m",
        Language.SPANISH: "80-10 m",
    },
    "band.preset.all": {
        Language.ENGLISH: "All bands",
        Language.SPANISH: "Todas las bandas",
    },
    "band.preset.custom": {
        Language.ENGLISH: "Custom",
        Language.SPANISH: "Personalizado",
    },
    "band.table.band": {Language.ENGLISH: "Band", Language.SPANISH: "Banda"},
    "band.table.range": {
        Language.ENGLISH: "Range (MHz)",
        Language.SPANISH: "Rango (MHz)",
    },
    "band.table.points": {Language.ENGLISH: "Points", Language.SPANISH: "Puntos"},
    "band.table.best_swr": {
        Language.ENGLISH: "Best SWR",
        Language.SPANISH: "Mejor ROE",
    },
    "band.table.at_frequency": {
        Language.ENGLISH: "At frequency",
        Language.SPANISH: "En frecuencia",
    },
    "band.table.gain": {Language.ENGLISH: "Gain", Language.SPANISH: "Ganancia"},
    "band.table.takeoff": {
        Language.ENGLISH: "Takeoff",
        Language.SPANISH: "Disparo",
    },
    "band.table.efficiency": {
        Language.ENGLISH: "Efficiency",
        Language.SPANISH: "Eficiencia",
    },
    "band.table.status": {Language.ENGLISH: "Status", Language.SPANISH: "Estado"},
    "band.selected": {
        Language.ENGLISH: "Bands: {bands}",
        Language.SPANISH: "Bandas: {bands}",
    },
    "band.no_selection": {
        Language.ENGLISH: "No bands selected",
        Language.SPANISH: "Sin bandas seleccionadas",
    },
    "band.none_selected": {
        Language.ENGLISH: "Select at least one band.",
        Language.SPANISH: "Seleccioná al menos una banda.",
    },
    "band.evidence.published": {
        Language.ENGLISH: "Evidence: published reference",
        Language.SPANISH: "Evidencia: referencia publicada",
    },
    "band.evidence.heuristic": {
        Language.ENGLISH: "Evidence: heuristic starting point",
        Language.SPANISH: "Evidencia: punto de partida heurístico",
    },
    "band.evidence.tunable": {
        Language.ENGLISH: "Evidence: tuner-assisted starting point",
        Language.SPANISH: "Evidencia: punto de partida con sintonizador",
    },
    "band.evidence.broadband": {
        Language.ENGLISH: "Evidence: broadband design",
        Language.SPANISH: "Evidencia: diseño de banda ancha",
    },
    "band.evidence.current": {
        Language.ENGLISH: "Evidence: current design band only",
        Language.SPANISH: "Evidencia: solo la banda actual del diseño",
    },
    "band.note.g5rv": {
        Language.ENGLISH: "Published G5RV coverage. WARC bands may require a tuner.",
        Language.SPANISH: "Cobertura publicada del G5RV. Las bandas WARC pueden requerir sintonizador.",
    },
    "band.note.zepp": {
        Language.ENGLISH: (
            "Odd-harmonic analysis plan for the 3/4-wave Zepp; the stub balance "
            "degrades on even harmonics. Tune each band and use a 1:1 choke at "
            "the transmitter end."
        ),
        Language.SPANISH: (
            "Plan de análisis por armónicos impares para el Zepp de 3/4 de onda; "
            "el balance del stub se degrada en armónicos pares. Ajustá cada banda "
            "y usá un choque 1:1 en el extremo del transmisor."
        ),
    },
    "band.note.zs6bkw": {
        Language.ENGLISH: (
            "Cebik/W4RNL no-ATU bands: 40, 20, 17, 12, and 10 m. "
            "80, 30, and 15 m are poor matches without a tuner."
        ),
        Language.SPANISH: (
            "Bandas sin sintonizador según Cebik/W4RNL: 40, 20, 17, 12 y 10 m. "
            "80, 30 y 15 m presentan malas adaptaciones sin sintonizador."
        ),
    },
    "band.note.ocfd": {
        Language.ENGLISH: "Harmonically related bands; verify them with the feed arrangement.",
        Language.SPANISH: "Bandas relacionadas por armónicos; verificarlas con la alimentación.",
    },
    "band.note.endfed": {
        Language.ENGLISH: "Starting point; the transformer and counterpoise determine coverage.",
        Language.SPANISH: "Punto de partida; el transformador y el contrapeso determinan la cobertura.",
    },
    "band.note.random_wire": {
        Language.ENGLISH: "Non-resonant wire; an external tuner is required.",
        Language.SPANISH: "Hilo no resonante; se requiere un sintonizador externo.",
    },
    "band.note.sloper": {
        Language.ENGLISH: "End-fed sloper geometry; coverage depends on the transformer and tuner.",
        Language.SPANISH: "Geometría sloper alimentada en el extremo; la cobertura depende del transformador y el sintonizador.",
    },
    "band.note.fan": {
        Language.ENGLISH: "Bands derived from element lengths; elements interact.",
        Language.SPANISH: "Bandas derivadas de las longitudes de los elementos; los elementos interactúan.",
    },
    "band.note.trap": {
        Language.ENGLISH: "The low and high trap-dipole design frequencies.",
        Language.SPANISH: "Las frecuencias de diseño baja y alta del dipolo con trampas.",
    },
    "band.note.t2fd": {
        Language.ENGLISH: "Broadband terminated antenna; not a set of narrow resonances.",
        Language.SPANISH: "Antena terminada de banda ancha; no es un conjunto de resonancias estrechas.",
    },
    "band.note.doublet": {
        Language.ENGLISH: "High-impedance/open-wire feed line; a tuner is required.",
        Language.SPANISH: "Línea de alimentación de alta impedancia o hilo abierto; se requiere sintonizador.",
    },
    "band.note.current": {
        Language.ENGLISH: "Current band only; select more bands manually if needed.",
        Language.SPANISH: "Solo la banda actual; seleccioná más bandas manualmente si hace falta.",
    },
    "status.analyzing_bands": {
        Language.ENGLISH: "Analyzing bands...",
        Language.SPANISH: "Analizando bandas...",
    },
    "status.bands_done": {
        Language.ENGLISH: "Band analysis complete.",
        Language.SPANISH: "Análisis por bandas completado.",
    },
    "status.bands_progress": {
        Language.ENGLISH: "Band {index}/{total}: {band}",
        Language.SPANISH: "Banda {index}/{total}: {band}",
    },
    "tab.impedance": {Language.ENGLISH: "Impedance / SWR", Language.SPANISH: "Impedancia / ROE"},
    "tab.pattern": {Language.ENGLISH: "Pattern", Language.SPANISH: "Patrón"},
    "tab.currents": {Language.ENGLISH: "Currents", Language.SPANISH: "Corrientes"},
    "tab.measurements": {
        Language.ENGLISH: "Measurements",
        Language.SPANISH: "Mediciones",
    },
    "measurement.details_title": {
        Language.ENGLISH: "Measurement Details",
        Language.SPANISH: "Detalles de la medición",
    },
    "measurement.name": {
        Language.ENGLISH: "Name",
        Language.SPANISH: "Nombre",
    },
    "measurement.calibration": {
        Language.ENGLISH: "Calibration",
        Language.SPANISH: "Calibración",
    },
    "measurement.reference_plane": {
        Language.ENGLISH: "Reference plane",
        Language.SPANISH: "Plano de referencia",
    },
    "measurement.feed_line": {
        Language.ENGLISH: "Feed line / accessories",
        Language.SPANISH: "Línea de alimentación / accesorios",
    },
    "measurement.notes": {
        Language.ENGLISH: "Notes",
        Language.SPANISH: "Notas",
    },
    "measurement.notes_hint": {
        Language.ENGLISH: "Optional measurement conditions or notes.",
        Language.SPANISH: "Condiciones o notas opcionales de la medición.",
    },
    "measurement.calibration_value": {
        Language.ENGLISH: "Calibration: {value}",
        Language.SPANISH: "Calibración: {value}",
    },
    "measurement.reference_plane_value": {
        Language.ENGLISH: "Reference plane: {value}",
        Language.SPANISH: "Plano de referencia: {value}",
    },
    "measurement.feed_line_value": {
        Language.ENGLISH: "Feed line: {value}",
        Language.SPANISH: "Línea: {value}",
    },
    "measurement.notes_value": {
        Language.ENGLISH: "Notes: {value}",
        Language.SPANISH: "Notas: {value}",
    },
    "measurement.select": {
        Language.ENGLISH: "Measurement",
        Language.SPANISH: "Medición",
    },
    "measurement.edit": {
        Language.ENGLISH: "Edit...",
        Language.SPANISH: "Editar...",
    },
    "measurement.delete": {
        Language.ENGLISH: "Delete",
        Language.SPANISH: "Eliminar",
    },
    "measurement.delete_title": {
        Language.ENGLISH: "Delete measurement",
        Language.SPANISH: "Eliminar medición",
    },
    "measurement.delete_confirm": {
        Language.ENGLISH: "Delete measurement '{name}'? This cannot be undone.",
        Language.SPANISH: "¿Eliminar la medición '{name}'? No se puede deshacer.",
    },
    "measurement.none": {
        Language.ENGLISH: "No measurements imported.",
        Language.SPANISH: "No hay mediciones importadas.",
    },
    "measurement.swr": {
        Language.ENGLISH: "Measured and simulated SWR",
        Language.SPANISH: "ROE medida y simulada",
    },
    "measurement.measured": {
        Language.ENGLISH: "Measured",
        Language.SPANISH: "Medida",
    },
    "measurement.simulated": {
        Language.ENGLISH: "Simulated",
        Language.SPANISH: "Simulada",
    },
    "measurement.metric": {
        Language.ENGLISH: "Plot",
        Language.SPANISH: "Gráfico",
    },
    "measurement.measured_title": {
        Language.ENGLISH: "Measured: {metric}",
        Language.SPANISH: "Medido: {metric}",
    },
    "measurement.comparison_title": {
        Language.ENGLISH: "Measured vs simulated: {metric}",
        Language.SPANISH: "Medido vs simulado: {metric}",
    },
    "measurement.resonance_measured": {
        Language.ENGLISH: "Measured resonance: {frequency} MHz (R={resistance} Ω)",
        Language.SPANISH: "Resonancia medida: {frequency} MHz (R={resistance} Ω)",
    },
    "measurement.resonance_simulated": {
        Language.ENGLISH: "Simulated resonance: {frequency} MHz (R={resistance} Ω)",
        Language.SPANISH: "Resonancia simulada: {frequency} MHz (R={resistance} Ω)",
    },
    "measurement.resonance_delta": {
        Language.ENGLISH: "Resonance difference: {delta} MHz",
        Language.SPANISH: "Diferencia de resonancia: {delta} MHz",
    },
    "measurement.resonance_none": {
        Language.ENGLISH: "No measured resonance in the sweep.",
        Language.SPANISH: "Sin resonancia medida en el barrido.",
    },
    "tab.diagnostics": {Language.ENGLISH: "Diagnostics", Language.SPANISH: "Diagnósticos"},
    "tab.raw": {Language.ENGLISH: "Raw data", Language.SPANISH: "Datos crudos"},
    "table.frequency": {Language.ENGLISH: "Frequency (MHz)", Language.SPANISH: "Frecuencia (MHz)"},
    "table.resistance": {Language.ENGLISH: "R (Ω)", Language.SPANISH: "R (Ω)"},
    "table.reactance": {Language.ENGLISH: "X (Ω)", Language.SPANISH: "X (Ω)"},
    "table.impedance": {Language.ENGLISH: "|Z| (Ω)", Language.SPANISH: "|Z| (Ω)"},
    "table.swr": {Language.ENGLISH: "SWR", Language.SPANISH: "ROE"},
    "table.swr_target": {
        Language.ENGLISH: "SWR (target)",
        Language.SPANISH: "ROE (objetivo)",
    },
    "pattern.settings_title": {
        Language.ENGLISH: "Simulation pattern",
        Language.SPANISH: "Patrón de simulación",
    },
    "pattern.frequency": {Language.ENGLISH: "Frequency", Language.SPANISH: "Frecuencia"},
    "pattern.cut_phi": {
        Language.ENGLISH: "Plane φ",
        Language.SPANISH: "Plano φ",
    },
    "pattern.cut_theta": {
        Language.ENGLISH: "Elevation θ",
        Language.SPANISH: "Elevación θ",
    },
    "pattern.mode": {Language.ENGLISH: "Pattern", Language.SPANISH: "Patrón"},
    "pattern.mode_azimuth": {
        Language.ENGLISH: "Azimuth",
        Language.SPANISH: "Azimut",
    },
    "pattern.mode_elevation": {
        Language.ENGLISH: "Elevation",
        Language.SPANISH: "Elevación",
    },
    "pattern.azimuth": {Language.ENGLISH: "Azimuth φ (°)", Language.SPANISH: "Azimut φ (°)"},
    "pattern.polar_elevation": {
        Language.ENGLISH: "Elevation lobes",
        Language.SPANISH: "Lóbulos de elevación",
    },
    "pattern.polar_azimuth": {
        Language.ENGLISH: "Azimuth lobes",
        Language.SPANISH: "Lóbulos de azimut",
    },
    "pattern.cut_tab": {
        Language.ENGLISH: "Cuts",
        Language.SPANISH: "Cortes",
    },
    "pattern.3d_tab": {
        Language.ENGLISH: "3D lobe",
        Language.SPANISH: "Lóbulo 3D",
    },
    "pattern.ground": {
        Language.ENGLISH: "Ground",
        Language.SPANISH: "Suelo",
    },
    "pattern.max_gain_ground": {
        Language.ENGLISH: "Power gain {gain:.2f} dBi · {angle:.1f}° above ground",
        Language.SPANISH: "Ganancia de potencia {gain:.2f} dBi · {angle:.1f}° sobre el suelo",
    },
    "pattern.max_gain_elevation": {
        Language.ENGLISH: "Power gain {gain:.2f} dBi · {angle:.1f}° elevation",
        Language.SPANISH: "Ganancia de potencia {gain:.2f} dBi · {angle:.1f}° de elevación",
    },
    "pattern.3d_hint": {
        Language.ENGLISH: "Drag to rotate · Wheel to zoom · Double-click to reset",
        Language.SPANISH: "Arrastrá para rotar · Rueda para zoom · Doble clic para restablecer",
    },
    "pattern.3d_polar": {
        Language.ENGLISH: "3D radiation pattern",
        Language.SPANISH: "Patrón de radiación 3D",
    },
    "pattern.antenna": {
        Language.ENGLISH: "Antenna",
        Language.SPANISH: "Antena",
    },
    "pattern.elevation": {Language.ENGLISH: "Elevation θ (°)", Language.SPANISH: "Elevación θ (°)"},
    "pattern.gain": {
        Language.ENGLISH: "Power gain (dBi)",
        Language.SPANISH: "Ganancia de potencia (dBi)",
    },
    "pattern.metric": {
        Language.ENGLISH: "Metric",
        Language.SPANISH: "Métrica",
    },
    "pattern.metric.power": {
        Language.ENGLISH: "Power gain",
        Language.SPANISH: "Ganancia de potencia",
    },
    "pattern.metric.directivity": {
        Language.ENGLISH: "Directivity",
        Language.SPANISH: "Directividad",
    },
    "pattern.metric.realized": {
        Language.ENGLISH: "Realized gain",
        Language.SPANISH: "Ganancia realizada",
    },
    "pattern.metric_axis": {
        Language.ENGLISH: "{metric} (dBi)",
        Language.SPANISH: "{metric} (dBi)",
    },
    "pattern.metric_unavailable": {
        Language.ENGLISH: "{metric} is unavailable for this frequency.",
        Language.SPANISH: "{metric} no está disponible para esta frecuencia.",
    },
    "pattern.none": {
        Language.ENGLISH: "No far-field pattern available.",
        Language.SPANISH: "No hay patrón de campo lejano disponible.",
    },
    "pattern.negative_resistance": {
        Language.ENGLISH: (
            "No pattern: negative input resistance. Check very short gaps or "
            "matching wires, segmentation, radial height, and the ground model."
        ),
        Language.SPANISH: (
            "Sin patrón: resistencia de entrada negativa. Revisá gaps o hilos de "
            "adaptación muy cortos, la segmentación, la altura de los radiales y el "
            "modelo de suelo."
        ),
    },
    "pattern.polar": {
        Language.ENGLISH: "Elevation lobes",
        Language.SPANISH: "Lóbulos de elevación",
    },
    "currents.frequency": {Language.ENGLISH: "Frequency", Language.SPANISH: "Frecuencia"},
    "compare.title": {Language.ENGLISH: "Compare Designs", Language.SPANISH: "Comparar diseños"},
    "compare.variant_a": {Language.ENGLISH: "Design A", Language.SPANISH: "Diseño A"},
    "compare.variant_b": {Language.ENGLISH: "Design B", Language.SPANISH: "Diseño B"},
    "compare.metric": {Language.ENGLISH: "Metric", Language.SPANISH: "Métrica"},
    "compare.swr": {Language.ENGLISH: "SWR comparison", Language.SPANISH: "Comparación de ROE"},
    "compare.pattern": {
        Language.ENGLISH: "Pattern comparison",
        Language.SPANISH: "Comparación de patrón",
    },
    "compare.max_gain": {
        Language.ENGLISH: "Max power gain (dBi)",
        Language.SPANISH: "Ganancia máxima de potencia (dBi)",
    },
    "compare.max_directivity": {
        Language.ENGLISH: "Max directivity (dBi)",
        Language.SPANISH: "Directividad máxima (dBi)",
    },
    "compare.max_realized_gain": {
        Language.ENGLISH: "Max realized gain (dBi)",
        Language.SPANISH: "Ganancia realizada máxima (dBi)",
    },
    "compare.efficiency": {Language.ENGLISH: "Efficiency (%)", Language.SPANISH: "Eficiencia (%)"},
    "compare.no_result": {
        Language.ENGLISH: "Simulate a design to include it in the comparison.",
        Language.SPANISH: "Simulá un diseño para incluirlo en la comparación.",
    },
    "action.compare": {
        Language.ENGLISH: "Compare Designs...",
        Language.SPANISH: "Comparar diseños...",
    },
    "action.new_variant": {
        Language.ENGLISH: "New Design in Project...",
        Language.SPANISH: "Nuevo diseño en el proyecto...",
    },
    "action.rename_variant": {
        Language.ENGLISH: "Rename Design...",
        Language.SPANISH: "Renombrar diseño...",
    },
    "action.delete_variant": {
        Language.ENGLISH: "Delete Design",
        Language.SPANISH: "Eliminar diseño",
    },
    "action.export_csv": {Language.ENGLISH: "Export CSV...", Language.SPANISH: "Exportar CSV..."},
    "action.export_pattern_csv": {
        Language.ENGLISH: "Export Pattern CSV...",
        Language.SPANISH: "Exportar CSV de patrón...",
    },
    "action.export_pattern_png": {
        Language.ENGLISH: "Export Pattern PNG...",
        Language.SPANISH: "Exportar PNG de patrón...",
    },
    "action.export_geometry_png": {
        Language.ENGLISH: "Export Geometry PNG...",
        Language.SPANISH: "Exportar PNG de geometría...",
    },
    "action.export_geometry_svg": {
        Language.ENGLISH: "Export Geometry SVG...",
        Language.SPANISH: "Exportar SVG de geometría...",
    },
    "action.export_geometry_pdf": {
        Language.ENGLISH: "Export Geometry PDF...",
        Language.SPANISH: "Exportar PDF de geometría...",
    },
    "action.export_geometry_dxf": {
        Language.ENGLISH: "Export Geometry DXF...",
        Language.SPANISH: "Exportar DXF de geometría...",
    },
    "action.export_html": {
        Language.ENGLISH: "Export HTML Report...",
        Language.SPANISH: "Exportar informe HTML...",
    },
    "action.export_pdf": {
        Language.ENGLISH: "Export PDF Report...",
        Language.SPANISH: "Exportar informe PDF...",
    },
    "action.compact_history": {
        Language.ENGLISH: "Compact Simulation History...",
        Language.SPANISH: "Compactar historial de simulaciones...",
    },
    "variant.label": {Language.ENGLISH: "Design", Language.SPANISH: "Diseño"},
    "variant.name": {Language.ENGLISH: "Design name", Language.SPANISH: "Nombre del diseño"},
    "variant.new_title": {
        Language.ENGLISH: "New Design in Project",
        Language.SPANISH: "Nuevo diseño en el proyecto",
    },
    "variant.rename_title": {
        Language.ENGLISH: "Rename Design",
        Language.SPANISH: "Renombrar diseño",
    },
    "variant.delete_title": {
        Language.ENGLISH: "Delete Design",
        Language.SPANISH: "Eliminar diseño",
    },
    "variant.delete_confirm": {
        Language.ENGLISH: "Delete design “{name}”?",
        Language.SPANISH: "¿Eliminar el diseño “{name}”?",
    },
    "variant.last_cannot_delete": {
        Language.ENGLISH: "A project must keep at least one design.",
        Language.SPANISH: "Un proyecto debe conservar al menos un diseño.",
    },
    "dialog.pattern_csv_title": {
        Language.ENGLISH: "Save pattern CSV",
        Language.SPANISH: "Guardar CSV de patrón",
    },
    "dialog.mmana_title": {
        Language.ENGLISH: "Import MMANA file",
        Language.SPANISH: "Importar archivo MMANA",
    },
    "dialog.mmana_filter": {
        Language.ENGLISH: "MMANA files (*.maa *.MAA);;All files (*)",
        Language.SPANISH: "Archivos MMANA (*.maa *.MAA);;Todos los archivos (*)",
    },
    "dialog.mmana_warnings": {
        Language.ENGLISH: "Imported with {count} warning(s):\n{details}",
        Language.SPANISH: "Importado con {count} advertencia(s):\n{details}",
    },
    "error.import_mmana": {
        Language.ENGLISH: "Could not import MMANA file: {message}",
        Language.SPANISH: "No se pudo importar el archivo MMANA: {message}",
    },
    "error.import_nec": {
        Language.ENGLISH: "Could not import NEC deck: {message}",
        Language.SPANISH: "No se pudo importar el archivo NEC: {message}",
    },
    "dialog.nec_title": {
        Language.ENGLISH: "Import NEC deck",
        Language.SPANISH: "Importar archivo NEC",
    },
    "dialog.nec_filter": {
        Language.ENGLISH: "NEC decks (*.nec *.NEC *.txt);;All files (*)",
        Language.SPANISH: "Archivos NEC (*.nec *.NEC *.txt);;Todos los archivos (*)",
    },
    "dialog.nec_warnings": {
        Language.ENGLISH: "Imported with {count} warning(s):\n{details}",
        Language.SPANISH: "Importado con {count} advertencia(s):\n{details}",
    },
    "dialog.undo_dirty_title": {
        Language.ENGLISH: "Unapplied design changes",
        Language.SPANISH: "Cambios de diseño sin aplicar",
    },
    "dialog.undo_dirty_message": {
        Language.ENGLISH: "There are unapplied design changes. Discard them and undo?",
        Language.SPANISH: "Hay cambios de diseño sin aplicar. ¿Descartarlos y deshacer?",
    },
    "dialog.redo_dirty_message": {
        Language.ENGLISH: "There are unapplied design changes. Discard them and redo?",
        Language.SPANISH: "Hay cambios de diseño sin aplicar. ¿Descartarlos y rehacer?",
    },
    "dialog.yagi_mismatch_title": {
        Language.ENGLISH: "Yagi dimensions and frequency",
        Language.SPANISH: "Dimensiones y frecuencia de la Yagi",
    },
    "dialog.yagi_mismatch_message": {
        Language.ENGLISH: "Element lengths do not look consistent with the design frequency. Simulate anyway?",
        Language.SPANISH: "Las longitudes de los elementos no parecen coincidir con la frecuencia de diseño. ¿Simular igualmente?",
    },
    "dialog.geometry_png_title": {
        Language.ENGLISH: "Save geometry image",
        Language.SPANISH: "Guardar imagen de geometría",
    },
    "dialog.geometry_svg_title": {
        Language.ENGLISH: "Save geometry SVG",
        Language.SPANISH: "Guardar SVG de geometría",
    },
    "dialog.geometry_pdf_title": {
        Language.ENGLISH: "Save geometry PDF",
        Language.SPANISH: "Guardar PDF de geometría",
    },
    "dialog.geometry_dxf_title": {
        Language.ENGLISH: "Save geometry DXF",
        Language.SPANISH: "Guardar DXF de geometría",
    },
    "dialog.pattern_png_title": {
        Language.ENGLISH: "Save pattern image",
        Language.SPANISH: "Guardar imagen de patrón",
    },
    "dialog.band_pattern_png_title": {
        Language.ENGLISH: "Select a folder for the band pattern images",
        Language.SPANISH: "Seleccioná una carpeta para las imágenes de patrón por banda",
    },
    "dialog.csv_title": {
        Language.ENGLISH: "Export simulation CSV",
        Language.SPANISH: "Exportar CSV de simulación",
    },
    "dialog.html_title": {
        Language.ENGLISH: "Export HTML report",
        Language.SPANISH: "Exportar informe HTML",
    },
    "dialog.png_filter": {
        Language.ENGLISH: "PNG images (*.png)",
        Language.SPANISH: "Imágenes PNG (*.png)",
    },
    "dialog.svg_filter": {
        Language.ENGLISH: "SVG images (*.svg)",
        Language.SPANISH: "Imágenes SVG (*.svg)",
    },
    "dialog.dxf_filter": {
        Language.ENGLISH: "DXF drawings (*.dxf)",
        Language.SPANISH: "Dibujos DXF (*.dxf)",
    },
    "dialog.csv_filter": {
        Language.ENGLISH: "CSV files (*.csv);;All files (*)",
        Language.SPANISH: "Archivos CSV (*.csv);;Todos los archivos (*)",
    },
    "dialog.html_filter": {
        Language.ENGLISH: "HTML files (*.html);;All files (*)",
        Language.SPANISH: "Archivos HTML (*.html);;Todos los archivos (*)",
    },
    "status.exported": {
        Language.ENGLISH: "Export complete.",
        Language.SPANISH: "Exportación completada.",
    },
    "status.compacted": {
        Language.ENGLISH: "Simulation history compacted.",
        Language.SPANISH: "Historial de simulaciones compactado.",
    },
    "variant.copy_name": {Language.ENGLISH: "{name} copy", Language.SPANISH: "{name} copia"},
    "error.no_result": {
        Language.ENGLISH: "Simulate the current design before exporting.",
        Language.SPANISH: "Simulá el diseño actual antes de exportar.",
    },
    "error.invalid_sweep": {
        Language.ENGLISH: "Sweep start must be lower than sweep stop.",
        Language.SPANISH: "El inicio del barrido debe ser menor que el fin.",
    },
    "error.estimate_changes_template": {
        Language.ENGLISH: (
            "The estimate attempted to change the current template. "
            "Use Change Template explicitly if you want a different family."
        ),
        Language.SPANISH: (
            "La estimación intentó cambiar la plantilla actual. Usá Cambiar "
            "plantilla de forma explícita si querés otra familia."
        ),
    },
    "error.export": {
        Language.ENGLISH: "Could not export: {message}",
        Language.SPANISH: "No se pudo exportar: {message}",
    },
    "action.undo": {Language.ENGLISH: "Undo", Language.SPANISH: "Deshacer"},
    "action.redo": {Language.ENGLISH: "Redo", Language.SPANISH: "Rehacer"},
    "history.apply_design": {
        Language.ENGLISH: "Apply design",
        Language.SPANISH: "Aplicar diseño",
    },
    "history.change_template": {
        Language.ENGLISH: "Change template",
        Language.SPANISH: "Cambiar plantilla",
    },
    "history.design_from_frequency": {
        Language.ENGLISH: "Estimate dimensions",
        Language.SPANISH: "Estimar dimensiones",
    },
    "history.new_variant": {
        Language.ENGLISH: "New design in project",
        Language.SPANISH: "Nuevo diseño en el proyecto",
    },
    "history.rename_variant": {
        Language.ENGLISH: "Rename design",
        Language.SPANISH: "Renombrar diseño",
    },
    "history.delete_variant": {
        Language.ENGLISH: "Delete design",
        Language.SPANISH: "Eliminar diseño",
    },
    "history.feed_line": {
        Language.ENGLISH: "Feed line",
        Language.SPANISH: "Línea de alimentación",
    },
    "history.matching_network": {
        Language.ENGLISH: "Matching network",
        Language.SPANISH: "Red de adaptación",
    },
    "history.balun_loss": {
        Language.ENGLISH: "Balun/unun loss",
        Language.SPANISH: "Pérdida de balun/unun",
    },
    "history.loads": {
        Language.ENGLISH: "Series loads",
        Language.SPANISH: "Cargas serie",
    },
    "history.measurement_import": {
        Language.ENGLISH: "Import measurement",
        Language.SPANISH: "Importar medición",
    },
    "history.measurement_edit": {
        Language.ENGLISH: "Edit measurement",
        Language.SPANISH: "Editar medición",
    },
    "history.measurement_delete": {
        Language.ENGLISH: "Delete measurement",
        Language.SPANISH: "Eliminar medición",
    },
    "history.simulate": {
        Language.ENGLISH: "Simulate",
        Language.SPANISH: "Simular",
    },
    "history.optimize": {
        Language.ENGLISH: "Optimize dimensions",
        Language.SPANISH: "Optimizar dimensiones",
    },
    "history.convert_custom": {
        Language.ENGLISH: "Convert to custom wires",
        Language.SPANISH: "Convertir a hilos personalizados",
    },
    "history.edit_generator": {
        Language.ENGLISH: "Edit generator",
        Language.SPANISH: "Editar generador",
    },
    "history.edit_custom": {
        Language.ENGLISH: "Edit custom wires",
        Language.SPANISH: "Editar hilos personalizados",
    },
    "history.save": {
        Language.ENGLISH: "Apply design before saving",
        Language.SPANISH: "Aplicar diseño antes de guardar",
    },
    "action.optimize": {
        Language.ENGLISH: "Optimize...",
        Language.SPANISH: "Optimizar...",
    },
    "action.design_from_frequency": {
        Language.ENGLISH: "Estimate Dimensions...",
        Language.SPANISH: "Estimar dimensiones...",
    },
    "action.synthesize": {
        Language.ENGLISH: "Synthesize Dimensions...",
        Language.SPANISH: "Sintetizar dimensiones...",
    },
    "action.optimize_yagi": {
        Language.ENGLISH: "Optimize Yagi Elements...",
        Language.SPANISH: "Optimizar elementos del Yagi...",
    },
    "action.optimize_fan": {
        Language.ENGLISH: "Optimize Fan Elements...",
        Language.SPANISH: "Optimizar elementos del dipolo abanico...",
    },
    "action.optimize_moxon": {
        Language.ENGLISH: "Optimize Moxon Dimensions...",
        Language.SPANISH: "Optimizar dimensiones del Moxon...",
    },
    "action.construction": {
        Language.ENGLISH: "Construction Sheet...",
        Language.SPANISH: "Hoja de construcción...",
    },
    "construction.title": {
        Language.ENGLISH: "Construction Sheet",
        Language.SPANISH: "Hoja de construcción",
    },
    "construction.save": {
        Language.ENGLISH: "Save HTML...",
        Language.SPANISH: "Guardar HTML...",
    },
    "construction.save_pdf": {
        Language.ENGLISH: "Save PDF...",
        Language.SPANISH: "Guardar PDF...",
    },
    "construction.pdf_subtitle": {
        Language.ENGLISH: "AntennaDesk construction sheet · SI units",
        Language.SPANISH: "Hoja de construcción de AntennaDesk · unidades SI",
    },
    "construction.dimensions": {
        Language.ENGLISH: "Dimensions",
        Language.SPANISH: "Dimensiones",
    },
    "construction.feed_height": {
        Language.ENGLISH: "Feed height above ground",
        Language.SPANISH: "Altura de alimentación sobre el suelo",
    },
    "construction.simulation": {
        Language.ENGLISH: "Simulation",
        Language.SPANISH: "Simulación",
    },
    "construction.no_result": {
        Language.ENGLISH: "No result yet.",
        Language.SPANISH: "Todavía no hay resultado.",
    },
    "construction.solver": {Language.ENGLISH: "Solver", Language.SPANISH: "Solver"},
    "construction.fingerprint": {
        Language.ENGLISH: "Fingerprint",
        Language.SPANISH: "Huella",
    },
    "construction.simulated_frequency": {
        Language.ENGLISH: "Simulated frequency",
        Language.SPANISH: "Frecuencia simulada",
    },
    "construction.impedance": {
        Language.ENGLISH: "Impedance",
        Language.SPANISH: "Impedancia",
    },
    "construction.max_gain": {
        Language.ENGLISH: "Max power gain",
        Language.SPANISH: "Ganancia máxima de potencia",
    },
    "construction.efficiency": {
        Language.ENGLISH: "Efficiency",
        Language.SPANISH: "Eficiencia",
    },
    "construction.resonance": {
        Language.ENGLISH: "Resonance",
        Language.SPANISH: "Resonancia",
    },
    "construction.no_resonance": {
        Language.ENGLISH: "No resonance in the sweep.",
        Language.SPANISH: "No hay resonancia en el barrido.",
    },
    "construction.notes": {
        Language.ENGLISH: "Construction notes",
        Language.SPANISH: "Notas de construcción",
    },
    "construction.pdf_notes": {
        Language.ENGLISH: "Trim and re-measure after installation. Real ground, supports, feed line, and nearby objects can shift the result. A low SWR does not prove high efficiency or a useful radiation pattern.",
        Language.SPANISH: "Recortá y volvé a medir después de la instalación. El suelo real, los soportes, la línea de alimentación y los objetos cercanos pueden modificar el resultado. Una ROE baja no garantiza alta eficiencia ni un patrón útil.",
    },
    "construction.pdf_footer": {
        Language.ENGLISH: "AntennaDesk · GPL-3.0-or-later",
        Language.SPANISH: "AntennaDesk · GPL-3.0-or-later",
    },
    "report.pdf_subtitle": {
        Language.ENGLISH: "AntennaDesk simulation report · finished {finished}",
        Language.SPANISH: "Informe de simulación de AntennaDesk · finalizado {finished}",
    },
    "report.not_recorded": {
        Language.ENGLISH: "not recorded",
        Language.SPANISH: "sin registrar",
    },
    "report.reproducibility": {
        Language.ENGLISH: "Reproducibility",
        Language.SPANISH: "Reproducibilidad",
    },
    "report.gain": {
        Language.ENGLISH: "Gain and efficiency",
        Language.SPANISH: "Ganancia y eficiencia",
    },
    "report.configuration": {
        Language.ENGLISH: "Simulation configuration",
        Language.SPANISH: "Configuración de la simulación",
    },
    "report.frequency_plan": {
        Language.ENGLISH: "Frequency plan",
        Language.SPANISH: "Plan de frecuencia",
    },
    "report.reference_impedance": {
        Language.ENGLISH: "Reference impedance",
        Language.SPANISH: "Impedancia de referencia",
    },
    "report.conductor_losses": {
        Language.ENGLISH: "Conductor losses",
        Language.SPANISH: "Pérdidas en conductores",
    },
    "report.far_field": {
        Language.ENGLISH: "Far field",
        Language.SPANISH: "Campo lejano",
    },
    "report.enabled": {Language.ENGLISH: "enabled", Language.SPANISH: "habilitado"},
    "report.disabled": {Language.ENGLISH: "disabled", Language.SPANISH: "deshabilitado"},
    "report.resonance": {
        Language.ENGLISH: "Resonance",
        Language.SPANISH: "Resonancia",
    },
    "report.charts": {Language.ENGLISH: "Charts", Language.SPANISH: "Gráficos"},
    "dialog.pdf_title": {
        Language.ENGLISH: "Save PDF",
        Language.SPANISH: "Guardar PDF",
    },
    "dialog.pdf_filter": {
        Language.ENGLISH: "PDF files (*.pdf)",
        Language.SPANISH: "Archivos PDF (*.pdf)",
    },
    "dialog.large_project": {
        Language.ENGLISH: "Project is {size:.1f} MB. Save anyway? Use Compact Simulation History to reduce it.",
        Language.SPANISH: "El proyecto pesa {size:.1f} MB. ¿Guardar igualmente? Usá Compactar historial para reducirlo.",
    },
    "dialog.project_too_large": {
        Language.ENGLISH: "Project is {size:.1f} MB and exceeds the {limit:.0f} MB limit. Compact Simulation History or remove designs.",
        Language.SPANISH: "El proyecto pesa {size:.1f} MB y supera el límite de {limit:.0f} MB. Compactá el historial o eliminá diseños.",
    },
    "dialog.compact_history": {
        Language.ENGLISH: "Remove older simulation runs? {count} runs will be reduced to the latest run per design ({keep} kept).",
        Language.SPANISH: "¿Eliminar corridas antiguas? {count} corridas se reducirán a la última por diseño ({keep} conservadas).",
    },
    "dialog.construction_title": {
        Language.ENGLISH: "Save construction sheet",
        Language.SPANISH: "Guardar hoja de construcción",
    },
    "custom.pattern_resolution": {
        Language.ENGLISH: "Pattern resolution",
        Language.SPANISH: "Resolución del patrón",
    },
    "custom.pattern_auto": {
        Language.ENGLISH: "Auto (max)",
        Language.SPANISH: "Automática (máx.)",
    },
    "custom.pattern_frequencies": {
        Language.ENGLISH: "Pattern frequencies",
        Language.SPANISH: "Frecuencias de patrón",
    },
    "custom.pattern_frequencies_auto": {
        Language.ENGLISH: "Auto (bands)",
        Language.SPANISH: "Automática (bandas)",
    },
    "custom.pattern_frequencies_option": {
        Language.ENGLISH: "{count} frequencies",
        Language.SPANISH: "{count} frecuencias",
    },
    "custom.pattern_requested": {
        Language.ENGLISH: (
            "Requested resolution: {value} · {count} pattern frequencies ({sweep} sweep points)"
        ),
        Language.SPANISH: (
            "Resolución solicitada: {value} · {count} frecuencias de patrón "
            "({sweep} puntos de barrido)"
        ),
    },
    "custom.pattern_effective": {
        Language.ENGLISH: (
            "Using {value} at {patterns} pattern frequencies · estimated project size {size:.1f} MB"
        ),
        Language.SPANISH: (
            "Usando {value} en {patterns} frecuencias de patrón · tamaño estimado del "
            "proyecto {size:.1f} MB"
        ),
    },
    "custom.pattern_reduced": {
        Language.ENGLISH: (
            "Using {value} (requested {requested}) at {patterns} pattern frequencies · "
            "estimated project size {size:.1f} MB"
        ),
        Language.SPANISH: (
            "Usando {value} (solicitada {requested}) en {patterns} frecuencias de patrón · "
            "tamaño estimado del proyecto {size:.1f} MB"
        ),
    },
    "custom.pattern_disabled": {
        Language.ENGLISH: (
            "Pattern disabled: the sweep is too large for the project size "
            "limit. Reduce frequencies or run a shorter pattern sweep."
        ),
        Language.SPANISH: (
            "Patrón desactivado: el barrido es demasiado grande para el límite "
            "de tamaño del proyecto. Reducí las frecuencias o hacé un barrido "
            "de patrón más corto."
        ),
    },
    "custom.title": {
        Language.ENGLISH: "Custom wire antenna",
        Language.SPANISH: "Antena de hilos personalizada",
    },
    "yagi.title": {
        Language.ENGLISH: "Yagi Generator",
        Language.SPANISH: "Generador de Yagi",
    },
    "inverted_l.title": {
        Language.ENGLISH: "Inverted-L Generator",
        Language.SPANISH: "Generador de L invertida",
    },
    "inverted_l.vertical_height": {
        Language.ENGLISH: "Vertical height",
        Language.SPANISH: "Altura vertical",
    },
    "inverted_l.horizontal_length": {
        Language.ENGLISH: "Horizontal length",
        Language.SPANISH: "Longitud horizontal",
    },
    "inverted_l.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "inverted_l.geometry": {
        Language.ENGLISH: "Total wire {total} {unit} · top {top} {unit}",
        Language.SPANISH: "Hilo total {total} {unit} · parte superior {top} {unit}",
    },
    "inverted_l.hint": {
        Language.ENGLISH: (
            "The vertical section is fed at the base and continues into a "
            "horizontal top wire. Define the azimuth as the direction of the "
            "horizontal run; base height keeps the feed and corner above ground."
        ),
        Language.SPANISH: (
            "La sección vertical se alimenta en la base y continúa en un tramo "
            "horizontal superior. El azimut define la dirección del tramo "
            "horizontal; la altura de base mantiene la alimentación y la esquina "
            "sobre el suelo."
        ),
    },
    "inverted_l.evidence": {
        Language.ENGLISH: (
            "Experimental generator: the bent-wire geometry is tested, but "
            "there is no independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueba la geometría de hilo doblado, "
            "pero no hay una referencia numérica independiente para esta "
            "configuración."
        ),
    },
    "magnetic_loop.title": {
        Language.ENGLISH: "Magnetic-Loop Generator",
        Language.SPANISH: "Generador de lazo magnético",
    },
    "magnetic_loop.diameter": {
        Language.ENGLISH: "Loop diameter",
        Language.SPANISH: "Diámetro del lazo",
    },
    "magnetic_loop.height": {
        Language.ENGLISH: "Bottom height",
        Language.SPANISH: "Altura inferior",
    },
    "magnetic_loop.sides": {
        Language.ENGLISH: "Polygon sides",
        Language.SPANISH: "Lados del polígono",
    },
    "magnetic_loop.gap": {
        Language.ENGLISH: "Tuning gap",
        Language.SPANISH: "Gap de sintonía",
    },
    "magnetic_loop.capacitance": {
        Language.ENGLISH: "Tuning capacitance",
        Language.SPANISH: "Capacidad de sintonía",
    },
    "magnetic_loop.esr": {
        Language.ENGLISH: "Capacitor ESR",
        Language.SPANISH: "ESR del capacitor",
    },
    "magnetic_loop.geometry": {
        Language.ENGLISH: (
            "Diameter {diameter} {unit} · path {circumference} {unit} · "
            "top {top} {unit} · gap {gap} {unit} · {capacitance} pF"
        ),
        Language.SPANISH: (
            "Diámetro {diameter} {unit} · recorrido {circumference} {unit} · "
            "superior {top} {unit} · gap {gap} {unit} · {capacitance} pF"
        ),
    },
    "magnetic_loop.model_hint": {
        Language.ENGLISH: (
            "The capacitor is an ideal series RLC element with the entered ESR. "
            "Conductor loss comes from the material and radius; a coupling loop "
            "and capacitor voltage are not modeled."
        ),
        Language.SPANISH: (
            "El capacitor es un elemento RLC serie ideal con la ESR ingresada. "
            "La pérdida del conductor surge del material y el radio; no se "
            "modelan el lazo de acoplamiento ni la tensión del capacitor."
        ),
    },
    "magnetic_loop.hint": {
        Language.ENGLISH: (
            "The loop is a vertical regular polygon with a gap centred on the "
            "top side. The feed is at the midpoint of the bottom side. Tune the "
            "capacitance with a fine SWR sweep or a measurement."
        ),
        Language.SPANISH: (
            "El lazo es un polígono regular vertical con un gap centrado en el "
            "lado superior. La alimentación está en el punto medio del lado "
            "inferior. Sintonizá la capacidad con un barrido fino de ROE o una "
            "medición."
        ),
    },
    "magnetic_loop.evidence": {
        Language.ENGLISH: (
            "Experimental model: geometry, gap, and series capacitor are tested, "
            "but there is no independent numerical reference for the generated "
            "design. Efficiency and bandwidth depend on conductor loss, capacitor "
            "ESR, and the matching network."
        ),
        Language.SPANISH: (
            "Modelo experimental: se prueban la geometría, el gap y el capacitor "
            "serie, pero no hay una referencia numérica independiente para el "
            "diseño generado. La eficiencia y el ancho de banda dependen de la "
            "pérdida del conductor, la ESR del capacitor y la red de adaptación."
        ),
    },
    "inverted_v.title": {
        Language.ENGLISH: "Inverted-V Generator",
        Language.SPANISH: "Generador de V invertida",
    },
    "scv.title": {
        Language.ENGLISH: "Half-Square / Bobtail-Curtain Generator",
        Language.SPANISH: "Generador de medio cuadrado / cortina bobtail",
    },
    "scv.kind": {
        Language.ENGLISH: "Array type",
        Language.SPANISH: "Tipo de conjunto",
    },
    "scv.kind.half_square": {
        Language.ENGLISH: "Half square",
        Language.SPANISH: "Medio cuadrado",
    },
    "scv.kind.bobtail_curtain": {
        Language.ENGLISH: "Bobtail curtain",
        Language.SPANISH: "Cortina bobtail",
    },
    "scv.horizontal_length": {
        Language.ENGLISH: "Overall horizontal length",
        Language.SPANISH: "Longitud horizontal total",
    },
    "scv.vertical_height": {
        Language.ENGLISH: "Vertical height",
        Language.SPANISH: "Altura vertical",
    },
    "scv.vertical_elements": {
        Language.ENGLISH: "Vertical elements",
        Language.SPANISH: "Elementos verticales",
    },
    "scv.feed_top": {
        Language.ENGLISH: "feed at top junction",
        Language.SPANISH: "alimentación en la unión superior",
    },
    "scv.feed_offset": {
        Language.ENGLISH: "Feed offset below top junction",
        Language.SPANISH: "Offset de alimentación bajo la unión superior",
    },
    "scv.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "scv.geometry": {
        Language.ENGLISH: "{type} · horizontal {horizontal} {unit} · vertical {vertical} {unit}",
        Language.SPANISH: ("{type} · horizontal {horizontal} {unit} · vertical {vertical} {unit}"),
    },
    "scv.load_reference": {
        Language.ENGLISH: "Load Cebik 7.15 MHz reference",
        Language.SPANISH: "Cargar referencia Cebik de 7,15 MHz",
    },
    "scv.load_reference_hint": {
        Language.ENGLISH: "Load the published 62.4 x 39 ft or 125 x 38 ft dimensions.",
        Language.SPANISH: "Carga las dimensiones publicadas de 62,4 x 39 ft o 125 x 38 ft.",
    },
    "scv.hint": {
        Language.ENGLISH: (
            "Both arrays are monoband, broadside, vertically polarized wire "
            "antennas. The half square uses two quarter-wave verticals and a "
            "half-wave top; the bobtail curtain adds a third vertical and a "
            "second top section. Feed at the top junction of an outer vertical "
            "(half square) or the center vertical (bobtail), not at a bottom "
            "voltage point. Moving the feed down the fed vertical is a matching "
            "adjustment. The published Cebik dimensions are a free-space starting "
            "point; ground, support height, and the feed line remain "
            "installation-specific."
        ),
        Language.SPANISH: (
            "Ambos conjuntos son antenas de hilo monobanda, bidireccionales y con "
            "polarización vertical. El medio cuadrado usa dos verticales de cuarto "
            "de onda y un hilo superior de media onda; la cortina bobtail agrega "
            "una tercera vertical y un segundo tramo superior. Alimentá en la unión "
            "superior de una vertical externa (medio cuadrado) o de la vertical "
            "central (bobtail), no en un punto de tensión inferior. Mover la "
            "alimentación hacia abajo de la vertical alimentada es un ajuste de "
            "adaptación. Las dimensiones publicadas de Cebik son un punto de "
            "partida en espacio libre; el suelo, la altura de soporte y la línea "
            "de alimentación dependen de la instalación."
        ),
    },
    "scv.evidence": {
        Language.ENGLISH: (
            "Published Cebik 7.15 MHz free-space starting geometry: half square "
            "62.4 ft by 39 ft, about 4.6 dBi and 65 ohm; bobtail curtain 125 ft by "
            "38 ft, about 6.3 dBi and 40 ohm at the center-wire/top junction. "
            "AntennaDesk does not independently validate the pattern, feedpoint "
            "impedance, ground, or matching."
        ),
        Language.SPANISH: (
            "Geometría inicial publicada por Cebik para 7,15 MHz en espacio libre: "
            "medio cuadrado de 62,4 ft por 39 ft, unos 4,6 dBi y 65 ohm; cortina "
            "bobtail de 125 ft por 38 ft, unos 6,3 dBi y 40 ohm en la unión de la "
            "vertical central con el hilo superior. AntennaDesk no valida "
            "independientemente el patrón, la impedancia de alimentación, el suelo "
            "ni la adaptación."
        ),
    },
    "ringo.title": {
        Language.ENGLISH: "Ringo Generator",
        Language.SPANISH: "Generador Ringo",
    },
    "ringo.radiator_height": {
        Language.ENGLISH: "Radiator height",
        Language.SPANISH: "Altura del radiador",
    },
    "ringo.ring_diameter": {
        Language.ENGLISH: "Ring diameter",
        Language.SPANISH: "Diámetro del anillo",
    },
    "ringo.ring_height": {
        Language.ENGLISH: "Ring height",
        Language.SPANISH: "Altura del anillo",
    },
    "ringo.ring_sides": {
        Language.ENGLISH: "Ring sides",
        Language.SPANISH: "Lados del anillo",
    },
    "ringo.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "ringo.geometry": {
        Language.ENGLISH: "Height {height} {unit} · ring {ring} {unit}",
        Language.SPANISH: "Altura {height} {unit} · anillo {ring} {unit}",
    },
    "ringo.hint": {
        Language.ENGLISH: (
            "The Ringo is a vertical radiator with a horizontal matching ring "
            "at its base. The generated antenna is an editable first-class design."
        ),
        Language.SPANISH: (
            "El Ringo es un radiador vertical con un anillo horizontal de "
            "adaptación en la base. La antena generada es un diseño editable de primera clase."
        ),
    },
    "ringo.evidence": {
        Language.ENGLISH: (
            "Experimental generator: the Cushcraft AR-6 starting dimensions are "
            "published, but the simplified matching ring is not an exact "
            "electrical model and its impedance and pattern are not validated."
        ),
        Language.SPANISH: (
            "Generador experimental: las dimensiones iniciales de la Cushcraft "
            "AR-6 están publicadas, pero el anillo de adaptación simplificado no "
            "es un modelo eléctrico exacto y no se validan impedancia ni patrón."
        ),
    },
    "ringo.ar6_example": {
        Language.ENGLISH: "Load Cushcraft AR-6 dimensions",
        Language.SPANISH: "Cargar dimensiones Cushcraft AR-6",
    },
    "ringo.ar6_example_hint": {
        Language.ENGLISH: (
            "Sets 52 MHz, 3.1 m overall height, and a 0.33 m ring. The ring is "
            "modeled at 0.05 m above the base, so the radiator is 3.05 m."
        ),
        Language.SPANISH: (
            "Configura 52 MHz, 3.1 m de altura total y un anillo de 0.33 m. El "
            "anillo se modela a 0.05 m de la base, por lo que el radiador mide "
            "3.05 m."
        ),
    },
    "j_pole.title": {
        Language.ENGLISH: "J-Pole / Slim-Jim Generator",
        Language.SPANISH: "Generador J Pole / Slim Jim",
    },
    "j_pole.radiator_height": {
        Language.ENGLISH: "Radiator height",
        Language.SPANISH: "Altura del radiador",
    },
    "j_pole.stub_length": {
        Language.ENGLISH: "Stub length",
        Language.SPANISH: "Longitud del stub",
    },
    "j_pole.spacing": {
        Language.ENGLISH: "Stub spacing",
        Language.SPANISH: "Separación del stub",
    },
    "j_pole.feed_offset": {
        Language.ENGLISH: "Feed offset from base",
        Language.SPANISH: "Offset de alimentación desde la base",
    },
    "j_pole.gap": {
        Language.ENGLISH: "Gap",
        Language.SPANISH: "Brecha",
    },
    "j_pole.base_height": {
        Language.ENGLISH: "Base height",
        Language.SPANISH: "Altura de la base",
    },
    "j_pole.folded": {
        Language.ENGLISH: "Folded (Slim Jim)",
        Language.SPANISH: "Plegada (Slim Jim)",
    },
    "j_pole.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "j_pole.geometry": {
        Language.ENGLISH: "{template} · height {height} {unit}",
        Language.SPANISH: "{template} · altura {height} {unit}",
    },
    "j_pole.hint": {
        Language.ENGLISH: (
            "The J Pole has a vertical radiator and a parallel stub. Enable "
            "Folded for a Slim-Jim geometry."
        ),
        Language.SPANISH: (
            "La J Pole tiene un radiador vertical y un stub paralelo. Activá "
            "Plegada para una geometría Slim Jim."
        ),
    },
    "j_pole.evidence": {
        Language.ENGLISH: (
            "Experimental generator: geometry is tested, but there is no "
            "independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueba la geometría, pero no hay una "
            "referencia numérica independiente para esta configuración."
        ),
    },
    "trap_dipole.title": {
        Language.ENGLISH: "Trap Dipole Generator",
        Language.SPANISH: "Generador de dipolo con trampas",
    },
    "trap_dipole.low_band": {
        Language.ENGLISH: "Low-band frequency",
        Language.SPANISH: "Frecuencia de banda baja",
    },
    "trap_dipole.high_band": {
        Language.ENGLISH: "High-band frequency",
        Language.SPANISH: "Frecuencia de banda alta",
    },
    "trap_dipole.inner_length": {
        Language.ENGLISH: "Center section length",
        Language.SPANISH: "Longitud de la sección central",
    },
    "trap_dipole.outer_length": {
        Language.ENGLISH: "Outer section length (each side)",
        Language.SPANISH: "Longitud de la sección exterior (cada lado)",
    },
    "trap_dipole.starting_dimensions": {
        Language.ENGLISH: "Set starting dimensions from bands",
        Language.SPANISH: "Calcular dimensiones iniciales desde las bandas",
    },
    "trap_dipole.trap_frequency": {
        Language.ENGLISH: "Trap frequency",
        Language.SPANISH: "Frecuencia de la trampa",
    },
    "trap_dipole.trap_inductance": {
        Language.ENGLISH: "Trap inductance",
        Language.SPANISH: "Inductancia de la trampa",
    },
    "trap_dipole.trap_capacitance": {
        Language.ENGLISH: "Trap capacitance",
        Language.SPANISH: "Capacitancia de la trampa",
    },
    "trap_dipole.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "trap_dipole.geometry": {
        Language.ENGLISH: (
            "Total {total} {unit} · center {inner} {unit} · traps at {left}/{right} {unit}"
        ),
        Language.SPANISH: (
            "Total {total} {unit} · centro {inner} {unit} · trampas en {left}/{right} {unit}"
        ),
    },
    "trap_dipole.trap_below_high_band": {
        Language.ENGLISH: (
            "Trap frequency is below the high band; verify that the traps "
            "isolate the outer sections."
        ),
        Language.SPANISH: (
            "La frecuencia de la trampa está por debajo de la banda alta; "
            "verificá que las trampas aíslen las secciones exteriores."
        ),
    },
    "trap_dipole.hint": {
        Language.ENGLISH: (
            "Starting dimensions use the half-wave factors for both bands. The "
            "traps load the outer sections on the low band, so the total length "
            "usually needs to be shorter; tune it with the solver. Trap "
            "capacitance is calculated from the target frequency and inductance."
        ),
        Language.SPANISH: (
            "Las dimensiones iniciales usan los factores de media onda para "
            "ambas bandas. Las trampas cargan las secciones exteriores en la "
            "banda baja, así que la longitud total normalmente debe ser menor; "
            "sintonizala con el solver. La capacitancia de la trampa se calcula "
            "a partir de la frecuencia objetivo y la inductancia."
        ),
    },
    "trap_dipole.evidence": {
        Language.ENGLISH: (
            "Experimental template: geometry and parallel LC traps are tested, "
            "but there is no independent numerical reference for this trap dipole."
        ),
        Language.SPANISH: (
            "Plantilla experimental: se prueban la geometría y las trampas LC "
            "paralelas, pero no hay una referencia numérica independiente para "
            "este dipolo con trampas."
        ),
    },
    "t2fd.title": {
        Language.ENGLISH: "T2FD Generator",
        Language.SPANISH: "Generador T2FD",
    },
    "t2fd.lowest_frequency": {
        Language.ENGLISH: "Lowest design frequency",
        Language.SPANISH: "Frecuencia más baja de diseño",
    },
    "t2fd.highest_frequency": {
        Language.ENGLISH: "Highest design frequency",
        Language.SPANISH: "Frecuencia más alta de diseño",
    },
    "t2fd.length": {
        Language.ENGLISH: "Element length",
        Language.SPANISH: "Longitud de cada elemento",
    },
    "t2fd.spacing": {
        Language.ENGLISH: "Conductor spacing",
        Language.SPANISH: "Separación entre conductores",
    },
    "t2fd.starting_dimensions": {
        Language.ENGLISH: "Set starting dimensions from frequency",
        Language.SPANISH: "Calcular dimensiones iniciales desde la frecuencia",
    },
    "t2fd.termination": {
        Language.ENGLISH: "Termination resistance",
        Language.SPANISH: "Resistencia de terminación",
    },
    "t2fd.transformer": {
        Language.ENGLISH: "Feed transformer ratio",
        Language.SPANISH: "Relación del transformador de alimentación",
    },
    "t2fd.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "t2fd.geometry": {
        Language.ENGLISH: (
            "Band {low}-{high} MHz · element {length} {unit} · spacing "
            "{spacing} {unit} · termination {termination} Ω · {ratio}:1"
        ),
        Language.SPANISH: (
            "Banda {low}-{high} MHz · elemento {length} {unit} · separación "
            "{spacing} {unit} · terminación {termination} Ω · {ratio}:1"
        ),
    },
    "t2fd.band_order": {
        Language.ENGLISH: (
            "The highest design frequency must be above the lowest design frequency."
        ),
        Language.SPANISH: ("La frecuencia más alta de diseño debe ser mayor que la más baja."),
    },
    "t2fd.hint": {
        Language.ENGLISH: (
            "Starting dimensions follow Cebik's wide-long T2FD: about "
            "300/F(MHz) feet of span and 10/F(MHz) feet of spacing. The "
            "800 Ω termination and 16:1 transformer follow the commercial "
            "3-30 MHz B&W design. The resistor dissipates a significant part "
            "of the applied power; the model uses an ideal resistor, an ideal "
            "transformer, and no balun losses."
        ),
        Language.SPANISH: (
            "Las dimensiones iniciales siguen el T2FD ancho y largo de Cebik: "
            "aproximadamente 300/F(MHz) pies de longitud y 10/F(MHz) pies de "
            "separación. La terminación de 800 Ω y el transformador 16:1 "
            "siguen el diseño comercial B&W de 3-30 MHz. El resistor disipa "
            "una parte importante de la potencia aplicada; el modelo usa un "
            "resistor ideal, un transformador ideal y no incluye pérdidas del "
            "balun."
        ),
    },
    "t2fd.evidence": {
        Language.ENGLISH: (
            "Reference-backed starting dimensions (Cebik, W4RNL; Wikipedia "
            "and the B&W AC3-30 commercial design). No independent numerical "
            "reference is claimed for the ideal termination and transformer "
            "model."
        ),
        Language.SPANISH: (
            "Dimensiones iniciales con referencia (Cebik, W4RNL; Wikipedia y "
            "el diseño comercial B&W AC3-30). No se reclama una referencia "
            "numérica independiente para el modelo ideal de terminación y "
            "transformador."
        ),
    },
    "endfed.preset.endfed": {
        Language.ENGLISH: "End-fed half-wave (EFHW)",
        Language.SPANISH: "Media onda alimentada en el extremo (EFHW)",
    },
    "endfed.efhw_presets": {
        Language.ENGLISH: "EFHW band preset",
        Language.SPANISH: "Preset EFHW por banda",
    },
    "endfed.preset.sloper": {
        Language.ENGLISH: "Sloper",
        Language.SPANISH: "Sloper",
    },
    "endfed.preset.random_wire": {
        Language.ENGLISH: "Random wire",
        Language.SPANISH: "Hilo aleatorio",
    },
    "endfed.sloper_title": {
        Language.ENGLISH: "Sloper Generator",
        Language.SPANISH: "Generador de sloper",
    },
    "endfed.random_wire_title": {
        Language.ENGLISH: "Random Wire Generator",
        Language.SPANISH: "Generador de hilo aleatorio",
    },
    "endfed.sloper_hint": {
        Language.ENGLISH: (
            "A half-wave wire sloping from a high feed point to a lower far end. "
            "The 49:1 transformer and counterpoise are application starting "
            "points; tune the length, slope, and matching with the solver."
        ),
        Language.SPANISH: (
            "Un hilo de media onda inclinado desde un punto de alimentación alto "
            "hacia un extremo más bajo. El transformador 49:1 y el contrapeso son "
            "puntos de partida; sintonizá la longitud, la inclinación y la "
            "adaptación con el solver."
        ),
    },
    "endfed.random_wire_hint": {
        Language.ENGLISH: (
            "A non-resonant end-fed wire with a 9:1 transformer and counterpoise. "
            "The 17 m length, transformer, and counterpoise are application "
            "starting points; tune them for your band and installation."
        ),
        Language.SPANISH: (
            "Un hilo no resonante alimentado en el extremo con transformador 9:1 "
            "y contrapeso. La longitud de 17 m, el transformador y el contrapeso "
            "son puntos de partida; sintonizalos para tu banda e instalación."
        ),
    },
    "endfed.sloper_evidence": {
        Language.ENGLISH: (
            "Experimental preset: the geometry and matching are application "
            "starting points, with no independent numerical reference for this "
            "sloper."
        ),
        Language.SPANISH: (
            "Preset experimental: la geometría y la adaptación son puntos de "
            "partida, sin una referencia numérica independiente para este sloper."
        ),
    },
    "endfed.random_wire_evidence": {
        Language.ENGLISH: (
            "Experimental preset: the geometry and matching are application "
            "starting points, with no independent numerical reference for this "
            "random wire."
        ),
        Language.SPANISH: (
            "Preset experimental: la geometría y la adaptación son puntos de "
            "partida, sin una referencia numérica independiente para este hilo "
            "aleatorio."
        ),
    },
    "endfed.title": {
        Language.ENGLISH: "End-Fed Half-Wave (EFHW) Generator",
        Language.SPANISH: "Generador de media onda alimentada (EFHW)",
    },
    "endfed.feed_height": {
        Language.ENGLISH: "Feed height",
        Language.SPANISH: "Altura de alimentación",
    },
    "endfed.end_height": {
        Language.ENGLISH: "End height",
        Language.SPANISH: "Altura del extremo",
    },
    "endfed.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "endfed.geometry": {
        Language.ENGLISH: (
            "Feed {feed} {unit} · end {end} {unit} · counterpoise {counterpoise} · {ratio}:1"
        ),
        Language.SPANISH: (
            "Alimentación {feed} {unit} · extremo {end} {unit} · contrapeso "
            "{counterpoise} · {ratio}:1"
        ),
    },
    "endfed.transformer_ratio": {
        Language.ENGLISH: "Transformer ratio",
        Language.SPANISH: "Relación del transformador",
    },
    "endfed.counterpoise_enabled": {
        Language.ENGLISH: "Use counterpoise",
        Language.SPANISH: "Usar contrapeso",
    },
    "endfed.counterpoise_length": {
        Language.ENGLISH: "Counterpoise length (0 = none)",
        Language.SPANISH: "Longitud del contrapeso (0 = ninguno)",
    },
    "endfed.counterpoise_height": {
        Language.ENGLISH: "Counterpoise height",
        Language.SPANISH: "Altura del contrapeso",
    },
    "endfed.counterpoise_azimuth": {
        Language.ENGLISH: "Counterpoise azimuth",
        Language.SPANISH: "Azimut del contrapeso",
    },
    "endfed.hint": {
        Language.ENGLISH: (
            "The wire is fed at one end. The EFHW band buttons load the published "
            "ARRL 40/20/10 m lengths and a 49:1 transformer, plus a 0.05λ "
            "counterpoise starting point. The optional counterpoise is modeled as "
            "a drop plus a horizontal wire. The transformer ratio is an ideal "
            "post-processing step: 49:1 means the antenna-side impedance is "
            "divided by 49 for the reported impedance and SWR."
        ),
        Language.SPANISH: (
            "El hilo se alimenta en un extremo. Los botones EFHW cargan las "
            "longitudes publicadas de ARRL para 40/20/10 m y un transformador "
            "49:1, más un contrapeso inicial de 0,05λ. El contrapeso opcional se "
            "modela como una bajada más un tramo horizontal. La relación del "
            "transformador es un post-proceso ideal: 49:1 significa que la "
            "impedancia del lado de la antena se divide por 49 para la "
            "impedancia y la ROE informadas."
        ),
    },
    "endfed.evidence": {
        Language.ENGLISH: (
            "The EFHW preset uses the published ARRL 66/33/16 ft radiator "
            "lengths and 49:1 transformer ratio. The counterpoise, installation, "
            "and edited geometry remain starting points, not independently "
            "validated impedance predictions."
        ),
        Language.SPANISH: (
            "El preset EFHW usa las longitudes publicadas de ARRL de 66/33/16 ft "
            "y una relación de transformador 49:1. El contrapeso, la instalación "
            "y la geometría editada siguen siendo puntos de partida, no "
            "predicciones de impedancia validadas independientemente."
        ),
    },
    "fan.title": {
        Language.ENGLISH: "Fan Dipole Generator",
        Language.SPANISH: "Generador de dipolo ventilador",
    },
    "fan.length": {
        Language.ENGLISH: "Element length",
        Language.SPANISH: "Longitud del elemento",
    },
    "fan.included_angle": {
        Language.ENGLISH: "Included angle",
        Language.SPANISH: "Ángulo incluido",
    },
    "fan.apex_height": {
        Language.ENGLISH: "Apex height",
        Language.SPANISH: "Altura del vértice",
    },
    "fan.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "fan.add_element": {
        Language.ENGLISH: "Add pair",
        Language.SPANISH: "Agregar par",
    },
    "fan.remove_element": {
        Language.ENGLISH: "Remove pair",
        Language.SPANISH: "Quitar par",
    },
    "fan.geometry": {
        Language.ENGLISH: "{count} pairs · apex {height} {unit}",
        Language.SPANISH: "{count} pares · vértice {height} {unit}",
    },
    "fan.hint": {
        Language.ENGLISH: (
            "Each row is one center-fed dipole pair sharing the apex. "
            "The generated antenna is an editable first-class design."
        ),
        Language.SPANISH: (
            "Cada fila es un par de dipolos con alimentación central que comparte "
            "el vértice. La antena generada es un diseño editable de primera clase."
        ),
    },
    "fan.evidence": {
        Language.ENGLISH: (
            "Experimental generator: geometry is tested, but there is no "
            "independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueba la geometría, pero no hay una "
            "referencia numérica independiente para esta configuración."
        ),
    },
    "moxon.title": {
        Language.ENGLISH: "Moxon Generator",
        Language.SPANISH: "Generador Moxon",
    },
    "moxon.width": {
        Language.ENGLISH: "Element width",
        Language.SPANISH: "Ancho del elemento",
    },
    "moxon.depth": {
        Language.ENGLISH: "Element spacing",
        Language.SPANISH: "Separación entre elementos",
    },
    "moxon.reflector_tip": {
        Language.ENGLISH: "Reflector tip",
        Language.SPANISH: "Punta del reflector",
    },
    "moxon.driven_tip": {
        Language.ENGLISH: "Driven tip",
        Language.SPANISH: "Punta del elemento alimentado",
    },
    "moxon.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "moxon.geometry": {
        Language.ENGLISH: "Tip gap {gap} {unit}",
        Language.SPANISH: "Separación de puntas {gap} {unit}",
    },
    "moxon.reference_preset": {
        Language.ENGLISH: "Load 20 m wire reference preset",
        Language.SPANISH: "Cargar preset de referencia de 20 m",
    },
    "moxon.polarization_hint": {
        Language.ENGLISH: (
            "Vertical polarization puts the whole rectangle in a vertical "
            "plane. Height is the boom centerline and must clear the rectangle."
        ),
        Language.SPANISH: (
            "La polarización vertical ubica todo el rectángulo en un plano "
            "vertical. La altura es la línea central del boom y debe dejar "
            "libre el rectángulo."
        ),
    },
    "moxon.clearance_warning": {
        Language.ENGLISH: (
            "A vertical Moxon needs a boom center height greater than {height} "
            "{unit} so the rectangle stays above ground."
        ),
        Language.SPANISH: (
            "Un Moxon vertical necesita una altura de centro del boom mayor "
            "que {height} {unit} para que el rectángulo quede sobre el suelo."
        ),
    },
    "moxon.hint": {
        Language.ENGLISH: (
            "The generator creates a reflector and driven element with bent tips. "
            "Vertical polarization puts the whole rectangle in a vertical plane "
            "with a horizontal boom. The generated antenna is an editable "
            "first-class design."
        ),
        Language.SPANISH: (
            "El generador crea un reflector y un elemento alimentado con puntas "
            "dobladas. La polarización vertical ubica todo el rectángulo en un "
            "plano vertical con el boom horizontal. La antena generada es un "
            "diseño editable de primera clase."
        ),
    },
    "moxon.evidence": {
        Language.ENGLISH: (
            "The 20 m wire preset is reference-backed by a published model; "
            "edited geometry is experimental."
        ),
        Language.SPANISH: (
            "El preset de alambre de 20 m tiene referencia de un modelo publicado; "
            "la geometría editada es experimental."
        ),
    },
    "ocfd.title": {
        Language.ENGLISH: "Off-Center-Fed Dipole Generator",
        Language.SPANISH: "Generador de dipolo con alimentación descentrada",
    },
    "ocfd.feed_offset": {
        Language.ENGLISH: "Feed offset",
        Language.SPANISH: "Desplazamiento de alimentación",
    },
    "ocfd.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "ocfd.geometry": {
        Language.ENGLISH: "Feed at {offset} {unit} from the start · total {total} {unit}",
        Language.SPANISH: "Alimentación a {offset} {unit} del inicio · total {total} {unit}",
    },
    "ocfd.transformer_ratio": {
        Language.ENGLISH: "Transformer ratio",
        Language.SPANISH: "Relación del transformador",
    },
    "ocfd.transformer_hint": {
        Language.ENGLISH: (
            "Ideal feed transformer. 4.0 is the common OCFD 4:1 balun; "
            "set 1.0 to see the raw antenna impedance."
        ),
        Language.SPANISH: (
            "Transformador de alimentación ideal. 4.0 es el balún 4:1 habitual "
            "del OCFD; poné 1.0 para ver la impedancia cruda de la antena."
        ),
    },
    "ocfd.hint": {
        Language.ENGLISH: (
            "The generator creates one horizontal wire with an offset feed. "
            "The generated antenna is an editable custom-wire design."
        ),
        Language.SPANISH: (
            "El generador crea un hilo horizontal con alimentación descentrada. "
            "La antena generada es un diseño de hilos editable."
        ),
    },
    "ocfd.evidence": {
        Language.ENGLISH: (
            "Experimental generator: geometry and scaling are tested, but there "
            "is no independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueban geometría y escalado, pero no "
            "hay una referencia numérica independiente para esta configuración."
        ),
    },
    "vertical.title": {
        Language.ENGLISH: "Vertical Generator",
        Language.SPANISH: "Generador de vertical",
    },
    "vertical.height": {
        Language.ENGLISH: "Radiator height",
        Language.SPANISH: "Altura del radiador",
    },
    "vertical.base_height": {
        Language.ENGLISH: "Base height",
        Language.SPANISH: "Altura de la base",
    },
    "vertical.radial_system": {
        Language.ENGLISH: "Radial system",
        Language.SPANISH: "Sistema de radiales",
    },
    "vertical.radial_system_hint": {
        Language.ENGLISH: (
            "Starting presets only. They set the base/radial-plane height, "
            "radial count, and radial length; the numeric fields stay editable."
        ),
        Language.SPANISH: (
            "Solo presets de inicio. Ajustan la altura de base/plano de "
            "radiales, la cantidad y la longitud; los campos numéricos siguen "
            "siendo editables."
        ),
    },
    "radial_preset.custom": {
        Language.ENGLISH: "Custom / measured",
        Language.SPANISH: "Personalizado / medido",
    },
    "radial_preset.none": {
        Language.ENGLISH: "No radials",
        Language.SPANISH: "Sin radiales",
    },
    "radial_preset.ground": {
        Language.ENGLISH: "Ground radials (16 x 0.25λ)",
        Language.SPANISH: "Radiales de suelo (16 x 0,25λ)",
    },
    "radial_preset.elevated": {
        Language.ENGLISH: "Elevated radials (4 x 0.25λ)",
        Language.SPANISH: "Radiales elevados (4 x 0,25λ)",
    },
    "radial_preset.screen": {
        Language.ENGLISH: "Ground screen (32 x 0.10λ)",
        Language.SPANISH: "Pantalla de suelo (32 x 0,10λ)",
    },
    "vertical.radial_count": {
        Language.ENGLISH: "Radial count",
        Language.SPANISH: "Cantidad de radiales",
    },
    "vertical.radial_length": {
        Language.ENGLISH: "Radial length",
        Language.SPANISH: "Longitud de radiales",
    },
    "vertical.radial_angle": {
        Language.ENGLISH: "First radial angle",
        Language.SPANISH: "Ángulo del primer radial",
    },
    "vertical.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "vertical.geometry": {
        Language.ENGLISH: "Top height {top} {unit} · {count} radials",
        Language.SPANISH: "Altura superior {top} {unit} · {count} radiales",
    },
    "vertical.loading_coil": {
        Language.ENGLISH: "Loading coil",
        Language.SPANISH: "Bobina de carga",
    },
    "vertical.loading_coil_enabled": {
        Language.ENGLISH: "Use loading coil",
        Language.SPANISH: "Usar bobina de carga",
    },
    "vertical.loading_coil_offset": {
        Language.ENGLISH: "Coil height above base",
        Language.SPANISH: "Altura de la bobina sobre la base",
    },
    "vertical.loading_coil_inductance": {
        Language.ENGLISH: "Inductance",
        Language.SPANISH: "Inductancia",
    },
    "vertical.loading_coil_q": {
        Language.ENGLISH: "Coil Q",
        Language.SPANISH: "Q de la bobina",
    },
    "vertical.loading_coil_q_hint": {
        Language.ENGLISH: (
            "Q is derived from the coil reactance and series resistance. "
            "Enter 0 for an ideal lossless coil."
        ),
        Language.SPANISH: (
            "La Q se deriva de la reactancia de la bobina y la resistencia "
            "serie. Ingresá 0 para una bobina ideal sin pérdidas."
        ),
    },
    "vertical.loading_coil_resistance": {
        Language.ENGLISH: "Coil resistance",
        Language.SPANISH: "Resistencia de la bobina",
    },
    "vertical.top_hat": {
        Language.ENGLISH: "Capacitive top hat",
        Language.SPANISH: "Sombrero capacitivo",
    },
    "vertical.top_hat_enabled": {
        Language.ENGLISH: "Enable top hat",
        Language.SPANISH: "Habilitar sombrero capacitivo",
    },
    "vertical.top_hat_radius": {
        Language.ENGLISH: "Hat radius",
        Language.SPANISH: "Radio del sombrero",
    },
    "vertical.top_hat_wires": {
        Language.ENGLISH: "Hat wires",
        Language.SPANISH: "Hilos del sombrero",
    },
    "vertical.loading_coil_summary": {
        Language.ENGLISH: "Series {inductance} µH at {offset} {unit} · R {resistance} Ω",
        Language.SPANISH: "Serie {inductance} µH a {offset} {unit} · R {resistance} Ω",
    },
    "vertical.hint": {
        Language.ENGLISH: (
            "The radiator is fed at its base. Radials are wires in the radial "
            "plane; over finite ground use at least 0.25 m to avoid numerical "
            "instability close to the soil."
        ),
        Language.SPANISH: (
            "El radiador se alimenta en la base. Los radiales son hilos en el "
            "plano de radiales; sobre suelo finito usá al menos 0.25 m para evitar "
            "inestabilidad numérica cerca del suelo."
        ),
    },
    "vertical.evidence": {
        Language.ENGLISH: (
            "Experimental generator: geometry and radial topology are tested, "
            "but there is no independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueban geometría y topología de radiales, "
            "pero no hay una referencia numérica independiente para esta configuración."
        ),
    },
    "vertical.mobile_title": {
        Language.ENGLISH: "Loaded vertical / mobile whip generator",
        Language.SPANISH: "Generador de vertical cargada / whip móvil",
    },
    "vertical.mobile_hint": {
        Language.ENGLISH: (
            "A short vertical with a series loading coil. The mobile preset uses "
            "a small radial plane as a simplified counterpoise; it does not model "
            "a vehicle body. The coil values are application starting points: "
            "tune the inductance and position with the solver."
        ),
        Language.SPANISH: (
            "Una vertical corta con bobina de carga en serie. El preset móvil usa "
            "un plano de radiales pequeño como contrapeso simplificado; no modela "
            "la carrocería de un vehículo. Los valores de la bobina son puntos de "
            "partida: sintonizá la inductancia y la posición con el solver."
        ),
    },
    "vertical.mobile_evidence": {
        Language.ENGLISH: (
            "Starting dimensions: only the published 102 in / 14.1 MHz example is "
            "reference-backed. Coil Q, ground, and the installation are not "
            "modeled; other loaded verticals remain experimental."
        ),
        Language.SPANISH: (
            "Dimensiones de partida: solo el ejemplo publicado de 102 in / "
            "14.1 MHz tiene referencia. No se modelan la Q de la bobina, el suelo "
            "ni la instalación; otras verticales cargadas siguen siendo "
            "experimentales."
        ),
    },
    "vertical.mobile_example": {
        Language.ENGLISH: "Load 102 in example",
        Language.SPANISH: "Cargar ejemplo de 102 in",
    },
    "vertical.mobile_example_hint": {
        Language.ENGLISH: (
            "Sets 14.1 MHz, a 102 in whip, and a 4.511 µH base loading coil. "
            "Coil Q, ground, and the installation are not modeled."
        ),
        Language.SPANISH: (
            "Configura 14.1 MHz, un whip de 102 in y una bobina de carga de "
            "4.511 µH en la base. No se modelan la Q de la bobina, el suelo ni "
            "la instalación."
        ),
    },
    "inverted_v.apex_height": {
        Language.ENGLISH: "Apex height",
        Language.SPANISH: "Altura del vértice",
    },
    "inverted_v.leg_length": {
        Language.ENGLISH: "Leg length",
        Language.SPANISH: "Longitud de cada rama",
    },
    "inverted_v.included_angle": {
        Language.ENGLISH: "Included angle",
        Language.SPANISH: "Ángulo incluido",
    },
    "inverted_v.wire_radius": {
        Language.ENGLISH: "Wire radius (mm)",
        Language.SPANISH: "Radio del hilo (mm)",
    },
    "inverted_v.geometry": {
        Language.ENGLISH: "Horizontal span {span} {unit} · end height {end} {unit}",
        Language.SPANISH: "Ancho horizontal {span} {unit} · altura de puntas {end} {unit}",
    },
    "inverted_v.hint": {
        Language.ENGLISH: (
            "The generator creates two sloping wires with a center feed at the "
            "apex. The generated antenna is an editable custom-wire design."
        ),
        Language.SPANISH: (
            "El generador crea dos hilos inclinados con alimentación central en "
            "el vértice. La antena generada es un diseño de hilos editable."
        ),
    },
    "inverted_v.evidence": {
        Language.ENGLISH: (
            "Experimental generator: geometry and scaling are tested, but there "
            "is no independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueban geometría y escalado, pero no "
            "hay una referencia numérica independiente para esta configuración."
        ),
    },
    "yagi.element": {
        Language.ENGLISH: "Element",
        Language.SPANISH: "Elemento",
    },
    "yagi.position": {
        Language.ENGLISH: "Boom position",
        Language.SPANISH: "Posición en el boom",
    },
    "yagi.length": {
        Language.ENGLISH: "Element length",
        Language.SPANISH: "Longitud del elemento",
    },
    "yagi.radius": {
        Language.ENGLISH: "Element radius",
        Language.SPANISH: "Radio del elemento",
    },
    "yagi.add_element": {
        Language.ENGLISH: "Add element",
        Language.SPANISH: "Agregar elemento",
    },
    "yagi.remove_element": {
        Language.ENGLISH: "Remove element",
        Language.SPANISH: "Quitar elemento",
    },
    "yagi.nbs_preset": {
        Language.ENGLISH: "Load NBS 5-element preset",
        Language.SPANISH: "Cargar preset NBS de 5 elementos",
    },
    "yagi.driven": {
        Language.ENGLISH: "Driven element",
        Language.SPANISH: "Elemento alimentado",
    },
    "yagi.frequency_mismatch": {
        Language.ENGLISH: "Element dimensions do not match the current frequency. Change the frequency from a known design or use Estimate Dimensions to rebuild the Yagi.",
        Language.SPANISH: "Las dimensiones de los elementos no coinciden con la frecuencia actual. Cambiá la frecuencia desde un diseño conocido o usá Estimar dimensiones para regenerar la Yagi.",
    },
    "yagi.geometry": {
        Language.ENGLISH: "{count} elements · boom {boom} {unit}",
        Language.SPANISH: "{count} elementos · boom {boom} {unit}",
    },
    "yagi.folded_driven": {
        Language.ENGLISH: "Folded driven element",
        Language.SPANISH: "Elemento alimentado plegado",
    },
    "yagi.match_type": {
        Language.ENGLISH: "Feed match",
        Language.SPANISH: "Adaptación de alimentación",
    },
    "yagi.match_none": {
        Language.ENGLISH: "None",
        Language.SPANISH: "Ninguna",
    },
    "yagi.match_beta_hairpin": {
        Language.ENGLISH: "Beta / hairpin",
        Language.SPANISH: "Beta / horquilla",
    },
    "yagi.match_length": {
        Language.ENGLISH: "Hairpin length",
        Language.SPANISH: "Longitud de horquilla",
    },
    "yagi.match_spacing": {
        Language.ENGLISH: "Hairpin spacing",
        Language.SPANISH: "Separación de horquilla",
    },
    "yagi.match_geometry": {
        Language.ENGLISH: "beta/hairpin · length {length} {unit} · spacing {spacing} {unit}",
        Language.SPANISH: "beta/horquilla · longitud {length} {unit} · separación {spacing} {unit}",
    },
    "yagi.match_clearance_warning": {
        Language.ENGLISH: (
            "Hairpin length and spacing must be greater than twice the driven-element "
            "radius (minimum {minimum} {unit}); otherwise the conductors overlap."
        ),
        Language.SPANISH: (
            "La longitud y la separación de la horquilla deben superar el doble del "
            "radio del elemento alimentado (mínimo {minimum} {unit}); de lo contrario "
            "los conductores se superponen."
        ),
    },
    "yagi.fold_spacing_clearance": {
        Language.ENGLISH: (
            "Fold spacing must be greater than twice the driven-element radius "
            "(minimum {minimum} {unit}); otherwise the conductors overlap."
        ),
        Language.SPANISH: (
            "La separación del plegado debe superar el doble del radio del elemento "
            "alimentado (mínimo {minimum} {unit}); de lo contrario los conductores se "
            "superponen."
        ),
    },
    "yagi.match_hint": {
        Language.ENGLISH: (
            "A beta/hairpin is a shorted stub across the driven-element gap. It "
            "changes the feed impedance without adding a lumped matching network."
        ),
        Language.SPANISH: (
            "Una beta/horquilla es un stub cortocircuitado sobre el gap del "
            "elemento alimentado. Cambia la impedancia de alimentación sin agregar "
            "una red de adaptación concentrada."
        ),
    },
    "yagi.gamma_note": {
        Language.ENGLISH: (
            "Gamma match: not modeled because NEC-2 close-spaced gamma assemblies "
            "are unreliable. Use the Matching Network dialog for an equivalent."
        ),
        Language.SPANISH: (
            "Gamma match: no modelado porque los ensambles gamma de NEC-2 con "
            "conductores muy cercanos no son confiables. Usá el diálogo de red de "
            "adaptación para un equivalente."
        ),
    },
    "yagi.fold_spacing": {
        Language.ENGLISH: "Fold spacing",
        Language.SPANISH: "Separación del plegado",
    },
    "yagi.folded_geometry": {
        Language.ENGLISH: "folded driven · spacing {spacing} {unit}",
        Language.SPANISH: "alimentado plegado · separación {spacing} {unit}",
    },
    "yagi.folded_hint": {
        Language.ENGLISH: (
            "Adds a second driven conductor and two end connectors. The driven "
            "element length stays the same; spacing changes the feed impedance "
            "and matching."
        ),
        Language.SPANISH: (
            "Agrega un segundo conductor alimentado y dos conectores de extremo. "
            "La longitud del elemento alimentado no cambia; la separación cambia "
            "la impedancia de alimentación y la adaptación."
        ),
    },
    "yagi.polarization_hint": {
        Language.ENGLISH: (
            "Vertical polarization keeps the boom horizontal and rotates the "
            "elements around it. Height is the boom centerline."
        ),
        Language.SPANISH: (
            "La polarización vertical mantiene el boom horizontal y gira los "
            "elementos alrededor de él. La altura es la línea central del boom."
        ),
    },
    "yagi.clearance_warning": {
        Language.ENGLISH: (
            "Vertical elements need a boom center height greater than {height} "
            "{unit} so the longest element stays above ground."
        ),
        Language.SPANISH: (
            "Los elementos verticales necesitan una altura de centro del boom "
            "mayor que {height} {unit} para que el elemento más largo quede "
            "sobre el suelo."
        ),
    },
    "yagi.hint": {
        Language.ENGLISH: (
            "Positions and lengths are editable. Polarization rotates the "
            "elements around a horizontal boom. The generated antenna is an "
            "editable custom-wire design."
        ),
        Language.SPANISH: (
            "Las posiciones y longitudes son editables. La polarización gira "
            "los elementos alrededor de un boom horizontal. La antena generada "
            "es un diseño de hilos personalizado editable."
        ),
    },
    "element_optimize.loop_title": {
        Language.ENGLISH: "Optimize Loop Elements",
        Language.SPANISH: "Optimizar elementos del lazo",
    },
    "element_optimize.vertical_title": {
        Language.ENGLISH: "Optimize Vertical Elements",
        Language.SPANISH: "Optimizar elementos de la vertical",
    },
    "element_optimize.inverted_v_title": {
        Language.ENGLISH: "Optimize Inverted-V Elements",
        Language.SPANISH: "Optimizar elementos de la V invertida",
    },
    "element_optimize.ringo_title": {
        Language.ENGLISH: "Optimize Ringo Elements",
        Language.SPANISH: "Optimizar elementos del Ringo",
    },
    "element_optimize.zs6bkw_title": {
        Language.ENGLISH: "Optimize ZS6BKW",
        Language.SPANISH: "Optimizar ZS6BKW",
    },
    "element_optimize.zs6bkw_hint": {
        Language.ENGLISH: (
            "Vary the dipole wire length and matching-line length together. "
            "The line impedance, velocity factor, and installation stay fixed. "
            "Verify the chosen match with a full band sweep."
        ),
        Language.SPANISH: (
            "Variá juntas la longitud del hilo y la de la línea de adaptación. "
            "La impedancia de línea, el factor de velocidad y la instalación "
            "quedan fijos. Verificá la adaptación elegida con un barrido "
            "completo de banda."
        ),
    },
    "element_optimize.yagi_title": {
        Language.ENGLISH: "Optimize Yagi Elements",
        Language.SPANISH: "Optimizar elementos del Yagi",
    },
    "element_optimize.fan_title": {
        Language.ENGLISH: "Optimize Fan Dipole Elements",
        Language.SPANISH: "Optimizar elementos del dipolo abanico",
    },
    "element_optimize.moxon_title": {
        Language.ENGLISH: "Optimize Moxon Dimensions",
        Language.SPANISH: "Optimizar dimensiones del Moxon",
    },
    "element_optimize.objective.target_impedance": {
        Language.ENGLISH: "Target impedance",
        Language.SPANISH: "Impedancia objetivo",
    },
    "element_optimize.objective.max_gain": {
        Language.ENGLISH: "Maximum gain",
        Language.SPANISH: "Ganancia máxima",
    },
    "element_optimize.objective.max_front_to_back": {
        Language.ENGLISH: "Maximum front-to-back",
        Language.SPANISH: "Máxima relación frente/espalda",
    },
    "element_optimize.objective.multi_objective": {
        Language.ENGLISH: "Multi-objective",
        Language.SPANISH: "Multiobjetivo",
    },
    "element_optimize.current_value": {
        Language.ENGLISH: "Current value",
        Language.SPANISH: "Valor actual",
    },
    "element_optimize.band": {
        Language.ENGLISH: "Band",
        Language.SPANISH: "Banda",
    },
    "element_optimize.band_custom": {
        Language.ENGLISH: "Custom frequency",
        Language.SPANISH: "Frecuencia personalizada",
    },
    "element_optimize.frequency_hint": {
        Language.ENGLISH: (
            "Selecting a band sets the target frequency; editing the frequency "
            "switches the selector to Custom."
        ),
        Language.SPANISH: (
            "Elegir una banda ajusta la frecuencia objetivo; editar la frecuencia "
            "cambia el selector a Personalizada."
        ),
    },
    "element_optimize.band_mismatch": {
        Language.ENGLISH: (
            "Selected elements are for {selected}, but the target frequency is in {target}."
        ),
        Language.SPANISH: (
            "Los elementos seleccionados son de {selected}, pero la frecuencia "
            "objetivo está en {target}."
        ),
    },
    "element_optimize.pareto": {
        Language.ENGLISH: "Pareto",
        Language.SPANISH: "Pareto",
    },
    "element_optimize.weight_gain": {
        Language.ENGLISH: "Gain weight",
        Language.SPANISH: "Peso de ganancia",
    },
    "element_optimize.weight_fb": {
        Language.ENGLISH: "F/B weight",
        Language.SPANISH: "Peso de F/B",
    },
    "element_optimize.weight_swr": {
        Language.ENGLISH: "SWR penalty weight",
        Language.SPANISH: "Peso de penalización de ROE",
    },
    "element_optimize.weight_efficiency": {
        Language.ENGLISH: "Efficiency weight",
        Language.SPANISH: "Peso de eficiencia",
    },
    "element_optimize.hint": {
        Language.ENGLISH: "Selected dimensions change together. Select a table row to apply a different candidate or Pareto compromise. Verify the applied design with a full simulation.",
        Language.SPANISH: "Las dimensiones seleccionadas cambian juntas. Seleccioná una fila de la tabla para aplicar otro candidato o compromiso de Pareto. Verificá el diseño aplicado con una simulación completa.",
    },
    "element_optimize.fan_hint": {
        Language.ENGLISH: (
            "All fan elements remain in the antenna. The Optimize column only "
            "selects which lengths are varied; the short element's SWR includes "
            "coupling from the other elements. To evaluate an element alone, "
            "remove the other elements in the editor."
        ),
        Language.SPANISH: (
            "Todos los elementos del fan permanecen en la antena. La columna "
            "Optimizar solo elige qué longitudes se varían; el ROE del elemento "
            "corto incluye el acoplamiento de los demás. Para evaluar un elemento "
            "solo, quitá los otros en el editor."
        ),
    },
    "element_optimize.yagi_hint": {
        Language.ENGLISH: "The element count is fixed; only the selected element lengths and boom gaps are optimized. The first element position stays fixed, gaps keep a 0.1 m minimum, and radii stay fixed. To change the number of elements, edit the Yagi before optimizing.",
        Language.SPANISH: "La cantidad de elementos queda fija; solo se optimizan las longitudes y separaciones seleccionadas. La posición del primer elemento queda fija, las separaciones mantienen un mínimo de 0,1 m y los radios no cambian. Para cambiar la cantidad de elementos, editá la Yagi antes de optimizar.",
    },
    "element_optimize.loop_hint": {
        Language.ENGLISH: "Full-wave loops typically show 100-150 Ω at resonance, so the target resistance defaults to 100 Ω. Use a 2:1 balun or Matching Network for a 50 Ω system; the loop shape and side count are preserved.",
        Language.SPANISH: "Los lazos de onda completa suelen presentar 100-150 Ω en resonancia, por eso la resistencia objetivo parte de 100 Ω. Usá un balun 2:1 o una red de adaptación para un sistema de 50 Ω; la forma y la cantidad de lados se conservan.",
    },
    "element_optimize.selected_summary": {
        Language.ENGLISH: "Selected candidate: {objective}",
        Language.SPANISH: "Candidato seleccionado: {objective}",
    },
    "element_optimize.run": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "element_optimize.apply": {
        Language.ENGLISH: "Apply dimensions",
        Language.SPANISH: "Aplicar dimensiones",
    },
    "element_optimize.no_variables": {
        Language.ENGLISH: "Select at least one dimension to optimize.",
        Language.SPANISH: "Seleccioná al menos una dimensión para optimizar.",
    },
    "element_optimize.running": {
        Language.ENGLISH: "Running optimization...",
        Language.SPANISH: "Ejecutando optimización...",
    },
    "element_optimize.error": {
        Language.ENGLISH: "Optimization failed: {message}",
        Language.SPANISH: "Falló la optimización: {message}",
    },
    "element_optimize.no_best": {
        Language.ENGLISH: "No valid dimensions were found.",
        Language.SPANISH: "No se encontraron dimensiones válidas.",
    },
    "element_optimize.summary": {
        Language.ENGLISH: "Best: {dimensions} · {objective}",
        Language.SPANISH: "Mejor: {dimensions} · {objective}",
    },
    "element_optimize.close": {
        Language.ENGLISH: "Cancel the running optimization before closing.",
        Language.SPANISH: "Cancelá la optimización en curso antes de cerrar.",
    },
    "moxon_optimize.title": {
        Language.ENGLISH: "Optimize Moxon Dimensions",
        Language.SPANISH: "Optimizar dimensiones del Moxon",
    },
    "moxon_optimize.variable": {
        Language.ENGLISH: "Dimension",
        Language.SPANISH: "Dimensión",
    },
    "moxon_optimize.target_impedance_objective": {
        Language.ENGLISH: "Target impedance",
        Language.SPANISH: "Impedancia objetivo",
    },
    "moxon_optimize.max_gain_objective": {
        Language.ENGLISH: "Maximum gain",
        Language.SPANISH: "Ganancia máxima",
    },
    "moxon_optimize.max_front_to_back_objective": {
        Language.ENGLISH: "Maximum front-to-back",
        Language.SPANISH: "Máxima relación frente/espalda",
    },
    "moxon_optimize.hint": {
        Language.ENGLISH: "Selected Moxon dimensions change together. Invalid tip/spacing combinations are rejected; verify the applied design with a full simulation.",
        Language.SPANISH: "Las dimensiones seleccionadas del Moxon cambian juntas. Las combinaciones inválidas de puntas/separación se rechazan; verificá el diseño aplicado con una simulación completa.",
    },
    "moxon_optimize.run": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "moxon_optimize.apply": {
        Language.ENGLISH: "Apply dimensions",
        Language.SPANISH: "Aplicar dimensiones",
    },
    "moxon_optimize.no_variables": {
        Language.ENGLISH: "Select at least one dimension to optimize.",
        Language.SPANISH: "Seleccioná al menos una dimensión para optimizar.",
    },
    "moxon_optimize.running": {
        Language.ENGLISH: "Running Moxon optimization...",
        Language.SPANISH: "Ejecutando optimización del Moxon...",
    },
    "moxon_optimize.error": {
        Language.ENGLISH: "Moxon optimization failed: {message}",
        Language.SPANISH: "Falló la optimización del Moxon: {message}",
    },
    "moxon_optimize.no_best": {
        Language.ENGLISH: "No valid Moxon dimensions were found.",
        Language.SPANISH: "No se encontraron dimensiones válidas del Moxon.",
    },
    "moxon_optimize.summary": {
        Language.ENGLISH: "Best: {dimensions} · {objective}",
        Language.SPANISH: "Mejor: {dimensions} · {objective}",
    },
    "moxon_optimize.close": {
        Language.ENGLISH: "Cancel the running optimization before closing.",
        Language.SPANISH: "Cancelá la optimización en curso antes de cerrar.",
    },
    "fan_optimize.title": {
        Language.ENGLISH: "Optimize Fan Dipole Elements",
        Language.SPANISH: "Optimizar elementos del dipolo abanico",
    },
    "fan_optimize.hint": {
        Language.ENGLISH: "Only selected element lengths change. The target is evaluated at one frequency; verify the other bands after applying.",
        Language.SPANISH: "Solo cambian las longitudes seleccionadas. El objetivo se evalúa en una frecuencia; verificá las otras bandas después de aplicar.",
    },
    "fan_optimize.run": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "fan_optimize.apply": {
        Language.ENGLISH: "Apply element lengths",
        Language.SPANISH: "Aplicar longitudes",
    },
    "fan_optimize.no_elements": {
        Language.ENGLISH: "Select at least one element to optimize.",
        Language.SPANISH: "Seleccioná al menos un elemento para optimizar.",
    },
    "fan_optimize.running": {
        Language.ENGLISH: "Running fan-dipole optimization...",
        Language.SPANISH: "Ejecutando optimización del dipolo abanico...",
    },
    "fan_optimize.error": {
        Language.ENGLISH: "Fan-dipole optimization failed: {message}",
        Language.SPANISH: "Falló la optimización del dipolo abanico: {message}",
    },
    "fan_optimize.no_best": {
        Language.ENGLISH: "No valid element lengths were found.",
        Language.SPANISH: "No se encontraron longitudes válidas.",
    },
    "fan_optimize.summary": {
        Language.ENGLISH: "Best: {lengths} · impedance error {error} Ω",
        Language.SPANISH: "Mejor: {lengths} · error de impedancia {error} Ω",
    },
    "fan_optimize.close": {
        Language.ENGLISH: "Cancel the running optimization before closing.",
        Language.SPANISH: "Cancelá la optimización en curso antes de cerrar.",
    },
    "yagi_optimize.title": {
        Language.ENGLISH: "Optimize Yagi Elements",
        Language.SPANISH: "Optimizar elementos del Yagi",
    },
    "yagi_optimize.front_to_back": {
        Language.ENGLISH: "F/B (dB)",
        Language.SPANISH: "F/B (dB)",
    },
    "yagi_optimize.objective_value": {
        Language.ENGLISH: "Objective",
        Language.SPANISH: "Objetivo",
    },
    "yagi_optimize.target_impedance_objective": {
        Language.ENGLISH: "Target impedance",
        Language.SPANISH: "Impedancia objetivo",
    },
    "yagi_optimize.max_gain_objective": {
        Language.ENGLISH: "Maximum gain",
        Language.SPANISH: "Ganancia máxima",
    },
    "yagi_optimize.max_front_to_back_objective": {
        Language.ENGLISH: "Maximum front-to-back",
        Language.SPANISH: "Máxima relación frente/espalda",
    },
    "yagi_optimize.use": {
        Language.ENGLISH: "Optimize",
        Language.SPANISH: "Optimizar",
    },
    "yagi_optimize.current": {
        Language.ENGLISH: "Current length",
        Language.SPANISH: "Longitud actual",
    },
    "yagi_optimize.current_length": {
        Language.ENGLISH: "Current length",
        Language.SPANISH: "Longitud actual",
    },
    "yagi_optimize.current_gap": {
        Language.ENGLISH: "Current gap",
        Language.SPANISH: "Separación actual",
    },
    "yagi_optimize.opt_length": {
        Language.ENGLISH: "Opt. length",
        Language.SPANISH: "Long. opt.",
    },
    "yagi_optimize.opt_gap": {
        Language.ENGLISH: "Opt. gap",
        Language.SPANISH: "Sep. opt.",
    },
    "yagi_optimize.length_range": {
        Language.ENGLISH: "Length range",
        Language.SPANISH: "Rango longitud",
    },
    "yagi_optimize.gap_range": {
        Language.ENGLISH: "Gap range",
        Language.SPANISH: "Rango separación",
    },
    "yagi_optimize.min_gap": {
        Language.ENGLISH: "Minimum gap",
        Language.SPANISH: "Separación mínima",
    },
    "yagi_optimize.minimum": {
        Language.ENGLISH: "Minimum",
        Language.SPANISH: "Mínimo",
    },
    "yagi_optimize.maximum": {
        Language.ENGLISH: "Maximum",
        Language.SPANISH: "Máximo",
    },
    "yagi_optimize.bound": {
        Language.ENGLISH: "Bound around current length",
        Language.SPANISH: "Margen alrededor de la longitud actual",
    },
    "yagi_optimize.samples": {
        Language.ENGLISH: "Samples per variable",
        Language.SPANISH: "Muestras por variable",
    },
    "yagi_optimize.passes": {
        Language.ENGLISH: "Refinement passes",
        Language.SPANISH: "Pasadas de refinamiento",
    },
    "yagi_optimize.run": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "yagi_optimize.apply": {
        Language.ENGLISH: "Apply element lengths",
        Language.SPANISH: "Aplicar longitudes",
    },
    "yagi_optimize.hint": {
        Language.ENGLISH: "Selected lengths and gaps change; the first element stays fixed and element order is preserved. Radii stay fixed.",
        Language.SPANISH: "Cambian las longitudes y separaciones seleccionadas; el primer elemento queda fijo y se conserva el orden. Los radios quedan fijos.",
    },
    "yagi_optimize.no_elements": {
        Language.ENGLISH: "Select at least one element to optimize.",
        Language.SPANISH: "Seleccioná al menos un elemento para optimizar.",
    },
    "yagi_optimize.running": {
        Language.ENGLISH: "Running Yagi optimization...",
        Language.SPANISH: "Ejecutando optimización del Yagi...",
    },
    "yagi_optimize.error": {
        Language.ENGLISH: "Yagi optimization failed: {message}",
        Language.SPANISH: "Falló la optimización del Yagi: {message}",
    },
    "yagi_optimize.no_best": {
        Language.ENGLISH: "No valid element lengths were found.",
        Language.SPANISH: "No se encontraron longitudes válidas.",
    },
    "yagi_optimize.summary": {
        Language.ENGLISH: "Best: {lengths} · impedance error {error} Ω",
        Language.SPANISH: "Mejor: {lengths} · error de impedancia {error} Ω",
    },
    "yagi_optimize.close": {
        Language.ENGLISH: "Cancel the running optimization before closing.",
        Language.SPANISH: "Cancelá la optimización en curso antes de cerrar.",
    },
    "yagi.evidence": {
        Language.ENGLISH: (
            "NBS TN-688 preset: 5 elements, 0.8 wavelength, 9.2 dBd reference "
            "gain. Modified geometries are experimental and have no external "
            "reference. The folded driven element changes feed impedance and "
            "has no independent impedance reference."
        ),
        Language.SPANISH: (
            "Preset NBS TN-688: 5 elementos, 0.8 longitud de onda, ganancia de "
            "referencia 9.2 dBd. Las geometrías modificadas son experimentales y "
            "no tienen referencia externa. El elemento alimentado plegado cambia "
            "la impedancia de alimentación y no tiene referencia independiente "
            "de impedancia."
        ),
    },
    "custom.metric_hint": {
        Language.ENGLISH: "Coordinates use the application length unit; wire radius is in mm.",
        Language.SPANISH: "Las coordenadas usan la unidad de longitud de la aplicación; el radio está en mm.",
    },
    "custom.id": {Language.ENGLISH: "ID", Language.SPANISH: "ID"},
    "custom.start_x": {Language.ENGLISH: "Start X", Language.SPANISH: "Inicio X"},
    "custom.start_y": {Language.ENGLISH: "Start Y", Language.SPANISH: "Inicio Y"},
    "custom.start_z": {Language.ENGLISH: "Start Z", Language.SPANISH: "Inicio Z"},
    "custom.end_x": {Language.ENGLISH: "End X", Language.SPANISH: "Fin X"},
    "custom.end_y": {Language.ENGLISH: "End Y", Language.SPANISH: "Fin Y"},
    "custom.end_z": {Language.ENGLISH: "End Z", Language.SPANISH: "Fin Z"},
    "custom.radius": {
        Language.ENGLISH: "Radius ({unit})",
        Language.SPANISH: "Radio ({unit})",
    },
    "custom.add_wire": {
        Language.ENGLISH: "Add wire",
        Language.SPANISH: "Agregar hilo",
    },
    "custom.remove_wire": {
        Language.ENGLISH: "Remove wires",
        Language.SPANISH: "Quitar hilos",
    },
    "custom.radials_title": {
        Language.ENGLISH: "Ground radials (experimental)",
        Language.SPANISH: "Radiales de suelo (experimental)",
    },
    "custom.radial_count": {
        Language.ENGLISH: "Radials",
        Language.SPANISH: "Radiales",
    },
    "custom.radial_length": {
        Language.ENGLISH: "Radial length",
        Language.SPANISH: "Longitud del radial",
    },
    "custom.radial_angle": {
        Language.ENGLISH: "Start angle",
        Language.SPANISH: "Ángulo inicial",
    },
    "custom.add_radials": {
        Language.ENGLISH: "Add radials",
        Language.SPANISH: "Agregar radiales",
    },
    "custom.radials_hint": {
        Language.ENGLISH: "Adds wires from the origin (0,0,0) on the ground plane. Edit coordinates after adding.",
        Language.SPANISH: "Agrega hilos desde el origen (0,0,0) sobre el plano de suelo. Editá las coordenadas después.",
    },
    "custom.feed_wire": {
        Language.ENGLISH: "Feed wire",
        Language.SPANISH: "Hilo de alimentación",
    },
    "custom.feed_offset": {
        Language.ENGLISH: "Feed offset",
        Language.SPANISH: "Posición de alimentación",
    },
    "action.import_nec": {
        Language.ENGLISH: "Import NEC Deck...",
        Language.SPANISH: "Importar archivo NEC...",
    },
    "action.import_vna": {
        Language.ENGLISH: "Import VNA CSV...",
        Language.SPANISH: "Importar CSV de VNA...",
    },
    "dialog.vna_title": {
        Language.ENGLISH: "Import VNA CSV",
        Language.SPANISH: "Importar CSV de VNA",
    },
    "dialog.vna_filter": {
        Language.ENGLISH: "CSV files (*.csv *.txt);;All files (*)",
        Language.SPANISH: "Archivos CSV (*.csv *.txt);;Todos los archivos (*)",
    },
    "dialog.vna_warnings": {
        Language.ENGLISH: "Imported with {count} warning(s):\n{details}",
        Language.SPANISH: "Importado con {count} advertencia(s):\n{details}",
    },
    "error.import_vna": {
        Language.ENGLISH: "Could not import VNA CSV: {message}",
        Language.SPANISH: "No se pudo importar el CSV de VNA: {message}",
    },
    "error.measurement": {
        Language.ENGLISH: "Could not update the measurement: {message}",
        Language.SPANISH: "No se pudo actualizar la medición: {message}",
    },
    "action.import_mmana": {
        Language.ENGLISH: "Import MMANA File...",
        Language.SPANISH: "Importar archivo MMANA...",
    },
    "action.edit_custom": {
        Language.ENGLISH: "Edit Custom Wires...",
        Language.SPANISH: "Editar hilos personalizados...",
    },
    "action.edit_generator": {
        Language.ENGLISH: "Edit Generator...",
        Language.SPANISH: "Editar generador...",
    },
    "action.change_template": {
        Language.ENGLISH: "Change Template...",
        Language.SPANISH: "Cambiar plantilla...",
    },
    "dialog.change_template_title": {
        Language.ENGLISH: "Change Template",
        Language.SPANISH: "Cambiar plantilla",
    },
    "dialog.change_template_message": {
        Language.ENGLISH: "Replace the current design with the selected template?",
        Language.SPANISH: "¿Reemplazar el diseño actual por la plantilla seleccionada?",
    },
    "action.convert_custom": {
        Language.ENGLISH: "Convert to Custom Wires...",
        Language.SPANISH: "Convertir a hilos personalizados...",
    },
    "custom.panel_title": {
        Language.ENGLISH: "Custom wires",
        Language.SPANISH: "Hilos personalizados",
    },
    "custom.summary": {
        Language.ENGLISH: "{count} wires · {length} total conductor",
        Language.SPANISH: "{count} hilos · {length} de conductor total",
    },
    "transmission_lines.title": {
        Language.ENGLISH: "Transmission lines",
        Language.SPANISH: "Líneas de transmisión",
    },
    "transmission_lines.start_wire": {
        Language.ENGLISH: "Start wire",
        Language.SPANISH: "Hilo inicial",
    },
    "transmission_lines.start_offset": {
        Language.ENGLISH: "Start offset",
        Language.SPANISH: "Desplazamiento inicial",
    },
    "transmission_lines.end_wire": {
        Language.ENGLISH: "End wire",
        Language.SPANISH: "Hilo final",
    },
    "transmission_lines.end_offset": {
        Language.ENGLISH: "End offset",
        Language.SPANISH: "Desplazamiento final",
    },
    "transmission_lines.z0": {
        Language.ENGLISH: "Characteristic impedance",
        Language.SPANISH: "Impedancia característica",
    },
    "transmission_lines.length": {
        Language.ENGLISH: "Physical length",
        Language.SPANISH: "Longitud física",
    },
    "transmission_lines.velocity_factor": {
        Language.ENGLISH: "Velocity factor",
        Language.SPANISH: "Factor de velocidad",
    },
    "transmission_lines.use_distance": {
        Language.ENGLISH: "Use straight-line distance",
        Language.SPANISH: "Usar distancia en línea recta",
    },
    "transmission_lines.add": {
        Language.ENGLISH: "Add line",
        Language.SPANISH: "Agregar línea",
    },
    "transmission_lines.remove": {
        Language.ENGLISH: "Remove line",
        Language.SPANISH: "Quitar línea",
    },
    "transmission_lines.hint": {
        Language.ENGLISH: (
            "A transmission line is a mathematical two-port between two wire "
            "points. It does not radiate. NEC-2 models it as lossless; use the "
            "feed-line post-processing model when line loss matters."
        ),
        Language.SPANISH: (
            "Una línea de transmisión es un dos-puertos matemático entre dos "
            "puntos de hilo. No irradia. NEC-2 la modela sin pérdidas; usá el "
            "modelo de línea de alimentación cuando importen las pérdidas."
        ),
    },
    "loads.title": {
        Language.ENGLISH: "Series Loads",
        Language.SPANISH: "Cargas en serie",
    },
    "loads.protected_message": {
        Language.ENGLISH: (
            "This load is managed by the antenna template. Change or disable it "
            "in the design panel."
        ),
        Language.SPANISH: (
            "Esta carga es administrada por la plantilla de antena. Cambiala o "
            "desactivala en el panel de diseño."
        ),
    },
    "loads.add": {Language.ENGLISH: "Add", Language.SPANISH: "Agregar"},
    "loads.remove": {Language.ENGLISH: "Remove", Language.SPANISH: "Quitar"},
    "loads.kind": {Language.ENGLISH: "Type", Language.SPANISH: "Tipo"},
    "loads.series": {Language.ENGLISH: "Series", Language.SPANISH: "Serie"},
    "loads.parallel": {Language.ENGLISH: "Parallel", Language.SPANISH: "Paralelo"},
    "loads.wire": {Language.ENGLISH: "Wire", Language.SPANISH: "Hilo"},
    "loads.offset": {
        Language.ENGLISH: "Position",
        Language.SPANISH: "Posición",
    },
    "loads.resistance": {
        Language.ENGLISH: "Resistance (Ω)",
        Language.SPANISH: "Resistencia (Ω)",
    },
    "loads.inductance": {
        Language.ENGLISH: "Inductance (µH)",
        Language.SPANISH: "Inductancia (µH)",
    },
    "loads.capacitance": {
        Language.ENGLISH: "Capacitance (pF)",
        Language.SPANISH: "Capacitancia (pF)",
    },
    "loads.trap_frequency": {
        Language.ENGLISH: "Trap frequency (MHz)",
        Language.SPANISH: "Frecuencia de trampa (MHz)",
    },
    "loads.add_trap": {
        Language.ENGLISH: "Add parallel trap",
        Language.SPANISH: "Agregar trampa paralelo",
    },
    "loads.trap_requires_l": {
        Language.ENGLISH: "Enter a positive inductance to calculate the trap capacitance.",
        Language.SPANISH: "Ingresá una inductancia positiva para calcular la capacidad de la trampa.",
    },
    "action.transmission_lines": {
        Language.ENGLISH: "Transmission Lines...",
        Language.SPANISH: "Líneas de transmisión...",
    },
    "history.transmission_lines": {
        Language.ENGLISH: "Edit transmission lines",
        Language.SPANISH: "Editar líneas de transmisión",
    },
    "action.loads": {
        Language.ENGLISH: "Edit Series Loads...",
        Language.SPANISH: "Editar cargas en serie...",
    },
    "optimize.title": {
        Language.ENGLISH: "Optimize Antenna Dimension",
        Language.SPANISH: "Optimizar dimensión de antena",
    },
    "optimize.min_length": {
        Language.ENGLISH: "Minimum dimension",
        Language.SPANISH: "Dimensión mínima",
    },
    "optimize.max_length": {
        Language.ENGLISH: "Maximum dimension",
        Language.SPANISH: "Dimensión máxima",
    },
    "optimize.objective": {
        Language.ENGLISH: "Objective",
        Language.SPANISH: "Objetivo",
    },
    "optimize.reactance_objective": {
        Language.ENGLISH: "Target reactance",
        Language.SPANISH: "Reactancia objetivo",
    },
    "optimize.target_impedance_objective": {
        Language.ENGLISH: "Target impedance",
        Language.SPANISH: "Impedancia objetivo",
    },
    "optimize.min_swr_objective": {
        Language.ENGLISH: "Minimum SWR",
        Language.SPANISH: "SWR mínimo",
    },
    "optimize.max_bandwidth_objective": {
        Language.ENGLISH: "Maximum SWR bandwidth",
        Language.SPANISH: "Máximo ancho de banda de SWR",
    },
    "optimize.max_gain_objective": {
        Language.ENGLISH: "Maximum power gain",
        Language.SPANISH: "Ganancia máxima de potencia",
    },
    "optimize.max_efficiency_objective": {
        Language.ENGLISH: "Maximum efficiency",
        Language.SPANISH: "Máxima eficiencia",
    },
    "optimize.balanced_objective": {
        Language.ENGLISH: "Balanced SWR + gain",
        Language.SPANISH: "SWR + ganancia equilibrados",
    },
    "optimize.target_reactance": {
        Language.ENGLISH: "Target reactance (Ω)",
        Language.SPANISH: "Reactancia objetivo (Ω)",
    },
    "optimize.target_resistance": {
        Language.ENGLISH: "Target resistance R (Ω)",
        Language.SPANISH: "Resistencia objetivo R (Ω)",
    },
    "optimize.max_evaluations": {
        Language.ENGLISH: "Maximum evaluations",
        Language.SPANISH: "Evaluaciones máximas",
    },
    "optimize.tolerance": {
        Language.ENGLISH: "Reactance tolerance (Ω)",
        Language.SPANISH: "Tolerancia de reactancia (Ω)",
    },
    "optimize.impedance_tolerance": {
        Language.ENGLISH: "Impedance tolerance (Ω)",
        Language.SPANISH: "Tolerancia de impedancia (Ω)",
    },
    "optimize.swr_tolerance": {
        Language.ENGLISH: "SWR tolerance",
        Language.SPANISH: "Tolerancia de SWR",
    },
    "optimize.swr_limit": {
        Language.ENGLISH: "SWR limit for bandwidth",
        Language.SPANISH: "Límite de SWR para ancho de banda",
    },
    "optimize.bandwidth": {
        Language.ENGLISH: "Bandwidth (MHz)",
        Language.SPANISH: "Ancho de banda (MHz)",
    },
    "optimize.gain": {
        Language.ENGLISH: "Max gain (dBi)",
        Language.SPANISH: "Ganancia máx. (dBi)",
    },
    "optimize.efficiency": {
        Language.ENGLISH: "Efficiency (%)",
        Language.SPANISH: "Eficiencia (%)",
    },
    "optimize.swr_weight": {
        Language.ENGLISH: "SWR weight",
        Language.SPANISH: "Peso de SWR",
    },
    "optimize.gain_weight": {
        Language.ENGLISH: "Gain weight",
        Language.SPANISH: "Peso de ganancia",
    },
    "optimize.efficiency_weight": {
        Language.ENGLISH: "Efficiency weight",
        Language.SPANISH: "Peso de eficiencia",
    },
    "optimize.max_swr_constraint": {
        Language.ENGLISH: "Maximum SWR constraint",
        Language.SPANISH: "Restricción de SWR máximo",
    },
    "optimize.bandwidth_result": {
        Language.ENGLISH: "Bandwidth {value} MHz",
        Language.SPANISH: "Ancho de banda {value} MHz",
    },
    "optimize.gain_result": {
        Language.ENGLISH: "Max gain {value} dBi",
        Language.SPANISH: "Ganancia máxima {value} dBi",
    },
    "optimize.efficiency_result": {
        Language.ENGLISH: "Efficiency {value} %",
        Language.SPANISH: "Eficiencia {value} %",
    },
    "optimize.score_result": {
        Language.ENGLISH: "Score {value}",
        Language.SPANISH: "Puntuación {value}",
    },
    "optimize.impedance_error_result": {
        Language.ENGLISH: "Impedance error {value} Ω",
        Language.SPANISH: "Error de impedancia {value} Ω",
    },
    "optimize.bandwidth_needs_sweep": {
        Language.ENGLISH: "Bandwidth optimization requires a frequency sweep.",
        Language.SPANISH: "La optimización por ancho de banda requiere un barrido de frecuencia.",
    },
    "optimize.gain_needs_far_field": {
        Language.ENGLISH: "Gain optimization requires the far-field pattern.",
        Language.SPANISH: "La optimización por ganancia requiere el patrón de campo lejano.",
    },
    "optimize.run": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "optimize.cancel_run": {
        Language.ENGLISH: "Cancel optimization",
        Language.SPANISH: "Cancelar optimización",
    },
    "optimize.apply": {
        Language.ENGLISH: "Apply best dimension",
        Language.SPANISH: "Aplicar dimensión óptima",
    },
    "optimize.running": {
        Language.ENGLISH: "Running optimization...",
        Language.SPANISH: "Ejecutando optimización...",
    },
    "optimize.summary": {
        Language.ENGLISH: "Status: {status} · Best dimension: {length} · X={reactance} Ω · SWR={swr}",
        Language.SPANISH: "Estado: {status} · Mejor dimensión: {length} · X={reactance} Ω · ROE={swr}",
    },
    "optimize.no_best": {
        Language.ENGLISH: "No valid dimension was found.",
        Language.SPANISH: "No se encontró una dimensión válida.",
    },
    "optimize.evaluations": {
        Language.ENGLISH: "Evaluations",
        Language.SPANISH: "Evaluaciones",
    },
    "optimize.sensitivity": {
        Language.ENGLISH: "Sensitivity",
        Language.SPANISH: "Sensibilidad",
    },
    "optimize.mode": {
        Language.ENGLISH: "Operating mode",
        Language.SPANISH: "Modo de operación",
    },
    "optimize.mode.single": {
        Language.ENGLISH: "Single frequency",
        Language.SPANISH: "Frecuencia única",
    },
    "optimize.mode.band_aware": {
        Language.ENGLISH: "Band-aware",
        Language.SPANISH: "Consciente de banda",
    },
    "optimize.mode.robust": {
        Language.ENGLISH: "Robust (tolerance)",
        Language.SPANISH: "Robusto (tolerancia)",
    },
    "optimize.band_edges": {
        Language.ENGLISH: "Band edges (MHz)",
        Language.SPANISH: "Bordes de banda (MHz)",
    },
    "optimize.band_edges_hint": {
        Language.ENGLISH: "Comma-separated frequencies in MHz; at least two.",
        Language.SPANISH: "Frecuencias separadas por comas en MHz; al menos dos.",
    },
    "optimize.band_edges_invalid": {
        Language.ENGLISH: "Enter at least two positive frequencies in MHz.",
        Language.SPANISH: "Introduce al menos dos frecuencias positivas en MHz.",
    },
    "optimize.robust_tolerance": {
        Language.ENGLISH: "Dimensional tolerance",
        Language.SPANISH: "Tolerancia dimensional",
    },
    "optimize.pareto": {
        Language.ENGLISH: "Pareto front (non-dominated trade-offs)",
        Language.SPANISH: "Frente de Pareto (compromisos no dominados)",
    },
    "optimize.recommendations": {
        Language.ENGLISH: "Recommendations",
        Language.SPANISH: "Recomendaciones",
    },
    "optimize.recommend.warning": {
        Language.ENGLISH: "Warning",
        Language.SPANISH: "Advertencia",
    },
    "optimize.recommend.info": {
        Language.ENGLISH: "Note",
        Language.SPANISH: "Nota",
    },
    "optimize.recommend.no_feasible": {
        Language.ENGLISH: (
            "No feasible candidate was found. Widen the variable bounds, relax a "
            "constraint, or unlock more variables."
        ),
        Language.SPANISH: (
            "No se encontró ningún candidato factible. Amplía los límites de las "
            "variables, relaja una restricción o desbloquea más variables."
        ),
    },
    "optimize.recommend.cancelled": {
        Language.ENGLISH: "The run was cancelled; the best candidate so far is not a completed result.",
        Language.SPANISH: "La ejecución se canceló; el mejor candidato hasta ahora no es un resultado completo.",
    },
    "optimize.recommend.budget": {
        Language.ENGLISH: "The evaluation budget was exhausted. Try the Thorough profile for a wider search.",
        Language.SPANISH: "Se agotó el presupuesto de evaluaciones. Prueba el perfil Exhaustivo para una búsqueda más amplia.",
    },
    "optimize.recommend.locked": {
        Language.ENGLISH: "Some variables were locked, so this is a partial optimization. Unlock them to search the full design.",
        Language.SPANISH: "Algunas variables estaban bloqueadas, así que esta es una optimización parcial. Desbloquéalas para buscar el diseño completo.",
    },
    "optimize.recommend.high_swr": {
        Language.ENGLISH: "The best design still has high SWR at the evaluated points. Consider a matching network or a different topology.",
        Language.SPANISH: "El mejor diseño aún tiene una ROE alta en los puntos evaluados. Considera una red de adaptación u otra topología.",
    },
    "optimize.recommend.high_swr_constraint": {
        Language.ENGLISH: "The SWR constraint was not met. Relax it or add a matching stage before applying the result.",
        Language.SPANISH: "No se cumplió la restricción de ROE. Relájala o añade una etapa de adaptación antes de aplicar el resultado.",
    },
    "optimize.recommend.band_spread": {
        Language.ENGLISH: "SWR varies strongly across the evaluated points. Check the band edges before applying the result.",
        Language.SPANISH: "La ROE varía mucho entre los puntos evaluados. Revisa los bordes de banda antes de aplicar el resultado.",
    },
    "optimize.recommend.robust": {
        Language.ENGLISH: "The score is sensitive to the dimensional tolerance. Tighten construction tolerances or re-run in band-aware mode.",
        Language.SPANISH: "La puntuación es sensible a la tolerancia dimensional. Ajusta las tolerancias de construcción o vuelve a ejecutar en modo consciente de banda.",
    },
    "optimize.recommend.sensitive": {
        Language.ENGLISH: "{variables} has the largest effect on the score. Control that dimension during construction.",
        Language.SPANISH: "{variables} tiene el mayor efecto en la puntuación. Controla esa dimensión durante la construcción.",
    },
    "optimize.last_summary": {
        Language.ENGLISH: (
            "Last run: {date} · {mode} · {objective} · {status} · "
            "{count} evaluations · best SWR {swr}"
        ),
        Language.SPANISH: (
            "Última ejecución: {date} · {mode} · {objective} · {status} · "
            "{count} evaluaciones · mejor ROE {swr}"
        ),
    },
    "optimize.budget_hint_quality": {
        Language.ENGLISH: (
            "Estimated solver runs: {count} ({points} frequencies x {scenarios} "
            "scenario(s) per candidate). Quality modes are expensive; the search "
            "may extend automatically."
        ),
        Language.SPANISH: (
            "Corridas estimadas del solver: {count} ({points} frecuencias x "
            "{scenarios} escenario(s) por candidato). Los modos de calidad son "
            "costosos; la búsqueda puede extenderse automáticamente."
        ),
    },
    "optimize.score": {
        Language.ENGLISH: "Score",
        Language.SPANISH: "Puntuación",
    },
    "optimize.rank": {Language.ENGLISH: "Rank", Language.SPANISH: "Ranking"},
    "optimize.iteration": {Language.ENGLISH: "#", Language.SPANISH: "#"},
    "optimize.length": {Language.ENGLISH: "Dimension", Language.SPANISH: "Dimensión"},
    "optimize.offset": {Language.ENGLISH: "Offset", Language.SPANISH: "Desvío"},
    "optimize.message": {Language.ENGLISH: "Message", Language.SPANISH: "Mensaje"},
    "optimize.apply_hint": {
        Language.ENGLISH: "Apply the best dimension and simulate to validate the full sweep.",
        Language.SPANISH: "Aplicá la mejor dimensión y simulá para validar el barrido completo.",
    },
    "optimize.close_optimization": {
        Language.ENGLISH: "Cancel the running optimization before closing.",
        Language.SPANISH: "Cancelá la optimización en curso antes de cerrar.",
    },
    "optimize.family_title": {
        Language.ENGLISH: "Family Optimizer",
        Language.SPANISH: "Optimizador de familia",
    },
    "optimize.variables": {
        Language.ENGLISH: "Design variables",
        Language.SPANISH: "Variables de diseño",
    },
    "optimize.use": {
        Language.ENGLISH: "Use",
        Language.SPANISH: "Usar",
    },
    "optimize.current": {
        Language.ENGLISH: "Current",
        Language.SPANISH: "Actual",
    },
    "optimize.minimum": {
        Language.ENGLISH: "Minimum",
        Language.SPANISH: "Mínimo",
    },
    "optimize.maximum": {
        Language.ENGLISH: "Maximum",
        Language.SPANISH: "Máximo",
    },
    "optimize.budget_profile": {
        Language.ENGLISH: "Search budget",
        Language.SPANISH: "Presupuesto de búsqueda",
    },
    "optimize.budget.fast": {
        Language.ENGLISH: "Fast",
        Language.SPANISH: "Rápido",
    },
    "optimize.budget.balanced": {
        Language.ENGLISH: "Balanced (recommended)",
        Language.SPANISH: "Balanceado (recomendado)",
    },
    "optimize.budget.thorough": {
        Language.ENGLISH: "Thorough",
        Language.SPANISH: "Exhaustivo",
    },
    "optimize.seed": {
        Language.ENGLISH: "Random seed",
        Language.SPANISH: "Semilla aleatoria",
    },
    "optimize.run_family": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "optimize.apply_best": {
        Language.ENGLISH: "Apply Best...",
        Language.SPANISH: "Aplicar mejor...",
    },
    "optimize.locked_partial": {
        Language.ENGLISH: "Partial optimization: some variables are locked.",
        Language.SPANISH: "Optimización parcial: algunas variables están bloqueadas.",
    },
    "optimize.family_summary": {
        Language.ENGLISH: "Status: {status} · Evaluations: {count} · Best score: {score}",
        Language.SPANISH: "Estado: {status} · Evaluaciones: {count} · Mejor puntuación: {score}",
    },
    "optimize.no_feasible": {
        Language.ENGLISH: "No feasible design was found within the selected bounds and constraints.",
        Language.SPANISH: "No se encontró un diseño factible dentro de los límites y restricciones elegidos.",
    },
    "optimize.budget_hint": {
        Language.ENGLISH: "Estimated solver runs: {count}, including sensitivity probes. The search may extend automatically.",
        Language.SPANISH: "Corridas estimadas del solver: {count}, incluyendo sondas de sensibilidad. La búsqueda puede extenderse automáticamente.",
    },
    "optimize.budget_hint_sweep": {
        Language.ENGLISH: (
            "Estimated solver runs: {count} ({points} frequencies per candidate). "
            "Bandwidth optimization is expensive; the search may extend automatically."
        ),
        Language.SPANISH: (
            "Corridas estimadas del solver: {count} ({points} frecuencias por candidato). "
            "La optimización por ancho de banda es costosa; la búsqueda puede extenderse automáticamente."
        ),
    },
    "optimize.group": {
        Language.ENGLISH: "Group",
        Language.SPANISH: "Grupo",
    },
    "optimize.group.geometry": {
        Language.ENGLISH: "Geometry",
        Language.SPANISH: "Geometría",
    },
    "optimize.group.feed": {
        Language.ENGLISH: "Feed",
        Language.SPANISH: "Alimentación",
    },
    "optimize.group.loads": {
        Language.ENGLISH: "Family loads",
        Language.SPANISH: "Cargas de familia",
    },
    "optimize.group.conductor": {
        Language.ENGLISH: "Conductor",
        Language.SPANISH: "Conductor",
    },
    "optimize.constraint.positive": {
        Language.ENGLISH: "This dimension must be positive.",
        Language.SPANISH: "Esta dimensión debe ser positiva.",
    },
    "optimize.constraint.non_negative": {
        Language.ENGLISH: "This dimension must not be negative.",
        Language.SPANISH: "Esta dimensión no puede ser negativa.",
    },
    "optimize.constraint.radial_count": {
        Language.ENGLISH: "The radial system requires at least one radial.",
        Language.SPANISH: "El sistema de radiales requiere al menos un radial.",
    },
    "optimize.constraint.coil_offset": {
        Language.ENGLISH: "The loading-coil offset must lie within the radiator.",
        Language.SPANISH: "El offset de la bobina debe quedar dentro del radiador.",
    },
    "optimize.constraint.top_hat_wires": {
        Language.ENGLISH: "The top hat requires at least one wire.",
        Language.SPANISH: "El top hat requiere al menos un hilo.",
    },
    "optimize.constraint.conductor_spacing": {
        Language.ENGLISH: "The conductor spacing is too small for the wire diameter.",
        Language.SPANISH: "La separación entre conductores es demasiado pequeña para el diámetro del hilo.",
    },
    "optimize.constraint.match_length": {
        Language.ENGLISH: "The hairpin match is shorter than the minimum conductor spacing.",
        Language.SPANISH: "El match hairpin es más corto que la separación mínima entre conductores.",
    },
    "optimize.constraint.feed_offset": {
        Language.ENGLISH: "The feed offset must be shorter than the fed element.",
        Language.SPANISH: "El offset de alimentación debe ser menor que el elemento alimentado.",
    },
    "optimize.constraint.endfed_height": {
        Language.ENGLISH: "The height difference must not exceed the end-fed wire length.",
        Language.SPANISH: "La diferencia de altura no puede superar la longitud del hilo alimentado en el extremo.",
    },
    "optimize.constraint.fan_angles": {
        Language.ENGLISH: "Fan-dipole elements must use distinct included angles.",
        Language.SPANISH: "Los elementos del dipolo abanico deben usar ángulos incluidos distintos.",
    },
    "optimize.constraint.trap_frequency": {
        Language.ENGLISH: "The trap frequency must be above the low-band design frequency.",
        Language.SPANISH: "La frecuencia de la trampa debe estar por encima de la frecuencia de diseño de la banda baja.",
    },
    "optimize.constraint.moxon_gap": {
        Language.ENGLISH: "The Moxon tips must leave a gap between the elements.",
        Language.SPANISH: "Las puntas del Moxon deben dejar una brecha entre los elementos.",
    },
    "optimize.constraint.vertical_clearance": {
        Language.ENGLISH: "A vertically polarized array must clear the ground.",
        Language.SPANISH: "Un conjunto con polarización vertical debe quedar por encima del suelo.",
    },
    "optimize.unavailable.pending_family": {
        Language.ENGLISH: "This family is waiting for its descriptor in the family-optimizer migration.",
        Language.SPANISH: "Esta familia espera su descriptor en la migración al optimizador de familias.",
    },
    "optimize.unavailable.magnetic_loop": {
        Language.ENGLISH: "The magnetic-loop capacitor and loss model are not accurate enough for an optimizer.",
        Language.SPANISH: "El modelo de capacitor y pérdidas del lazo magnético no es suficientemente preciso para un optimizador.",
    },
    "optimize.unavailable.random_wire": {
        Language.ENGLISH: "A random wire is deliberately non-resonant and tuner-assisted; it has no stable optimum.",
        Language.SPANISH: "Un hilo aleatorio es deliberadamente no resonante y depende de un tuner; no tiene un óptimo estable.",
    },
    "optimize.unavailable.custom_generator": {
        Language.ENGLISH: "This generator must first become a typed family before it can be optimized.",
        Language.SPANISH: "Este generador debe convertirse primero en una familia tipada antes de poder optimizarse.",
    },
    "optimize.unavailable.custom_geometry": {
        Language.ENGLISH: "Arbitrary custom geometry has no parameterized topology to optimize.",
        Language.SPANISH: "La geometría personalizada arbitraria no tiene una topología parametrizada para optimizar.",
    },
    "optimize.unavailable.unsupported": {
        Language.ENGLISH: "This antenna type has no registered optimizer.",
        Language.SPANISH: "Este tipo de antena no tiene un optimizador registrado.",
    },
    "element_optimize.objective.min_swr": {
        Language.ENGLISH: "Minimum SWR",
        Language.SPANISH: "SWR mínimo",
    },
    "element_optimize.objective.max_efficiency": {
        Language.ENGLISH: "Maximum efficiency",
        Language.SPANISH: "Máxima eficiencia",
    },
    "optimize_status.converged": {
        Language.ENGLISH: "converged",
        Language.SPANISH: "convergió",
    },
    "optimize_status.max_evaluations": {
        Language.ENGLISH: "maximum evaluations reached",
        Language.SPANISH: "máximo de evaluaciones alcanzado",
    },
    "optimize_status.no_feasible": {
        Language.ENGLISH: "no feasible design",
        Language.SPANISH: "sin diseño factible",
    },
    "optimize_status.no_bracket": {
        Language.ENGLISH: "target not bracketed",
        Language.SPANISH: "objetivo fuera del intervalo",
    },
    "optimize_status.cancelled": {
        Language.ENGLISH: "cancelled",
        Language.SPANISH: "cancelada",
    },
    "optimize_status.error": {Language.ENGLISH: "error", Language.SPANISH: "error"},
    "error.optimize": {
        Language.ENGLISH: "Optimization failed: {message}",
        Language.SPANISH: "Falló la optimización: {message}",
    },
    "error.optimize_custom": {
        Language.ENGLISH: "Custom or imported geometry has no generic optimizer. Select variables explicitly or use a template.",
        Language.SPANISH: "La geometría personalizada o importada no tiene un optimizador genérico. Seleccioná variables explícitamente o usá una plantilla.",
    },
    "error.optimize_magnetic_loop": {
        Language.ENGLISH: (
            "The magnetic-loop generator has no generic optimizer yet. Tune the "
            "capacitance with the SWR sweep or a measurement."
        ),
        Language.SPANISH: (
            "El generador de lazo magnético todavía no tiene un optimizador "
            "genérico. Sintonizá el capacitor con el barrido de ROE o una "
            "medición."
        ),
    },
    "error.optimize_inverted_l": {
        Language.ENGLISH: (
            "The inverted-L generator has no generic optimizer yet. Adjust the "
            "vertical height and horizontal run directly, or optimize a related "
            "wire design."
        ),
        Language.SPANISH: (
            "El generador de L invertida todavía no tiene un optimizador "
            "genérico. Ajustá la altura vertical y el tramo horizontal "
            "directamente, u optimizá un diseño de hilo relacionado."
        ),
    },
    "synthesis.title": {
        Language.ENGLISH: "Synthesize Antenna Dimensions",
        Language.SPANISH: "Sintetizar dimensiones de antena",
    },
    "synthesis.target_frequency": {
        Language.ENGLISH: "Target frequency (MHz)",
        Language.SPANISH: "Frecuencia objetivo (MHz)",
    },
    "synthesis.target_resistance": {
        Language.ENGLISH: "Target resistance R (Ω)",
        Language.SPANISH: "Resistencia objetivo R (Ω)",
    },
    "synthesis.target_reactance": {
        Language.ENGLISH: "Target reactance X (Ω)",
        Language.SPANISH: "Reactancia objetivo X (Ω)",
    },
    "synthesis.ocfd_transformer_note": {
        Language.ENGLISH: (
            "Targets are transmitter-side. With the {ratio}:1 ideal transformer, "
            "a {target} Ω target at the transmitter is about {antenna} Ω at the antenna."
        ),
        Language.SPANISH: (
            "Los objetivos son del lado del transmisor. Con el transformador ideal "
            "{ratio}:1, un objetivo de {target} Ω en el transmisor equivale a unos "
            "{antenna} Ω en la antena."
        ),
    },
    "synthesis.impedance_error": {
        Language.ENGLISH: "|Z-Zt| (Ω)",
        Language.SPANISH: "|Z-Zt| (Ω)",
    },
    "measurement.measured_r": {
        Language.ENGLISH: "Measured R (Ω)",
        Language.SPANISH: "R medida (Ω)",
    },
    "measurement.measured_x": {
        Language.ENGLISH: "Measured X (Ω)",
        Language.SPANISH: "X medida (Ω)",
    },
    "measurement.measured_z": {
        Language.ENGLISH: "Measured |Z| (Ω)",
        Language.SPANISH: "|Z| medida (Ω)",
    },
    "measurement.measured_swr": {
        Language.ENGLISH: "Measured SWR",
        Language.SPANISH: "ROE medida",
    },
    "measurement.simulated_r": {
        Language.ENGLISH: "Simulated R (Ω)",
        Language.SPANISH: "R simulada (Ω)",
    },
    "measurement.simulated_x": {
        Language.ENGLISH: "Simulated X (Ω)",
        Language.SPANISH: "X simulada (Ω)",
    },
    "measurement.impedance_error": {
        Language.ENGLISH: "Impedance error (Ω)",
        Language.SPANISH: "Error de impedancia (Ω)",
    },
    "measurement.comparison_summary": {
        Language.ENGLISH: "Compared {count} points · mean |ΔZ| = {mean} Ω · max = {maximum} Ω",
        Language.SPANISH: "Comparados {count} puntos · |ΔZ| medio = {mean} Ω · máximo = {maximum} Ω",
    },
    "measurement.comparison_none": {
        Language.ENGLISH: "No overlapping simulated frequencies.",
        Language.SPANISH: "No hay frecuencias simuladas superpuestas.",
    },
    "synthesis.minimum": {
        Language.ENGLISH: "Minimum",
        Language.SPANISH: "Mínimo",
    },
    "synthesis.maximum": {
        Language.ENGLISH: "Maximum",
        Language.SPANISH: "Máximo",
    },
    "synthesis.run": {
        Language.ENGLISH: "Run synthesis",
        Language.SPANISH: "Ejecutar síntesis",
    },
    "synthesis.apply": {
        Language.ENGLISH: "Apply dimensions",
        Language.SPANISH: "Aplicar dimensiones",
    },
    "synthesis.running": {
        Language.ENGLISH: "Running synthesis...",
        Language.SPANISH: "Ejecutando síntesis...",
    },
    "synthesis.summary": {
        Language.ENGLISH: "Status: {status} · {a} · {b} · R={resistance} Ω, X={reactance} Ω · SWR={swr} · impedance error={error} Ω",
        Language.SPANISH: "Estado: {status} · {a} · {b} · R={resistance} Ω, X={reactance} Ω · ROE={swr} · error de impedancia={error} Ω",
    },
    "synthesis.no_best": {
        Language.ENGLISH: "No valid dimensions were found ({status}).",
        Language.SPANISH: "No se encontraron dimensiones válidas ({status}).",
    },
    "synthesis.apply_hint": {
        Language.ENGLISH: "This is a numerical starting point. Apply it, run a full sweep, and verify the result before construction.",
        Language.SPANISH: "Este es un punto de partida numérico. Aplicalo, ejecutá un barrido completo y verificá el resultado antes de construir.",
    },
    "synthesis.error": {
        Language.ENGLISH: "Synthesis failed: {message}",
        Language.SPANISH: "Falló la síntesis: {message}",
    },
    "synthesis.close_synthesis": {
        Language.ENGLISH: "Cancel the running synthesis before closing.",
        Language.SPANISH: "Cancelá la síntesis en curso antes de cerrar.",
    },
    "currents.none": {
        Language.ENGLISH: "No current data.",
        Language.SPANISH: "Sin datos de corriente.",
    },
    "currents.segment": {Language.ENGLISH: "Segment", Language.SPANISH: "Segmento"},
    "currents.magnitude": {Language.ENGLISH: "Current (A)", Language.SPANISH: "Corriente (A)"},
    "resonance.label": {
        Language.ENGLISH: "Resonance: {frequency} MHz, R={resistance} Ω",
        Language.SPANISH: "Resonancia: {frequency} MHz, R={resistance} Ω",
    },
    "resonance.none": {
        Language.ENGLISH: "No resonance in the sweep.",
        Language.SPANISH: "Sin resonancia en el barrido.",
    },
    "cursor.impedance_readout": {
        Language.ENGLISH: "{frequency} · R {resistance} · X {reactance} · |Z| {magnitude} · SWR {swr}",
        Language.SPANISH: "{frequency} · R {resistance} · X {reactance} · |Z| {magnitude} · ROE {swr}",
    },
    "cursor.swr_readout": {
        Language.ENGLISH: "{frequency} · SWR {swr}",
        Language.SPANISH: "{frequency} · ROE {swr}",
    },
    "cursor.gain_readout": {
        Language.ENGLISH: "{angle} · {gain}",
        Language.SPANISH: "{angle} · {gain}",
    },
    "cursor.current_readout": {
        Language.ENGLISH: "{frequency} · segment {segment} · {current}",
        Language.SPANISH: "{frequency} · segmento {segment} · {current}",
    },
    "plot.currents": {
        Language.ENGLISH: "Segment current",
        Language.SPANISH: "Corriente por segmento",
    },
    "plot.impedance": {Language.ENGLISH: "Impedance", Language.SPANISH: "Impedancia"},
    "plot.impedance_axis": {Language.ENGLISH: "Impedance (Ω)", Language.SPANISH: "Impedancia (Ω)"},
    "plot.swr": {Language.ENGLISH: "SWR", Language.SPANISH: "ROE"},
    "plot.pattern": {
        Language.ENGLISH: "Power gain pattern",
        Language.SPANISH: "Patrón de ganancia de potencia",
    },
    "results.none": {
        Language.ENGLISH: "No simulation results yet.",
        Language.SPANISH: "Todavía no hay resultados de simulación.",
    },
    "diagnostic.severity": {Language.ENGLISH: "Severity", Language.SPANISH: "Severidad"},
    "diagnostic.code": {Language.ENGLISH: "Code", Language.SPANISH: "Código"},
    "diagnostic.message": {Language.ENGLISH: "Message", Language.SPANISH: "Mensaje"},
    "diagnostic.none": {Language.ENGLISH: "No diagnostics.", Language.SPANISH: "Sin diagnósticos."},
    "diagnostic.antenna.feed.at_wire_end": {
        Language.ENGLISH: "The feed is at the end of its wire.",
        Language.SPANISH: "La alimentación está en el extremo del hilo.",
    },
    "diagnostic.antenna.feed.out_of_range": {
        Language.ENGLISH: "The feed offset is outside its wire.",
        Language.SPANISH: "La posición de alimentación está fuera del hilo.",
    },
    "diagnostic.antenna.feed.unknown_wire": {
        Language.ENGLISH: "The feed references an unknown wire.",
        Language.SPANISH: "La alimentación referencia un hilo inexistente.",
    },
    "diagnostic.antenna.frequency.invalid": {
        Language.ENGLISH: "The antenna frequency is invalid.",
        Language.SPANISH: "La frecuencia de la antena es inválida.",
    },
    "diagnostic.antenna.name.empty": {
        Language.ENGLISH: "The antenna name is empty.",
        Language.SPANISH: "El nombre de la antena está vacío.",
    },
    "diagnostic.antenna.wire.duplicate_id": {
        Language.ENGLISH: "Two wires use the same identifier.",
        Language.SPANISH: "Dos hilos usan el mismo identificador.",
    },
    "diagnostic.antenna.wires.empty": {
        Language.ENGLISH: "The antenna has no wires.",
        Language.SPANISH: "La antena no tiene hilos.",
    },
    "diagnostic.far_field.below_ground": {
        Language.ENGLISH: "The far-field request goes below ground.",
        Language.SPANISH: "La solicitud de campo lejano llega debajo del suelo.",
    },
    "diagnostic.normalization.feed_segment_missing": {
        Language.ENGLISH: "The feed segment was not found in the solver output.",
        Language.SPANISH: "No se encontró el segmento de alimentación en la salida del solver.",
    },
    "diagnostic.normalization.impedance_missing": {
        Language.ENGLISH: "The solver output has no impedance data.",
        Language.SPANISH: "La salida del solver no tiene datos de impedancia.",
    },
    "diagnostic.normalization.negative_resistance": {
        Language.ENGLISH: (
            "Negative input resistance: the passive antenna model is invalid. "
            "Check very short gaps or matching wires, segmentation, radial height, "
            "and the ground model; far-field gains are unavailable."
        ),
        Language.SPANISH: (
            "Resistencia de entrada negativa: el modelo pasivo de la antena no es "
            "válido. Revisá gaps o hilos de adaptación muy cortos, la segmentación, "
            "la altura de los radiales y el modelo de suelo; las ganancias de campo "
            "lejano no están disponibles."
        ),
    },
    "diagnostic.project.design.duplicate_id": {
        Language.ENGLISH: "Two designs use the same identifier.",
        Language.SPANISH: "Dos diseños usan el mismo identificador.",
    },
    "diagnostic.project.design.duplicate_name": {
        Language.ENGLISH: "Two designs use the same name.",
        Language.SPANISH: "Dos diseños usan el mismo nombre.",
    },
    "diagnostic.project.name.empty": {
        Language.ENGLISH: "The project name is empty.",
        Language.SPANISH: "El nombre del proyecto está vacío.",
    },
    "diagnostic.project.simulation_run.duplicate_id": {
        Language.ENGLISH: "Two simulation runs use the same identifier.",
        Language.SPANISH: "Dos corridas usan el mismo identificador.",
    },
    "diagnostic.project.simulation_run.unknown_design": {
        Language.ENGLISH: "A simulation run references an unknown design.",
        Language.SPANISH: "Una corrida referencia un diseño inexistente.",
    },
    "diagnostic.project.timestamp.invalid": {
        Language.ENGLISH: "A project timestamp is invalid.",
        Language.SPANISH: "Una marca de tiempo del proyecto es inválida.",
    },
    "diagnostic.project.timestamp.order": {
        Language.ENGLISH: "The project timestamps are out of order.",
        Language.SPANISH: "Las marcas de tiempo del proyecto están fuera de orden.",
    },
    "diagnostic.solver.pattern_resolution_reduced": {
        Language.ENGLISH: (
            "The far-field pattern resolution was reduced to fit the project storage limit."
        ),
        Language.SPANISH: (
            "Se redujo la resolución del patrón de campo lejano para ajustarse "
            "al límite de almacenamiento del proyecto."
        ),
    },
    "diagnostic.solver.pattern_disabled": {
        Language.ENGLISH: (
            "The far-field pattern was disabled because the sweep is too large "
            "for the project storage limit."
        ),
        Language.SPANISH: (
            "Se desactivó el patrón de campo lejano porque el barrido es "
            "demasiado grande para el límite de almacenamiento del proyecto."
        ),
    },
    "diagnostic.geometry.ground_clearance": {
        Language.ENGLISH: (
            "The model was raised slightly above the ground plane so NEC can "
            "evaluate the ground-mounted wires."
        ),
        Language.SPANISH: (
            "El modelo se elevó ligeramente sobre el plano de tierra para que "
            "NEC pueda evaluar los hilos montados sobre el suelo."
        ),
    },
    "diagnostic.geometry.ground_mounted_wires": {
        Language.ENGLISH: (
            "Conductors at or near ground level (for example, ground-mounted "
            "radials) use a 1 cm NEC clearance. NEC-2 does not model buried or "
            "soil-contact wires, so impedance and gain may be numerically "
            "unreliable. Use a sensitivity study and measurement, or raise the "
            "radial plane."
        ),
        Language.SPANISH: (
            "Los conductores al nivel del suelo o muy cerca de él (por ejemplo, "
            "radiales apoyados) usan un despeje NEC de 1 cm. NEC-2 no modela "
            "hilos enterrados ni en contacto con el suelo, así que la impedancia "
            "y la ganancia pueden no ser confiables numéricamente. Usá un estudio "
            "de sensibilidad y medición, o elevá el plano de radiales."
        ),
    },
    "diagnostic.geometry.below_ground": {
        Language.ENGLISH: (
            "The model has wires below the ground plane. Raise the geometry above z = 0."
        ),
        Language.SPANISH: (
            "El modelo tiene hilos debajo del plano de tierra. Elevá la "
            "geometría por encima de z = 0."
        ),
    },
    "diagnostic.solver.output_too_large": {
        Language.ENGLISH: (
            "The solver output exceeded the storage limit. Reduce sweep points, "
            "use a coarser pattern resolution, or disable the far-field pattern."
        ),
        Language.SPANISH: (
            "La salida del solver superó el límite de almacenamiento. Reducí los "
            "puntos del barrido, usá una resolución de patrón más gruesa o "
            "desactivá el patrón de campo lejano."
        ),
    },
    "diagnostic.segmentation.transmission_line_offset": {
        Language.ENGLISH: (
            "A transmission-line endpoint is not at a segment center; the "
            "connection is approximate."
        ),
        Language.SPANISH: (
            "Un extremo de la línea de transmisión no está en el centro de un "
            "segmento; la conexión es aproximada."
        ),
    },
    "diagnostic.segmentation.feed_offset": {
        Language.ENGLISH: "The feed is not centered on a segment; the delta gap is approximate.",
        Language.SPANISH: "La alimentación no está centrada en un segmento; el gap delta es aproximado.",
    },
    "diagnostic.segmentation.few_segments": {
        Language.ENGLISH: "A wire uses too few segments for an accurate current distribution.",
        Language.SPANISH: "Un hilo usa muy pocos segmentos para una distribución de corriente precisa.",
    },
    "diagnostic.segmentation.segment_too_long": {
        Language.ENGLISH: "A segment is longer than lambda/10; NEC accuracy may degrade.",
        Language.SPANISH: "Un segmento supera lambda/10; la precisión de NEC puede degradarse.",
    },
    "diagnostic.segmentation.segment_too_short": {
        Language.ENGLISH: "A segment is shorter than 1/1000 of a wavelength; NEC loses accuracy.",
        Language.SPANISH: (
            "Un segmento es más corto que 1/1000 de una longitud de onda; NEC pierde precisión."
        ),
    },
    "diagnostic.segmentation.radius_ratio_low": {
        Language.ENGLISH: (
            "The segment length to radius ratio is below 8; the thin-wire kernel "
            "can exceed 1% error."
        ),
        Language.SPANISH: (
            "La relación entre longitud de segmento y radio es menor que 8; el "
            "kernel de hilo delgado puede superar el 1% de error."
        ),
    },
    "diagnostic.segmentation.segment_too_thin": {
        Language.ENGLISH: "A segment is shorter than twice the wire radius.",
        Language.SPANISH: "Un segmento es más corto que dos veces el radio del hilo.",
    },
    "diagnostic.solver.cancelled": {
        Language.ENGLISH: "Simulation cancelled.",
        Language.SPANISH: "Simulación cancelada.",
    },
    "diagnostic.solver.execution_error": {
        Language.ENGLISH: "The solver process failed.",
        Language.SPANISH: "El proceso del solver falló.",
    },
    "diagnostic.solver.exit_code": {
        Language.ENGLISH: "The solver exited with an error.",
        Language.SPANISH: "El solver terminó con error.",
    },
    "diagnostic.solver.input_error": {
        Language.ENGLISH: "The solver rejected the input.",
        Language.SPANISH: "El solver rechazó la entrada.",
    },
    "diagnostic.solver.not_available": {
        Language.ENGLISH: "The NEC2C executable is not available.",
        Language.SPANISH: "El ejecutable NEC2C no está disponible.",
    },
    "diagnostic.solver.permeability_unsupported": {
        Language.ENGLISH: "Relative permeability is not emitted to NEC.",
        Language.SPANISH: "La permeabilidad relativa no se envía a NEC.",
    },
    "diagnostic.solver.timeout": {
        Language.ENGLISH: "The solver timed out.",
        Language.SPANISH: "El solver agotó el tiempo de espera.",
    },
    "severity.info": {Language.ENGLISH: "Info", Language.SPANISH: "Información"},
    "severity.warning": {Language.ENGLISH: "Warning", Language.SPANISH: "Advertencia"},
    "severity.error": {Language.ENGLISH: "Error", Language.SPANISH: "Error"},
    "status_value.completed": {Language.ENGLISH: "completed", Language.SPANISH: "completada"},
    "status_value.cancelled": {Language.ENGLISH: "cancelled", Language.SPANISH: "cancelada"},
    "status_value.partial": {Language.ENGLISH: "partial", Language.SPANISH: "parcial"},
    "status_value.error": {Language.ENGLISH: "error", Language.SPANISH: "error"},
    "results.status": {Language.ENGLISH: "Status", Language.SPANISH: "Estado"},
    "results.solver": {Language.ENGLISH: "Solver", Language.SPANISH: "Motor"},
    "results.duration": {Language.ENGLISH: "Duration", Language.SPANISH: "Duración"},
    "results.fingerprint": {Language.ENGLISH: "Fingerprint", Language.SPANISH: "Huella"},
    "results.frequency_count": {Language.ENGLISH: "Frequencies", Language.SPANISH: "Frecuencias"},
    "results.gain_summary": {
        Language.ENGLISH: (
            "Power gain {gain} · Directivity {directivity} · Realized gain {realized}"
        ),
        Language.SPANISH: (
            "Ganancia de potencia {gain} · Directividad {directivity} · "
            "Ganancia realizada {realized}"
        ),
    },
    "results.link_summary": {
        Language.ENGLISH: (
            "Mismatch {mismatch} · line {line} · network {network} · balun {balun} "
            "at {frequency} MHz"
        ),
        Language.SPANISH: (
            "Desadaptación {mismatch} · línea {line} · red {network} · balun {balun} "
            "a {frequency} MHz"
        ),
    },
    "results.summary": {
        Language.ENGLISH: "{status} · {solver} {version} · {frequencies} frequencies · {duration:.3f} s · {fingerprint}",
        Language.SPANISH: "{status} · {solver} {version} · {frequencies} frecuencias · {duration:.3f} s · {fingerprint}",
    },
    "raw.input": {Language.ENGLISH: "Input deck", Language.SPANISH: "Deck de entrada"},
    "raw.output": {Language.ENGLISH: "Output", Language.SPANISH: "Salida"},
    "dialog.open_title": {
        Language.ENGLISH: "Open AntennaDesk project",
        Language.SPANISH: "Abrir proyecto AntennaDesk",
    },
    "dialog.save_title": {
        Language.ENGLISH: "Save AntennaDesk project",
        Language.SPANISH: "Guardar proyecto AntennaDesk",
    },
    "dialog.project_filter": {
        Language.ENGLISH: "AntennaDesk project (*.antennadesk);;All files (*)",
        Language.SPANISH: "Proyecto AntennaDesk (*.antennadesk);;Todos los archivos (*)",
    },
    "dialog.all_files": {
        Language.ENGLISH: "All files (*)",
        Language.SPANISH: "Todos los archivos (*)",
    },
    "dialog.solver_title": {
        Language.ENGLISH: "Select nec2c executable",
        Language.SPANISH: "Seleccionar el ejecutable nec2c",
    },
    "dialog.save_changes": {
        Language.ENGLISH: "Save changes before continuing?",
        Language.SPANISH: "¿Guardar los cambios antes de continuar?",
    },
    "error.invalid_design": {
        Language.ENGLISH: "Invalid design: {message}",
        Language.SPANISH: "Diseño inválido: {message}",
    },
    "error.open": {
        Language.ENGLISH: "Could not open project: {message}",
        Language.SPANISH: "No se pudo abrir el proyecto: {message}",
    },
    "error.save": {
        Language.ENGLISH: "Could not save project: {message}",
        Language.SPANISH: "No se pudo guardar el proyecto: {message}",
    },
    "error.no_project": {
        Language.ENGLISH: "No project is open.",
        Language.SPANISH: "No hay ningún proyecto abierto.",
    },
    "error.solver": {
        Language.ENGLISH: "The solver is not configured. Locate nec2c or set NEC2C.",
        Language.SPANISH: "El motor no está configurado. Ubicá nec2c o definí NEC2C.",
    },
    "error.simulation": {
        Language.ENGLISH: "Simulation failed: {message}",
        Language.SPANISH: "Simulación fallida: {message}",
    },
    "error.solver_start": {
        Language.ENGLISH: "The selected executable could not be started: {message}",
        Language.SPANISH: "No se pudo iniciar el ejecutable seleccionado: {message}",
    },
    "dialog.close_simulation": {
        Language.ENGLISH: "Cancel the running simulation before closing the window.",
        Language.SPANISH: "Cancelá la simulación en curso antes de cerrar la ventana.",
    },
    "wizard.title": {Language.ENGLISH: "New Antenna", Language.SPANISH: "Nueva antena"},
    "wizard.project_placeholder": {
        Language.ENGLISH: "40 m dipole",
        Language.SPANISH: "dipolo de 40 m",
    },
    "wizard.project_page": {Language.ENGLISH: "Frequency", Language.SPANISH: "Frecuencia"},
    "wizard.project_page_desc": {
        Language.ENGLISH: "Choose a project name, a band, or a custom frequency.",
        Language.SPANISH: "Elegí un nombre de proyecto, una banda o una frecuencia personalizada.",
    },
    "wizard.geometry_page": {Language.ENGLISH: "Geometry", Language.SPANISH: "Geometría"},
    "wizard.geometry_page_desc": {
        Language.ENGLISH: "Suggested dimensions are starting heuristics, not universal final values.",
        Language.SPANISH: "Las dimensiones sugeridas son heurísticas iniciales, no valores finales universales.",
    },
    "wizard.conductor_page": {Language.ENGLISH: "Conductor", Language.SPANISH: "Conductor"},
    "wizard.conductor_page_desc": {
        Language.ENGLISH: "Choose the wire material and diameter.",
        Language.SPANISH: "Elegí el material y el diámetro del hilo.",
    },
    "wizard.ground_page": {Language.ENGLISH: "Ground", Language.SPANISH: "Suelo"},
    "wizard.ground_page_desc": {
        Language.ENGLISH: "Choose the ground model used by the simulation.",
        Language.SPANISH: "Elegí el modelo de suelo usado por la simulación.",
    },
    "wizard.review_page": {Language.ENGLISH: "Review", Language.SPANISH: "Revisión"},
    "wizard.review_page_desc": {
        Language.ENGLISH: "Review the design. You can change it after creating it.",
        Language.SPANISH: "Revisá el diseño. Podés cambiarlo después de crearlo.",
    },
    "wizard.band": {Language.ENGLISH: "Band", Language.SPANISH: "Banda"},
    "wizard.custom": {Language.ENGLISH: "Custom", Language.SPANISH: "Personalizada"},
    "wizard.suggest_length": {
        Language.ENGLISH: "Suggest starting length",
        Language.SPANISH: "Sugerir longitud inicial",
    },
    "wizard.review": {
        Language.ENGLISH: "Project: {project}\nType: {type}\nFrequency: {frequency} MHz\n{primary_label}: {primary}\n{secondary_label}: {secondary}\n{height_label}: {height}\nAzimuth: {azimuth}°\nWire: {diameter} {material}\nGround: {ground}",
        Language.SPANISH: "Proyecto: {project}\nTipo: {type}\nFrecuencia: {frequency} MHz\n{primary_label}: {primary}\n{secondary_label}: {secondary}\n{height_label}: {height}\nAzimut: {azimuth}°\nHilo: {diameter} {material}\nSuelo: {ground}",
    },
    "unit.m": {Language.ENGLISH: "m", Language.SPANISH: "m"},
    "unit.ft": {Language.ENGLISH: "ft", Language.SPANISH: "ft"},
    "unit.mm": {Language.ENGLISH: "mm", Language.SPANISH: "mm"},
    "unit.in": {Language.ENGLISH: "in", Language.SPANISH: "in"},
}


class Translator:
    def __init__(self, language: Language = Language.ENGLISH) -> None:
        self._language = language

    @property
    def language(self) -> Language:
        return self._language

    def set_language(self, language: Language) -> None:
        self._language = language

    def t(self, key: str, **values: object) -> str:
        template = _TRANSLATIONS.get(key, {}).get(self._language)
        if template is None:
            return key
        return template.format(**values)
