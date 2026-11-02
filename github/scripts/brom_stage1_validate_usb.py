#!/usr/bin/env python3
"""Execute only mt6885 BROM stage1 over the WinUSB/libusb backend."""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import struct
import sys
import time
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYDEPS = PROJECT_ROOT / "tools" / "mtkclient_pydeps"
MTK_ROOT = PROJECT_ROOT / "tools" / "research" / "mtkclient"
WINDOWS_USB = MTK_ROOT / "mtkclient" / "Windows"
PAYLOAD_PATH = MTK_ROOT / "mtkclient" / "payloads" / "mt6885_payload.bin"

for dependency_path in (PYDEPS, MTK_ROOT):
    dependency_text = str(dependency_path)
    if dependency_text not in sys.path:
        sys.path.insert(0, dependency_text)

if os.name == "nt":
    os.environ["PATH"] = f"{WINDOWS_USB};{os.environ.get('PATH', '')}"
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(WINDOWS_USB))

from mtkclient.Library.Exploit.kamakiri import Kamakiri  # noqa: E402
from mtkclient.Library.Exploit.kamakiri2 import Kamakiri2  # noqa: E402
from mtkclient.Library.mtk_class import Mtk  # noqa: E402
from mtkclient.config.mtk_config import MtkConfig  # noqa: E402


EXPECTED_HWCODE = 0x0816
EXPECTED_TARGET_CONFIG = 0x000000E7
EXPECTED_PAYLOAD_SHA256 = (
    "77378F8F83D2A36E478A388B1704AF466515E054A92874BBB9DD53845A57610D"
)
HANDSHAKE = bytes((0xA0, 0x0A, 0x50, 0x05))
ACK_INT = 0xA1A2A3A4
ACK_BYTES = ACK_INT.to_bytes(4, "big")


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def log(message: str) -> None:
    print(f"{timestamp()} {message}", flush=True)


def load_payload() -> bytes:
    payload = PAYLOAD_PATH.read_bytes()
    digest = hashlib.sha256(payload).hexdigest().upper()
    log(f"payload_path={PAYLOAD_PATH}")
    log(f"payload_size={len(payload)}")
    log(f"payload_sha256={digest}")
    if digest != EXPECTED_PAYLOAD_SHA256:
        raise RuntimeError("mt6885 payload hash mismatch")
    if len(payload) % 4:
        raise RuntimeError("mt6885 payload is not word-aligned")
    return payload


def stage1_second_handshake(mtk: Mtk) -> bool:
    for outgoing in HANDSHAKE:
        expected = (~outgoing) & 0xFF
        if not mtk.port.usbwrite(bytes((outgoing,))):
            log(f"stage1_handshake_write_failed=tx={outgoing:02X}")
            return False
        incoming = mtk.port.usbread(1, 1000)
        if incoming != bytes((expected,)):
            log(
                f"stage1_handshake_failed tx={outgoing:02X} "
                f"expected={expected:02X} "
                f"rx={incoming.hex().upper() or '(empty)'}"
            )
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", type=int, default=300)
    parser.add_argument(
        "--exploit",
        choices=("kamakiri2", "kamakiri"),
        default="kamakiri2",
    )
    parser.add_argument("--execute-mt6885-stage1", action="store_true")
    args = parser.parse_args()

    log("mode=BROM_STAGE1_VALIDATE_USB")
    log("backend=WinUSB/libusb1")
    log(f"exploit={args.exploit}")
    log("blocked=DA,partition,gpt,seccfg,rpmb,flash,erase,unlock,reset")
    if not args.execute_mt6885_stage1:
        log("result=EXECUTION_FLAG_MISSING")
        return 2

    payload = load_payload()
    config = MtkConfig(loglevel=logging.INFO)
    config.ptype = args.exploit
    config.skipwdt = True
    mtk = Mtk(config=config, loglevel=logging.INFO)

    if not mtk.port.wait_for_device(
        max_attempts=max(1, args.wait), interval=1, wait=True
    ):
        log("result=BROM_NOT_FOUND")
        return 4

    if not mtk.port.run_handshake():
        log("result=HANDSHAKE_FAILED")
        return 5

    hw_pair = mtk.preloader.get_hwcode()
    if not hw_pair:
        log("result=HW_CODE_FAILED")
        return 6
    hwcode, hwver = hw_pair
    log(f"hwcode=0x{hwcode:04X} hwver=0x{hwver:04X}")
    if hwcode != EXPECTED_HWCODE:
        log("result=HWCODE_MISMATCH")
        return 7

    config.init_hwcode(hwcode)
    target = mtk.preloader.get_target_config(display=False)
    target_bits = (
        (0x01 if target["sbc"] else 0)
        | (0x02 if target["sla"] else 0)
        | (0x04 if target["daa"] else 0)
        | (0x08 if target["epp"] else 0)
        | (0x10 if target["cert"] else 0)
        | (0x20 if target["memread"] else 0)
        | (0x40 if target["memwrite"] else 0)
        | (0x80 if target["cmdC8"] else 0)
    )
    config.target_config = target
    log(f"target_config=0x{target_bits:08X}")
    if target_bits != EXPECTED_TARGET_CONFIG:
        log("result=TARGET_CONFIG_MISMATCH")
        return 8

    exploit_class = Kamakiri2 if args.exploit == "kamakiri2" else Kamakiri
    kamakiri = exploit_class(mtk=mtk, loglevel=logging.INFO)
    log("starting_isolated_stage1")
    try:
        result = kamakiri.runpayload(payload, ack=ACK_INT)
    except Exception as exc:
        log(
            "result=STAGE1_EXCEPTION "
            f"type={type(exc).__name__} error={exc}"
        )
        return 10
    if result != ACK_INT:
        log(
            "result=STAGE1_ACK_MISSING "
            f"returned={result!r}"
        )
        return 11
    log(f"stage1_ack={ACK_BYTES.hex().upper()}")

    if not stage1_second_handshake(mtk):
        log("result=STAGE1_SECOND_HANDSHAKE_FAILED")
        return 12
    log("stage1_handshake=OK")
    log("result=STAGE1_ACK_AND_HANDSHAKE_OK")
    log("stopping_without_DA_or_partition_access")

    # Do not send any further command. Closing the host handle allows BROM's
    # watchdog to reset the device naturally.
    mtk.port.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
