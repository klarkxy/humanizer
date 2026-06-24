# 安装说明

本文给 agent 或维护者使用，目标是把本仓库安装成可被 Codex/Agent Skill 系统发现的 skill。

## 安装根调度 skill

将整个仓库目录复制到你的 skills 目录，并保持目录名为 `humanizer-zh-novel`：

```powershell
$skillRoot = "$env:USERPROFILE\.codex\skills\humanizer-zh-novel"
New-Item -ItemType Directory -Force (Split-Path $skillRoot) | Out-Null
Copy-Item -Recurse -Force "E:\Users\27837\Documents\OH-WorkSpace\src\humanizer" $skillRoot
```

安装后，根入口是：

```text
humanizer-zh-novel/SKILL.md
```

使用时让 agent 调用：

```text
使用 $humanizer-zh-novel 按已有作品风格改写这段中文小说正文。
```

## 安装单个作品风格

如果只想安装某个作品风格，可以只复制对应目录：

```powershell
$skillRoot = "$env:USERPROFILE\.codex\skills\humanizer-zh-fanrenxiuxianzhuan"
Copy-Item -Recurse -Force "E:\Users\27837\Documents\OH-WorkSpace\src\humanizer\references\humanizer-zh-fanrenxiuxianzhuan" $skillRoot
```

可安装的成品目录形如：

```text
references/humanizer-zh-<slug>/
  SKILL.md
  _meta.json
```

## 新建作品风格

新建风格必须通过根 skill 显式触发：

```text
使用 $humanizer-zh-novel，从 <小说原文路径> 新建一个作品风格 humanizer。
```

根 skill 会读取：

```text
references/humanizer-zh-novel-meta/SKILL.md
```

元 skill 会先把草案写入：

```text
tmp/humanizer-zh-<slug>/
```

用户批准后，才允许写入：

```text
references/humanizer-zh-<slug>/
```

## 校验

校验根 skill：

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

校验元 skill：

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" references\humanizer-zh-novel-meta
```

校验成品 skill：

```powershell
python references\humanizer-zh-novel-meta\scripts\validate_skill.py references\humanizer-zh-fanrenxiuxianzhuan
```

## 注意事项

- 面向用户和正文内容的说明必须使用中文。
- `tmp/`、`*.local.md`、`source.local.txt` 不进入 Git。
- 成品作品目录进入 Git 时只包含 `SKILL.md` 和 `_meta.json`。
- 未索引风格不能自动新建；新建必须由用户显式提出，并提供原文路径或原文文本。

