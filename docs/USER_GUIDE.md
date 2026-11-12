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

## Help me choose an antenna

Use **File → Help me choose...** or the **Help me choose...** button on the
start page when you do not yet know which antenna family you need. The advisor
asks for:

- the bands you want to cover;
- the available height and horizontal space (or **Not specified**);
- whether the installation is permanent or portable;
- the main use: NVIS/local, regional, DX, or receive only;
- whether you have an antenna tuner;
- the maximum construction effort;
- whether you prefer an omnidirectional antenna, a directional beam, or have
  no preference;
- whether one antenna must cover all selected bands.

Press **Find antennas** to get up to three catalog families. The table shows
the typical space, minimum height, feed arrangement, build effort, and fit
level. Select a row to see the description, evidence, typical gain/takeoff/
bandwidth class, reasons, warnings, and limitations.

The advisor applies hard constraints and transparent preferences. It does not
simulate every candidate, does not call a language model, and does not produce
a single magic score. Suitability values are planning heuristics, not
validated construction dimensions. If a project has an active installation
profile, its available height, space, and portable flag prefill the form.

**Open selected design** opens the normal editor for the chosen family. Set the
final frequency there and use **Estimate Dimensions...** to refine the starting
dimensions; the advisor only chooses the family. This first slice covers HF
bands. VHF/UHF family templates remain available through the catalog.

## First simulation

The application starts with no project. The start page offers **New Antenna...**
to create a project from a template and **Open Project...** to load an existing
`.antennadesk` file. The edit toolbar and the design actions appear only after a
project is open.

Create a design from the catalog, review the generated template, and press
**Simulate** (or F5). The design panel on the left shows antenna type, frequency,
geometry, height, wire diameter, material, ground, reference impedance, and the
frequency sweep. A single action bar above the panel has **Apply design**,
**Estimate Dimensions...**, and **Optimize...**. **Apply design** saves the
current form values without simulating; **Simulate** saves them and runs the
solver. Where available, hover a field label or its control for a short
explanation of the model assumption, unit, or starting point. **Help → What's
This?** (Shift+F1) enters the same help mode for keyboard use. The tooltip is
optional and does not replace this guide. While a simulation runs, the status bar shows an indeterminate progress
bar with elapsed time and the current phase (preparing model, running NEC-2,
processing results). A multi-band analysis, including the automatic fan-dipole
path, uses a determinate counter for the selected bands. **Simulation →
Cancel** or the toolbar cancel action stops the run; the bar reports the
cancelling state until the worker stops. The collapsible **Advanced
simulation** section at the bottom of the panel contains **Solver**,
**Simulation sweep**, **Simulation pattern**, and **Band analysis**. The sweep
field shows the template's effective range and is read-only until **Custom** is
selected.

For a frequency-first start, select a template first and then press **Estimate
Dimensions...** above the design panel. The dialog refines only the template
already loaded in the editor. It preloads the current family, frequency, height,
orientation, and template-specific fields, so it cannot silently replace a
Ringo with a Wire Dipole. Apply the estimate, review the resulting dimensions,
and simulate or optimize. Templates without a frequency-first estimator show
the action disabled with an explanation; use their own starting-dimension
controls or change the template explicitly.

The current template is shown read-only in the design panel. Use **Change...**
next to it or **Design → Change Template...** (Ctrl+Shift+T) to replace it;
AntennaDesk preselects the current catalog entry and asks for confirmation.
**Apply design** and **Simulate** only save the current template's parameters;
they never switch the template.

The basic templates are:

- **Wire dipole**: one straight wire; choose horizontal or vertical. For a
  vertical dipole the height is the base height and the azimuth is disabled.
  A horizontal dipole can also set a **Wire sag**: the span is replaced by a
  sampled parabolic path, the feed moves to the center segment, and the report
  adds the sag and conductor length. Sag is a geometry setting and is not
  optimized.
- **Folded dipole**: two parallel elements and two end connectors; set the
  element length and spacing.
- **Loop**: a regular polygon in a vertical or horizontal plane; set the
  circumference, the number of sides, the orientation, and the height above
  ground. A horizontal loop is the sky-loop configuration.

Changing the template converts the current design only after the explicit
confirmation. The center shows a dimensioned sketch with a ground line and
scale bar. The sketch draws the actual wire model, so loops keep their polygon
shape and arrays keep every element. Use the **View** selector to switch
between:

- **Construction**: the single dimensioned construction view. The application
  chooses the projection that shows the principal plane instead of asking you
  to pick an arbitrary projection:
  - vertical-plane antennas (J-Pole, Slim Jim, vertical loops, vertical
    Yagi/Moxon, half-square, bobtail, biquad, Ringo) use the front elevation;
  - horizontal planar antennas and beams (Yagi, Moxon, hexbeam, trapped Yagi,
    T2FD, folded dipole, horizontal loop) use the top view;
  - a cubical quad uses the top boom layout;
  - non-planar antennas (vertical with radials, discone, phased vertical) use
    the front elevation with a top inset.
  A projection that would collapse the antenna to a line is not offered. A
  Slim Jim therefore shows its folded front elevation, stub spacing, gap
  detail, and feed offset; a Yagi shows its element layout, boom, and element
  lengths.
  Beam families use detail insets for crowded values: the Yagi labels every
  element and inter-element spacing, the Moxon shows a tip detail with both tip
  lengths and the gap, the hexbeam shows the spreader angle and a half-detail
  with the four segment lengths, the trapped Yagi shows a symmetric trap inset,
  and the quad beam labels each loop and the director spacing. Single-wire
  families dimension the feed offset and every load position; verticals add the
  loading-coil height and top-hat radius; fan dipoles label each leg and the
  construction sheet lists the included angles and end heights. The discone
  shows the cone angle and radial step, phased verticals label each source's
  phase and amplitude, the biquad shows the loop-side stack, and the quad beam
  has a driven-loop front detail inset.
- **3D**: isometric wireframe colored by gain (green low, yellow intermediate, red high), with a dBi legend, ground grid, feed marker, axes, and scale.

The construction view is selected automatically. Press **Apply design** or
**Simulate** and the view resets to fit the new model; changing antennas also
resets zoom, pan, and vertical exaggeration. Dimensions are placed around the
geometry with collision avoidance; the header reports how many low-priority
dimensions were hidden for space. Very small features such as the Slim Jim gap
use a detail inset marked *not to scale*. The **Zoom** selector scales the
sketch (0.5x, 1x, 2x, 4x, 8x); the mouse wheel steps through those values,
dragging pans, and double-click resets zoom and pan. The **Vertical scale**
selector can exaggerate the height (1x, 1.5x, 2x, 3x) for low horizontal
antennas. In a small pane the sketch switches to a compact layout with smaller
labels and margins; detail insets are hidden when there is not enough room, and
the header reports how many dimensions were hidden, and a compact strip below
the sketch lists their values. The wire schedule and construction sheet carry
the same data. Every linear dimension is anchored to
the model: its value matches the distance between its endpoints within 1% or
5 mm.

The construction sheet includes the rendered construction view and a **wire
schedule**: every canonical wire with its start and end coordinates, length,
diameter, and material, plus the primary feed point. When the construction view
is a top view, the sheet also includes an **Installation view (front)** with
height, ground line, and feed height; for front-view families whose horizontal
layout adds information, it includes a **Top layout** view instead. The sheet
also includes an **Isometric view** for the 3D relationship, so a family with a
complementary projection gets three views. The HTML page uses a responsive
two-column grid; the native PDF draws the additional views side by side with
captions. The sheet also includes a title block and
a bill of materials that totals conductor length by material and diameter,
plus load, transmission-line, and source counts. The construction sheet, HTML
report, and native PDF exports follow the UI language; technical identifiers,
wire IDs, units, and project names remain canonical. The native PDF keeps the
construction and auxiliary views as vector figures when the SVG source is
available and falls back to the raster preview otherwise; the simulation
report charts are also drawn as vectors. Use **File → Export → Export
wire schedule CSV...** to save the per-wire schedule as a spreadsheet file, or
**Export bill of materials CSV...** for the grouped conductor totals.
The sheet also carries an **Evidence and limitations** section with the
template's evidence level, source, tolerance, and unmodeled items. Use the schedule when a
dimension is too small to read or is hidden by the layout; it is the
authoritative construction data.

## Workflow modes and the next-step coach

AntennaDesk has three progressive workflow modes. Choose one from **View →
Workflow mode** or from the **Mode** selector in the toolbar. The choice is
saved with the other UI preferences and applies to the next window.

- **Guided** hides advanced actions and shows a compact **Next step** panel
  above the design actions. The panel changes with the project state: simulate,
  review diagnostics, inspect a high-SWR match, open the construction sheet,
  import a VNA measurement, or compare measured and simulated results. Use
  **Show advanced options** to reveal the full **Advanced** mode; no feature is
  removed permanently.
- **Standard** shows the full design editor with the **Advanced simulation**
  section collapsed. This is the default.
- **Advanced** shows the full editor and expands the solver, sweep, pattern,
  and band-analysis controls.

The next-step panel is a recommendation, not a lock. You can always use the
menus, switch designs, or open another result tab. In Guided mode the panel is
the quickest path through the design loop; in Standard and Advanced it remains
available as a lightweight reminder.

