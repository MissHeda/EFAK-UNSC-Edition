# Builds the signed release and uploads it to the Workshop item as an update.
#
#   powershell -ExecutionPolicy Bypass -File tools\publish.ps1 -ChangeNote "What changed"
#
# Steam must be running and logged in to the account that owns the item. -DryRun builds and
# unpacks, but uploads nothing.
param(
  [string]$ChangeNote = '',
  [string]$Id = '3845590963',
  [string]$Publisher = 'D:\Steam\steamapps\common\Arma 3 Tools\Publisher\PublisherCmd.exe',
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$Repo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $Repo

$v = Get-Content 'addons\main\script_version.hpp' -Raw
$part = { param($n) [regex]::Match($v, "#define\s+$n\s+(\d+)").Groups[1].Value }
$ver = '{0}.{1}.{2}' -f (& $part 'MAJOR'), (& $part 'MINOR'), (& $part 'PATCH')
if ($ver -notmatch '^\d+\.\d+\.\d+$') { throw "Could not read the version: $ver" }
if ($ChangeNote -eq '') { $ChangeNote = "Update $ver" }
"Version $ver"

if (-not (Test-Path $Publisher)) { throw "PublisherCmd not found: $Publisher" }
if (-not $DryRun -and -not (Get-Process steam -ErrorAction SilentlyContinue)) { throw 'Steam is not running - start it and log in first.' }

hemtt release
if ($LASTEXITCODE -ne 0) { throw "hemtt release failed ($LASTEXITCODE)" }

$zip = Join-Path $Repo "releases\efku-$ver.zip"
if (-not (Test-Path $zip)) { throw "No release zip: $zip" }
$dir = Join-Path $Repo "releases\efku-$ver"
if (Test-Path $dir) { Remove-Item $dir -Recurse -Force }
Expand-Archive $zip $dir
$mod = Join-Path $dir '@efku'
"Content: $mod"
Get-ChildItem $mod -Recurse -File | Measure-Object Length -Sum | ForEach-Object { '{0} files, {1:N1} MB' -f $_.Count, ($_.Sum / 1MB) }

if ($DryRun) { 'Dry run - nothing uploaded.'; exit 0 }

"Uploading to Workshop item $Id ..."
# Run from the Publisher's own folder: Steam reads steam_appid.txt from the working directory, and
# from anywhere else the upload is refused (Steam error 15, access denied).
Push-Location (Split-Path $Publisher)
try {
  & $Publisher update "/id:$Id" "/changeNote:$ChangeNote" "/path:$mod" /nologo
  $code = $LASTEXITCODE
} finally { Pop-Location }
if ($code -ne 0) { throw "PublisherCmd failed ($code)" }
"Done: https://steamcommunity.com/sharedfiles/filedetails/?id=$Id"
