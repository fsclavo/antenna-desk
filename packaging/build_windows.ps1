# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Build the Windows onedir bundle, portable zip, and NSIS installer.
#
# Usage (PowerShell):
#   packaging\build_windows.ps1
#   $env:NEC2C = "C:\path\to\nec2c.exe"; packaging\build_windows.ps1
#
# Requirements:
#   - NSIS (makensis.exe), for example: choco install nsis -y
#
# Optional Authenticode signing:
#   $env:WINDOWS_SIGN_CERT = "C:\path\to\certificate.pfx"
#   $env:WINDOWS_SIGN_PASSWORD = "..."
#   $env:WINDOWS_TIMESTAMP_URL = "http://timestamp.digicert.com"

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$Nec2c = if ($env:NEC2C) { $env:NEC2C } else { Join-Path $Root "spikes\phase0\build\nec2c.exe" }
if (-not (Test-Path $Nec2c)) {
  throw "nec2c.exe not found at $Nec2c. Build it with spikes/phase0/scripts/build_nec2c_windows.sh or set NEC2C."
}

$Version = (uv run python -c "import antennadesk; print(antennadesk.__version__)").Trim()
$DistRoot = Join-Path $Root "build\pyinstaller-dist"
$Bundle = Join-Path $DistRoot "AntennaDesk"
$DistDir = Join-Path $Root "dist"
$Zip = Join-Path $DistDir "AntennaDesk-$Version-windows-x86_64.zip"
$Setup = Join-Path $DistDir "AntennaDesk-$Version-windows-x86_64-setup.exe"
$Icon = Join-Path $Root "packaging\antennadesk.ico"
$Nsi = Join-Path $Root "packaging\windows\antennadesk.nsi"

function Get-MakeNsis {
  $Command = Get-Command makensis.exe -ErrorAction SilentlyContinue
  if ($Command) {
    return $Command.Source
  }
  $Candidates = @(
    (Join-Path ${env:ProgramFiles(x86)} "NSIS\makensis.exe"),
    (Join-Path $env:ProgramFiles "NSIS\makensis.exe")
  )
  foreach ($Candidate in $Candidates) {
    if ($Candidate -and (Test-Path $Candidate)) {
      return $Candidate
    }
  }
  throw "makensis.exe not found. Install NSIS (for example: choco install nsis -y) or add it to PATH."
}

function Sign-Binary {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$SignTool,
    [Parameter(Mandatory = $true)][string]$TimestampUrl
  )
  & $SignTool sign /f $env:WINDOWS_SIGN_CERT /p $env:WINDOWS_SIGN_PASSWORD `
    /tr $TimestampUrl /td sha256 $Path
  if ($LASTEXITCODE -ne 0) {
    throw "signtool failed with exit code $LASTEXITCODE for $Path"
  }
}

Write-Host "Building AntennaDesk $Version for Windows"
Remove-Item -Recurse -Force $DistRoot -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $DistRoot | Out-Null
New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

uv run --group packaging pyinstaller `
  packaging\antennadesk.spec `
  --noconfirm `
  --clean `
  --distpath $DistRoot `
  --workpath (Join-Path $Root "build\pyinstaller")

$Executable = Join-Path $Bundle "AntennaDesk.exe"
if (-not (Test-Path $Executable)) {
  throw "PyInstaller did not produce $Executable"
}
Copy-Item $Nec2c (Join-Path $Bundle "nec2c.exe")

uv run python packaging\collect_bundle_licenses.py $Bundle
if ($LASTEXITCODE -ne 0) { throw "license collection failed" }
uv run python packaging\check_bundle_licenses.py $Bundle
if ($LASTEXITCODE -ne 0) { throw "license audit failed" }

$SignTool = $null
$TimestampUrl = if ($env:WINDOWS_TIMESTAMP_URL) { $env:WINDOWS_TIMESTAMP_URL } else { "http://timestamp.digicert.com" }
if ($env:WINDOWS_SIGN_CERT) {
  $SignTool = (Get-Command signtool.exe -ErrorAction SilentlyContinue).Source
  if (-not $SignTool) {
    $KitsRoot = Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\bin"
    $SignTool = Get-ChildItem -Path $KitsRoot -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue |
      Where-Object { $_.FullName -match '\\x64\\signtool\.exe$' } |
      Sort-Object FullName -Descending |
      Select-Object -First 1 -ExpandProperty FullName
  }
  if (-not $SignTool) {
    throw "WINDOWS_SIGN_CERT is set but signtool.exe could not be found."
  }
  foreach ($Binary in @($Executable, (Join-Path $Bundle "nec2c.exe"))) {
    Sign-Binary -Path $Binary -SignTool $SignTool -TimestampUrl $TimestampUrl
  }
}

Compress-Archive -Path (Join-Path $Bundle "*") -DestinationPath $Zip -Force
$Hash = (Get-FileHash -Algorithm SHA256 $Zip).Hash.ToLower()
"$Hash  $(Split-Path -Leaf $Zip)" | Set-Content -Encoding ascii "$Zip.sha256"
Write-Host "Created $Zip"

$MakeNsis = Get-MakeNsis
Write-Host "Building Windows installer with $MakeNsis"
& $MakeNsis `
  "/DVERSION=$Version" `
  "/DSRCDIR=$Bundle" `
  "/DOUTFILE=$Setup" `
  "/DICONFILE=$Icon" `
  $Nsi
if ($LASTEXITCODE -ne 0) {
  throw "makensis failed with exit code $LASTEXITCODE"
}
if (-not (Test-Path $Setup)) {
  throw "NSIS did not produce $Setup"
}

if ($env:WINDOWS_SIGN_CERT) {
  Sign-Binary -Path $Setup -SignTool $SignTool -TimestampUrl $TimestampUrl
}

$Hash = (Get-FileHash -Algorithm SHA256 $Setup).Hash.ToLower()
"$Hash  $(Split-Path -Leaf $Setup)" | Set-Content -Encoding ascii "$Setup.sha256"
Write-Host "Created $Setup"
