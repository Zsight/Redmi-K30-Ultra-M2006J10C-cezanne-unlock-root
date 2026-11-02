# Agent instructions

This workspace contains evidence from a device-specific bootloader and Root
research project. Treat device integrity and user data as higher priority than
task completion.

## Required reading order

1. `README.md`
2. `docs/compatibility.md`
3. `docs/quick-start.md`
4. `docs/verified-path.md`
5. `docs/failure-notes.md`
6. `docs/triage.md`
7. `docs/recovery.md`

## Device gate

Do not proceed with device-changing work unless the phone reports all of:

```text
ro.product.device=cezanne
ro.product.model=M2006J10C
ro.build.version.incremental=V14.0.5.0.SJNCNXM
```

and the observed SoC HW code is `0x0816`.

If any value differs, stop and report the mismatch. Do not substitute another
firmware, boot image, payload, partition offset, or seccfg image.

## Authorization gate

Before an operation that can write persistent state, the user must explicitly
name the scope. Examples include:

- uploading and executing a BROM stage1 payload;
- starting a DA session;
- writing `seccfg`;
- flashing `boot`;
- erasing or formatting a partition;
- entering RPMB operations;
- locking or unlocking the bootloader.

An earlier broad statement does not authorize an unrelated destructive action.
Explain the exact target, expected result, backup, recovery path, and risk
before requesting confirmation.

## Default operating mode

- Start read-only.
- Use PowerShell on Windows.
- Prefer `rg` for searching.
- Save command, timestamp, exit code, stdout and stderr under `logs/`.
- Distinguish verified facts, reasoned inference, and unknown items.
- Never hide a failed command or reinterpret a missing ACK as success.
- Do not use Fastboot unlock, flash, erase, format, RPMB, or seccfg writes
  merely because a tutorial says they work on another MTK device.

## Physical actions

The agent cannot perform phone button sequences or inspect the physical screen
unless the user reports the state. When BROM is detected, explicitly tell the
user to release the volume keys; holding them does not extend the BROM timeout.

After a reboot, verify ADB or Fastboot separately. Never assume Android booted
from the absence of an error message.

## Backup gate

Before a persistent boot-chain write, verify:

- exact model and build;
- original boot backup exists and its hash is recorded;
- seccfg backup exists;
- GPT and partition mapping are known;
- a restore command and recovery route are available;
- the image to be written is the intended one and its hash is recorded.

## Privacy

Do not send or publish IMEI, MEID, SOCID, UFS serial/CID, serial numbers,
Windows usernames, local absolute paths, or unredacted raw logs.

## Completion rule

An operation is complete only after an independent read-back or runtime check.
For example, do not call stage1 successful unless `A1A2A3A4` and the second
handshake are observed. Do not call Root successful unless `su -c id` returns
UID 0.

