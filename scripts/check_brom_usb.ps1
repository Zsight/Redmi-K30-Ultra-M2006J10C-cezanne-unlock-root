[CmdletBinding()]
param()

$ErrorActionPreference = 'Continue'
$deviceIdPattern = '^USB\\VID_0E8D&PID_0003\\'
$registryRoot = 'HKLM:\SYSTEM\CurrentControlSet\Enum\USB\VID_0E8D&PID_0003'

Write-Output 'Read-only Windows BROM driver check'
Write-Output 'Target: USB\VID_0E8D&PID_0003'
Write-Output ''

$pnpDevices = @()
$pnpQuerySucceeded = $false
try {
    $pnpDevices = Get-PnpDevice -PresentOnly -ErrorAction Stop |
        Where-Object { $_.InstanceId -match $deviceIdPattern }
    $pnpQuerySucceeded = $true
}
catch {
    Write-Output "Get-PnpDevice unavailable: $($_.Exception.Message)"
}

if ($pnpDevices.Count -gt 0) {
    foreach ($deviceItem in $pnpDevices) {
        $service = ''
        try {
            $service = (Get-PnpDeviceProperty `
                -InstanceId $deviceItem.InstanceId `
                -KeyName 'DEVPKEY_Device_Service' `
                -ErrorAction Stop).Data
        }
        catch {
            $service = ''
        }
        [pscustomobject]@{
            Status = $deviceItem.Status
            Class = $deviceItem.Class
            FriendlyName = $deviceItem.FriendlyName
            InstanceId = $deviceItem.InstanceId
            Service = $service
        } | Format-List
    }
}
else {
    if ($pnpQuerySucceeded) {
        Write-Output 'No connected 0E8D:0003 device is currently reported by Get-PnpDevice.'
    }
    else {
        Write-Output 'Connected-state check was unavailable; registry history is shown below only.'
    }
}

Write-Output 'Historical registry instances:'
if (Test-Path -LiteralPath $registryRoot) {
    Get-ChildItem -LiteralPath $registryRoot -ErrorAction SilentlyContinue |
        ForEach-Object {
            $values = Get-ItemProperty -LiteralPath $_.PSPath -ErrorAction SilentlyContinue
            [pscustomobject]@{
                Instance = $_.PSChildName
                FriendlyName = $values.FriendlyName
                Service = $values.Service
                Driver = $values.Driver
                LocationInformation = $values.LocationInformation
            }
        } | Format-List
}
else {
    Write-Output 'No historical VID_0E8D&PID_0003 registry key exists.'
}

$services = @(
    Get-ChildItem -LiteralPath $registryRoot -ErrorAction SilentlyContinue |
        ForEach-Object {
            (Get-ItemProperty -LiteralPath $_.PSPath -ErrorAction SilentlyContinue).Service
        }
)

Write-Output ''
if ($services -contains 'WinUSB') {
    Write-Output 'RESULT: WinUSB binding observed. Continue only if the device is currently enumerated.'
}
elseif ($services -contains 'usbser') {
    Write-Output 'RESULT: usbser binding observed. Follow docs/zadig-win-usb.md before Kamakiri.'
}
else {
    Write-Output 'RESULT: No expected driver binding was observed. Enter BROM and repeat this check.'
}

