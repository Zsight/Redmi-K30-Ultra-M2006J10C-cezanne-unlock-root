#!/usr/bin/env python3
"""Read-only USB enumeration diagnostic for the cezanne research workspace."""

from __future__ import annotations

import ctypes
import os
import platform
import sys
import traceback
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MTK_ROOT = PROJECT_ROOT / "tools" / "research" / "mtkclient"
PYDEPS = PROJECT_ROOT / "tools" / "mtkclient_pydeps"
CAPSTONE = PROJECT_ROOT / "tools" / "python"
WINDOWS_USB = MTK_ROOT / "mtkclient" / "Windows"

for dependency_path in (PYDEPS, CAPSTONE, MTK_ROOT):
    dependency_text = str(dependency_path)
    if dependency_text not in sys.path:
        sys.path.insert(0, dependency_text)

if os.name == "nt" and hasattr(os, "add_dll_directory"):
    os.add_dll_directory(str(WINDOWS_USB))

import usb.core  # noqa: E402
import usb.backend.libusb0  # noqa: E402
import usb.backend.libusb1  # noqa: E402


class LibusbVersion(ctypes.Structure):
    _fields_ = [
        ("major", ctypes.c_uint16),
        ("minor", ctypes.c_uint16),
        ("micro", ctypes.c_uint16),
        ("nano", ctypes.c_uint16),
        ("rc", ctypes.c_char_p),
        ("describe", ctypes.c_char_p),
    ]


def version_tuple(
    version: ctypes.POINTER[LibusbVersion],
) -> tuple[int, int, int, int, str]:
    result = version.contents
    description = result.describe.decode("ascii", errors="replace")
    return (
        result.major,
        result.minor,
        result.micro,
        result.nano,
        description,
    )


def main() -> int:
    dll_path = WINDOWS_USB / "libusb-1.0.dll"
    print(f"python={sys.version.split()[0]}")
    print(f"python_executable={sys.executable}")
    print(f"python_pointer_bits={ctypes.sizeof(ctypes.c_void_p) * 8}")
    print(f"platform={platform.platform()}")
    print(f"pyusb_version={usb.__version__}")
    print(f"pyusb_path={Path(usb.__file__).resolve()}")
    print(f"libusb_dll={dll_path.resolve()} exists={dll_path.exists()}")

    backend = usb.backend.libusb1.get_backend(
        find_library=lambda _name: str(dll_path)
    )
    print(f"libusb1_backend_loaded={backend is not None}")
    if backend is None:
        print("ERROR=libusb1 backend could not be loaded")
        return 2

    try:
        backend.lib.libusb_get_version.argtypes = []
        backend.lib.libusb_get_version.restype = ctypes.POINTER(LibusbVersion)
        version = version_tuple(backend.lib.libusb_get_version())
        print(
            "libusb_runtime_version="
            f"{version[0]}.{version[1]}.{version[2]}.{version[3]}"
            f" ({version[4]})"
        )
    except Exception:
        print("libusb_runtime_version=ERROR")
        traceback.print_exc(file=sys.stdout)

    bridge = usb.backend.libusb0.get_backend()
    print(f"libusb0_backend_loaded={bridge is not None}")

    try:
        devices = list(usb.core.find(find_all=True, backend=backend))
    except Exception as exc:
        print("ENUMERATION=FAILED")
        print(f"exception_type={type(exc).__name__}")
        print(f"exception={exc}")
        traceback.print_exc(file=sys.stdout)
        return 3

    print("ENUMERATION=OK")
    print(f"device_count={len(devices)}")
    for device in devices:
        print(
            "device="
            f"bus:{device.bus} "
            f"address:{device.address} "
            f"vid:{device.idVendor:04x} "
            f"pid:{device.idProduct:04x} "
            f"bDeviceClass:0x{device.bDeviceClass:02x} "
            f"bcdUSB:0x{device.bcdUSB:04x}"
        )
        for attribute in ("manufacturer", "product", "serial_number"):
            try:
                value = getattr(device, attribute)
                print(f"  {attribute}={value}")
            except Exception as exc:
                print(f"  {attribute}_error={type(exc).__name__}: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
