[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
$adb = Join-Path $root 'platform-tools\adb.exe'
$fastboot = Join-Path $root 'platform-tools\fastboot.exe'

function Show-Check {
    param([string]$Name, [bool]$Ok, [string]$Detail = '')
    $state = if ($Ok) { 'OK' } else { 'MISSING/ERROR' }
    Write-Output ("{0,-28} {1} {2}" -f $Name, $state, $Detail)
}

Show-Check 'Windows' ($env:OS -eq 'Windows_NT') $env:OS
Show-Check '64-bit PowerShell' ([Environment]::Is64BitProcess)
Show-Check 'adb.exe' (Test-Path -LiteralPath $adb) $adb
Show-Check 'fastboot.exe' (Test-Path -LiteralPath $fastboot) $fastboot

$python = Get-Command python.exe -ErrorAction SilentlyContinue
Show-Check 'Python' ($null -ne $python) $(if ($python) { $python.Source } else { '' })
if ($python) {
    $version = & python.exe --version 2>&1
    Write-Output "Python version: $version"
}

$git = Get-Command git.exe -ErrorAction SilentlyContinue
Show-Check 'Git' ($null -ne $git) $(if ($git) { $git.Source } else { '' })

$driveRoot = [System.IO.Path]::GetPathRoot($root)
$driveName = $driveRoot.Substring(0, 1)
$drive = Get-PSDrive -Name $driveName -ErrorAction SilentlyContinue
if ($drive) {
    Write-Output ("Free space on workspace drive: {0:N1} GiB" -f ($drive.Free / 1GB))
}

if (Test-Path -LiteralPath $adb) {
    Write-Output ''
    Write-Output 'ADB devices:'
    & $adb devices -l
    Write-Output "adb_exit_code=$LASTEXITCODE"
}

Write-Output ''
Write-Output 'Read README.md and docs/quick-start.md before issuing any device-changing command.'

