# User guide

## Before you start

The Linux AppImage, Debian package, and Windows zip include `nec2c` and their
own Python runtime. The instructions below build and run from source.

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
height, wire diameter, material, ground, reference impedance, and the frequency
sweep. A single action bar above the panel has **Apply design**, **Estimate
Dimensions...**, and **Optimize...**. The compact **Simulation pattern** group
sets the global pattern resolution and pattern frequency count for every
antenna family.

For a frequency-first start, press **Estimate Dimensions...** above the design
panel, choose the family and target frequency, and apply the estimate. The form
then shows the resulting dimensions for review.

Choose the antenna type in the form:

- **Wire dipole**: one straight wire; choose horizontal or vertical. For a
  vertical dipole the height is the base height and the azimuth is disabled.
- **Folded dipole**: two parallel elements and two end connectors; set the
  element length and spacing.
- **Loop**: a vertical regular polygon; set the circumference, the number of
  sides, and the bottom height above ground.

Changing the type converts the current design when you press **Apply design**
or **Simulate**. The center shows a dimensioned sketch with a ground line and
scale bar. The sketch draws the actual wire model, so loops keep their polygon
shape and arrays keep every element. Use the **View** selector to switch
between:

- **Elevation / front**: the view that shows the construction shape for a
  vertical-plane antenna. A quad or delta loop appears as its real square or
  triangle, a Slim Jim shows its folded rectangle and gap detail, and an
  end-fed wire keeps its slope. It also shows height above ground, feed
  height, ground line, and scale. For a horizontal array whose elements
  overlap in front view, the header tells you to use Plan.
- **Plan / top**: the true top view. For a vertical loop this is edge-on, which
  is expected; use Elevation to see its polygon. For horizontal arrays such as
  a Yagi or Moxon it shows the element layout, boom spacing, and element
  lengths. For a ring or radial vertical, a top inset shows the horizontal
  structure while the main view keeps the installation height.
- **3D**: isometric wireframe colored by gain (green low, yellow intermediate, red high), with a dBi legend, ground grid, feed marker, axes, and scale.

The default view is selected from the geometry: vertical-plane antennas use
elevation, horizontal planar arrays use plan, and non-planar antennas show a
front view with a top inset. Press **Apply design** or **Simulate** and the
view resets to fit the new model; changing antennas also resets zoom, pan, and
vertical exaggeration. Dimensions are placed around the geometry with
collision avoidance. Very small features such as the Slim Jim gap use a detail
inset marked *not to scale*. The **Zoom** selector scales the sketch (0.5x, 1x,
2x, 4x, 8x); the mouse wheel steps through those values, dragging pans, and
double-click resets zoom and pan. The **Vertical scale** selector can
exaggerate the height (1x, 1.5x, 2x, 3x) for low horizontal antennas.

## Undo and redo

Use **Edit → Undo** and **Edit → Redo**, or the standard Ctrl+Z / Ctrl+Shift+Z
shortcuts, to move through applied project changes: design edits, template
changes, variants, loads, feed line, matching network, measurements, and design
estimates. Undo/Redo does not remove completed simulation runs or compact the
solver history. If a form has unapplied changes, AntennaDesk asks before
discarding them for a project-level undo. Text editors keep their own Ctrl+Z
while they have focus.

## Design from frequency

Use the **Estimate Dimensions...** button above the design panel or
**Design → Estimate Dimensions...** to estimate initial dimensions from a
frequency and an antenna family. The dialog supports wire and folded dipoles,
loops (generic, quad, delta), verticals in 1/4λ, 1/2λ, and 5/8λ, inverted-V,
fan dipoles, end-fed wires, OCFD, J Pole, Slim Jim, Ringo, Yagi, and Moxon.

The result is a **starting point**, not a verified construction measurement.
The dialog shows assumptions, warnings, confidence, and dimension values. Apply
the estimate to the current design, then use **Optimize...** to refine it with
NEC. The checkbox **Open an optimizer or synthesis dialog after applying**
does this in one step when a solver is configured. For Yagi, the frequency
estimator supports 2 to 32 elements from the DL6WU trimming reference; the
NBS five-element preset remains available in the Yagi editor.

## Analyze multiple bands

Use **Simulation → Analyze Bands...** or the central **Band analysis** group to
run the current design over several amateur bands. The dialog starts from the
family default and lets you select any catalog band from 160 m to 23 cm, with a sweep
point count for each band.

Band ranges are generic IARU ranges; local allocations differ and the user is
responsible for operating within them. Family defaults are starting points, not
resonance guarantees:

