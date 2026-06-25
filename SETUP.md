# AGENT 安装手册

本文件给 agent 阅读。用户不需要手动执行这些步骤；用户只需要把 README 开头那句安装指令粘贴给 agent。

## 触发条件

当用户说：

```text
请直接读取 https://raw.githubusercontent.com/klarkxy/humanizer-zh-novel/main/SETUP.md 并按其中指引安装。
```

agent 读取本文件后，按下方步骤执行。安装逻辑已写在本文件中，无需用户再补充。

## 安装目标

本仓库是 monorepo，每个 `skills/humanizer-zh-<slug>/` 都是独立 skill。agent 按用户需求安装对应 skill。

默认 skills 目录：

- Windows Codex：`%USERPROFILE%\.codex\skills`
- macOS/Linux Codex：`~/.codex/skills`

如果当前环境有明确的 `CODEX_HOME`，优先使用：

```text
$CODEX_HOME/skills
```

## 安装策略优先级

按以下顺序尝试，一旦成功即停止：

1. **`npx skills add`**：Codex skill 管理器，最推荐。
2. **`git clone` + 复制子目录**：`npx skills add` 失败或没有 `npx` 时使用。
3. **github-raw 下载 zip + 复制子目录**：没有 `git` 时的兜底。

## 按需安装指定 skill

本仓库没有统一的“根 skill”。用户想用什么，就安装什么：

| 需求 | 安装目标 |
| --- | --- |
| 用凡人修仙传风格改写 | `humanizer-zh-fanrenxiuxianzhuan` |
| 用修真聊天群风格改写 | `humanizer-zh-xiuzhenliaotianqun` |
| 用黎明之剑风格改写 | `humanizer-zh-limingzhijian` |
| 列出/安装风格，或引导新建 | `humanizer-zh-novel-finder` |
| 从长篇小说生成新风格 | `humanizer-zh-novel-meta` |

### 方式 1：按 skill 名称安装（最推荐）

```bash
npx skills add klarkxy/humanizer-zh-novel --skill humanizer-zh-fanrenxiuxianzhuan -g -y
```

其他可用名称：

- `humanizer-zh-xiuzhenliaotianqun`
- `humanizer-zh-limingzhijian`
- `humanizer-zh-novel-finder`
- `humanizer-zh-novel-meta`

### 方式 2：按子路径安装

如果管理器不支持 `--skill`，尝试 `--subpath`：

```bash
npx skills add klarkxy/humanizer-zh-novel --subpath skills/humanizer-zh-fanrenxiuxianzhuan -g -y
```

> 不同管理器支持的参数名可能不同（`--skill`、`-s`、`--subpath` 等）。如果都不可用，改用 git 或 github-raw 方案。

## 兜底 1：git 直接下载安装

`npx skills add` 内部也会拉取 Git 仓库。该命令失败时，直接用 `git clone` 更可控。

### Windows PowerShell

```powershell
$repoUrl = "https://github.com/klarkxy/humanizer-zh-novel.git"
$skillName = "humanizer-zh-fanrenxiuxianzhuan"  # 改成你要安装的 skill 名称
$skillsDir = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $env:USERPROFILE ".codex\skills" }
$target = Join-Path $skillsDir $skillName
$tmp = Join-Path $env:TEMP "humanizer-zh-novel-install"

if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
git clone $repoUrl $tmp

New-Item -ItemType Directory -Force $skillsDir | Out-Null
if (Test-Path $target) { Remove-Item -Recurse -Force $target }
Copy-Item -Recurse -Path (Join-Path $tmp "skills\$skillName") -Destination $target -Force

Remove-Item -Recurse -Force $tmp
```

### macOS / Linux

```bash
repo_url="https://github.com/klarkxy/humanizer-zh-novel.git"
skill_name="humanizer-zh-fanrenxiuxianzhuan"  # 改成你要安装的 skill 名称
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
target="$skills_dir/$skill_name"
tmp="$(mktemp -d)"

git clone "$repo_url" "$tmp"
mkdir -p "$skills_dir"
rm -rf "$target"
cp -R "$tmp/skills/$skill_name" "$target"

rm -rf "$tmp"
```

### 欢迎测试他人的 fork 或 PR

