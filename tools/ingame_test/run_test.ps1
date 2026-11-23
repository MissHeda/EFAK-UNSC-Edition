# Unattended lid test: its own windowed Arma (own profile, input locked), every kit in a ground
# holder, the lids opened by script, pictures taken from outside whenever the RPT says SHOT.
#
#   hemtt build
#   powershell -ExecutionPolicy Bypass -File tools\ingame_test\run_test.ps1
#
# Another running Arma is left alone. Pictures land in tools\ingame_test\out\shots (not in git).
param(
  [string]$Arma = 'C:\SteamLibrary\steamapps\common\Arma 3\arma3_x64.exe',
  [string]$Workshop = 'C:\SteamLibrary\steamapps\workshop\content\107410',
  [string]$Python = 'python',
  [string]$Mission = 'EFKU_Lids.Stratis',
  # further Workshop items to load, e.g. 3389065865 (The Cole Protocol) for EFKU_TCPSize.VR
  [string[]]$Extra = @()
)
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Repo = (Resolve-Path (Join-Path $Here '..\..')).Path
$S = Join-Path $Here 'out'
$prof = Join-Path $S 'arma_profile'
$shots = Join-Path $S 'shots'
New-Item -ItemType Directory -Force $prof, $shots, (Join-Path $S 'mod\addons') | Out-Null
Get-ChildItem $prof -Filter *.rpt -ErrorAction SilentlyContinue | ForEach-Object { try { Remove-Item $_.FullName -Force -ErrorAction Stop } catch {} }
Get-ChildItem $shots -Filter *.png -ErrorAction SilentlyContinue | Remove-Item -Force
& $Python (Join-Path $Here 'make_pbo.py') (Join-Path $Here 'mission') (Join-Path $S 'mod\addons\efku_test.pbo') 'z\efku_test'

Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class W {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
[W]::SetProcessDPIAware() | Out-Null
Add-Type -AssemblyName System.Drawing

$mods = @("$Workshop\450814997", "$Workshop\463939057", "$Workshop\3809430149", "$Workshop\3812667721",
  (Join-Path $Repo '.hemttout\build'), (Join-Path $S 'mod')) + ($Extra | ForEach-Object { "$Workshop\$_" })
$mods = $mods -join ';'
$argv = @('-window', '-noPause', '-skipIntro', '-noSplash', '-showScriptErrors', '-x=1600', '-y=900',
  '-name=efkutest', "`"-profiles=$prof`"", "`"-mod=$mods`"",
  "`"-init=playMission['','\z\efku_test\missions\$Mission']`"")
$p = Start-Process $Arma -ArgumentList $argv -PassThru
"PID $($p.Id)"

function Shot($name) {
  $p.Refresh()
  $h = $p.MainWindowHandle
  $r = New-Object W+RECT
  [W]::GetClientRect($h, [ref]$r) | Out-Null
  $w = $r.R - $r.L; $hh = $r.B - $r.T
  if ($w -le 0) { "no window for $name"; return }
  $bmp = New-Object System.Drawing.Bitmap $w, $hh
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $dc = $g.GetHdc()
  [W]::PrintWindow($h, $dc, 3) | Out-Null
  $g.ReleaseHdc($dc); $g.Dispose()
  $bmp.Save((Join-Path $shots "$name.png"), [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  "shot $name ${w}x${hh}"
}

$seen = 0
$deadline = (Get-Date).AddSeconds(420)
while ((Get-Date) -lt $deadline -and -not $p.HasExited) {
  Start-Sleep -Milliseconds 400
  $rpt = Get-ChildItem $prof -Filter *.rpt -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
  if (-not $rpt) { continue }
  $lines = @(Get-Content $rpt.FullName -ErrorAction SilentlyContinue | Where-Object { $_ -match 'EFKUTEST|Error' })
  for ($i = $seen; $i -lt $lines.Count; $i++) {
    $l = $lines[$i]
    $l
    if ($l -match 'EFKUTEST SHOT ([A-Za-z0-9_]+)') { Shot $Matches[1] }
    if ($l -match 'EFKUTEST DONE') { $deadline = Get-Date }
  }
  $seen = $lines.Count
}
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force; "stopped $($p.Id)" }
$p.WaitForExit(15000) | Out-Null
