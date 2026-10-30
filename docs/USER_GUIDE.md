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

If the engine is not found automatically, use **Tools → Locate NEC2C...** or set
the `NEC2C` environment variable.

## First simulation

The application opens with a 40 m horizontal dipole loaded. Press **Simulate**
(or F5). The design panel on the left shows antenna type, frequency, geometry,
height, wire diameter, material, ground, reference impedance, pattern
resolution, and the frequency sweep.

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

## Create an antenna

Use **File → New Antenna...** to open the antenna catalog. Search or filter by
**Antenna Type** and choose the desired generator. The catalog is grouped by
antenna family: Dipole, Yagi, Loop, Vertical, and Custom. The Dipole family
contains the straight dipole, folded dipole, end-fed wire, inverted-V,
off-center-fed dipole, and fan dipole. The Yagi family includes the parametric
Yagi and the Moxon rectangle.
The Loop family includes the generic loop plus delta-loop and quad-loop presets.
The catalog shows a short description and evidence level for each type.

### Basic templates

For a wire dipole, folded dipole, or loop, the guided wizard asks for:

1. Project name, antenna type, band, and frequency.
2. Geometry for the selected type: wire dipole length/orientation, folded
   dipole element length/spacing, or loop circumference/side count. The
   suggested length is a heuristic, not a universal final dimension.
3. Wire material and diameter.
4. Ground model. Finite ground asks for relative permittivity and conductivity.
5. A summary before creating the project.

After creation, adjust the design panel and press **Apply design** or
**Simulate**. The design panel separates **Family** from **Template**; generated
templates now have their own inline editors. The Template field shows the current
template; use **Change Template...** to open the catalog and replace the current
design with another template.

## Create a Yagi

Choose **File → New Antenna... → Yagi** to generate a Yagi as a first-class
template. The table contains each element's boom position, total length, and
radius. Add or remove elements, edit the values, and select the driven element.
**Load NBS 5-element preset** fills the NBS TN-688 0.8λ starting geometry
scaled to the selected frequency.

The NBS preset is reference-backed for gain: the published design has 9.2 dBd
gain over a half-wave dipole. A single straight driven element is generated
instead of the published folded dipole, so the feed impedance is not the
reference impedance. Once you edit positions or lengths, the result is an
experimental geometry with no external reference; simulate it and judge it on
its own modeled performance. The design panel keeps the element table editable;
use **Edit Custom Wires...** only when you want raw coordinates.

## Create a Moxon

Choose **File → New Antenna... → Moxon rectangle** to generate a two-element
Moxon with a reflector and driven element with bent tips. Set the element
width, spacing, tip lengths, height, azimuth, radius, material, and ground. The
dialog reports the remaining tip gap. Moxon is a first-class template with an
inline editor; it is experimental and has no independent numerical reference.

## Create an inverted-V

Choose **File → New Antenna... → Inverted-V** to generate a first-class
two-leg inverted-V. Set the apex height, leg length, included angle,
azimuth, wire radius, material, and ground. The dialog shows the resulting
horizontal span and end height. The default ground is finite ground; choose
**Free space** only if you deliberately want a free-space model. The feed is at
the apex.

This is an experimental generator: its geometry and frequency scaling are
tested, but it has no independent numerical reference for gain or impedance.
Simulate it and judge the modeled performance; the design panel keeps the
generator fields editable. Use **Edit Custom Wires...** for raw coordinates. The
elevation view is selected automatically so the included angle is visible; Plan
remains available.

## Create a Ringo

Choose **File → New Antenna... → Ringo** to generate a half-wave vertical with
a horizontal matching ring at its base. Set radiator height, ring diameter,
ring height, ring side count, radius, material, and ground. The ring height
must be positive when using a ground model; the default is 0.25 m. Ringo is a
first-class experimental template with an inline editor.

## Create a J Pole or Slim Jim

Choose **File → New Antenna... → J Pole** or **Slim Jim** to generate a vertical
radiator with a parallel matching stub. Set radiator height, stub length,
spacing, feed offset, base height, radius, material, and ground. The base
height must be positive when using a ground model; the default is 0.25 m to keep
the base connector out of the NEC ground plane. Slim Jim adds the top connector
and is also available by enabling **Folded** in the J Pole editor. Both are
first-class experimental templates.

## Create an end-fed wire

Choose **File → New Antenna... → End-fed wire** to generate a single wire fed
at one end, optionally sloping between feed and far-end heights. Set length,
feed height, end height, azimuth, radius, material, and ground. End-fed is a
first-class experimental template with an inline editor.

## Create a fan dipole

