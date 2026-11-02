# Recovery notes

## Minimal boot recovery

If Android fails to boot after installing Magisk, and Fastboot is available:

```text
fastboot flash boot original-boot.img
fastboot reboot
```

Use only the original boot image matching the current build.

## Boot-chain backups

Keep an offline copy of:

- original boot;
- patched boot;
- original and modified seccfg;
- vbmeta and vendor/system vbmeta;
- lk and lk2;
- dtbo;
- Preloader A/B LUNs;
- GPT head and backup tail.

Do not publish signed firmware images in a public Git repository.

## seccfg recovery

Restore seccfg only with a verified BROM/DA session using the exact partition
layout and a matching backup. Do not guess offsets or use another model's
seccfg.

## Relocking

Do not run a lock command while Android, boot, vbmeta, or seccfg are in mixed
states. Relocking can make an otherwise recoverable device unbootable.

## User data

The boot-chain backup is not a user-data backup. It does not protect photos,
application data, or the dynamic `super` partition. Perform a separate
user-approved data backup if needed.

