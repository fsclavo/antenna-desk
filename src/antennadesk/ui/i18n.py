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
    "menu.language": {Language.ENGLISH: "Language", Language.SPANISH: "Idioma"},
    "menu.help": {Language.ENGLISH: "Help", Language.SPANISH: "Ayuda"},
    "menu.units": {Language.ENGLISH: "Units", Language.SPANISH: "Unidades"},
    "action.new": {Language.ENGLISH: "New Dipole...", Language.SPANISH: "Nuevo dipolo..."},
    "action.open": {Language.ENGLISH: "Open Project...", Language.SPANISH: "Abrir proyecto..."},
    "action.save": {Language.ENGLISH: "Save", Language.SPANISH: "Guardar"},
    "action.save_as": {Language.ENGLISH: "Save As...", Language.SPANISH: "Guardar como..."},
    "action.locate_solver": {
        Language.ENGLISH: "Locate NEC2C...",
        Language.SPANISH: "Ubicar NEC2C...",
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
    "geometry.view": {Language.ENGLISH: "View", Language.SPANISH: "Vista"},
    "geometry.view_elevation": {Language.ENGLISH: "Elevation", Language.SPANISH: "Alzado"},
    "geometry.view_plan": {Language.ENGLISH: "Plan", Language.SPANISH: "Planta"},
    "geometry.vertical_scale": {
        Language.ENGLISH: "Vertical scale",
        Language.SPANISH: "Escala vertical",
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
    "tab.diagnostics": {Language.ENGLISH: "Diagnostics", Language.SPANISH: "Diagnósticos"},
    "tab.raw": {Language.ENGLISH: "Raw data", Language.SPANISH: "Datos crudos"},
    "table.frequency": {Language.ENGLISH: "Frequency (MHz)", Language.SPANISH: "Frecuencia (MHz)"},
    "table.resistance": {Language.ENGLISH: "R (Ω)", Language.SPANISH: "R (Ω)"},
    "table.reactance": {Language.ENGLISH: "X (Ω)", Language.SPANISH: "X (Ω)"},
    "table.impedance": {Language.ENGLISH: "|Z| (Ω)", Language.SPANISH: "|Z| (Ω)"},
    "table.swr": {Language.ENGLISH: "SWR", Language.SPANISH: "ROE"},
    "pattern.frequency": {Language.ENGLISH: "Frequency", Language.SPANISH: "Frecuencia"},
    "pattern.elevation": {Language.ENGLISH: "Elevation θ (°)", Language.SPANISH: "Elevación θ (°)"},
    "pattern.gain": {
        Language.ENGLISH: "Power gain (dBi)",
        Language.SPANISH: "Ganancia de potencia (dBi)",
    },
    "pattern.none": {
        Language.ENGLISH: "No far-field pattern available.",
        Language.SPANISH: "No hay patrón de campo lejano disponible.",
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
    "action.export_html": {
        Language.ENGLISH: "Export HTML Report...",
        Language.SPANISH: "Exportar informe HTML...",
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
    "dialog.csv_title": {
        Language.ENGLISH: "Export simulation CSV",
        Language.SPANISH: "Exportar CSV de simulación",
    },
    "dialog.html_title": {
        Language.ENGLISH: "Export HTML report",
        Language.SPANISH: "Exportar informe HTML",
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
        Language.ENGLISH: "Optimize Length...",
        Language.SPANISH: "Optimizar longitud...",
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
    "dialog.construction_title": {
        Language.ENGLISH: "Save construction sheet",
        Language.SPANISH: "Guardar hoja de construcción",
    },
    "optimize.title": {
        Language.ENGLISH: "Optimize Dipole Length",
        Language.SPANISH: "Optimizar longitud del dipolo",
    },
    "optimize.min_length": {
        Language.ENGLISH: "Minimum length",
        Language.SPANISH: "Longitud mínima",
    },
    "optimize.max_length": {
        Language.ENGLISH: "Maximum length",
        Language.SPANISH: "Longitud máxima",
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
    "optimize.run": {
        Language.ENGLISH: "Run optimization",
        Language.SPANISH: "Ejecutar optimización",
    },
    "optimize.cancel_run": {
        Language.ENGLISH: "Cancel optimization",
        Language.SPANISH: "Cancelar optimización",
    },
    "optimize.apply": {
        Language.ENGLISH: "Apply best length",
        Language.SPANISH: "Aplicar longitud óptima",
    },
    "optimize.running": {
        Language.ENGLISH: "Running optimization...",
        Language.SPANISH: "Ejecutando optimización...",
    },
    "optimize.summary": {
        Language.ENGLISH: "Status: {status} · Best length: {length} · X={reactance} Ω · SWR={swr}",
        Language.SPANISH: "Estado: {status} · Mejor longitud: {length} · X={reactance} Ω · ROE={swr}",
    },
    "optimize.no_best": {
        Language.ENGLISH: "No valid length was found.",
        Language.SPANISH: "No se encontró una longitud válida.",
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
    "optimize.length": {Language.ENGLISH: "Length", Language.SPANISH: "Longitud"},
    "optimize.offset": {Language.ENGLISH: "Offset", Language.SPANISH: "Desvío"},
    "optimize.message": {Language.ENGLISH: "Message", Language.SPANISH: "Mensaje"},
    "optimize.apply_hint": {
        Language.ENGLISH: "Apply the best length and simulate to validate the full sweep.",
        Language.SPANISH: "Aplicá la mejor longitud y simulá para validar el barrido completo.",
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
    "wizard.title": {Language.ENGLISH: "New Dipole", Language.SPANISH: "Nuevo dipolo"},
    "wizard.project_page": {Language.ENGLISH: "Frequency", Language.SPANISH: "Frecuencia"},
    "wizard.project_page_desc": {
        Language.ENGLISH: "Choose a project name, a band, or a custom frequency.",
        Language.SPANISH: "Elegí un nombre de proyecto, una banda o una frecuencia personalizada.",
    },
    "wizard.geometry_page": {Language.ENGLISH: "Geometry", Language.SPANISH: "Geometría"},
    "wizard.geometry_page_desc": {
        Language.ENGLISH: "The initial length is a half-wave approximation, not a universal final length.",
        Language.SPANISH: "La longitud inicial es una aproximación de media onda, no una longitud final universal.",
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
        Language.ENGLISH: "Suggest half-wave length",
        Language.SPANISH: "Sugerir longitud de media onda",
    },
    "wizard.review": {
        Language.ENGLISH: "Project: {project}\nFrequency: {frequency} MHz\nLength: {length}\nHeight: {height}\nAzimuth: {azimuth}°\nWire: {diameter} {material}\nGround: {ground}",
        Language.SPANISH: "Proyecto: {project}\nFrecuencia: {frequency} MHz\nLongitud: {length}\nAltura: {height}\nAzimut: {azimuth}°\nHilo: {diameter} {material}\nSuelo: {ground}",
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
