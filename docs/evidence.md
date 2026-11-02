# Evidence summary

## BROM and exploit evidence

```text
hwcode=0x0816
hwver=0x0000
target_config=0x000000E7
exploit=kamakiri2
stage1_ack=A1A2A3A4
stage1_second_handshake=OK
```

## DA evidence

```text
UFS=THGJFCT2T84BAK
GPT=read successfully
DA stage1=loaded
DA stage2=loaded
seccfg hardware type=V4
```

## seccfg evidence

```text
magic=0x4D4D4D4D
version=4
size=0x3C
lock_state before=2
lock_state after=3
dm_verity_state=0
```

## Final status evidence

```text
fastboot unlocked=yes
fastboot oem lks=0
ro.boot.flash.locked=0
ro.boot.vbmeta.device_state=unlocked
ro.boot.verifiedbootstate=orange
sys.boot_completed=1
```

```text
su -v      -> 31.1:MAGISKSU
su -c id   -> uid=0(root) context=u:r:magisk:s0
```

## Private data

The public repository should omit:

- MEID;
- SOCID;
- UFS serial/CID;
- IMEI;
- serial numbers;
- local Windows paths containing a username.

