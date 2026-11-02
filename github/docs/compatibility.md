# Compatibility

## Tested matrix

| Item | Tested value |
|---|---|
| Model | Redmi K30 Ultra M2006J10C |
| Codename | cezanne |
| SoC | MT6889Z / Dimensity 1000+ |
| BROM HW code | `0x0816` |
| BROM target config | `0x000000E7` |
| Android | 12 |
| MIUI | `V14.0.5.0.SJNCNXM` |
| Build | `SP1A.210812.016` |
| Active LK | matched official `lk.img` |

## Explicitly not claimed

This repository does not claim compatibility with:

- another Redmi K30 model;
- another MT689x/MT688x device;
- a different MIUI/Android build;
- a modified boot chain;
- a different eMMC/UFS layout.

The fact that two devices share `hwcode=0x0816` does not prove that their BROM
addresses, seccfg hash method, preloader layout, LK behavior, or AVB keys are
identical.

## Required revalidation

For any different firmware or device, repeat the read-only stage:

1. Verify device, model, build, and HW code.
2. Compare the active LK with the claimed firmware.
3. Read the GPT and verify partition names and addresses.
4. Read seccfg and identify its structure and lock state.
5. Verify the boot and vbmeta format.
6. Confirm the exact BROM target configuration.

