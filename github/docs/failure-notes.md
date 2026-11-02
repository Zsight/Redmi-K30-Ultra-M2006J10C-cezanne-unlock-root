# Failure notes and discarded assumptions

These notes exist so others do not repeat the same dead ends.

## Fastboot unlock is not an unsigned bypass

The LK `oem unlock` / `flashing unlock` path checks a 0x100-byte
Xiaomi-signed token before changing the lock state. No unsigned Fastboot
handler was found.

## `adb reboot edl` did not expose BROM

The reboot request was accepted by adbd, but no `0E8D:0003` device appeared.
The phone returned to Android. Do not treat an accepted reboot command as
proof that EDL/BROM was entered.

## `usbser` is insufficient for this exploit

The BROM appeared as:

```text
0E8D:0003
```

Windows sometimes bound it to `usbser` and exposed COM7. That was sufficient
for read-only handshake and HW-code queries, but the Kamakiri trigger needed a
vendor control transfer that the COM path could not provide.

The host was changed to bind only `USB\VID_0E8D&PID_0003` to WinUSB.

## The old Kamakiri mode failed

With `--ptype kamakiri`, several attempts reached:

```text
Done sending payload...
```

but then failed with a USB pipe error and no `A1A2A3A4` ACK. Updating the
payload did not solve it. The older mode is not the verified path for this
firmware.

`Kamakiri2` succeeded with the same MT6885-family payload.

## Holding hardware buttons does not keep BROM alive

BROM has an internal USB download timeout. Releasing or holding Volume Up/Down
after enumeration does not control that timer. Holding the buttons after a
timeout can make the subsequent boot enter Fastboot.

## `fastboot boot` was not usable

The patched image was transferred, but the device disconnected during
`Booting` and returned a USB read failure. This did not write a partition.
Persistent boot flashing was a separate, explicitly confirmed step.

## File size alone is not firmware validation

A reconstructed Fastboot archive reached the exact expected size:

```text
5,675,852,185 bytes
```

but its MD5 did not match the official value. The archive was discarded.
Always verify the official digest; Do not use a same-size file.

## Do not write seccfg without a recovery path

`seccfg` is not a harmless text/configuration file. A bad hash, interrupted
write, or V4 generation mismatch can prevent normal boot. Preserve the original
image and validate the read-back before rebooting.