想抢先试用社区贡献的新风格或修复，可以在复制到 skills 目录前切换到他人在 fork 或 PR 中的分支：

```bash
cd "$tmp"
git fetch origin pull/<PR_NUMBER>/head:<LOCAL_BRANCH_NAME>
git checkout <LOCAL_BRANCH_NAME>
```

Windows 同样使用 `git fetch` 与 `git checkout`，再复制目标子目录。

试用后若觉得不错，可回到 GitHub 页面给该 PR 点赞或留言；agent 不代替你合并、发布或提交。

## 兜底 2：通过 github-raw 下载安装

本方案不依赖本地 `git`，直接从 GitHub 下载仓库压缩包，只复制需要的子目录到 skills 目录。适用于没有 `npx` 也没有 `git` 的环境。

### Windows PowerShell

```powershell
$repoUrl = "https://github.com/klarkxy/humanizer-zh-novel/archive/refs/heads/main.zip"
$skillName = "humanizer-zh-fanrenxiuxianzhuan"  # 改成你要安装的 skill 名称
$skillsDir = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $env:USERPROFILE ".codex\skills" }
$target = Join-Path $skillsDir $skillName
$tmp = Join-Path $env:TEMP "humanizer-zh-novel-install"
$zip = Join-Path $tmp "humanizer-zh-novel-main.zip"

if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp }
New-Item -ItemType Directory -Force $tmp | Out-Null

Invoke-WebRequest -Uri $repoUrl -OutFile $zip -UseBasicParsing
Expand-Archive -Path $zip -DestinationPath $tmp -Force

New-Item -ItemType Directory -Force $skillsDir | Out-Null
if (Test-Path $target) { Remove-Item -Recurse -Force $target }
Move-Item -Path (Join-Path $tmp "humanizer-zh-novel-main\skills\$skillName") -Destination $target -Force

Remove-Item -Recurse -Force $tmp
```

### macOS / Linux

```bash
repo_url="https://github.com/klarkxy/humanizer-zh-novel/archive/refs/heads/main.zip"
skill_name="humanizer-zh-fanrenxiuxianzhuan"  # 改成你要安装的 skill 名称
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
tmp="$(mktemp -d)"

mkdir -p "$skills_dir"
rm -rf "$skills_dir/$skill_name"

curl -L -o "$tmp/humanizer-zh-novel-main.zip" "$repo_url"
unzip -q "$tmp/humanizer-zh-novel-main.zip" -d "$tmp"
mv "$tmp/humanizer-zh-novel-main/skills/$skill_name" "$skills_dir/$skill_name"

rm -rf "$tmp"
```

## 安装后校验

进入安装目录：

```text
<skills-dir>/<skill-name>
```

必须确认：

- `SKILL.md` 存在。
- 如果安装的是成品风格，`skills/humanizer-zh-novel-meta/scripts/validate_skill.py` 可以通过（先把校验脚本复制到可访问位置，或定位到本仓库的元生成器目录）。

如果本机有 skill-creator 校验脚本，可运行：

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

校验脚本不存在时，不要失败退出；报告“已复制安装，未运行 skill-creator 校验”。

## 完成后回复用户

安装成功后，简短回复：

```text
已安装 <skill-name>。你可以说：使用 $<skill-name> 按凡人修仙传风格改写这段中文小说正文。
```

## 约束

- 不要把仓库安装成 `humanizer` 或 `humanizer-zh-novel` 这样的目录名；必须按 skill 名称安装（如 `humanizer-zh-fanrenxiuxianzhuan`）。
- 不要提交或复制用户本地小说原文到 Git。
- 如果目标目录已存在，可以覆盖安装，但不要删除 skills 目录里的其他 skill。
- 鼓励试用他人 fork 或 PR 中的新风格，但 agent 只帮忙拉取代码，不会代替你合并、发布或提交。

## 协议

- 根项目（元生成器、校验脚本、公共模板、风格发现器等）采用 SATA-2.0 License。
- 每个 `skills/humanizer-zh-<slug>/` 作品风格由不同贡献者提交，其 LICENSE 以该目录下的 `LICENSE` 文件或 `_meta.json` 中的 `license` 字段为准；如无特别说明，默认与根项目一致。
