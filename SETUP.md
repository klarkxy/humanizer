# AGENT 安装手册

本文件给 agent 阅读。用户不需要手动执行这些步骤；用户只需要把 README 开头那句安装指令粘贴给 agent。

## 触发条件

当用户说：

```text
请优先用 npx 安装 https://github.com/klarkxy/humanizer 的 humanizer-zh-novel skill；如果 npx 安装失败，请改用 git 直接下载并安装。
```

agent 必须先尝试 npx 安装；只有 npx 不可用、安装失败、网络失败或无法解析该仓库 skill 时，才使用 git 直接下载安装方案。

## 安装目标

把 GitHub 仓库安装为一个可被 skill 系统发现的根 skill：

```text
<skills-dir>/humanizer-zh-novel/
  SKILL.md
  references/
  agents/
```

默认 skills 目录：

- Windows Codex：`%USERPROFILE%\.codex\skills`
- macOS/Linux Codex：`~/.codex/skills`

如果当前环境有明确的 `CODEX_HOME`，优先使用：

```text
$CODEX_HOME/skills
```

## 首选：npx 安装

先确认 `npx` 可用：

```powershell
npx --version
```

如果可用，优先运行：

```powershell
npx skills add klarkxy/humanizer@humanizer-zh-novel -g -y
```

macOS/Linux 同样优先运行：

```bash
npx skills add klarkxy/humanizer@humanizer-zh-novel -g -y
```

如果该命令成功，继续执行“安装后校验”。如果失败，记录失败原因，改走下面的 git 兜底方案。

## 兜底：Windows PowerShell git 直接下载安装

```powershell
$repoUrl = "https://github.com/klarkxy/humanizer.git"
$skillName = "humanizer-zh-novel"
$skillsDir = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $env:USERPROFILE ".codex\skills" }
$target = Join-Path $skillsDir $skillName
$tmp = Join-Path $env:TEMP "humanizer-zh-novel-install"

if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
git clone $repoUrl $tmp

New-Item -ItemType Directory -Force $skillsDir | Out-Null
if (Test-Path $target) { Remove-Item -Recurse -Force $target }
Copy-Item -Recurse -Force $tmp $target

Remove-Item -Recurse -Force $tmp
```

## 兜底：macOS/Linux git 直接下载安装

```bash
repo_url="https://github.com/klarkxy/humanizer.git"
skill_name="humanizer-zh-novel"
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
target="$skills_dir/$skill_name"
tmp="$(mktemp -d)"

git clone "$repo_url" "$tmp"
mkdir -p "$skills_dir"
rm -rf "$target"
cp -R "$tmp" "$target"
rm -rf "$tmp"
```

## 安装后校验

进入安装目录。若使用 npx 安装，请先定位实际安装目录；若使用 git 兜底方案，安装目录应为：

```text
<skills-dir>/humanizer-zh-novel
```

必须确认：

- `SKILL.md` 存在。
- `references/humanizer-zh-novel-meta/SKILL.md` 存在。
- 至少存在一个 `references/humanizer-zh-*/SKILL.md` 成品风格。

如果本机有 skill-creator 校验脚本，运行：

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" references\humanizer-zh-novel-meta
```

然后校验成品风格：

```powershell
python references\humanizer-zh-novel-meta\scripts\validate_skill.py references\humanizer-zh-fanrenxiuxianzhuan
python references\humanizer-zh-novel-meta\scripts\validate_skill.py references\humanizer-zh-xiuzhenliaotianqun
python references\humanizer-zh-novel-meta\scripts\validate_skill.py references\humanizer-zh-limingzhijian
```

如果校验脚本不存在，不要失败退出；改为报告“已复制安装，未运行 skill-creator 校验”。

## 完成后回复用户

安装成功后，简短回复：

```text
已安装 humanizer-zh-novel skill。你可以说：使用 $humanizer-zh-novel 按凡人修仙传风格改写这段中文小说正文。
```

## 约束

- 不要把仓库安装成 `humanizer`，必须安装成 `humanizer-zh-novel`。
- 不要把 `references/humanizer-zh-novel-meta/` 单独当根 skill 安装，除非用户明确只要元生成器。
- 不要提交或复制用户本地小说原文到 Git。
- 如果目标目录已存在，可以覆盖安装，但不要删除 skills 目录里的其他 skill。
