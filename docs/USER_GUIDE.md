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
(or F5). The design panel on the left shows frequency, orientation, length,
height, wire diameter, material, ground, reference impedance, and the frequency
sweep. Choose **Vertical** for a vertical center-fed dipole; in that case the
height field is the base height above ground and the azimuth is disabled.
The center shows a dimensioned construction sketch with the wire, feed point,
center, ends, height, total length, per-leg lengths, ground line, and a separate
scale bar. Use the **View** selector above the sketch to switch between
**Elevation** and **Plan**. The **Vertical scale** selector can exaggerate the
height (1x, 1.5x, 2x, 3x) for low horizontal antennas; it is disabled for
vertical dipoles and plan view. The elevation view draws vertical dipoles with
base-height and total-length dimensions.

## Create a dipole with the wizard

Use **File → New Dipole...**. The wizard asks for:

1. Project name, band, and frequency.
2. Orientation, total length, height, and azimuth. For a vertical dipole the
   height is the base height. The suggested length is a half-wave
   approximation, not a universal final length.
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

SWR is computed with the reference impedance in the design panel (default
50 Ω). A low SWR does not prove high efficiency or a useful pattern.

## Variants and comparison

Use **File → New Variant...** to duplicate the current design, **Rename
Variant...** to change its name, and **Delete Variant** to remove it. The
variant selector in the toolbar switches between designs. Each variant keeps
its own last simulation result for the current session.

Simulate the variants you want to compare, then use **File → Compare
Variants...**. The dialog shows design and result metrics side by side, an SWR
overlay, and a gain-pattern overlay for the frequency nearest each variant's
design frequency. Missing results are reported in the dialog.

## Optimize the length

Use **Optimize Length...** in the design panel or the File menu. Set the
minimum and maximum physical length, the target reactance (0 Ω for series
resonance), the maximum number of solver evaluations, and the reactance
tolerance. The dialog evaluates the dipole at the design frequency, shows every
evaluation, and reports the best length. A sensitivity table evaluates the best
length at ±10 mm and ±25 mm so construction tolerances are visible.

Press **Apply best length** to update the design; the application then runs the
full sweep/pattern simulation with the current settings. The optimizer is
bounded by the length range and evaluation limit; it is not a multi-objective
optimizer.

## Construction sheet

Use **File → Construction Sheet...** for a printable sheet with target
frequency, total wire length, left and right leg lengths, feed position, height,
wire, ground, simulated impedance/SWR, resonance, and construction notes.
**Save HTML...** writes the sheet; use the browser print dialog for PDF.

## Export results

Use **File → Export CSV...** for the frequency sweep table, or **File → Export
HTML Report...** for a self-contained report with design parameters,
configuration, solver metadata, fingerprint, diagnostics, impedance,
resonance, and charts. The HTML report can be printed to PDF from a browser.
Results are not stored in the project file, so export before closing the
session.

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

- The GUI supports horizontal and vertical center-fed dipoles; loops, folded
  dipoles, VNA CSV import, and measurement records are not implemented yet.
- The GUI currently edits the first design variant in a project.
- No loads, networks, transmission lines, or radial ground screens.
- Simulation results are not saved inside the project; comparison, export, and
  the construction sheet use results from the current session.
- Native PDF export is deferred; use the browser print dialog for the HTML
  report and construction sheet.
- Optimization is one-dimensional length adjustment against a single reactance
  target; bandwidth, gain, efficiency, and multi-objective optimization are not
  implemented yet.
- Relative permeability is not emitted to NEC; conductor conductivity is.
- Domain and solver diagnostic messages are currently reported in English.
- A simulation is a prediction conditioned by the model. Unmodeled buildings,
  trees, masts, feed lines, and real ground can change measured performance.