## Installation profiles

Use **Design → Installation profile...** to record the physical conditions of a
site. A project can store several named profiles, and the selected one is the
**active** profile. Use **Add**, **Duplicate**, and **Remove** to manage them.

Each profile records:

- the available height and horizontal space (leave them at **Not specified** if
  they are unknown);
- the preferred orientation;
- the support type: mast, tree, building, fence, portable, or other;
- a recommended ground preset;
- free notes about access, restrictions, or site conditions;
- an optional local image reference.

The profile is metadata. It does not change the antenna geometry or apply its
ground preset automatically; use the antenna editor for the model itself. The
active profile appears below the feed and matching summary and in the design
summary, construction sheet, HTML report, and native PDF reports. The height and
space values are upper bounds for the future advisor and comparison features,
not the design's actual dimensions. The image is referenced by path and is not
embedded in the project file.

## Undo and redo

Use **Edit → Undo** and **Edit → Redo**, or the standard Ctrl+Z / Ctrl+Shift+Z
shortcuts, to move through applied project changes: design edits, template
changes, new designs, loads, feed line, matching network, measurements, and
dimension estimates. Undo/Redo does not remove completed simulation runs or compact the
solver history. If a form has unapplied changes, AntennaDesk asks before
discarding them for a project-level undo. Text editors keep their own Ctrl+Z
while they have focus.

## Estimate dimensions for the current template

Use the **Estimate Dimensions...** button above the design panel or
**Design → Estimate Dimensions...** to refine the template already loaded in the
editor. The dialog supports wire and folded dipoles, loops (generic, quad,
delta), verticals in 1/4λ, 1/2λ, and 5/8λ, inverted-V, fan dipoles, end-fed
wires, OCFD, J Pole, Slim Jim, Ringo, Yagi, Moxon, and T2FD. The half-square
and bobtail-curtain templates have no frequency-first estimator; set their
dimensions from a published design or tune them with the solver. The estimator
does not offer a family selector and never changes the antenna type. The T2FD
path asks for the highest design frequency and applies the Cebik wide-long
broadband rule.

The result is a **starting point**, not a verified construction measurement.
The dialog shows assumptions, warnings, confidence, and dimension values. Apply
the estimate to the current design, then use **Optimize...** to refine it with
NEC. The checkbox **Open the family optimizer after applying** does this in one
step when a solver is configured and the family has an optimizer. For Yagi, the frequency
estimator supports 2 to 32 elements from the DL6WU trimming reference; the
NBS five-element preset remains available in the Yagi editor. For Yagi and
Moxon, **Estimate Dimensions...** keeps the polarization selected in the
dialog and uses the current boom height. For loops, it preserves the current
vertical or horizontal orientation and applies the estimated circumference.

## Analyze multiple bands

Use **Simulation → Analyze Bands...** or expand **Advanced simulation** at the
bottom of the design panel and use its **Band analysis** group to run the
current design over several amateur bands. The dialog starts from the family
default and lets you select any catalog band from 160 m to 23 cm, with a sweep
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

The analysis runs the solver once per band and builds a **Bands** results tab,
shown first. Each row shows the best SWR, its frequency, the sampled power gain,
takeoff angle, efficiency, and status. Selecting a row reuses the existing
impedance, pattern, currents, diagnostics, and raw-data views for that band;
double-clicking a row opens the impedance/SWR charts directly. A **Band**
selector above the result tabs switches bands from any view, and the active band
name appears in the impedance and SWR chart titles. Completed bands are kept if
another band fails or the analysis is cancelled.

The dialog also sets **Parallel workers** (1–4, default
`min(4, max(1, CPU count - 1))`). Only independent bands are parallelized; the
frequency points and pattern snapshots inside one band still run in order. Each
worker launches its own solver process, so more workers reduce wall time but use
more CPU and transient memory. The band order and the **Bands** table remain in
the selected order. Cancellation is propagated to every running band and keeps
the results that completed. Set the value to 1 for large models or a
memory-limited machine.

The global **Simulation pattern** group in **Advanced simulation** controls the
angular resolution and the pattern-frequency policy. Band analysis applies that
policy inside every selected band, so **Auto (bands)** uses the band snapshots
and a fixed count uses that many snapshots per band. The **Pattern** frequency
selector lists the snapshots from every analyzed band; selecting one switches
the impedance, currents, and pattern views to that band. Selecting a row in the
**Bands** tab does the same. CSV, HTML, and PDF exports include a band column or
summary when a band analysis is active; the source results CSV adds a band
column as well.

Defaults are evidence-labelled in the dialog. Transformer, tuner, counterpoise,
ground, and installation effects are not modeled as ideal guarantees; verify
the selected bands with a simulation and, when possible, a measurement.

## Result confidence and explanations

The **Diagnostics** tab now begins with a **Result confidence** card for the
current design. It shows:

- the template evidence level, source, tolerance, and limitation;
- what the model includes: canonical wires, feed, ground, loads, and the
  feed-line/matching post-processing chain;
- the dominant uncertainties: ground model, installation height, feed-line
  routing, common-mode current, and construction tolerances;
- a reminder that the model is an estimate and that critical dimensions and the
  installed match should be verified with measurements.

Use **What does this mean?** to switch between short explanations of impedance,
SWR, efficiency, gain/directivity/realized gain, takeoff angle, bandwidth,
ground model, and feed-line/matching losses. The explanations are contextual and
practical; they do not replace the solver results or the template limitations.
The same card is available without a completed simulation, because the evidence
and limitations belong to the design, not only to the last run.

## Create an antenna

Use **File → New Antenna...** to open the antenna catalog. Search or filter by
**Antenna Type** and choose the desired generator. The catalog is grouped by
antenna family: Dipole, Yagi, Loop, Vertical, and Custom. The Dipole family
contains the straight dipole, folded dipole, trap dipole, T2FD, end-fed wire,
sloper, random wire, doublet, inverted-V, inverted-L, off-center-fed dipole,
and fan dipole. The Yagi family includes the parametric Yagi and the Moxon
rectangle. The Loop family includes the generic vertical/horizontal loop plus
delta-loop, quad-loop, and magnetic-loop presets; the loop editor switches the
plane with the **Orientation** field. The Vertical family includes the generic vertical radiator,
the inverted-L, the half square, the bobtail curtain, and the loaded
vertical / mobile whip preset. The catalog lists each type by name and shows
its family, description, and evidence level in the detail pane. For every
template, choose the type first, complete its single editor dialog, and then
confirm the project name with a suggested name such as “40m Ringo”. The basic
dipole, folded dipole, and loop templates open the same variable editor used
after creation; there is no multi-page wizard.

### Basic templates

For a wire dipole, folded dipole, or loop, the editor opens directly with
frequency-aware starting dimensions:

1. Frequency, then the geometry for the selected type: wire dipole
   length/orientation, folded dipole element length/spacing, or loop
   circumference, side count, and orientation. The suggested length is a
   heuristic, not a universal final dimension.
2. Wire material and diameter.
3. Ground model. Finite ground asks for relative permittivity and conductivity.
   A **Soil preset** list provides typical starting values for average soil /
   clay, rich soil / loam, dry sand, rocky soil, fresh water, and salt water.
   The two numeric fields remain editable; changing either one switches the
   preset to **Custom / measured**.
4. Optional frequency sweep start/stop/points and reference impedance.

Confirm the editor with **OK**, then confirm the project name. The modal hides
the Family and Template rows because the template was already selected in the
catalog, and it fits the full editor without a scrollbar at the default size.
The full design panel remains available after creation for later changes.
Reports translate diagnostic messages and evidence source, tolerance, and
limitation text when a translation exists.

The soil presets are broad HF starting points adapted from the ARRL/Terman
ground table. Moisture, frequency, and local geology change the real values, so
use them as a first approximation, not as a measurement of the installation.

After creation, adjust the design panel and press **Apply design** or
**Simulate**. The design panel separates **Family** from **Template**; generated
templates now have their own inline editors. The Template field is read-only;
use **Change...** next to it or **Design → Change Template...** (or Ctrl+Shift+T)
to open the catalog and replace the current design with another template.

A full-wave loop normally presents roughly 100-150 Ω at resonance, so a direct
50 Ω target may require a matching network. Use a 2:1 balun or the Matching
Network dialog for a 50 Ω system. The loop optimizer keeps the selected loop
shape, orientation, and side count fixed and searches circumference, height,
and conductor radius jointly. The
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

**Estimate Dimensions...** applies Cebik's wide-long rule and requires both the
lowest and highest design frequencies. **Set starting dimensions from frequency**
in the editor applies the same rule: about `300/F(MHz)` feet of span and
`10/F(MHz)` feet of conductor spacing at the lowest design frequency. The default 3.5-30 MHz design starts with an 800 Ω
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
reported after a run. **Optimize...** searches element length, conductor
spacing, height, termination resistance, ideal transformer ratio, and conductor
radius together. The termination resistor and transformer remain ideal models,
and the span and spacing are construction starting points, not verified cut
lengths.

## Create a Yagi

