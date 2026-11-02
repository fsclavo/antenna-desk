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
    "app.about": {
        Language.ENGLISH: "AntennaDesk {version} — GPL-3.0-or-later\nLocal-first antenna design and simulation.",
        Language.SPANISH: "AntennaDesk {version} — GPL-3.0-or-later\nDiseño y simulación de antenas local-first.",
    },
    "menu.file": {Language.ENGLISH: "File", Language.SPANISH: "Archivo"},
    "menu.import": {Language.ENGLISH: "Import", Language.SPANISH: "Importar"},
    "menu.export": {Language.ENGLISH: "Export", Language.SPANISH: "Exportar"},
    "menu.design": {Language.ENGLISH: "Design", Language.SPANISH: "Diseño"},
    "menu.variants": {Language.ENGLISH: "Variants", Language.SPANISH: "Variantes"},
    "menu.custom_wires": {
        Language.ENGLISH: "Custom Wires",
        Language.SPANISH: "Hilos personalizados",
    },
    "menu.simulation": {
        Language.ENGLISH: "Simulation",
        Language.SPANISH: "Simulación",
    },
    "menu.tools": {Language.ENGLISH: "Tools", Language.SPANISH: "Herramientas"},
    "menu.language": {Language.ENGLISH: "Language", Language.SPANISH: "Idioma"},
    "menu.help": {Language.ENGLISH: "Help", Language.SPANISH: "Ayuda"},
    "menu.units": {Language.ENGLISH: "Units", Language.SPANISH: "Unidades"},
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
        Language.ENGLISH: "Regular-polygon loop in a vertical plane.",
        Language.SPANISH: "Lazo poligonal regular en un plano vertical.",
    },
    "catalog.yagi": {Language.ENGLISH: "Yagi", Language.SPANISH: "Yagi"},
    "catalog.yagi.description": {
        Language.ENGLISH: "Editable multi-element Yagi with an NBS starting preset.",
        Language.SPANISH: "Yagi editable de múltiples elementos con preset inicial NBS.",
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
    "catalog.slim_jim": {
        Language.ENGLISH: "Slim Jim",
        Language.SPANISH: "Slim Jim",
    },
    "catalog.slim_jim.description": {
        Language.ENGLISH: "Folded rectangle with a gap in one vertical leg.",
        Language.SPANISH: "Rectángulo plegado con una brecha en una pata vertical.",
    },
    "catalog.endfed": {
        Language.ENGLISH: "End-fed wire",
        Language.SPANISH: "Hilo alimentado en el extremo",
    },
    "catalog.endfed.description": {
        Language.ENGLISH: "Single wire fed at one end, optionally sloping.",
        Language.SPANISH: "Hilo alimentado en un extremo, opcionalmente inclinado.",
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
        Language.ENGLISH: "Two-element rectangle with bent reflector and driven tips.",
        Language.SPANISH: "Rectángulo de dos elementos con reflector y puntas dobladas.",
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
    "catalog.vertical": {
        Language.ENGLISH: "Vertical + radials",
        Language.SPANISH: "Vertical + radiales",
    },
    "catalog.vertical.description": {
        Language.ENGLISH: "Vertical radiator with an optional radial ground plane.",
        Language.SPANISH: "Radiador vertical con plano de radiales opcional.",
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
    "action.exit": {Language.ENGLISH: "Exit", Language.SPANISH: "Salir"},
    "action.about": {
        Language.ENGLISH: "About AntennaDesk",
        Language.SPANISH: "Acerca de AntennaDesk",
    },
    "action.simulate": {Language.ENGLISH: "Simulate", Language.SPANISH: "Simular"},
    "action.cancel": {Language.ENGLISH: "Cancel", Language.SPANISH: "Cancelar"},
    "action.apply": {Language.ENGLISH: "Apply design", Language.SPANISH: "Aplicar diseño"},
    "action.next": {Language.ENGLISH: "Next", Language.SPANISH: "Siguiente"},
    "action.back": {Language.ENGLISH: "Back", Language.SPANISH: "Atrás"},
    "action.finish": {Language.ENGLISH: "Create", Language.SPANISH: "Crear"},
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
        Language.ENGLISH: "Design from frequency",
        Language.SPANISH: "Diseñar desde frecuencia",
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
        Language.ENGLISH: "Open an optimizer or synthesis dialog after applying",
        Language.SPANISH: "Abrir un optimizador o síntesis después de aplicar",
    },
    "design_from_frequency.hint": {
        Language.ENGLISH: "These are starting dimensions, not verified construction values. Apply them and refine with the existing optimizer or synthesis if needed.",
        Language.SPANISH: "Son dimensiones iniciales, no valores de construcción verificados. Aplicarlas y refinar con el optimizador o la síntesis existente si hace falta.",
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
        Language.ENGLISH: "ARRL Antenna Book — quarter-wave vertical",
        Language.SPANISH: "ARRL Antenna Book — vertical de cuarto de onda",
    },
    "source.nbs.tn688.five_element": {
        Language.ENGLISH: "NBS TN-688 — five-element Yagi",
        Language.SPANISH: "NBS TN-688 — Yagi de cinco elementos",
    },
    "source.cebik.moxon_review.table1": {
        Language.ENGLISH: "Cebik, W4RNL — Moxon review, Table 1",
        Language.SPANISH: "Cebik, W4RNL — revisión Moxon, Tabla 1",
    },
    "source.antennadesk.heuristic.application_preset": {
        Language.ENGLISH: "AntennaDesk application preset (heuristic)",
        Language.SPANISH: "Preset de aplicación de AntennaDesk (heurístico)",
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
        Language.ENGLISH: "the matching transformer and counterpoise are not included",
        Language.SPANISH: "no se incluye el transformador de adaptación ni el contrapeso",
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
    "estimator.warning.starting_point": {
        Language.ENGLISH: "starting point only; verify with simulation or measurement",
        Language.SPANISH: "solo punto de partida; verificar con simulación o medición",
    },
    "estimator.warning.folded_impedance": {
        Language.ENGLISH: "spacing strongly affects the step-up impedance",
        Language.SPANISH: "la separación afecta fuertemente la impedancia elevada",
    },
    "estimator.warning.vertical_matching": {
        Language.ENGLISH: "5/8-wave verticals need matching and a suitable radial system",
        Language.SPANISH: "las verticales de 5/8 necesitan adaptación y un sistema de radiales adecuado",
    },
    "estimator.warning.fan_interaction": {
        Language.ENGLISH: "fan elements interact; optimize the final lengths",
        Language.SPANISH: "los elementos del fan interactúan; optimizar las longitudes finales",
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
    "wizard.name_wire": {Language.ENGLISH: "dipole", Language.SPANISH: "dipolo"},
    "wizard.name_folded": {
        Language.ENGLISH: "folded dipole",
        Language.SPANISH: "dipolo plegado",
    },
    "wizard.name_loop": {Language.ENGLISH: "loop", Language.SPANISH: "lazo"},
    "field.height": {Language.ENGLISH: "Height", Language.SPANISH: "Altura"},
    "field.base_height": {Language.ENGLISH: "Base height", Language.SPANISH: "Altura de base"},
    "field.orientation": {Language.ENGLISH: "Orientation", Language.SPANISH: "Orientación"},
    "orientation.horizontal": {Language.ENGLISH: "Horizontal", Language.SPANISH: "Horizontal"},
    "orientation.vertical": {Language.ENGLISH: "Vertical", Language.SPANISH: "Vertical"},
    "field.azimuth": {Language.ENGLISH: "Azimuth (°)", Language.SPANISH: "Azimut (°)"},
    "field.diameter": {Language.ENGLISH: "Wire diameter", Language.SPANISH: "Diámetro del hilo"},
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
    "field.reference_impedance": {
        Language.ENGLISH: "Reference impedance (Ω)",
        Language.SPANISH: "Impedancia de referencia (Ω)",
    },
    "field.pattern_resolution": {
        Language.ENGLISH: "Pattern resolution",
        Language.SPANISH: "Resolución del patrón",
    },
    "field.pattern_points_label": {
        Language.ENGLISH: "Pattern points",
        Language.SPANISH: "Puntos de patrón",
    },
    "field.pattern_points": {
        Language.ENGLISH: "{count} pattern points",
        Language.SPANISH: "{count} puntos de patrón",
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
        Language.ENGLISH: "Estimated dimensions applied. Choose an optimization or synthesis tool to refine them.",
        Language.SPANISH: "Dimensiones estimadas aplicadas. Elegí un optimizador o síntesis para refinarlas.",
    },
    "status.cancelling": {Language.ENGLISH: "Cancelling...", Language.SPANISH: "Cancelando..."},
    "status.saved": {Language.ENGLISH: "Project saved.", Language.SPANISH: "Proyecto guardado."},
    "status.opened": {Language.ENGLISH: "Project opened.", Language.SPANISH: "Proyecto abierto."},
    "status.no_project": {
        Language.ENGLISH: "No project open.",
        Language.SPANISH: "No hay proyecto abierto.",
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
    "pattern.none": {
        Language.ENGLISH: "No far-field pattern available.",
        Language.SPANISH: "No hay patrón de campo lejano disponible.",
    },
    "pattern.polar": {
        Language.ENGLISH: "Elevation lobes",
        Language.SPANISH: "Lóbulos de elevación",
    },
    "currents.frequency": {Language.ENGLISH: "Frequency", Language.SPANISH: "Frecuencia"},
    "compare.title": {Language.ENGLISH: "Compare Variants", Language.SPANISH: "Comparar variantes"},
    "compare.variant_a": {Language.ENGLISH: "Variant A", Language.SPANISH: "Variante A"},
    "compare.variant_b": {Language.ENGLISH: "Variant B", Language.SPANISH: "Variante B"},
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
    "compare.efficiency": {Language.ENGLISH: "Efficiency (%)", Language.SPANISH: "Eficiencia (%)"},
    "compare.no_result": {
        Language.ENGLISH: "Simulate a variant to include it in the comparison.",
        Language.SPANISH: "Simulá una variante para incluirla en la comparación.",
    },
    "action.compare": {
        Language.ENGLISH: "Compare Variants...",
        Language.SPANISH: "Comparar variantes...",
    },
    "action.new_variant": {
        Language.ENGLISH: "New Variant...",
        Language.SPANISH: "Nueva variante...",
    },
    "action.rename_variant": {
        Language.ENGLISH: "Rename Variant...",
        Language.SPANISH: "Renombrar variante...",
    },
    "action.delete_variant": {
        Language.ENGLISH: "Delete Variant",
        Language.SPANISH: "Eliminar variante",
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
    "variant.label": {Language.ENGLISH: "Variant", Language.SPANISH: "Variante"},
    "variant.name": {Language.ENGLISH: "Variant name", Language.SPANISH: "Nombre de la variante"},
    "variant.new_title": {Language.ENGLISH: "New Variant", Language.SPANISH: "Nueva variante"},
    "variant.rename_title": {
        Language.ENGLISH: "Rename Variant",
        Language.SPANISH: "Renombrar variante",
    },
    "variant.delete_title": {
        Language.ENGLISH: "Delete Variant",
        Language.SPANISH: "Eliminar variante",
    },
    "variant.delete_confirm": {
        Language.ENGLISH: "Delete variant “{name}”?",
        Language.SPANISH: "¿Eliminar la variante “{name}”?",
    },
    "variant.last_cannot_delete": {
        Language.ENGLISH: "A project must keep at least one design variant.",
        Language.SPANISH: "Un proyecto debe conservar al menos una variante.",
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
        Language.ENGLISH: "Simulate the current variant before exporting.",
        Language.SPANISH: "Simulá la variante actual antes de exportar.",
    },
    "error.export": {
        Language.ENGLISH: "Could not export: {message}",
        Language.SPANISH: "No se pudo exportar: {message}",
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
        Language.ENGLISH: "Project is {size:.1f} MB and exceeds the 10 MB limit. Compact Simulation History or remove designs.",
        Language.SPANISH: "El proyecto pesa {size:.1f} MB y supera el límite de 10 MB. Compactá el historial o eliminá diseños.",
    },
    "dialog.compact_history": {
        Language.ENGLISH: "Remove older simulation runs? {count} runs will be reduced to the latest run per design ({keep} kept).",
        Language.SPANISH: "¿Eliminar corridas antiguas? {count} corridas se reducirán a la última por diseño ({keep} conservadas).",
    },
    "dialog.construction_title": {
        Language.ENGLISH: "Save construction sheet",
        Language.SPANISH: "Guardar hoja de construcción",
    },
    "custom.title": {
        Language.ENGLISH: "Custom wire antenna",
        Language.SPANISH: "Antena de hilos personalizada",
    },
    "yagi.title": {
        Language.ENGLISH: "Yagi Generator",
        Language.SPANISH: "Generador de Yagi",
    },
    "inverted_v.title": {
        Language.ENGLISH: "Inverted-V Generator",
        Language.SPANISH: "Generador de V invertida",
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
            "Experimental generator: geometry is tested, but there is no "
            "independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueba la geometría, pero no hay una "
            "referencia numérica independiente para esta configuración."
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
    "endfed.title": {
        Language.ENGLISH: "End-Fed Wire Generator",
        Language.SPANISH: "Generador de hilo alimentado en el extremo",
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
        Language.ENGLISH: "Feed {feed} {unit} · end {end} {unit}",
        Language.SPANISH: "Alimentación {feed} {unit} · extremo {end} {unit}",
    },
    "endfed.hint": {
        Language.ENGLISH: (
            "The wire is fed at one end. The generated antenna is an editable first-class design."
        ),
        Language.SPANISH: (
            "El hilo se alimenta en un extremo. La antena generada es un diseño "
            "editable de primera clase."
        ),
    },
    "endfed.evidence": {
        Language.ENGLISH: (
            "Experimental generator: geometry is tested, but there is no "
            "independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueba la geometría, pero no hay una "
            "referencia numérica independiente para esta configuración."
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
    "moxon.hint": {
        Language.ENGLISH: (
            "The generator creates a reflector and driven element with bent tips. "
            "The generated antenna is an editable first-class design."
        ),
        Language.SPANISH: (
            "El generador crea un reflector y un elemento alimentado con puntas "
            "dobladas. La antena generada es un diseño editable de primera clase."
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
    "yagi.radius_mm": {
        Language.ENGLISH: "Element radius (mm)",
        Language.SPANISH: "Radio del elemento (mm)",
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
        Language.ENGLISH: "Element dimensions do not match the current frequency. Change the frequency from a known design or use Design from Frequency to rebuild the Yagi.",
        Language.SPANISH: "Las dimensiones de los elementos no coinciden con la frecuencia actual. Cambiá la frecuencia desde un diseño conocido o usá Diseñar desde frecuencia para regenerar la Yagi.",
    },
    "yagi.geometry": {
        Language.ENGLISH: "{count} elements · boom {boom} {unit}",
        Language.SPANISH: "{count} elementos · boom {boom} {unit}",
    },
    "yagi.hint": {
        Language.ENGLISH: (
            "Positions and lengths are editable. The generated antenna is an "
            "editable custom-wire design."
        ),
        Language.SPANISH: (
            "Las posiciones y longitudes son editables. La antena generada es "
            "un diseño de hilos personalizado editable."
        ),
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
        Language.ENGLISH: "Selected dimensions change together. The target is evaluated at one frequency; verify the applied design with a full simulation.",
        Language.SPANISH: "Las dimensiones seleccionadas cambian juntas. El objetivo se evalúa en una frecuencia; verificá el diseño aplicado con una simulación completa.",
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
        Language.ENGLISH: "Use",
        Language.SPANISH: "Usar",
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
            "reference."
        ),
        Language.SPANISH: (
            "Preset NBS TN-688: 5 elementos, 0.8 longitud de onda, ganancia de "
            "referencia 9.2 dBd. Las geometrías modificadas son experimentales y "
            "no tienen referencia externa."
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
    "custom.radius": {Language.ENGLISH: "Radius (mm)", Language.SPANISH: "Radio (mm)"},
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
    "loads.title": {
        Language.ENGLISH: "Series Loads",
        Language.SPANISH: "Cargas en serie",
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
    "optimize_status.converged": {
        Language.ENGLISH: "converged",
        Language.SPANISH: "convergió",
    },
    "optimize_status.max_evaluations": {
        Language.ENGLISH: "maximum evaluations reached",
        Language.SPANISH: "máximo de evaluaciones alcanzado",
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
