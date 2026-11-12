# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Small English/Spanish translation layer for the Phase 3 UI."""

from __future__ import annotations

from enum import StrEnum

from .evidence_i18n import EVIDENCE_SPANISH
from .report_i18n import REPORT_SPANISH


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
    "workflow.mode_label": {
        Language.ENGLISH: "Mode",
        Language.SPANISH: "Modo",
    },
    "workflow.mode.guided": {
        Language.ENGLISH: "Guided",
        Language.SPANISH: "Guiado",
    },
    "workflow.mode.standard": {
        Language.ENGLISH: "Standard",
        Language.SPANISH: "Estándar",
    },
    "workflow.mode.advanced": {
        Language.ENGLISH: "Advanced",
        Language.SPANISH: "Avanzado",
    },
    "workflow.panel_title": {
        Language.ENGLISH: "Next step",
        Language.SPANISH: "Próximo paso",
    },
    "workflow.show_advanced": {
        Language.ENGLISH: "Show advanced options",
        Language.SPANISH: "Mostrar opciones avanzadas",
    },
    "workflow.next.create_project.title": {
        Language.ENGLISH: "Start a project",
        Language.SPANISH: "Iniciá un proyecto",
    },
    "workflow.next.create_project.body": {
        Language.ENGLISH: ("Create an antenna from the catalog or open an existing project."),
        Language.SPANISH: ("Creá una antena desde el catálogo o abrí un proyecto existente."),
    },
    "workflow.next.create_project.action": {
        Language.ENGLISH: "New Antenna...",
        Language.SPANISH: "Nueva antena...",
    },
    "workflow.next.configure_solver.title": {
        Language.ENGLISH: "Configure the solver",
        Language.SPANISH: "Configurá el solver",
    },
    "workflow.next.configure_solver.body": {
        Language.ENGLISH: (
            "AntennaDesk needs nec2c to simulate. Locate the executable and "
            "then return to this design."
        ),
        Language.SPANISH: (
            "AntennaDesk necesita nec2c para simular. Ubicá el ejecutable y volvé a este diseño."
        ),
    },
    "workflow.next.configure_solver.action": {
        Language.ENGLISH: "Locate solver...",
        Language.SPANISH: "Ubicar solver...",
    },
    "workflow.next.simulate.title": {
        Language.ENGLISH: "Simulate the design",
        Language.SPANISH: "Simulá el diseño",
    },
    "workflow.next.simulate.body": {
        Language.ENGLISH: (
            "Run the solver to get impedance, SWR, gain, and the radiation pattern."
        ),
        Language.SPANISH: (
            "Ejecutá el solver para obtener impedancia, ROE, ganancia y patrón de radiación."
        ),
    },
    "workflow.next.simulate.action": {
        Language.ENGLISH: "Simulate",
        Language.SPANISH: "Simular",
    },
    "workflow.next.review_diagnostics.title": {
        Language.ENGLISH: "Review the diagnostics",
        Language.SPANISH: "Revisá los diagnósticos",
    },
    "workflow.next.review_diagnostics.body": {
        Language.ENGLISH: (
            "The last run finished with warnings or errors. Check the diagnostics "
            "before building or comparing."
        ),
        Language.SPANISH: (
            "La última corrida terminó con advertencias o errores. Revisá los "
            "diagnósticos antes de construir o comparar."
        ),
    },
    "workflow.next.review_diagnostics.action": {
        Language.ENGLISH: "View diagnostics",
        Language.SPANISH: "Ver diagnósticos",
    },
    "workflow.next.review_swr.title": {
        Language.ENGLISH: "Review the match",
        Language.SPANISH: "Revisá la adaptación",
    },
    "workflow.next.review_swr.body": {
        Language.ENGLISH: (
            "The SWR at the design frequency is above 2:1. Inspect the impedance "
            "and consider a matching network, a length adjustment, or a different "
            "feed point."
        ),
        Language.SPANISH: (
            "La ROE en la frecuencia de diseño supera 2:1. Revisá la impedancia y "
            "considerá una red de adaptación, un ajuste de longitud u otro punto "
            "de alimentación."
        ),
    },
    "workflow.next.review_swr.action": {
        Language.ENGLISH: "Review impedance",
        Language.SPANISH: "Revisar impedancia",
    },
    "workflow.next.build_sheet.title": {
        Language.ENGLISH: "Prepare the construction sheet",
        Language.SPANISH: "Prepará la hoja de construcción",
    },
    "workflow.next.build_sheet.body": {
        Language.ENGLISH: (
            "The design is simulated. Generate the construction sheet to check "
            "dimensions, the wire schedule, and the bill of materials."
        ),
        Language.SPANISH: (
            "El diseño está simulado. Generá la hoja de construcción para revisar "
            "dimensiones, el listado de hilos y la lista de materiales."
        ),
    },
    "workflow.next.build_sheet.action": {
        Language.ENGLISH: "Open construction sheet",
        Language.SPANISH: "Abrir hoja de construcción",
    },
    "workflow.next.measure.title": {
        Language.ENGLISH: "Measure the built antenna",
        Language.SPANISH: "Medí la antena construida",
    },
    "workflow.next.measure.body": {
        Language.ENGLISH: (
            "Import a NanoVNA CSV to compare the real antenna with the model. "
            "This closes the design loop."
        ),
        Language.SPANISH: (
            "Importá un CSV del NanoVNA para comparar la antena real con el modelo. "
            "Así cerrás el ciclo de diseño."
        ),
    },
    "workflow.next.measure.action": {
        Language.ENGLISH: "Import VNA CSV...",
        Language.SPANISH: "Importar CSV de VNA...",
    },
    "workflow.next.compare_measurement.title": {
        Language.ENGLISH: "Compare measured and simulated",
        Language.SPANISH: "Compará medido y simulado",
    },
    "workflow.next.compare_measurement.body": {
        Language.ENGLISH: (
            "Open the Measurements tab to compare SWR, R, X, and resonance with the simulation."
        ),
        Language.SPANISH: (
            "Abrí la pestaña Mediciones para comparar ROE, R, X y resonancia con la simulación."
        ),
    },
    "workflow.next.compare_measurement.action": {
        Language.ENGLISH: "Compare measurement",
        Language.SPANISH: "Comparar medición",
    },
    "workflow.next.complete.title": {
        Language.ENGLISH: "Design loop complete",
        Language.SPANISH: "Ciclo de diseño completo",
    },
    "workflow.next.complete.body": {
        Language.ENGLISH: (
            "You have a simulated design, a construction sheet, and a measurement "
            "comparison. Export the report or start another design."
        ),
        Language.SPANISH: (
            "Tenés un diseño simulado, una hoja de construcción y una comparación "
            "de mediciones. Exportá el informe o empezá otro diseño."
        ),
    },
    "workflow.next.complete.action": {
        Language.ENGLISH: "Export PDF report",
        Language.SPANISH: "Exportar informe PDF",
    },
    "installation.title": {
        Language.ENGLISH: "Installation profiles",
        Language.SPANISH: "Perfiles de instalación",
    },
    "installation.hint": {
        Language.ENGLISH: (
            "Describe the site envelope and constraints. Profiles are metadata: "
            "they do not change the antenna model by themselves."
        ),
        Language.SPANISH: (
            "Describí el entorno y las restricciones del sitio. Los perfiles son "
            "metadatos: no cambian el modelo de antena por sí solos."
        ),
    },
    "installation.profiles": {
        Language.ENGLISH: "Saved installation profiles",
        Language.SPANISH: "Perfiles de instalación guardados",
    },
    "installation.name": {
        Language.ENGLISH: "Profile name",
        Language.SPANISH: "Nombre del perfil",
    },
    "installation.available_height": {
        Language.ENGLISH: "Available height",
        Language.SPANISH: "Altura disponible",
    },
    "installation.available_width": {
        Language.ENGLISH: "Available horizontal space",
        Language.SPANISH: "Espacio horizontal disponible",
    },
    "installation.orientation": {
        Language.ENGLISH: "Orientation",
        Language.SPANISH: "Orientación",
    },
    "installation.support": {
        Language.ENGLISH: "Support",
        Language.SPANISH: "Soporte",
    },
    "installation.ground": {
        Language.ENGLISH: "Ground preset",
        Language.SPANISH: "Suelo de referencia",
    },
    "installation.notes": {
        Language.ENGLISH: "Notes",
        Language.SPANISH: "Notas",
    },
    "installation.notes_placeholder": {
        Language.ENGLISH: "Roof, tree, mast, restrictions, access, and other site notes.",
        Language.SPANISH: "Techo, árbol, mástil, restricciones, acceso y otras notas del sitio.",
    },
    "installation.image_reference": {
        Language.ENGLISH: "Image reference",
        Language.SPANISH: "Referencia de imagen",
    },
    "installation.add": {
        Language.ENGLISH: "Add",
        Language.SPANISH: "Agregar",
    },
    "installation.duplicate": {
        Language.ENGLISH: "Duplicate",
        Language.SPANISH: "Duplicar",
    },
    "installation.remove": {
        Language.ENGLISH: "Remove",
        Language.SPANISH: "Quitar",
    },
    "installation.edit": {
        Language.ENGLISH: "Edit profile...",
        Language.SPANISH: "Editar perfil...",
    },
    "installation.browse": {
        Language.ENGLISH: "Browse...",
        Language.SPANISH: "Examinar...",
    },
    "installation.default_name": {
        Language.ENGLISH: "Site {index}",
        Language.SPANISH: "Sitio {index}",
    },
    "installation.copy_name": {
        Language.ENGLISH: "{name} copy",
        Language.SPANISH: "{name} (copia)",
    },
    "installation.active_note": {
        Language.ENGLISH: "The selected profile is the active one.",
        Language.SPANISH: "El perfil seleccionado es el activo.",
    },
    "installation.not_set": {
        Language.ENGLISH: "Not specified",
        Language.SPANISH: "Sin especificar",
    },
    "installation.none": {
        Language.ENGLISH: "No installation profile",
        Language.SPANISH: "Sin perfil de instalación",
    },
    "installation.none_hint": {
        Language.ENGLISH: (
            "Add a profile to record the available height, space, orientation, support, and ground."
        ),
        Language.SPANISH: (
            "Agregá un perfil para registrar la altura, el espacio, la orientación, "
            "el soporte y el suelo disponibles."
        ),
    },
    "installation.duplicate_name": {
        Language.ENGLISH: "Profile names must be unique.",
        Language.SPANISH: "Los nombres de perfil deben ser únicos.",
    },
    "installation.no_selection": {
        Language.ENGLISH: "Select an installation profile first.",
        Language.SPANISH: "Seleccioná primero un perfil de instalación.",
    },
    "installation.ground_none": {
        Language.ENGLISH: "Not specified",
        Language.SPANISH: "Sin especificar",
    },
    "installation.ground_free_space": {
        Language.ENGLISH: "Free space",
        Language.SPANISH: "Espacio libre",
    },
    "installation.ground_perfect": {
        Language.ENGLISH: "Perfect ground",
        Language.SPANISH: "Plano perfecto",
    },
    "installation.ground_custom": {
        Language.ENGLISH: "Custom / not listed",
        Language.SPANISH: "Personalizado / no listado",
    },
    "installation.ground_custom_value": {
        Language.ENGLISH: "Custom (eps_r={permittivity}, sigma={conductivity} S/m)",
        Language.SPANISH: "Personalizado (eps_r={permittivity}, sigma={conductivity} S/m)",
    },
    "installation.image_title": {
        Language.ENGLISH: "Select an installation image",
        Language.SPANISH: "Seleccionar una imagen de instalación",
    },
    "installation.image_filter": {
        Language.ENGLISH: "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        Language.SPANISH: "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)",
    },
    "installation.support.mast": {
        Language.ENGLISH: "Mast",
        Language.SPANISH: "Mástil",
    },
    "installation.support.tree": {
        Language.ENGLISH: "Tree",
        Language.SPANISH: "Árbol",
    },
    "installation.support.building": {
        Language.ENGLISH: "Building",
        Language.SPANISH: "Edificio",
    },
    "installation.support.fence": {
        Language.ENGLISH: "Fence",
        Language.SPANISH: "Cerca",
    },
    "installation.support.portable": {
        Language.ENGLISH: "Portable",
        Language.SPANISH: "Portátil",
    },
    "installation.support.other": {
        Language.ENGLISH: "Other",
        Language.SPANISH: "Otro",
    },
    "advisor.title": {
        Language.ENGLISH: "Antenna advisor",
        Language.SPANISH: "Asesor de antenas",
    },
    "advisor.hint": {
        Language.ENGLISH: (
            "Describe your bands and site. The advisor applies hard constraints "
            "and shows up to three practical alternatives. It does not simulate "
            "every candidate; open one to refine it with the solver."
        ),
        Language.SPANISH: (
            "Describí tus bandas y tu sitio. El asesor aplica restricciones duras "
            "y muestra hasta tres alternativas prácticas. No simula todos los "
            "candidatos; abrí uno para refinarlo con el solver."
        ),
    },
    "advisor.criteria": {
        Language.ENGLISH: "Your constraints",
        Language.SPANISH: "Tus restricciones",
    },
    "advisor.bands": {
        Language.ENGLISH: "Bands",
        Language.SPANISH: "Bandas",
    },
    "advisor.height": {
        Language.ENGLISH: "Available height",
        Language.SPANISH: "Altura disponible",
    },
    "advisor.width": {
        Language.ENGLISH: "Available horizontal space",
        Language.SPANISH: "Espacio horizontal disponible",
    },
    "advisor.not_set": {
        Language.ENGLISH: "Not specified",
        Language.SPANISH: "Sin especificar",
    },
    "advisor.installation": {
        Language.ENGLISH: "Installation",
        Language.SPANISH: "Instalación",
    },
    "advisor.permanent": {
        Language.ENGLISH: "Permanent",
        Language.SPANISH: "Permanente",
    },
    "advisor.portable": {
        Language.ENGLISH: "Portable",
        Language.SPANISH: "Portátil",
    },
    "advisor.intent": {
        Language.ENGLISH: "Main use",
        Language.SPANISH: "Uso principal",
    },
    "advisor.intent.nvis": {
        Language.ENGLISH: "NVIS / local",
        Language.SPANISH: "NVIS / local",
    },
    "advisor.intent.regional": {
        Language.ENGLISH: "Regional",
        Language.SPANISH: "Regional",
    },
    "advisor.intent.dx": {
        Language.ENGLISH: "DX",
        Language.SPANISH: "DX",
    },
    "advisor.intent.receive": {
        Language.ENGLISH: "Receive only",
        Language.SPANISH: "Solo recepción",
    },
    "advisor.tuner": {
        Language.ENGLISH: "I have an antenna tuner",
        Language.SPANISH: "Tengo un sintonizador de antena",
    },
    "advisor.complexity": {
        Language.ENGLISH: "Maximum construction effort",
        Language.SPANISH: "Esfuerzo máximo de construcción",
    },
    "advisor.complexity.simple": {
        Language.ENGLISH: "Simple",
        Language.SPANISH: "Simple",
    },
    "advisor.complexity.moderate": {
        Language.ENGLISH: "Moderate",
        Language.SPANISH: "Moderado",
    },
    "advisor.complexity.advanced": {
        Language.ENGLISH: "Advanced",
        Language.SPANISH: "Avanzado",
    },
    "advisor.directionality": {
        Language.ENGLISH: "Pattern preference",
        Language.SPANISH: "Preferencia de patrón",
    },
    "advisor.directionality.any": {
        Language.ENGLISH: "No preference",
        Language.SPANISH: "Sin preferencia",
    },
    "advisor.directionality.omni": {
        Language.ENGLISH: "Omnidirectional",
        Language.SPANISH: "Omnidireccional",
    },
    "advisor.directionality.directional": {
        Language.ENGLISH: "Directional",
        Language.SPANISH: "Direccional",
    },
    "advisor.multiband": {
        Language.ENGLISH: "One antenna should cover all selected bands",
        Language.SPANISH: "Una sola antena debe cubrir todas las bandas seleccionadas",
    },
    "advisor.find": {
        Language.ENGLISH: "Find antennas",
        Language.SPANISH: "Buscar antenas",
    },
    "advisor.results": {
        Language.ENGLISH: "Top matches",
        Language.SPANISH: "Mejores coincidencias",
    },
    "advisor.table.antenna": {
        Language.ENGLISH: "Antenna",
        Language.SPANISH: "Antena",
    },
    "advisor.table.fit": {
        Language.ENGLISH: "Fit",
        Language.SPANISH: "Encaje",
    },
    "advisor.table.bands": {
        Language.ENGLISH: "Bands",
        Language.SPANISH: "Bandas",
    },
    "advisor.table.space": {
        Language.ENGLISH: "Typical space",
        Language.SPANISH: "Espacio típico",
    },
    "advisor.table.height": {
        Language.ENGLISH: "Minimum height",
        Language.SPANISH: "Altura mínima",
    },
    "advisor.table.feed": {
        Language.ENGLISH: "Feed",
        Language.SPANISH: "Alimentación",
    },
    "advisor.table.complexity": {
        Language.ENGLISH: "Build",
        Language.SPANISH: "Construcción",
    },
    "advisor.open": {
        Language.ENGLISH: "Open selected design",
        Language.SPANISH: "Abrir diseño seleccionado",
    },
    "advisor.no_bands": {
        Language.ENGLISH: "Select at least one band.",
        Language.SPANISH: "Seleccioná al menos una banda.",
    },
    "advisor.no_match": {
        Language.ENGLISH: (
            "No catalog antenna fits all hard constraints. Try allowing a tuner, "
            "more space or height, fewer bands, or a simpler build."
        ),
        Language.SPANISH: (
            "Ninguna antena del catálogo cumple todas las restricciones duras. "
            "Probá permitir un sintonizador, más espacio o altura, menos bandas "
            "o una construcción más simple."
        ),
    },
    "advisor.blockers": {
        Language.ENGLISH: "Constraints that blocked candidates:",
        Language.SPANISH: "Restricciones que bloquearon candidatos:",
    },
    "advisor.blocker.bands": {
        Language.ENGLISH: "band coverage",
        Language.SPANISH: "cobertura de bandas",
    },
    "advisor.blocker.space": {
        Language.ENGLISH: "available space",
        Language.SPANISH: "espacio disponible",
    },
    "advisor.blocker.height": {
        Language.ENGLISH: "available height",
        Language.SPANISH: "altura disponible",
    },
    "advisor.blocker.portable": {
        Language.ENGLISH: "portable installation",
        Language.SPANISH: "instalación portátil",
    },
    "advisor.blocker.tuner": {
        Language.ENGLISH: "tuner required",
        Language.SPANISH: "sintonizador requerido",
    },
    "advisor.blocker.complexity": {
        Language.ENGLISH: "construction effort",
        Language.SPANISH: "esfuerzo de construcción",
    },
    "advisor.blocker.pattern": {
        Language.ENGLISH: "pattern preference",
        Language.SPANISH: "preferencia de patrón",
    },
    "advisor.fit.excellent": {
        Language.ENGLISH: "Excellent fit",
        Language.SPANISH: "Encaje excelente",
    },
    "advisor.fit.good": {
        Language.ENGLISH: "Good fit",
        Language.SPANISH: "Buen encaje",
    },
    "advisor.fit.conditional": {
        Language.ENGLISH: "Conditional",
        Language.SPANISH: "Condicional",
    },
    "advisor.feed.direct": {
        Language.ENGLISH: "Direct 50 Ω",
        Language.SPANISH: "Directa 50 Ω",
    },
    "advisor.feed.tuner": {
        Language.ENGLISH: "Tuner",
        Language.SPANISH: "Sintonizador",
    },
    "advisor.feed.transformer": {
        Language.ENGLISH: "Transformer",
        Language.SPANISH: "Transformador",
    },
    "advisor.feed.matching": {
        Language.ENGLISH: "Matching network",
        Language.SPANISH: "Red de adaptación",
    },
    "advisor.reason.covers_requested_bands": {
        Language.ENGLISH: "Covers all selected bands",
        Language.SPANISH: "Cubre todas las bandas seleccionadas",
    },
    "advisor.reason.covers_a_requested_band": {
        Language.ENGLISH: "Covers a selected band",
        Language.SPANISH: "Cubre una banda seleccionada",
    },
    "advisor.reason.fits_available_space": {
        Language.ENGLISH: "Fits the available space",
        Language.SPANISH: "Entra en el espacio disponible",
    },
    "advisor.reason.fits_available_height": {
        Language.ENGLISH: "Fits the available height",
        Language.SPANISH: "Entra en la altura disponible",
    },
    "advisor.reason.portable_supported": {
        Language.ENGLISH: "Suitable for portable use",
        Language.SPANISH: "Apta para uso portátil",
    },
    "advisor.reason.no_tuner_required": {
        Language.ENGLISH: "No tuner required",
        Language.SPANISH: "No requiere sintonizador",
    },
    "advisor.reason.tuner_optional": {
        Language.ENGLISH: "Tuner optional",
        Language.SPANISH: "Sintonizador opcional",
    },
    "advisor.reason.tuner_required": {
        Language.ENGLISH: "Tuner required",
        Language.SPANISH: "Requiere sintonizador",
    },
    "advisor.warning.height_below_recommended": {
        Language.ENGLISH: "Below the recommended height; the pattern may change.",
        Language.SPANISH: "Por debajo de la altura recomendada; el patrón puede cambiar.",
    },
    "advisor.warning.needs_tuner": {
        Language.ENGLISH: "Needs a tuner on at least some bands.",
        Language.SPANISH: "Necesita sintonizador en algunas bandas.",
    },
    "advisor.warning.intent_mismatch": {
        Language.ENGLISH: "Not the strongest match for the selected use.",
        Language.SPANISH: "No es la mejor opción para el uso seleccionado.",
    },
    "advisor.warning.space_tight": {
        Language.ENGLISH: "Fits, but with little clearance.",
        Language.SPANISH: "Entra, pero con poco margen.",
    },
    "advisor.warning.experimental_starting_point": {
        Language.ENGLISH: "Experimental starting point; verify with the solver.",
        Language.SPANISH: "Punto de partida experimental; verificá con el solver.",
    },
    "advisor.details.typical": {
        Language.ENGLISH: "Typical: gain {gain} · takeoff {takeoff} · bandwidth {bandwidth}",
        Language.SPANISH: "Típico: ganancia {gain} · salida {takeoff} · ancho de banda {bandwidth}",
    },
    "advisor.details.evidence": {
        Language.ENGLISH: "Evidence: {value}",
        Language.SPANISH: "Evidencia: {value}",
    },
    "advisor.details.reasons": {
        Language.ENGLISH: "Why it fits:",
        Language.SPANISH: "Por qué encaja:",
    },
    "advisor.details.warnings": {
        Language.ENGLISH: "Watch out:",
        Language.SPANISH: "Atención:",
    },
    "advisor.open_hint": {
        Language.ENGLISH: (
            "Opening a design opens its editor. Set the final frequency and use "
            "Estimate Dimensions there."
        ),
        Language.SPANISH: (
            "Abrir un diseño abre su editor. Ahí definí la frecuencia final y usá "
            "Estimar dimensiones."
        ),
    },
    "advisor.disclaimer": {
        Language.ENGLISH: (
            "Suitability values are planning heuristics, not validated construction dimensions."
        ),
        Language.SPANISH: (
            "Los valores de idoneidad son heurísticas de planificación, no "
            "dimensiones de construcción validadas."
        ),
    },
    "advisor.gain.low": {
        Language.ENGLISH: "low",
        Language.SPANISH: "baja",
    },
    "advisor.gain.medium": {
        Language.ENGLISH: "medium",
        Language.SPANISH: "media",
    },
    "advisor.gain.high": {
        Language.ENGLISH: "high",
        Language.SPANISH: "alta",
    },
    "advisor.takeoff.high": {
        Language.ENGLISH: "high angle",
        Language.SPANISH: "ángulo alto",
    },
    "advisor.takeoff.medium": {
        Language.ENGLISH: "medium angle",
        Language.SPANISH: "ángulo medio",
    },
    "advisor.takeoff.low": {
        Language.ENGLISH: "low angle",
        Language.SPANISH: "ángulo bajo",
    },
    "advisor.bandwidth.narrow": {
        Language.ENGLISH: "narrow",
        Language.SPANISH: "angosto",
    },
    "advisor.bandwidth.moderate": {
        Language.ENGLISH: "moderate",
        Language.SPANISH: "moderado",
    },
    "advisor.bandwidth.wide": {
        Language.ENGLISH: "wide",
        Language.SPANISH: "amplio",
    },
    "advisor.profile.wire_dipole.tradeoff": {
        Language.ENGLISH: (
            "Simple, inexpensive, and easy to tune. One band per dipole; height "
            "strongly affects the takeoff angle."
        ),
        Language.SPANISH: (
            "Simple, económico y fácil de sintonizar. Un dipolo por banda; la altura "
            "afecta mucho el ángulo de salida."
        ),
    },
    "advisor.profile.inverted_v.tradeoff": {
        Language.ENGLISH: (
            "Needs one high support and less horizontal span. Higher angle of "
            "radiation; good for local and NVIS work."
        ),
        Language.SPANISH: (
            "Necesita un soporte alto y menos espacio horizontal. Ángulo de radiación "
            "más alto; bueno para trabajo local y NVIS."
        ),
    },
    "advisor.profile.endfed.tradeoff": {
        Language.ENGLISH: (
            "One wire and a transformer; easy to deploy. Needs a counterpoise or a "
            "good installation return, and the feed line can affect SWR."
        ),
        Language.SPANISH: (
            "Un solo hilo y un transformador; fácil de instalar. Necesita contrapeso "
            "o un buen retorno de instalación, y la línea puede afectar la ROE."
        ),
    },
    "advisor.profile.ocfd.tradeoff": {
        Language.ENGLISH: (
            "Multiband with a 4:1 transformer; no tuner on the designed bands. Needs "
            "a longer span and a clear feed point."
        ),
        Language.SPANISH: (
            "Multibanda con transformador 4:1; sin sintonizador en las bandas de "
            "diseño. Necesita más luz y un punto de alimentación despejado."
        ),
    },
    "advisor.profile.g5rv.tradeoff": {
        Language.ENGLISH: (
            "Classic multiband wire with a matching section; a tuner is normally "
            "required. Long span and feed-line losses matter."
        ),
        Language.SPANISH: (
            "Hilo multibanda clásico con sección de adaptación; normalmente requiere "
            "sintonizador. Importan la luz y las pérdidas de la línea."
        ),
    },
    "advisor.profile.vertical.tradeoff": {
        Language.ENGLISH: (
            "Low angle and small footprint; needs a radial system or counterpoise. "
            "Ground and radial quality dominate efficiency."
        ),
        Language.SPANISH: (
            "Ángulo bajo y poca planta; necesita radiales o contrapeso. La calidad "
            "del suelo y de los radiales domina la eficiencia."
        ),
    },
    "advisor.profile.loop.tradeoff": {
        Language.ENGLISH: (
            "Quiet receive and broad pattern; needs a large horizontal footprint and "
            "a matching network."
        ),
        Language.SPANISH: (
            "Recepción más silenciosa y patrón amplio; necesita una planta horizontal "
            "grande y una red de adaptación."
        ),
    },
    "advisor.profile.yagi.tradeoff": {
        Language.ENGLISH: (
            "Directional gain and front-to-back; needs a boom, rotator, and careful "
            "tuning. Best for DX."
        ),
        Language.SPANISH: (
            "Ganancia directiva y relación frente-espalda; necesita boom, rotor y "
            "ajuste cuidadoso. Ideal para DX."
        ),
    },
    "advisor.profile.moxon.tradeoff": {
        Language.ENGLISH: (
            "Compact directional beam with good front-to-back; less gain than a full "
            "Yagi and still needs aiming."
        ),
        Language.SPANISH: (
            "Beam direccional compacto con buena relación frente-espalda; menos "
            "ganancia que un Yagi completo y también necesita orientación."
        ),
    },
    "advisor.profile.random_wire.tradeoff": {
        Language.ENGLISH: (
            "Very simple wire and a tuner; performance depends on the tuner, "
            "counterpoise, and installation. Experimental starting point."
        ),
        Language.SPANISH: (
            "Hilo muy simple y sintonizador; el rendimiento depende del sintonizador, "
            "el contrapeso y la instalación. Punto de partida experimental."
        ),
    },
    "advisor.profile.fan_dipole.tradeoff": {
        Language.ENGLISH: (
            "Multiband with separate resonant legs; no tuner on the designed bands, "
            "but interaction between legs requires tuning."
        ),
        Language.SPANISH: (
            "Multibanda con ramas resonantes separadas; sin sintonizador en las bandas "
            "de diseño, pero la interacción entre ramas exige ajuste."
        ),
    },
    "advisor.profile.trap_dipole.tradeoff": {
        Language.ENGLISH: (
            "Multiband with traps; compact for its bands, but trap loss and tuning need attention."
        ),
        Language.SPANISH: (
            "Multibanda con trampas; compacto para sus bandas, pero la pérdida de las "
            "trampas y el ajuste requieren atención."
        ),
    },
    "advanced.title": {
        Language.ENGLISH: "Advanced simulation",
        Language.SPANISH: "Simulación avanzada",
    },
    "solver.group_title": {
        Language.ENGLISH: "Solver",
        Language.SPANISH: "Solver",
    },
    "solver.timeout": {
        Language.ENGLISH: "Analysis timeout",
        Language.SPANISH: "Tiempo máximo de análisis",
    },
    "solver.timeout_hint": {
        Language.ENGLISH: (
            "Maximum wall-clock time for one solver run. Raise it for large "
            "arrays; the default is 180 s."
        ),
        Language.SPANISH: (
            "Tiempo máximo de una corrida del solver. Aumentalo para arrays "
            "grandes; el valor por defecto es 180 s."
        ),
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
        Language.ENGLISH: (
            "AntennaDesk {version} — GPL-3.0-or-later\n"
            "Developed by Fernando Sclavo (LU2EFI).\n"
            "Local-first antenna design and simulation."
        ),
        Language.SPANISH: (
            "AntennaDesk {version} — GPL-3.0-or-later\n"
            "Desarrollado por Fernando Sclavo (LU2EFI).\n"
            "Diseño y simulación de antenas local-first."
        ),
    },
    "menu.file": {Language.ENGLISH: "File", Language.SPANISH: "Archivo"},
    "menu.edit": {Language.ENGLISH: "Edit", Language.SPANISH: "Editar"},
    "menu.view": {Language.ENGLISH: "View", Language.SPANISH: "Ver"},
    "menu.workflow_mode": {
        Language.ENGLISH: "Workflow mode",
        Language.SPANISH: "Modo de trabajo",
    },
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
    "preferences.workflow_mode": {
        Language.ENGLISH: "Workflow mode",
        Language.SPANISH: "Modo de trabajo",
    },
    "preferences.hint": {
        Language.ENGLISH: (
            "Language, units, font size, and workflow mode apply after you "
            "accept. System follows the operating system language. Project "
            "files always store metric SI units."
        ),
        Language.SPANISH: (
            "El idioma, las unidades, el tamaño de fuente y el modo de trabajo "
            "se aplican al aceptar. Sistema sigue el idioma del sistema "
            "operativo. Los archivos de proyecto siempre guardan unidades SI "
            "métricas."
        ),
    },
    "action.preferences": {
        Language.ENGLISH: "Preferences...",
        Language.SPANISH: "Preferencias...",
    },
    "action.installation_profile": {
        Language.ENGLISH: "Installation profile...",
        Language.SPANISH: "Perfil de instalación...",
    },
    "action.antenna_advisor": {
        Language.ENGLISH: "Help me choose...",
        Language.SPANISH: "Ayúdame a elegir...",
    },
    "start.advise": {
        Language.ENGLISH: "Help me choose...",
        Language.SPANISH: "Ayúdame a elegir...",
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
    "catalog.biquad": {
        Language.ENGLISH: "Biquad",
        Language.SPANISH: "Biquad",
    },
    "catalog.biquad.description": {
        Language.ENGLISH: (
            "Two stacked square loops with an optional wire reflector, fed at the "
            "central rail; a broadband broadside starting point."
        ),
        Language.SPANISH: (
            "Dos lazos cuadrados apilados con reflector de hilo opcional, "
            "alimentados en el travesaño central; un punto de partida bidireccional "
            "y de banda ancha."
        ),
    },
    "catalog.double_biquad": {
        Language.ENGLISH: "Double biquad",
        Language.SPANISH: "Biquad doble",
    },
    "catalog.double_biquad.description": {
        Language.ENGLISH: (
            "Four stacked loops sharing horizontal rails, with an optional wire "
            "reflector; a higher-gain extension of the biquad starting point."
        ),
        Language.SPANISH: (
            "Cuatro lazos apilados que comparten travesaños horizontales, con "
            "reflector de hilo opcional; una extensión de mayor ganancia del punto "
            "de partida biquad."
        ),
    },
    "catalog.beverage": {
        Language.ENGLISH: "Beverage",
        Language.SPANISH: "Beverage",
    },
    "catalog.beverage.description": {
        Language.ENGLISH: (
            "Long horizontal traveling-wave receiving wire with an optional "
            "resistor termination to ground; broadside end-fire toward the "
            "termination."
        ),
        Language.SPANISH: (
            "Hilo receptor horizontal largo de onda viajera con terminación "
            "resistiva opcional a tierra; patrón directivo hacia la terminación."
        ),
    },
    "catalog.loaded_dipole": {
        Language.ENGLISH: "Loaded / linked dipole",
        Language.SPANISH: "Dipolo cargado / enlazado",
    },
    "catalog.loaded_dipole.description": {
        Language.ENGLISH: (
            "Center-fed dipole with symmetric loading coils, or with open links "
            "that leave only the center section active; portable and SOTA use."
        ),
        Language.SPANISH: (
            "Dipolo alimentado en el centro con bobinas de carga simétricas, o con "
            "enlaces abiertos que dejan activa solo la sección central; uso "
            "portátil y SOTA."
        ),
    },
    "catalog.phased_vertical": {
        Language.ENGLISH: "Phased vertical array",
        Language.SPANISH: "Arreglo vertical en fase",
    },
    "catalog.phased_vertical.description": {
        Language.ENGLISH: (
            "Two to four vertical radiators spaced along a line and driven with "
            "an ideal phase step and amplitude taper; the first vertical is the "
            "primary feed."
        ),
        Language.SPANISH: (
            "De dos a cuatro verticales separadas sobre una línea y excitadas con "
            "un escalón de fase y una atenuación de amplitud ideales; la primera "
            "vertical es la alimentación principal."
        ),
    },
    "catalog.quad_beam": {
        Language.ENGLISH: "Quad beam",
        Language.SPANISH: "Beam cuádruple",
    },
    "catalog.quad_beam.description": {
        Language.ENGLISH: (
            "Two or three square loops on a boom: a reflector, a driven loop, "
            "and an optional director, with a horizontal pattern."
        ),
        Language.SPANISH: (
            "Dos o tres lazos cuadrados sobre un boom: reflector, lazo excitado "
            "y director opcional, con patrón horizontal."
        ),
    },
    "catalog.discone": {
        Language.ENGLISH: "Discone",
        Language.SPANISH: "Discono",
    },
    "catalog.discone.description": {
        Language.ENGLISH: (
            "Broadband vertical antenna with a radial-wire cone and a larger top "
            "disc, fed across a small gap at the apex."
        ),
        Language.SPANISH: (
            "Antena vertical de banda ancha con un cono de hilos radiales y un "
            "disco superior más grande, alimentada en una pequeña brecha del vértice."
        ),
    },
    "catalog.trap_yagi": {
        Language.ENGLISH: "Trapped Yagi",
        Language.SPANISH: "Yagi con trampas",
    },
    "catalog.trap_yagi.description": {
        Language.ENGLISH: (
            "Two-band Yagi with one parallel LC trap pair on every element; the "
            "traps isolate the outer tips on the high band."
        ),
        Language.SPANISH: (
            "Yagi de dos bandas con un par de trampas LC en paralelo en cada "
            "elemento; las trampas aíslan las puntas externas en la banda alta."
        ),
    },
    "catalog.hexbeam": {
        Language.ENGLISH: "Hexbeam",
        Language.SPANISH: "Hexbeam",
    },
    "catalog.hexbeam.description": {
        Language.ENGLISH: (
            "Single-band broadband beam with a W-shaped driven element and a "
            "U-shaped reflector on a six-spreader frame."
        ),
        Language.SPANISH: (
            "Beam de banda ancha y una sola banda con elemento excitado en forma "
            "de W y reflector en forma de U sobre un marco de seis separadores."
        ),
    },
    "catalog.family.wire": {
        Language.ENGLISH: "Wire antennas",
        Language.SPANISH: "Antenas de hilo",
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
    "catalog.shortened_endfed_80_10": {
        Language.ENGLISH: "Shortened EFHW 80-10 m",
        Language.SPANISH: "EFHW acortada 80-10 m",
    },
    "catalog.shortened_endfed_80_10.description": {
        Language.ENGLISH: (
            "End-fed half-wave with a 110 µH loading coil: 20.35 m lower "
            "section, 2.39 m top section, and a 49:1 transformer."
        ),
        Language.SPANISH: (
            "Media onda alimentada en el extremo con bobina de carga de 110 µH: "
            "tramo inferior de 20,35 m, tramo superior de 2,39 m y "
            "transformador 49:1."
        ),
    },
    "catalog.shortened_endfed_40_10": {
        Language.ENGLISH: "Shortened EFHW 40-20-10 m",
        Language.SPANISH: "EFHW acortada 40-20-10 m",
    },
    "catalog.shortened_endfed_40_10.description": {
        Language.ENGLISH: (
            "End-fed half-wave with a 23 µH loading coil: 10.01 m lower "
            "section, 1.85 m top section, and a 49:1 transformer."
        ),
        Language.SPANISH: (
            "Media onda alimentada en el extremo con bobina de carga de 23 µH: "
            "tramo inferior de 10,01 m, tramo superior de 1,85 m y "
            "transformador 49:1."
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
    "action.feed_chain": {
        Language.ENGLISH: "Feed-Chain Loss Budget...",
        Language.SPANISH: "Presupuesto de pérdidas...",
    },
    "action.component_calculator": {
        Language.ENGLISH: "Component Calculators...",
        Language.SPANISH: "Calculadoras de componentes...",
    },
    "action.measurement_sessions": {
        Language.ENGLISH: "Measurement Sessions...",
        Language.SPANISH: "Sesiones de medición...",
    },
    "action.tuning_assistant": {
        Language.ENGLISH: "Tuning Assistant...",
        Language.SPANISH: "Asistente de ajuste...",
    },
    "action.exit": {Language.ENGLISH: "Exit", Language.SPANISH: "Salir"},
    "action.about": {
        Language.ENGLISH: "About AntennaDesk",
        Language.SPANISH: "Acerca de AntennaDesk",
    },
    "action.whats_this": {
        Language.ENGLISH: "What's This?",
        Language.SPANISH: "¿Qué es esto?",
    },
    "action.whats_this.tooltip": {
        Language.ENGLISH: "Click a control or label to read its help.",
        Language.SPANISH: "Hacé clic en un control o etiqueta para leer su ayuda.",
    },
    "help.chart.impedance": {
        Language.ENGLISH: "Resistance and reactance versus frequency.",
        Language.SPANISH: "Resistencia y reactancia en función de la frecuencia.",
    },
    "help.chart.swr": {
        Language.ENGLISH: "SWR versus frequency for the selected reference impedance.",
        Language.SPANISH: "ROE en función de la frecuencia para la impedancia de referencia.",
    },
    "help.chart.pattern": {
        Language.ENGLISH: "Far-field gain pattern at the selected snapshot frequency.",
        Language.SPANISH: "Patrón de ganancia de campo lejano en la frecuencia seleccionada.",
    },
    "help.chart.currents": {
        Language.ENGLISH: "Current magnitude along the modeled wires.",
        Language.SPANISH: "Magnitud de corriente a lo largo de los hilos modelados.",
    },
    "help.chart.measurement": {
        Language.ENGLISH: "Imported measurement compared with the simulated SWR.",
        Language.SPANISH: "Medición importada comparada con la ROE simulada.",
    },
    "help.band.selector": {
        Language.ENGLISH: "Select the band shown in the result tabs.",
        Language.SPANISH: "Seleccioná la banda que se muestra en las pestañas de resultados.",
    },
    "help.pattern.frequency": {
        Language.ENGLISH: "Snapshot frequency used for the pattern.",
        Language.SPANISH: "Frecuencia de captura usada para el patrón.",
    },
    "help.pattern.mode": {
        Language.ENGLISH: "Pattern cut plane.",
        Language.SPANISH: "Plano de corte del patrón.",
    },
    "help.pattern.cut": {
        Language.ENGLISH: "Cut angle for the polar pattern.",
        Language.SPANISH: "Ángulo de corte para el patrón polar.",
    },
    "help.pattern.metric": {
        Language.ENGLISH: "Gain metric shown in the pattern.",
        Language.SPANISH: "Métrica de ganancia mostrada en el patrón.",
    },
    "help.currents.frequency": {
        Language.ENGLISH: "Frequency used for the current distribution.",
        Language.SPANISH: "Frecuencia usada para la distribución de corriente.",
    },
    "help.table.impedance": {
        Language.ENGLISH: "Frequency, resistance, reactance, impedance, and SWR rows.",
        Language.SPANISH: "Filas de frecuencia, resistencia, reactancia, impedancia y ROE.",
    },
    "help.table.sources": {
        Language.ENGLISH: "Per-source voltage, current, impedance, amplitude, phase, and power.",
        Language.SPANISH: "Tensión, corriente, impedancia, amplitud, fase y potencia por fuente.",
    },
    "help.table.bands": {
        Language.ENGLISH: "Best SWR, frequency, gain, takeoff, efficiency, and status per band.",
        Language.SPANISH: "Mejor ROE, frecuencia, ganancia, ángulo de salida, eficiencia y estado por banda.",
    },
    "help.table.measurement": {
        Language.ENGLISH: "Imported measurement points and comparison values.",
        Language.SPANISH: "Puntos de medición importados y valores de comparación.",
    },
    "help.table.diagnostics": {
        Language.ENGLISH: "Severity, message, and field for solver diagnostics.",
        Language.SPANISH: "Severidad, mensaje y campo de los diagnósticos del solver.",
    },
    "help.status.progress": {
        Language.ENGLISH: "Current background task and its estimated progress.",
        Language.SPANISH: "Tarea en segundo plano y su progreso estimado.",
    },
    "help.status.solver": {
        Language.ENGLISH: "Configured NEC engine and executable.",
        Language.SPANISH: "Motor NEC configurado y ejecutable.",
    },
    "help.status.message": {
        Language.ENGLISH: "Current application status and last operation result.",
        Language.SPANISH: "Estado actual de la aplicación y resultado de la última operación.",
    },
    "help.action.cancel": {
        Language.ENGLISH: "Stop the running simulation or analysis.",
        Language.SPANISH: "Detené la simulación o el análisis en curso.",
    },
    "help.action.export": {
        Language.ENGLISH: "Export the current result, geometry, or construction data.",
        Language.SPANISH: "Exportá el resultado, la geometría o los datos de construcción actuales.",
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
        Language.ENGLISH: (
            "{template} · radiator {radiator} · stub {stub} · spacing {spacing} · "
            "feed offset {feed} · base {base}"
        ),
        Language.SPANISH: (
            "{template} · radiador {radiator} · stub {stub} · separación {spacing} · "
            "desplazamiento de alimentación {feed} · base {base}"
        ),
    },
    "geometry.slim_jim_elevation": {
        Language.ENGLISH: (
            "{template} · radiator {radiator} · stub {stub} · gap {gap} · "
            "spacing {spacing} · feed offset {feed} · base {base}"
        ),
        Language.SPANISH: (
            "{template} · radiador {radiator} · stub {stub} · brecha {gap} · "
            "separación {spacing} · desplazamiento de alimentación {feed} · base {base}"
        ),
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
    "geometry.endfed_return_proxy": {
        Language.ENGLISH: (
            "Installation return is modeled but not drawn; it represents the "
            "coax/mast/earth path, not a physical radial"
        ),
        Language.SPANISH: (
            "El retorno de instalación se modela pero no se dibuja; representa el "
            "camino del coaxil/mástil/tierra, no una radial física"
        ),
    },
    "geometry.endfed_bend_note": {
        Language.ENGLISH: (
            "The inverted-L bend is a sharp 90° corner; support the corner and keep "
            "the horizontal run clear of nearby objects"
        ),
        Language.SPANISH: (
            "El codo en L invertida es una esquina recta de 90°; soportá la esquina y "
            "mantené el tramo horizontal alejado de objetos cercanos"
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
    "geometry.upper_section": {
        Language.ENGLISH: "upper section",
        Language.SPANISH: "tramo superior",
    },
    "geometry.lower_section": {
        Language.ENGLISH: "lower section",
        Language.SPANISH: "tramo inferior",
    },
    "geometry.left_leg": {
        Language.ENGLISH: "left leg",
        Language.SPANISH: "pierna izquierda",
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
    "geometry.inner": {Language.ENGLISH: "inner", Language.SPANISH: "interior"},
    "geometry.outer": {Language.ENGLISH: "outer", Language.SPANISH: "exterior"},
    "geometry.reflector_tip": {
        Language.ENGLISH: "reflector tip",
        Language.SPANISH: "punta del reflector",
    },
    "geometry.driven_tip": {
        Language.ENGLISH: "driven tip",
        Language.SPANISH: "punta del excitado",
    },
    "geometry.reflector_element": {
        Language.ENGLISH: "reflector",
        Language.SPANISH: "reflector",
    },
    "geometry.driven_element": {
        Language.ENGLISH: "driven",
        Language.SPANISH: "excitado",
    },
    "geometry.director_element": {
        Language.ENGLISH: "director",
        Language.SPANISH: "director",
    },
    "geometry.reflector_loop": {
        Language.ENGLISH: "reflector loop",
        Language.SPANISH: "lazo reflector",
    },
    "geometry.driven_loop": {
        Language.ENGLISH: "driven loop",
        Language.SPANISH: "lazo excitado",
    },
    "geometry.director_loop": {
        Language.ENGLISH: "director loop",
        Language.SPANISH: "lazo director",
    },
    "geometry.reflector_spacing": {
        Language.ENGLISH: "reflector spacing",
        Language.SPANISH: "separación del reflector",
    },
    "geometry.director_spacing": {
        Language.ENGLISH: "director spacing",
        Language.SPANISH: "separación del director",
    },
    "geometry.trap_inset_label": {
        Language.ENGLISH: "trap inset",
        Language.SPANISH: "inserción de trampa",
    },
    "geometry.detail_tip": {
        Language.ENGLISH: "tip detail (not to scale)",
        Language.SPANISH: "detalle de puntas (sin escala)",
    },
    "geometry.detail_half": {
        Language.ENGLISH: "left half; symmetric (not to scale)",
        Language.SPANISH: "mitad izquierda; simétrica (sin escala)",
    },
    "geometry.detail_loop": {
        Language.ENGLISH: "driven loop front detail · side {side} (not to scale)",
        Language.SPANISH: "detalle frontal del lazo excitado · lado {side} (sin escala)",
    },
    "geometry.detail_trap": {
        Language.ENGLISH: "trap detail; symmetric (not to scale)",
        Language.SPANISH: "detalle de trampas; simétrico (sin escala)",
    },
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
    "geometry.span": {
        Language.ENGLISH: "span",
        Language.SPANISH: "envergadura",
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
    "geometry.projected_length_note": {
        Language.ENGLISH: (
            "true wire length {length}; the dimension shows the projected {projected}"
        ),
        Language.SPANISH: (
            "longitud real del hilo {length}; la cota muestra la proyección {projected}"
        ),
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
    "geometry.hidden_values": {
        Language.ENGLISH: "Hidden for space: {values}",
        Language.SPANISH: "Ocultas por espacio: {values}",
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
    "geometry.view_construction": {
        Language.ENGLISH: "Construction",
        Language.SPANISH: "Construcción",
    },
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
    "design_from_frequency.unsupported_loaded_endfed": {
        Language.ENGLISH: (
            "A shortened EFHW depends on its loading coil and matching unit, so "
            "automatic frequency-first estimation is not available."
        ),
        Language.SPANISH: (
            "Una EFHW acortada depende de su bobina de carga y su unidad de "
            "adaptación, por lo que no hay estimación automática desde frecuencia."
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
    "help.field.frequency": {
        Language.ENGLISH: (
            "Design frequency in MHz. Changing it reloads the template's suggested "
            "starting dimensions."
        ),
        Language.SPANISH: (
            "Frecuencia de diseño en MHz. Al cambiarla se recargan las dimensiones "
            "iniciales sugeridas por la plantilla."
        ),
    },
    "help.field.height": {
        Language.ENGLISH: (
            "Wire height above the selected ground model. It is installation context, "
            "not optimized by default."
        ),
        Language.SPANISH: (
            "Altura del hilo sobre el modelo de suelo elegido. Es contexto de "
            "instalación y no se optimiza por defecto."
        ),
    },
    "help.wire_dipole.field.height": {
        Language.ENGLISH: (
            "Height of the horizontal wire above ground; the feed and ends share this "
            "default height."
        ),
        Language.SPANISH: (
            "Altura del hilo horizontal sobre el suelo; la alimentación y los extremos "
            "usan esta altura por defecto."
        ),
    },
    "help.field.antenna_type": {
        Language.ENGLISH: (
            "Antenna family selected for this design. Changing the family may replace "
            "the editable topology."
        ),
        Language.SPANISH: (
            "Familia de antena seleccionada para este diseño. Cambiar de familia puede "
            "reemplazar la topología editable."
        ),
    },
    "help.field.azimuth": {
        Language.ENGLISH: (
            "Rotation of the antenna around the vertical axis, in degrees clockwise from north."
        ),
        Language.SPANISH: (
            "Rotación de la antena alrededor del eje vertical, en grados y en sentido "
            "horario desde el norte."
        ),
    },
    "help.field.base_height": {
        Language.ENGLISH: "Height of the feed or base above the selected ground model.",
        Language.SPANISH: "Altura de la alimentación o de la base sobre el modelo de suelo elegido.",
    },
    "help.field.circumference": {
        Language.ENGLISH: (
            "Total conductor length around the loop; the polygon side length follows "
            "the side count."
        ),
        Language.SPANISH: (
            "Longitud total del conductor del lazo; el lado del polígono depende de la "
            "cantidad de lados."
        ),
    },
    "help.field.conductivity": {
        Language.ENGLISH: (
            "Ground conductivity in siemens per metre; used only by the finite-ground model."
        ),
        Language.SPANISH: (
            "Conductividad del suelo en siemens por metro; solo la usa el modelo de suelo finito."
        ),
    },
    "help.field.design_frequency": {
        Language.ENGLISH: (
            "Frequency used for the template's starting dimensions and the default simulation band."
        ),
        Language.SPANISH: (
            "Frecuencia usada para las dimensiones iniciales de la plantilla y la banda "
            "de simulación por defecto."
        ),
    },
    "help.field.diameter": {
        Language.ENGLISH: "Conductor diameter; it affects the modeled impedance and losses.",
        Language.SPANISH: "Diámetro del conductor; afecta la impedancia y las pérdidas modeladas.",
    },
    "help.field.element_length": {
        Language.ENGLISH: "Length of one driven or parasitic element in the current array.",
        Language.SPANISH: "Longitud de un elemento alimentado o parásito del arreglo actual.",
    },
    "help.field.family": {
        Language.ENGLISH: "Broad antenna family shown for the current template.",
        Language.SPANISH: "Familia amplia de antena que corresponde a la plantilla actual.",
    },
    "help.field.fundamental_frequency": {
        Language.ENGLISH: (
            "Lowest design frequency used to derive the template's harmonic coverage."
        ),
        Language.SPANISH: (
            "Frecuencia de diseño más baja usada para derivar la cobertura armónica de "
            "la plantilla."
        ),
    },
    "help.field.ground": {
        Language.ENGLISH: "Ground model used by the solver: free space, perfect, or finite.",
        Language.SPANISH: "Modelo de suelo del solver: espacio libre, perfecto o finito.",
    },
    "help.field.length": {
        Language.ENGLISH: (
            "Primary conductor length; the template defines which physical span it represents."
        ),
        Language.SPANISH: (
            "Longitud principal del conductor; la plantilla define qué tramo físico representa."
        ),
    },
    "help.field.material": {
        Language.ENGLISH: "Conductor material preset; it sets the conductivity used for losses.",
        Language.SPANISH: "Material del conductor; ajusta la conductividad usada para las pérdidas.",
    },
    "help.field.orientation": {
        Language.ENGLISH: (
            "Plane of the antenna: horizontal, vertical, or the template-specific equivalent."
        ),
        Language.SPANISH: (
            "Plano de la antena: horizontal, vertical o el equivalente de la plantilla."
        ),
    },
    "help.field.permittivity": {
        Language.ENGLISH: (
            "Relative permittivity of the ground; used only by the finite-ground model."
        ),
        Language.SPANISH: (
            "Permitividad relativa del suelo; solo la usa el modelo de suelo finito."
        ),
    },
    "help.field.polarization": {
        Language.ENGLISH: (
            "Polarization of the radiated field; it controls the element orientation."
        ),
        Language.SPANISH: (
            "Polarización del campo radiado; controla la orientación de los elementos."
        ),
    },
    "help.field.primary_dimension": {
        Language.ENGLISH: "Main dimension optimized by the current template.",
        Language.SPANISH: "Dimensión principal que optimiza la plantilla actual.",
    },
    "help.field.project_name": {
        Language.ENGLISH: "Name shown in the project title and saved in the project file.",
        Language.SPANISH: "Nombre que aparece en el título del proyecto y se guarda en el archivo.",
    },
    "help.field.reference_impedance": {
        Language.ENGLISH: (
            "Impedance used for the reported SWR; it does not change the antenna model."
        ),
        Language.SPANISH: (
            "Impedancia usada para la ROE informada; no cambia el modelo de la antena."
        ),
    },
    "help.field.sag": {
        Language.ENGLISH: (
            "Additional conductor length for a sagging horizontal span; zero keeps the "
            "span straight."
        ),
        Language.SPANISH: (
            "Longitud adicional de conductor para un tramo horizontal con flecha; cero "
            "lo mantiene recto."
        ),
    },
    "help.field.secondary_dimension": {
        Language.ENGLISH: "Second dimension optimized alongside the primary dimension.",
        Language.SPANISH: "Segunda dimensión que se optimiza junto con la dimensión principal.",
    },
    "help.field.sides": {
        Language.ENGLISH: "Number of straight segments used to approximate the loop.",
        Language.SPANISH: "Cantidad de segmentos rectos usados para aproximar el lazo.",
    },
    "help.field.soil_preset": {
        Language.ENGLISH: (
            "Starting ground values for a typical soil; choosing one fills permittivity "
            "and conductivity."
        ),
        Language.SPANISH: (
            "Valores iniciales de suelo típico; al elegir uno se completan permitividad "
            "y conductividad."
        ),
    },
    "help.field.spacing": {
        Language.ENGLISH: (
            "Separation between parallel conductors or array elements, depending on the template."
        ),
        Language.SPANISH: (
            "Separación entre conductores paralelos o elementos del arreglo, según la plantilla."
        ),
    },
    "help.field.sweep": {
        Language.ENGLISH: "Frequency range used for the impedance and SWR sweep.",
        Language.SPANISH: "Rango de frecuencias usado para el barrido de impedancia y ROE.",
    },
    "help.field.sweep_enabled": {
        Language.ENGLISH: "Adds a frequency sweep instead of a single-frequency run.",
        Language.SPANISH: "Agrega un barrido de frecuencia en lugar de una corrida de frecuencia única.",
    },
    "help.field.sweep_points": {
        Language.ENGLISH: (
            "Number of frequency samples in the sweep; more points resolve narrow features."
        ),
        Language.SPANISH: (
            "Cantidad de muestras del barrido; más puntos resuelven detalles estrechos."
        ),
    },
    "help.field.sweep_start": {
        Language.ENGLISH: "Lowest frequency in the custom sweep.",
        Language.SPANISH: "Frecuencia más baja del barrido personalizado.",
    },
    "help.field.sweep_stop": {
        Language.ENGLISH: "Highest frequency in the custom sweep.",
        Language.SPANISH: "Frecuencia más alta del barrido personalizado.",
    },
    "help.field.template": {
        Language.ENGLISH: "Catalog template that defines the current editable fields.",
        Language.SPANISH: "Plantilla del catálogo que define los campos editables actuales.",
    },
    "help.field.wire_radius": {
        Language.ENGLISH: "Conductor radius; it affects the modeled impedance and losses.",
        Language.SPANISH: "Radio del conductor; afecta la impedancia y las pérdidas modeladas.",
    },
    "help.yagi.field.height": {
        Language.ENGLISH: (
            "Boom centerline height above ground; vertical polarization also uses it "
            "for element clearance."
        ),
        Language.SPANISH: (
            "Altura de la línea central del boom sobre el suelo; la polarización "
            "vertical también la usa para la separación de los elementos."
        ),
    },
    "help.yagi.field.polarization": {
        Language.ENGLISH: (
            "Vertical polarization keeps the boom horizontal and rotates the elements "
            "around it; height is the boom centerline."
        ),
        Language.SPANISH: (
            "La polarización vertical mantiene el boom horizontal y gira los elementos "
            "alrededor de él; la altura es la línea central del boom."
        ),
    },
    "help.moxon.field.polarization": {
        Language.ENGLISH: (
            "Vertical polarization turns the Moxon rectangle into a vertical-plane "
            "array; height stays the rectangle center."
        ),
        Language.SPANISH: (
            "La polarización vertical convierte el rectángulo Moxon en un arreglo en "
            "plano vertical; la altura sigue siendo el centro del rectángulo."
        ),
    },
    "help.moxon.field.height": {
        Language.ENGLISH: (
            "Height of the Moxon rectangle center above ground; it sets the modeled "
            "installation, not the rectangle size."
        ),
        Language.SPANISH: (
            "Altura del centro del rectángulo Moxon sobre el suelo; define la "
            "instalación modelada, no el tamaño del rectángulo."
        ),
    },
    "help.hexbeam.field.height": {
        Language.ENGLISH: (
            "Height of the hexbeam center above ground; the spreader geometry is "
            "rebuilt around this center."
        ),
        Language.SPANISH: (
            "Altura del centro del hexbeam sobre el suelo; la geometría de los "
            "separadores se reconstruye alrededor de este centro."
        ),
    },
    "help.trap_yagi.field.height": {
        Language.ENGLISH: (
            "Boom centerline height above ground; the trap elements keep their "
            "published spacing around it."
        ),
        Language.SPANISH: (
            "Altura de la línea central del boom sobre el suelo; los elementos con "
            "trampas mantienen su separación publicada alrededor de ella."
        ),
    },
    "help.phased_vertical.field.height": {
        Language.ENGLISH: (
            "Common vertical-element height above the base; spacing and phase set the "
            "array pattern."
        ),
        Language.SPANISH: (
            "Altura común de los elementos verticales sobre la base; la separación y "
            "la fase definen el patrón del arreglo."
        ),
    },
    "help.quad_beam.field.height": {
        Language.ENGLISH: (
            "Height of the driven loop center above ground; reflector and director "
            "loops share the same center height."
        ),
        Language.SPANISH: (
            "Altura del centro del lazo alimentado sobre el suelo; los lazos reflector "
            "y director comparten esa altura."
        ),
    },
    "help.dipole.field.spacing": {
        Language.ENGLISH: (
            "Separation between the two folded-dipole conductors; it does not apply to "
            "a straight wire dipole."
        ),
        Language.SPANISH: (
            "Separación entre los dos conductores del dipolo plegado; no se aplica a "
            "un dipolo de hilo recto."
        ),
    },
    "help.beverage.termination_resistance": {
        Language.ENGLISH: (
            "Termination resistor at the far end; it absorbs the traveling wave and "
            "reduces the back lobe."
        ),
        Language.SPANISH: (
            "Resistencia de terminación en el extremo lejano; absorbe la onda viajera y "
            "reduce el lóbulo trasero."
        ),
    },
    "help.biquad.kind": {
        Language.ENGLISH: (
            "Biquad variant; single and double biquads use different loop and reflector geometry."
        ),
        Language.SPANISH: (
            "Variante de biquad; el biquad simple y el doble usan geometrías de lazo y "
            "reflector diferentes."
        ),
    },
    "help.biquad.reflector_spacing": {
        Language.ENGLISH: "Distance from the driven loop to the reflector loop.",
        Language.SPANISH: "Distancia desde el lazo alimentado hasta el lazo reflector.",
    },
    "help.discone.cone_radius": {
        Language.ENGLISH: ("Radius of the cone base; the wire cone approximates a solid skirt."),
        Language.SPANISH: (
            "Radio de la base del cono; el cono de hilos aproxima una falda sólida."
        ),
    },
    "help.discone.disc_gap": {
        Language.ENGLISH: "Feed gap between the cone apex and the disc.",
        Language.SPANISH: "Separación de alimentación entre el vértice del cono y el disco.",
    },
    "help.discone.wire_count": {
        Language.ENGLISH: "Number of radial wires used to approximate the cone and disc.",
        Language.SPANISH: "Cantidad de hilos radiales usados para aproximar el cono y el disco.",
    },
    "help.endfed.counterpoise_length": {
        Language.ENGLISH: ("Counterpoise wire length; it is a real wire, not an ideal ground."),
        Language.SPANISH: ("Longitud del hilo de contrapeso; es un hilo real, no un suelo ideal."),
    },
    "help.endfed.counterpoise_height": {
        Language.ENGLISH: "Counterpoise height above ground.",
        Language.SPANISH: "Altura del contrapeso sobre el suelo.",
    },
    "help.endfed.counterpoise_azimuth": {
        Language.ENGLISH: "Counterpoise direction around the feed.",
        Language.SPANISH: "Dirección del contrapeso alrededor de la alimentación.",
    },
    "help.endfed.bend_enabled": {
        Language.ENGLISH: (
            "Use an inverted-L installation: a vertical rise from the feed followed by "
            "a horizontal run."
        ),
        Language.SPANISH: (
            "Usa una instalación en L invertida: un tramo vertical desde la alimentación "
            "seguido de un tramo horizontal."
        ),
    },
    "help.endfed.bend_vertical": {
        Language.ENGLISH: (
            "Wire length from the feed to the bend; the horizontal run is the rest of "
            "the total wire length."
        ),
        Language.SPANISH: (
            "Longitud de hilo desde la alimentación hasta el codo; el tramo horizontal "
            "es el resto de la longitud total."
        ),
    },
    "help.endfed.transformer_ratio": {
        Language.ENGLISH: (
            "Ideal transformer ratio; the antenna-side impedance is divided by this "
            "value for reports."
        ),
        Language.SPANISH: (
            "Relación ideal del transformador; la impedancia del lado de la antena se "
            "divide por este valor en los informes."
        ),
    },
    "help.endfed.loading_coil_inductance": {
        Language.ENGLISH: (
            "Series loading-coil inductance; the coil is ideal unless a resistance is entered."
        ),
        Language.SPANISH: (
            "Inductancia de la bobina serie; la bobina es ideal salvo que se ingrese "
            "una resistencia."
        ),
    },
    "help.endfed.loading_coil_offset": {
        Language.ENGLISH: "Distance from the feed to the loading coil.",
        Language.SPANISH: "Distancia desde la alimentación hasta la bobina de carga.",
    },
    "help.endfed.loading_coil_resistance": {
        Language.ENGLISH: "Series resistance of the loading coil; zero keeps it ideal.",
        Language.SPANISH: "Resistencia serie de la bobina de carga; cero la mantiene ideal.",
    },
    "help.endfed.loading_coil_q": {
        Language.ENGLISH: (
            "Coil Q at the design frequency; shown only when a series resistance is entered."
        ),
        Language.SPANISH: (
            "Q de la bobina en la frecuencia de diseño; se muestra solo cuando hay una "
            "resistencia serie."
        ),
    },
    "help.g5rv.line_impedance": {
        Language.ENGLISH: "Characteristic impedance of the matching line.",
        Language.SPANISH: "Impedancia característica de la línea de adaptación.",
    },
    "help.g5rv.line_length": {
        Language.ENGLISH: "Physical length of the matching line.",
        Language.SPANISH: "Longitud física de la línea de adaptación.",
    },
    "help.g5rv.velocity_factor": {
        Language.ENGLISH: (
            "Line velocity factor; it changes the electrical length of the matching section."
        ),
        Language.SPANISH: (
            "Factor de velocidad de la línea; cambia la longitud eléctrica del tramo de adaptación."
        ),
    },
    "help.hexbeam.tip_gap": {
        Language.ENGLISH: "Gap between adjacent spreader tips at the element ends.",
        Language.SPANISH: "Separación entre puntas de separadores adyacentes en los extremos.",
    },
    "help.hexbeam.element_separation": {
        Language.ENGLISH: "Boom-axis spacing between the driven element and reflector.",
        Language.SPANISH: "Separación sobre el boom entre el elemento alimentado y el reflector.",
    },
    "help.hexbeam.turning_radius": {
        Language.ENGLISH: "Tip-to-boom turning radius used by the space constraint.",
        Language.SPANISH: "Radio de giro desde la punta al boom usado por la restricción de espacio.",
    },
    "help.j_pole.feed_offset": {
        Language.ENGLISH: "Feed-point distance above the stub.",
        Language.SPANISH: "Distancia del punto de alimentación por encima del stub.",
    },
    "help.j_pole.gap": {
        Language.ENGLISH: "Gap between the radiator and the stub.",
        Language.SPANISH: "Separación entre el radiador y el stub.",
    },
    "help.j_pole.spacing": {
        Language.ENGLISH: "Center-to-center spacing between the radiator and stub.",
        Language.SPANISH: "Separación entre centros del radiador y el stub.",
    },
    "help.loaded_dipole.link_offset": {
        Language.ENGLISH: "Distance from the center to the loading coil or link.",
        Language.SPANISH: "Distancia desde el centro hasta la bobina de carga o el enlace.",
    },
    "help.loaded_dipole.coil_inductance": {
        Language.ENGLISH: "Loading-coil inductance.",
        Language.SPANISH: "Inductancia de la bobina de carga.",
    },
    "help.loaded_dipole.coil_resistance": {
        Language.ENGLISH: "Series resistance of the loading coil; zero keeps it ideal.",
        Language.SPANISH: "Resistencia serie de la bobina de carga; cero la mantiene ideal.",
    },
    "help.magnetic_loop.capacitance": {
        Language.ENGLISH: (
            "Tuning capacitance; it sets the resonant frequency with the loop inductance."
        ),
        Language.SPANISH: (
            "Capacitancia de sintonía; define la frecuencia de resonancia junto con la "
            "inductancia del lazo."
        ),
    },
    "help.magnetic_loop.esr": {
        Language.ENGLISH: "Equivalent series resistance of the tuning capacitor.",
        Language.SPANISH: "Resistencia serie equivalente del capacitor de sintonía.",
    },
    "help.magnetic_loop.gap": {
        Language.ENGLISH: "Gap in the loop where the tuning capacitor is connected.",
        Language.SPANISH: "Separación en el lazo donde se conecta el capacitor de sintonía.",
    },
    "help.moxon.depth": {
        Language.ENGLISH: "Front-to-back depth of the Moxon rectangle.",
        Language.SPANISH: "Profundidad frontal-trasera del rectángulo Moxon.",
    },
    "help.moxon.reflector_tip": {
        Language.ENGLISH: "Reflector tip length beyond the side connector.",
        Language.SPANISH: "Longitud de la punta del reflector más allá del conector lateral.",
    },
    "help.moxon.driven_tip": {
        Language.ENGLISH: "Driven-element tip length beyond the side connector.",
        Language.SPANISH: "Longitud de la punta del elemento alimentado más allá del conector lateral.",
    },
    "help.ocfd.feed_offset": {
        Language.ENGLISH: (
            "Feed-point distance from the wire center as a fraction of total length."
        ),
        Language.SPANISH: (
            "Distancia del punto de alimentación desde el centro del hilo como fracción "
            "de la longitud total."
        ),
    },
    "help.ocfd.transformer_ratio": {
        Language.ENGLISH: (
            "Ideal transformer ratio; the antenna-side impedance is divided by this "
            "value for reports."
        ),
        Language.SPANISH: (
            "Relación ideal del transformador; la impedancia del lado de la antena se "
            "divide por este valor en los informes."
        ),
    },
    "help.phased_vertical.amplitude_taper": {
        Language.ENGLISH: "Relative amplitude applied across the vertical elements.",
        Language.SPANISH: "Amplitud relativa aplicada a los elementos verticales.",
    },
    "help.phased_vertical.phase_step": {
        Language.ENGLISH: "Progressive phase difference between adjacent vertical elements.",
        Language.SPANISH: "Diferencia de fase progresiva entre elementos verticales adyacentes.",
    },
    "help.phased_vertical.spacing": {
        Language.ENGLISH: "Center-to-center spacing between adjacent vertical elements.",
        Language.SPANISH: "Separación entre centros de elementos verticales adyacentes.",
    },
    "help.quad_beam.director_scale": {
        Language.ENGLISH: "Scale factor applied to the director loop size.",
        Language.SPANISH: "Factor de escala aplicado al tamaño del lazo director.",
    },
    "help.quad_beam.reflector_scale": {
        Language.ENGLISH: "Scale factor applied to the reflector loop size.",
        Language.SPANISH: "Factor de escala aplicado al tamaño del lazo reflector.",
    },
    "help.quad_beam.director_spacing": {
        Language.ENGLISH: "Boom-axis spacing from the driven loop to the director.",
        Language.SPANISH: "Separación sobre el boom desde el lazo alimentado hasta el director.",
    },
    "help.quad_beam.reflector_spacing": {
        Language.ENGLISH: "Boom-axis spacing from the reflector to the driven loop.",
        Language.SPANISH: "Separación sobre el boom desde el reflector hasta el lazo alimentado.",
    },
    "help.ringo.ring_diameter": {
        Language.ENGLISH: "Diameter of the matching ring.",
        Language.SPANISH: "Diámetro del anillo de adaptación.",
    },
    "help.ringo.ring_height": {
        Language.ENGLISH: "Height of the matching ring above ground.",
        Language.SPANISH: "Altura del anillo de adaptación sobre el suelo.",
    },
    "help.scv.kind": {
        Language.ENGLISH: "Self-contained vertical variant: half square or bobtail curtain.",
        Language.SPANISH: "Variante vertical autocontenida: media cuadrada o cortina bobtail.",
    },
    "help.scv.feed_offset": {
        Language.ENGLISH: "Feed-point distance below the top corner.",
        Language.SPANISH: "Distancia del punto de alimentación por debajo de la esquina superior.",
    },
    "help.t2fd.termination": {
        Language.ENGLISH: (
            "Termination resistance at the far end; it dissipates part of the input power."
        ),
        Language.SPANISH: (
            "Resistencia de terminación en el extremo lejano; disipa parte de la "
            "potencia de entrada."
        ),
    },
    "help.t2fd.transformer": {
        Language.ENGLISH: "Ideal transformer ratio at the feed.",
        Language.SPANISH: "Relación ideal del transformador en la alimentación.",
    },
    "help.trap_dipole.trap_frequency": {
        Language.ENGLISH: "Trap resonant frequency.",
        Language.SPANISH: "Frecuencia de resonancia de la trampa.",
    },
    "help.trap_dipole.trap_inductance": {
        Language.ENGLISH: ("Trap inductance; the capacitance is derived from the trap frequency."),
        Language.SPANISH: (
            "Inductancia de la trampa; la capacitancia se deriva de la frecuencia de la trampa."
        ),
    },
    "help.trap_dipole.trap_capacitance": {
        Language.ENGLISH: "Trap capacitance derived from the trap frequency and inductance.",
        Language.SPANISH: "Capacitancia derivada de la frecuencia y la inductancia de la trampa.",
    },
    "help.trap_yagi.high_band_frequency": {
        Language.ENGLISH: "High-band design frequency for the trapped elements.",
        Language.SPANISH: "Frecuencia de diseño de banda alta para los elementos con trampas.",
    },
    "help.trap_yagi.trap_frequency": {
        Language.ENGLISH: "Trap resonant frequency.",
        Language.SPANISH: "Frecuencia de resonancia de la trampa.",
    },
    "help.trap_yagi.trap_inductance": {
        Language.ENGLISH: ("Trap inductance; the capacitance is derived from the trap frequency."),
        Language.SPANISH: (
            "Inductancia de la trampa; la capacitancia se deriva de la frecuencia de la trampa."
        ),
    },
    "help.trap_yagi.trap_inset": {
        Language.ENGLISH: "Distance from the element center to each trap.",
        Language.SPANISH: "Distancia desde el centro del elemento hasta cada trampa.",
    },
    "help.vertical.radial_system": {
        Language.ENGLISH: ("Radial model; it changes the ground return and the modeled pattern."),
        Language.SPANISH: ("Modelo de radiales; cambia el retorno de tierra y el patrón modelado."),
    },
    "help.vertical.radial_count": {
        Language.ENGLISH: "Number of radials.",
        Language.SPANISH: "Cantidad de radiales.",
    },
    "help.vertical.radial_length": {
        Language.ENGLISH: "Radial length.",
        Language.SPANISH: "Longitud de los radiales.",
    },
    "help.vertical.radial_angle": {
        Language.ENGLISH: "Azimuth step between radials.",
        Language.SPANISH: "Paso de azimut entre radiales.",
    },
    "help.vertical.loading_coil_inductance": {
        Language.ENGLISH: "Loading-coil inductance.",
        Language.SPANISH: "Inductancia de la bobina de carga.",
    },
    "help.vertical.loading_coil_offset": {
        Language.ENGLISH: "Distance from the base to the loading coil.",
        Language.SPANISH: "Distancia desde la base hasta la bobina de carga.",
    },
    "help.vertical.loading_coil_resistance": {
        Language.ENGLISH: "Series resistance of the loading coil; zero keeps it ideal.",
        Language.SPANISH: "Resistencia serie de la bobina de carga; cero la mantiene ideal.",
    },
    "help.vertical.top_hat_radius": {
        Language.ENGLISH: "Top-hat radius.",
        Language.SPANISH: "Radio del sombrero capacitivo.",
    },
    "help.vertical.top_hat_wires": {
        Language.ENGLISH: "Number of top-hat wires.",
        Language.SPANISH: "Cantidad de hilos del sombrero capacitivo.",
    },
    "help.yagi.match_type": {
        Language.ENGLISH: "Matching method; beta/hairpin adds a shorted stub.",
        Language.SPANISH: "Método de adaptación; beta/hairpin agrega un stub en cortocircuito.",
    },
    "help.yagi.match_length": {
        Language.ENGLISH: "Hairpin stub length.",
        Language.SPANISH: "Longitud del stub en horquilla.",
    },
    "help.yagi.match_spacing": {
        Language.ENGLISH: "Hairpin stub spacing.",
        Language.SPANISH: "Separación del stub en horquilla.",
    },
    "help.yagi.taper_length": {
        Language.ENGLISH: "Optional tapered tip length; zero keeps a straight element.",
        Language.SPANISH: "Longitud opcional de la punta cónica; cero mantiene el elemento recto.",
    },
    "help.yagi.taper_radius": {
        Language.ENGLISH: "Radius at the tapered tip.",
        Language.SPANISH: "Radio en la punta cónica.",
    },
    "help.yagi.fold_spacing": {
        Language.ENGLISH: "Spacing between the two conductors of the folded driven element.",
        Language.SPANISH: "Separación entre los dos conductores del elemento alimentado plegado.",
    },
    "help.zepp.impedance": {
        Language.ENGLISH: "Characteristic impedance of the matching stub.",
        Language.SPANISH: "Impedancia característica del stub de adaptación.",
    },
    "help.zepp.matching_length": {
        Language.ENGLISH: "Physical length of the matching stub.",
        Language.SPANISH: "Longitud física del stub de adaptación.",
    },
    "help.zepp.spacing": {
        Language.ENGLISH: "Spacing between the radiator and matching stub.",
        Language.SPANISH: "Separación entre el radiador y el stub de adaptación.",
    },
    "help.inverted_v.included_angle": {
        Language.ENGLISH: "Angle between the two legs at the apex.",
        Language.SPANISH: "Ángulo entre las dos patas en el vértice.",
    },
    "help.feed_line.characteristic_impedance": {
        Language.ENGLISH: (
            "Characteristic impedance of the feed line; it sets the transformation and "
            "the SWR at the transmitter end."
        ),
        Language.SPANISH: (
            "Impedancia característica de la línea; define la transformación y la ROE "
            "en el extremo del transmisor."
        ),
    },
    "help.feed_line.length": {
        Language.ENGLISH: "Physical feed-line length.",
        Language.SPANISH: "Longitud física de la línea de alimentación.",
    },
    "help.feed_line.velocity_factor": {
        Language.ENGLISH: (
            "Velocity factor of the feed line; it sets the electrical length for a "
            "given physical length."
        ),
        Language.SPANISH: (
            "Factor de velocidad de la línea; define la longitud eléctrica para una "
            "longitud física dada."
        ),
    },
    "help.feed_line.loss": {
        Language.ENGLISH: "Matched loss per 100 m at the operating frequency.",
        Language.SPANISH: "Pérdida adaptada por 100 m en la frecuencia de operación.",
    },
    "help.balun_loss.reference_frequency": {
        Language.ENGLISH: "Frequency at which the reference insertion loss is specified.",
        Language.SPANISH: "Frecuencia en la que se especifica la pérdida de inserción de referencia.",
    },
    "help.balun_loss.reference_loss": {
        Language.ENGLISH: "Matched insertion loss at the reference frequency.",
        Language.SPANISH: "Pérdida de inserción adaptada en la frecuencia de referencia.",
    },
    "help.balun_loss.exponent": {
        Language.ENGLISH: (
            "Frequency exponent used to scale the loss away from the reference frequency."
        ),
        Language.SPANISH: (
            "Exponente de frecuencia usado para escalar la pérdida fuera de la "
            "frecuencia de referencia."
        ),
    },
    "help.loads.kind": {
        Language.ENGLISH: "Load type: series or parallel; trap loads combine inductance and capacitance.",
        Language.SPANISH: "Tipo de carga: serie o paralelo; las trampas combinan inductancia y capacitancia.",
    },
    "help.loads.wire": {
        Language.ENGLISH: "Wire that carries the load.",
        Language.SPANISH: "Hilo que lleva la carga.",
    },
    "help.loads.offset": {
        Language.ENGLISH: "Distance from the wire start to the load.",
        Language.SPANISH: "Distancia desde el inicio del hilo hasta la carga.",
    },
    "help.loads.resistance": {
        Language.ENGLISH: "Load resistance.",
        Language.SPANISH: "Resistencia de la carga.",
    },
    "help.loads.inductance": {
        Language.ENGLISH: "Load inductance.",
        Language.SPANISH: "Inductancia de la carga.",
    },
    "help.loads.capacitance": {
        Language.ENGLISH: "Load capacitance.",
        Language.SPANISH: "Capacitancia de la carga.",
    },
    "help.loads.trap_frequency": {
        Language.ENGLISH: "Resonant frequency of the parallel LC trap.",
        Language.SPANISH: "Frecuencia de resonancia de la trampa LC paralelo.",
    },
    "help.transmission_lines.start_wire": {
        Language.ENGLISH: "Wire where the transmission line starts.",
        Language.SPANISH: "Hilo donde comienza la línea de transmisión.",
    },
    "help.transmission_lines.start_offset": {
        Language.ENGLISH: "Distance from the start wire's beginning to the line connection.",
        Language.SPANISH: "Distancia desde el inicio del hilo hasta la conexión de la línea.",
    },
    "help.transmission_lines.end_wire": {
        Language.ENGLISH: "Wire where the transmission line ends.",
        Language.SPANISH: "Hilo donde termina la línea de transmisión.",
    },
    "help.transmission_lines.end_offset": {
        Language.ENGLISH: "Distance from the end wire's beginning to the line connection.",
        Language.SPANISH: "Distancia desde el inicio del hilo final hasta la conexión de la línea.",
    },
    "help.transmission_lines.z0": {
        Language.ENGLISH: "Characteristic impedance of the transmission line.",
        Language.SPANISH: "Impedancia característica de la línea de transmisión.",
    },
    "help.transmission_lines.length": {
        Language.ENGLISH: "Physical transmission-line length.",
        Language.SPANISH: "Longitud física de la línea de transmisión.",
    },
    "help.transmission_lines.velocity_factor": {
        Language.ENGLISH: "Velocity factor used to convert physical length to electrical length.",
        Language.SPANISH: "Factor de velocidad usado para convertir longitud física en eléctrica.",
    },
    "help.synthesis.target_frequency": {
        Language.ENGLISH: "Frequency at which the impedance target is evaluated.",
        Language.SPANISH: "Frecuencia en la que se evalúa el objetivo de impedancia.",
    },
    "help.synthesis.target_resistance": {
        Language.ENGLISH: "Target feed-point resistance.",
        Language.SPANISH: "Resistencia objetivo en el punto de alimentación.",
    },
    "help.synthesis.target_reactance": {
        Language.ENGLISH: "Target feed-point reactance.",
        Language.SPANISH: "Reactancia objetivo en el punto de alimentación.",
    },
    "help.synthesis.minimum": {
        Language.ENGLISH: "Lower bound for the selected synthesis variable.",
        Language.SPANISH: "Límite inferior de la variable de síntesis seleccionada.",
    },
    "help.synthesis.maximum": {
        Language.ENGLISH: "Upper bound for the selected synthesis variable.",
        Language.SPANISH: "Límite superior de la variable de síntesis seleccionada.",
    },
    "help.optimize.objective": {
        Language.ENGLISH: "Objective used to rank optimization candidates.",
        Language.SPANISH: "Objetivo usado para ordenar los candidatos de optimización.",
    },
    "help.optimize.min_length": {
        Language.ENGLISH: "Lower bound for the optimized dimension.",
        Language.SPANISH: "Límite inferior de la dimensión optimizada.",
    },
    "help.optimize.max_length": {
        Language.ENGLISH: "Upper bound for the optimized dimension.",
        Language.SPANISH: "Límite superior de la dimensión optimizada.",
    },
    "help.optimize.target_resistance": {
        Language.ENGLISH: "Target resistance for the impedance objective.",
        Language.SPANISH: "Resistencia objetivo para el objetivo de impedancia.",
    },
    "help.optimize.target_reactance": {
        Language.ENGLISH: "Target reactance for the reactance objective.",
        Language.SPANISH: "Reactancia objetivo para el objetivo de reactancia.",
    },
    "help.optimize.swr_limit": {
        Language.ENGLISH: "SWR limit used by the bandwidth objective.",
        Language.SPANISH: "Límite de ROE usado por el objetivo de ancho de banda.",
    },
    "help.optimize.swr_weight": {
        Language.ENGLISH: "Relative SWR weight in the balanced objective.",
        Language.SPANISH: "Peso relativo de la ROE en el objetivo balanceado.",
    },
    "help.optimize.gain_weight": {
        Language.ENGLISH: "Relative gain weight in the balanced objective.",
        Language.SPANISH: "Peso relativo de la ganancia en el objetivo balanceado.",
    },
    "help.optimize.max_evaluations": {
        Language.ENGLISH: "Maximum number of solver evaluations.",
        Language.SPANISH: "Cantidad máxima de evaluaciones del solver.",
    },
    "help.optimize.tolerance": {
        Language.ENGLISH: "Convergence tolerance for the selected objective.",
        Language.SPANISH: "Tolerancia de convergencia para el objetivo seleccionado.",
    },
    "help.custom.feed_wire": {
        Language.ENGLISH: "Wire selected for the feed point.",
        Language.SPANISH: "Hilo seleccionado para el punto de alimentación.",
    },
    "help.custom.feed_offset": {
        Language.ENGLISH: "Distance from the wire start to the feed point.",
        Language.SPANISH: "Distancia desde el inicio del hilo hasta el punto de alimentación.",
    },
    "help.custom.radial_count": {
        Language.ENGLISH: "Number of radial wires.",
        Language.SPANISH: "Cantidad de hilos radiales.",
    },
    "help.custom.radial_length": {
        Language.ENGLISH: "Radial wire length.",
        Language.SPANISH: "Longitud de los hilos radiales.",
    },
    "help.custom.radial_angle": {
        Language.ENGLISH: "Azimuth step between radial wires.",
        Language.SPANISH: "Paso de azimut entre hilos radiales.",
    },
    "help.measurement.name": {
        Language.ENGLISH: "Label used for this measurement.",
        Language.SPANISH: "Etiqueta usada para esta medición.",
    },
    "help.measurement.calibration": {
        Language.ENGLISH: "Calibration type recorded with the measurement.",
        Language.SPANISH: "Tipo de calibración registrado con la medición.",
    },
    "help.measurement.reference_plane": {
        Language.ENGLISH: "Reference plane of the measurement.",
        Language.SPANISH: "Plano de referencia de la medición.",
    },
    "help.measurement.feed_line": {
        Language.ENGLISH: "Feed line associated with the measurement.",
        Language.SPANISH: "Línea de alimentación asociada con la medición.",
    },
    "help.measurement.notes": {
        Language.ENGLISH: "Free-form notes stored with the measurement.",
        Language.SPANISH: "Notas libres guardadas con la medición.",
    },
    "help.matching_network.topology": {
        Language.ENGLISH: "Matching-network topology; it determines which component fields apply.",
        Language.SPANISH: "Topología de la red de adaptación; determina qué campos de componentes se usan.",
    },
    "help.matching_network.position": {
        Language.ENGLISH: (
            "Place the network at the antenna feedpoint or in the shack before "
            "the feed line. A shack tuner makes the line carry a high SWR."
        ),
        Language.SPANISH: (
            "Ubicá la red en el punto de alimentación o en la estación antes de la "
            "línea. Un sintonizador de shack hace que la línea transporte ROE alta."
        ),
    },
    "help.matching_network.q_factor": {
        Language.ENGLISH: "Component Q used to estimate matching-network loss.",
        Language.SPANISH: "Q de los componentes usado para estimar las pérdidas de la red.",
    },
    "help.matching_network.load_r": {
        Language.ENGLISH: "Load resistance presented to the matching network.",
        Language.SPANISH: "Resistencia de carga presentada a la red de adaptación.",
    },
    "help.matching_network.load_x": {
        Language.ENGLISH: "Load reactance presented to the matching network.",
        Language.SPANISH: "Reactancia de carga presentada a la red de adaptación.",
    },
    "help.matching_network.frequency": {
        Language.ENGLISH: "Frequency used to compute the component values.",
        Language.SPANISH: "Frecuencia usada para calcular los valores de los componentes.",
    },
    "help.matching_network.source_impedance": {
        Language.ENGLISH: "Real source impedance the network is designed to match.",
        Language.SPANISH: "Impedancia real de la fuente a la que se adapta la red.",
    },
    "help.matching_network.design_origin": {
        Language.ENGLISH: "Where the stored design target came from.",
        Language.SPANISH: "Origen del objetivo de diseño guardado.",
    },
    "help.matching_network.use_current_point": {
        Language.ENGLISH: (
            "Copy frequency and the raw feed impedance from the current simulation "
            "result into the design target."
        ),
        Language.SPANISH: (
            "Copia la frecuencia y la impedancia cruda de alimentación del resultado "
            "de simulación actual al objetivo de diseño."
        ),
    },
    "help.matching_network.auto_design": {
        Language.ENGLISH: "Compute a lossless L network for the current design target.",
        Language.SPANISH: "Calcula una red L sin pérdidas para el objetivo de diseño actual.",
    },
    "help.matching_network.shunt_at_input": {
        Language.ENGLISH: "Place the L-network shunt element on the transmitter side.",
        Language.SPANISH: "Coloca el elemento en derivación de la red L del lado del transmisor.",
    },
    "help.results.create_matching_network": {
        Language.ENGLISH: (
            "Create a project matching network from the raw primary-side feed "
            "impedance of the selected frequency row."
        ),
        Language.SPANISH: (
            "Crea una red de adaptación del proyecto desde la impedancia cruda de "
            "alimentación del lado primario de la fila de frecuencia seleccionada."
        ),
    },
    "help.matching_network.series_l": {
        Language.ENGLISH: "Series inductance in the matching network.",
        Language.SPANISH: "Inductancia serie de la red de adaptación.",
    },
    "help.matching_network.series_c": {
        Language.ENGLISH: "Series capacitance in the matching network.",
        Language.SPANISH: "Capacitancia serie de la red de adaptación.",
    },
    "help.matching_network.shunt_l": {
        Language.ENGLISH: "Shunt inductance at the selected node.",
        Language.SPANISH: "Inductancia en derivación en el nodo seleccionado.",
    },
    "help.matching_network.shunt_c": {
        Language.ENGLISH: "Shunt capacitance at the selected node.",
        Language.SPANISH: "Capacitancia en derivación en el nodo seleccionado.",
    },
    "help.matching_network.input_shunt_l": {
        Language.ENGLISH: "Shunt inductance on the input side.",
        Language.SPANISH: "Inductancia en derivación del lado de entrada.",
    },
    "help.matching_network.input_shunt_c": {
        Language.ENGLISH: "Shunt capacitance on the input side.",
        Language.SPANISH: "Capacitancia en derivación del lado de entrada.",
    },
    "help.matching_network.output_shunt_l": {
        Language.ENGLISH: "Shunt inductance on the output side.",
        Language.SPANISH: "Inductancia en derivación del lado de salida.",
    },
    "help.matching_network.output_shunt_c": {
        Language.ENGLISH: "Shunt capacitance on the output side.",
        Language.SPANISH: "Capacitancia en derivación del lado de salida.",
    },
    "help.matching_network.input_series_l": {
        Language.ENGLISH: "Series inductance on the input side.",
        Language.SPANISH: "Inductancia serie del lado de entrada.",
    },
    "help.matching_network.input_series_c": {
        Language.ENGLISH: "Series capacitance on the input side.",
        Language.SPANISH: "Capacitancia serie del lado de entrada.",
    },
    "help.matching_network.output_series_l": {
        Language.ENGLISH: "Series inductance on the output side.",
        Language.SPANISH: "Inductancia serie del lado de salida.",
    },
    "help.matching_network.output_series_c": {
        Language.ENGLISH: "Series capacitance on the output side.",
        Language.SPANISH: "Capacitancia serie del lado de salida.",
    },
    "help.section.design": {
        Language.ENGLISH: (
            "Antenna type, template, geometry, feed, ground, and the apply, estimate, "
            "and optimize actions."
        ),
        Language.SPANISH: (
            "Tipo de antena, plantilla, geometría, alimentación, suelo y las acciones "
            "de aplicar, estimar y optimizar."
        ),
    },
    "help.section.advanced": {
        Language.ENGLISH: (
            "Solver timeout, frequency sweep, pattern resolution, and band-analysis controls."
        ),
        Language.SPANISH: (
            "Tiempo límite del solver, barrido de frecuencia, resolución de patrón y "
            "controles de análisis por banda."
        ),
    },
    "help.section.solver": {
        Language.ENGLISH: (
            "Per-run solver timeout. It limits each NEC process and does not change the model."
        ),
        Language.SPANISH: (
            "Tiempo límite por corrida. Limita cada proceso NEC y no cambia el modelo."
        ),
    },
    "help.section.sweep": {
        Language.ENGLISH: "Frequency range used for the impedance and SWR sweep.",
        Language.SPANISH: "Rango de frecuencias usado para el barrido de impedancia y ROE.",
    },
    "help.section.pattern": {
        Language.ENGLISH: (
            "Far-field pattern resolution and the frequencies used for pattern snapshots."
        ),
        Language.SPANISH: (
            "Resolución del patrón de campo lejano y las frecuencias usadas para las "
            "capturas de patrón."
        ),
    },
    "help.section.band": {
        Language.ENGLISH: "Select and run the amateur bands analyzed for the current design.",
        Language.SPANISH: "Seleccioná y ejecutá las bandas de radioaficionado analizadas para el diseño actual.",
    },
    "help.section.geometry": {
        Language.ENGLISH: "Dimensioned construction view and 3D view of the canonical wire model.",
        Language.SPANISH: "Vista de construcción acotada y vista 3D del modelo de hilos canónico.",
    },
    "help.section.feed_matching": {
        Language.ENGLISH: (
            "Internal EFHW matching, project matching network, feed line, and balun "
            "loss for the current design."
        ),
        Language.SPANISH: (
            "Adaptación interna del EFHW, red de adaptación del proyecto, línea de "
            "alimentación y pérdida del balun para el diseño actual."
        ),
    },
    "help.section.workflow": {
        Language.ENGLISH: "Current recommendation and the next action for this design.",
        Language.SPANISH: "Recomendación actual y próxima acción para este diseño.",
    },
    "help.section.installation": {
        Language.ENGLISH: "Active installation profile: site envelope, support, ground, and notes.",
        Language.SPANISH: "Perfil de instalación activo: entorno, soporte, suelo y notas del sitio.",
    },
    "help.action.installation_profile": {
        Language.ENGLISH: "Create, edit, duplicate, or activate an installation profile.",
        Language.SPANISH: "Creá, editá, duplicá o activá un perfil de instalación.",
    },
    "help.action.feed_chain": {
        Language.ENGLISH: "Show the feed-chain stages and their dissipative losses.",
        Language.SPANISH: "Mostrá las etapas de la cadena y sus pérdidas disipativas.",
    },
    "help.action.component_calculator": {
        Language.ENGLISH: "Open coil, trap, balun, and conductor construction calculators.",
        Language.SPANISH: "Abrí calculadoras de bobina, trampa, balun y conductor.",
    },
    "help.action.measurement_sessions": {
        Language.ENGLISH: (
            "Group measurements into field sessions and compare them before and after tuning."
        ),
        Language.SPANISH: (
            "Agrupá mediciones en sesiones de campo y comparalas antes y después de ajustar."
        ),
    },
    "help.action.tuning_assistant": {
        Language.ENGLISH: (
            "Estimate a bounded primary-dimension change from a measured reference and solver sensitivity."
        ),
        Language.SPANISH: (
            "Estimá un cambio acotado de la dimensión principal a partir de una referencia "
            "medida y la sensibilidad del solver."
        ),
    },
    "help.tuning.measurement": {
        Language.ENGLISH: "Measurement used for the current physical reference.",
        Language.SPANISH: "Medición usada como referencia física actual.",
    },
    "help.tuning.target": {
        Language.ENGLISH: "Frequency the tuned antenna should reach.",
        Language.SPANISH: "Frecuencia que debería alcanzar la antena ajustada.",
    },
    "help.tuning.current_dimension": {
        Language.ENGLISH: "Primary family dimension that the assistant will adjust.",
        Language.SPANISH: "Dimensión principal de la familia que ajustará el asistente.",
    },
    "help.tuning.max_adjustment": {
        Language.ENGLISH: "Hard bound on the proposed change; the estimate is clipped to this value.",
        Language.SPANISH: "Límite duro del cambio propuesto; la estimación se recorta a este valor.",
    },
    "help.tuning.analyze": {
        Language.ENGLISH: "Run the bounded solver probes and build a proposal.",
        Language.SPANISH: "Ejecutá las sondas acotadas del solver y generá una propuesta.",
    },
    "help.tuning.cancel": {
        Language.ENGLISH: "Stop the running solver probes.",
        Language.SPANISH: "Detené las sondas del solver en ejecución.",
    },
    "help.tuning.apply": {
        Language.ENGLISH: "Apply the proposed primary dimension to the design.",
        Language.SPANISH: "Aplicá la dimensión principal propuesta al diseño.",
    },
    "help.tuning.table": {
        Language.ENGLISH: "Solver probes at the current, lower, higher, and proposed dimensions.",
        Language.SPANISH: "Sondas del solver en la dimensión actual, menor, mayor y propuesta.",
    },
    "help.tuning.assumptions": {
        Language.ENGLISH: "The estimate is local and model-based; verify with a new measurement.",
        Language.SPANISH: "La estimación es local y basada en el modelo; verificá con una nueva medición.",
    },
    "help.measurement.session": {
        Language.ENGLISH: "Optional field session that groups measurements taken under the same setup.",
        Language.SPANISH: "Sesión de campo opcional que agrupa mediciones tomadas con la misma instalación.",
    },
    "help.measurement.sessions": {
        Language.ENGLISH: "Open the measurement timeline and session manager.",
        Language.SPANISH: "Abrí la línea de tiempo y el gestor de sesiones de medición.",
    },
    "help.measurement.compare": {
        Language.ENGLISH: "Compare two measurements on their overlapping frequency range.",
        Language.SPANISH: "Compará dos mediciones en su rango de frecuencia superpuesto.",
    },
    "help.measurement.tune": {
        Language.ENGLISH: "Estimate a bounded dimension change from this measurement and the solver.",
        Language.SPANISH: "Estimá un cambio acotado de dimensión desde esta medición y el solver.",
    },
    "help.measurement.session.name": {
        Language.ENGLISH: "Name shown in the timeline and measurement selector.",
        Language.SPANISH: "Nombre que aparece en la línea de tiempo y el selector.",
    },
    "help.measurement.session.date": {
        Language.ENGLISH: "Date and time of the field session.",
        Language.SPANISH: "Fecha y hora de la sesión de campo.",
    },
    "help.measurement.session.design": {
        Language.ENGLISH: "Design measured in this session; optional.",
        Language.SPANISH: "Diseño medido en esta sesión; opcional.",
    },
    "help.measurement.session.location": {
        Language.ENGLISH: "Site or location of the session.",
        Language.SPANISH: "Sitio o ubicación de la sesión.",
    },
    "help.measurement.session.conditions": {
        Language.ENGLISH: "Ground, weather, height, and other conditions.",
        Language.SPANISH: "Suelo, clima, altura y otras condiciones.",
    },
    "help.measurement.session.notes": {
        Language.ENGLISH: "What changed or what to remember about the session.",
        Language.SPANISH: "Qué cambió o qué recordar de la sesión.",
    },
    "help.measurement.sessions.timeline": {
        Language.ENGLISH: "Sessions ordered by date; unassigned measurements appear at the end.",
        Language.SPANISH: "Sesiones ordenadas por fecha; las mediciones sin sesión aparecen al final.",
    },
    "help.measurement.sessions.details": {
        Language.ENGLISH: "Selected session date, design, location, conditions, and notes.",
        Language.SPANISH: "Fecha, diseño, ubicación, condiciones y notas de la sesión.",
    },
    "help.measurement.sessions.table": {
        Language.ENGLISH: "Measurements in the selected session.",
        Language.SPANISH: "Mediciones de la sesión seleccionada.",
    },
    "help.measurement.sessions.new": {
        Language.ENGLISH: "Create a field session.",
        Language.SPANISH: "Crear una sesión de campo.",
    },
    "help.measurement.sessions.edit": {
        Language.ENGLISH: "Change the selected session.",
        Language.SPANISH: "Cambiar la sesión seleccionada.",
    },
    "help.measurement.sessions.delete": {
        Language.ENGLISH: "Delete the session and keep its measurements as unassigned.",
        Language.SPANISH: "Eliminar la sesión y conservar sus mediciones sin sesión.",
    },
    "help.measurement.sessions.edit_measurement": {
        Language.ENGLISH: "Edit the selected measurement or assign it to a session.",
        Language.SPANISH: "Editar la medición seleccionada o asignarla a una sesión.",
    },
    "help.measurement.sessions.compare": {
        Language.ENGLISH: "Compare two measurements from any session.",
        Language.SPANISH: "Comparar dos mediciones de cualquier sesión.",
    },
    "help.measurement.comparison.reference": {
        Language.ENGLISH: "Reference impedance used for both SWR curves; it does not change R or X.",
        Language.SPANISH: "Impedancia de referencia usada para ambas curvas de ROE; no cambia R ni X.",
    },
    "help.measurement.comparison.before": {
        Language.ENGLISH: "Baseline measurement.",
        Language.SPANISH: "Medición de referencia.",
    },
    "help.measurement.comparison.after": {
        Language.ENGLISH: "Measurement after the change.",
        Language.SPANISH: "Medición después del cambio.",
    },
    "help.measurement.comparison.summary": {
        Language.ENGLISH: "Compared points and mean/max impedance change.",
        Language.SPANISH: "Puntos comparados y cambio medio/máximo de impedancia.",
    },
    "help.measurement.comparison.table": {
        Language.ENGLISH: "Aligned frequency, R, X, SWR, and deltas for both measurements.",
        Language.SPANISH: "Frecuencia, R, X, ROE y diferencias alineadas para ambas mediciones.",
    },
    "help.measurement.comparison.plot": {
        Language.ENGLISH: "SWR before and after at the comparison reference impedance.",
        Language.SPANISH: "ROE antes y después con la impedancia de referencia elegida.",
    },
    "help.component_calculator.coil": {
        Language.ENGLISH: "Wheeler air-core coil approximation and turns estimate.",
        Language.SPANISH: "Aproximación de Wheeler para bobina de aire y estimación de vueltas.",
    },
    "help.component_calculator.trap": {
        Language.ENGLISH: "Ideal LC trap resonance and reactance calculation.",
        Language.SPANISH: "Resonancia y reactancia ideales de una trampa LC.",
    },
    "help.component_calculator.balun": {
        Language.ENGLISH: "Ideal turns ratio and impedance ratio relation.",
        Language.SPANISH: "Relación ideal entre vueltas e impedancias.",
    },
    "help.component_calculator.conductor": {
        Language.ENGLISH: "Compare DC and approximate RF conductor resistance.",
        Language.SPANISH: "Compará resistencia CC y RF aproximada de conductores.",
    },
    "help.component_calculator.choke": {
        Language.ENGLISH: "Reference notes for common-mode chokes; no numeric model.",
        Language.SPANISH: "Notas de referencia sobre chokes de modo común; sin modelo numérico.",
    },
    "help.component_calculator.inductance": {
        Language.ENGLISH: "Target or calculated inductance in microhenries.",
        Language.SPANISH: "Inductancia objetivo o calculada en microhenrios.",
    },
    "help.component_calculator.diameter": {
        Language.ENGLISH: "Coil form or conductor diameter in the current units.",
        Language.SPANISH: "Diámetro del soporte o conductor en las unidades actuales.",
    },
    "help.component_calculator.winding_length": {
        Language.ENGLISH: "Physical length of the single-layer winding.",
        Language.SPANISH: "Longitud física del bobinado de una capa.",
    },
    "help.component_calculator.turns": {
        Language.ENGLISH: "Number of turns in the coil.",
        Language.SPANISH: "Cantidad de vueltas de la bobina.",
    },
    "help.component_calculator.frequency": {
        Language.ENGLISH: "Operating or resonant frequency.",
        Language.SPANISH: "Frecuencia de operación o resonancia.",
    },
    "help.component_calculator.capacitance": {
        Language.ENGLISH: "Capacitance in picofarads.",
        Language.SPANISH: "Capacitancia en picofaradios.",
    },
    "help.component_calculator.turns_ratio": {
        Language.ENGLISH: "Ideal transformer turns ratio.",
        Language.SPANISH: "Relación de vueltas del transformador ideal.",
    },
    "help.component_calculator.impedance_ratio": {
        Language.ENGLISH: "Ideal impedance transformation ratio.",
        Language.SPANISH: "Relación de transformación de impedancia ideal.",
    },
    "help.component_calculator.material": {
        Language.ENGLISH: "Conductor material preset.",
        Language.SPANISH: "Preset de material conductor.",
    },
    "help.component_calculator.use": {
        Language.ENGLISH: "Return the coil or trap result to the load editor.",
        Language.SPANISH: "Devolver el resultado de bobina o trampa al editor de cargas.",
    },
    "help.component_calculator.calculate": {
        Language.ENGLISH: "Calculate the conductor comparison.",
        Language.SPANISH: "Calcular la comparación de conductores.",
    },
    "help.loads.calculator": {
        Language.ENGLISH: "Open a coil or trap calculator seeded from these load fields.",
        Language.SPANISH: "Abrí una calculadora de bobina o trampa con estos campos.",
    },
    "help.action.preflight": {
        Language.ENGLISH: (
            "Pre-flight check of geometry, feedpoint, segmentation, site, "
            "simulation, and construction data before building."
        ),
        Language.SPANISH: (
            "Revisá geometría, alimentación, segmentación, sitio, simulación y "
            "datos de construcción antes de construir."
        ),
    },
    "help.preflight.table": {
        Language.ENGLISH: "Findings grouped by severity, with the affected item and the suggested fix.",
        Language.SPANISH: "Hallazgos agrupados por severidad, con el elemento afectado y la corrección sugerida.",
    },
    "help.preflight.status": {
        Language.ENGLISH: "Overall readiness. Any error blocks a ready-to-build result.",
        Language.SPANISH: "Preparación general. Cualquier error impide declarar listo para construir.",
    },
    "help.preflight.go_to": {
        Language.ENGLISH: "Close this report and open the editor that can resolve the selected finding.",
        Language.SPANISH: "Cerrá este informe y abrí el editor que puede resolver el hallazgo seleccionado.",
    },
    "help.action.construction_record": {
        Language.ENGLISH: "Record as-built dimensions, notes, and the construction checklist.",
        Language.SPANISH: "Registrá dimensiones as-built, notas y la lista de control.",
    },
    "help.construction_record.notes": {
        Language.ENGLISH: "Free notes about the actual build and any deviations from the design.",
        Language.SPANISH: "Notas libres sobre la construcción real y desvíos del diseño.",
    },
    "help.construction_record.dimensions": {
        Language.ENGLISH: "Compare design and measured dimensions; differences use the current units.",
        Language.SPANISH: "Compará dimensiones de diseño y medidas; las diferencias usan las unidades actuales.",
    },
    "help.construction_record.checklist": {
        Language.ENGLISH: "Mark the construction, safety, and measurement checks you completed.",
        Language.SPANISH: "Marcá las verificaciones de construcción, seguridad y medición completadas.",
    },
    "help.construction_record.add": {
        Language.ENGLISH: "Add a measured dimension row.",
        Language.SPANISH: "Agregá una fila de dimensión medida.",
    },
    "help.construction_record.remove": {
        Language.ENGLISH: "Remove the selected measured dimension row.",
        Language.SPANISH: "Quitá la fila de dimensión medida seleccionada.",
    },
    "help.feed_chain.path": {
        Language.ENGLISH: "Order of the transmitter, matching network, feed line, and antenna.",
        Language.SPANISH: "Orden del transmisor, red de adaptación, línea y antena.",
    },
    "help.feed_chain.power": {
        Language.ENGLISH: "Transmitter power used to estimate power at the antenna and radiated power.",
        Language.SPANISH: "Potencia del transmisor usada para estimar la potencia en antena y radiada.",
    },
    "help.feed_chain.hint": {
        Language.ENGLISH: "Loss components are evaluated from the current simulation result.",
        Language.SPANISH: "Los componentes de pérdida se evalúan con el resultado actual.",
    },
    "help.table.feed_chain": {
        Language.ENGLISH: "Per-frequency SWR, mismatch, line, network, balun, delivered, and radiated power.",
        Language.SPANISH: "ROE, desadaptación, línea, red, balun, potencia entregada y radiada por frecuencia.",
    },
    "help.section.advisor": {
        Language.ENGLISH: "Bands, site limits, and practical preferences used to shortlist catalog antennas.",
        Language.SPANISH: "Bandas, límites del sitio y preferencias prácticas para preseleccionar antenas del catálogo.",
    },
    "help.action.antenna_advisor": {
        Language.ENGLISH: "Describe your needs and get a shortlist of catalog antennas.",
        Language.SPANISH: "Describí tus necesidades y obtené una preselección de antenas del catálogo.",
    },
    "help.action.new": {
        Language.ENGLISH: "Create a project from the antenna catalog.",
        Language.SPANISH: "Creá un proyecto desde el catálogo de antenas.",
    },
    "help.action.open": {
        Language.ENGLISH: "Open an existing .antennadesk project.",
        Language.SPANISH: "Abrí un proyecto .antennadesk existente.",
    },
    "help.advisor.bands": {
        Language.ENGLISH: "Select the amateur bands the antenna should cover.",
        Language.SPANISH: "Seleccioná las bandas de radioaficionado que debe cubrir la antena.",
    },
    "help.advisor.height": {
        Language.ENGLISH: "Maximum height available for the antenna, or Not specified.",
        Language.SPANISH: "Altura máxima disponible para la antena, o Sin especificar.",
    },
    "help.advisor.width": {
        Language.ENGLISH: "Maximum horizontal space available, or Not specified.",
        Language.SPANISH: "Espacio horizontal máximo disponible, o Sin especificar.",
    },
    "help.advisor.installation": {
        Language.ENGLISH: "Whether the antenna is permanent or must be easy to deploy and remove.",
        Language.SPANISH: "Si la antena es permanente o debe ser fácil de instalar y quitar.",
    },
    "help.advisor.intent": {
        Language.ENGLISH: "Main use: NVIS/local, regional, DX, or receive only.",
        Language.SPANISH: "Uso principal: NVIS/local, regional, DX o solo recepción.",
    },
    "help.advisor.complexity": {
        Language.ENGLISH: "Maximum construction and tuning effort you want.",
        Language.SPANISH: "Esfuerzo máximo de construcción y ajuste que querés asumir.",
    },
    "help.advisor.directionality": {
        Language.ENGLISH: "Prefer an omnidirectional antenna, a directional beam, or no preference.",
        Language.SPANISH: "Preferí una antena omnidireccional, un beam direccional o sin preferencia.",
    },
    "help.advisor.tuner": {
        Language.ENGLISH: "Allow designs that need an antenna tuner on some bands.",
        Language.SPANISH: "Permitir diseños que necesitan sintonizador en algunas bandas.",
    },
    "help.advisor.multiband": {
        Language.ENGLISH: "Require one antenna to cover all selected bands.",
        Language.SPANISH: "Exigir que una sola antena cubra todas las bandas seleccionadas.",
    },
    "help.advisor.find": {
        Language.ENGLISH: "Apply the constraints and show up to three catalog matches.",
        Language.SPANISH: "Aplicá las restricciones y mostrá hasta tres coincidencias del catálogo.",
    },
    "help.advisor.open": {
        Language.ENGLISH: "Open the selected antenna family in its normal editor.",
        Language.SPANISH: "Abrí la familia de antena seleccionada en su editor normal.",
    },
    "help.table.advisor": {
        Language.ENGLISH: "Shortlisted antennas, fit level, bands, space, height, feed, and build effort.",
        Language.SPANISH: "Antenas preseleccionadas, encaje, bandas, espacio, altura, alimentación y esfuerzo.",
    },
    "help.compare.designs": {
        Language.ENGLISH: "Select two to four designs to compare.",
        Language.SPANISH: "Seleccioná de dos a cuatro diseños para comparar.",
    },
    "help.compare.start": {
        Language.ENGLISH: "First frequency of the common comparison sweep.",
        Language.SPANISH: "Primera frecuencia del barrido común de comparación.",
    },
    "help.compare.stop": {
        Language.ENGLISH: "Last frequency of the common comparison sweep.",
        Language.SPANISH: "Última frecuencia del barrido común de comparación.",
    },
    "help.compare.points": {
        Language.ENGLISH: "Number of frequency points used for every design.",
        Language.SPANISH: "Cantidad de puntos de frecuencia usados para cada diseño.",
    },
    "help.compare.ground": {
        Language.ENGLISH: "Ground model applied to every design before recomputing.",
        Language.SPANISH: "Modelo de suelo aplicado a cada diseño antes de recalcular.",
    },
    "help.compare.reference_height": {
        Language.ENGLISH: "Common height, or Native heights to keep each design's height.",
        Language.SPANISH: "Altura común, o Alturas nativas para conservar la de cada diseño.",
    },
    "help.compare.reference_frequency": {
        Language.ENGLISH: "Frequency used for impedance, SWR, and pattern comparison.",
        Language.SPANISH: "Frecuencia usada para comparar impedancia, ROE y patrón.",
    },
    "help.compare.recompute": {
        Language.ENGLISH: "Re-run every selected design with the common basis.",
        Language.SPANISH: "Volvé a simular cada diseño con la base común.",
    },
    "help.table.comparison": {
        Language.ENGLISH: "Metric-by-design comparison table.",
        Language.SPANISH: "Tabla de métricas por diseño.",
    },
    "help.confidence.title": {
        Language.ENGLISH: "Evidence, modeled scope, limitations, and uncertainties for the current result.",
        Language.SPANISH: "Evidencia, alcance modelado, limitaciones e incertidumbres del resultado actual.",
    },
    "help.confidence.topic": {
        Language.ENGLISH: "Choose a result topic to read its practical meaning and limitations.",
        Language.SPANISH: "Elegí un tema del resultado para leer su significado práctico y sus límites.",
    },
    "help.installation.profiles": {
        Language.ENGLISH: "Saved profiles for this project; the selected one is active.",
        Language.SPANISH: "Perfiles guardados del proyecto; el seleccionado está activo.",
    },
    "help.installation.name": {
        Language.ENGLISH: "A short name for this site, such as Home, Portable, or Field day.",
        Language.SPANISH: "Un nombre corto para el sitio, como Casa, Portátil o Field day.",
    },
    "help.installation.available_height": {
        Language.ENGLISH: "Maximum height available for the antenna, or Not specified.",
        Language.SPANISH: "Altura máxima disponible para la antena, o Sin especificar.",
    },
    "help.installation.available_width": {
        Language.ENGLISH: "Maximum horizontal space available, or Not specified.",
        Language.SPANISH: "Espacio horizontal máximo disponible, o Sin especificar.",
    },
    "help.installation.orientation": {
        Language.ENGLISH: "Preferred installation orientation in degrees from north.",
        Language.SPANISH: "Orientación preferida de la instalación en grados desde el norte.",
    },
    "help.installation.support": {
        Language.ENGLISH: "Structure that supports the antenna: mast, tree, building, fence, or portable.",
        Language.SPANISH: "Estructura que soporta la antena: mástil, árbol, edificio, cerca o portátil.",
    },
    "help.installation.ground": {
        Language.ENGLISH: "Recommended site ground preset; it is not applied automatically.",
        Language.SPANISH: "Suelo de referencia recomendado para el sitio; no se aplica automáticamente.",
    },
    "help.installation.notes": {
        Language.ENGLISH: "Free notes about access, restrictions, supports, and site conditions.",
        Language.SPANISH: "Notas libres sobre acceso, restricciones, soportes y condiciones del sitio.",
    },
    "help.installation.image_reference": {
        Language.ENGLISH: "Optional local image path; the image is not embedded in the project.",
        Language.SPANISH: "Ruta local opcional de una imagen; la imagen no se incrusta en el proyecto.",
    },
    "help.installation.add": {
        Language.ENGLISH: "Add a new installation profile to this project.",
        Language.SPANISH: "Agregá un nuevo perfil de instalación al proyecto.",
    },
    "help.installation.duplicate": {
        Language.ENGLISH: "Copy the selected profile with a new name.",
        Language.SPANISH: "Copiá el perfil seleccionado con un nombre nuevo.",
    },
    "help.installation.remove": {
        Language.ENGLISH: "Remove the selected profile from this project.",
        Language.SPANISH: "Quitá el perfil seleccionado del proyecto.",
    },
    "help.action.next_step": {
        Language.ENGLISH: "Run the recommended next action for the current design.",
        Language.SPANISH: "Ejecutá la próxima acción recomendada para el diseño actual.",
    },
    "help.action.show_advanced": {
        Language.ENGLISH: "Reveal the full editor and advanced simulation controls.",
        Language.SPANISH: "Mostrá el editor completo y los controles de simulación avanzada.",
    },
    "help.mode.guided": {
        Language.ENGLISH: "Guided hides advanced options and shows one next step at a time.",
        Language.SPANISH: "Guiado oculta las opciones avanzadas y muestra un próximo paso por vez.",
    },
    "help.mode.standard": {
        Language.ENGLISH: "Standard shows the full editor with advanced options collapsed.",
        Language.SPANISH: "Estándar muestra el editor completo con las opciones avanzadas contraídas.",
    },
    "help.mode.advanced": {
        Language.ENGLISH: "Advanced expands the solver, sweep, pattern, and band-analysis controls.",
        Language.SPANISH: "Avanzado expande el solver, el barrido, el patrón y el análisis por banda.",
    },
    "help.preferences.workflow_mode": {
        Language.ENGLISH: "Guided, Standard, or Advanced control how much of the editor is visible.",
        Language.SPANISH: "Guiado, Estándar o Avanzado controlan cuánto del editor se muestra.",
    },
    "help.feed_matching.override": {
        Language.ENGLISH: (
            "The project matching network replaces the internal EFHW matching unit; "
            "the two networks are not cascaded."
        ),
        Language.SPANISH: (
            "La red del proyecto reemplaza la unidad de adaptación interna del EFHW; "
            "las dos redes no se conectan en cascada."
        ),
    },
    "help.feed_matching.remove": {
        Language.ENGLISH: (
            "Remove the project matching network and restore the internal EFHW matching unit."
        ),
        Language.SPANISH: (
            "Quita la red de adaptación del proyecto y restaura la unidad interna del EFHW."
        ),
    },
    "help.action.matching_network": {
        Language.ENGLISH: "Edit or create the project-wide L, Pi, or T matching network.",
        Language.SPANISH: "Edita o crea la red de adaptación L, Pi o T de todo el proyecto.",
    },
    "help.action.simulate": {
        Language.ENGLISH: "Save the current form values and run the solver.",
        Language.SPANISH: "Guardá los valores actuales del formulario y ejecutá el solver.",
    },
    "help.action.analyze_bands": {
        Language.ENGLISH: "Run the current design over a selected set of amateur bands.",
        Language.SPANISH: "Ejecutá el diseño actual sobre un conjunto seleccionado de bandas.",
    },
    "help.action.apply_design": {
        Language.ENGLISH: "Save the current form values without running the solver.",
        Language.SPANISH: "Guardá los valores actuales del formulario sin ejecutar el solver.",
    },
    "help.action.optimize": {
        Language.ENGLISH: "Open the family optimizer for the current design.",
        Language.SPANISH: "Abrí el optimizador de familia para el diseño actual.",
    },
    "help.tab.impedance": {
        Language.ENGLISH: "Impedance, SWR, and band charts.",
        Language.SPANISH: "Gráficos de impedancia, ROE y bandas.",
    },
    "help.tab.sources": {
        Language.ENGLISH: "Per-source voltage, current, impedance, and power for multi-source antennas.",
        Language.SPANISH: "Tensión, corriente, impedancia y potencia por fuente para antenas multifuente.",
    },
    "help.tab.pattern": {
        Language.ENGLISH: "Far-field polar and 3D radiation patterns.",
        Language.SPANISH: "Patrones de radiación de campo lejano en polar y 3D.",
    },
    "help.tab.currents": {
        Language.ENGLISH: "Wire current distribution.",
        Language.SPANISH: "Distribución de corriente en los hilos.",
    },
    "help.tab.measurements": {
        Language.ENGLISH: "Imported VNA measurements and comparison.",
        Language.SPANISH: "Mediciones VNA importadas y comparación.",
    },
    "help.tab.diagnostics": {
        Language.ENGLISH: "Solver warnings and validation messages.",
        Language.SPANISH: "Advertencias del solver y mensajes de validación.",
    },
    "help.tab.raw": {
        Language.ENGLISH: "Raw NEC input and solver output.",
        Language.SPANISH: "Entrada NEC y salida del solver sin procesar.",
    },
    "help.tab.bands": {
        Language.ENGLISH: "Per-band results from the last analysis.",
        Language.SPANISH: "Resultados por banda del último análisis.",
    },
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
    "field.height": {Language.ENGLISH: "Height", Language.SPANISH: "Altura"},
    "field.sag": {
        Language.ENGLISH: "Wire sag",
        Language.SPANISH: "Flecha del hilo",
    },
    "geometry.sag_note": {
        Language.ENGLISH: "Sagged wire: {segments} straight segments.",
        Language.SPANISH: "Hilo con flecha: {segments} tramos rectos.",
    },
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
    "feed_matching.title": {
        Language.ENGLISH: "Feed & matching",
        Language.SPANISH: "Alimentación y adaptación",
    },
    "feed_matching.endfed": {
        Language.ENGLISH: "EFHW design matching",
        Language.SPANISH: "Adaptación del diseño EFHW",
    },
    "feed_matching.project": {
        Language.ENGLISH: "Project matching",
        Language.SPANISH: "Adaptación del proyecto",
    },
    "feed_matching.feed_line": {
        Language.ENGLISH: "Feed line",
        Language.SPANISH: "Línea de alimentación",
    },
    "feed_matching.balun": {
        Language.ENGLISH: "Balun/unun loss",
        Language.SPANISH: "Pérdida de balun/unun",
    },
    "feed_matching.none": {
        Language.ENGLISH: "None",
        Language.SPANISH: "Ninguna",
    },
    "feed_matching.not_applicable": {
        Language.ENGLISH: "Not applicable",
        Language.SPANISH: "No aplica",
    },
    "feed_matching.active": {
        Language.ENGLISH: "active",
        Language.SPANISH: "activa",
    },
    "feed_matching.inactive": {
        Language.ENGLISH: "inactive",
        Language.SPANISH: "inactiva",
    },
    "feed_matching.retained": {
        Language.ENGLISH: "retained, not applied",
        Language.SPANISH: "retenida, no aplicada",
    },
    "feed_matching.internal_value": {
        Language.ENGLISH: ("{capacitance} pF shunt + {leakage} µH leakage ({status})"),
        Language.SPANISH: ("{capacitance} pF en paralelo + {leakage} µH de fuga ({status})"),
    },
    "feed_matching.network_state": {
        Language.ENGLISH: "{network} ({state}, {position})",
        Language.SPANISH: "{network} ({state}, {position})",
    },
    "feed_matching.position_feedpoint": {
        Language.ENGLISH: "at feedpoint",
        Language.SPANISH: "en el feedpoint",
    },
    "feed_matching.position_shack": {
        Language.ENGLISH: "in shack",
        Language.SPANISH: "en la estación",
    },
    "feed_matching.feed_line_value": {
        Language.ENGLISH: "{impedance} Ω · {length} {unit} · VF {velocity}",
        Language.SPANISH: "{impedance} Ω · {length} {unit} · FV {velocity}",
    },
    "feed_matching.balun_value": {
        Language.ENGLISH: "{loss} dB at {frequency} MHz · exponent {exponent}",
        Language.SPANISH: "{loss} dB a {frequency} MHz · exponente {exponent}",
    },
    "feed_chain.title": {
        Language.ENGLISH: "Feed-chain loss budget",
        Language.SPANISH: "Presupuesto de pérdidas de la cadena",
    },
    "feed_chain.path_direct": {
        Language.ENGLISH: "Transmitter → feed line → antenna.",
        Language.SPANISH: "Transmisor → línea → antena.",
    },
    "feed_chain.path_feedpoint": {
        Language.ENGLISH: "Transmitter → feed line → matching network (feedpoint) → antenna.",
        Language.SPANISH: "Transmisor → línea → red de adaptación (feedpoint) → antena.",
    },
    "feed_chain.path_shack": {
        Language.ENGLISH: "Transmitter → matching network (shack) → feed line → antenna.",
        Language.SPANISH: "Transmisor → red de adaptación (estación) → línea → antena.",
    },
    "feed_chain.power": {
        Language.ENGLISH: "Transmitter power",
        Language.SPANISH: "Potencia del transmisor",
    },
    "feed_chain.frequency": {
        Language.ENGLISH: "Frequency (MHz)",
        Language.SPANISH: "Frecuencia (MHz)",
    },
    "feed_chain.swr": {
        Language.ENGLISH: "SWR",
        Language.SPANISH: "ROE",
    },
    "feed_chain.mismatch": {
        Language.ENGLISH: "Mismatch",
        Language.SPANISH: "Desadaptación",
    },
    "feed_chain.line": {
        Language.ENGLISH: "Line",
        Language.SPANISH: "Línea",
    },
    "feed_chain.network": {
        Language.ENGLISH: "Network",
        Language.SPANISH: "Red",
    },
    "feed_chain.balun": {
        Language.ENGLISH: "Balun",
        Language.SPANISH: "Balun",
    },
    "feed_chain.delivered": {
        Language.ENGLISH: "At antenna",
        Language.SPANISH: "En antena",
    },
    "feed_chain.radiated": {
        Language.ENGLISH: "Radiated",
        Language.SPANISH: "Radiada",
    },
    "feed_chain.dominant": {
        Language.ENGLISH: "Dominant loss",
        Language.SPANISH: "Pérdida dominante",
    },
    "feed_chain.summary": {
        Language.ENGLISH: ("At {power} W: worst line loss {line} dB, worst SWR {swr}."),
        Language.SPANISH: ("Con {power} W: peor pérdida de línea {line} dB, peor ROE {swr}."),
    },
    "feed_chain.hint": {
        Language.ENGLISH: (
            "Losses are evaluated from the current simulation. The component "
            "values may not add exactly under mismatch. Change the matching-network "
            "position or feed line and simulate again to update the budget."
        ),
        Language.SPANISH: (
            "Las pérdidas se evalúan con la simulación actual. Los componentes "
            "pueden no sumar exactamente con desadaptación. Cambiá la posición de "
            "la red o la línea y volvé a simular para actualizar el presupuesto."
        ),
    },
    "feed_matching.override_warning": {
        Language.ENGLISH: (
            "The project matching network overrides the internal EFHW matching "
            "network. The internal values are retained but not applied; the two "
            "networks are not cascaded."
        ),
        Language.SPANISH: (
            "La red de adaptación del proyecto reemplaza la red interna del EFHW. "
            "Los valores internos se retienen pero no se aplican; las dos redes no "
            "se conectan en cascada."
        ),
    },
    "feed_matching.edit": {
        Language.ENGLISH: "Edit project network...",
        Language.SPANISH: "Editar red del proyecto...",
    },
    "feed_matching.remove": {
        Language.ENGLISH: "Remove project network",
        Language.SPANISH: "Quitar red del proyecto",
    },
    "feed_matching.remove_title": {
        Language.ENGLISH: "Remove matching network",
        Language.SPANISH: "Quitar red de adaptación",
    },
    "feed_matching.remove_question": {
        Language.ENGLISH: (
            "Remove the project matching network? The internal EFHW matching "
            "network will become effective again."
        ),
        Language.SPANISH: (
            "¿Quitar la red de adaptación del proyecto? La red interna del EFHW "
            "volverá a ser efectiva."
        ),
    },
    "matching_network.replace_title": {
        Language.ENGLISH: "Replace matching network",
        Language.SPANISH: "Reemplazar red de adaptación",
    },
    "matching_network.replace_question": {
        Language.ENGLISH: (
            "A project matching network already exists. Replace it with a network "
            "designed from this impedance point?"
        ),
        Language.SPANISH: (
            "Ya existe una red de adaptación del proyecto. ¿Reemplazarla por una "
            "red diseñada desde este punto de impedancia?"
        ),
    },
    "matching_network.efhw_override_title": {
        Language.ENGLISH: "EFHW matching override",
        Language.SPANISH: "Reemplazo de adaptación del EFHW",
    },
    "matching_network.efhw_override_question": {
        Language.ENGLISH: (
            "This design has an active internal EFHW matching network. The project "
            "network will replace it; the two networks are not cascaded. Continue?"
        ),
        Language.SPANISH: (
            "Este diseño tiene una red de adaptación interna del EFHW activa. La "
            "red del proyecto la reemplazará; las dos redes no se conectan en "
            "cascada. ¿Continuar?"
        ),
    },
    "results.create_matching_network": {
        Language.ENGLISH: "Create Project Matching Network...",
        Language.SPANISH: "Crear red de adaptación del proyecto...",
    },
    "results.matching_point_unavailable": {
        Language.ENGLISH: "Raw feed impedance is unavailable for this row.",
        Language.SPANISH: "La impedancia cruda de alimentación no está disponible para esta fila.",
    },
    "matching_network.title": {
        Language.ENGLISH: "Matching Network",
        Language.SPANISH: "Red de adaptación",
    },
    "matching_network.design_target": {
        Language.ENGLISH: "Design target",
        Language.SPANISH: "Objetivo de diseño",
    },
    "matching_network.components": {
        Language.ENGLISH: "Components",
        Language.SPANISH: "Componentes",
    },
    "matching_network.enabled": {
        Language.ENGLISH: "Enable matching network",
        Language.SPANISH: "Habilitar red de adaptación",
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
    "matching_network.position": {
        Language.ENGLISH: "Position",
        Language.SPANISH: "Posición",
    },
    "matching_network.position_feedpoint": {
        Language.ENGLISH: "At the antenna feedpoint",
        Language.SPANISH: "En el punto de alimentación",
    },
    "matching_network.position_shack": {
        Language.ENGLISH: "In the shack, before the feed line",
        Language.SPANISH: "En la estación, antes de la línea",
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
    "matching_network.source_impedance": {
        Language.ENGLISH: "Source impedance",
        Language.SPANISH: "Impedancia de la fuente",
    },
    "matching_network.design_origin": {
        Language.ENGLISH: "Target origin",
        Language.SPANISH: "Origen del objetivo",
    },
    "matching_network.origin.none": {
        Language.ENGLISH: "Not recorded",
        Language.SPANISH: "Sin registrar",
    },
    "matching_network.origin.manual": {
        Language.ENGLISH: "Manual entry",
        Language.SPANISH: "Entrada manual",
    },
    "matching_network.origin.simulation": {
        Language.ENGLISH: "Current simulation point",
        Language.SPANISH: "Punto de simulación actual",
    },
    "matching_network.use_current_point": {
        Language.ENGLISH: "Use current simulation point",
        Language.SPANISH: "Usar punto de simulación actual",
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
            "Lossless L, Pi, or T network evaluated before the feed line. It "
            "changes impedance and SWR but not the antenna pattern or power gain."
        ),
        Language.SPANISH: (
            "Red L, Pi o T sin pérdidas evaluada antes de la línea. Cambia la "
            "impedancia y el SWR, pero no el patrón ni la ganancia de potencia."
        ),
    },
    "matching_network.override_warning": {
        Language.ENGLISH: (
            "This network replaces the internal EFHW matching unit on end-fed "
            "designs. The internal values stay in the design but are not applied; "
            "the networks are not cascaded."
        ),
        Language.SPANISH: (
            "Esta red reemplaza la unidad de adaptación interna del EFHW en diseños "
            "alimentados en el extremo. Los valores internos quedan en el diseño "
            "pero no se aplican; las redes no se conectan en cascada."
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
    "status.comparing": {
        Language.ENGLISH: "Comparing designs...",
        Language.SPANISH: "Comparando diseños...",
    },
    "status.comparing_progress": {
        Language.ENGLISH: "Comparing {index}/{total}: {name}",
        Language.SPANISH: "Comparando {index}/{total}: {name}",
    },
    "status.comparison_done": {
        Language.ENGLISH: "Comparison complete.",
        Language.SPANISH: "Comparación completa.",
    },
    "status.comparison_cancelled": {
        Language.ENGLISH: "Comparison cancelled.",
        Language.SPANISH: "Comparación cancelada.",
    },
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
    "status.installation_profile": {
        Language.ENGLISH: "Installation profile updated.",
        Language.SPANISH: "Perfil de instalación actualizado.",
    },
    "status.construction_record": {
        Language.ENGLISH: "As-built record updated.",
        Language.SPANISH: "Registro as-built actualizado.",
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
    "status.measurement_sessions": {
        Language.ENGLISH: "Measurement sessions updated.",
        Language.SPANISH: "Sesiones de medición actualizadas.",
    },
    "status.tuning_applied": {
        Language.ENGLISH: "Tuning change applied.",
        Language.SPANISH: "Cambio de ajuste aplicado.",
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
    "progress.accessible_name": {
        Language.ENGLISH: "Task progress",
        Language.SPANISH: "Progreso de la tarea",
    },
    "progress.working": {
        Language.ENGLISH: "Working...",
        Language.SPANISH: "Trabajando...",
    },
    "progress.preparing": {
        Language.ENGLISH: "Preparing model...",
        Language.SPANISH: "Preparando modelo...",
    },
    "progress.running_solver": {
        Language.ENGLISH: "Running NEC-2...",
        Language.SPANISH: "Ejecutando NEC-2...",
    },
    "progress.processing": {
        Language.ENGLISH: "Processing results...",
        Language.SPANISH: "Procesando resultados...",
    },
    "progress.analyzing_bands": {
        Language.ENGLISH: "Analyzing bands...",
        Language.SPANISH: "Analizando bandas...",
    },
    "progress.with_elapsed": {
        Language.ENGLISH: "{text} · {seconds} s",
        Language.SPANISH: "{text} · {seconds} s",
    },
    "progress.completed": {
        Language.ENGLISH: "Completed",
        Language.SPANISH: "Completado",
    },
    "progress.cancelled": {
        Language.ENGLISH: "Cancelled",
        Language.SPANISH: "Cancelado",
    },
    "progress.failed": {
        Language.ENGLISH: "Failed",
        Language.SPANISH: "Fallido",
    },
    "status.preparing_save": {
        Language.ENGLISH: "Preparing project...",
        Language.SPANISH: "Preparando proyecto...",
    },
    "status.opening": {
        Language.ENGLISH: "Opening project...",
        Language.SPANISH: "Abriendo proyecto...",
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
    "band.workers": {
        Language.ENGLISH: "Parallel workers",
        Language.SPANISH: "Workers paralelos",
    },
    "band.workers_hint": {
        Language.ENGLISH: (
            "Analyze independent bands in parallel. Each worker launches a "
            "separate solver process; more workers reduce wall time but use more "
            "CPU and memory. Use 1 for large models or limited memory."
        ),
        Language.SPANISH: (
            "Analizá bandas independientes en paralelo. Cada worker lanza un "
            "proceso del solver separado; más workers reducen el tiempo pero usan "
            "más CPU y memoria. Usá 1 para modelos grandes o memoria limitada."
        ),
    },
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
    "band.note.endfed_loaded_80_10": {
        Language.ENGLISH: (
            "Published 80-10 m starting point; the loading coil, matching unit, "
            "and installation determine the actual coverage."
        ),
        Language.SPANISH: (
            "Punto de partida publicado para 80-10 m; la bobina de carga, la "
            "unidad de adaptación y la instalación determinan la cobertura real."
        ),
    },
    "band.note.endfed_loaded_40_10": {
        Language.ENGLISH: (
            "Published 40-20-10 m starting point; the loading coil, matching "
            "unit, and installation determine the actual coverage."
        ),
        Language.SPANISH: (
            "Punto de partida publicado para 40-20-10 m; la bobina de carga, la "
            "unidad de adaptación y la instalación determinan la cobertura real."
        ),
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
    "band.note.biquad": {
        Language.ENGLISH: "Current band only; the biquad is a broadband starting point, not a validated multiband design.",
        Language.SPANISH: "Solo la banda actual; el biquad es un punto de partida de banda ancha, no un diseño multibanda validado.",
    },
    "band.note.beverage": {
        Language.ENGLISH: "Current band only; the Beverage is a receiving starting point with low gain.",
        Language.SPANISH: "Solo la banda actual; la Beverage es un punto de partida de recepción con ganancia baja.",
    },
    "band.note.loaded_dipole": {
        Language.ENGLISH: "Current band only; the loaded/linked dipole is a monoband starting point.",
        Language.SPANISH: "Solo la banda actual; el dipolo cargado/enlazado es un punto de partida monobanda.",
    },
    "band.note.phased_vertical": {
        Language.ENGLISH: (
            "Current band only; the phased vertical array is a narrowband "
            "starting point and its combining network is ideal."
        ),
        Language.SPANISH: (
            "Solo la banda actual; el arreglo vertical en fase es un punto de "
            "partida de banda angosta y su red combinadora es ideal."
        ),
    },
    "band.note.quad_beam": {
        Language.ENGLISH: (
            "Current band only; the quad beam is a narrowband starting point "
            "with heuristic loop and spacing dimensions."
        ),
        Language.SPANISH: (
            "Solo la banda actual; el beam cuádruple es un punto de partida de "
            "banda angosta con dimensiones heurísticas de lazo y separación."
        ),
    },
    "band.note.discone": {
        Language.ENGLISH: (
            "Heuristic broadband plan from 0.5x to 1.5x the design frequency; "
            "the radial-wire surfaces are approximate."
        ),
        Language.SPANISH: (
            "Plan de banda ancha heurístico de 0,5x a 1,5x la frecuencia de "
            "diseño; las superficies de hilos radiales son aproximadas."
        ),
    },
    "band.note.trap_yagi": {
        Language.ENGLISH: (
            "Two-band starting plan from the trap design frequencies; trap loss "
            "and the installed bandwidth are not validated."
        ),
        Language.SPANISH: (
            "Plan de partida de dos bandas a partir de las frecuencias de diseño "
            "de las trampas; no están validadas las pérdidas de las trampas ni el "
            "ancho de banda instalado."
        ),
    },
    "band.note.hexbeam": {
        Language.ENGLISH: ("Current band only; the hexbeam is a single-band starting design."),
        Language.SPANISH: (
            "Solo la banda actual; el hexbeam es un diseño de partida de una sola banda."
        ),
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
    "tab.sources": {Language.ENGLISH: "Sources", Language.SPANISH: "Fuentes"},
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
    "measurement.session": {
        Language.ENGLISH: "Session",
        Language.SPANISH: "Sesión",
    },
    "measurement.session_unassigned": {
        Language.ENGLISH: "Unassigned",
        Language.SPANISH: "Sin sesión",
    },
    "measurement.session_value": {
        Language.ENGLISH: "Session: {value}",
        Language.SPANISH: "Sesión: {value}",
    },
    "measurement.sessions": {
        Language.ENGLISH: "Sessions...",
        Language.SPANISH: "Sesiones...",
    },
    "measurement.compare": {
        Language.ENGLISH: "Compare...",
        Language.SPANISH: "Comparar...",
    },
    "measurement.tune": {
        Language.ENGLISH: "Tune...",
        Language.SPANISH: "Ajustar...",
    },
    "measurement.session_title": {
        Language.ENGLISH: "Measurement session",
        Language.SPANISH: "Sesión de medición",
    },
    "measurement.session_name": {
        Language.ENGLISH: "Session name",
        Language.SPANISH: "Nombre de la sesión",
    },
    "measurement.session_name_required": {
        Language.ENGLISH: "Enter a session name.",
        Language.SPANISH: "Ingresá un nombre de sesión.",
    },
    "measurement.session_date": {
        Language.ENGLISH: "Date and time",
        Language.SPANISH: "Fecha y hora",
    },
    "measurement.session_design": {
        Language.ENGLISH: "Design",
        Language.SPANISH: "Diseño",
    },
    "measurement.session_location": {
        Language.ENGLISH: "Location",
        Language.SPANISH: "Ubicación",
    },
    "measurement.session_conditions": {
        Language.ENGLISH: "Conditions",
        Language.SPANISH: "Condiciones",
    },
    "measurement.session_notes": {
        Language.ENGLISH: "Notes",
        Language.SPANISH: "Notas",
    },
    "measurement.session_no_design": {
        Language.ENGLISH: "Project (all designs)",
        Language.SPANISH: "Proyecto (todos los diseños)",
    },
    "measurement.sessions_title": {
        Language.ENGLISH: "Measurement sessions",
        Language.SPANISH: "Sesiones de medición",
    },
    "measurement.sessions_timeline": {
        Language.ENGLISH: (
            "Timeline · newest sessions first. Select a session to see its measurements."
        ),
        Language.SPANISH: (
            "Línea de tiempo · sesiones más nuevas primero. Seleccioná una sesión "
            "para ver sus mediciones."
        ),
    },
    "measurement.sessions_measurements": {
        Language.ENGLISH: "Measurements in the selected session",
        Language.SPANISH: "Mediciones de la sesión seleccionada",
    },
    "measurement.sessions_unassigned": {
        Language.ENGLISH: "Unassigned measurements",
        Language.SPANISH: "Mediciones sin sesión",
    },
    "measurement.sessions_unassigned_hint": {
        Language.ENGLISH: ("Measurements without a session. Edit a measurement to assign it."),
        Language.SPANISH: ("Mediciones sin sesión. Editá una medición para asignarla."),
    },
    "measurement.sessions_count": {
        Language.ENGLISH: "Measurements",
        Language.SPANISH: "Mediciones",
    },
    "measurement.session_new": {
        Language.ENGLISH: "New session...",
        Language.SPANISH: "Nueva sesión...",
    },
    "measurement.session_edit": {
        Language.ENGLISH: "Edit session...",
        Language.SPANISH: "Editar sesión...",
    },
    "measurement.session_delete": {
        Language.ENGLISH: "Delete session",
        Language.SPANISH: "Eliminar sesión",
    },
    "measurement.session_delete_title": {
        Language.ENGLISH: "Delete measurement session",
        Language.SPANISH: "Eliminar sesión de medición",
    },
    "measurement.session_delete_confirm": {
        Language.ENGLISH: (
            "Delete session '{name}'? Its measurements are kept and become unassigned."
        ),
        Language.SPANISH: (
            "¿Eliminar la sesión '{name}'? Sus mediciones se conservan y quedan sin sesión."
        ),
    },
    "measurement.sessions_edit_measurement": {
        Language.ENGLISH: "Edit measurement...",
        Language.SPANISH: "Editar medición...",
    },
    "measurement.sessions_compare": {
        Language.ENGLISH: "Compare measurements...",
        Language.SPANISH: "Comparar mediciones...",
    },
    "measurement.points": {
        Language.ENGLISH: "Points",
        Language.SPANISH: "Puntos",
    },
    "measurement.reference": {
        Language.ENGLISH: "Reference",
        Language.SPANISH: "Referencia",
    },
    "measurement.source": {
        Language.ENGLISH: "Source",
        Language.SPANISH: "Origen",
    },
    "measurement.before_after_title": {
        Language.ENGLISH: "Measurement before / after",
        Language.SPANISH: "Medición antes / después",
    },
    "measurement.before_after_summary": {
        Language.ENGLISH: (
            "Compared {count} points · mean |ΔZ| {mean} Ω · max {maximum} Ω · "
            "mean SWR {before} → {after}"
        ),
        Language.SPANISH: (
            "Comparados {count} puntos · |ΔZ| medio {mean} Ω · máximo {maximum} Ω · "
            "ROE media {before} → {after}"
        ),
    },
    "measurement.before_after_no_overlap": {
        Language.ENGLISH: ("No overlapping frequency range between the selected measurements."),
        Language.SPANISH: (
            "No hay un rango de frecuencia superpuesto entre las mediciones seleccionadas."
        ),
    },
    "measurement.comparison_unavailable": {
        Language.ENGLISH: "Select two measurements.",
        Language.SPANISH: "Seleccioná dos mediciones.",
    },
    "measurement.comparison_need_two": {
        Language.ENGLISH: ("Import or record at least two measurements to compare."),
        Language.SPANISH: ("Importá o registrá al menos dos mediciones para comparar."),
    },
    "measurement.comparison_conditions": {
        Language.ENGLISH: ("Conditions differ: {fields}. Treat the comparison as indicative."),
        Language.SPANISH: (
            "Las condiciones difieren: {fields}. Tomá la comparación como indicativa."
        ),
    },
    "measurement.comparison_resonance_before": {
        Language.ENGLISH: "Resonance before: {value}",
        Language.SPANISH: "Resonancia antes: {value}",
    },
    "measurement.comparison_resonance_after": {
        Language.ENGLISH: "Resonance after: {value}",
        Language.SPANISH: "Resonancia después: {value}",
    },
    "measurement.comparison_resonance_shift": {
        Language.ENGLISH: "Shift: {value} kHz",
        Language.SPANISH: "Desplazamiento: {value} kHz",
    },
    "measurement.comparison_before": {
        Language.ENGLISH: "Before",
        Language.SPANISH: "Antes",
    },
    "measurement.comparison_after": {
        Language.ENGLISH: "After",
        Language.SPANISH: "Después",
    },
    "measurement.comparison_reference": {
        Language.ENGLISH: "Comparison SWR reference",
        Language.SPANISH: "Referencia de ROE para comparar",
    },
    "measurement.frequency_mhz": {
        Language.ENGLISH: "Frequency (MHz)",
        Language.SPANISH: "Frecuencia (MHz)",
    },
    "measurement.comparison_before_r": {
        Language.ENGLISH: "Before R (Ω)",
        Language.SPANISH: "R antes (Ω)",
    },
    "measurement.comparison_before_x": {
        Language.ENGLISH: "Before X (Ω)",
        Language.SPANISH: "X antes (Ω)",
    },
    "measurement.comparison_before_swr": {
        Language.ENGLISH: "Before SWR",
        Language.SPANISH: "ROE antes",
    },
    "measurement.comparison_after_r": {
        Language.ENGLISH: "After R (Ω)",
        Language.SPANISH: "R después (Ω)",
    },
    "measurement.comparison_after_x": {
        Language.ENGLISH: "After X (Ω)",
        Language.SPANISH: "X después (Ω)",
    },
    "measurement.comparison_after_swr": {
        Language.ENGLISH: "After SWR",
        Language.SPANISH: "ROE después",
    },
    "measurement.comparison_delta_z": {
        Language.ENGLISH: "Δ|Z| (Ω)",
        Language.SPANISH: "Δ|Z| (Ω)",
    },
    "measurement.comparison_delta_swr": {
        Language.ENGLISH: "ΔSWR",
        Language.SPANISH: "ΔROE",
    },
    "tuning.title": {
        Language.ENGLISH: "Sensitivity tuning assistant",
        Language.SPANISH: "Asistente de ajuste por sensibilidad",
    },
    "tuning.measurement": {
        Language.ENGLISH: "Measurement",
        Language.SPANISH: "Medición",
    },
    "tuning.target": {
        Language.ENGLISH: "Target frequency",
        Language.SPANISH: "Frecuencia objetivo",
    },
    "tuning.current_dimension": {
        Language.ENGLISH: "Current primary dimension",
        Language.SPANISH: "Dimensión principal actual",
    },
    "tuning.max_adjustment": {
        Language.ENGLISH: "Maximum adjustment",
        Language.SPANISH: "Ajuste máximo",
    },
    "tuning.measured_resonance": {
        Language.ENGLISH: "Measured resonance: {value}",
        Language.SPANISH: "Resonancia medida: {value}",
    },
    "tuning.measured_min_swr": {
        Language.ENGLISH: "Measured minimum-SWR frequency: {value}",
        Language.SPANISH: "Frecuencia de ROE mínima medida: {value}",
    },
    "tuning.analyze": {
        Language.ENGLISH: "Analyze",
        Language.SPANISH: "Analizar",
    },
    "tuning.cancel": {
        Language.ENGLISH: "Cancel analysis",
        Language.SPANISH: "Cancelar análisis",
    },
    "tuning.apply": {
        Language.ENGLISH: "Apply proposed change",
        Language.SPANISH: "Aplicar cambio propuesto",
    },
    "tuning.sensitivity": {
        Language.ENGLISH: "Sensitivity: {value}",
        Language.SPANISH: "Sensibilidad: {value}",
    },
    "tuning.proposed_change": {
        Language.ENGLISH: "Proposed change: {value}",
        Language.SPANISH: "Cambio propuesto: {value}",
    },
    "tuning.proposed_change_clipped": {
        Language.ENGLISH: "Proposed change: {value} (clipped to the adjustment limit)",
        Language.SPANISH: "Cambio propuesto: {value} (limitado por el ajuste máximo)",
    },
    "tuning.bounds": {
        Language.ENGLISH: "Allowed change: {lower} to {upper}",
        Language.SPANISH: "Cambio permitido: {lower} a {upper}",
    },
    "tuning.predicted": {
        Language.ENGLISH: "Predicted model resonance: {resonance} · SWR at target: {swr}",
        Language.SPANISH: "Resonancia modelada prevista: {resonance} · ROE en el objetivo: {swr}",
    },
    "tuning.predicted_no_resonance": {
        Language.ENGLISH: "No modeled resonance in the verification sweep. Predicted SWR at target: {swr}",
        Language.SPANISH: "No hay resonancia modelada en el barrido de verificación. ROE prevista en el objetivo: {swr}",
    },
    "tuning.assumptions_text": {
        Language.ENGLISH: (
            "This is a local finite-difference estimate from the current solver model, "
            "not a measurement. Ground, height, nearby objects, and calibration can "
            "shift the real resonance. Change the antenna in small steps and re-measure."
        ),
        Language.SPANISH: (
            "Es una estimación local por diferencias finitas del modelo actual, no una "
            "medición. El suelo, la altura, los objetos cercanos y la calibración pueden "
            "desplazar la resonancia real. Cambiá la antena en pasos pequeños y volvé a medir."
        ),
    },
    "tuning.table.probe": {
        Language.ENGLISH: "Probe",
        Language.SPANISH: "Sonda",
    },
    "tuning.table.dimension": {
        Language.ENGLISH: "Dimension",
        Language.SPANISH: "Dimensión",
    },
    "tuning.table.resonance": {
        Language.ENGLISH: "Model resonance",
        Language.SPANISH: "Resonancia del modelo",
    },
    "tuning.table.swr": {
        Language.ENGLISH: "SWR at target",
        Language.SPANISH: "ROE en el objetivo",
    },
    "tuning.probe.current": {
        Language.ENGLISH: "Current",
        Language.SPANISH: "Actual",
    },
    "tuning.probe.lower": {
        Language.ENGLISH: "Lower",
        Language.SPANISH: "Menor",
    },
    "tuning.probe.higher": {
        Language.ENGLISH: "Higher",
        Language.SPANISH: "Mayor",
    },
    "tuning.probe.proposed": {
        Language.ENGLISH: "Proposed",
        Language.SPANISH: "Propuesta",
    },
    "tuning.message.ready": {
        Language.ENGLISH: "Set the target and maximum adjustment, then Analyze.",
        Language.SPANISH: "Definí el objetivo y el ajuste máximo, y luego Analizá.",
    },
    "tuning.message.running": {
        Language.ENGLISH: "Probing the solver around the current dimension.",
        Language.SPANISH: "Sondeando el solver alrededor de la dimensión actual.",
    },
    "tuning.message.proposed": {
        Language.ENGLISH: "A bounded adjustment is available for review.",
        Language.SPANISH: "Hay un ajuste acotado disponible para revisar.",
    },
    "tuning.message.verified": {
        Language.ENGLISH: "The proposed dimension was verified with the solver.",
        Language.SPANISH: "La dimensión propuesta se verificó con el solver.",
    },
    "tuning.message.verified_no_resonance": {
        Language.ENGLISH: "The proposed dimension has no modeled resonance in the sweep.",
        Language.SPANISH: "La dimensión propuesta no tiene resonancia modelada en el barrido.",
    },
    "tuning.message.no_change": {
        Language.ENGLISH: "The measured reference is already at the target within the estimate.",
        Language.SPANISH: "La referencia medida ya está en el objetivo dentro de la estimación.",
    },
    "tuning.message.no_sensitivity": {
        Language.ENGLISH: "The model resonance is not sensitive enough to this dimension.",
        Language.SPANISH: "La resonancia del modelo no es suficientemente sensible a esta dimensión.",
    },
    "tuning.message.no_resonance": {
        Language.ENGLISH: "No model resonance was found near the measured reference.",
        Language.SPANISH: "No se encontró una resonancia del modelo cerca de la referencia medida.",
    },
    "tuning.message.cancelled": {
        Language.ENGLISH: "Analysis cancelled.",
        Language.SPANISH: "Análisis cancelado.",
    },
    "tuning.message.error": {
        Language.ENGLISH: "The tuning analysis failed.",
        Language.SPANISH: "Falló el análisis de ajuste.",
    },
    "tuning.need_measurement": {
        Language.ENGLISH: "Import a measurement before using the tuning assistant.",
        Language.SPANISH: "Importá una medición antes de usar el asistente de ajuste.",
    },
    "tuning.unavailable_family": {
        Language.ENGLISH: (
            "The tuning assistant needs a family with an editable primary dimension."
        ),
        Language.SPANISH: (
            "El asistente de ajuste necesita una familia con una dimensión principal editable."
        ),
    },
    "tuning.progress": {
        Language.ENGLISH: "Solver probes: {completed}/{total}",
        Language.SPANISH: "Sondas del solver: {completed}/{total}",
    },
    "tuning.progress_done": {
        Language.ENGLISH: "Analysis complete.",
        Language.SPANISH: "Análisis completo.",
    },
    "tuning.cancelling": {
        Language.ENGLISH: "Cancelling the analysis...",
        Language.SPANISH: "Cancelando el análisis...",
    },
    "tuning.failed": {
        Language.ENGLISH: "Analysis failed.",
        Language.SPANISH: "El análisis falló.",
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
    "confidence.title": {
        Language.ENGLISH: "Result confidence",
        Language.SPANISH: "Confianza del resultado",
    },
    "confidence.topic_label": {
        Language.ENGLISH: "What does this mean?",
        Language.SPANISH: "¿Qué significa esto?",
    },
    "confidence.no_design": {
        Language.ENGLISH: "Select a design to see its evidence and limitations.",
        Language.SPANISH: "Seleccioná un diseño para ver su evidencia y limitaciones.",
    },
    "confidence.modeled": {
        Language.ENGLISH: (
            "Modeled: canonical wires, feed, ground, loads, and the feed-line/"
            "matching post-processing chain."
        ),
        Language.SPANISH: (
            "Modelado: hilos canónicos, alimentación, suelo, cargas y la cadena de "
            "post-procesamiento de línea y adaptación."
        ),
    },
    "confidence.uncertainties": {
        Language.ENGLISH: (
            "Dominant uncertainties: ground model, installation height, feed-line "
            "routing, common-mode current, and construction tolerances."
        ),
        Language.SPANISH: (
            "Incertidumbres dominantes: modelo de suelo, altura de instalación, "
            "recorrido de la línea, corriente de modo común y tolerancias de construcción."
        ),
    },
    "confidence.disclaimer": {
        Language.ENGLISH: (
            "The model is an estimate. Verify critical dimensions and the installed "
            "match with measurements."
        ),
        Language.SPANISH: (
            "El modelo es una estimación. Verificá las dimensiones críticas y la "
            "adaptación instalada con mediciones."
        ),
    },
    "confidence.topic.impedance": {
        Language.ENGLISH: "Impedance",
        Language.SPANISH: "Impedancia",
    },
    "confidence.topic.swr": {Language.ENGLISH: "SWR", Language.SPANISH: "ROE"},
    "confidence.topic.efficiency": {
        Language.ENGLISH: "Efficiency",
        Language.SPANISH: "Eficiencia",
    },
    "confidence.topic.gain": {
        Language.ENGLISH: "Gain, directivity, and realized gain",
        Language.SPANISH: "Ganancia, directividad y ganancia realizada",
    },
    "confidence.topic.takeoff": {
        Language.ENGLISH: "Takeoff angle",
        Language.SPANISH: "Ángulo de salida",
    },
    "confidence.topic.bandwidth": {
        Language.ENGLISH: "Bandwidth",
        Language.SPANISH: "Ancho de banda",
    },
    "confidence.topic.ground": {
        Language.ENGLISH: "Ground model",
        Language.SPANISH: "Modelo de suelo",
    },
    "confidence.topic.feed_loss": {
        Language.ENGLISH: "Feed-line and matching losses",
        Language.SPANISH: "Pérdidas de línea y adaptación",
    },
    "confidence.explain.impedance": {
        Language.ENGLISH: (
            "Impedance has a resistive part R and a reactive part X. R includes "
            "radiation and loss; X comes from stored energy. A 50 Ω system wants "
            "about 50 + j0 Ω at the feedpoint, but a good match does not guarantee "
            "high efficiency."
        ),
        Language.SPANISH: (
            "La impedancia tiene una parte resistiva R y una reactiva X. R incluye "
            "radiación y pérdidas; X viene de energía almacenada. Un sistema de 50 Ω "
            "quiere unos 50 + j0 Ω en el punto de alimentación, pero una buena "
            "adaptación no garantiza alta eficiencia."
        ),
    },
    "confidence.explain.swr": {
        Language.ENGLISH: (
            "SWR describes mismatch at the reference plane, not antenna quality. A "
            "low SWR can hide high loss in a lossy antenna or feed line. Read SWR "
            "together with efficiency and realized gain."
        ),
        Language.SPANISH: (
            "La ROE describe la desadaptación en el plano de referencia, no la calidad "
            "de la antena. Una ROE baja puede ocultar pérdidas altas en una antena o "
            "línea con pérdidas. Leé la ROE junto con la eficiencia y la ganancia realizada."
        ),
    },
    "confidence.explain.efficiency": {
        Language.ENGLISH: (
            "Efficiency is radiated power divided by accepted power. Conductor, "
            "ground, load, and mismatch losses reduce it. A low-efficiency antenna "
            "can still show a low SWR."
        ),
        Language.SPANISH: (
            "La eficiencia es la potencia radiada dividida por la potencia aceptada. "
            "Las pérdidas de conductor, suelo, cargas y desadaptación la reducen. Una "
            "antena de baja eficiencia puede mostrar igualmente una ROE baja."
        ),
    },
    "confidence.explain.gain": {
        Language.ENGLISH: (
            "Power gain is the far-field maximum relative to an isotropic radiator "
            "(dBi). Directivity ignores losses; realized gain includes mismatch, "
            "feed-line, matching, and balun loss. Compare like with like."
        ),
        Language.SPANISH: (
            "La ganancia de potencia es el máximo de campo lejano respecto de un "
            "radiador isotrópico (dBi). La directividad ignora las pérdidas; la "
            "ganancia realizada incluye desadaptación, línea, adaptación y balun. "
            "Compará cosas equivalentes."
        ),
    },
    "confidence.explain.takeoff": {
        Language.ENGLISH: (
            "Takeoff angle is the elevation of the main lobe. Low angles favor DX; "
            "high angles favor NVIS and regional paths. Height, ground, and the "
            "antenna type change it."
        ),
        Language.SPANISH: (
            "El ángulo de salida es la elevación del lóbulo principal. Los ángulos "
            "bajos favorecen DX; los altos favorecen NVIS y trayectos regionales. La "
            "altura, el suelo y el tipo de antena lo cambian."
        ),
    },
    "confidence.explain.bandwidth": {
        Language.ENGLISH: (
            "Bandwidth is the frequency range that meets the chosen SWR or gain "
            "criterion. It depends on conductor size, height, ground, and matching. "
            "A narrow design may need careful tuning."
        ),
        Language.SPANISH: (
            "El ancho de banda es el rango de frecuencia que cumple el criterio de ROE "
            "o ganancia elegido. Depende del diámetro del conductor, la altura, el "
            "suelo y la adaptación. Un diseño angosto puede necesitar ajuste cuidadoso."
        ),
    },
    "confidence.explain.ground": {
        Language.ENGLISH: (
            "The ground model changes the pattern, feedpoint impedance, and losses. "
            "Average soil is a starting point, not a measurement. Use the soil "
            "presets and verify with the installed antenna."
        ),
        Language.SPANISH: (
            "El modelo de suelo cambia el patrón, la impedancia de alimentación y las "
            "pérdidas. El suelo promedio es un punto de partida, no una medición. Usá "
            "los presets y verificá con la antena instalada."
        ),
    },
    "confidence.explain.feed_loss": {
        Language.ENGLISH: (
            "Feed-line, matching-network, and balun losses reduce realized gain. A "
            "tuner can lower SWR at the transmitter while increasing line loss, "
            "especially with high SWR. Check the loss breakdown, not only SWR."
        ),
        Language.SPANISH: (
            "Las pérdidas de línea, red de adaptación y balun reducen la ganancia "
            "realizada. Un sintonizador puede bajar la ROE en el transmisor y a la vez "
            "aumentar la pérdida de línea, sobre todo con ROE alta. Revisá el desglose "
            "de pérdidas, no solo la ROE."
        ),
    },
    "table.frequency": {Language.ENGLISH: "Frequency (MHz)", Language.SPANISH: "Frecuencia (MHz)"},
    "table.resistance": {Language.ENGLISH: "R (Ω)", Language.SPANISH: "R (Ω)"},
    "table.reactance": {Language.ENGLISH: "X (Ω)", Language.SPANISH: "X (Ω)"},
    "table.impedance": {Language.ENGLISH: "|Z| (Ω)", Language.SPANISH: "|Z| (Ω)"},
    "table.swr": {Language.ENGLISH: "SWR", Language.SPANISH: "ROE"},
    "table.source": {Language.ENGLISH: "Source", Language.SPANISH: "Fuente"},
    "table.wire": {Language.ENGLISH: "Wire", Language.SPANISH: "Hilo"},
    "table.amplitude": {Language.ENGLISH: "Amplitude", Language.SPANISH: "Amplitud"},
    "table.phase": {Language.ENGLISH: "Phase", Language.SPANISH: "Fase"},
    "table.power": {Language.ENGLISH: "Power (W)", Language.SPANISH: "Potencia (W)"},
    "sources.note": {
        Language.ENGLISH: (
            "Ideal source inputs. Negative power means that source absorbs power; "
            "the primary feed still sets the reported impedance and SWR."
        ),
        Language.SPANISH: (
            "Entradas ideales de las fuentes. Potencia negativa significa que esa "
            "fuente absorbe potencia; la alimentación primaria sigue definiendo la "
            "impedancia y la ROE informadas."
        ),
    },
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
    "compare.designs": {
        Language.ENGLISH: "Designs to compare",
        Language.SPANISH: "Diseños a comparar",
    },
    "compare.basis": {
        Language.ENGLISH: "Common comparison basis",
        Language.SPANISH: "Base común de comparación",
    },
    "compare.start": {
        Language.ENGLISH: "Start frequency",
        Language.SPANISH: "Frecuencia inicial",
    },
    "compare.stop": {
        Language.ENGLISH: "Stop frequency",
        Language.SPANISH: "Frecuencia final",
    },
    "compare.points": {
        Language.ENGLISH: "Sweep points",
        Language.SPANISH: "Puntos del barrido",
    },
    "compare.ground": {
        Language.ENGLISH: "Ground",
        Language.SPANISH: "Suelo",
    },
    "compare.ground_free_space": {
        Language.ENGLISH: "Free space",
        Language.SPANISH: "Espacio libre",
    },
    "compare.ground_perfect": {
        Language.ENGLISH: "Perfect ground",
        Language.SPANISH: "Plano perfecto",
    },
    "compare.reference_height": {
        Language.ENGLISH: "Reference height",
        Language.SPANISH: "Altura de referencia",
    },
    "compare.height_native": {
        Language.ENGLISH: "Native heights",
        Language.SPANISH: "Alturas nativas",
    },
    "compare.reference_frequency": {
        Language.ENGLISH: "Compare at",
        Language.SPANISH: "Comparar en",
    },
    "compare.recompute": {
        Language.ENGLISH: "Recompute comparison",
        Language.SPANISH: "Recalcular comparación",
    },
    "compare.basis_text": {
        Language.ENGLISH: (
            "Basis: {start}-{stop} MHz · {points} points · height {height} · "
            "compare at {frequency} MHz. Recompute to apply changes."
        ),
        Language.SPANISH: (
            "Base: {start}-{stop} MHz · {points} puntos · altura {height} · "
            "comparar en {frequency} MHz. Recalculá para aplicar cambios."
        ),
    },
    "compare.invalid_range": {
        Language.ENGLISH: "Stop frequency must be greater than start frequency.",
        Language.SPANISH: "La frecuencia final debe ser mayor que la inicial.",
    },
    "compare.select_two": {
        Language.ENGLISH: "Select at least two designs.",
        Language.SPANISH: "Seleccioná al menos dos diseños.",
    },
    "compare.max_four": {
        Language.ENGLISH: "Select up to four designs.",
        Language.SPANISH: "Seleccioná hasta cuatro diseños.",
    },
    "compare.recomputing": {
        Language.ENGLISH: "Recomputing with the selected basis...",
        Language.SPANISH: "Recalculando con la base seleccionada...",
    },
    "compare.recompute_error": {
        Language.ENGLISH: "Comparison failed: {message}",
        Language.SPANISH: "La comparación falló: {message}",
    },
    "compare.height_warning.native_height": {
        Language.ENGLISH: "Native height used for {name}.",
        Language.SPANISH: "Se usó la altura nativa de {name}.",
    },
    "compare.height_warning.height_too_low": {
        Language.ENGLISH: "Reference height is too low for {name}; native height used.",
        Language.SPANISH: "La altura de referencia es demasiado baja para {name}; se usó la nativa.",
    },
    "compare.height_warning.height_mapping_unavailable": {
        Language.ENGLISH: "Height mapping is not available for {name}; native height used.",
        Language.SPANISH: "No hay mapeo de altura para {name}; se usó la nativa.",
    },
    "compare.footprint": {
        Language.ENGLISH: "Footprint",
        Language.SPANISH: "Planta",
    },
    "compare.max_height": {
        Language.ENGLISH: "Max height",
        Language.SPANISH: "Altura máxima",
    },
    "compare.conductor_length": {
        Language.ENGLISH: "Conductor length",
        Language.SPANISH: "Longitud de conductor",
    },
    "compare.wires": {
        Language.ENGLISH: "Wires",
        Language.SPANISH: "Hilos",
    },
    "compare.loads": {
        Language.ENGLISH: "Loads",
        Language.SPANISH: "Cargas",
    },
    "compare.lines": {
        Language.ENGLISH: "Transmission lines",
        Language.SPANISH: "Líneas de transmisión",
    },
    "compare.build_effort": {
        Language.ENGLISH: "Build effort",
        Language.SPANISH: "Esfuerzo de construcción",
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
    "action.export_sources_csv": {
        Language.ENGLISH: "Export source results CSV...",
        Language.SPANISH: "Exportar resultados de fuentes CSV...",
    },
    "action.export_wire_schedule_csv": {
        Language.ENGLISH: "Export wire schedule CSV...",
        Language.SPANISH: "Exportar lista de hilos CSV...",
    },
    "action.export_bom_csv": {
        Language.ENGLISH: "Export bill of materials CSV...",
        Language.SPANISH: "Exportar lista de materiales CSV...",
    },
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
    "dialog.sources_csv_title": {
        Language.ENGLISH: "Export source results CSV",
        Language.SPANISH: "Exportar CSV de resultados de fuentes",
    },
    "dialog.wire_schedule_csv_title": {
        Language.ENGLISH: "Export wire schedule CSV",
        Language.SPANISH: "Exportar CSV de lista de hilos",
    },
    "dialog.bom_csv_title": {
        Language.ENGLISH: "Export bill of materials CSV",
        Language.SPANISH: "Exportar CSV de lista de materiales",
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
    "history.installation_profile": {
        Language.ENGLISH: "installation profile",
        Language.SPANISH: "perfil de instalación",
    },
    "history.construction_record": {
        Language.ENGLISH: "as-built record",
        Language.SPANISH: "registro as-built",
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
    "history.measurement_sessions": {
        Language.ENGLISH: "Measurement sessions",
        Language.SPANISH: "Sesiones de medición",
    },
    "history.tuning": {
        Language.ENGLISH: "Apply tuning change",
        Language.SPANISH: "Aplicar cambio de ajuste",
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
    "action.preflight": {
        Language.ENGLISH: "Construction Pre-flight...",
        Language.SPANISH: "Pre-flight de construcción...",
    },
    "action.construction": {
        Language.ENGLISH: "Construction Sheet...",
        Language.SPANISH: "Hoja de construcción...",
    },
    "action.construction_record": {
        Language.ENGLISH: "As-Built / Checklist...",
        Language.SPANISH: "As-built / lista de control...",
    },
    "construction_record.title": {
        Language.ENGLISH: "As-built record and checklist",
        Language.SPANISH: "Registro as-built y lista de control",
    },
    "construction_record.notes": {
        Language.ENGLISH: "As-built notes",
        Language.SPANISH: "Notas as-built",
    },
    "construction_record.notes_placeholder": {
        Language.ENGLISH: "Actual build deviations, hardware substitutions, and field notes.",
        Language.SPANISH: "Desvíos reales de construcción, sustituciones de hardware y notas de campo.",
    },
    "construction_record.dimensions": {
        Language.ENGLISH: "Measured dimensions",
        Language.SPANISH: "Dimensiones medidas",
    },
    "construction_record.checklist": {
        Language.ENGLISH: "Construction checklist",
        Language.SPANISH: "Lista de control de construcción",
    },
    "construction_record.add": {
        Language.ENGLISH: "Add dimension",
        Language.SPANISH: "Agregar dimensión",
    },
    "construction_record.remove": {
        Language.ENGLISH: "Remove dimension",
        Language.SPANISH: "Quitar dimensión",
    },
    "construction_record.label": {
        Language.ENGLISH: "Dimension",
        Language.SPANISH: "Dimensión",
    },
    "construction_record.design_value": {
        Language.ENGLISH: "Design ({unit})",
        Language.SPANISH: "Diseño ({unit})",
    },
    "construction_record.actual_value": {
        Language.ENGLISH: "Actual ({unit})",
        Language.SPANISH: "Real ({unit})",
    },
    "construction_record.notes_column": {
        Language.ENGLISH: "Notes",
        Language.SPANISH: "Notas",
    },
    "construction_record.invalid_value": {
        Language.ENGLISH: "Row {row}, column {column}: enter a valid number or leave it empty.",
        Language.SPANISH: "Fila {row}, columna {column}: ingresá un número válido o dejalo vacío.",
    },
    "construction_record.checklist.prepare_drawings": {
        Language.ENGLISH: "Prepare the construction drawing and wire schedule.",
        Language.SPANISH: "Preparar el plano de construcción y la lista de hilos.",
    },
    "construction_record.checklist.check_dimensions": {
        Language.ENGLISH: "Check every dimension against the design before cutting.",
        Language.SPANISH: "Verificar cada dimensión contra el diseño antes de cortar.",
    },
    "construction_record.checklist.inspect_insulators": {
        Language.ENGLISH: "Inspect insulators, supports, and hardware for damage.",
        Language.SPANISH: "Inspeccionar aisladores, soportes y herrajes en busca de daños.",
    },
    "construction_record.checklist.check_feedpoint": {
        Language.ENGLISH: "Check the feedpoint, balun/unun, and strain relief.",
        Language.SPANISH: "Revisar el punto de alimentación, balun/unun y alivio de tensión.",
    },
    "construction_record.checklist.seal_connectors": {
        Language.ENGLISH: "Seal outdoor connectors and route the coax safely.",
        Language.SPANISH: "Sellar conectores exteriores y tender el coax de forma segura.",
    },
    "construction_record.checklist.check_supports": {
        Language.ENGLISH: "Check mast, guy lines, and clearances.",
        Language.SPANISH: "Revisar mástil, vientos y distancias de seguridad.",
    },
    "construction_record.checklist.verify_grounding": {
        Language.ENGLISH: "Verify station and antenna grounding.",
        Language.SPANISH: "Verificar la puesta a tierra de la estación y la antena.",
    },
    "construction_record.checklist.measure_swr": {
        Language.ENGLISH: "Measure SWR and resonance with the installed feed line.",
        Language.SPANISH: "Medir ROE y resonancia con la línea instalada.",
    },
    "construction_record.checklist.record_measurement": {
        Language.ENGLISH: "Record the measurement session in the project.",
        Language.SPANISH: "Registrar la sesión de medición en el proyecto.",
    },
    "construction_record.checklist.update_as_built": {
        Language.ENGLISH: "Update the as-built dimensions and notes.",
        Language.SPANISH: "Actualizar las dimensiones y notas as-built.",
    },
    "preflight.title": {
        Language.ENGLISH: "Construction pre-flight",
        Language.SPANISH: "Pre-flight de construcción",
    },
    "preflight.intro": {
        Language.ENGLISH: (
            "Read-only checks of the current design before cutting wire. "
            "Pre-flight does not replace a simulation or a physical measurement."
        ),
        Language.SPANISH: (
            "Verificaciones de solo lectura del diseño actual antes de cortar "
            "hilo. El pre-flight no reemplaza una simulación ni una medición real."
        ),
    },
    "preflight.summary.error": {
        Language.ENGLISH: "Not ready to build: {errors} error(s) must be fixed.",
        Language.SPANISH: "No listo para construir: hay que corregir {errors} error(es).",
    },
    "preflight.summary.warning": {
        Language.ENGLISH: (
            "Ready to build with {warnings} warning(s). Review them before cutting."
        ),
        Language.SPANISH: (
            "Listo para construir con {warnings} advertencia(s). Revisalas antes de cortar."
        ),
    },
    "preflight.summary.ready": {
        Language.ENGLISH: "Ready to build: no pre-flight issues found.",
        Language.SPANISH: "Listo para construir: no se encontraron problemas de pre-flight.",
    },
    "preflight.summary.ready_info": {
        Language.ENGLISH: "Ready to build: {info} informational note(s).",
        Language.SPANISH: "Listo para construir: {info} nota(s) informativa(s).",
    },
    "preflight.counts": {
        Language.ENGLISH: "Errors: {errors} · Warnings: {warnings} · Info: {info}",
        Language.SPANISH: "Errores: {errors} · Advertencias: {warnings} · Información: {info}",
    },
    "preflight.group.errors": {
        Language.ENGLISH: "Errors",
        Language.SPANISH: "Errores",
    },
    "preflight.group.warnings": {
        Language.ENGLISH: "Warnings",
        Language.SPANISH: "Advertencias",
    },
    "preflight.group.info": {
        Language.ENGLISH: "Information",
        Language.SPANISH: "Información",
    },
    "preflight.column.finding": {
        Language.ENGLISH: "Finding",
        Language.SPANISH: "Hallazgo",
    },
    "preflight.column.category": {
        Language.ENGLISH: "Category",
        Language.SPANISH: "Categoría",
    },
    "preflight.column.where": {
        Language.ENGLISH: "Where",
        Language.SPANISH: "Dónde",
    },
    "preflight.column.action": {
        Language.ENGLISH: "Suggested action",
        Language.SPANISH: "Acción sugerida",
    },
    "preflight.no_findings": {
        Language.ENGLISH: "No pre-flight issues found.",
        Language.SPANISH: "No se encontraron problemas de pre-flight.",
    },
    "preflight.go_to": {
        Language.ENGLISH: "Go to problem",
        Language.SPANISH: "Ir al problema",
    },
    "preflight.category.geometry": {
        Language.ENGLISH: "Geometry",
        Language.SPANISH: "Geometría",
    },
    "preflight.category.feed": {
        Language.ENGLISH: "Feedpoint and connections",
        Language.SPANISH: "Alimentación y conexiones",
    },
    "preflight.category.segmentation": {
        Language.ENGLISH: "Segmentation",
        Language.SPANISH: "Segmentación",
    },
    "preflight.category.supports": {
        Language.ENGLISH: "Site and supports",
        Language.SPANISH: "Sitio y soportes",
    },
    "preflight.category.construction": {
        Language.ENGLISH: "Construction data",
        Language.SPANISH: "Datos de construcción",
    },
    "preflight.category.simulation": {
        Language.ENGLISH: "Simulation",
        Language.SPANISH: "Simulación",
    },
    "preflight.category.solver": {
        Language.ENGLISH: "Solver assumptions",
        Language.SPANISH: "Supuestos del solver",
    },
    "preflight.action.edit_geometry": {
        Language.ENGLISH: "Review the geometry",
        Language.SPANISH: "Revisar la geometría",
    },
    "preflight.action.edit_feed": {
        Language.ENGLISH: "Review the feedpoint",
        Language.SPANISH: "Revisar la alimentación",
    },
    "preflight.action.edit_loads": {
        Language.ENGLISH: "Open the loads editor",
        Language.SPANISH: "Abrir el editor de cargas",
    },
    "preflight.action.edit_lines": {
        Language.ENGLISH: "Open the transmission lines editor",
        Language.SPANISH: "Abrir el editor de líneas de transmisión",
    },
    "preflight.action.edit_segmentation": {
        Language.ENGLISH: "Review segmentation",
        Language.SPANISH: "Revisar la segmentación",
    },
    "preflight.action.edit_supports": {
        Language.ENGLISH: "Open the installation profile",
        Language.SPANISH: "Abrir el perfil de instalación",
    },
    "preflight.action.edit_construction": {
        Language.ENGLISH: "Open the as-built record",
        Language.SPANISH: "Abrir el registro as-built",
    },
    "preflight.action.run_simulation": {
        Language.ENGLISH: "Review or run the simulation",
        Language.SPANISH: "Revisar o ejecutar la simulación",
    },
    "construction.project": {
        Language.ENGLISH: "Project",
        Language.SPANISH: "Proyecto",
    },
    "construction.design": {
        Language.ENGLISH: "Design",
        Language.SPANISH: "Diseño",
    },
    "construction.antenna": {
        Language.ENGLISH: "Antenna",
        Language.SPANISH: "Antena",
    },
    "construction.frequency": {
        Language.ENGLISH: "Frequency",
        Language.SPANISH: "Frecuencia",
    },
    "construction.units": {
        Language.ENGLISH: "Units",
        Language.SPANISH: "Unidades",
    },
    "construction.updated": {
        Language.ENGLISH: "Updated",
        Language.SPANISH: "Actualizado",
    },
    "construction.as_built": {
        Language.ENGLISH: "As-built record",
        Language.SPANISH: "Registro as-built",
    },
    "construction.hardware_bom": {
        Language.ENGLISH: "Hardware BOM",
        Language.SPANISH: "Lista de materiales de herrajes",
    },
    "construction.coils_traps": {
        Language.ENGLISH: "Coils and traps",
        Language.SPANISH: "Bobinas y trampas",
    },
    "construction.checklist": {
        Language.ENGLISH: "Construction checklist",
        Language.SPANISH: "Lista de control de construcción",
    },
    "construction.bom": {
        Language.ENGLISH: "Bill of materials",
        Language.SPANISH: "Lista de materiales",
    },
    "construction.evidence": {
        Language.ENGLISH: "Evidence and limitations",
        Language.SPANISH: "Evidencia y limitaciones",
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
    "construction.save_package": {
        Language.ENGLISH: "Save Package...",
        Language.SPANISH: "Guardar paquete...",
    },
    "construction.pdf_subtitle": {
        Language.ENGLISH: "AntennaDesk construction sheet · SI units",
        Language.SPANISH: "Hoja de construcción de AntennaDesk · unidades SI",
    },
    "construction.view": {
        Language.ENGLISH: "Construction view",
        Language.SPANISH: "Vista de construcción",
    },
    "construction.isometric_view": {
        Language.ENGLISH: "Isometric view",
        Language.SPANISH: "Vista isométrica",
    },
    "construction.additional_views": {
        Language.ENGLISH: "Additional views",
        Language.SPANISH: "Vistas adicionales",
    },
    "construction.installation_view": {
        Language.ENGLISH: "Installation view (front)",
        Language.SPANISH: "Vista de instalación (frontal)",
    },
    "construction.top_layout": {
        Language.ENGLISH: "Top layout",
        Language.SPANISH: "Disposición en planta",
    },
    "construction.wire_schedule": {
        Language.ENGLISH: "Wire schedule",
        Language.SPANISH: "Lista de hilos",
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
    "dialog.zip_title": {
        Language.ENGLISH: "Export construction package",
        Language.SPANISH: "Exportar paquete de construcción",
    },
    "dialog.zip_filter": {
        Language.ENGLISH: "ZIP package (*.zip)",
        Language.SPANISH: "Paquete ZIP (*.zip)",
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
    "magnetic_loop.diameter_note": {
        Language.ENGLISH: (
            "circumscribed loop diameter {diameter}; the polygon is not drawn as a circle"
        ),
        Language.SPANISH: (
            "diámetro circunscripto del lazo {diameter}; el polígono no se dibuja como círculo"
        ),
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
        Language.ENGLISH: "Load Cebik reference scaled to current frequency",
        Language.SPANISH: "Cargar referencia Cebik escalada a la frecuencia actual",
    },
    "scv.load_reference_hint": {
        Language.ENGLISH: (
            "Scale the published 62.4 x 39 ft or 125 x 38 ft dimensions from "
            "7.15 MHz to the current frequency."
        ),
        Language.SPANISH: (
            "Escala las dimensiones publicadas de 62,4 x 39 ft o 125 x 38 ft "
            "desde 7,15 MHz a la frecuencia actual."
        ),
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
            "Dimensions scaled to another frequency are a heuristic starting "
            "point, not an independent reference. AntennaDesk does not "
            "independently validate the pattern, feedpoint impedance, ground, or "
            "matching."
        ),
        Language.SPANISH: (
            "Geometría inicial publicada por Cebik para 7,15 MHz en espacio libre: "
            "medio cuadrado de 62,4 ft por 39 ft, unos 4,6 dBi y 65 ohm; cortina "
            "bobtail de 125 ft por 38 ft, unos 6,3 dBi y 40 ohm en la unión de la "
            "vertical central con el hilo superior. Las dimensiones escaladas a "
            "otra frecuencia son un punto de partida heurístico, no una referencia "
            "independiente. AntennaDesk no valida independientemente el patrón, la "
            "impedancia de alimentación, el suelo ni la adaptación."
        ),
    },
    "biquad.title": {
        Language.ENGLISH: "Biquad Generator",
        Language.SPANISH: "Generador biquad",
    },
    "biquad.kind": {
        Language.ENGLISH: "Biquad type",
        Language.SPANISH: "Tipo de biquad",
    },
    "biquad.kind.single": {
        Language.ENGLISH: "Biquad (two loops)",
        Language.SPANISH: "Biquad (dos lazos)",
    },
    "biquad.kind.double": {
        Language.ENGLISH: "Double biquad (four loops)",
        Language.SPANISH: "Biquad doble (cuatro lazos)",
    },
    "biquad.loop_side": {
        Language.ENGLISH: "Loop side",
        Language.SPANISH: "Lado del lazo",
    },
    "biquad.loops": {
        Language.ENGLISH: "Loops",
        Language.SPANISH: "Lazos",
    },
    "biquad.height": {
        Language.ENGLISH: "Stack height",
        Language.SPANISH: "Altura de la pila",
    },
    "biquad.reflector_enabled": {
        Language.ENGLISH: "Wire reflector",
        Language.SPANISH: "Reflector de hilo",
    },
    "biquad.reflector_spacing": {
        Language.ENGLISH: "Reflector spacing",
        Language.SPANISH: "Separación del reflector",
    },
    "biquad.reflector": {
        Language.ENGLISH: "Reflector",
        Language.SPANISH: "Reflector",
    },
    "biquad.reflector_off": {
        Language.ENGLISH: "off",
        Language.SPANISH: "desactivado",
    },
    "biquad.reflector_spacing_note": {
        Language.ENGLISH: "Reflector wire {spacing} behind the driven plane.",
        Language.SPANISH: "Hilo reflector {spacing} detrás del plano activo.",
    },
    "biquad.geometry": {
        Language.ENGLISH: (
            "{loops} loops · side {side} {unit} · stack {height} {unit} · "
            "base {base} {unit} · reflector {reflector}"
        ),
        Language.SPANISH: (
            "{loops} lazos · lado {side} {unit} · pila {height} {unit} · "
            "base {base} {unit} · reflector {reflector}"
        ),
    },
    "biquad.load_starting": {
        Language.ENGLISH: "Load quarter-wave starting dimensions",
        Language.SPANISH: "Cargar dimensiones iniciales de cuarto de onda",
    },
    "biquad.load_starting_hint": {
        Language.ENGLISH: "Set the loop side to a quarter wave and the reflector to half that side.",
        Language.SPANISH: "Ajusta el lado del lazo a un cuarto de onda y el reflector a la mitad de ese lado.",
    },
    "biquad.hint": {
        Language.ENGLISH: (
            "A biquad is a vertical stack of square loops with a wire reflector. "
            "The single variant has two loops; the double variant has four. The "
            "loops share their horizontal rails and the feed sits at the midpoint "
            "of the central rail. The quarter-wave side and eighth-wave reflector "
            "spacing are starting heuristics; gain, impedance, and the reflector "
            "model are not independently validated."
        ),
        Language.SPANISH: (
            "Un biquad es una pila vertical de lazos cuadrados con un reflector de "
            "hilo. La variante simple tiene dos lazos; la doble tiene cuatro. Los "
            "lazos comparten sus travesaños horizontales y la alimentación está en "
            "el punto medio del travesaño central. El lado de cuarto de onda y la "
            "separación de octavo de onda son heurísticas iniciales; la ganancia, "
            "la impedancia y el modelo del reflector no están validados "
            "independientemente."
        ),
    },
    "biquad.evidence": {
        Language.ENGLISH: (
            "Starting geometry only. The model is a wire approximation of a "
            "biquad; it does not claim a published gain, feedpoint impedance, or "
            "bandwidth. Measure or simulate the installed antenna before relying "
            "on the result."
        ),
        Language.SPANISH: (
            "Solo geometría inicial. El modelo es una aproximación de hilo de un "
            "biquad; no afirma una ganancia, impedancia de alimentación ni ancho de "
            "banda publicados. Medí o simulá la antena instalada antes de confiar "
            "en el resultado."
        ),
    },
    "beverage.title": {
        Language.ENGLISH: "Beverage Generator",
        Language.SPANISH: "Generador Beverage",
    },
    "beverage.termination_enabled": {
        Language.ENGLISH: "Resistive termination to ground",
        Language.SPANISH: "Terminación resistiva a tierra",
    },
    "beverage.termination_resistance": {
        Language.ENGLISH: "Termination resistance",
        Language.SPANISH: "Resistencia de terminación",
    },
    "beverage.termination": {
        Language.ENGLISH: "Termination",
        Language.SPANISH: "Terminación",
    },
    "beverage.termination_note": {
        Language.ENGLISH: "Resistive termination to ground: {resistance}.",
        Language.SPANISH: "Terminación resistiva a tierra: {resistance}.",
    },
    "beverage.termination_off": {
        Language.ENGLISH: "off",
        Language.SPANISH: "desactivada",
    },
    "beverage.geometry": {
        Language.ENGLISH: (
            "length {length} {unit} · height {height} {unit} · termination {termination}"
        ),
        Language.SPANISH: (
            "longitud {length} {unit} · altura {height} {unit} · terminación {termination}"
        ),
    },
    "beverage.load_starting": {
        Language.ENGLISH: "Load one-wavelength starting length",
        Language.SPANISH: "Cargar longitud inicial de una onda",
    },
    "beverage.load_starting_hint": {
        Language.ENGLISH: "Set the wire length to one wavelength at the current frequency.",
        Language.SPANISH: "Ajusta la longitud del hilo a una onda en la frecuencia actual.",
    },
    "beverage.hint": {
        Language.ENGLISH: (
            "A Beverage is a long horizontal receiving wire fed at the near end "
            "and terminated by a resistor to ground at the far end. The model "
            "uses a short vertical termination wire and a series resistor; the "
            "one-wavelength length and 500 ohm termination are starting "
            "heuristics, not validated low-band receiving performance."
        ),
        Language.SPANISH: (
            "Una Beverage es un hilo receptor horizontal largo alimentado en el "
            "extremo cercano y terminado con una resistencia a tierra en el "
            "extremo lejano. El modelo usa un tramo vertical corto de terminación "
            "y una resistencia serie; la longitud de una onda y la terminación de "
            "500 ohm son heurísticas iniciales, no un rendimiento de recepción "
            "validado en bandas bajas."
        ),
    },
    "beverage.evidence": {
        Language.ENGLISH: (
            "Experimental receiving model. The termination is a wire stub with a "
            "series resistor, not a full ground system. Gain is low and is not "
            "independently validated; use the model for relative pattern and "
            "termination studies, then verify with a measurement."
        ),
        Language.SPANISH: (
            "Modelo de recepción experimental. La terminación es un tramo de hilo "
            "con una resistencia serie, no un sistema de tierra completo. La "
            "ganancia es baja y no está validada independientemente; usá el modelo "
            "para estudios relativos de patrón y terminación, y verificá con una "
            "medición."
        ),
    },
    "loaded_dipole.title": {
        Language.ENGLISH: "Loaded / Linked Dipole Generator",
        Language.SPANISH: "Generador de dipolo cargado / enlazado",
    },
    "loaded_dipole.link_open": {
        Language.ENGLISH: "Links open (center section only)",
        Language.SPANISH: "Enlaces abiertos (solo sección central)",
    },
    "loaded_dipole.link_offset": {
        Language.ENGLISH: "Link / coil offset from feed",
        Language.SPANISH: "Offset de enlace / bobina desde la alimentación",
    },
    "loaded_dipole.active_length": {
        Language.ENGLISH: "Active length",
        Language.SPANISH: "Longitud activa",
    },
    "loaded_dipole.full_length": {
        Language.ENGLISH: "Full length",
        Language.SPANISH: "Longitud total",
    },
    "loaded_dipole.state": {
        Language.ENGLISH: "State",
        Language.SPANISH: "Estado",
    },
    "loaded_dipole.coil_enabled": {
        Language.ENGLISH: "Loading coils",
        Language.SPANISH: "Bobinas de carga",
    },
    "loaded_dipole.coil_inductance": {
        Language.ENGLISH: "Coil inductance",
        Language.SPANISH: "Inductancia de la bobina",
    },
    "loaded_dipole.coil_resistance": {
        Language.ENGLISH: "Coil series resistance",
        Language.SPANISH: "Resistencia serie de la bobina",
    },
    "loaded_dipole.state_loaded": {
        Language.ENGLISH: "{inductance:.3f} µH coils, Q {q}",
        Language.SPANISH: "bobinas de {inductance:.3f} µH, Q {q}",
    },
    "loaded_dipole.state_linked": {
        Language.ENGLISH: "links open",
        Language.SPANISH: "enlaces abiertos",
    },
    "loaded_dipole.state_plain": {
        Language.ENGLISH: "no loading coils",
        Language.SPANISH: "sin bobinas de carga",
    },
    "loaded_dipole.coil_note": {
        Language.ENGLISH: "Two {inductance:.3f} µH loading coils, {offset} from the feed.",
        Language.SPANISH: "Dos bobinas de carga de {inductance:.3f} µH, a {offset} de la alimentación.",
    },
    "loaded_dipole.geometry": {
        Language.ENGLISH: (
            "active {active} {unit} · full {total} {unit} · link offset {offset} {unit} · {state}"
        ),
        Language.SPANISH: (
            "activo {active} {unit} · total {total} {unit} · "
            "offset de enlace {offset} {unit} · {state}"
        ),
    },
    "loaded_dipole.hint": {
        Language.ENGLISH: (
            "The loaded state keeps the full wire and places a series coil at each "
            "link position. The linked state disconnects the outer sections and "
            "leaves only the center wire active. Coil Q is reported from the "
            "explicit series resistance; it is not a hidden correction."
        ),
        Language.SPANISH: (
            "El estado cargado conserva el hilo completo y coloca una bobina serie "
            "en cada posición de enlace. El estado enlazado desconecta las "
            "secciones externas y deja activo solo el hilo central. La Q de la "
            "bobina se informa a partir de la resistencia serie explícita; no es "
            "una corrección oculta."
        ),
    },
    "loaded_dipole.evidence": {
        Language.ENGLISH: (
            "Experimental portable model. The coil is an ideal series R-L load; "
            "core loss, self-capacitance, link contact resistance, and the "
            "installation are not independently validated. Tune with the solver "
            "or a measurement."
        ),
        Language.SPANISH: (
            "Modelo portátil experimental. La bobina es una carga R-L serie ideal; "
            "las pérdidas del núcleo, la capacidad parásita, la resistencia de "
            "contacto de los enlaces y la instalación no están validadas "
            "independientemente. Ajustá con el solver o una medición."
        ),
    },
    "phased_vertical.title": {
        Language.ENGLISH: "Phased Vertical Array Generator",
        Language.SPANISH: "Generador de arreglo vertical en fase",
    },
    "phased_vertical.element_count": {
        Language.ENGLISH: "Verticals",
        Language.SPANISH: "Verticales",
    },
    "phased_vertical.spacing": {
        Language.ENGLISH: "Element spacing",
        Language.SPANISH: "Separación entre elementos",
    },
    "phased_vertical.phase_step": {
        Language.ENGLISH: "Phase step per element",
        Language.SPANISH: "Escalón de fase por elemento",
    },
    "phased_vertical.amplitude_taper": {
        Language.ENGLISH: "Amplitude taper",
        Language.SPANISH: "Atenuación de amplitud",
    },
    "phased_vertical.geometry": {
        Language.ENGLISH: (
            "{count} verticals · spacing {spacing} {unit} · height {height} {unit} · "
            "phase step {phase}° · taper {taper:.0f}% · {radials} radials each"
        ),
        Language.SPANISH: (
            "{count} verticales · separación {spacing} {unit} · altura {height} {unit} · "
            "escalón de fase {phase}° · atenuación {taper:.0f}% · {radials} radiales cada una"
        ),
    },
    "phased_vertical.radial_overlap_warning": {
        Language.ENGLISH: (
            "The radial screens overlap: twice the radial length exceeds the "
            "element spacing. Adjacent radials may cross or touch, which can "
            "produce unreliable NEC impedance or negative resistance. Shorten "
            "the radials, increase the spacing, or model the bonded screen "
            "explicitly."
        ),
        Language.SPANISH: (
            "Las pantallas de radiales se superponen: el doble del largo del "
            "radial supera la separación entre elementos. Los radiales vecinos "
            "pueden cruzarse o tocarse, lo que puede producir impedancia poco "
            "confiable o resistencia negativa en NEC. Acortá los radiales, "
            "aumentá la separación o modelá la pantalla unida explícitamente."
        ),
    },
    "phased_vertical.hint": {
        Language.ENGLISH: (
            "The first vertical is the primary feed with unit amplitude and zero "
            "phase. Later verticals use index x phase step and a linear amplitude "
            "taper. The array feed network is ideal; per-element matching and "
            "feed-line loss are not modeled."
        ),
        Language.SPANISH: (
            "La primera vertical es la alimentación principal con amplitud unitaria "
            "y fase cero. Las siguientes usan índice x escalón de fase y una "
            "atenuación lineal de amplitud. La red de alimentación del arreglo es "
            "ideal; no se modelan el ajuste por elemento ni las pérdidas de línea."
        ),
    },
    "phased_vertical.evidence": {
        Language.ENGLISH: (
            "Experimental array model. The elements are ideal thin wires over the "
            "selected ground; mutual coupling is included by the solver, but the "
            "combining network, per-element matching, feed lines, and installation "
            "are not independently validated. Verify the pattern and match with "
            "the solver or a measurement."
        ),
        Language.SPANISH: (
            "Modelo experimental de arreglo. Los elementos son hilos delgados "
            "ideales sobre el suelo elegido; el solver incluye el acoplamiento "
            "mutuo, pero la red combinadora, el ajuste por elemento, las líneas de "
            "alimentación y la instalación no están validadas independientemente. "
            "Verificá el patrón y el ajuste con el solver o una medición."
        ),
    },
    "phased_vertical.phase_note": {
        Language.ENGLISH: (
            "Phase step {phase}° · amplitude taper {taper}% · first vertical is "
            "the primary feed · ideal combining network"
        ),
        Language.SPANISH: (
            "Escalón de fase {phase}° · atenuación de amplitud {taper}% · la "
            "primera vertical es la alimentación principal · red combinadora ideal"
        ),
    },
    "phased_vertical.constraint.phase": {
        Language.ENGLISH: "The phase step must stay within ±360°.",
        Language.SPANISH: "El escalón de fase debe quedar dentro de ±360°.",
    },
    "phased_vertical.constraint.amplitude_taper": {
        Language.ENGLISH: "The amplitude taper must stay between 0 and 0.9.",
        Language.SPANISH: "La atenuación de amplitud debe quedar entre 0 y 0,9.",
    },
    "hexbeam.title": {
        Language.ENGLISH: "Hexbeam Generator",
        Language.SPANISH: "Generador de hexbeam",
    },
    "hexbeam.driver_half": {
        Language.ENGLISH: "Driver half-length",
        Language.SPANISH: "Semilongitud del excitado",
    },
    "hexbeam.reflector_half": {
        Language.ENGLISH: "Reflector half-length",
        Language.SPANISH: "Semilongitud del reflector",
    },
    "hexbeam.turning_radius": {
        Language.ENGLISH: "Turning radius",
        Language.SPANISH: "Radio de giro",
    },
    "hexbeam.tip_gap": {
        Language.ENGLISH: "Tip gap",
        Language.SPANISH: "Separación de puntas",
    },
    "hexbeam.feed_gap": {
        Language.ENGLISH: "Center feed gap",
        Language.SPANISH: "Brecha de alimentación central",
    },
    "hexbeam.element_separation": {
        Language.ENGLISH: "Driver/reflector center offset",
        Language.SPANISH: "Desplazamiento entre centros",
    },
    "hexbeam.geometry": {
        Language.ENGLISH: (
            "driver {driver} {unit} half · reflector {reflector} {unit} half · "
            "span {span} {unit} · turning radius {radius} {unit}"
        ),
        Language.SPANISH: (
            "excitado {driver} {unit} semilongitud · reflector {reflector} {unit} "
            "semilongitud · envergadura {span} {unit} · radio de giro {radius} {unit}"
        ),
    },
    "hexbeam.hint": {
        Language.ENGLISH: (
            "The driver is a W-shaped wire with a small center feed gap; the "
            "reflector is a U-shaped wire just behind it. The apexes lie on the "
            "60° spreader rays at the turning radius. The published 20 m reference "
            "is scaled linearly with frequency."
        ),
        Language.SPANISH: (
            "El excitado es un hilo en forma de W con una pequeña brecha central de "
            "alimentación; el reflector es un hilo en forma de U justo detrás. Los "
            "vértices se apoyan en los rayos de 60° a la distancia del radio de giro. "
            "La referencia publicada de 20 m se escala linealmente con la frecuencia."
        ),
    },
    "hexbeam.evidence": {
        Language.ENGLISH: (
            "Published starting dimensions from G3TXQ (219 in driver half, 207 in "
            "reflector half, 24 in tip gap, 130 in turning radius at 14.184 MHz), "
            "reconstructed as a bent wire. The frame, spreader sag, feed balun, "
            "and multi-band nesting are not modeled; gain, front-to-back ratio, "
            "and impedance are not independently validated."
        ),
        Language.SPANISH: (
            "Dimensiones iniciales publicadas por G3TXQ (219 in de semilongitud del "
            "excitado, 207 in del reflector, 24 in de separación de puntas y 130 in "
            "de radio de giro a 14,184 MHz), reconstruidas como hilo doblado. No se "
            "modelan el marco, la flecha de los separadores, el balun ni el anidado "
            "multibanda; la ganancia, la relación delante/atrás y la impedancia no "
            "están validadas independientemente."
        ),
    },
    "hexbeam.constraint.driver_length": {
        Language.ENGLISH: "The driver half must exceed 1.5 times the turning radius.",
        Language.SPANISH: "La semilongitud del excitado debe superar 1,5 veces el radio de giro.",
    },
    "hexbeam.constraint.reflector_length": {
        Language.ENGLISH: "The reflector half is too short for the turning radius and tip gap.",
        Language.SPANISH: "La semilongitud del reflector es demasiado corta para el radio de giro y la separación de puntas.",
    },
    "hexbeam.geometry_note": {
        Language.ENGLISH: (
            "W driver and U reflector on a six-spreader frame; turning radius "
            "{radius}. Frame, spreader sag, and balun are not modeled."
        ),
        Language.SPANISH: (
            "Excitado en W y reflector en U sobre un marco de seis separadores; "
            "radio de giro {radius}. No se modelan el marco, la flecha de los "
            "separadores ni el balun."
        ),
    },
    "hexbeam.spreader_angle_note": {
        Language.ENGLISH: (
            "spreader angle {spreader}° from the boom axis; wire bend at the apex {bend}°"
        ),
        Language.SPANISH: (
            "ángulo del separador {spreader}° desde el eje del boom; quiebre del "
            "hilo en el vértice {bend}°"
        ),
    },
    "hexbeam.tip_gap_note": {
        Language.ENGLISH: (
            "published tip-gap parameter {published}; drawn clear tip-to-tip gap {clear}"
        ),
        Language.SPANISH: (
            "parámetro publicado de separación de puntas {published}; separación "
            "libre dibujada entre puntas {clear}"
        ),
    },
    "trap_yagi.title": {
        Language.ENGLISH: "Trapped Yagi Generator",
        Language.SPANISH: "Generador de Yagi con trampas",
    },
    "trap_yagi.high_band_frequency": {
        Language.ENGLISH: "High-band frequency",
        Language.SPANISH: "Frecuencia de banda alta",
    },
    "trap_yagi.element_count": {
        Language.ENGLISH: "Elements",
        Language.SPANISH: "Elementos",
    },
    "trap_yagi.driven_length": {
        Language.ENGLISH: "Driven element length",
        Language.SPANISH: "Longitud del elemento excitado",
    },
    "trap_yagi.reflector_spacing": {
        Language.ENGLISH: "Reflector spacing",
        Language.SPANISH: "Separación del reflector",
    },
    "trap_yagi.director_spacing": {
        Language.ENGLISH: "Director spacing",
        Language.SPANISH: "Separación del director",
    },
    "trap_yagi.reflector_scale": {
        Language.ENGLISH: "Reflector length factor",
        Language.SPANISH: "Factor de longitud del reflector",
    },
    "trap_yagi.director_scale": {
        Language.ENGLISH: "Director length factor",
        Language.SPANISH: "Factor de longitud del director",
    },
    "trap_yagi.trap_inset": {
        Language.ENGLISH: "Trap inset from center",
        Language.SPANISH: "Inserción de la trampa desde el centro",
    },
    "trap_yagi.trap_frequency": {
        Language.ENGLISH: "Trap frequency",
        Language.SPANISH: "Frecuencia de la trampa",
    },
    "trap_yagi.trap_inductance": {
        Language.ENGLISH: "Trap inductance",
        Language.SPANISH: "Inductancia de la trampa",
    },
    "trap_yagi.geometry": {
        Language.ENGLISH: (
            "{count} elements · driven {driven} {unit} · boom {boom} {unit} · "
            "trap inset {inset} {unit} · traps {trap:.3f} MHz"
        ),
        Language.SPANISH: (
            "{count} elementos · excitado {driven} {unit} · boom {boom} {unit} · "
            "inserción de trampa {inset} {unit} · trampas {trap:.3f} MHz"
        ),
    },
    "trap_yagi.hint": {
        Language.ENGLISH: (
            "Each element has one parallel LC trap on each side of its center. "
            "The traps are resonant on the high band and isolate the outer tips "
            "there; on the low band they load the elements. The trap model is "
            "ideal and has no core or dielectric loss."
        ),
        Language.SPANISH: (
            "Cada elemento tiene una trampa LC en paralelo a cada lado de su "
            "centro. Las trampas resuenan en la banda alta y aíslan allí las "
            "puntas externas; en la banda baja cargan los elementos. El modelo de "
            "trampa es ideal y no tiene pérdidas de núcleo ni dieléctricas."
        ),
    },
    "trap_yagi.evidence": {
        Language.ENGLISH: (
            "Experimental trapped-Yagi model. The parallel LC traps are ideal, "
            "and boom mounting, trap hardware, feed line, and matching network "
            "are not modeled. Gain, front-to-back ratio, and impedance on either "
            "band are not independently validated."
        ),
        Language.SPANISH: (
            "Modelo experimental de Yagi con trampas. Las trampas LC en paralelo "
            "son ideales y no se modelan el montaje en boom, el hardware de las "
            "trampas, la línea de alimentación ni la red de ajuste. La ganancia, "
            "la relación delante/atrás y la impedancia en ambas bandas no están "
            "validadas independientemente."
        ),
    },
    "trap_yagi.constraint.trap_inset": {
        Language.ENGLISH: "The trap inset must lie inside every element.",
        Language.SPANISH: "La inserción de la trampa debe quedar dentro de cada elemento.",
    },
    "trap_yagi.constraint.reflector_scale": {
        Language.ENGLISH: "The reflector length factor must stay between 1.0 and 1.2.",
        Language.SPANISH: "El factor de longitud del reflector debe quedar entre 1,0 y 1,2.",
    },
    "trap_yagi.constraint.director_scale": {
        Language.ENGLISH: "The director length factor must stay between 0.8 and 1.0.",
        Language.SPANISH: "El factor de longitud del director debe quedar entre 0,8 y 1,0.",
    },
    "trap_yagi.geometry_note": {
        Language.ENGLISH: (
            "Traps at {inset} from each element center, resonant at {trap} MHz. "
            "Boom mounting, trap loss, and the matching network are not modeled."
        ),
        Language.SPANISH: (
            "Trampas a {inset} del centro de cada elemento, resonantes en {trap} "
            "MHz. No se modelan el montaje en boom, las pérdidas de las trampas "
            "ni la red de ajuste."
        ),
    },
    "discone.title": {
        Language.ENGLISH: "Discone Generator",
        Language.SPANISH: "Generador de discono",
    },
    "discone.cone_height": {
        Language.ENGLISH: "Cone height",
        Language.SPANISH: "Altura del cono",
    },
    "discone.cone_radius": {
        Language.ENGLISH: "Cone base radius",
        Language.SPANISH: "Radio de la base del cono",
    },
    "discone.disc_radius": {
        Language.ENGLISH: "Disc radius",
        Language.SPANISH: "Radio del disco",
    },
    "discone.disc_gap": {
        Language.ENGLISH: "Feed gap",
        Language.SPANISH: "Brecha de alimentación",
    },
    "discone.wire_count": {
        Language.ENGLISH: "Radial wires",
        Language.SPANISH: "Hilos radiales",
    },
    "discone.geometry": {
        Language.ENGLISH: (
            "cone {height} {unit} high · base radius {radius} {unit} · disc {disc} {unit} · "
            "{count} radial wires"
        ),
        Language.SPANISH: (
            "cono de {height} {unit} de alto · radio de base {radius} {unit} · "
            "disco {disc} {unit} · {count} hilos radiales"
        ),
    },
    "discone.hint": {
        Language.ENGLISH: (
            "The cone opens downward and the disc sits above the apex with a "
            "small feed gap. The source is on the vertical wire across that gap. "
            "The cone and disc are radial wire approximations, not solid surfaces."
        ),
        Language.SPANISH: (
            "El cono se abre hacia abajo y el disco está sobre el vértice con una "
            "pequeña brecha de alimentación. La fuente está en el hilo vertical "
            "que cruza esa brecha. El cono y el disco son aproximaciones de hilos "
            "radiales, no superficies sólidas."
        ),
    },
    "discone.evidence": {
        Language.ENGLISH: (
            "Experimental discone model. The radial wires approximate the solid "
            "cone and disc; the coax, mast, and feed transition are not modeled. "
            "Impedance, bandwidth, and pattern are not independently validated. "
            "Use it as a starting point and verify with the solver or a measurement."
        ),
        Language.SPANISH: (
            "Modelo experimental de discono. Los hilos radiales aproximan el cono "
            "y el disco sólidos; no se modelan el coaxil, el mástil ni la "
            "transición de alimentación. La impedancia, el ancho de banda y el "
            "patrón no están validados independientemente. Usalo como punto de "
            "partida y verificá con el solver o una medición."
        ),
    },
    "discone.constraint.disc_radius": {
        Language.ENGLISH: "The disc radius must be at least the cone radius.",
        Language.SPANISH: "El radio del disco debe ser al menos el radio del cono.",
    },
    "discone.angle_note": {
        Language.ENGLISH: ("cone half-angle {half}°; {count} radial wires every {step}°"),
        Language.SPANISH: ("semángulo del cono {half}°; {count} hilos radiales cada {step}°"),
    },
    "discone.geometry_note": {
        Language.ENGLISH: (
            "Radial-wire cone and disc. The source is across the small apex gap; "
            "coax, mast, and solid surfaces are not modeled."
        ),
        Language.SPANISH: (
            "Cono y disco de hilos radiales. La fuente está en la pequeña brecha "
            "del vértice; no se modelan coaxil, mástil ni superficies sólidas."
        ),
    },
    "quad_beam.title": {
        Language.ENGLISH: "Quad Beam Generator",
        Language.SPANISH: "Generador de beam cuádruple",
    },
    "quad_beam.element_count": {
        Language.ENGLISH: "Loops",
        Language.SPANISH: "Lazos",
    },
    "quad_beam.loop_side": {
        Language.ENGLISH: "Driven loop side",
        Language.SPANISH: "Lado del lazo excitado",
    },
    "quad_beam.reflector_spacing": {
        Language.ENGLISH: "Reflector spacing",
        Language.SPANISH: "Separación del reflector",
    },
    "quad_beam.director_spacing": {
        Language.ENGLISH: "Director spacing",
        Language.SPANISH: "Separación del director",
    },
    "quad_beam.reflector_scale": {
        Language.ENGLISH: "Reflector length factor",
        Language.SPANISH: "Factor de longitud del reflector",
    },
    "quad_beam.director_scale": {
        Language.ENGLISH: "Director length factor",
        Language.SPANISH: "Factor de longitud del director",
    },
    "quad_beam.geometry": {
        Language.ENGLISH: (
            "{count} loops · driven side {side} {unit} · spacing {spacing} {unit} · "
            "boom {boom} {unit} · height {height} {unit}"
        ),
        Language.SPANISH: (
            "{count} lazos · lado excitado {side} {unit} · separación {spacing} {unit} · "
            "boom {boom} {unit} · altura {height} {unit}"
        ),
    },
    "quad_beam.hint": {
        Language.ENGLISH: (
            "The reflector sits behind the driven loop and the optional director "
            "in front. The feed is the midpoint of the left vertical side of the "
            "driven loop. Loop sides and spacing are starting heuristics; the "
            "boom, spreaders, and matching network are not modeled."
        ),
        Language.SPANISH: (
            "El reflector está detrás del lazo excitado y el director opcional "
            "delante. La alimentación es el punto medio del lado vertical "
            "izquierdo del lazo excitado. Los lados y la separación son heurísticas "
            "de partida; no se modelan el boom, los separadores ni la red de ajuste."
        ),
    },
    "quad_beam.evidence": {
        Language.ENGLISH: (
            "Experimental quad-beam model. The loops are ideal thin-wire squares "
            "over the selected ground. Gain, front-to-back ratio, feedpoint "
            "impedance, boom and mast effects, and the matching network are not "
            "independently validated. Verify the pattern and match with the solver "
            "or a measurement."
        ),
        Language.SPANISH: (
            "Modelo experimental de beam cuádruple. Los lazos son cuadrados de "
            "hilo delgado ideales sobre el suelo elegido. La ganancia, la relación "
            "delante/atrás, la impedancia de alimentación, los efectos del boom y "
            "del mástil y la red de ajuste no están validadas independientemente. "
            "Verificá el patrón y el ajuste con el solver o una medición."
        ),
    },
    "quad_beam.geometry_note": {
        Language.ENGLISH: (
            "Square loops across the boom; feed at the driven loop's left side "
            "midpoint. Boom, spreaders, and matching network are not modeled."
        ),
        Language.SPANISH: (
            "Lazos cuadrados perpendiculares al boom; alimentación en el punto "
            "medio del lado izquierdo del lazo excitado. No se modelan el boom, "
            "los separadores ni la red de ajuste."
        ),
    },
    "quad_beam.constraint.reflector_scale": {
        Language.ENGLISH: "The reflector length factor must stay between 1.0 and 1.2.",
        Language.SPANISH: "El factor de longitud del reflector debe quedar entre 1,0 y 1,2.",
    },
    "quad_beam.constraint.director_scale": {
        Language.ENGLISH: "The director length factor must stay between 0.8 and 1.0.",
        Language.SPANISH: "El factor de longitud del director debe quedar entre 0,8 y 1,0.",
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
        Language.ENGLISH: "Load Cushcraft AR-6 dimensions (52 MHz)",
        Language.SPANISH: "Cargar dimensiones Cushcraft AR-6 (52 MHz)",
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
    "endfed.shortened_presets": {
        Language.ENGLISH: "Shortened EFHW reference",
        Language.SPANISH: "Referencia EFHW acortada",
    },
    "endfed.preset.shortened_80_10": {
        Language.ENGLISH: "80-10 m",
        Language.SPANISH: "80-10 m",
    },
    "endfed.preset.shortened_40_10": {
        Language.ENGLISH: "40-20-10 m",
        Language.SPANISH: "40-20-10 m",
    },
    "endfed.loading_coil": {
        Language.ENGLISH: "Loading coil",
        Language.SPANISH: "Bobina de carga",
    },
    "endfed.loading_coil_offset": {
        Language.ENGLISH: "Coil position from feed",
        Language.SPANISH: "Posición de la bobina desde la alimentación",
    },
    "endfed.loading_coil_inductance": {
        Language.ENGLISH: "Coil inductance",
        Language.SPANISH: "Inductancia de la bobina",
    },
    "endfed.loading_coil_resistance": {
        Language.ENGLISH: "Coil series resistance",
        Language.SPANISH: "Resistencia serie de la bobina",
    },
    "endfed.loading_coil_q": {
        Language.ENGLISH: "Coil Q at design frequency",
        Language.SPANISH: "Q de la bobina en la frecuencia de diseño",
    },
    "endfed.ideal_coil": {
        Language.ENGLISH: "ideal",
        Language.SPANISH: "ideal",
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
    "endfed.shortened_80_10_title": {
        Language.ENGLISH: "Shortened EFHW 80-10 m",
        Language.SPANISH: "EFHW acortada 80-10 m",
    },
    "endfed.shortened_40_10_title": {
        Language.ENGLISH: "Shortened EFHW 40-20-10 m",
        Language.SPANISH: "EFHW acortada 40-20-10 m",
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
    "endfed.shortened_80_10_hint": {
        Language.ENGLISH: (
            "Published shortened EFHW: 20.35 m lower section, 110 µH loading "
            "coil, 2.39 m top section, 49:1 transformer, and a 100 pF matching "
            "capacitor. The default is horizontal at 10 m; change the feed/end "
            "heights for a sloper, or enable the inverted-L bend for the published "
            "8 m vertical / about 15 m horizontal starting installation. The "
            "primary 100 pF shunt and 0.198 µH leakage starting value are modeled; "
            "the sharp bend, choke, ground, core loss, winding capacitance, and "
            "capacitor ESR are not independently validated."
        ),
        Language.SPANISH: (
            "EFHW acortada publicada: tramo inferior de 20,35 m, bobina de carga "
            "de 110 µH, tramo superior de 2,39 m, transformador 49:1 y capacitor "
            "de adaptación de 100 pF. El valor por defecto es horizontal a 10 m; "
            "cambiá las alturas de alimentación/extremo para un sloper, o "
            "habilitá el codo en L invertida para la instalación publicada de "
            "unos 8 m verticales y 15 m horizontales. Se modelan el shunt de "
            "100 pF en el primario y una fuga inicial de 0,198 µH; el codo recto, "
            "el choke, el suelo, las pérdidas del núcleo, la capacidad de los "
            "bobinados y el ESR del capacitor no están validados independientemente."
        ),
    },
    "endfed.shortened_40_10_hint": {
        Language.ENGLISH: (
            "Published shortened EFHW: 10.01 m lower section, 23 µH loading "
            "coil, 1.85 m top section, 49:1 transformer, and a 100 pF matching "
            "capacitor. The default is horizontal at 10 m; change the feed/end "
            "heights for a sloper, or enable the inverted-L bend. The primary "
            "100 pF shunt and 0.198 µH leakage starting value are modeled; the "
            "sharp bend, choke, ground, support geometry, core loss, winding "
            "capacitance, and capacitor ESR are not independently validated. "
            "CA4EMT documents a different 40-20-10 variant (34 µH, 1.6 m top, "
            "1:8); this preset follows the 23 µH/100 pF schematic."
        ),
        Language.SPANISH: (
            "EFHW acortada publicada: tramo inferior de 10,01 m, bobina de carga "
            "de 23 µH, tramo superior de 1,85 m, transformador 49:1 y capacitor "
            "de adaptación de 100 pF. El valor por defecto es horizontal a 10 m; "
            "cambiá las alturas de alimentación/extremo para un sloper, o "
            "habilitá el codo en L invertida. Se modelan el shunt de 100 pF en "
            "el primario y una fuga inicial de 0,198 µH; el codo recto, el "
            "choke, el suelo, la geometría de soporte, las pérdidas del núcleo, "
            "la capacidad de los bobinados y el ESR del capacitor no están "
            "validados independientemente. CA4EMT documenta otra variante de "
            "40-20-10 (34 µH, tramo superior de 1,6 m, 1:8); este preset sigue "
            "el esquema de 23 µH/100 pF."
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
    "endfed.shortened_80_10_evidence": {
        Language.ENGLISH: (
            "Published starting dimensions from G0KYA, EA7EER, and G4WIF. "
            "The exact 110 µH / 20.35 m / 2.39 m geometry is reference-backed "
            "for construction only. The primary 100 pF shunt and 0.198 µH "
            "leakage starting estimate are modeled; the optional inverted-L bend "
            "uses a sharp 90° corner and is not independently validated. Core "
            "loss, winding capacitance, capacitor ESR, common-mode choke, ground, "
            "and installation are not modeled."
        ),
        Language.SPANISH: (
            "Dimensiones iniciales publicadas por G0KYA, EA7EER y G4WIF. La "
            "geometría exacta de 110 µH / 20,35 m / 2,39 m tiene referencia "
            "solo para la construcción. Se modelan el shunt de 100 pF en el "
            "primario y una fuga inicial de 0,198 µH; el codo opcional en L "
            "invertida usa una esquina recta de 90° y no está validado "
            "independientemente. Las pérdidas del núcleo, la capacidad de los "
            "bobinados, el ESR del capacitor, el choke de modo común, el suelo y "
            "la instalación no están modelados."
        ),
    },
    "endfed.shortened_40_10_evidence": {
        Language.ENGLISH: (
            "Published starting dimensions from the radioaficion / PA0EJH "
            "schematic: 23 µH / 10.01 m / 1.85 m. The primary 100 pF shunt and "
            "0.198 µH leakage starting estimate are modeled; the optional "
            "inverted-L bend is a sharp 90° corner with no independent reference. "
            "Core loss, winding capacitance, capacitor ESR, choke, ground, and "
            "installation are not modeled. CA4EMT documents a different 34 µH "
            "variant."
        ),
        Language.SPANISH: (
            "Dimensiones iniciales publicadas en el esquema de radioaficion / "
            "PA0EJH: 23 µH / 10,01 m / 1,85 m. Se modelan el shunt de 100 pF "
            "en el primario y una fuga inicial de 0,198 µH; el codo opcional en "
            "L invertida es una esquina recta de 90° sin referencia independiente. "
            "Las pérdidas del núcleo, la capacidad de los bobinados, el ESR del "
            "capacitor, el choke, el suelo y la instalación no están modelados. "
            "CA4EMT documenta otra variante de 34 µH."
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
    "endfed.bend_enabled": {
        Language.ENGLISH: "Inverted-L bend",
        Language.SPANISH: "Codo en L invertida",
    },
    "endfed.bend_vertical": {
        Language.ENGLISH: "Vertical section",
        Language.SPANISH: "Tramo vertical",
    },
    "endfed.bend_vertical_hint": {
        Language.ENGLISH: (
            "Conductor length from the feed up to the bend. The horizontal run is "
            "the remaining wire length. The published G0KYA installation uses about "
            "8 m vertical and 15 m horizontal."
        ),
        Language.SPANISH: (
            "Longitud de conductor desde la alimentación hasta el codo. El tramo "
            "horizontal es el resto de la longitud del hilo. La instalación publicada "
            "de G0KYA usa unos 8 m verticales y 15 m horizontales."
        ),
    },
    "endfed.bend_horizontal": {
        Language.ENGLISH: "Horizontal run",
        Language.SPANISH: "Tramo horizontal",
    },
    "endfed.bend_horizontal_none": {
        Language.ENGLISH: "Disabled; the wire stays straight or sloped.",
        Language.SPANISH: "Deshabilitado; el hilo queda recto o inclinado.",
    },
    "endfed.bend_horizontal_value": {
        Language.ENGLISH: "{horizontal} {unit} horizontal · top at {top} {unit}",
        Language.SPANISH: "{horizontal} {unit} horizontales · parte superior a {top} {unit}",
    },
    "endfed.bend_geometry": {
        Language.ENGLISH: (
            "feed {feed} {unit} · vertical {vertical} {unit} · horizontal "
            "{horizontal} {unit} · top {top_height} {unit} · counterpoise "
            "{counterpoise} · {ratio}:1"
        ),
        Language.SPANISH: (
            "alimentación {feed} {unit} · vertical {vertical} {unit} · horizontal "
            "{horizontal} {unit} · parte superior {top_height} {unit} · contrapeso "
            "{counterpoise} · {ratio}:1"
        ),
    },
    "endfed.loaded_bend_geometry": {
        Language.ENGLISH: (
            "feed {feed} {unit} · vertical {vertical} {unit} · horizontal "
            "{horizontal} {unit} · top {top_height} {unit} · coil {coil} {unit} · "
            "{inductance} µH · top section {top} {unit} · counterpoise "
            "{counterpoise} · {ratio}:1"
        ),
        Language.SPANISH: (
            "alimentación {feed} {unit} · vertical {vertical} {unit} · horizontal "
            "{horizontal} {unit} · parte superior {top_height} {unit} · bobina "
            "{coil} {unit} · {inductance} µH · tramo superior {top} {unit} · "
            "contrapeso {counterpoise} · {ratio}:1"
        ),
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
    "endfed.feed_section_summary": {
        Language.ENGLISH: "feed section {value} {unit}",
        Language.SPANISH: "tramo de alimentación {value} {unit}",
    },
    "endfed.installation_return_summary": {
        Language.ENGLISH: "installation return {value} {unit} (proxy)",
        Language.SPANISH: "retorno de instalación {value} {unit} (proxy)",
    },
    "endfed.loaded_geometry": {
        Language.ENGLISH: (
            "Feed {feed} {unit} · end {end} {unit} · coil at {coil} {unit} · "
            "{inductance} µH · top {top} {unit} · counterpoise {counterpoise} · "
            "{ratio}:1"
        ),
        Language.SPANISH: (
            "Alimentación {feed} {unit} · extremo {end} {unit} · bobina a "
            "{coil} {unit} · {inductance} µH · tramo superior {top} {unit} · "
            "contrapeso {counterpoise} · {ratio}:1"
        ),
    },
    "endfed.transformer_ratio": {
        Language.ENGLISH: "Transformer ratio",
        Language.SPANISH: "Relación del transformador",
    },
    "endfed.matching_capacitance": {
        Language.ENGLISH: "Matching capacitor (primary)",
        Language.SPANISH: "Capacitor de adaptación (primario)",
    },
    "endfed.matching_capacitance_hint": {
        Language.ENGLISH: (
            "Ideal shunt capacitor across the 49:1 transformer primary. "
            "100 pF is the published starting value; it compensates the "
            "transformer leakage inductance."
        ),
        Language.SPANISH: (
            "Capacitor shunt ideal en el primario del transformador 49:1. "
            "100 pF es el valor inicial publicado; compensa la inductancia de "
            "fuga del transformador."
        ),
    },
    "endfed.transformer_leakage": {
        Language.ENGLISH: "Transformer leakage",
        Language.SPANISH: "Fuga del transformador",
    },
    "endfed.transformer_leakage_hint": {
        Language.ENGLISH: (
            "Primary leakage inductance. The 0.198 µH default is a starting "
            "estimate from Squash Practice's measured 49:1 transformer, not this "
            "exact build; "
            "edit it or set 0 for an ideal transformer."
        ),
        Language.SPANISH: (
            "Inductancia de fuga del primario. El valor inicial de 0,198 µH "
            "es una estimación de un transformador 49:1 medido, no de esta "
            "construcción exacta; editalo o usá 0 para un transformador ideal."
        ),
    },
    "endfed.matching_summary": {
        Language.ENGLISH: "matching {capacitance} pF + {leakage} µH leakage",
        Language.SPANISH: "adaptación {capacitance} pF + {leakage} µH de fuga",
    },
    "endfed.matching_override": {
        Language.ENGLISH: (
            "Internal matching values are retained but inactive because the project "
            "matching network overrides them. Use Edit or Remove in Feed & matching."
        ),
        Language.SPANISH: (
            "Los valores de adaptación internos se retienen pero están inactivos "
            "porque la red de adaptación del proyecto los reemplaza. Usá Editar o "
            "Quitar en Alimentación y adaptación."
        ),
    },
    "endfed.counterpoise_enabled": {
        Language.ENGLISH: "Use counterpoise",
        Language.SPANISH: "Usar contrapeso",
    },
    "endfed.feed_section": {
        Language.ENGLISH: "Fixed feed section",
        Language.SPANISH: "Tramo de alimentación fijo",
    },
    "endfed.feed_section_hint": {
        Language.ENGLISH: (
            "Modeling partition at the start of the same wire; it stabilizes the "
            "NEC end-fed source. Do not cut a separate conductor."
        ),
        Language.SPANISH: (
            "Partición de modelo al inicio del mismo hilo; estabiliza la fuente "
            "NEC alimentada en el extremo. No cortar un conductor separado."
        ),
    },
    "endfed.installation_return": {
        Language.ENGLISH: "Installation return (proxy)",
        Language.SPANISH: "Retorno de instalación (proxy)",
    },
    "endfed.installation_return_hint": {
        Language.ENGLISH: (
            "A short return models the unavoidable coax/mast/earth path. It is "
            "not a physical radial; the real coax routing dominates the SWR. "
            "Use a real counterpoise when available."
        ),
        Language.SPANISH: (
            "Un retorno corto modela el camino inevitable del coaxil/mástil/"
            "tierra. No es una radial física; el ruteo real del coaxil domina el "
            "SWR. Usá un contrapeso real cuando esté disponible."
        ),
    },
    "endfed.warning.feed_section": {
        Language.ENGLISH: ("No fixed feed section: the end-fed source is segmentation-sensitive."),
        Language.SPANISH: (
            "Sin tramo de alimentación fijo: la fuente alimentada en el extremo es "
            "sensible a la segmentación."
        ),
    },
    "endfed.warning.return": {
        Language.ENGLISH: (
            "No counterpoise or installation return: feedpoint impedance depends "
            "on the coax/mast/earth path."
        ),
        Language.SPANISH: (
            "Sin contrapeso ni retorno de instalación: la impedancia de entrada "
            "depende del camino del coaxil/mástil/tierra."
        ),
    },
    "endfed.warning.matching_leakage": {
        Language.ENGLISH: (
            "Primary matching capacitor without transformer leakage: set a "
            "measured leakage or treat the capacitor as experimental."
        ),
        Language.SPANISH: (
            "Capacitor de adaptación en el primario sin fuga del transformador: "
            "ingresá una fuga medida o tratá el capacitor como experimental."
        ),
    },
    "endfed.convergence_check": {
        Language.ENGLISH: "Check convergence",
        Language.SPANISH: "Verificar convergencia",
    },
    "endfed.convergence_running": {
        Language.ENGLISH: "Checking segment convergence...",
        Language.SPANISH: "Verificando convergencia de segmentos...",
    },
    "endfed.convergence_converged": {
        Language.ENGLISH: ("Converged: R, X and SWR are stable across segment counts."),
        Language.SPANISH: ("Convergido: R, X y SWR son estables entre segmentaciones."),
    },
    "endfed.convergence_unresolved": {
        Language.ENGLISH: (
            "Not converged: the absolute SWR is segmentation-sensitive; verify with a VNA."
        ),
        Language.SPANISH: (
            "No convergido: el SWR absoluto es sensible a la segmentación; verificá con VNA."
        ),
    },
    "endfed.convergence_impedance_converged": {
        Language.ENGLISH: ("Impedance converged: R and X are stable across segment counts."),
        Language.SPANISH: ("Impedancia convergida: R y X son estables entre segmentaciones."),
    },
    "endfed.convergence_impedance_unresolved": {
        Language.ENGLISH: ("Not converged: R or X changes with segmentation."),
        Language.SPANISH: ("No convergida: R o X cambian con la segmentación."),
    },
    "endfed.convergence_result": {
        Language.ENGLISH: (
            "{status}\n{points}\nSWR spread {swr_spread:.3f} · R spread "
            "{resistance_spread:.1%} · X spread {reactance_spread:.2f} Ω"
        ),
        Language.SPANISH: (
            "{status}\n{points}\nDispersión de SWR {swr_spread:.3f} · R "
            "{resistance_spread:.1%} · X {reactance_spread:.2f} Ω"
        ),
    },
    "endfed.convergence_result_impedance": {
        Language.ENGLISH: (
            "{status}\n{points}\nR spread {resistance_spread:.2f} Ω · X "
            "spread {reactance_spread:.2f} Ω\nSWR is informational; the "
            "matching unit is not fully modeled."
        ),
        Language.SPANISH: (
            "{status}\n{points}\nDispersión de R {resistance_spread:.2f} Ω · X "
            "{reactance_spread:.2f} Ω\nEl SWR es informativo; la unidad de "
            "adaptación no está completamente modelada."
        ),
    },
    "endfed.convergence_matching_note": {
        Language.ENGLISH: (
            "The primary 100 pF shunt and leakage estimate are modeled, but "
            "core loss, capacitor ESR, winding capacitance, and the exact "
            "transformer are not; use the R/X stability and verify the absolute "
            "SWR with a VNA."
        ),
        Language.SPANISH: (
            "Se modelan el shunt de 100 pF en el primario y la fuga estimada, "
            "pero no las pérdidas del núcleo, el ESR del capacitor, la capacidad "
            "de los bobinados ni el transformador exacto; usá la estabilidad de "
            "R/X y verificá el SWR absoluto con un VNA."
        ),
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
        Language.ENGLISH: "Load 20 m reference scaled to current frequency",
        Language.SPANISH: "Cargar referencia de 20 m escalada a la frecuencia actual",
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
            "with a horizontal boom. The reference preset scales the published "
            "20 m wire dimensions to the current frequency and keeps the current "
            "height, ground, wire radius, and polarization."
        ),
        Language.SPANISH: (
            "El generador crea un reflector y un elemento alimentado con puntas "
            "dobladas. La polarización vertical ubica todo el rectángulo en un "
            "plano vertical con el boom horizontal. El preset de referencia escala "
            "las dimensiones publicadas de alambre de 20 m a la frecuencia actual y "
            "conserva la altura, el ground, el radio de hilo y la polarización "
            "actuales."
        ),
    },
    "moxon.evidence": {
        Language.ENGLISH: (
            "The exact 14.17 MHz Cebik 20 m wire dimensions are reference-backed. "
            "Dimensions scaled to another frequency or edited are a heuristic "
            "starting point, not an independent reference."
        ),
        Language.SPANISH: (
            "Las dimensiones exactas de Cebik para alambre de 20 m a 14,17 MHz "
            "tienen referencia publicada. Las dimensiones escaladas a otra "
            "frecuencia o editadas son un punto de partida heurístico, no una "
            "referencia independiente."
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
        Language.ENGLISH: "Load 102 in example (14.1 MHz)",
        Language.SPANISH: "Cargar ejemplo de 102 in (14,1 MHz)",
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
    "yagi.taper_length": {
        Language.ENGLISH: "Tapered tip length (0 = straight)",
        Language.SPANISH: "Longitud de punta cónica (0 = recto)",
    },
    "yagi.taper_radius": {
        Language.ENGLISH: "Tapered tip radius",
        Language.SPANISH: "Radio de punta cónica",
    },
    "yagi.taper_geometry": {
        Language.ENGLISH: "tips {length} {unit} at {radius} {radius_unit}",
        Language.SPANISH: "puntas {length} {unit} a {radius} {radius_unit}",
    },
    "yagi.taper_note": {
        Language.ENGLISH: "tapered tips: {length}; tip radius {radius}",
        Language.SPANISH: "puntas cónicas: {length}; radio de punta {radius}",
    },
    "yagi.taper_summary": {
        Language.ENGLISH: "Tapered tips",
        Language.SPANISH: "Puntas cónicas",
    },
    "yagi.boom_note": {
        Language.ENGLISH: (
            "Element lengths are physical tip-to-tip dimensions. A boom-mounting "
            "correction is not modeled; use published or measured lengths when "
            "the boom diameter and clamps matter."
        ),
        Language.SPANISH: (
            "Las longitudes son de punta a punta. No se modela una corrección de "
            "montaje sobre el boom; usá longitudes publicadas o medidas cuando el "
            "diámetro del boom y las abrazaderas importen."
        ),
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
    "component_calculator.title": {
        Language.ENGLISH: "Component calculators",
        Language.SPANISH: "Calculadoras de componentes",
    },
    "component_calculator.coil": {
        Language.ENGLISH: "Coil",
        Language.SPANISH: "Bobina",
    },
    "component_calculator.trap": {
        Language.ENGLISH: "Trap / LC",
        Language.SPANISH: "Trampa / LC",
    },
    "component_calculator.balun": {
        Language.ENGLISH: "Balun / unun",
        Language.SPANISH: "Balun / unun",
    },
    "component_calculator.conductor": {
        Language.ENGLISH: "Conductor",
        Language.SPANISH: "Conductor",
    },
    "component_calculator.choke": {
        Language.ENGLISH: "Common-mode choke",
        Language.SPANISH: "Choke de modo común",
    },
    "component_calculator.inductance": {
        Language.ENGLISH: "Inductance",
        Language.SPANISH: "Inductancia",
    },
    "component_calculator.diameter": {
        Language.ENGLISH: "Diameter",
        Language.SPANISH: "Diámetro",
    },
    "component_calculator.winding_length": {
        Language.ENGLISH: "Winding length",
        Language.SPANISH: "Longitud del bobinado",
    },
    "component_calculator.turns": {
        Language.ENGLISH: "Turns",
        Language.SPANISH: "Vueltas",
    },
    "component_calculator.frequency": {
        Language.ENGLISH: "Frequency",
        Language.SPANISH: "Frecuencia",
    },
    "component_calculator.capacitance": {
        Language.ENGLISH: "Capacitance",
        Language.SPANISH: "Capacitancia",
    },
    "component_calculator.turns_ratio": {
        Language.ENGLISH: "Turns ratio",
        Language.SPANISH: "Relación de vueltas",
    },
    "component_calculator.impedance_ratio": {
        Language.ENGLISH: "Impedance ratio",
        Language.SPANISH: "Relación de impedancias",
    },
    "component_calculator.material": {
        Language.ENGLISH: "Material",
        Language.SPANISH: "Material",
    },
    "component_calculator.copper": {
        Language.ENGLISH: "Copper",
        Language.SPANISH: "Cobre",
    },
    "component_calculator.aluminum": {
        Language.ENGLISH: "Aluminum",
        Language.SPANISH: "Aluminio",
    },
    "component_calculator.from_turns": {
        Language.ENGLISH: "Inductance from turns",
        Language.SPANISH: "Inductancia desde vueltas",
    },
    "component_calculator.for_inductance": {
        Language.ENGLISH: "Turns for inductance",
        Language.SPANISH: "Vueltas para inductancia",
    },
    "component_calculator.solve_c": {
        Language.ENGLISH: "Solve C",
        Language.SPANISH: "Resolver C",
    },
    "component_calculator.solve_l": {
        Language.ENGLISH: "Solve L",
        Language.SPANISH: "Resolver L",
    },
    "component_calculator.solve_f": {
        Language.ENGLISH: "Solve f",
        Language.SPANISH: "Resolver f",
    },
    "component_calculator.impedance_from_turns": {
        Language.ENGLISH: "Impedance from turns",
        Language.SPANISH: "Impedancia desde vueltas",
    },
    "component_calculator.turns_from_impedance": {
        Language.ENGLISH: "Turns from impedance",
        Language.SPANISH: "Vueltas desde impedancia",
    },
    "component_calculator.calculate": {
        Language.ENGLISH: "Calculate",
        Language.SPANISH: "Calcular",
    },
    "component_calculator.use": {
        Language.ENGLISH: "Use result",
        Language.SPANISH: "Usar resultado",
    },
    "component_calculator.result_coil": {
        Language.ENGLISH: "Estimated {inductance} µH for {turns} turns (Wheeler approximation).",
        Language.SPANISH: "Inductancia estimada: {inductance} µH para {turns} vueltas (aproximación de Wheeler).",
    },
    "component_calculator.result_turns": {
        Language.ENGLISH: "Estimated {turns} turns for {inductance} µH (Wheeler approximation).",
        Language.SPANISH: "Vueltas estimadas: {turns} para {inductance} µH (aproximación de Wheeler).",
    },
    "component_calculator.result_trap_c": {
        Language.ENGLISH: "Capacitance {capacitance} pF resonates at {frequency} MHz.",
        Language.SPANISH: "Una capacidad de {capacitance} pF resuena a {frequency} MHz.",
    },
    "component_calculator.result_trap_l": {
        Language.ENGLISH: "Inductance {inductance} µH resonates at {frequency} MHz.",
        Language.SPANISH: "Una inductancia de {inductance} µH resuena a {frequency} MHz.",
    },
    "component_calculator.result_trap_f": {
        Language.ENGLISH: "Resonance at {frequency} MHz · XL {xl} Ω · XC {xc} Ω.",
        Language.SPANISH: "Resonancia a {frequency} MHz · XL {xl} Ω · XC {xc} Ω.",
    },
    "component_calculator.result_balun_impedance": {
        Language.ENGLISH: "{turns}:1 turns gives a {ratio}:1 impedance ratio.",
        Language.SPANISH: "{turns}:1 vueltas dan una relación de impedancias {ratio}:1.",
    },
    "component_calculator.result_balun_turns": {
        Language.ENGLISH: "{ratio}:1 impedance needs about {turns}:1 turns.",
        Language.SPANISH: "{ratio}:1 de impedancia necesita unas {turns}:1 vueltas.",
    },
    "component_calculator.result_conductor": {
        Language.ENGLISH: "DC {dc} Ω/m · RF estimate {rf} Ω/m · skin depth {depth} µm.",
        Language.SPANISH: "CC {dc} Ω/m · estimación RF {rf} Ω/m · profundidad de piel {depth} µm.",
    },
    "component_calculator.coil_hint": {
        Language.ENGLISH: "Wheeler air-core approximation. Winding length should not be much shorter than the diameter; verify the actual coil.",
        Language.SPANISH: "Aproximación de Wheeler para núcleo de aire. El bobinado no debería ser mucho más corto que el diámetro; verificá la bobina real.",
    },
    "component_calculator.trap_hint": {
        Language.ENGLISH: "Ideal LC resonance. Trap loss, self-capacitance, and component tolerance are not included.",
        Language.SPANISH: "Resonancia LC ideal. No se incluyen pérdidas de la trampa, autocapacidad ni tolerancias de componentes.",
    },
    "component_calculator.balun_hint": {
        Language.ENGLISH: "Ideal turns/impedance relation only. Core loss, winding capacitance, power rating, and bandwidth are not modeled.",
        Language.SPANISH: "Solo la relación ideal vueltas/impedancia. No se modelan pérdidas de núcleo, capacidad de bobinado, potencia ni ancho de banda.",
    },
    "component_calculator.conductor_hint": {
        Language.ENGLISH: "DC resistance plus an approximate high-frequency skin-effect estimate. Compare materials and diameters, not exact losses.",
        Language.SPANISH: "Resistencia CC más una estimación aproximada de efecto piel. Compará materiales y diámetros, no pérdidas exactas.",
    },
    "component_calculator.choke_text": {
        Language.ENGLISH: (
            "<h3>Common-mode choke reference</h3>"
            "<p>A current balun/choke suppresses common-mode current on the outside "
            "of the coax. It is not the same as a differential impedance transformer.</p>"
            "<p>The useful quantity is the common-mode impedance <b>Zcm(f)</b>; it "
            "depends on the ferrite mix, number of turns, cable diameter, and power "
            "level. A matched insertion-loss number does not describe it.</p>"
            "<p>AntennaDesk does not model a common-mode choke. Use the manufacturer's "
            "Zcm(f) data or a measurement; do not count its resistance as differential "
            "feed-line loss.</p>"
        ),
        Language.SPANISH: (
            "<h3>Referencia de choke de modo común</h3>"
            "<p>Un balun/choke de corriente suprime la corriente de modo común por el "
            "exterior del coax. No es lo mismo que un transformador de impedancia "
            "diferencial.</p>"
            "<p>La magnitud útil es la impedancia de modo común <b>Zcm(f)</b>; depende "
            "del material de ferrita, las vueltas, el diámetro del cable y la potencia. "
            "Una pérdida de inserción adaptada no la describe.</p>"
            "<p>AntennaDesk no modela un choke de modo común. Usá datos Zcm(f) del "
            "fabricante o una medición; no cuentes su resistencia como pérdida "
            "diferencial de la línea.</p>"
        ),
    },
    "loads.title": {
        Language.ENGLISH: "Series Loads",
        Language.SPANISH: "Cargas en serie",
    },
    "loads.calculator": {
        Language.ENGLISH: "Calculator...",
        Language.SPANISH: "Calculadora...",
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
    "optimize.min_swr_edges_objective": {
        Language.ENGLISH: "Minimum SWR at band edges",
        Language.SPANISH: "SWR mínimo en bordes de banda",
    },
    "optimize.min_swr_operating_objective": {
        Language.ENGLISH: "Minimum SWR at operating frequencies",
        Language.SPANISH: "SWR mínimo en frecuencias de operación",
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
    "optimize.progress": {
        Language.ENGLISH: ("Evaluations {completed} / ~{total} (estimated) · best score {score}"),
        Language.SPANISH: (
            "Evaluaciones {completed} / ~{total} (estimadas) · mejor puntuación {score}"
        ),
    },
    "optimize.progress_evaluations": {
        Language.ENGLISH: "Evaluations {completed} / ~{total} (estimated)",
        Language.SPANISH: "Evaluaciones {completed} / ~{total} (estimadas)",
    },
    "optimize.progress_completed": {
        Language.ENGLISH: "Completed · {count} evaluations",
        Language.SPANISH: "Completado · {count} evaluaciones",
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
    "optimize.operating_frequencies": {
        Language.ENGLISH: "Operating frequencies from the current band plan: {frequencies}",
        Language.SPANISH: "Frecuencias de operación del plan de bandas actual: {frequencies}",
    },
    "optimize.robust_tolerance": {
        Language.ENGLISH: "Dimensional tolerance",
        Language.SPANISH: "Tolerancia dimensional",
    },
    "optimize.max_boom": {
        Language.ENGLISH: "Maximum boom length",
        Language.SPANISH: "Longitud máxima del boom",
    },
    "optimize.max_turning": {
        Language.ENGLISH: "Maximum turning radius",
        Language.SPANISH: "Radio de giro máximo",
    },
    "optimize.no_limit": {
        Language.ENGLISH: "no limit",
        Language.SPANISH: "sin límite",
    },
    "optimize.export_csv": {
        Language.ENGLISH: "Export CSV...",
        Language.SPANISH: "Exportar CSV...",
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
    "optimize.recommend.seed_divergence": {
        Language.ENGLISH: (
            "The seed runs found different designs or not all of them produced a "
            "feasible result. The best-scoring design was selected; review it "
            "before applying and consider a wider budget or a different objective."
        ),
        Language.SPANISH: (
            "Las ejecuciones con distintas semillas encontraron diseños diferentes "
            "o no todas produjeron un resultado factible. Se seleccionó el diseño "
            "con mejor puntuación; revísalo antes de aplicarlo y considera un "
            "presupuesto mayor u otro objetivo."
        ),
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
    "optimize.seed_runs": {
        Language.ENGLISH: "Seed runs",
        Language.SPANISH: "Ejecuciones con semilla",
    },
    "optimize.seed_runs_hint": {
        Language.ENGLISH: (
            "Run the search with consecutive seeds and compare the designs. "
            "Thorough defaults to 3; the best-scoring run is used and divergent "
            "designs are reported."
        ),
        Language.SPANISH: (
            "Ejecuta la búsqueda con semillas consecutivas y compara los diseños. "
            "Exhaustivo usa 3 por defecto; se usa la ejecución con mejor puntuación "
            "y se informan los diseños divergentes."
        ),
    },
    "optimize.workers": {
        Language.ENGLISH: "Parallel workers",
        Language.SPANISH: "Workers paralelos",
    },
    "optimize.workers_hint": {
        Language.ENGLISH: (
            "Each worker launches a separate solver process. More workers reduce "
            "wall time on independent candidates but use more CPU and memory; "
            "use 1 for large models or limited memory."
        ),
        Language.SPANISH: (
            "Cada worker lanza un proceso del solver separado. Más workers "
            "reducen el tiempo en candidatos independientes pero usan más CPU y "
            "memoria; usá 1 para modelos grandes o memoria limitada."
        ),
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
    "optimize.endfed.matching_context": {
        Language.ENGLISH: (
            "The primary matching capacitor and transformer leakage stay at "
            "their design values; they are not optimized until a measured "
            "transformer model is available."
        ),
        Language.SPANISH: (
            "El capacitor de adaptación en el primario y la fuga del "
            "transformador quedan en sus valores de diseño; no se optimizan "
            "hasta tener un modelo medido del transformador."
        ),
    },
    "optimize.matching_override": {
        Language.ENGLISH: (
            "Optimization includes the project matching network, which replaces the "
            "internal EFHW matching network. The networks are not cascaded."
        ),
        Language.SPANISH: (
            "La optimización incluye la red de adaptación del proyecto, que "
            "reemplaza la red interna del EFHW. Las redes no se conectan en cascada."
        ),
    },
    "optimize.family_summary": {
        Language.ENGLISH: "Status: {status} · Evaluations: {count} · Best score: {score}",
        Language.SPANISH: "Estado: {status} · Evaluaciones: {count} · Mejor puntuación: {score}",
    },
    "optimize.no_feasible": {
        Language.ENGLISH: "No feasible design was found within the selected bounds and constraints.",
        Language.SPANISH: "No se encontró un diseño factible dentro de los límites y restricciones elegidos.",
    },
    "optimize.seed_verification_converged": {
        Language.ENGLISH: (
            "Seed verification: {count}/{requested} runs converged (score spread "
            "{score_spread}, parameter spread {parameter_spread}%). Winning seed "
            "{seed}."
        ),
        Language.SPANISH: (
            "Verificación de semillas: {count}/{requested} ejecuciones convergieron "
            "(dispersión de puntuación {score_spread}, dispersión de parámetros "
            "{parameter_spread}%). Semilla ganadora {seed}."
        ),
    },
    "optimize.seed_verification_diverged": {
        Language.ENGLISH: (
            "Seed verification warning: {count}/{requested} runs produced a "
            "feasible result, but the designs differ (score spread {score_spread}, "
            "parameter spread {parameter_spread}%). The best-scoring result was "
            "selected. Review it before applying."
        ),
        Language.SPANISH: (
            "Advertencia de verificación de semillas: {count}/{requested} "
            "ejecuciones produjeron un resultado factible, pero los diseños "
            "difieren (dispersión de puntuación {score_spread}, dispersión de "
            "parámetros {parameter_spread}%). Se seleccionó el resultado con mejor "
            "puntuación. Revísalo antes de aplicarlo."
        ),
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
    "optimize.budget_hint_seeds": {
        Language.ENGLISH: (
            "Estimated solver runs: {count} ({seeds} seeds), including sensitivity "
            "probes. The search may extend automatically."
        ),
        Language.SPANISH: (
            "Corridas estimadas del solver: {count} ({seeds} semillas), incluyendo "
            "sondas de sensibilidad. La búsqueda puede extenderse automáticamente."
        ),
    },
    "optimize.budget_hint_sweep_seeds": {
        Language.ENGLISH: (
            "Estimated solver runs: {count} ({seeds} seeds x {points} frequencies "
            "per candidate). Bandwidth optimization is expensive; the search may "
            "extend automatically."
        ),
        Language.SPANISH: (
            "Corridas estimadas del solver: {count} ({seeds} semillas x {points} "
            "frecuencias por candidato). La optimización por ancho de banda es "
            "costosa; la búsqueda puede extenderse automáticamente."
        ),
    },
    "optimize.budget_hint_quality_seeds": {
        Language.ENGLISH: (
            "Estimated solver runs: {count} ({seeds} seeds x {points} frequencies "
            "x {scenarios} scenario(s) per candidate). Seed verification multiplies "
            "the cost; the search may extend automatically."
        ),
        Language.SPANISH: (
            "Corridas estimadas del solver: {count} ({seeds} semillas x {points} "
            "frecuencias x {scenarios} escenario(s) por candidato). La verificación "
            "de semillas multiplica el costo; la búsqueda puede extenderse "
            "automáticamente."
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
    "optimize.constraint.reflector_spacing": {
        Language.ENGLISH: "The reflector spacing is too small for the wire diameter.",
        Language.SPANISH: "La separación del reflector es demasiado pequeña para el diámetro del hilo.",
    },
    "loaded_dipole.constraint.offset": {
        Language.ENGLISH: "The link offset must not exceed half the total length.",
        Language.SPANISH: "El offset del enlace no debe superar la mitad de la longitud total.",
    },
    "optimize.constraint.boom_length": {
        Language.ENGLISH: "The boom exceeds the maximum length.",
        Language.SPANISH: "El boom supera la longitud máxima.",
    },
    "optimize.constraint.turning_radius": {
        Language.ENGLISH: "The turning radius exceeds the maximum.",
        Language.SPANISH: "El radio de giro supera el máximo.",
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
    "optimize.constraint.endfed_coil_offset": {
        Language.ENGLISH: "The loading-coil position must be shorter than the wire.",
        Language.SPANISH: "La posición de la bobina de carga debe ser menor que el hilo.",
    },
    "optimize.constraint.endfed_bend_length": {
        Language.ENGLISH: "The bend height must be shorter than the end-fed wire.",
        Language.SPANISH: "La altura del codo debe ser menor que el hilo alimentado en el extremo.",
    },
    "optimize.constraint.endfed_bend_feed_section": {
        Language.ENGLISH: "The bend must not fall inside the fixed feed section.",
        Language.SPANISH: "El codo no puede quedar dentro del tramo de alimentación fijo.",
    },
    "optimize.constraint.endfed_bend_coil": {
        Language.ENGLISH: "The bend must not fall inside the loading-coil section.",
        Language.SPANISH: "El codo no puede quedar dentro del tramo de la bobina de carga.",
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
    "optimize.constraint.director_length_taper": {
        Language.ENGLISH: (
            "Director lengths must preserve the starting taper; a director cannot "
            "become longer than the previous one beyond the initial shape tolerance."
        ),
        Language.SPANISH: (
            "Las longitudes de los directores deben preservar el taper inicial; un "
            "director no puede volverse más largo que el anterior más allá de la "
            "tolerancia de forma inicial."
        ),
    },
    "optimize.constraint.director_gap_taper": {
        Language.ENGLISH: (
            "Director gaps must preserve the starting spacing trend; adjacent gaps "
            "cannot reverse the initial taper."
        ),
        Language.SPANISH: (
            "Las separaciones entre directores deben preservar la tendencia inicial; "
            "gaps adyacentes no pueden invertir el taper inicial."
        ),
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
    "diagnostic.geometry.wire_too_short": {
        Language.ENGLISH: "Wire {wire} is shorter than 1 cm.",
        Language.SPANISH: "El hilo {wire} mide menos de 1 cm.",
    },
    "diagnostic.geometry.wire_overlap": {
        Language.ENGLISH: (
            "Wires {first} and {second} overlap. Separate or merge them before construction."
        ),
        Language.SPANISH: (
            "Los hilos {first} y {second} se superponen. Sepalos o unificalos antes de construir."
        ),
    },
    "diagnostic.geometry.wire_crossing": {
        Language.ENGLISH: (
            "Wires {first} and {second} cross without a shared connection. "
            "Add an insulator or reroute them."
        ),
        Language.SPANISH: (
            "Los hilos {first} y {second} se cruzan sin una conexión compartida. "
            "Agregá un aislador o cambiales el recorrido."
        ),
    },
    "diagnostic.geometry.free_space": {
        Language.ENGLISH: (
            "The model uses free space. Confirm that this matches the installed antenna."
        ),
        Language.SPANISH: (
            "El modelo usa espacio libre. Confirmá que coincida con la antena instalada."
        ),
    },
    "diagnostic.supports.no_profile": {
        Language.ENGLISH: (
            "No active installation profile: height, width, and support type are unchecked."
        ),
        Language.SPANISH: (
            "No hay un perfil de instalación activo: no se verificaron altura, ancho ni soporte."
        ),
    },
    "diagnostic.supports.height_unknown": {
        Language.ENGLISH: "The profile has no available height; confirm the {top} m top height fits.",
        Language.SPANISH: (
            "El perfil no tiene altura disponible; confirmá que entren los {top} m de altura."
        ),
    },
    "diagnostic.supports.height_exceeded": {
        Language.ENGLISH: (
            "The design top height {top} m exceeds the profile's available height {available} m."
        ),
        Language.SPANISH: (
            "La altura superior del diseño ({top} m) supera la altura disponible del perfil "
            "({available} m)."
        ),
    },
    "diagnostic.supports.width_unknown": {
        Language.ENGLISH: "The profile has no available width; confirm the {span} m span fits.",
        Language.SPANISH: (
            "El perfil no tiene ancho disponible; confirmá que entren los {span} m de extensión."
        ),
    },
    "diagnostic.supports.width_exceeded": {
        Language.ENGLISH: (
            "The design horizontal span {span} m exceeds the profile's available width "
            "{available} m."
        ),
        Language.SPANISH: (
            "La extensión horizontal del diseño ({span} m) supera el ancho disponible del "
            "perfil ({available} m)."
        ),
    },
    "diagnostic.supports.ground_mismatch": {
        Language.ENGLISH: (
            "The model ground differs from the installation profile's recommended ground."
        ),
        Language.SPANISH: (
            "El suelo del modelo difiere del suelo recomendado por el perfil de instalación."
        ),
    },
    "diagnostic.construction.record_missing": {
        Language.ENGLISH: "No as-built record or checklist has been started.",
        Language.SPANISH: "No se inició un registro as-built ni una lista de control.",
    },
    "diagnostic.construction.dimensions_missing": {
        Language.ENGLISH: "The as-built record has no measured dimensions yet.",
        Language.SPANISH: "El registro as-built todavía no tiene dimensiones medidas.",
    },
    "diagnostic.construction.checklist_incomplete": {
        Language.ENGLISH: "The construction checklist is incomplete ({checked} of {total}).",
        Language.SPANISH: "La lista de control de construcción está incompleta ({checked} de {total}).",
    },
    "diagnostic.simulation.missing": {
        Language.ENGLISH: "No simulation result is stored; electrical performance is unverified.",
        Language.SPANISH: "No hay un resultado de simulación guardado; el desempeño eléctrico no está verificado.",
    },
    "diagnostic.simulation.failed": {
        Language.ENGLISH: "The latest simulation finished with an error.",
        Language.SPANISH: "La última simulación terminó con un error.",
    },
    "diagnostic.simulation.cancelled": {
        Language.ENGLISH: "The latest simulation was cancelled.",
        Language.SPANISH: "La última simulación se canceló.",
    },
    "diagnostic.simulation.partial": {
        Language.ENGLISH: "The latest simulation finished only partially.",
        Language.SPANISH: "La última simulación terminó solo parcialmente.",
    },
    "diagnostic.simulation.stale": {
        Language.ENGLISH: "The latest simulation used a different antenna model.",
        Language.SPANISH: "La última simulación usó un modelo de antena diferente.",
    },
    "diagnostic.segmentation.invalid": {
        Language.ENGLISH: "Segmentation could not be evaluated for this model.",
        Language.SPANISH: "No se pudo evaluar la segmentación de este modelo.",
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
    "diagnostic.antenna.load.duplicate_id": {
        Language.ENGLISH: "Two loads use the same identifier.",
        Language.SPANISH: "Dos cargas usan el mismo identificador.",
    },
    "diagnostic.antenna.load.out_of_range": {
        Language.ENGLISH: "A load position is outside its wire.",
        Language.SPANISH: "La posición de una carga está fuera de su hilo.",
    },
    "diagnostic.antenna.load.unknown_wire": {
        Language.ENGLISH: "A load references an unknown wire.",
        Language.SPANISH: "Una carga referencia un hilo inexistente.",
    },
    "diagnostic.antenna.source.duplicate": {
        Language.ENGLISH: "Two sources use the same wire point.",
        Language.SPANISH: "Dos fuentes usan el mismo punto del hilo.",
    },
    "diagnostic.antenna.source.out_of_range": {
        Language.ENGLISH: "A source position is outside its wire.",
        Language.SPANISH: "La posición de una fuente está fuera de su hilo.",
    },
    "diagnostic.antenna.source.unknown_wire": {
        Language.ENGLISH: "A source references an unknown wire.",
        Language.SPANISH: "Una fuente referencia un hilo inexistente.",
    },
    "diagnostic.antenna.transmission_line.duplicate_id": {
        Language.ENGLISH: "Two transmission lines use the same identifier.",
        Language.SPANISH: "Dos líneas de transmisión usan el mismo identificador.",
    },
    "diagnostic.antenna.transmission_line.out_of_range": {
        Language.ENGLISH: "A transmission-line endpoint is outside its wire.",
        Language.SPANISH: "Un extremo de la línea de transmisión está fuera de su hilo.",
    },
    "diagnostic.antenna.transmission_line.unknown_wire": {
        Language.ENGLISH: "A transmission line references an unknown wire.",
        Language.SPANISH: "Una línea de transmisión referencia un hilo inexistente.",
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
    "diagnostic.normalization.pattern_missing": {
        Language.ENGLISH: (
            "One or more far-field snapshots were missing and were interpolated or omitted."
        ),
        Language.SPANISH: (
            "Faltaban una o más instantáneas de campo lejano y se interpolaron u omitieron."
        ),
    },
    "diagnostic.normalization.source_absorbs_power": {
        Language.ENGLISH: (
            "One or more ideal sources absorb power; the primary feed remains "
            "the impedance/SWR reference."
        ),
        Language.SPANISH: (
            "Una o más fuentes ideales absorben potencia; la alimentación "
            "principal sigue siendo la referencia de impedancia/ROE."
        ),
    },
    "diagnostic.matching_network.applied": {
        Language.ENGLISH: ("Impedance, SWR, and realized gain include the matching network."),
        Language.SPANISH: (
            "La impedancia, la ROE y la ganancia realizada incluyen la red de adaptación."
        ),
    },
    "diagnostic.matching_network.override": {
        Language.ENGLISH: (
            "The project matching network replaces the internal EFHW matching "
            "network; the two networks are not cascaded."
        ),
        Language.SPANISH: (
            "La red de adaptación del proyecto reemplaza la red interna del EFHW; "
            "las dos redes no se conectan en cascada."
        ),
    },
    "diagnostic.transformer.applied": {
        Language.ENGLISH: ("Impedance, SWR, and realized gain include the ideal feed transformer."),
        Language.SPANISH: (
            "La impedancia, la ROE y la ganancia realizada incluyen el "
            "transformador de alimentación ideal."
        ),
    },
    "diagnostic.balun_loss.applied": {
        Language.ENGLISH: (
            "Impedance and SWR exclude the matched balun/unun loss; realized gain includes it."
        ),
        Language.SPANISH: (
            "La impedancia y la ROE excluyen la pérdida adaptada del balun/unun; "
            "la ganancia realizada la incluye."
        ),
    },
    "diagnostic.feed_line.applied": {
        Language.ENGLISH: ("Impedance, SWR, and realized gain include the feed line."),
        Language.SPANISH: (
            "La impedancia, la ROE y la ganancia realizada incluyen la línea de alimentación."
        ),
    },
    "diagnostic.band.cancelled": {
        Language.ENGLISH: "Band analysis cancelled before this band ran.",
        Language.SPANISH: "El análisis por banda se canceló antes de ejecutar esta banda.",
    },
    "diagnostic.band.error": {
        Language.ENGLISH: "A band analysis failed.",
        Language.SPANISH: "Falló un análisis por banda.",
    },
    "diagnostic.custom.wire.short": {
        Language.ENGLISH: "A wire is shorter than 1 cm.",
        Language.SPANISH: "Un hilo mide menos de 1 cm.",
    },
    "diagnostic.custom.wires.cross": {
        Language.ENGLISH: "Two wires cross.",
        Language.SPANISH: "Dos hilos se cruzan.",
    },
    "diagnostic.custom.wires.overlap": {
        Language.ENGLISH: "Two wires overlap.",
        Language.SPANISH: "Dos hilos se superponen.",
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
    "diagnostic.project.measurement.duplicate_id": {
        Language.ENGLISH: "Two measurements use the same identifier.",
        Language.SPANISH: "Dos mediciones usan el mismo identificador.",
    },
    "diagnostic.project.measurement.unknown_session": {
        Language.ENGLISH: "A measurement references an unknown session.",
        Language.SPANISH: "Una medición referencia una sesión inexistente.",
    },
    "diagnostic.project.measurement_session.duplicate_id": {
        Language.ENGLISH: "Two measurement sessions use the same identifier.",
        Language.SPANISH: "Dos sesiones de medición usan el mismo identificador.",
    },
    "diagnostic.project.measurement_session.unknown_design": {
        Language.ENGLISH: "A measurement session references an unknown design.",
        Language.SPANISH: "Una sesión de medición referencia un diseño inexistente.",
    },
    "diagnostic.project.design.duplicate_id": {
        Language.ENGLISH: "Two designs use the same identifier.",
        Language.SPANISH: "Dos diseños usan el mismo identificador.",
    },
    "diagnostic.project.design.duplicate_name": {
        Language.ENGLISH: "Two designs use the same name.",
        Language.SPANISH: "Dos diseños usan el mismo nombre.",
    },
    "diagnostic.project.installation_profile.duplicate_id": {
        Language.ENGLISH: "Two installation profiles use the same identifier.",
        Language.SPANISH: "Dos perfiles de instalación usan el mismo identificador.",
    },
    "diagnostic.project.installation_profile.duplicate_name": {
        Language.ENGLISH: "Two installation profiles use the same name.",
        Language.SPANISH: "Dos perfiles de instalación usan el mismo nombre.",
    },
    "diagnostic.project.installation_profile.unknown_active": {
        Language.ENGLISH: "The active installation profile does not exist.",
        Language.SPANISH: "El perfil de instalación activo no existe.",
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

    def optional(self, key: str) -> str | None:
        """Return the translated text for ``key``, or ``None`` when absent.

        Unlike :meth:`t`, this never returns the raw key. It is used by
        optional UI help, where a missing translation must leave the widget
        without a tooltip instead of showing an internal identifier.
        """

        return _TRANSLATIONS.get(key, {}).get(self._language)

    def report(self, text: str, /, **values: object) -> str:
        """Translate an English report label, template, or value.

        Reporting modules stay Qt-free and English-first.  They call this
        callback only when the UI asks for another language.  Unknown strings
        fall back to the English source, and named placeholders are formatted
        after translation so each language can reorder them.
        """

        if self._language is Language.SPANISH and text.startswith("diagnostic."):
            diagnostic = _TRANSLATIONS.get(text, {}).get(self._language)
            if diagnostic is not None:
                return diagnostic.format(**values) if values else diagnostic
        if self._language is Language.SPANISH and text.startswith("evidence."):
            parts = text.split(".", 2)
            if len(parts) == 3:
                translated = EVIDENCE_SPANISH.get(parts[1], {}).get(parts[2])
                if translated is not None:
                    return translated.format(**values) if values else translated
        template = text if self._language is Language.ENGLISH else REPORT_SPANISH.get(text, text)
        return template.format(**values) if values else template