- **G5RV**: 80/40/20/15/10 m; WARC bands are available for manual selection.
- **OCFD**: harmonically related bands, for example 40/20/10 m for a 40 m
  design and 80/40/20/10 m for an 80 m design.
- **End-fed**: the design band and its documented harmonics; **random wire**
  defaults to 80-10 m and requires an external tuner.
- **Sloper**: a conservative end-fed subset.
- **Fan dipole**: one band per element length.
- **Trap dipole**: the low and high design frequencies.
- **T2FD**: the broadband HF range.
- **Doublet**: 80-10 m when the project uses a high-impedance/open-wire feed
  line; otherwise select bands manually.

The analysis runs the solver once per band and builds a **Bands** results tab.
Each row shows the best SWR, its frequency, the sampled power gain, takeoff
angle, efficiency, and status. Selecting a row reuses the existing impedance,
pattern, currents, diagnostics, and raw-data views for that band. Completed
bands are kept if another band fails or the analysis is cancelled.

The global **Simulation pattern** group controls the angular resolution.
Band analysis uses one representative pattern snapshot per band by default, so
a band list does not multiply the pattern data. CSV, HTML, and PDF exports
include a band column or summary when a band analysis is active. The G5RV custom
panel still offers its continuous 3.5-30 MHz sweep as a separate mode.

Defaults are evidence-labelled in the dialog. Transformer, tuner, counterpoise,
ground, and installation effects are not modeled as ideal guarantees; verify
the selected bands with a simulation and, when possible, a measurement.

## Create an antenna

Use **File → New Antenna...** to open the antenna catalog. Search or filter by
**Antenna Type** and choose the desired generator. The catalog is grouped by
antenna family: Dipole, Yagi, Loop, Vertical, and Custom. The Dipole family
contains the straight dipole, folded dipole, trap dipole, T2FD, end-fed wire,
sloper, random wire, doublet, inverted-V, off-center-fed dipole, and fan dipole.
The Yagi family includes the parametric Yagi and the Moxon rectangle. The Loop
family includes the generic loop plus delta-loop and quad-loop presets. The
Vertical family includes the generic vertical radiator and the loaded vertical
/ mobile whip preset. The catalog shows a short description and evidence level
for each type.

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
template; use **Design → Change Template...** (or Ctrl+Shift+T) to open the
catalog and replace the current design with another template.

A full-wave loop normally presents roughly 100-150 Ω at resonance, so a direct
50 Ω target may be unreachable by changing only its circumference. Use a 2:1
balun or the Matching Network dialog for a 50 Ω system. The loop optimizer
keeps the selected loop shape and side count fixed and starts its target
resistance at 100 Ω; change it to 50 Ω only if you are not using a balun. The
suggested circumference includes a polygon correction calibrated for the
AntennaDesk loop model; it is still a starting point, so verify it with a
simulation.

## Create a trap dipole

Choose **File → New Antenna... → Trap dipole** to generate a center-fed dipole
with one parallel LC trap on each side. Set the low-band and high-band
frequencies, the center-section length, the outer-section length, the trap
frequency, the trap inductance, the wire height, orientation, azimuth, radius,
material, and ground. The trap capacitance is calculated from the trap
frequency and inductance.

**Set starting dimensions from bands** uses the half-wave factor for the
high band as the center section and the half-wave factor for the low band as
the total length. The traps load the outer sections on the low band, so the
real total length is usually shorter; tune it with the solver. The trap
frequency should normally be at or above the high band; the editor warns when
it is below. The template is experimental: the geometry and parallel LC traps
are tested, but there is no independent numerical reference for this
configuration. The loads editor protects the two trap loads; edit them through
the trap-dipole fields.

## Create a T2FD

Choose **File → New Antenna... → T2FD** for a terminated folded dipole. Set the
lowest and highest design frequencies, the element length, the conductor
spacing, the termination resistance, the feed transformer ratio, the height,
orientation, azimuth, radius, material, and ground.

**Set starting dimensions from frequency** applies Cebik's wide-long rule:
about `300/F(MHz)` feet of span and `10/F(MHz)` feet of conductor spacing at the
lowest design frequency. The default 3.5-30 MHz design starts with an 800 Ω
non-inductive resistor and a 16:1 transformer, following the commercial
B&W AC3-30 design. A 390-480 Ω resistor with a 4:1 transformer to 75 Ω is the
other common arrangement; both fields are editable.