Choose **File → New Antenna... → Yagi** to generate a Yagi as a first-class
template. The table contains each element's boom position, total length, and
radius. Add or remove elements, edit the values, and select the driven element.
**Polarization** selects horizontal or vertical elements. In both cases the
boom stays horizontal; vertical polarization rotates each element around the
boom. Height is the boom centerline, so a vertical Yagi needs enough clearance
for the longest element to stay above ground. The form rejects a geometry whose
lowest tip would reach the ground. Enable **Folded driven element** to replace
the driven element with two parallel conductors and two end connectors; set
**Fold spacing** to control the feed impedance and matching. Alternatively,
select **Feed match → Beta / hairpin** to split the straight driven element and
add a shorted stub along the boom; set its length and spacing. A folded driven
element and a beta/hairpin match cannot be combined. Hairpin length and spacing
must exceed twice the driven-element radius, otherwise the conductors overlap and
NEC-2 can report negative resistance. Matching hardware is not rescaled when the
frequency changes; tune it separately. Projects saved with undersized matching
hardware are repaired on load by schema 15. A gamma match is not modeled because
NEC-2 is unreliable for close-spaced gamma assemblies; use the Matching Network
dialog for an equivalent. **Load NBS 5-element preset** fills
the NBS TN-688 0.8λ starting geometry scaled to the selected frequency. Changing the frequency in the form rescales
the current element positions and lengths by the wavelength ratio. If the
element dimensions do not look consistent with the current frequency, the form
shows a warning; use **Design → Estimate Dimensions...** to rebuild a
2–32 element DL6WU starting design.

Set **Tapered tip length** and **Tapered tip radius** to add a smaller-radius
tip section to both ends of every element. A zero tip length keeps straight
elements. Tapering is not supported together with a folded driven element or a
beta/hairpin match, because those driven-element wires already have a separate
matching topology. The model uses physical tip-to-tip element lengths and does
not apply a boom-mounting correction; use published or measured lengths when
the boom diameter and clamps matter.

The NBS preset is reference-backed for gain: the published design has 9.2 dBd
gain over a half-wave dipole. The published design uses a folded driven
element; enable the folded option to model it. The feed impedance is not the
reference impedance in the straight, folded, or beta/hairpin case, so tune the
matching with the solver or the matching network. Once you edit positions or lengths, the result is an
experimental geometry with no external reference; simulate it and judge it on
its own modeled performance. The design panel keeps the element table editable;
use **Edit Custom Wires...** only when you want raw coordinates.

## Create a Moxon

Choose **File → New Antenna... → Moxon rectangle** to generate a two-element
Moxon with a reflector and driven element with bent tips. Set the element
width, spacing, tip lengths, height, azimuth, polarization, radius, material,
and ground. Horizontal polarization places the rectangle in a horizontal
plane. Vertical polarization places the complete rectangle in a vertical plane
while the boom stays horizontal. Height is the boom centerline, so a vertical
Moxon needs `height > width / 2` to keep the rectangle above ground. The dialog
reports the remaining tip gap. Use **Load 20 m reference scaled to current
frequency** to scale the published Cebik 20 m dimensions to the frequency in
the editor; it preserves the current height, ground, wire radius, polarization,
and material. The exact 14.17 MHz dimensions are reference-backed for
impedance, gain, and front-to-back ratio; scaled or edited geometry is a
heuristic starting point and has no independent reference.

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
construction view is the front elevation, so the included angle is visible.

## Create an inverted-L

Choose **File → New Antenna... → Inverted L** to generate a bent end-fed wire
with a vertical section and a horizontal top run. Set the vertical height, the
horizontal length, the base height, azimuth, wire radius, material, and ground.
The feed is at the base of the vertical section; the azimuth is the direction
of the horizontal run. Base height keeps the feedpoint and the top corner above
ground.

The generator is experimental: the bent-wire geometry is tested, but there is
no independent numerical reference for gain, impedance, or the matching
network. **Estimate Dimensions...** is disabled until a source-backed estimator
exists; **Optimize...** searches the vertical height, horizontal run, base
height, and conductor radius jointly. The construction view is the front
elevation, which shows the vertical section and the horizontal top run.

## Create a Ringo

Choose **File → New Antenna... → Ringo** to generate a half-wave vertical with
a horizontal matching ring at its base. Set radiator height, ring diameter,
ring height, ring side count, radius, material, and ground. The ring height
must be positive when using a ground model; the default is 0.25 m. Ringo is a
first-class experimental template with an inline editor.

## Create a half square or bobtail curtain

Choose **File → New Antenna... → Half square** or **Bobtail curtain** to generate
a self-contained vertical array. Both variants are monoband, broadside, and
vertically polarized:

- The **half square** has two quarter-wave verticals joined by one half-wave top
  wire. It is fed at the top corner of one outer vertical.
- The **bobtail curtain** has three quarter-wave verticals joined by two
  half-wave top wires. It is fed at the top junction of the center vertical.

The shared editor selects the array type and sets the overall horizontal span,
vertical height, base height, feed offset, azimuth, wire radius, material, and
ground. The **feed offset below top junction** moves the feed down the fed
vertical as a matching adjustment; zero is the published current-feed point.
Do not feed either array at a bottom corner: that is a high-voltage point and
produces a very high impedance. The **Load Cebik reference scaled to current
frequency** button scales the published 62.4 x 39 ft half-square or 125 x 38 ft
bobtail dimensions from 7.15 MHz to the current frequency, preserving the base
height, feed offset, radius, material, and ground. Those are free-space,
maximum-gain starting dimensions; scaled geometry is not independently
validated for gain, impedance, or a specific site.
The construction sheet lists the individual vertical and top-wire cuts. The
construction view is the front elevation. Neither template has a
frequency-first estimator; **Optimize...**
searches the horizontal span, vertical height, base height, feed offset, and
conductor radius jointly.

## Create a J Pole or Slim Jim

Choose **File → New Antenna... → J Pole** or **Slim Jim** to generate a vertical
radiator with a parallel matching stub. Set radiator height, stub length,
spacing, feed offset, base height, radius, material, and ground. The base
height must be positive when using a ground model; the default is 0.25 m to keep
the base connector out of the NEC ground plane. Slim Jim adds the top connector
and is also available by enabling **Folded** in the J Pole editor. Both are
first-class experimental templates. The construction view is the front
elevation; it dimensions the radiator or upper section, the stub or lower
section, the left leg, the gap, the stub spacing, the feed offset, and the base
height.

## Create an end-fed half-wave (EFHW)

Choose **File → New Antenna... → End-fed wire / EFHW** to generate a wire fed at
one end, optionally sloping between feed and far-end heights. Set the physical
wire length, feed height, end height, azimuth, radius, material, and ground; the
horizontal run is derived from the height difference. The **EFHW band preset**
buttons load the published ARRL 40/20/10 m lengths (66/33/16 ft), a 49:1
transformer, and a 0.05λ counterpoise starting point. Enable **Use counterpoise**
to model it as a drop from the feed plus a horizontal wire; disable it to remove
the counterpoise while keeping its last values for later. The transformer ratio
is an ideal feed-point transformation: `49` means a 49:1 unun, so the
antenna-side impedance is divided by 49 for the reported impedance and SWR. If
the requested end height is outside the wire's vertical reach, the frequency-
first estimator clamps it to the nearest reachable height and reports a warning.
EFHW is a first-class experimental template with an inline editor.

The **Fixed feed section** is a modeling partition at the start of the same
wire, not an extra conductor; it stabilizes the NEC end-fed source. When the
real counterpoise is disabled, a short **installation return** (0.10 m by
default) models the unavoidable coax/mast/earth path. It is a model proxy, not
a physical radial, and is modeled for the solver but not drawn or included in
the wire schedule/BOM. The return terminates at the ground plane; when the feed
is at ground level it is a 0.10 m wire on the ground plane. The real coax
routing dominates the SWR. The editor warns when either the fixed feed section
or the return/counterpoise is missing. **Check convergence** runs the same
design with 10, 21, and 51 radiator segments and reports the R, X, and SWR
spread. For the shortened presets the verdict uses **R and X only** (absolute R
spread up to 1 Ω and X spread up to 10 Ω); the SWR is informational because the
matching unit is not fully modeled. The 80-10 preset is impedance-converged
with the current model; the 40-20-10 preset remains R/X-sensitive. Verify the
installed SWR with a VNA.

The design panel's **Feed & matching** summary shows the internal EFHW matching
state, the project matching network, the feed line, and the balun loss as
separate rows. When both an active project network and an active internal EFHW
matching unit exist, the project network overrides the internal unit; it is
never cascaded. The internal values are retained but disabled until the project
network is removed. See
[ADR-0028](ADR/0028-matching-network-precedence.md).

### Shortened EFHW with a loading coil

The catalog also has **Shortened EFHW 80-10 m** and **Shortened EFHW
40-20-10 m** entries. They extend the End-fed family with a series loading
coil:

- **80-10 m:** 20.35 m from the feed to a 110 µH coil, then 2.39 m of top
  wire; 49:1 transformer and a 100 pF matching capacitor. The reference is
  G0KYA, also documented by EA7EER and G4WIF.
- **40-20-10 m:** 10.01 m from the feed to a 23 µH coil, then 1.85 m of top
  wire; 49:1 transformer and a 100 pF matching capacitor. The reference is
  the radioaficion.com / PA0EJH schematic.

