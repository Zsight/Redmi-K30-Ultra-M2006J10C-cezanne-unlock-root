# Triage matrix

| Symptom | Likely cause | Safe next action |
|---|---|---|
| Fastboot reports `unlocked: no` and `oem lks = 1` | LK lock state is still not 3; ordinary Fastboot unlock needs a signed token | Stop. Do not issue repeated unlock commands. Verify `seccfg` and the research path first. |
| `adb reboot edl` succeeds but no `0E8D:0003` appears | This platform did not expose BROM from that reboot reason | Do not assume EDL succeeded. Use the verified physical BROM entry method or stop. |
| BROM appears as COM7 but mtkclient cannot open it | Windows bound `0E8D:0003` to `usbser`; Kamakiri needs a WinUSB/libusb path | Follow [`zadig-win-usb.md`](zadig-win-usb.md) and bind only `USB\VID_0E8D&PID_0003` to WinUSB. |
| `fastboot boot patched.img` disconnects during `Booting` | This implementation rejected or reset the temporary boot path | No partition was written. Do not repeat blindly; use persistent flashing only with a validated image and explicit recovery plan. |
| Stage1 reports `Done sending payload` but no ACK | The Kamakiri variant did not execute; an ACK is mandatory | Do not continue to DA. Try only a source-supported variant such as the verified `Kamakiri2` path after review. |
| `A1A2A3A4` ACK appears and the second handshake succeeds | Stage1 reached its patched command handler | Proceed only with the next explicitly scoped operation. |
| BROM resets to Fastboot while buttons remain held | BROM's USB download timeout expired | Button state does not extend the timeout. Power-cycle and repeat only if a watcher is ready. |
| DA reports `Authentication required` | The BROM security bypass did not establish a usable DA session | Stop. Do not attempt writes or use an unrelated authentication file. |
| `seccfg` hash does not match a plain SHA-256 | The V4 hash is protected by the MTK SEJ/HACC path | Do not patch offsets manually. Generate and verify the replacement through the matching hardware path. |
| Firmware file has the exact size but MD5 fails | The download is incomplete, sparse, or incorrectly reconstructed | Discard the file. A matching size is not integrity validation. |
| Root command returns `Permission denied` | Magisk is installed but the shell UID has not been granted | Grant the intended UID in Magisk Superuser, or verify with an app that has been explicitly authorized. |
| `su -v` works but `su -c id` fails | MagiskSU is present, but the caller is not granted root | This is a policy issue, not a boot-image failure. |
| Android boots with Verified Boot `orange` | Bootloader is unlocked and the boot chain is modified | This is expected; do not relock without restoring and validating the full official chain. |

## Stop conditions

Stop immediately if:

- the expected HW code or target config changes;
- stage1 ACK is missing;
- DA authentication state is unexpected;
- a partition hash or GPT mapping is ambiguous;
- the phone enters an undocumented mode;
- a write is proposed without a matching backup and recovery route.

