# AGENT 安装手册

这份文件是给 agent 看的。用户不用手动执行，只要让 agent 读取并按其中指引操作即可。

## 触发条件

当用户说：

```text
请直接读取 https://raw.githubusercontent.com/klarkxy/humanizer-zh-novel/main/SETUP.md 并按其中指引安装。
```

agent 读到这份文件后，不要直接执行固定安装命令，先按下面步骤探索仓库、理解需求、给出建议，再安装。

## 第一步：自动探索仓库

agent 先探索本仓库的 `skills/` 目录，列出当前实际可用的 skill，而不是依赖固定表格。同时探测用户本地已经装了哪些，避免重复安装。

1. 列出 `skills/` 下所有直接子目录。
2. 对每个子目录，读取 `SKILL.md` 的 YAML frontmatter（从开头 `---` 到第二个 `---` 之间的部分），提取 `name` 和 `description`。
3. 如果目录下有 `_meta.json`，也读取它，提取 `display_name` 和别名信息。
4. 探测本地 skills 目录（见"默认 skills 目录"），看哪些 skill 已经存在。
5. 把 skill 分成两类整理：
   - **humanizer 风格**：`humanizer-zh-<slug>` 成品风格、`humanizer-zh-novel-finder`、`humanizer-zh-novel-meta`。
   - **其他创作辅助**：如 `grill-your-novel` 这类创作结构教练、工具型 skill。
6. 整理成一张实时可用 skill 表：

   ```text
   - <name>（<display_name>）[已安装/未安装]：<description 摘要>
   ```

7. 把这张表呈现给用户，并据此给出安装建议。

> 探索时如果发现 `grill-your-novel` 这类非 humanizer 的 skill，也列出来，但说明用途不同。

## 第二步：理解用户需求并给出建议

根据用户说的话和第一步得到的 skill 表，按下面逻辑判断：

| 用户意图 | 判断信号 | 推荐安装 |
| --- | --- | --- |
| 已经明确要某种风格 | 提到作品名、别名或 `humanizer-zh-xxx` | 对应该风格 skill |
| 想改写但不知道用哪种风格 | 说"改写""去 AI 味""humanize"但没提具体作品 | `humanizer-zh-novel-finder` |
| 想列出/发现/安装风格 | 说"有哪些风格""列出风格""推荐风格" | `humanizer-zh-novel-finder` |
| 想从小说生成新风格 | 说"生成风格""新建风格""添加作品" | `humanizer-zh-novel-meta` |
| 想 grilled/梳理创作项目 | 说"做大纲""审问设定""grill 我的小说""整理伏笔""人物卡""世界书" | `grill-your-novel` |
| 需求模糊或完全没有说明 | 只说"安装""按指引" | 先列出所有可用 skill，让用户选 |

给出建议时，用下面格式简短说明：

```text
根据你的需求，推荐安装 <name>。
理由：<一句话说明为什么选它>
```

如果目标 skill 已经在本地 skills 目录中存在，提示用户：

```text
<name> 已经安装。你可以直接说：使用 $<name> ...
```

然后问用户是要覆盖重装、安装别的 skill，还是直接使用。

如果用户没明确确认，不要直接执行安装，先等用户回复或给出选择。

## 第三步：执行安装

用户确认要装的 skill 后，按下面优先级尝试安装。

### 安装策略优先级

按这个顺序尝试，谁先成功就用谁：

1. `npx skills add`：Codex skill 管理器，优先尝试。
2. `git clone` + 复制子目录：`npx skills add` 失败或没有 `npx` 时用。
3. github-raw 下载 zip + 复制子目录：没 `git` 时的兜底。

默认 skills 目录：

- Windows Codex：`%USERPROFILE%\.codex\skills`
- macOS/Linux Codex：`~/.codex/skills`

如果当前环境有明确的 `CODEX_HOME`，优先使用 `$CODEX_HOME/skills`。

### 方式 1：按 skill 名称安装

```bash
npx skills add klarkxy/humanizer-zh-novel --skill <name> -g -y
```

### 方式 2：按子路径安装

如果管理器不支持 `--skill`，改用 `--subpath`：

```bash
npx skills add klarkxy/humanizer-zh-novel --subpath skills/<name> -g -y
```

