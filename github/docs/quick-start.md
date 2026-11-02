# Quick start

## Goal of the first session

The first session is read-only. Do not unlock, flash, erase, format, or start a
DA write merely because the environment is ready.

## 1. Prepare the folder

The workspace should look like this:

```text
cezanne-unlock-research/
  platform-tools/
    adb.exe
    fastboot.exe
  scripts/
  docs/
  logs/
  device_info/
  firmware/
  boot_analysis/
  lk_analysis/
  preloader_analysis/
```

Use the Android Platform Tools package that matches the host architecture.
Do not mix unrelated ADB/fastboot versions.

## 2. Prepare Windows

Install or verify:

- Windows 10/11 x64;
- 64-bit Python 3.11;
- Git;
- PowerShell 7 or Windows PowerShell 5.1;
- current Codex/CLI agent if AI assistance is desired;
- a stable USB data cable.

The environment check is:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_environment.ps1
```

## 3. Prepare the phone

1. Back up personal data separately.
2. Charge the phone above 50%.
3. Enable Developer options.
4. Enable USB debugging.
5. Connect USB and approve the RSA fingerprint prompt.
6. Run `adb devices -l` and require state `device`.

Expected target values:

```text
product:cezanne
model:M2006J10C
ro.build.version.incremental=V14.0.5.0.SJNCNXM
```

## 4. Read-only baseline

Collect:

```text
adb devices -l
adb shell getprop ro.product.device
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.version.incremental
adb shell getprop ro.boot.slot_suffix
adb shell getprop ro.boot.verifiedbootstate
adb shell getprop ro.boot.flash.locked
```

If Root already exists, optionally collect:

```text
adb shell su -c id
adb shell su -v
```

Then collect the partition symlink map:

```powershell
.\platform-tools\adb.exe shell "su -c 'ls -l /dev/block/by-name'"
```

If root is not available, record the permission error and stop. Do not attempt
privilege escalation in the baseline phase.

## 5. Back up before any write

At minimum:

- original boot;
- seccfg;
- vbmeta and vendor/system vbmeta;
- lk/lk2;
- dtbo;
- Preloader A/B;
- GPT head and backup tail;
- exact official firmware metadata and checksum.

Store copies offline. Save SHA-256 values in a private manifest. Never put
`seccfg`, signed images, or user-identifying logs in a public repository.

## 6. Decide whether to continue

Do not continue if:

- the model/build is different;
- BROM HW code is not `0x0816`;
- target config differs from `0x000000E7`;
- stage1 ACK is missing;
- a backup hash is missing;
- the recovery route is unknown.

The verified technical path is in [`verified-path.md`](verified-path.md).

