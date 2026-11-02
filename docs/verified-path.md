# Verified cezanne unlock and root path

## Scope

This path was verified on:

```text
Redmi K30 Ultra / M2006J10C / cezanne
MT6889Z / Dimensity 1000+
MIUI V14.0.5.0.SJNCNXM
Android 12
UFS THGJFCT2T84BAK
```

It is not a general MTK procedure.

## Prerequisites

- Exact official `V14.0.5.0.SJNCNXM` firmware metadata and component package.
- A full backup of the original boot chain and `seccfg`.
- Windows Platform Tools and a verified WinUSB/libusb backend for
  `0E8D:0003`.
- `mtkclient` source and its `mt6885_payload.bin`.
- A reliable physical BROM entry sequence for this device.

## 1. Record the initial state

```text
adb devices -l
adb shell getprop ro.product.device
adb shell getprop ro.build.version.incremental
adb shell getprop ro.boot.verifiedbootstate
adb shell getprop ro.boot.flash.locked
```

Expected for this target before unlocking:

```text
cezanne
V14.0.5.0.SJNCNXM
green
1
```

## 2. Back up before writing

The important items are:

- original `boot`;
- `seccfg`;
- `vbmeta`, `vbmeta_system`, `vbmeta_vendor`;
- `lk`, `lk2`;
- `dtbo`;
- Preloader A/B LUNs;
- primary and backup GPT regions;
- exact official firmware metadata and hashes.

Do not commit these images to a public repository. Store them offline and
record their SHA-256 hashes in a private recovery log.

## 3. Bind only the BROM USB ID

The verified Windows host setup bound only:

```text
USB\VID_0E8D&PID_0003
```

to WinUSB. It did not bind the phone's Android/Fastboot IDs and did not touch
other USB devices.

The checked result in the Windows device registry was:

```text
Service=WinUSB
```

## 4. Enter BROM

The working sequence was:

1. Request or perform a normal power-off.
2. Wait for the screen to go black.
3. Disconnect USB.
4. Hold Volume Up and Volume Down.
5. Reconnect USB while holding both buttons.
6. Watch for `0E8D:0003` enumeration.
7. Release the buttons after BROM is enumerated.

BROM has a finite USB download timeout. Holding buttons does not extend it.
If it expires, the following boot path can end at Fastboot.

## 5. Validate stage1

The verified path used `Kamakiri2`, not the older `Kamakiri` mode:

```text
mtkclient --ptype kamakiri2
```

Required observations:

```text
hwcode=0x0816
target_config=0x000000E7
stage1_ack=A1A2A3A4
stage1_second_handshake=OK
```

Do not continue merely because a payload was sent. Both the ACK and the second
handshake must succeed.

## 6. Read before changing state

The verified DA session successfully read:

- UFS identity and capacity;
- GPT;
- `seccfg`;
- `boot`;
- `vbmeta`;
- `lk`.

The target `seccfg` was V4:

```text
magic=0x4D4D4D4D
version=4
size=0x3C
lock_state=2
dm_verity_state=0
```

The stored hash is not a plain truncated SHA-256 and must be generated through
the matching SEJ/HACC path.

## 7. seccfg unlock

The verified command was:

```text
mtkclient da seccfg unlock --ptype kamakiri2
```

It reported:

```text
SecCfgV4 - hwtype found: V4
Done: 0x200/0x200
Successfully wrote seccfg
```

A full read-back must show `lock_state=3` before rebooting.

After reboot, independent checks must show:

```text
fastboot getvar unlocked  -> unlocked: yes
fastboot oem lks          -> lks = 0
ro.boot.flash.locked      -> 0
ro.boot.vbmeta.device_state -> unlocked
```

## 8. Magisk boot

Use the exact current `boot` image extracted from the device and the official
Magisk release. Do not use a boot image from another firmware version.

The verified sequence was:

1. Patch `boot_readonly.img` with Magisk.
2. Verify the patched boot header and ramdisk markers.
3. Temporarily test if supported.
4. If temporary boot is not supported, explicitly authorize a persistent
   `fastboot flash boot` after preserving the original boot.
5. Reboot and verify:

```text
su -v
su -c id
```

Expected:

```text
31.1:MAGISKSU
uid=0(root) context=u:r:magisk:s0
```

## Result

The device booted Android with:

```text
Bootloader unlocked
Verified Boot state: orange
MagiskSU: 31.1
Root UID: 0
```

