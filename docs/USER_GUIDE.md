# User guide

## Before you start

AntennaDesk uses the external `nec2c` engine. Build it once from the
repository:

```bash
bash spikes/phase0/scripts/build_nec2c.sh
```

On Windows, use the MSYS2/UCRT64 build script:

```bash
bash spikes/phase0/scripts/build_nec2c_windows.sh
```

Then install the Python environment and launch the GUI:

```bash
uv sync
uv run python -m antennadesk
```

If the engine is not found automatically, use **File → Locate NEC2C...** or set
the `NEC2C` environment variable.

## First simulation

The application opens with a 40 m horizontal dipole loaded. Press **Simulate**
(or F5). The design panel on the left shows antenna type, frequency, geometry,
height, wire diameter, material, ground, reference impedance, and the frequency
sweep.

Choose the antenna type first:

- **Wire dipole**: one straight wire; choose horizontal or vertical. For a
  vertical dipole the height is the base height and the azimuth is disabled.
- **Folded dipole**: two parallel elements and two end connectors; set the
  element length and spacing.
- **Loop**: a vertical regular polygon; set the circumference, the number of
  sides, and the bottom height above ground.

Changing the type converts the current design when you press **Apply design**
or **Simulate**. The center shows a dimensioned sketch with a ground line and scale bar. Use
the **View** selector to switch between:

- **Plan**: construction dimensions. For a wire dipole it shows the total
  length, both feed legs, feed position, ends, azimuth, and scale. For a
  folded dipole it shows both elements with exaggerated spacing for clarity,
  element length, spacing, and total conductor length. For a loop it shows a
  circle with diameter, circumference, side count, and feed position.
- **Elevation**: installation and position above ground. It shows the antenna
  height, feed height, ground line, and scale. A folded dipole also includes a
  small section symbol showing its two conductors and spacing. A loop is shown
  edge-on as a vertical line with its diameter; Plan shows the loop in its own
  plane as a circle with diameter, circumference, and side count. Construction
  dimensions stay in Plan.
- **3D**: isometric wireframe with ground grid, feed marker, axes, and scale.

Multi-wire designs switch to Plan automatically. A vertical dipole is a point
in Plan, so its elevation keeps the vertical construction dimensions. The
**Zoom** selector scales the sketch (0.5x, 1x, 2x, 4x, 8x); the mouse wheel
steps through those values, dragging pans, and double-click resets zoom and pan. The **Vertical scale**
selector can exaggerate the height (1x, 1.5x, 2x, 3x) for low horizontal
antennas.

## Create a dipole with the wizard

Use **File → New Antenna...**. The wizard starts with the antenna type
currently selected in the design panel. It asks for:

1. Project name, antenna type, band, and frequency.
2. Geometry for the selected type: wire dipole length/orientation, folded
   dipole element length/spacing, or loop circumference/side count. The
   suggested length is a heuristic, not a universal final dimension.
3. Wire material and diameter.
4. Ground model. Finite ground asks for relative permittivity and conductivity.
5. A summary before creating the project.

After creation, adjust the design panel and press **Apply design** or
**Simulate**.

## Read the results

- **Impedance / SWR**: table of frequency, resistance, reactance, magnitude,
  and SWR, plus charts of impedance and SWR over the sweep. Resonance points
  where the reactance crosses zero are marked and listed above the table.
- **Pattern**: elevation cut of NEC power gain for each simulated frequency.
  Power gain is not realized gain.
- **Currents**: segment current magnitude for the selected frequency, with the
  feed segment marked.
- **Diagnostics**: solver version, status, duration, fingerprint, and warnings
  or errors.
- **Raw data**: the generated NEC input deck and the raw solver output.

Diagrams and charts follow the application's light or dark Qt palette. The
geometry sketch, chart backgrounds, axes, labels, and series colors update when
the palette changes.

SWR is computed with the reference impedance in the design panel (default
50 Ω). A low SWR does not prove high efficiency or a useful pattern.