The termination is modeled as a series load at the midpoint of the non-driven
conductor. The transformer is an ideal post-processing two-port: it scales the
antenna impedance for the transmitter-side SWR and realized gain, but it is not
part of the NEC geometry. The resistor dissipates a large part of the applied
power, especially near the lowest frequency; check the efficiency and realized
gain, not only the SWR. The model supports flat horizontal and vertical
installations. It does not model a tilted installation, balun loss, resistor
temperature rise, or a feed line as part of the antenna.

The design panel starts with a 31-point sweep from the lowest to the highest
design frequency. The pattern is computed at amateur-band snapshots with the
finest resolution that fits the project storage budget; the effective value is
reported after a run. The T2FD span and spacing are construction starting
points, not verified cut lengths.

## Create a Yagi

Choose **File → New Antenna... → Yagi** to generate a Yagi as a first-class
template. The table contains each element's boom position, total length, and
radius. Add or remove elements, edit the values, and select the driven element.
**Load NBS 5-element preset** fills the NBS TN-688 0.8λ starting geometry
scaled to the selected frequency. Changing the frequency in the form rescales
the current element positions and lengths by the wavelength ratio. If the
element dimensions do not look consistent with the current frequency, the form
shows a warning; use **Design → Estimate Dimensions...** to rebuild a
2–32 element DL6WU starting design.

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
dialog reports the remaining tip gap. Use **Load 20 m wire reference preset**
to load the published Cebik 20 m dimensions; that preset is reference-backed
for impedance, gain, and front-to-back ratio. Any edited geometry is
experimental and has no external reference.

## Create an inverted-V

Choose **File → New Antenna... → Inverted-V** to generate a first-class
two-leg inverted-V. Set the apex height, leg length, included angle,
azimuth, wire radius, material, and ground. The dialog shows the resulting
horizontal span and end height. The default ground is finite ground; choose
**Free space** only if you deliberately want a free-space model. The feed is at
the apex.

If the requested apex height would put the leg ends below ground, the
frequency-first estimator widens the included angle (and raises the apex if
needed) and reports a warning. Manual entries must keep the ends above ground;
the form rejects a geometry that would cross the ground plane. This is an
experimental generator: its geometry and frequency scaling are tested, but it
has no independent numerical reference for gain or impedance.
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

Choose **File → New Antenna... → End-fed wire** to generate a wire fed at one
end, optionally sloping between feed and far-end heights. Set the physical wire
length, feed height, end height, azimuth, radius, material, and ground; the
horizontal run is derived from the height difference. Enable
**Use counterpoise** to model it as a drop from the feed plus a horizontal
wire; disable it to remove
the counterpoise while keeping its last values for later. The transformer
ratio is an ideal feed-point transformation: `49` means a 49:1 unun, so the
antenna-side impedance is divided by 49 for the reported impedance and SWR.
If the requested end height is outside the wire's vertical reach, the
frequency-first estimator clamps it to the nearest reachable height and reports
a warning. End-fed is a first-class experimental template with an inline
editor.

## Create a sloper

Choose **File → New Antenna... → Sloper** for an end-fed half-wave wire sloping
from a high feed point to a lower far end. The preset starts with a 10 m feed
height, a 49:1 transformer, and a 0.05λ counterpoise. The end height is chosen
so the height difference fits inside the wire length. These are application
starting points; tune the length, slope, transformer, and counterpoise with the
solver. The design is an `EndFedParameters` design with the `sloper` preset, so
the inline end-fed editor remains available and the reports label it as a
sloper.

## Create a random wire

Choose **File → New Antenna... → Random wire** for a non-resonant end-fed wire
with a 9:1 transformer and a 0.05λ counterpoise. The preset starts with a 17 m
wire at 10 m height. The length is intentionally non-resonant and is an
application starting point; tune it for the bands and the matching you use.
The design is an `EndFedParameters` design with the `random_wire` preset.

## Create a G5RV

Choose **File → New Antenna... → G5RV** for the published 102 ft dipole with a
symmetric matching line. The preset uses a 31.1 m dipole and either:

- 300 Ω, 8.84 m (29 ft), or
- 450 Ω, 10.36 m (34 ft).

The dipole height, feed height, azimuth, radius, material, and ground are
editable. The matching line is modeled as a lossless geometry transmission line
between the dipole center and a short source wire. Set the line velocity factor
for your actual ladder line; the default `1.0` treats the published length as
the electrical length. The transmitter coax is not part of the antenna model;
add it with **Simulation → Feed Line...** if you want its loss and impedance
transformation.

