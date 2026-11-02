[CmdletBinding()]
param()

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Continue'

$projectRoot = Split-Path -Parent $PSScriptRoot
$adb = Join-Path $projectRoot 'platform-tools\adb.exe'
$fastboot = Join-Path $projectRoot 'platform-tools\fastboot.exe'
$logDir = Join-Path $projectRoot 'logs'
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$logPath = Join-Path $logDir "security_baseline_${timestamp}.txt"

if (-not (Test-Path -LiteralPath $adb)) {
    throw "adb not found: $adb"
}

$output = [System.Collections.Generic.List[string]]::new()

function Add-Line {
    param([string]$Text = '')
    $output.Add($Text)
}

function Invoke-Captured {
    param(
        [string]$Name,
        [string]$Command,
        [string[]]$Arguments
    )
    $started = Get-Date
    Add-Line "===== COMMAND ====="
    Add-Line "name=$Name"
    Add-Line "started_at=$($started.ToString('o'))"
    Add-Line "command=$Command $($Arguments -join ' ')"
    $stdout = & $Command @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    if ($null -ne $stdout) {
        $stdout | ForEach-Object { Add-Line $_.ToString() }
    }
    Add-Line "exit_code=$exitCode"
    Add-Line "finished_at=$((Get-Date).ToString('o'))"
    Add-Line
}

Add-Line "device=Redmi K30 Ultra / cezanne / M2006J10C"
Add-Line "collected_at=$((Get-Date).ToString('o'))"
Add-Line "mode=ROOTED_READ_ONLY_BASELINE"
Add-Line

Invoke-Captured 'adb_devices' $adb @('devices', '-l')
Invoke-Captured 'adb_version' $adb @('version')
Invoke-Captured 'fastboot_version' $fastboot @('--version')
Invoke-Captured 'root_id' $adb @('shell', "su -c 'id'")
Invoke-Captured 'magisk_version' $adb @('shell', "su -c 'magisk -v'")
Invoke-Captured 'su_version' $adb @('shell', 'su -v')

$properties = @(
    'ro.product.device',
    'ro.product.model',
    'ro.build.version.release',
    'ro.build.version.incremental',
    'ro.build.fingerprint',
    'ro.boot.slot_suffix',
    'ro.boot.verifiedbootstate',
    'ro.boot.flash.locked',
    'ro.boot.vbmeta.device_state',
    'ro.boot.veritymode',
    'sys.boot_completed'
)

foreach ($prop in $properties) {
    Invoke-Captured "prop_$prop" $adb @('shell', 'getprop', $prop)
}

Invoke-Captured 'block_by_name' $adb @(
    'shell',
    "su -c 'ls -l /dev/block/by-name'"
)
Invoke-Captured 'magisk_path' $adb @(
    'shell',
    "su -c 'magisk --path'"
)
Invoke-Captured 'magisk_modules' $adb @(
    'shell',
    "su -c 'ls -la /data/adb/modules'"
)

Add-Line "===== BACKUP HASHES ====="
$backupFiles = @(
    'boot_analysis\boot_readonly.img',
    'boot_analysis\magisk_patched-31100_2ZuI2.img',
    'boot_analysis\seccfg_readonly.img',
    'boot_analysis\seccfg_after_unlock.img',
    'boot_analysis\vbmeta_readonly.img',
    'lk_analysis\lk_readonly.img'
)

foreach ($relativePath in $backupFiles) {
    $path = Join-Path $projectRoot $relativePath
    if (Test-Path -LiteralPath $path) {
        $item = Get-Item -LiteralPath $path
        $hash = Get-FileHash -LiteralPath $path -Algorithm SHA256
        Add-Line "$relativePath size=$($item.Length) sha256=$($hash.Hash)"
    }
    else {
        Add-Line "$relativePath MISSING"
    }
}
Add-Line

Add-Line "===== FIRMWARE DOWNLOAD STATUS ====="
$downloadDir = Join-Path $projectRoot 'firmware\downloads'
Get-ChildItem -LiteralPath $downloadDir -File -ErrorAction SilentlyContinue |
    Sort-Object Name |
    ForEach-Object {
        Add-Line "$($_.Name) size=$($_.Length) modified=$($_.LastWriteTime.ToString('o'))"
    }

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($logPath, [string]::Join(
    [Environment]::NewLine,
    $output
), $utf8NoBom)

Write-Output "LOG_PATH=$logPath"
