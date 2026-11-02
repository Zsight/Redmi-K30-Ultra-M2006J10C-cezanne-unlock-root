# Zadig / WinUSB 操作说明

本节只解决一个问题：让 Windows 上的 mtkclient/libusb 能访问 MTK BROM。

## 只绑定哪个设备

目标设备 ID 必须是：

```text
0E8D:0003
```

不要修改：

- 正常 Android USB ID `18D1:4EE7`；
- Fastboot 设备的正常 USB ID；
- 蓝牙、摄像头、鼠标、集线器或其他 USB 设备。

不做批量驱动替换。

## 为什么需要这一步

该机 BROM 在 Windows 上可能被识别为：

```text
USB 串行设备 (COM7)
```

Windows 可能把 `0E8D:0003` 绑定到 `usbser`。COM 串口可以完成最基础的
只读字节握手，但 Kamakiri 需要的 vendor control transfer 不一定能通过
COM 驱动完成。

因此需要将 **仅 `0E8D:0003`** 绑定到 WinUSB，让 mtkclient 的 libusb 后端
直接访问。

## 官方工具

官方页面：

```text
https://zadig.akeo.ie/
```

Zadig 2.9 官方 Release：

```text
https://github.com/pbatard/libwdi/releases/download/v1.5.1/zadig-2.9.exe
```

本项目实际核验的文件信息：

```text
size=5,334,088 bytes
sha256=4ECAA95DF3DA3621486A043AEF8B3050B8BAFE7C901402871E816229EF82039B
Authenticode=Valid
Signer=Akeo Consulting
```

发布仓库不附带 Zadig 二进制；请从官方地址下载并自行核对签名。

## 操作前准备

1. 先确认手机能进入 BROM。
2. 准备监听脚本或 mtkclient。
3. 不要先启动一个已经知道会失败的批量驱动操作。
4. 记录当前设备状态，尤其是 `0E8D:0003` 是否存在。
5. BROM 的 USB 下载窗口有限，驱动安装和后续操作要连续规划。

## 进入 BROM

本机验证过的时序：

1. 正常关机。
2. 等屏幕完全黑掉。
3. 拔掉 USB。
4. 同时按住音量上、音量下。
5. 保持按住并插入 USB。
6. 检测到 `0E8D:0003` 后松开按键。

按钮不能延长 BROM USB 超时。检测到设备后应尽快完成后续步骤。

## Zadig 点击步骤

1. 以管理员权限运行 Zadig。
2. 点击 **Options / 选项**。
3. 勾选 **List All Devices / 列出所有设备**。
4. 点设备下拉框。
5. 找到 USB 串行设备或对应描述。
6. 核对设备页面左侧的 USB ID：

```text
USB ID: 0E8D 0003
```

7. 右侧目标 Driver 选择：

```text
WinUSB (v6.1.7600.16385)
```

8. 当前驱动可能显示 `usbser`。确认 VID/PID 无误后点击：

```text
Replace Driver
```

9. 如果 Windows 弹出 UAC，选择“是”。
10. 等待安装完成。安装可能提示最多需要数分钟。

## 绝对不要点到这些按钮

- **Install WCID Driver**：不是本流程需要的按 VID/PID 生成 WCID 驱动。
- **Downgrade WCID Driver**：不要因为当前选中了别的设备而点击。
- **Extract Files**：只解出文件，不绑定当前 BROM。
- 下拉列表中其他设备：尤其是 Intel Bluetooth、Integrated Camera、USB Mouse。

如果 USB ID 不是 `0E8D:0003`，不要安装，重新选择设备。

## 安装后验证

驱动安装可能跨越 BROM 超时，因此 BROM 可能先消失。重新进入 BROM 后运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check_brom_usb.ps1
python .\scripts\usb_enum_readonly.py
python .\scripts\brom_usb_control_probe.py --wait 30
```

预期看到：

```text
device=... vid:0e8d pid:0003
libusb1_backend_loaded=True
vendor_control_transfer=OK
result=BROM_CONTROL_PATH_AVAILABLE
```

也可以检查 Windows 设备注册表实例的 `Service`：

```text
HKLM\SYSTEM\CurrentControlSet\Enum\USB\VID_0E8D&PID_0003
Service=WinUSB
```

## 常见失败

| 现象 | 原因 | 处理 |
|---|---|---|
| 下拉框中没有 `0E8D:0003` | BROM 已超时或没有进入 | 先确认 BROM 枚举，再打开 Zadig |
| 选中了 Bluetooth/Camera | 选错设备 | 立即停止，重新选择 USB ID `0E8D:0003` |
| 安装提示成功但 mtkclient 仍找不到 | 设备已从 BROM 退出，或使用了错误后端 | 重新进入 BROM，先枚举 VID/PID，再测试 libusb |
| `usbser` 仍然存在 | 替换未完成或选错设备 | 回读 Service，不要盲目重复安装 |
| `vendor_control_transfer=FAILED` | 驱动仍是 COM 或 WinUSB 绑定不完整 | 停止，记录错误，不要继续 DA 写入 |

## 恢复驱动

仅当必须恢复时，重新进入 BROM，再在 Zadig 中选中同一个
`0E8D:0003`，将目标驱动改为 USB Serial (CDC)，再执行替换。

不要删除所有 USB 驱动，不要使用“一键清理驱动”工具。