The preset is multiband: the custom design panel starts with a **41-point
3.5–30 MHz sweep** so you can inspect the G5RV bands. The pattern resolution is
**Auto (max)** by default: AntennaDesk estimates the saved project size and
uses the finest pattern step that fits. The 41-point default uses a 1° pattern
at nine band snapshot frequencies. If even the coarsest pattern would be too
large,
it disables the far-field pattern and leaves the impedance/SWR sweep intact.
The panel shows the requested and effective resolution after a run.

The published dimensions are reference-backed (Carr, *Practical Antenna
Handbook*, via the Wikipedia G5RV article); the lossless TL model and the
installation are simplified. Tune the line length, velocity factor, and feed
line for your installation.

## Create a doublet

Choose **File → New Antenna... → Doublet** for a center-fed dipole intended for
open-wire feed line and a tuner. Set the dipole length, height, orientation,
azimuth, radius, material, and ground, plus the feed-line characteristic
impedance, length, velocity factor, and loss. The preset starts with a half-wave
dipole and a 450 Ω, 10 m line. The feed line is project-level, so later changes
are made in **Design → Feed Line**. The line is post-processed at the feedpoint
and transforms the impedance seen at the transmitter; a tuner is not modeled as
a matching network. The antenna itself is a normal `DipoleParameters` design,
so the inline dipole editor remains available.

## Create a fan dipole

Choose **File → New Antenna... → Fan dipole** to generate multiple center-fed
dipole pairs sharing a common apex feed. Each row sets the element length and
included angle; add or remove pairs as needed. Set the apex height, azimuth,
radius, material, and ground. Elements must use different included angles: two elements with the same angle
would overlap, so the model rejects them. The form defaults to 120°/90° and its
**Add element** button chooses a narrower angle that is not already in use. The
frequency-first estimator fans the elements at progressively narrower angles and
raises the apex if needed to keep all ends above ground. The fan dipole is a
first-class experimental template with an inline editor. The design frequency
is the lowest element band. When the elements map to distinct amateur bands,
**Simulate** automatically runs a band analysis over all of them and opens the
**Bands** tab.

Estimated element lengths are straight half-wave starting points. The V angle
and the coupling between elements shift the actual resonance, especially on the
highest band. Use the Bands tab to tune each element with all bands visible;
changing a short element while looking only at the lowest band will show almost
no effect.

## Create an off-center-fed dipole

Choose **File → New Antenna... → Off-center-fed dipole** to generate a single
horizontal wire with an offset feed. Set the total length, feed offset as a
percentage of the wire, height, azimuth, radius, material, ground, and
transformer ratio. The dialog shows the resulting feed distance. New designs
start with an ideal **4:1** transformer, the common OCFD balun; set **1.0** to
see the raw antenna impedance. The transformer changes impedance, SWR, and
realized gain, not the NEC pattern. Actual balun loss and common-mode current
are not modeled. OCFD is a first-class template: after creation its parameters
stay in the left design panel and can be edited inline. The generator is
experimental.

## Create a vertical

Ground-mounted radials are modeled **1 cm above the ground plane** so NEC-2 can
evaluate them. The canonical design keeps the base height you enter; the small
clearance is applied only to the solver deck and is reported as an
informational diagnostic. Without it, `nec2c` rejects radials lying exactly on
the ground with exit code 255.

Choose **File → New Antenna... → Vertical + radials** to generate a first-class
vertical radiator with an optional radial plane. Set the radiator height, base height,
radial count, radial length, first radial angle, wire radius, material, and
ground. The base height is also the radial-plane height. The default is 0.25 m;
over finite ground keep at least this height to avoid numerical instability very
close to the soil.

The **Loading coil** group adds a series coil at a selected height above the
radiator base. The model is an ideal series inductor with optional series
resistance; enter a measured or estimated coil resistance when you need a more
realistic efficiency estimate. The coil is part of the vertical template, so
the design panel updates it when you apply the vertical fields, and the loads
list and reports show it as a series load on the radiator. Disable **Use
loading coil** to remove it.

The generator is experimental: geometry and radial topology are tested, but it
has no independent numerical performance reference. The feed is at the base of
the radiator, so the usual delta-gap warning can appear. The design panel keeps
the height, base, radial, and coil fields editable; use **Edit Custom Wires...**
for raw coordinates.

## Create a loaded vertical / mobile whip

Choose **File → New Antenna... → Loaded vertical / mobile whip** for a short
vertical with a series loading coil. The mobile preset starts with a 2.0 m
radiator, a 0.25 m base height, four 1.0 m radials, and a 10 µH coil at 1.0 m.
These are application starting points, not calculated resonance values: tune
the height, coil position, and inductance with the solver for your band and
installation.