Both presets open horizontally at 10 m by default. Change the feed and end
heights for a sloper or vertical installation. The coil position, inductance,
and optional series resistance are editable; the Q is reported when a resistance
is entered.
The shortened presets also use the fixed feed section and the installation-
return proxy when no real counterpoise is enabled. The loading coil is modeled
at a fixed node: the radiator is partitioned at the published coil offset, and
the coil section keeps three segments, so changing the radiator segmentation
does not move the coil. The wire schedule and bill of materials merge the
modeling partitions into one physical conductor for straight designs; a bent
design lists the vertical and horizontal sections separately.
The 100 pF capacitor is modeled as an ideal **primary shunt** across the 49:1
transformer; the transformer leakage is an editable starting value (0.198 µH)
from Squash Practice's measured 49:1 transformer, not this exact build. The
common-mode choke, ground, support geometry, core loss, winding capacitance,
and capacitor ESR are not modeled. The 40-20-10 preset follows the 23 µH/100 pF
schematic; CA4EMT documents a different 34 µH/150 pF variant.
When a project matching network is active, it replaces this internal unit
instead of cascading with it; the internal 100 pF/leakage values stay in the
design and are marked retained, not applied.
Enable **Inverted-L bend** to model the published installation: the
**Vertical section** is measured from the feed, the horizontal run is the
remaining wire length, and the form shows the resulting top height. The G0KYA
starting installation is about 8 m vertical and 15 m horizontal; the model
uses a sharp 90° corner and has not been independently validated. The default
is the straight horizontal installation, so existing designs are unchanged.
Edited or frequency-scaled geometry is experimental. Automatic frequency-first
estimation is disabled for these loaded presets. The matching capacitor and
transformer leakage remain context values in the family optimizer; they are not
optimized until a measured transformer model is available.

The frequency is the **design frequency** for the half-wave radiator; the
matching transformer and counterpoise remain installation-specific. Use
**Choose analysis bands...** to select the harmonic plan. The default for a
40 m design is 40/20/10 m, and the chosen plan is stored with the design.
Random wire is treated as tuner-assisted instead: its default analysis plan is
80–10 m, but changing that plan does not change the non-resonant wire length.

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
The design is an `EndFedParameters` design with the `random_wire` preset. Its
80–10 m default is an analysis band plan, not a continuous low/high geometry
input; use **Choose analysis bands...** in the generator to customize it.

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

The preset is multiband: the design panel starts with a **41-point
3.5–30 MHz sweep** so you can inspect the G5RV bands. The pattern resolution is
**Auto (max)** by default: AntennaDesk estimates the saved project size and
uses the finest pattern step that fits. The 41-point default uses a 1° pattern
at nine band snapshot frequencies. If even the coarsest pattern would be too
large,
it disables the far-field pattern and leaves the impedance/SWR sweep intact.
The panel shows the requested and effective resolution after a run.

The published dimensions are reference-backed (Carr, *Practical Antenna
Handbook*, via the Wikipedia G5RV article); the lossless TL model and the
installation are simplified. **Optimize...** searches dipole length, height,
feed height, line impedance, line length, velocity factor, and conductor radius
jointly. Tune the final line length, velocity factor, and feed line for your
installation.

## Create a ZS6BKW

Choose **File → New Antenna... → ZS6BKW** for a multiband doublet with a
matching section. The preset offers two documented variants:

- **Cebik/W4RNL reference:** 28.4 m wire with a 13.6 m, 400 Ω matching section.
- **Commercial variant:** 27.5 m wire with a 12.2 m, 450 Ω matching section.

The dipole height, feed height, azimuth, radius, material, ground, and line
velocity factor are editable. The matching section is a lossless geometry
transmission line between the dipole center and a short source wire; add the
transmitter coax with **Simulation → Feed Line...** when needed.

The Cebik reference gives usable no-ATU matches on **40, 20, 17, 12, and 10 m**;
80, 30, and 15 m are poor matches without a tuner. The design panel starts with
a **61-point 7.0–29.7 MHz sweep**, and **Band analysis** preselects
the five no-ATU bands. **Optimize...** searches the wire length, height, feed
height, line impedance, line length, velocity factor, and conductor radius
jointly. Dimensions are starting points: height, ground, line velocity factor,
and installation change the match. See L. B. Cebik, W4RNL, “The G5RV
Antenna System Re-Visited, Part 3: The Almost-No-ATU ZS6BKW”, and PA0FRI’s
commercial variant notes.

## Create a Zepp

Choose **File → New Antenna... → Zepp** for a classic 3/4-wave end-fed Zepp.
The preset starts with:

- radiator = practical half-wave length at the design frequency;
- matching stub = practical quarter-wave length at the design frequency;
- conductor spacing = 0.05 m, about 469 Ω with a 1 mm radius;
- feed/base height = 1 m; the radiator sits one stub length above the base.

The matching section is real geometry: one conductor connects to the radiator,
the second is open at the antenna end, and both join at the base connector. The
feed is the midpoint of that connector. The radiator length, stub length,
spacing, base height, azimuth, radius, material, and ground are editable. The
estimated impedance is shown for the current spacing and radius. **Set starting
dimensions from frequency** resets the radiator and stub to the half/quarter-wave
starting values.

The 1:1 common-mode choke at the transmitter end is required but not modeled;
NEC-2 has no choke or ferrite element. The coax and common-mode current are also
outside the model. Band analysis starts with odd harmonics (40/15 m for a 7.1
MHz design); even harmonics have severe stub imbalance. **Optimize...** searches
radiator length, stub length, conductor spacing, base height, and conductor
radius jointly. Tune the radiator and stub for the installed height, ground,
and hardware.

## Create a biquad or double biquad

Choose **File → New Antenna... → Biquad** for two stacked square loops, or
**Double biquad** for four. Both variants share horizontal rails. The feed is
at the midpoint of the central rail and an optional rectangular wire reflector
sits behind the driven plane.

The editor sets the design frequency, loop side, base height, reflector
enabled state and spacing, azimuth, radius, material, and ground. **Load
quarter-wave starting dimensions** sets the loop side to a quarter wave and the
reflector to half that side (an eighth wave). The feed height is derived from
the base, loop side, and loop count. The biquad is a broadband starting point,
not a validated multiband design. **Optimize...** searches loop side, base
height, reflector spacing when enabled, and conductor radius jointly. The
reflector can be disabled in the editor; the spacing is then excluded from the
optimizer.

The biquad's quarter-wave loop side and eighth-wave reflector spacing are
**published starting dimensions** (level B). The model uses a wire-rectangle
reflector and shared rails rather than the published solid reflector, so gain,
feedpoint impedance, and bandwidth are not independently validated. Simulate or
measure the installed antenna before relying on the result. The **double
biquad** remains experimental because its four-loop vertical stack differs from
the published side-by-side double-biquad topology.

## Create a loaded / linked dipole

Choose **File → New Antenna... → Loaded / linked dipole** for a portable
center-fed dipole. Set the frequency, orientation, full wire length, height,
link/coil offset from the feed, and either symmetric loading coils or open
links.

- **Loaded**: the full wire is active and a series R-L coil sits at each link
  position. The editor exposes inductance in µH and series resistance in Ω;
  the reported Q is `2πfL / R`. The model is an ideal series R-L load, not a
  core-loss calculation.
- **Linked**: the outer sections are disconnected and only the center section
  of length `2 × offset` remains active. Link contact resistance and physical
  link hardware are not modeled.
- **No coils**: with coils disabled, the closed-link state is a plain dipole.

**Optimize...** searches the active/full length, link offset, height, coil
inductance and resistance when enabled, and conductor radius jointly. The
family is classified **experimental**; tune the final geometry and coil with the
solver or a measurement.

## Create a hexbeam

Choose **File → New Antenna... → Hexbeam** for a single-band broadband beam
with a W-shaped driven element and a U-shaped reflector on a six-spreader
frame. The editor sets the frequency, driver and reflector half-lengths,
turning radius, tip gap, height, center feed gap, driver/reflector center
offset, azimuth, conductor radius, material, and ground.

The defaults are the published G3TXQ 20 m reference at 14.184 MHz: 219 in
driver half, 207 in reflector half, 24 in tip gap, and 130 in turning radius.
**Load starting dimensions** scales those values linearly with frequency.
**Optimize...** searches the driver and reflector halves, turning radius, tip
gap, height, and conductor radius jointly. The element model reconstructs the
bent wire path; the frame, spreader sag, feed balun, and multi-band nesting are
not modeled. Gain, front-to-back ratio, and impedance are not independently
validated.

## Create a trapped Yagi

Choose **File → New Antenna... → Trapped Yagi** for a two-band Yagi with one
parallel LC trap pair on every element. The editor sets the low- and high-band
frequencies, element count, driven element length, reflector and director
spacing, length factors, trap inset, trap frequency and inductance, height,
azimuth, conductor radius, material, and ground.

The traps are resonant on the high band, so the outer tips are effectively
isolated there; on the low band they load and shorten the elements.
**Load starting dimensions** sets the driven element to a half wave at the low
band, the trap inset to a quarter wave at the high band, and the spacing to a
fifth wave. **Optimize...** searches the driven length, reflector and director
factors and spacing, trap inset, trap inductance, height, and conductor radius
jointly. The element count, band frequencies, azimuth, ground, and material
remain user context.

