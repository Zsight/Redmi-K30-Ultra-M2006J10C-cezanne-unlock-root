# Windows environment

## Recommended host

- Windows 10/11 x64.
- Administrator access only when binding a USB driver or installing a system
  prerequisite.
- Do not use a shared or untrusted USB driver installation.

## Required tools

- Android Platform Tools, placed at `platform-tools\adb.exe` and
  `platform-tools\fastboot.exe`.
- 64-bit Python 3.11 for the analysis scripts.
- Git for version control.
- The reviewed `mtkclient` source and its Python dependencies for DA/BROM work.
- Zadig/libwdi only for narrow BROM WinUSB binding as described in the verified
  path.

Record tool versions and hashes before running device commands.

## USB driver rule

Bind only:

```text
USB\VID_0E8D&PID_0003
```

Never use a bulk “replace all drivers” operation. Do not touch the normal
Android/Fastboot VID or unrelated Bluetooth, camera, mouse, or hub devices.

## USB debugging

1. Enable Developer options.
2. Enable USB debugging.
3. Connect the data cable.
4. Approve the RSA fingerprint prompt.
5. Verify:

```powershell
.\platform-tools\adb.exe devices -l
```

The result must show state `device`, not `unauthorized`, before any command
is issued.

