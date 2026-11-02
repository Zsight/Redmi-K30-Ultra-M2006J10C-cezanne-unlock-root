#!/usr/bin/env python3
"""Minimal, read-only MTK BROM identification over an existing COM port.

The script performs the standard BROM byte handshake and only sends the
read-only GET_HW_CODE, GET_TARGET_CONFIG, GET_BL_VER and GET_BROM_VERSION
commands. It does not disable the watchdog, start a DA, access partitions, or
write RPMB/seccfg.
"""

from __future__ import annotations

import argparse
import struct
import sys
import time
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYDEPS = PROJECT_ROOT / "tools" / "mtkclient_pydeps"
if str(PYDEPS) not in sys.path:
    sys.path.insert(0, str(PYDEPS))

try:
    import serial  # noqa: E402
    import serial.tools.list_ports  # noqa: E402
except ImportError as exc:
    print(f"ERROR=pyserial is not installed: {exc}")
    print("Install it with: python -m pip install pyserial")
    raise SystemExit(2) from exc


BROM_VID = 0x0E8D
BROM_PID = 0x0003
HANDSHAKE = bytes((0xA0, 0x0A, 0x50, 0x05))

GET_HW_CODE = 0xFD
GET_TARGET_CONFIG = 0xD8
GET_BL_VER = 0xFE
GET_VERSION = 0xFF


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="milliseconds")


def log(message: str) -> None:
    print(f"{timestamp()} {message}", flush=True)


def candidate_ports(explicit_port: str | None) -> list[serial.tools.list_ports.ListPortInfo]:
    ports = list(serial.tools.list_ports.comports())
    if explicit_port:
        return [
            port
            for port in ports
            if port.device.casefold() == explicit_port.casefold()
        ]
    return [
        port
        for port in ports
        if port.vid == BROM_VID and port.pid == BROM_PID
    ]


def wait_for_port(
    explicit_port: str | None, deadline: float
) -> serial.tools.list_ports.ListPortInfo | None:
    last_inventory: tuple[str, ...] | None = None
    while time.monotonic() < deadline:
        ports = list(serial.tools.list_ports.comports())
        candidates = candidate_ports(explicit_port)
        inventory = tuple(
            f"{port.device}:{port.vid:04X}:{port.pid:04X}"
            if port.vid is not None and port.pid is not None
            else f"{port.device}:----:----"
            for port in ports
        )
        if inventory != last_inventory:
            rendered = ", ".join(inventory) if inventory else "(none)"
            log(f"serial_ports={rendered}")
            last_inventory = inventory
        if candidates:
            selected = candidates[0]
            log(
                "selected_port="
                f"{selected.device} vid={selected.vid!r} pid={selected.pid!r} "
                f"description={selected.description!r}"
            )
            return selected
        time.sleep(0.15)
    return None


def read_exact(port: serial.Serial, length: int, timeout: float) -> bytes:
    deadline = time.monotonic() + timeout
    data = bytearray()
    while len(data) < length and time.monotonic() < deadline:
        chunk = port.read(length - len(data))
        if chunk:
            data.extend(chunk)
    return bytes(data)


def handshake(port: serial.Serial) -> bool:
    port.reset_input_buffer()
    for outgoing in HANDSHAKE:
        port.write(bytes((outgoing,)))
        port.flush()
        incoming = read_exact(port, 1, 0.25)
        expected = (~outgoing) & 0xFF
        if incoming != bytes((expected,)):
            log(
                "handshake_byte_failed="
                f"tx={outgoing:02X} expected={expected:02X} "
                f"rx={incoming.hex().upper() or '(empty)'}"
            )
            return False
    log("handshake=OK")
    return True