The radial plane is a simplified counterpoise. It does not model a vehicle
body, roof, or chassis, so treat mobile performance as qualitative until you
have measurements or a more detailed model. The loaded vertical uses the same
first-class `VerticalParameters` as the generic vertical; the coil is stored as
a series load on the radiator and appears in the loads editor, reports, and
construction sheet.

## Read the results

- **Bands**: appears after a band analysis. One row per selected band with best
  SWR, frequency at best SWR, sampled power gain, takeoff angle, efficiency, and
  status. Selecting a row switches the other tabs to that band's result.
- **Impedance / SWR**: table of frequency, resistance, reactance, magnitude,
  and SWR, plus impedance and SWR charts side by side over the sweep. Resonance points
  where the reactance crosses zero are marked and listed above the table.
- **Pattern**: selectable **Azimuth** or **Elevation** cuts of NEC power gain
  for each simulated frequency. The **Cuts** tab shows a line chart and a polar
  lobe diagram; the **3D lobe** tab shows a projected wireframe of the complete
  pattern, with each line colored by gain (green low, yellow intermediate, red
  high) and a min/max dBi legend. The interior stays transparent because only
  lines are drawn. Azimuth is the default cut view; use the selectors to inspect
  another plane. The default azimuth cut is chosen at the elevation with the
  highest gain; the azimuth diagram includes a dashed line showing the antenna
  orientation. Above-ground elevation cuts are drawn as open arcs rather than
  closed lobes. The angular resolution comes from **Pattern resolution** in the
  global **Simulation pattern** group; higher resolution samples the same NEC
  solution more finely.
  While you rotate or zoom the 3D lobe, AntennaDesk draws a coarser display
  mesh; when the movement stops it redraws the full-resolution wireframe. The
  stored pattern, the cuts, and the exports keep the full resolution. The
  pattern frequency selector lists the pattern snapshot frequencies, not every
  impedance-sweep point. The 3D lobe draws a ground plane when the model has
  ground and only the
  upper-hemisphere pattern is requested. Its maximum-gain marker reports the
  gain and the takeoff angle above the ground plane; for free-space models it
  reports elevation above the horizontal plane instead. The marker is the
  highest sampled direction, so the reported angle is quantized to the selected
  pattern resolution. Drag the 3D lobe to rotate
  it, use the mouse wheel to zoom, and double-click to reset the view. Power
  gain is not realized gain; see the gain summary below.
- **Currents**: segment current magnitude for the selected frequency, with the
  feed segment marked.
- **Measurements**: imported VNA sweeps with measured and simulated SWR,
  resistance, reactance, or |Z|, plus measured/simulated resonance and their
  frequency difference.
- **Diagnostics**: solver version, status, duration, fingerprint, and warnings
  or errors.
- **Raw data**: the generated NEC input deck and the raw solver output.

### Gain, directivity, and realized gain

The Diagnostics tab summary and the reports show three different metrics:

- **Power gain (NEC)**: radiated power density relative to the power accepted by
  the antenna. It includes conductor and ground losses when those are enabled,
  but not the feed line, matching network, transformer, or transmitter
  mismatch.
- **Directivity**: power gain divided by the structure radiation efficiency. It
  describes the pattern alone and requires a power budget; if conductor losses
  are disabled, the reported directivity is only meaningful for the modeled
  lossless structure.
- **Realized gain**: power gain plus the transducer gain of the feed line,
  matching network, and ideal transformer cascade. It includes transmitter
  mismatch, line loss, network loss, and residual load mismatch.

The summary also reports the mismatch, matched feed-line, and network loss at
the frequency with the highest realized gain. These components are evaluated at
their nominal reference planes and need not add exactly to the difference
between power gain and realized gain. The pattern charts and CSV pattern export
still contain NEC power gain; the per-frequency CSV includes the new metrics.

Hover the mouse over the Impedance, SWR, Pattern, Currents, or Measurements
charts to show a cursor at the nearest data point. The floating readout shows
the frequency, resistance/reactance, SWR, gain, current, segment, or measured
and simulated values as appropriate. The cursor hides when the pointer leaves
the chart and does not change the chart auto-range.

Diagrams and charts follow the application's light or dark Qt palette. The
geometry sketch, chart backgrounds, axes, labels, and series colors update when
the palette changes.

SWR is computed with the reference impedance in the design panel (default
50 Ω). A low SWR does not prove high efficiency or a useful pattern.

The **Frequency sweep** is disabled by default. When enabled, it uses **1,000
points** by default and accepts up to 10,000. Frequency points improve the
impedance/SWR curve. **Pattern resolution** controls the angular sampling of
the radiation pattern: 30°, 20°, 15°, 10° (normal), 5° (fine, default), 2°
(very fine), or 1° (maximum).

