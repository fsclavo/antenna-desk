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
        Language.ENGLISH: "AntennaDesk — GPL-3.0-or-later\nLocal-first antenna design and simulation.",
        Language.SPANISH: "AntennaDesk — GPL-3.0-or-later\nDiseño y simulación de antenas local-first.",
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
        Language.ENGLISH: "Slim Jim · radiator {radiator} · stub {stub} · gap {gap} · spacing {spacing}",
        Language.SPANISH: "Slim Jim · radiador {radiator} · stub {stub} · brecha {gap} · separación {spacing}",
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
    "dialog.geometry_png_title": {
        Language.ENGLISH: "Save geometry image",
        Language.SPANISH: "Guardar imagen de geometría",
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
        Language.ENGLISH: "Optimize Dimension...",
        Language.SPANISH: "Optimizar dimensión...",
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
            "Experimental generator: geometry is tested, but there is no "
            "independent numerical reference for this configuration."
        ),
        Language.SPANISH: (
            "Generador experimental: se prueba la geometría, pero no hay una "
            "referencia numérica independiente para esta configuración."
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
    "optimize.max_evaluations": {
        Language.ENGLISH: "Maximum evaluations",
        Language.SPANISH: "Evaluaciones máximas",
    },
    "optimize.tolerance": {
        Language.ENGLISH: "Reactance tolerance (Ω)",
        Language.SPANISH: "Tolerancia de reactancia (Ω)",
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
