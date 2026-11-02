#!/usr/bin/env python3
"""Offline parser for the read-only boot and vbmeta images."""

from __future__ import annotations

import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def u64(data: bytes, offset: int) -> int:
    return struct.unpack_from("<Q", data, offset)[0]


def u32be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def u64be(data: bytes, offset: int) -> int:
    return struct.unpack_from(">Q", data, offset)[0]


def c_string(data: bytes, offset: int, size: int) -> str:
    return data[offset : offset + size].split(b"\0", 1)[0].decode(
        "utf-8", errors="replace"
    )


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def parse_boot(path: Path) -> None:
    data = path.read_bytes()
    print(f"boot_path={path}")
    print(f"boot_file_size={len(data)}")
    print(f"boot_magic={data[:8]!r}")
    if data[:8] != b"ANDROID!":
        print("boot_parse=FAILED")
        return
    fields = {
        "kernel_size": u32(data, 8),
        "kernel_addr": u32(data, 12),
        "ramdisk_size": u32(data, 16),
        "ramdisk_addr": u32(data, 20),
        "second_size": u32(data, 24),
        "second_addr": u32(data, 28),
        "tags_addr": u32(data, 32),
        "page_size": u32(data, 36),
        "header_version": u32(data, 40),
        "os_version": u32(data, 44),
    }
    for name, value in fields.items():
        print(f"boot_{name}=0x{value:08X} ({value})")
    print(f"boot_name={c_string(data, 48, 16)!r}")
    print(f"boot_cmdline={c_string(data, 64, 512)!r}")
    print(f"boot_id={data[576:608].hex().upper()}")
    print(f"boot_extra_cmdline={c_string(data, 608, 1024)!r}")
    page_size = fields["page_size"]
    if page_size <= 0:
        print("boot_page_layout=invalid")
        return
    kernel_off = page_size
    ramdisk_off = align(kernel_off + fields["kernel_size"], page_size)
    second_off = align(ramdisk_off + fields["ramdisk_size"], page_size)
    print(f"boot_kernel_offset=0x{kernel_off:X}")
    print(f"boot_ramdisk_offset=0x{ramdisk_off:X}")
    print(f"boot_second_offset=0x{second_off:X}")
    if fields["ramdisk_size"]:
        ramdisk = data[ramdisk_off : ramdisk_off + fields["ramdisk_size"]]
        print(f"ramdisk_magic={ramdisk[:4]!r}")


def parse_hash_descriptor(data: bytes, pos: int, length: int) -> dict[str, object]:
    image_size = u64be(data, pos)
    hash_algorithm = (
        data[pos + 8 : pos + 40].split(b"\0", 1)[0].decode(
            "ascii", errors="replace"
        )
    )
    name_len = u32be(data, pos + 40)
    salt_len = u32be(data, pos + 44)
    digest_len = u32be(data, pos + 48)
    flags = u32be(data, pos + 52)
    # The hash descriptor reserves 60 bytes after its fixed fields.
    cursor = pos + 0x74
    name = data[cursor : cursor + name_len].decode("utf-8", errors="replace")
    cursor = align(cursor + name_len, 8)
    salt = data[cursor : cursor + salt_len]
    cursor = align(cursor + salt_len, 8)
    digest = data[cursor : cursor + digest_len]
    return {
        "image_size": image_size,
        "hash_algorithm": hash_algorithm,
        "partition_name": name,
        "salt": salt.hex().upper(),
        "digest": digest.hex().upper(),
        "flags": flags,
        "declared_length": length,
    }


def parse_vbmeta(path: Path) -> None:
    data = path.read_bytes()
    print(f"vbmeta_path={path}")
    print(f"vbmeta_magic={data[:4]!r}")
    if data[:4] != b"AVB0":
        print("vbmeta_parse=FAILED")
        return
    required_major = u32be(data, 4)
    required_minor = u32be(data, 8)
    auth_size = u64be(data, 12)
    aux_size = u64be(data, 20)
    algorithm = u32be(data, 28)
    hash_offset = u64be(data, 32)
    hash_size = u64be(data, 40)
    signature_offset = u64be(data, 48)
    signature_size = u64be(data, 56)
    public_key_offset = u64be(data, 64)
    public_key_size = u64be(data, 72)
    metadata_offset = u64be(data, 80)
    metadata_size = u64be(data, 88)
    descriptor_offset = u64be(data, 96)
    descriptor_size = u64be(data, 104)
    rollback_index = struct.unpack_from(">Q", data, 108)[0]
    flags = u32be(data, 116)
    rollback_index_location = u32be(data, 120)
    release_string = c_string(data, 128, 48)
    for name, value in (
        ("required_major", required_major),
        ("required_minor", required_minor),
        ("authentication_data_block_size", auth_size),
        ("auxiliary_data_block_size", aux_size),
        ("algorithm_type", algorithm),
        ("hash_offset", hash_offset),
        ("hash_size", hash_size),
        ("signature_offset", signature_offset),
        ("signature_size", signature_size),
        ("public_key_offset", public_key_offset),
        ("public_key_size", public_key_size),
        ("public_key_metadata_offset", metadata_offset),
        ("public_key_metadata_size", metadata_size),
        ("descriptors_offset", descriptor_offset),
        ("descriptors_size", descriptor_size),
        ("rollback_index", rollback_index),
        ("flags", flags),
        ("rollback_index_location", rollback_index_location),
    ):
        print(f"vbmeta_{name}={value}")
    print(f"vbmeta_release_string={release_string!r}")

    auth_start = 256
    aux_start = auth_start + auth_size
    descriptor_start = aux_start + descriptor_offset
    descriptor_end = descriptor_start + descriptor_size
    print(f"vbmeta_auth_block=0x{auth_start:X}:0x{auth_start + auth_size:X}")
    print(f"vbmeta_aux_block=0x{aux_start:X}:0x{aux_start + aux_size:X}")
    print(f"vbmeta_descriptors=0x{descriptor_start:X}:0x{descriptor_end:X}")
    if descriptor_end > len(data):
        print("vbmeta_descriptor_block=OUT_OF_RANGE")
        return

    tags = {
        0: "property",
        1: "hashtree",
        2: "hash",
        3: "kernel_cmdline",
        4: "chain_partition",
    }
    pos = descriptor_start
    while pos + 16 <= descriptor_end:
        tag = u64be(data, pos)
        length = u64be(data, pos + 8)
        body = pos + 16
        print(
            f"vbmeta_descriptor offset=0x{pos:X} "
            f"tag=0x{tag:X} ({tags.get(tag, 'unknown')}) "
            f"length={length}"
        )
        if length < 16 or body + length > descriptor_end:
            print("vbmeta_descriptor=invalid_length")
            break
        if tag == 2:
            print(f"vbmeta_hash_descriptor={parse_hash_descriptor(data, body, length)}")
        elif tag == 0:
            key_len = u32be(data, body)
            value_len = u32be(data, body + 4)
            cursor = body + 8
            key = data[cursor : cursor + key_len].decode(
                "utf-8", errors="replace"
            )
            value = data[cursor + key_len : cursor + key_len + value_len]
            print(f"vbmeta_property={key!r} value={value!r}")
        pos = align(body + length, 8)


def main() -> int:
    parse_boot(ROOT / "boot_analysis" / "boot_readonly.img")
    parse_vbmeta(ROOT / "boot_analysis" / "vbmeta_readonly.img")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