The selected pattern resolution is a **maximum**: before a run, AntennaDesk
estimates the saved project size and may coarsen the pattern to the finest step
that fits. This prevents oversized solver output and projects that cannot be
saved. A diagnostic reports when the resolution was reduced. If even the
coarsest pattern does not fit, the far-field pattern is disabled and the
impedance/SWR sweep still runs. Custom designs also expose **Auto (max)**,
which always chooses the finest fitting step; the custom panel shows the
requested and effective resolution and the estimated project size.

For sweeps longer than five points, the pattern is computed at up to **five
evenly spaced snapshot frequencies**, always including the first and last
frequency. When the design frequency falls inside the sweep, the nearest sweep
point to it is included as well. The impedance/SWR sweep keeps every point. The pattern tab lists the
snapshot frequencies, so the 3D lobe resolution no longer degrades when you use
a dense impedance sweep. A 200-point G5RV sweep, for example, can use a 5°
pattern at five frequencies instead of a 30° pattern at every frequency.
The form shows the estimated number of pattern points. More points produce
smoother cuts and a smoother 3D lobe, but increase solver time and project
size; use high resolution for final runs rather than routine exploration.
Custom designs have their own sweep controls and default to 100 points.
Generated templates use a 31-point sweep around the design frequency to keep
large radial models responsive. Default segmentation targets 0.05 wavelength
per segment; this is a standard accuracy/performance compromise. Very large
models can still be slow, so reduce radial count/length or pattern resolution
for routine exploration.

## Import VNA measurements

Use **File → Import → VNA CSV...** to add a measured sweep. The importer accepts
frequency/R/X columns, S11 real/imaginary columns, or magnitude/phase columns.
Before importing, a details dialog asks for the measurement name, calibration,
reference plane, feed line/accessories, and optional notes. The measurement is
stored in the project and appears in the **Measurements** tab. Use the
**Plot** selector to compare measured and simulated SWR, R, X, or |Z|. The tab
also reports the measured and simulated series resonances and their frequency
difference. **Edit...** changes the measurement name, calibration, reference
plane, feed line, and notes without touching the imported points. **Delete**
removes the measurement after confirmation. Imported data is treated as
untrusted input; invalid rows are skipped with warnings.

## Feed line

Use **Simulation → Feed Line...** to configure a uniform transmission line between
the transmitter and the antenna feed. Set its characteristic impedance, length,
velocity factor, and matched loss in dB per 100 m. When enabled, the Impedance /
SWR tab reports the impedance and SWR at the **transmitter end**; the Pattern
tab still reports antenna power gain, because the line does not change the
radiation pattern. Realized gain in the results summary includes the line loss
and mismatch. A diagnostics row confirms that the line was applied.

Disable the feed line to return to antenna-terminal impedance. The feed-line
configuration is saved with the project and with each simulation run; it is
not part of the antenna geometry.

## Transmission lines as geometry

Use **Design → Transmission Lines...** to add a lossless two-port between two
points of the structure. Select the start and end wire and offsets, the
characteristic impedance, the physical length, and the velocity factor. **Use
straight-line distance** fills the length from the current endpoints. The line
is emitted as a NEC `TL` card; the adapter converts physical length to the
free-space-equivalent length using the velocity factor.

A geometry line is different from the transmitter feed line:

- it connects two points of the structure and participates in the current
  solution;
- it is mathematical, so it does not radiate;
- NEC-2 models it without loss;
- its endpoints are attached to segments, so place them near segment centers
  (the solver warns when they are not).

Geometry lines are drawn as dashed construction lines in the sketch. They are
saved in the project, appear in construction sheets and reports, and can be
edited or removed without changing the antenna wires. A project can have both
geometry lines and a transmitter feed line.


## Matching network and traps

Use **Simulation → Matching Network...** to add a lossless matching network at
the antenna feed. Choose **L**, **Pi**, or **T** topology and set the reactive
elements in µH/pF. For an L network, choose whether the shunt element is on the
transmitter side. Enter the load R/X at the design frequency and use
**Auto-design L network** to calculate one valid L section; the dialog reports
when a single section cannot match the load. Pi/T are manual designs in this
slice. Set a component Q to include loss in the input impedance (0 means
lossless). The network is evaluated before the feed line: antenna → matching
network → feed line → transmitter. Impedance and SWR include the network;
pattern and power gain remain antenna-side. Network loss is included in
realized gain and reported separately.

