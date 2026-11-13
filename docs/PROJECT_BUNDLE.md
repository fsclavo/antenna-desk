# Portable project bundles

AntennaDesk project bundles move a project and its referenced local images
between machines. They are plain ZIP files with a documented manifest and no
server, account, telemetry, or executable content.

## Export

Use **File → Export Project Bundle...** to write a
`.antennadesk-bundle` file. The export:

- serializes the current project exactly as the native project format does;
- includes every existing image referenced by an installation profile or a
  journal entry;
- rewrites the bundled project copy's image references to `assets/...`; the live
  project is not modified;
- records missing image references in the manifest and reports them after the
  export;
- writes the ZIP atomically through a temporary file next to the destination.

The project payload keeps the normal schema, migrations, simulation runs, and
64 MB compressed limit. The bundle adds no project schema field.

## Bundle contents

```text
manifest.json
project.antennadesk
assets/0001-site-photo.jpg
assets/0002-plan.png
```

`project.antennadesk` is the normal gzip-compressed project payload. The
manifest has this shape:

```json
{
  "format": "antennadesk.project_bundle",
  "format_version": 1,
  "application_version": "0.5.0",
  "created_at": "2026-11-12T12:00:00+00:00",
  "project_file": "project.antennadesk",
  "project_name": "40 m dipole",
  "assets": [
    {
      "original_reference": "/home/user/photos/site.jpg",
      "asset_path": "assets/0001-site.jpg",
      "size": 123456,
      "sha256": "…",
      "missing": false
    }
  ]
}
```

Missing references keep `missing: true` and have no asset path, size, or hash.
Duplicate references share one asset. Asset names are generated from the
original file name with a numeric prefix; the original reference is retained in
the manifest for traceability.

## Limits

| Item | Limit |
|---|---:|
| Bundle file (compressed) | 256 MiB |
| Total uncompressed payload | 512 MiB |
| Assets | 100 |
| One asset | 25 MiB |
| Manifest | 1 MiB |
| Project payload | 64 MiB (native project limit) |

The limits are enforced on export and import. A bundle that exceeds them is
rejected with an explicit error.

## Import

Use **File → Import Project Bundle...**, select the bundle, and choose a
destination folder. AntennaDesk:

- validates the ZIP entry names, manifest format/version, file sizes, project
  payload, and each asset's SHA-256;
- rejects path traversal, absolute paths, backslashes, symlinks, encrypted
  entries, duplicate entries, unknown entries, unlisted assets, and size or
  checksum mismatches;
- creates a new folder named after the project (`Name (2)`, `Name (3)`, … if
  needed);
- extracts the assets, rewrites the project's image references to the new local
  absolute paths, and saves `project.antennadesk` in that folder;
- opens the imported project;
- reports missing image references, which remain in the project but are not
  available locally.

Import treats the bundle as untrusted data. It never calls `extractall`, never
runs bundle content, and never reads a manifest path outside the validated
`assets/` directory.

## Portability notes

- The exported bundle is self-contained. The imported project uses local
  absolute image paths; moving the imported folder breaks those paths, so export
  a new bundle before moving it again.
- The bundle does not include the solver binary, build reports, or external
  measurement CSVs. Measurements are already stored inside the project.
- Project bundles do not change the native `.antennadesk` format and do not add
  a schema migration.
