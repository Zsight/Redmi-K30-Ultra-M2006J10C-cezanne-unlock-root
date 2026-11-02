# 官方固件获取与校验

## 不要相信“大小正确”

本次研究中曾出现过一个文件：

```text
size=5,675,852,185
```

但 MD5 与官方值不同，因此它是无效文件。大小正确不等于内容正确。

## 本机匹配版本

```text
filename=cezanne_images_V14.0.5.0.SJNCNXM_20230705.0000.00_12.0_cn_1342c50d37.tgz
size=5,675,852,185 bytes
md5=1342c50d373956b036ede312f86b0b13
```

小米官方更新接口：

```text
https://update.intl.miui.com/updates/miota-fullrom.php?d=cezanne&b=F&r=cn&n=&l=en_US
```

CDN 地址可能变化，也可能返回 403。应使用当前官方响应中的文件名和
元数据，不要盲目使用过期链接。

## 下载后校验

PowerShell：

```powershell
Get-Item .\cezanne_images_V14.0.5.0.SJNCNXM_20230705.0000.00_12.0_cn_1342c50d37.tgz |
  Select-Object Name,Length

Get-FileHash .\cezanne_images_V14.0.5.0.SJNCNXM_20230705.0000.00_12.0_cn_1342c50d37.tgz |
  Select-Object Algorithm,Hash
```

官方值是 MD5：

```text
1342c50d373956b036ede312f86b0b13
```

如果大小或 MD5 任一不一致，不要刷写、不要解包作为恢复母版。

## 解包前的边界

官方包只用于离线分析或恢复。解包、校验和查看镜像可以在电脑上完成；
不要把任何分区写入手机，除非已经完成设备匹配、备份和恢复验证。