The trapped Yagi is classified **experimental**. The traps are ideal parallel
LC loads with no core or dielectric loss; boom mounting, trap hardware, feed
line, and matching network are not modeled. Gain, front-to-back ratio, and
impedance on either band are not independently validated.

## Create a discone

Choose **File → New Antenna... → Discone** for a broadband vertical antenna
with a radial-wire cone and a larger top disc. The editor sets the frequency,
cone height and base radius, disc radius, base height, feed gap, radial wire
count, azimuth, conductor radius, material, and ground.

**Load quarter-wave starting dimensions** sets the cone to a quarter-wave slant
with a 30° half-angle and a disc radius of 0.7 times that slant. **Optimize...**
searches cone height, cone radius, disc radius, base height, and conductor
radius jointly. The wire count, feed gap, azimuth, ground, and material remain
user context.

The discone is classified **experimental**. The cone and disc are radial wire
approximations, not solid surfaces; the coax, mast, and feed transition are not
modeled. Impedance, bandwidth, and pattern are not independently validated.
The default band analysis is a heuristic broadband range from 0.5x to 1.5x the
design frequency. Use it as a starting point and verify with the solver or a
measurement.

## Create a quad beam

Choose **File → New Antenna... → Quad beam** for a two- or three-element beam
built from square loops. The reflector sits behind the driven loop and the
optional director in front. The feed is the midpoint of the left vertical side
of the driven loop.

The editor sets the frequency, loop count, driven loop side, reflector and
director spacing, bottom height, reflector and director length factors, boom
azimuth, radius, material, and ground. **Load quarter-wave starting dimensions**
sets the driven loop side to a quarter wave, the spacing to a fifth wave, and
the bottom height to a quarter wave. **Optimize...** searches the loop side,
spacings, height, reflector factor, director factor when enabled, and conductor
radius jointly. The loop count, azimuth, ground, and material remain user
context.

The quad beam is classified **experimental**. The loops are ideal thin-wire
squares; the boom, spreaders, mast, feed line, and matching network are not
modeled. Gain, front-to-back ratio, and feedpoint impedance are not
independently validated. Verify the pattern and match with the solver or a
measurement.

## Create a phased vertical array

Choose **File → New Antenna... → Phased vertical array** for two to four
vertical radiators spaced along one line. The editor sets the frequency,
element count, spacing, height, base height, phase step, amplitude taper,
radial screen, array azimuth, radius, material, and ground.

The first vertical is the primary feed with unit amplitude and zero phase.
Later verticals use `index × phase step` and a linear amplitude taper from 1 to
`1 - taper`. **Load quarter-wave starting dimensions** sets the radiator height,
spacing, and radial length to a quarter wave at the current frequency.
**Optimize...** searches height, spacing, base height, phase step, amplitude
taper, radial length when radials are enabled, and conductor radius jointly.
The element count, radial count, azimuth, ground, and material remain user
context.

The array is classified **experimental**. Mutual coupling is included by the
wire solver, but the combining network is ideal, per-element matching and
feed-line loss are not modeled, and the reported impedance and SWR refer only to
the primary feed. Verify the pattern and match with the solver or a measurement.

Keep the radial screens from overlapping. If twice the radial length exceeds the
element spacing, adjacent radials can cross or touch. The editor shows a warning
in that case because intersecting screens can produce unstable impedance or a
negative primary resistance in NEC. Shorten the radials, increase the spacing,
or model a bonded screen explicitly. With ideal phase and amplitude sources, an
individual port can also absorb power even without overlapping screens; check
the **Sources** results and the feed-network assumptions before tuning the
geometry.

## Create a Beverage

Choose **File → New Antenna... → Beverage** for a long horizontal receiving
wire fed at the near end. The editor sets the design frequency, length, height,
azimuth, radius, material, and ground, plus an optional resistive termination
to ground at the far end.

The model adds a short vertical wire at the far end and a series resistor.
**Load one-wavelength starting length** sets the wire length to one wavelength
at the current frequency; the default termination is 500 Ω. Both are starting
heuristics. **Optimize...** searches length, height, termination resistance when
enabled, and conductor radius jointly. Disabling the termination removes the
resistor and produces a bidirectional receiving pattern.

The one-wavelength starting length, 500 Ω nominal termination, and 6–10 ft
height guidance are **published starting dimensions** (level B). The Beverage
is a low-gain receiving antenna; the termination is not a complete ground
system, and the gain, pattern, received signal, and termination efficiency are
not independently validated. Use relative simulations for direction and
termination studies, then verify with a measurement.

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

The frequency is the **fundamental design frequency**; the geometry is not
optimized across a continuous Low–High range. Use **Choose analysis bands...**
in the generator to select the harmonic band plan. The default for a 40 m
design is 40/20/10 m, which are the 1x, 2x, and 4x harmonics. The selected plan
is stored with the design and restored when the project is reopened. Bands
outside that harmonic set, such as 15 m (3x), can be selected, but they will
usually dominate a worst-case or RMS score unless the feed ratio and
transformer are included in the optimization.

## Create a magnetic loop

Choose **File → New Antenna... → Magnetic loop** to generate a small vertical
loop with a gap at the top and a series tuning capacitor. Set the loop diameter,
bottom height, polygon side count, gap length, tuning capacitance, capacitor
ESR, azimuth, wire radius, material, and ground. The feed is at the midpoint of
the bottom side.

The capacitor is an ideal series RLC element. Conductor loss comes from the
material and wire radius; the capacitor ESR is the entered series resistance.
A coupling loop, capacitor voltage rating, and detailed capacitor loss model
are not included. The default capacitance is only a starting point: tune it
with a fine SWR sweep or a measurement, and use the existing matching-network
dialog when a direct 50 Ω feed is not practical.

The generator is experimental. It has no frequency-first estimator and no
family optimizer; **Estimate Dimensions...** and **Optimize...** are disabled
for this template because the ideal capacitor and loss model are not accurate
enough for optimization. The construction sheet reports the loop dimensions, gap,
capacitance, ESR, efficiency, and the simulated SWR bandwidth when a sweep is
available.

## Create a vertical

Ground-mounted radials are approximated **1 cm above the ground plane** so
NEC-2 can evaluate them. The canonical design keeps the base height you enter;
the small clearance is applied only to the solver deck and is reported as an
informational diagnostic. Without it, `nec2c` rejects radials lying exactly on
the ground with exit code 255.

That clearance is a numerical workaround, not a buried-wire or soil-contact
model. On finite ground the solver adds a warning when a conductor is at or
near ground level: impedance and gain can be numerically unreliable, and a
positive input resistance does not prove that the result is converged. Use
on-ground results for relative trends, run a sensitivity study over radial
count, radial length, and soil parameters, and validate the final design with a
feedpoint measurement. Do not tune a loading coil around a single on-ground
run.

Choose **File → New Antenna... → Vertical + radials** to generate a first-class
vertical radiator with an optional radial plane. Set the radiator height, base
height, radial count, radial length, first radial angle, wire radius, material,
and ground. The base height is also the radial-plane height. The default is
0.25 m. For a numerically stable model over finite ground, raise the radial
plane to about 0.75–1 m for 40 m. A 0.25 m plane can still produce invalid
negative resistance depending on radial length and automatic segmentation; the
solver reports that case as an error.

The **Radial system** list provides starting presets: **No radials**, **Ground
radials** (16 radial wires at 0.25λ), **Elevated radials** (four wires at
0.25λ with a 2 m radial plane), and **Ground screen** (a dense 32-wire,
0.10λ radial approximation). The presets write the base/radial-plane height,
radial count, and radial length; they do not replace the numeric fields. Editing
any of those fields switches the selector to **Custom / measured**. The
ground-screen preset is a dense radial approximation, not a bonded mesh or a
buried-wire model.

The **Loading coil** group adds a series coil at a selected height above the
radiator base. The model is an ideal series inductor with optional series
resistance; enter a measured or estimated coil resistance when you need a more
realistic efficiency estimate. **Coil Q** is shown as a derived value and can
also be entered: leaving Q at 0 means a lossless coil, while a positive Q sets
the series resistance from `Q = 2πfL / R`. Editing the resistance updates Q.
The coil is part of the vertical template, so the design panel updates it when
you apply the vertical fields, and the loads list and reports show it as a
series load on the radiator. Disable **Use loading coil** to remove it.

The **Capacitive top hat** group adds horizontal wires at the top of the
radiator. Set the hat radius and wire count; the wires are part of the generated
geometry and survive the round trip through **Edit Custom Wires...**. The hat
improves the short-radiator current distribution, but the model still uses an
ideal coil and does not include coil Q, a vehicle body, or a mast.

The generator is experimental: geometry and radial topology are tested, but it
has no independent numerical performance reference beyond the published
loaded-vertical example. The feed is at the base of the radiator, so the usual
delta-gap warning can appear. The design panel keeps the height, base, radial,
and coil fields editable; use **Edit Custom Wires...** for raw coordinates.