## Variants and comparison

Use **File → New Variant...** to duplicate the current design, **Rename
Variant...** to change its name, and **Delete Variant** to remove it. The
variant selector in the toolbar switches between designs. Completed runs are
stored in the project; the latest run for each variant is shown when you switch
or reopen the project.

Simulate the variants you want to compare, then use **File → Compare
Variants...**. The dialog shows design and result metrics side by side, an SWR
overlay, and a gain-pattern overlay for the frequency nearest each variant's
design frequency. Missing results are reported in the dialog.

## Optimize the length

Use **Optimize Dimension...** in the design panel or the File menu. Choose the
objective: **target reactance** (0 Ω for series resonance) or **minimum SWR**.
Set the minimum and maximum dimension, the maximum number of solver evaluations, and
the objective tolerance. For **maximum SWR bandwidth**, set the SWR limit and
use a frequency sweep; the grid resolution is controlled by the evaluation
limit. The optimized dimension is the total length for a wire dipole or
folded-dipole element, and the circumference for a loop. The dialog evaluates
the design at the design frequency, shows every evaluation, and reports the
best dimension. A sensitivity table evaluates the best dimension at ±10 mm and
±25 mm so construction tolerances are visible.

Press **Apply best dimension** to update the design; the application then runs
the full sweep/pattern simulation with the current settings. The optimizer is
bounded by the dimension range and evaluation limit; it is not a
multi-objective optimizer.

## Construction sheet

Use **File → Construction Sheet...** for a printable sheet with target
frequency, type-aware dimensions, feed position, height, wire, ground,
simulated impedance/SWR, resonance, and construction notes. Dipoles show first
and second leg lengths; folded dipoles show element and connector lengths;
loops show side length, circumference, side count, and feed side.
**Save HTML...** writes the sheet and **Save PDF...** writes a native PDF.

## Export results

Use **File → Export CSV...** for the frequency sweep table, **File → Export
HTML Report...** for a self-contained HTML report, or **File → Export PDF
Report...** for a native PDF with design parameters, configuration, solver
metadata, fingerprint, diagnostics, impedance, resonance, and charts.
Simulation runs are stored when you save the project, including raw solver
text. The project size limit is 10 MB; saving above 8 MB shows a warning, and
**File → Compact Simulation History...** keeps only the latest run per
variant.

## Cancel and errors

While a simulation runs, the interface stays responsive. Press **Cancel** to
terminate the solver. The status bar and diagnostics tab explain failures.
Invalid designs are rejected before the solver runs.

## Save and open

Use **File → Save** / **Save As...** to write a versioned `.antennadesk` JSON
project, and **File → Open Project...** to reopen it. The application prompts
before discarding unsaved changes.

## Language and units

Use the **Language** menu for English or Español. Use the **Units** menu for
metric (m, mm) or imperial (ft, in). The domain and project files always store
canonical meters and hertz.

## Current limitations

- Horizontal and vertical wire dipoles, folded dipoles, and regular-polygon
  loops are supported. Folded and loop geometry use theoretical sanity checks;
  independent impedance references and VNA CSV import are not implemented yet.
- Series RLC loads are supported on one wire segment. Networks, transmission
  lines, and radial ground screens are not implemented.
- Project files store normalized results and raw solver text; many long runs
  can reach the 10 MB project limit.
- Simulation reports and construction sheets have native PDF export; HTML
  versions remain available for browser printing.
- Optimization is one-dimensional adjustment of the primary dimension against
  a single reactance, SWR, or bandwidth objective; gain, efficiency, and
  multi-objective optimization are not implemented yet.
- Relative permeability is not emitted to NEC; conductor conductivity is.
- Known diagnostic codes are localized; the raw solver detail remains in
  English in the tooltip and raw-output tab.
- A simulation is a prediction conditioned by the model. Unmodeled buildings,
  trees, masts, feed lines, and real ground can change measured performance.
