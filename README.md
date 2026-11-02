# Redmi K30 Ultra (cezanne) 解锁与 Root 研究记录

这是一个**特定设备、特定固件、特定日期**的实机验证项目。它不是通用
MTK 解锁工具，也不能把其他机型的分区、BROM 地址或 DA payload 直接套用。

## 已验证设备

| 项目 | 值 |
|---|---|
| 手机 | Redmi K30 Ultra / 红米 K30 至尊纪念版 |
| 型号 | M2006J10C |
| 代号 | `cezanne` |
| SoC | MediaTek MT6889Z / Dimensity 1000+ |
| 系统 | MIUI `V14.0.5.0.SJNCNXM` |
| Android | 12 |
| UFS | `THGJFCT2T84BAK` |
| 验证日期 | 2026-11-02 |

最终验证结果：

```text
Bootloader: unlocked
Fastboot:   unlocked: yes, oem lks = 0
Verified Boot: orange
Root: MagiskSU 31.1, uid=0(root)
```

只有在上述机型、上述固件和同等当前安全状态下，才可能参考本记录。
其他版本必须重新做只读识别和风险评估。

## 重要声明

本项目包含会修改设备持久状态的真实研究步骤。它可能导致：

- 数据丢失；
- 无法进入 Android；
- Fastboot/BROM 之外的恢复条件失效；
- OTA 更新失败或 Root 丢失；
- 保修和服务条款方面的后果。

请只对自己的设备执行，并在执行任何写操作前完成离线备份。

本仓库刻意不包含：

- 官方固件、boot、lk、preloader、vbmeta 或 seccfg 镜像；
- Magisk APK、mtkclient 二进制或其他第三方可执行文件；
- IMEI、MEID、SOCID、UFS 序列号或设备唯一标识；
- 可以直接无确认执行写操作的“一键脚本”。

## 目录

- [`docs/quick-start.md`](docs/quick-start.md) — 从下载到完成只读基线。
- [`docs/compatibility.md`](docs/compatibility.md) — 严格兼容范围。
- [`docs/environment-windows.md`](docs/environment-windows.md) — 电脑与手机准备。
- [`docs/download-firmware.md`](docs/download-firmware.md) — 官方固件元数据和校验。
- [`docs/codex-workspace.md`](docs/codex-workspace.md) — 如何把目录交给 Codex/CLI。
- [`docs/verified-path.md`](docs/verified-path.md) — 实际成功的完整技术路径。
- [`docs/failure-notes.md`](docs/failure-notes.md) — 已经排除的错误路线。
- [`docs/triage.md`](docs/triage.md) — 现象、原因和下一步排错矩阵。
- [`docs/recovery.md`](docs/recovery.md) — 恢复与备份要求。
- [`docs/evidence.md`](docs/evidence.md) — 不含设备唯一标识的证据摘要。
- [`docs/github-publish.md`](docs/github-publish.md) — 正确创建 GitHub Repository。
- [`AGENTS.md`](AGENTS.md) — 给 Codex/CLI agent 的安全工作规则。
- `scripts/` — 只读采集和验证工具，不是一键解锁工具。

## 快速开始

1. 下载/克隆本仓库。
2. 把 Android Platform Tools 放到仓库根目录的 `platform-tools/`。
3. 安装 64 位 Python 3.11、Git 和当前版本的 Codex 或兼容 CLI agent。
4. 用 Codex 打开整个仓库目录作为 workspace。
5. 让 agent 先阅读 `AGENTS.md` 和 `docs/quick-start.md`。
6. 在手机上开启开发者选项和 USB 调试。
7. 先只做识别和设备信息采集，不执行任何写入。
8. 确认型号、固件、SoC、分区表和安全状态完全一致后，才讨论下一阶段。

可先运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_environment.ps1
```

## 使用 Codex 时建议的起始指令

```text
先阅读 AGENTS.md 和 docs/quick-start.md。
本机目标是 Redmi K30 Ultra / cezanne / M2006J10C /
V14.0.5.0.SJNCNXM。
先只做只读识别，不执行任何 flash、erase、format、解锁、
DA 写入、seccfg 写入或 RPMB 操作。
每次命令保存原始输出、错误和时间；遇到不匹配先停止并解释证据。
```

AI 可以帮助检查环境、运行只读命令、解析镜像和整理日志，但不能代替
用户确认物理按键、授权风险或判断是否应该继续写入。

## 成功路线摘要

```text
精确固件和设备识别
-> 原始启动链与 seccfg 备份
-> BROM 0E8D:0003
-> WinUSB/libusb
-> Kamakiri2 MT6885-family stage1
-> DA XFLASH
-> seccfg V4 lock_state 2 -> 3
-> 验证 Bootloader unlocked
-> Magisk patched boot
-> Fastboot flash boot
-> su -c id = uid=0(root)
```

这条记录已经包含成功尝试和失败尝试。请同时阅读
[`failure-notes.md`](docs/failure-notes.md)；只复制成功命令而不理解失败
条件，会再次造成试错和风险。

## 许可与上游

仓库发布前必须由仓库所有者选择许可证。`mtkclient` 采用 GPLv3；
凡引用或发布与其衍生代码有关的部分，都必须保留上游归属并遵守其许可证。
Magisk 应从官方 Release 获取，不要在仓库中分发其 APK。