If a simulation reports **negative input resistance**, the passive model is
numerically invalid and the far-field gains are discarded. Raise the base and
radial plane (about 0.75–1 m for 40 m is a safer starting point), or use a
ground model that matches the installation, then simulate again. Do not tune the
coil around a negative resistance: the result has no physical meaning.

## Create a loaded vertical / mobile whip

Choose **File → New Antenna... → Loaded vertical / mobile whip** for a short
vertical with a series loading coil. The mobile preset starts with a 2.0 m
radiator, a 0.25 m base height, four 1.0 m radials, and a 10 µH coil at 1.0 m.
These are application starting points, not calculated resonance values: tune
the height, coil position, and inductance with the solver for your band and
installation. **Load 102 in example** sets the published K7MEM/ARRL starting
dimensions for 14.1 MHz: a 2.5908 m whip and a 4.511 µH base coil.

The radial plane is a simplified counterpoise. It does not model a vehicle
body, roof, or chassis, so treat mobile performance as qualitative until you
have measurements or a more detailed model. The same **Radial system** presets
are available in the loaded-vertical editor; choose **Custom / measured** to
keep the mobile-specific radial dimensions. The loaded vertical uses the same
first-class `VerticalParameters` as the generic vertical; the coil is stored as
a series load on the radiator and appears in the loads editor, reports, and
construction sheet. A capacitive top hat is also available for short verticals
with a large top load.

## Read the results

- **Bands**: appears first after a band analysis. One row per selected band with
  best SWR, frequency at best SWR, sampled power gain, takeoff angle, efficiency,
  and status. Selecting a row switches the other tabs to that band's result;
  double-clicking a row opens the impedance/SWR charts, whose titles show the
  active band. The **Band** selector above the result tabs is available from
  every view.
- **Impedance / SWR**: table of frequency, resistance, reactance, magnitude,
  and SWR, plus impedance and SWR charts side by side over the sweep. Resonance points
  where the reactance crosses zero are marked and listed above the table.
- **Sources**: for multi-source designs, one row per frequency and driven
  source with the source number, wire, amplitude, phase, resistance,
  reactance, and ideal input power. Negative power marks a source that absorbs
  power; the simulation also adds a diagnostic warning, and the primary feed
  still sets the reported impedance and SWR.
- **Pattern**: selectable **Azimuth** or **Elevation** cuts, with a **Metric**
  selector for **Power gain**, **Directivity**, or **Realized gain**, for each
  simulated frequency. The **Cuts** tab shows a line chart and a polar
  lobe diagram; the **3D lobe** tab shows a projected wireframe of the complete
  pattern, with each line colored by gain (green low, yellow intermediate, red
  high) and a min/max dBi legend. The interior stays transparent because only
  lines are drawn. Azimuth is the default cut view; use the selectors to inspect
  another plane. The default azimuth cut is chosen at the elevation with the
  highest gain; the azimuth diagram includes a dashed line showing the antenna
  orientation. Above-ground elevation cuts are drawn as open arcs rather than
  closed lobes. The angular resolution comes from **Pattern resolution** in the
  global **Simulation pattern** group under **Advanced simulation**; higher
  resolution samples the same NEC solution more finely.
  While you rotate or zoom the 3D lobe, AntennaDesk draws a coarser interactive
  mesh. When the movement stops it redraws the high-resolution display mesh,
  capped to **60% of the stored angular resolution** (40% coarser) for large
  patterns; this only affects the 3D paint. The stored pattern, the cuts, and
  the exports keep the full simulated resolution. The
  pattern frequency selector lists the pattern snapshot frequencies, not every
  impedance-sweep point. During a band analysis it lists all analyzed bands and
  switches the active band when you choose an entry. The 3D lobe draws a ground plane when the model has
  ground and only the
  upper-hemisphere pattern is requested. Its maximum-gain marker reports the
  gain and the takeoff angle above the ground plane; for free-space models it
  reports elevation above the horizontal plane instead. The marker is the
  highest sampled direction, so the reported angle is quantized to the selected
  pattern resolution. Drag the 3D lobe to rotate
  it, use the mouse wheel to zoom, and double-click to reset the view. The
  **Metric** selector changes the cuts, polar plot, 3D lobe, and cursor readout.
  Directivity and realized gain are derived by shifting the power-gain pattern
  to the corresponding value at its maximum direction. Power gain is not
  realized gain; see the gain summary below.
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
between power gain and realized gain. The pattern charts can display any of the
three metrics; the pattern CSV still contains the NEC power-gain columns, while
the per-frequency CSV includes the new metrics.

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

The **Solver** group sets the **analysis timeout** for one solver run, in
seconds. The default is 180 s and the accepted range is 10–3600 s. The value
applies to single simulations, band analysis, and family optimizations. Raise it
for large arrays or dense sweeps; lower it when you want a faster failure on a
stuck solver. A timeout does not fix invalid geometry or a negative-resistance
result, so check the diagnostics after a large run. The cancel action remains
available while the solver is running.

The **Simulation sweep** group controls the impedance/SWR frequency plan. In
**Auto (template)** mode the fields show the effective template range and use
the generator's default: a 31-point ±5% sweep for most generated templates, a
100-point sweep for basic and custom designs, the wide G5RV range, and the
family-specific bands for trap, T2FD, and fan designs. Select **Custom** to
override Start, Stop, and Points for the next single-design simulation. Band
analysis ignores this override and uses the per-band point count from its own
dialog. **Pattern resolution** controls the angular sampling of the radiation
pattern: 30°, 20°, 15°, 10° (normal), 5° (fine, default), 2° (very fine), or 1°
(maximum).

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
Custom designs keep their own template sweep controls; **Auto (template)** uses
them, while **Custom** in **Simulation sweep** overrides them for one run.
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

## Balun/unun loss

Use **Simulation → Balun/Unun Loss...** to add a matched insertion loss for a
balun or unun. The model uses a reference loss at a reference frequency and a
power-law exponent:

```text
loss(f) = Lref x (f / fref)^n
```

The preview shows the resulting loss at 1.8, 7, 14, and 28 MHz. The loss
reduces realized gain, but it does not change geometry, impedance, or SWR.
This is an application fit, not a core-loss calculation; use measured
insertion-loss data when available. The setting is project-level and saved
with the project and simulation runs.

## Feed-chain position and loss budget

The project matching network can sit in two places. Open **Simulation →
Matching Network...** and choose **Position**:

- **At the antenna feedpoint**: transmitter → feed line → matching network →
  antenna. This is the legacy behavior.
- **In the shack, before the feed line**: transmitter → matching network → feed
  line → antenna. The line carries the antenna mismatch, so its loss can be
  much higher even though the transmitter sees a good SWR.

Use **Simulation → Feed-Chain Loss Budget...** after a simulation to inspect the
selected chain. The dialog shows the path, lets you set the transmitter power,
and lists per frequency: SWR, mismatch loss, actual line loss, matching-network
loss, balun loss, power delivered at the antenna, radiated power, and the
dominant loss stage. The line loss is the dissipative loss under the modeled
impedance, not the matched-line value. Component values may not add exactly
when mismatch changes between stages. Change the position or line and simulate
again to refresh the budget.

The ideal family transformer remains at the antenna. The current balun/unun
model is a matched insertion loss and is not assigned a shack/antenna position;
a measured frequency-dependent balun model would be needed for that. See
[ADR-0030](ADR/0030-feed-chain-topology.md).

## Component calculators

Use **Tools → Component Calculators...** for construction helpers:

- **Coil**: Wheeler air-core approximation; calculate inductance from turns or
  turns for a target inductance.
- **Trap / LC**: solve the missing capacitance, inductance, or resonant
  frequency and show the inductive and capacitive reactance at resonance.
- **Balun / unun**: ideal turns-ratio and impedance-ratio conversion. It does
  not model core loss, winding capacitance, power rating, or bandwidth.
- **Conductor**: compare DC resistance, an approximate high-frequency
  resistance, and skin depth for copper or aluminum.
- **Common-mode choke**: reference notes. AntennaDesk does not model a
  common-mode choke; use measured `Zcm(f)` data.

The **Loads** editor has a **Calculator...** button. It opens the coil or trap
tab with the current load values and **Use result** copies the calculated
inductance/capacitance back into the load form. Coil and trap results are
starting values; verify them with the solver and a measurement. The calculators
are construction aids, not antenna models.

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
the antenna feed. The dialog separates the **Design target** from the
**Components**.

The design target stores the design frequency, load R, load X, source
impedance, and where the target came from. **Use current simulation point**
copies the frequency and the raw primary-side feed impedance from the current
simulation result; it divides the solver's antenna-side source impedance by the
ideal transformer ratio, so it does not copy the post-chain impedance shown in
the Impedance tab. The target is saved with the project, preloaded the next time
the dialog opens, and cleared when the project network is removed.

Choose **L**, **Pi**, or **T** topology and set the reactive elements in µH/pF.
Only the component fields used by the selected topology are shown. For an L
network, choose whether the shunt element is on the transmitter side. Use
**Auto-design L network** to calculate one valid L section from the target and
source impedance; the dialog reports when a single section cannot match the
load. Pi/T are manual designs in this slice. Set a component Q to include loss
in the input impedance (0 means lossless).

