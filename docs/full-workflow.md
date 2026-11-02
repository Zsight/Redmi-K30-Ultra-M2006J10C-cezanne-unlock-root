# 完整工作流程

这是一套研究流程，不是“一键解锁”。每个阶段都有通过条件和停止条件。

## 阶段 0：确定边界

确认自己接受以下风险：

- 数据丢失；
- bootloop；
- Bootloader、AVB、seccfg 状态异常；
- OTA 失败；
- 设备保修或服务条款后果。

先把个人数据单独备份。本文的启动链备份不包含照片、微信、应用数据和
完整 `userdata`。

## 阶段 1：准备手机

1. 电量保持在 50% 以上。
2. 在设置中打开开发者选项。
3. 打开 USB 调试。
4. 连接数据线，在手机上允许“USB 调试”的 RSA 指纹。
5. 执行：

```powershell
.\platform-tools\adb.exe devices -l
```

必须是 `device`，不能是 `unauthorized` 或空列表。

记录：

```text
ro.product.device=cezanne
ro.product.model=M2006J10C
ro.build.version.incremental=V14.0.5.0.SJNCNXM
```

## 阶段 2：准备 Windows 工作区

1. 下载本仓库。
2. 将 Platform Tools 放入 `platform-tools/`。
3. 安装 64 位 Python 3.11、Git 和 pyserial/pyusb 等依赖。
4. 把审核过的 mtkclient 放到 `tools/research/mtkclient/`。
5. 运行环境检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_environment.ps1
```

如果要在 Codex 中工作，见 [`codex-workspace.md`](codex-workspace.md)。

## 阶段 3：只读系统基线

采集设备型号、Android/MIUI、Build、slot、Verified Boot、锁定状态和
`/dev/block/by-name`。

通过条件：

```text
device=cezanne
model=M2006J10C
build=V14.0.5.0.SJNCNXM
verifiedbootstate=green（解锁前）
flash.locked=1（解锁前）
```

只要有一项不符合，就停止并重新确认固件。

## 阶段 4：官方固件与备份

获取精确匹配的官方 Fastboot 包，核对文件名、大小和 MD5。不要用大小
正确但哈希错误的文件。

至少备份：

- boot；
- seccfg；
- vbmeta、vbmeta_system、vbmeta_vendor；
- lk、lk2；
- dtbo；
- Preloader A/B；
- GPT head 和 backup tail。

备份只保存在加密离线位置，不进入公开 Git。

## 阶段 5：BROM 和 WinUSB

先进入 BROM，再按 [`zadig-win-usb.md`](zadig-win-usb.md) 只绑定：

```text
USB\VID_0E8D&PID_0003 -> WinUSB
```

通过条件：

```text
USB enumeration sees 0E8D:0003
libusb backend loads
vendor control transfer succeeds
```

如果仍是 COM/usbser，停止，不要发送 stage1。

## 阶段 6：Stage1

使用审核过的 MT6885-family payload 和 `Kamakiri2` 路径。

通过条件：

```text
hwcode=0x0816
target_config=0x000000E7
stage1_ack=A1A2A3A4
stage1_second_handshake=OK
```

旧的 `Kamakiri` 路径没有 ACK，不应继续 DA。不要因为“payload sent”就
继续。

## 阶段 7：DA 只读阶段

启动 DA 后只做：

- UFS/GPT 识别；
- seccfg、boot、vbmeta、lk 等指定分区只读；
- 保存原始日志和哈希。

不在此阶段写任何分区。确认 seccfg V4、lock state、boot header 和
vbmeta 签名状态。

## 阶段 8：seccfg 解锁

这是第一次持久写入，必须是单独授权。

本机验证过的结果是：

```text
seccfg lock_state: 2 -> 3
dm_verity_state: 0
```

写入后必须回读整个 seccfg，并在重启后验证：

```text
fastboot getvar unlocked -> unlocked: yes
fastboot oem lks -> 0
ro.boot.flash.locked -> 0
ro.boot.vbmeta.device_state -> unlocked
```

未通过就停止，不要继续刷 boot。

## 阶段 9：Magisk patch boot

使用当前设备实际读取的 boot 镜像，不要使用其他版本或第三方 boot。

1. 用官方 Magisk 生成 patched boot。
2. 校验大小、header、ramdisk 和 SHA-256。
3. 明确确认要执行 `fastboot flash boot`。
4. 先确保原始 boot 已保存并可恢复。

临时 `fastboot boot` 可能被设备拒绝；本机实测在 `Booting` 阶段断开，
所以不能把它当作成功标准。

## 阶段 10：Root 验证

重启后执行：

```text
su -v
su -c id
```

通过条件：

```text
MagiskSU version
uid=0(root)
```

只有看到 UID 0，才能称为 Root 成功。

## 阶段 11：恢复和维护

- 保留原始 boot 和完整恢复材料。
- 不在混合状态下尝试重新锁定 Bootloader。
- OTA 可能覆盖 Root。
- 不刷其他机型镜像。
- 不公开设备唯一标识和原厂二进制。

