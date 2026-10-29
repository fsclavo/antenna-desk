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

The application opens with a 40 m dipole loaded. Press **Simulate** (or F5).
The design panel on the left shows frequency, length, height, orientation,
wire diameter, material, ground, reference impedance, and the frequency sweep.
The center shows a dimensioned construction sketch with the wire, feed point,
center, ends, height, total length, per-leg lengths, ground line, and a separate
scale bar. Use the **View** selector above the sketch to switch between
**Elevation** and **Plan**. The **Vertical scale** selector can exaggerate the
height (1x, 1.5x, 2x, 3x) when the antenna is low relative to its length; the
summary notes when vertical exaggeration is active.

## Create a dipole with the wizard

Use **File → New Dipole...**. The wizard asks for:

1. Project name, band, and frequency.
2. Total length, height, and azimuth. The suggested length is a half-wave
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

- Only horizontal center-fed dipoles are implemented in the GUI.
- The GUI currently edits the first design variant in a project.
- No loads, networks, transmission lines, or radial ground screens.
- Simulation results are not saved inside the project; comparison and export
  use results from the current session.
- Native PDF export is deferred; use the browser print dialog for the HTML
  report.
- Relative permeability is not emitted to NEC; conductor conductivity is.
- Domain and solver diagnostic messages are currently reported in English.
- A simulation is a prediction conditioned by the model. Unmodeled buildings,
  trees, masts, feed lines, and real ground can change measured performance.