The project network is global: it applies to every design in the project. Its
**Position** selects the chain order. **At the antenna feedpoint** evaluates
transmitter → feed line → matching network → antenna; **In the shack** evaluates
transmitter → matching network → feed line → antenna. The default is feedpoint
for compatibility with older projects. Impedance and SWR include the network;
pattern and power gain remain antenna-side. Network loss is included in realized
gain and reported separately, and the actual line loss changes with the selected
position.

In the Impedance/SWR table, right-click a frequency row and choose **Create
Project Matching Network...** to start from that simulation point. The action
uses the raw primary-side feed impedance from the solver source result, divided
by the ideal transformer ratio, rather than the post-chain impedance shown in
the table. The dialog opens with the frequency, load R/X, and reference
impedance filled in. If raw source impedance is unavailable, the action is
disabled and the menu explains why. Replacing an existing project network asks
for confirmation, and an EFHW design with active internal matching shows the
override warning before the dialog opens.

### Project network on an EFHW design

For an end-fed design with active internal matching, an active project matching
network **replaces** the internal EFHW matching capacitor and transformer
leakage. The project network is not cascaded with the internal unit. The ideal
transformer ratio still applies. The internal values stay in the design but are
disabled and marked **retained, not applied** in the End-fed editor and in the
**Feed & matching** summary.

To restore the internal EFHW network, use **Remove project network** in the
summary or the End-fed editor. The project network is then cleared and the
internal model becomes effective again. The same rule applies to every
`EndFedParameters` preset. See
[ADR-0028](ADR/0028-matching-network-precedence.md) for the full policy and the
no-cascade limitation.

In the load editor, **Add parallel trap** calculates the capacitance for a
parallel LC trap from the entered inductance and resonant frequency. The trap is
stored as a normal parallel RLC load and emitted as a NEC `LD 1` load.

## Designs and comparison

Use **Design → Designs → New Design in Project...** to duplicate the current
design inside the same project, **Rename Design...** to change its name, and
**Delete Design** to remove it. The design selector in the toolbar switches
between designs. Completed runs are stored in the project; the latest run for
each design is shown when you switch or reopen the project.

Use **Design → Designs → Compare Designs...** to compare **two to four**
designs. The dialog no longer treats stored results from different conditions as
directly comparable. It shows a **Common comparison basis** with a shared
frequency sweep, ground model, optional reference height, and reference
frequency. Press **Recompute comparison** to run every selected design with that
basis. The project's feed line, matching network, and balun loss remain part of
the common chain.

The reference height maps the family's own height field: horizontal wire
families use their wire or apex height; Yagi, Moxon, and beams use the boom
height; verticals shift their base so the radiator top reaches the reference.
Ambiguous families keep their native height and show a warning. Choose **Native
heights** to disable height mapping explicitly; the ground is still normalized.
The basis and warnings stay visible, so a comparison never silently claims
equivalent conditions.

The metric table has one column per design and includes impedance, SWR, gain,
directivity, realized gain, efficiency, footprint, maximum height, conductor
length, wire/load/line counts, and build effort. When band analyses exist, a
band-summary table shows the best SWR per design and band. The SWR and gain
pattern charts overlay every selected design, and missing results are reported.
The comparison is based on the same solver results, not a new electromagnetic
model; see [ADR-0029](ADR/0029-comparison-basis.md).

## Optimize the current design

Use **Optimize...** in the design panel or the **Design** menu. The dialog is
driven by an explicit optimizer descriptor for the current family. There is no
generic dipole fallback: a family either has its own descriptor or the action is
disabled with an explanation.

While a run is active, the dialog shows a determinate progress bar with the
completed evaluations and the estimated total. The estimate is an upper bound:
the optimizer may converge early and the bar completes when the run stops. The
family dialog also shows the best score seen so far; updates are throttled so
large budgets stay responsive. The element and synthesis dialogs use the same
progress pattern with their own maximum-evaluation budget.

### Variables and topology

The dialog lists every optimizer variable, grouped into **Geometry**, **Feed**,
**Family loads**, and **Conductor**. Typical tuning dimensions are enabled by
default. Installation context is available but **unchecked by default**:
installation height (including apex, base, feed, counterpoise, and ring
heights), feed-point placement, conductor radius/diameter, and
transformer/balun ratios. Check a box to include a context variable; clear it
to lock it. Any excluded variable marks the run as a partial optimization.
Material and ground remain installation context outside the optimizer.

The topology is chosen in the family editor and stays fixed during a run:
orientation, polarization, loop sides, Yagi element count, folded elements,
matching type, SCV variant, EndFed preset, and whether the top hat, loading
coil, radial system, or counterpoise exists. Change the topology in the editor
first, then optimize. To compare topologies, duplicate the design variant and
optimize each one separately.

The optimizer searches all enabled geometry, feed, and family-load dimensions
jointly with a deterministic hybrid of differential evolution and a bounded
local pattern search. It is not a one-dimensional sweep and not a
coordinate-only search. Frequency, band plan, ground model, material, and
pointing azimuth remain design context; they are not silently optimized.

### Objectives and constraints

Choose the objective supported by the current descriptor:

- **Target impedance** with selectable `R + jX`;
- **Minimum SWR** at the band edges (worst case);
- **Minimum SWR at operating frequencies**: balances the RMS SWR at the
  family operating frequencies. For an OCFD it uses the harmonics that fall
  inside each selected band (for example 7.1, 14.2, and 28.4 MHz); other
  families use the band centers;
- **Maximum power gain**;
- **Maximum front-to-back ratio**;
- **Maximum efficiency**;
- **Maximum SWR bandwidth**;
- **Balanced** weighted gain/front-to-back/SWR/efficiency. The weighted terms
  are normalized (3 dB of gain, 10 dB of front-to-back, `SWR - 1`, and
  efficiency as a fraction) so the weights are comparable.

Gain and front-to-back require a far-field request. Bandwidth requires a
frequency sweep. The optional **Maximum SWR** field adds a soft constraint; the
hard constraints are the family geometry rules, minimum conductor spacing,
element ordering, feed limits, and positive dimensions.

### Operating modes

The **Operating mode** selector controls how many operating points each
candidate is evaluated at:

- **Single frequency** is the default and uses the design frequency once.
- **Band-aware** evaluates the scoring frequencies and reports the worst SWR,
  impedance error, gain, front-to-back ratio, and efficiency. With the
  **Minimum SWR at operating frequencies** objective, the scoring points are
  the family operating frequencies (OCFD harmonics or band centers); otherwise
  they are the listed band edges. The band-edge list defaults to the current
  band plan (start, center, and stop of each selected band) and can be edited as
  comma-separated MHz values.
- **Robust (tolerance)** evaluates the scoring frequencies at the nominal
  geometry and at two deterministic dimensional-tolerance corners (± the
  selected percentage of every active length and radius). Variables left
  unchecked are not perturbed. The score adds a variance penalty, so a design
  that only performs well at the nominal dimensions ranks lower.

Band-aware and robust modes multiply the solver runs by the number of scoring
frequencies and tolerance scenarios. The budget hint shows the resulting
estimate. Bandwidth optimization is only available in single-frequency mode
because it already requires a frequency sweep. The maximum-SWR soft constraint
uses the worst evaluated scoring point in these modes. The band analysis after
Apply Best still shows every band edge, including the ones that were not part
of the score.

### Budget and results

Choose a search budget:

- **Fast** for a quick exploratory run;
- **Balanced** as the recommended default;
- **Thorough** for a final design; it runs at least 1,500 global and 1,000
  local candidate evaluations before the frequency/scenario multiplier.

The budget hint is counted in **solver runs**, not candidate designs: each
candidate can use several frequencies and tolerance scenarios. The result table
and summary report the winning seed's candidate evaluations; the
`seed_evaluations_total` metric records the total across all seeds. If the best
score is still improving near the end of the budget, the run extends
automatically up to twice the initial candidate budget. The random seed is
exposed for reproducibility.

**Seed runs** executes the same search with consecutive seeds (`seed`,
`seed + 1`, ...) and compares the resulting designs. **Thorough** defaults to
three runs; the other profiles default to one, and the control accepts 1–4.
The runs are evaluated sequentially, so each run keeps its own parallel
candidate workers, and cancellation stops the current run without starting the
next one. The best-scoring result is applied and its seed is stored in the
summary. Two tolerances decide whether the runs converged: the score spread
must be at most the larger of 2% of the best score or 0.05, and every active
continuous parameter must stay within 2% of its search span. Integer and choice
variables must match exactly. When the designs diverge, the dialog reports the
spread and the recommendation block warns that the selected design should be
reviewed. To inspect an individual run, set **Seed runs** to 1 and enter that
seed. With one seed run the result keeps the single-run shape and no
verification metrics are added.

**Apply Best** applies the best nominal parameters and keeps the optimization
summary with the design. In **Single frequency** mode it then runs the normal
single simulation. In **Band-aware** and **Robust** modes it runs a full band
analysis with the current band plan, so the **Bands** tab, impedance/SWR charts,
and patterns show every analyzed band for the applied geometry. Robust mode
analyzes the nominal geometry; the ± tolerance corners are used only for
scoring. The optimizer result table remains an aggregate summary (for example,
the worst SWR across the scoring frequencies); per-band values are in the band
analysis.

