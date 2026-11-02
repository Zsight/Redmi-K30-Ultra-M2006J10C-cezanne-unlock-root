#!/usr/bin/env python3
"""Probe whether the current Windows driver allows MTK BROM control transfer."""

from __future__ import annotations

import argparse
import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYDEPS = PROJECT_ROOT / "tools" / "mtkclient_pydeps"
MTK_ROOT = PROJECT_ROOT / "tools" / "research" / "mtkclient"
WINDOWS_USB = MTK_ROOT / "mtkclient" / "Windows"

for dependency_path in (PYDEPS, MTK_ROOT):
    dependency_text = str(dependency_path)
    if dependency_text not in sys.path:
        sys.path.insert(0, dependency_text)

if os.name == "nt" and hasattr(os, "add_dll_directory"):
    os.add_dll_directory(str(WINDOWS_USB))

import usb.core  # noqa: E402
import usb.backend.libusb1  # noqa: E402


VID = 0x0E8D
PID = 0x0003
VAR1 = 0x0A


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def log(message: str) -> None:
    print(f"{timestamp()} {message}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", type=int, default=240)
    args = parser.parse_args()

    dll_path = WINDOWS_USB / "libusb-1.0.dll"
    backend = usb.backend.libusb1.get_backend(
        find_library=lambda _name: str(dll_path)
    )
    log("mode=BROM_USB_BACKEND_PROBE")
    log(f"libusb1_backend_loaded={backend is not None}")
    if backend is None:
        return 2

    deadline = time.monotonic() + args.wait
    device = None
    while time.monotonic() < deadline:
        try:
            device = usb.core.find(
                idVendor=VID, idProduct=PID, backend=backend
            )
        except Exception as exc:
            log(f"enumeration_error={type(exc).__name__}: {exc}")
        if device is not None:
            break
        time.sleep(0.15)

    if device is None:
        log("result=BROM_NOT_FOUND")
        return 4

    log(
        f"brom_found bus={device.bus} address={device.address} "
        f"vid={device.idVendor:04X} pid={device.idProduct:04X} "
        f"bDeviceClass=0x{device.bDeviceClass:02X}"
    )
    try:
        log(
            f"bNumConfigurations={device.bNumConfigurations} "
            f"bcdUSB=0x{device.bcdUSB:04X}"
        )
    except Exception:
        log("descriptor_read_error")
        traceback.print_exc(file=sys.stdout)

    try:
        # mtkclient's Kamakiri trigger intentionally bypasses PyUSB's managed
        # interface claim. The request targets wIndex=0x0A, which is a BROM
        # protocol selector rather than an actual USB interface number.
        device._ctx.managed_claim_interface = lambda *args, **kwargs: None
        transferred = device.ctrl_transfer(
            0xA1, 0x00, 0x0000, VAR1, 0
        )
        log(f"vendor_control_transfer=OK transferred={transferred}")
        log("result=BROM_CONTROL_PATH_AVAILABLE")
        return 0
    except Exception as exc:
        log(
            "vendor_control_transfer=FAILED "
            f"type={type(exc).__name__} error={exc}"
        )
        traceback.print_exc(file=sys.stdout)
        log("result=BROM_CONTROL_PATH_UNAVAILABLE")
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