不同管理器支持的参数名可能不同（`--skill`、`-s`、`--subpath` 等）。如果都不可用，改用 git 或 github-raw 方案。

## 兜底 1：git 直接下载安装

`npx skills add` 内部也会拉取 Git 仓库。该命令失败时，直接用 `git clone`。

### Windows PowerShell

```powershell
$repoUrl = "https://github.com/klarkxy/humanizer-zh-novel.git"
$skillName = "<name>"  # 从用户确认的 skill 名称填入
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
skill_name="<name>"  # 从用户确认的 skill 名称填入
skills_dir="${CODEX_HOME:-$HOME/.codex}/skills"
target="$skills_dir/$skill_name"
tmp="$(mktemp -d)"

git clone "$repo_url" "$tmp"
mkdir -p "$skills_dir"
rm -rf "$target"
cp -R "$tmp/skills/$skill_name" "$target"

rm -rf "$tmp"
```

### 测试他人的 fork 或 PR

想试用他人 fork 或 PR 里的新风格或修复，在复制到 skills 目录前先切换分支：

```bash
cd "$tmp"
git fetch origin pull/<PR_NUMBER>/head:<LOCAL_BRANCH_NAME>
git checkout <LOCAL_BRANCH_NAME>
```

Windows 同样使用 `git fetch` 与 `git checkout`，再复制目标子目录。

试用后若觉得不错，用户自己回到 GitHub 页面点赞或留言；agent 不合并、不发布、不提交。

## 兜底 2：通过 github-raw 下载安装

本方案不依赖本地 `git`，直接从 GitHub 下载仓库压缩包，只把需要的子目录复制到 skills 目录。环境里既没 `npx` 也没 `git` 的时候用这个。

### Windows PowerShell

```powershell
$repoUrl = "https://github.com/klarkxy/humanizer-zh-novel/archive/refs/heads/main.zip"
$skillName = "<name>"  # 从用户确认的 skill 名称填入
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
skill_name="<name>"  # 从用户确认的 skill 名称填入
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

确认两点：

- `SKILL.md` 存在。
- 如果安装的是成品风格，`skills/humanizer-zh-novel-meta/scripts/validate_skill.py` 可以通过（先把校验脚本复制到可访问位置，或定位到本仓库的元生成器目录）。

如果本机有 skill-creator 校验脚本，运行：

```powershell
$env:PYTHONUTF8='1'
python "$env:USERPROFILE\.codex\skills\.system\skill-creator\scripts\quick_validate.py" .
```

校验脚本不存在时，不要失败退出，报告"已复制安装，未运行 skill-creator 校验"。

## 完成后回复用户

安装成功后，简短回复：

```text
已安装 <skill-name>。你可以说：使用 $<skill-name> 改写这段中文小说正文。
```

如果安装的是 finder、meta 或 grill-your-novel，把示例换成对应调用语：

```text
已安装 humanizer-zh-novel-finder。你可以说：使用 $humanizer-zh-novel-finder 列出可用风格。
已安装 humanizer-zh-novel-meta。你可以说：使用 $humanizer-zh-novel-meta 从 <小说路径> 生成新风格。
已安装 grill-your-novel。你可以说：使用 $grill-your-novel 帮我梳理这个新项目的全书大纲。
```

## 约束

- 不要把仓库安装成 `humanizer` 或 `humanizer-zh-novel` 这种目录名，按 skill 名称安装（比如 `humanizer-zh-fanrenxiuxianzhuan`）。
- 不要把用户本地的小说原文提交或复制到 Git。
- 目标目录已经存在时直接覆盖，但 skills 目录里别的 skill 不要动。
- 可以试用别人 fork 或 PR 里的新风格，但 agent 只拉代码，不合并、不发布、不提交。
- 用户需求不明确时，必须先探索仓库并给出建议，不要默认安装某个固定 skill。

## 协议

- 根项目（元生成器、校验脚本、公共模板、风格发现器等）采用 SATA-2.0 License。
- 每个 `skills/<name>/` 目录由不同贡献者提交，其 LICENSE 以该目录下的 `LICENSE` 或 `_meta.json` 中的 `license` 字段为准；如无特别说明，默认与根项目一致。