In the load editor, **Add parallel trap** calculates the capacitance for a
parallel LC trap from the entered inductance and resonant frequency. The trap is
stored as a normal parallel RLC load and emitted as a NEC `LD 1` load.

## Variants and comparison

Use **Design → Variants → New Variant...** to duplicate the current design,
**Rename Variant...** to change its name, and **Delete Variant** to remove it. The
variant selector in the toolbar switches between designs. Completed runs are
stored in the project; the latest run for each variant is shown when you switch
or reopen the project.

Simulate the variants you want to compare, then use **Design → Variants → Compare Variants...**. The dialog shows design and result metrics side by side, an SWR
overlay, and a gain-pattern overlay for the frequency nearest each variant's
design frequency. Missing results are reported in the dialog.

## Optimize the current design

Use **Optimize...** in the design panel or the **Design** menu. The dialog adapts
to the current template: single-dimension, multi-element, or impedance
synthesis. For single-dimension templates, choose the
objective: **target impedance** (selectable `R + jX`), **target reactance**
(0 Ω for series resonance), **minimum SWR**, **maximum SWR bandwidth**,
**maximum power gain**, **maximum efficiency**, or **balanced SWR + gain**.
Set the minimum and maximum dimension and the maximum number of solver
evaluations. For target impedance, target reactance, and minimum-SWR searches,
also set the objective tolerance. For **maximum SWR bandwidth**, set the SWR
limit and use a frequency sweep; the grid resolution is controlled by the
evaluation limit. Gain objectives require a far-field request. Efficiency uses
the solver's power budget.

**Target impedance** is the most direct option when the load matters, for
example an OCFD where 200 Ω is a reasonable starting target. The optimizer
evaluates the bounded dimension range and selects the point with the smallest
complex impedance error, then reports that error and the resulting SWR. For
target-impedance searches, SWR is relative to the target resistance, not the
50 Ω simulation reference; target reactance is treated as a reactance to be
cancelled by the matching network, while the complex impedance error still
includes it. A single dimension may not reach both R and X exactly; the error
makes the remaining mismatch visible. OCFD, end-fed wire, wire-dipole,
folded-dipole, and loop designs support this dimension search. The evaluation
table is ranked
from best to worst for the selected objective; the **Rank** column is separate
from the original evaluation number, and failed evaluations appear last.

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

## Optimize Yagi elements

For a Yagi, use **Design → Optimize...**. Select which element
lengths, boom gaps, and element count to include, choose the objective
(**target impedance**, **maximum gain**, or **maximum front-to-back ratio**),
and set the search margin and evaluation budget. Target impedance also asks for
R/X; gain and front-to-back require a far-field pattern request. The optimizer
performs a bounded coordinate search over the selected variables. The first
element stays fixed, gaps keep a fixed 0.1 m minimum, and the element order
remains valid; radii stay fixed. **Element count** adds or removes trailing
directors from the DL6WU reference scaled to the design frequency and never
removes the driven element. The count range runs from the driven element up to
32 elements; a design with more than 32 elements can only keep or remove its
current elements. Existing element lengths and gaps remain the optimized
variables; newly added directors use the reference dimensions until the design
is applied and edited. More elements generally increase gain but also boom
length and wind load; there is no boom-length constraint yet, so choose the
count range deliberately.

The evaluation table is ranked by the selected objective and shows R, X, SWR,
gain, F/B, efficiency, and the objective value. The SWR column is relative to
the target resistance shown in the dialog; it is 50 Ω unless you select target
impedance and enter a different value. **Multi-objective** combines
gain, F/B, SWR penalty, and efficiency with user weights. The table also shows a
Pareto rank (1 = non-dominated front) for the selected metrics. Select any
table row to apply that candidate; without a selection the best weighted score
is applied. **Apply element lengths** updates the Yagi
editor and starts the normal full sweep/pattern simulation. This is a numerical
starting point; verify the applied design with a full simulation and, where
possible, a measurement.

## Optimize Moxon dimensions

For a Moxon, use **Design → Optimize...**. Choose the objective
(target impedance, maximum gain, or maximum front-to-back), the dimensions to
include, the search margin, and the evaluation budget. Target impedance also
asks for R/X; gain and F/B require a far-field request. The optimizer varies the
selected width, spacing, reflector tip, and driven tip together. Some families
also expose discrete variables such as radial count, loop side count, or Ringo
ring sides; those are searched as integers.

The evaluation table is ranked by the selected objective and reports R, X, SWR,
gain, F/B, and the objective value. **Apply dimensions** updates the Moxon
editor and starts the normal full sweep. Invalid tip/spacing combinations are
rejected, so verify the applied geometry with a full simulation.

