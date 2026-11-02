# Toolchain

## Verified versions

| Tool | Verified version |
|---|---|
| Platform Tools | ADB/Fastboot 37.0.1 |
| Python | 3.11.9 x64 |
| pyusb | 1.3.1 |
| bundled libusb | 1.0.24 |
| mtkclient reviewed commit | `118a000a83ea31c4f427fe5225abfe964546e05e` |
| Magisk | 31.1 (31100) |
| Zadig | 2.9 |

## Required layout

The analysis scripts expect:

```text
<repo>/
  platform-tools/
  tools/
    research/
      mtkclient/
  scripts/
```

If mtkclient is kept elsewhere, set:

```powershell
$env:MTKCLIENT_ROOT = "D:\path\to\mtkclient"
```

The public repository does not vendor mtkclient or its binaries.

`scripts/check_environment.ps1` checks the expected local layout and Python
modules. `scripts/check_brom_usb.ps1` is a read-only check of the current
`0E8D:0003` Windows binding.

## Official sources

- Android Platform Tools: `https://developer.android.com/tools/releases/platform-tools`
- Python: `https://www.python.org/downloads/`
- Git: `https://git-scm.com/downloads`
- mtkclient: `https://github.com/bkerler/mtkclient`
- Zadig/libwdi: `https://zadig.akeo.ie/`
- Magisk: `https://github.com/topjohnwu/Magisk/releases`

## Python dependencies

Install `pyusb` and `pyserial` into the Python environment used to run the
scripts:

```powershell
python -m pip install pyusb pyserial
```

mtkclient has its own dependency set; review and install its requirements in a
separate virtual environment where possible.

## License

Do not copy mtkclient source or binaries into a public repository without
reviewing its GPLv3 obligations. Link to the upstream source and pin the
reviewed commit instead.