Choose **File → New Antenna... → Fan dipole** to generate multiple center-fed
dipole pairs sharing a common apex feed. Each row sets the element length and
included angle; add or remove pairs as needed. Set the apex height, azimuth,
radius, material, and ground. The fan dipole is a first-class experimental
template with an inline editor.

## Create an off-center-fed dipole

Choose **File → New Antenna... → Off-center-fed dipole** to generate a single
horizontal wire with an offset feed. Set the total length, feed offset as a
percentage of the wire, height, azimuth, radius, material, and ground. The
dialog shows the resulting feed distance. OCFD is a first-class template: after
creation its parameters stay in the left design panel and can be edited inline.
The generator is experimental.

## Create a vertical

Choose **File → New Antenna... → Vertical + radials** to generate a first-class
vertical radiator with an optional radial plane. Set the radiator height, base height,
radial count, radial length, first radial angle, wire radius, material, and
ground. The base height is also the radial-plane height. The default is 0.25 m;
over finite ground keep at least this height to avoid numerical instability very
close to the soil.

The generator is experimental: geometry and radial topology are tested, but it
has no independent numerical performance reference. The feed is at the base of
the radiator, so the usual delta-gap warning can appear. The design panel keeps
the height, base, and radial fields editable; use **Edit Custom Wires...** for
raw coordinates.

## Read the results

- **Impedance / SWR**: table of frequency, resistance, reactance, magnitude,
  and SWR, plus impedance and SWR charts side by side over the sweep. Resonance points
  where the reactance crosses zero are marked and listed above the table.
- **Pattern**: selectable **Azimuth** or **Elevation** cuts of NEC power gain
  for each simulated frequency. The **Cuts** tab shows a line chart and a polar
  lobe diagram; the **3D lobe** tab shows a projected wireframe of the complete
  pattern. Azimuth is the default cut view; use the selectors to inspect
  another plane. The default azimuth cut is chosen at the elevation with the
  highest gain; the azimuth diagram includes a dashed line showing the antenna
  orientation. Above-ground elevation cuts are drawn as open arcs rather than
  closed lobes. The angular resolution comes from **Pattern resolution** in the
  design panel; higher resolution samples the same NEC solution more finely.
  The 3D lobe draws a ground plane when the model has ground and only the
  upper-hemisphere pattern is requested. Drag the 3D lobe to rotate it, use the
  mouse wheel to zoom, and double-click to reset the view. Power gain is not
  realized gain.
- **Currents**: segment current magnitude for the selected frequency, with the
  feed segment marked.
- **Measurements**: imported VNA sweeps with measured SWR and a simulated SWR
  overlay for the current design.
- **Diagnostics**: solver version, status, duration, fingerprint, and warnings
  or errors.
- **Raw data**: the generated NEC input deck and the raw solver output.

Diagrams and charts follow the application's light or dark Qt palette. The
geometry sketch, chart backgrounds, axes, labels, and series colors update when
the palette changes.

SWR is computed with the reference impedance in the design panel (default
50 Ω). A low SWR does not prove high efficiency or a useful pattern.

The **Frequency sweep** is disabled by default. When enabled, it uses **1,000
points** by default and accepts up to 10,000. Frequency points improve the
impedance/SWR curve. **Pattern resolution** controls the angular sampling of
the radiation pattern: 10° (normal), 5° (fine, default), 2° (very fine), or 1°
(maximum).
The form shows the estimated number of pattern points. More points produce
smoother cuts and a smoother 3D lobe, but increase solver time and project
size; use high resolution for final runs rather than routine exploration.
Custom and generated designs have their own sweep controls in the custom panel;
they default to 100 points around the design frequency.

## Import VNA measurements

Use **File → Import → VNA CSV...** to add a measured sweep. The importer accepts
frequency/R/X columns, S11 real/imaginary columns, or magnitude/phase columns.
Before importing, a details dialog asks for the measurement name, calibration,
reference plane, feed line/accessories, and optional notes. The measurement is
stored in the project and appears in the **Measurements** tab, with measured SWR
and the current simulated SWR overlaid. Imported data is treated as untrusted
input; invalid rows are skipped with warnings.

## Feed line

Use **Simulation → Feed Line...** to configure a uniform transmission line between
the transmitter and the antenna feed. Set its characteristic impedance, length,
velocity factor, and matched loss in dB per 100 m. When enabled, the Impedance /
SWR tab reports the impedance and SWR at the **transmitter end**; the Pattern
tab still reports antenna power gain, because the line does not change the
radiation pattern. A diagnostics row confirms that the line was applied.

Disable the feed line to return to antenna-terminal impedance. The feed-line
configuration is saved with the project and with each simulation run; it is
not part of the antenna geometry.