**Parallel workers** controls how many independent candidate evaluations run at
once. The value is capped at four in the dialog and defaults to
`min(4, max(1, CPU count - 1))`; set it to 1 to keep the sequential path. Only
whole candidates are parallelized: the scoring frequencies and pattern points
inside one candidate are still evaluated in order. Each worker launches its own solver
process, so more workers reduce wall time but increase CPU and memory use; the
analysis timeout applies independently to each worker's solver run. For a fixed
search configuration the candidate order and the reported results are
deterministic. The one-worker and multi-worker paths use different deterministic
search trajectories, so compare runs at the same worker setting. Cancellation is
propagated to every in-flight solver process and queued evaluations are
discarded.

**Maximum turning radius** rejects candidates whose horizontal footprint from
the mast exceeds the limit. The mast is the boom midpoint for Yagi and Moxon
arrays and the feed's horizontal projection for every other family. **Maximum
boom length** is available for Yagi and Moxon arrays. A zero value means no
limit. These are hard mechanical constraints: an out-of-limit candidate is
reported and never offered as Apply Best, and the limit is stored with the
optimization summary.

The result table is ranked from best to worst and reports the score, R, X, SWR,
gain, front-to-back, efficiency, and any error. The summary reports the status,
evaluation count, and best score. The sensitivity line ranks the variables that
most affect the score, so fragile dimensions are visible before construction.

When at least two metrics are available, the dialog also shows the non-dominated
Pareto front: candidates that trade one metric for another, such as lower SWR
against higher gain or a smaller target-impedance error. These candidates are
informational; **Apply Best...** still uses the ranked best score.

Deterministic **Recommendations** point out a failed search, an exhausted
budget, locked variables, high SWR, strong band-edge variation, tolerance
sensitivity, or the single dimension that most affects the score. They describe
the modeled search, not a guaranteed physical outcome.

**Export CSV...** writes the ranked evaluation log, metrics, errors, Pareto
flags, and every design variable to a UTF-8 CSV file. The export is independent
of the project file and is useful for external analysis.

**Apply Best...** writes the result to the correct family editor and starts the
normal full sweep/pattern simulation. The run summary (mode, objective, status,
seed, evaluation count, band edges, tolerance, winning vector, metrics, and
recommendation keys) is stored with the design in schema version 18 and shown
the next time the optimizer dialog opens. Verify the applied design with the
full simulation and, where possible, a measurement.

### Families with a family optimizer

The following typed families have a complete joint optimizer:

- wire dipole and folded dipole;
- loop;
- vertical, including radial system, loading coil, and top hat;
- inverted-V and inverted-L;
- J Pole and Slim Jim;
- Ringo;
- half square and bobtail curtain;
- biquad and double biquad;
- Beverage receiving wire;
- loaded / linked dipole;
- phased vertical array;
- quad beam;
- discone;
- trapped Yagi;
- hexbeam;
- OCFD, EndFed/EFHW, and sloper;
- typed G5RV, ZS6BKW, and Zepp;
- the doublet radiator as a dipole, with its feed line in the matching stage;
- fan dipole, trap dipole, and T2FD;
- Yagi and Moxon.

For a Yagi, the element count is fixed; the optimizer varies every element
length, every inter-element gap, height, folded-driven spacing when enabled, and
beta/hairpin length and spacing when selected. The optimizer preserves the
starting director-length taper and inter-director gap trend: adjacent directors
or gaps cannot invert the initial shape. A DL6WU start stays DL6WU-like, while
the NBS preset keeps its published small non-monotonicity. To change the shape,
edit the Yagi or start from a different reference before optimizing.
Polarization and match type remain editor choices. For a fan dipole, both
lengths and included angles are optimized together, with a constraint that keeps
the wires distinct. For a Moxon, width, depth, both tip lengths, height, and
radius are searched jointly.

### Families without an optimizer

The Optimize action is disabled, with a tooltip explaining the reason, for:

- **Magnetic loop**: the ideal tuning capacitor and ESR model are not accurate
  enough to optimize efficiency or bandwidth without false precision.
- **Random wire**: deliberately non-resonant and tuner-assisted.
- **Custom geometry and imported designs**: the topology is not parameterized.

G5RV, ZS6BKW, Zepp, and the doublet are typed families and have a family
optimizer. The doublet remains a dipole plus a project-level feed line, so its
radiator is optimized with the dipole descriptor and its feed line belongs to
the separate matching stage.

The old one-dimensional length search and OCFD/J-Pole synthesis dialog have been
superseded by the family optimizer for the affected typed families. Bounded
impedance synthesis remains an internal application capability, not a separate
menu action.

## Construction sheet

Use **Design → Construction Sheet...** for a printable sheet with target
frequency, type-aware dimensions, feed position, height, wire, ground,
simulated impedance/SWR, resonance, and construction notes. Dipoles show first
and second leg lengths; folded dipoles show element and connector lengths;
loops show orientation, side length, circumference, side count, height, and
feed side.
**Save HTML...** writes the sheet and **Save PDF...** writes a native PDF.
**Save Package...** writes one ZIP with the HTML sheet, the native PDF, the
wire-schedule CSV, the conductor BOM CSV, and a plain-text build-notes file.

Use **Design → As-Built / Checklist...** to record what was actually built:
measured dimensions with their design values and differences, free notes, and
a construction checklist. The record is saved in the project and appears in the
construction sheet and PDF. The sheet also includes a starting hardware BOM
(insulators, supports, connectors, balun/unun, radial wire, ground rod, traps,
loading coils, and guy line) and target values for every loading coil and trap.
Hardware quantities are starting estimates; adjust them for your actual
installation.

## Export results

Use **File → Export → CSV...** for the frequency sweep table, **File → Export
→ Source results CSV...** for one row per frequency and driven source when the
design has multiple sources, **File → Export
→ Pattern CSV...** for the far-field grid (frequency, θ, φ, gains,
polarization, and E-field components), **File → Export → Pattern PNG...** for
the current cut/3D pattern image using the selected metric, or one image per
band when a band analysis is active. **File → Export → Geometry PNG...**,
**Geometry SVG...**, **Geometry PDF...**, or **Geometry DXF...** for the
current geometry view, **File → Export → HTML Report...** for a self-contained
HTML report, or **File → Export → PDF Report...** for a native PDF with design
parameters, configuration, solver metadata, fingerprint, diagnostics,
impedance, resonance, and charts.
Simulation runs are stored when you save the project, including raw solver
text. Project files are losslessly gzip-compressed JSON; the 64 MB limit applies
to the compressed file. Saving above 32 MB compressed shows a warning, and
**Tools → Compact Simulation History...** keeps only the latest run per
design.

## Cancel and errors

While a simulation runs, the interface stays responsive. Press **Cancel** to
terminate the solver. The status bar and diagnostics tab explain failures.
Invalid designs are rejected before the solver runs.

## Save and open

Use **File → Save** / **Save As...** to write a versioned `.antennadesk` JSON
project, and **File → Open Project...** to reopen it. The application prompts
before discarding unsaved changes.

Project serialization and gzip compression run in a worker thread. For a large
project, a modal **Preparing project...** progress dialog appears while the
payload is prepared; the window remains responsive and the operating system
does not report the application as unresponsive. The payload is serialized once
and then written atomically; the 32 MB warning and 64 MB hard limit still
apply.

Opening a project also runs decompression, migration, and validation in a
worker thread. A modal **Opening project...** dialog appears for large files and
the project is applied only after validation succeeds.

## Language, units, and font size

Use **Edit → Preferences...** (`Ctrl+,`) to set the language (**System**,
English, or Español), the display units (metric m/mm or imperial ft/in), and
the font size (Small, Normal, or Large). **Restore Defaults** returns to
System, metric units, and Normal font size.

Preferences are saved and applied at startup. **Normal** restores the system
font. The font preset scales the standard widgets, the antenna sketch, the
pattern views, the chart axes and legends, the start-page headline, and dialog
initial sizes. Changing the language updates every antenna-family editor, and
changing the units converts every editor and generator dialog without losing
the physical dimensions. Exported reports keep their own fixed typography. The
domain and project files always store canonical meters and hertz.

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
- Optimization covers every geometry, feed, and family-load variable of the
  supported typed families with a joint hybrid search, including G5RV, ZS6BKW,
  and Zepp. Custom/imported designs, magnetic loops, and random wires are
  excluded. There are no boom-length or turning-radius constraints. Band-aware,
  robust, Pareto, persisted-summary, and recommendation support is implemented;
  the Pareto front is descriptive and is not itself optimized.
- Project files store normalized results and raw solver text; many long runs
  can reach the 64 MB project limit.
- The feed line is a uniform-line post-processing model. It reports impedance
  and SWR at the transmitter but does not add line loss to the pattern gain or
  realized-gain calculation.
- Far-field samples are NEC power gains. The pattern view can shift them to
  directivity or realized gain at the maximum direction, but the pattern CSV
  keeps the original power-gain columns. Relative permeability is not emitted to
  NEC; conductor conductivity is.
- Multiband defaults are starting points. The doublet default is inferred from
  a high-impedance project feed line; the tuner is not modeled as an automatic
  matching network. Design comparison shows a band summary when analyses are
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