## Optimize fan dipole elements

For a fan dipole, use **Design → Optimize...**. Select the element
pairs to include, choose the **Band** (or **Custom frequency**), set R/X, the
search margin, and the evaluation budget. The band selector and target frequency
stay synchronized, and the element table shows the band associated with each
element. If only one element is selected, its band is selected automatically.
Opening the optimizer after selecting a band in the **Bands** tab starts on that
band; otherwise it starts on the lowest element band, not on a stale design
frequency.

The **Optimize** column selects which lengths are varied. Every element remains
in the antenna, so the SWR of the short element includes coupling from the
others. To evaluate an element alone, remove the other elements in the fan
editor. The optimizer performs a bounded coordinate search and reports the best
complex impedance match; segmentation is recomputed for the target frequency.
**Apply element lengths** updates the fan editor and starts the normal full
sweep; check the other bands after applying because the elements interact.

## Synthesize dimensions

For an **OCFD**, **J Pole**, or **Slim Jim**, use **Design → Optimize...**.
Set the target frequency and the desired feed-point
resistance/reactance, then choose bounds for the two search variables:

- OCFD: total wire length and feed ratio.
- J Pole: radiator height and feed-offset position.
- Slim Jim: radiator height and stub length.

The dialog evaluates a bounded grid at the target frequency and reports the
best resistance, reactance, SWR, and impedance error. The result table is
ranked by complex impedance error, so the first row is the best candidate;
failed evaluations appear last. **Apply dimensions** updates the design and
starts the normal full sweep/pattern simulation.

This is a numerical starting point, not a guarantee that the target is
physically reachable. Verify the applied design with a full sweep, check
construction tolerances, and treat the result as experimental until it has an
independent validation reference.

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
the current cut/3D pattern image, **File → Export → Geometry PNG...**,
**Geometry SVG...**, **Geometry PDF...**, or **Geometry DXF...** for the
current geometry view, **File → Export → HTML Report...** for a self-contained
HTML report, or **File → Export → PDF Report...** for a native PDF with design
parameters, configuration, solver metadata, fingerprint, diagnostics,
impedance, resonance, and charts.
Simulation runs are stored when you save the project, including raw solver
text. Project files are losslessly gzip-compressed JSON; the 32 MB limit applies
to the compressed file. Saving above 20 MB compressed shows a warning, and
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

Use **Tools → Language** for English or Español. Use **Tools → Units** for
metric (m, mm) or imperial (ft, in). The domain and project files always store
canonical meters and hertz.

## Current limitations

- Native packages include `nec2c` but are unsigned by default; verify the
  published SHA-256 checksums before installing them.
- All catalog families are implemented, but some remain experimental or
  heuristic. Folded dipoles still lack an independent impedance reference;
  loops have the ARRL quad-loop resistance check. VNA CSV import and
  measurement comparison are implemented; live instrument control is not.
- Series and parallel RLC loads are supported on one wire segment. L/Pi/T
  matching networks are post-processed at the feedpoint, and the vertical
  generator supports a radial screen. General transmission-line geometry and
  arbitrary radial screens are not modeled.
- NEC import supports a practical subset (GW, EX, FR, GE/GN, LD 0/1), not the
  full language; unsupported cards are reported. MMANA import covers basic wire
  geometry and source only; ground and loads are not imported.
- Optimization covers primary-dimension, multi-element, integer, and Pareto
  searches for generated templates. Custom/imported designs are excluded, and
  there are no boom-length or turning-radius constraints.
- Project files store normalized results and raw solver text; many long runs
  can reach the 32 MB project limit.
- The feed line is a uniform-line post-processing model. It reports impedance
  and SWR at the transmitter but does not add line loss to the pattern gain or
  realized-gain calculation.
- Far-field values are NEC power gains. Realized gain and directivity are not
  separated yet. Relative permeability is not emitted to NEC; conductor
  conductivity is.
- Multiband defaults are starting points. The doublet default is inferred from
  a high-impedance project feed line; the tuner is not modeled as an automatic
  matching network. Variant comparison shows a band summary when analyses are
  available, but the main comparison values still use the selected band result.
- Pattern resolution is angular sampling, not additional electromagnetic
  accuracy. Fine patterns and long frequency sweeps increase runtime and
  project size.
- Simulation reports and construction sheets have native PDF export; HTML
  versions remain available for browser printing.
- Known diagnostic codes are localized; the raw solver detail remains in
  English in the tooltip and raw-output tab.
- A simulation is a prediction conditioned by the model. Unmodeled buildings,
  trees, masts, feed lines, and real ground can change measured performance.
