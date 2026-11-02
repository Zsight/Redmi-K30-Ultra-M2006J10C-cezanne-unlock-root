# Using the repository with Codex or another CLI agent

## Download or clone

Put the repository in a dedicated directory, for example:

```text
C:\HomeFolder\项目\K30U_ROOT
```

Then place Platform Tools under:

```text
C:\HomeFolder\项目\K30U_ROOT\platform-tools\
```

Do not point the agent at the whole user profile or an unrelated download
folder.

## Open as workspace

In Codex or a compatible desktop agent:

1. Choose **Open folder / Add workspace**.
2. Select the repository root.
3. Open a new terminal in that root.
4. Let the agent read `AGENTS.md` before executing commands.

## Suggested first prompt

```text
读取 AGENTS.md、docs/compatibility.md 和 docs/quick-start.md。
当前目标是 Redmi K30 Ultra / cezanne / M2006J10C，
系统为 V14.0.5.0.SJNCNXM。
先只做只读环境检测和设备识别，不允许 flash、erase、format、
解锁、DA 写入、seccfg 写入或 RPMB 操作。
所有输出保存到 logs，遇到不匹配立即停止并解释证据。
```

## How to use AI safely

The agent may help with:

- checking installed tools;
- running read-only ADB/Fastboot queries;
- parsing boot/vbmeta/lk images;
- recording logs and hashes;
- explaining errors and comparing reports;
- preparing a recovery checklist.

The human must:

- physically enter BROM/Fastboot;
- observe and report the phone screen;
- approve every persistence-changing command;
- keep offline firmware and partition backups;
- decide whether the security and warranty risks are acceptable.

## Agent rules in this repository

`AGENTS.md` deliberately forbids the agent from treating a broad “continue”
message as permission to flash arbitrary images or modify `seccfg`/RPMB. The
agent must identify the exact target and describe the recovery path before
requesting authorization.