def read_command(
    port: serial.Serial,
    command: int,
    response_length: int,
    *,
    expect_echo: bool = True,
) -> bytes | None:
    port.write(bytes((command,)))
    port.flush()
    if expect_echo:
        echo = read_exact(port, 1, 0.5)
        if echo != bytes((command,)):
            log(
                f"command_echo_failed=cmd={command:02X} "
                f"rx={echo.hex().upper() or '(empty)'}"
            )
            return None
    response = read_exact(port, response_length, 1.0)
    if len(response) != response_length:
        log(
            f"command_response_incomplete=cmd={command:02X} "
            f"expected={response_length} got={len(response)} "
            f"rx={response.hex().upper()}"
        )
        return None
    return response


def identify(port: serial.Serial) -> None:
    hw_response = read_command(port, GET_HW_CODE, 4)
    if hw_response is None:
        return
    hw_value = struct.unpack(">I", hw_response)[0]
    log(f"GET_HW_CODE=0x{hw_value:08X}")
    log(f"hwcode=0x{(hw_value >> 16) & 0xFFFF:04X}")
    log(f"hwver=0x{hw_value & 0xFFFF:04X}")

    target_response = read_command(port, GET_TARGET_CONFIG, 6)
    if target_response is not None:
        target_config, status = struct.unpack(">IH", target_response)
        fields = {
            "sbc": bool(target_config & 0x01),
            "sla": bool(target_config & 0x02),
            "daa": bool(target_config & 0x04),
            "epp": bool(target_config & 0x08),
            "cert": bool(target_config & 0x10),
            "memread_auth": bool(target_config & 0x20),
            "memwrite_auth": bool(target_config & 0x40),
            "cmd_c8_blocked": bool(target_config & 0x80),
        }
        log(f"target_config=0x{target_config:08X}")
        log(f"target_status=0x{status:04X}")
        for name, enabled in fields.items():
            log(f"target_{name}={str(enabled).lower()}")

    # GET_BL_VER only echoes 0xFE. The echo itself identifies BROM mode.
    bl_response = read_command(port, GET_BL_VER, 0)
    if bl_response is not None:
        log("BROM mode detected.")

    # Unlike the preceding command, GET_VERSION returns its one-byte version
    # directly and does not echo 0xFF first.
    brom_response = read_command(
        port, GET_VERSION, 1, expect_echo=False
    )
    if brom_response is not None:
        log(f"bromver=0x{brom_response[0]:02X}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        help="Explicit COM port. If omitted, detect VID_0E8D&PID_0003.",
    )
    parser.add_argument("--wait", type=int, default=180)
    parser.add_argument("--handshake-attempts", type=int, default=80)
    args = parser.parse_args()

    log("mode=READ_ONLY_BROM_SERIAL_IDENTIFY")
    log("allowed=handshake,GET_HW_CODE,GET_TARGET_CONFIG,GET_BL_VER,GET_VERSION")
    log("blocked=watchdog_write,DA,partition_io,seccfg,rpmb,reset,flash")

    deadline = time.monotonic() + args.wait
    port_info = wait_for_port(args.port, deadline)
    if port_info is None:
        log("result=NO_BROM_SERIAL_PORT")
        return 4

    connected = False
    for attempt in range(1, args.handshake_attempts + 1):
        if time.monotonic() >= deadline:
            break
        try:
            with serial.Serial(
                port=port_info.device,
                baudrate=115200,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1,
                write_timeout=0.25,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
                exclusive=True,
            ) as serial_port:
                serial_port.dtr = False
                serial_port.rts = False
                if handshake(serial_port):
                    connected = True
                    identify(serial_port)
                    break
        except (serial.SerialException, OSError) as exc:
            log(f"serial_open_or_handshake_error={type(exc).__name__}: {exc}")
        if attempt % 10 == 0:
            log(f"handshake_attempts={attempt}/{args.handshake_attempts}")
        time.sleep(0.1)

    if not connected:
        log("result=PORT_FOUND_BUT_HANDSHAKE_FAILED")
        return 5

    log("result=READ_ONLY_IDENTIFY_COMPLETED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