## Variants and comparison

Use **Design → Variants → New Variant...** to duplicate the current design,
**Rename Variant...** to change its name, and **Delete Variant** to remove it. The
variant selector in the toolbar switches between designs. Completed runs are
stored in the project; the latest run for each variant is shown when you switch
or reopen the project.

Simulate the variants you want to compare, then use **Design → Variants → Compare Variants...**. The dialog shows design and result metrics side by side, an SWR
overlay, and a gain-pattern overlay for the frequency nearest each variant's
design frequency. Missing results are reported in the dialog.

## Optimize the length

Use **Optimize Dimension...** in the design panel or the **Design** menu. Choose the
objective: **target reactance** (0 Ω for series resonance), **minimum SWR**,
**maximum SWR bandwidth**, **maximum power gain**, **maximum efficiency**, or
**balanced SWR + gain**. Set the minimum and maximum dimension and the maximum
number of solver evaluations. For reactance and minimum-SWR searches, also set
the objective tolerance. For **maximum SWR bandwidth**, set the SWR limit and
use a frequency sweep; the grid resolution is controlled by the evaluation
limit. Gain objectives require a far-field request. Efficiency uses the
solver's power budget.

For **balanced SWR + gain**, set non-negative SWR and gain weights. The dialog
maximizes `gain_weight × gain_dBi − swr_weight × max(SWR − 1, 0)` at the design
frequency; this is a transparent weighted score, not a Pareto front. The
optimized dimension is the total length for a wire dipole or folded-dipole
element, and the circumference for a loop. The dialog evaluates the design at
the design frequency, shows resistance, reactance, SWR, bandwidth, gain, and
efficiency for every evaluation, and reports the best dimension. A sensitivity
table evaluates the best dimension at ±10 mm and ±25 mm so construction
tolerances are visible.

Press **Apply best dimension** to update the design; the application then runs
the full sweep/pattern simulation with the current settings. The optimizer is
bounded by the dimension range and evaluation limit. It changes only one
dimension; the SWR/gain balance is a weighted score, not a Pareto optimizer.

## Construction sheet

Use **Design → Construction Sheet...** for a printable sheet with target
frequency, type-aware dimensions, feed position, height, wire, ground,
simulated impedance/SWR, resonance, and construction notes. Dipoles show first
and second leg lengths; folded dipoles show element and connector lengths;
loops show side length, circumference, side count, and feed side.
**Save HTML...** writes the sheet and **Save PDF...** writes a native PDF.

## Export results

Use **File → Export → CSV...** for the frequency sweep table, **File → Export
→ Pattern CSV...** for the far-field grid (frequency, θ, φ, gains,
polarization, and E-field components), **File → Export → Pattern PNG...** for
the current cut/3D pattern image, **File → Export → Geometry PNG...** for the
current geometry view, **File → Export → HTML Report...** for a self-contained
HTML report, or **File → Export → PDF Report...** for a native PDF with design
parameters, configuration, solver metadata, fingerprint, diagnostics,
impedance, resonance, and charts.
Simulation runs are stored when you save the project, including raw solver
text. The project size limit is 10 MB; saving above 8 MB shows a warning, and
**Tools → Compact Simulation History...** keeps only the latest run per
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
- Series and parallel RLC loads are supported on one wire segment. General
  networks, transmission lines, and radial ground screens are not implemented.
- NEC import supports a practical subset (GW, EX, FR, GE/GN, LD 0/1), not the
  full language; unsupported cards are reported. MMANA import covers basic wire
  geometry and source only; ground and loads are not imported.
- Project files store normalized results and raw solver text; many long runs
  can reach the 10 MB project limit.
- The feed line is a uniform-line post-processing model. It reports impedance
  and SWR at the transmitter but does not add line loss to the pattern gain or
  realized-gain calculation.
- Pattern resolution is angular sampling, not additional electromagnetic
  accuracy. Fine patterns and long frequency sweeps increase runtime and
  project size.
- Simulation reports and construction sheets have native PDF export; HTML
  versions remain available for browser printing.
- Optimization is one-dimensional adjustment of the primary dimension against
  a reactance, SWR, bandwidth, gain, or efficiency objective, or a weighted
  SWR/gain score. It does not produce a Pareto front or optimize multiple
  dimensions.
- Relative permeability is not emitted to NEC; conductor conductivity is.
- Known diagnostic codes are localized; the raw solver detail remains in
  English in the tooltip and raw-output tab.
- A simulation is a prediction conditioned by the model. Unmodeled buildings,
  trees, masts, feed lines, and real ground can change measured performance.
