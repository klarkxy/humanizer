# humanizer-zh-novel

这个仓库收录了中文小说 humanizer 和其他中文创作辅助 skill，以 monorepo 形式组织。每个 `skills/<name>/` 都是独立 skill，skills.sh 这类管理器可以直接识别。

## 一句话安装

把下面这句粘贴给你的 agent：

```text
请直接读取 https://raw.githubusercontent.com/klarkxy/humanizer-zh-novel/main/SETUP.md 并按其中指引安装。
```

## 仓库结构

```text
humanizer-zh-novel/
├── skills/                           # 独立 skill 集合
│   ├── humanizer-zh-novel-finder/    # 风格发现与安装引导
│   ├── humanizer-zh-novel-meta/      # 元生成器：从长篇小说生成新风格
│   ├── humanizer-zh-<slug>/          # 作品风格成品
│   │   ├── SKILL.md
│   │   └── _meta.json
│   └── grill-your-novel/             # 中文长篇创作结构教练（非 humanizer）
├── tmp/                              # 本地工作产物，被 .gitignore 排除
├── README.md
├── SETUP.md
└── LICENSE
```

## 可用风格

| 名称 | 显示名 | 别名 |
| --- | --- | --- |
| humanizer-zh-fanrenxiuxianzhuan | 凡人修仙传风格 | 凡人修仙传、凡人、韩立 |
| humanizer-zh-xiuzhenliaotianqun | 修真聊天群风格 | 修真聊天群、修聊、宋书航 |
| humanizer-zh-limingzhijian | 黎明之剑风格 | 黎明之剑、黎明、高文、塞西尔 |
| humanizer-zh-niliuchunzheniandai | 逆流纯真年代风格 | 逆流纯真年代、纯真年代、人间武库、九二年代 |

## 其他创作辅助 skill

| 名称 | 用途 |
| --- | --- |
| grill-your-novel | 中文长篇/短篇/散文/非虚构创作的结构教练。帮你做大纲、人物卡、世界书、伏笔管理、正文门禁、TODO 和 proposal，不是替你做 canon。 |

## 安装某个作品风格

每个风格都能独立安装：

```bash
npx skills add klarkxy/humanizer-zh-novel --skill humanizer-zh-fanrenxiuxianzhuan -g -y
```

如果管理器不支持 `--skill`，改用 `--subpath`：

```bash
npx skills add klarkxy/humanizer-zh-novel --subpath skills/humanizer-zh-fanrenxiuxianzhuan -g -y
```

安装后调用：

```text
使用 $humanizer-zh-fanrenxiuxianzhuan 改写这段中文小说正文。
```

## 安装其他创作辅助 skill

```bash
npx skills add klarkxy/humanizer-zh-novel --skill grill-your-novel -g -y
```

安装后调用：

```text
使用 $grill-your-novel 帮我梳理这个新项目的全书大纲。
```

## 发现风格或新建风格

不确定有哪些风格、想安装某个风格、或想从长篇小说生成新风格时，安装风格发现器：

```bash
npx skills add klarkxy/humanizer-zh-novel --skill humanizer-zh-novel-finder -g -y
```

然后调用：

```text
使用 $humanizer-zh-novel-finder 列出可用风格。
```

## 长篇输入门槛

元生成器 `humanizer-zh-novel-meta` 只接受稳定长篇输入：

- 至少 20 个可识别正文章节。
- 至少 100000 个中文字符。
- 必须有稳定章节标记；不会把无章节长文按字数硬切。

## 公开元数据

`_meta.json` 只记录公开摘要，不记录原文路径、本地证据路径、规则快照路径或任何可复现的私有信息。

## 贡献新 skill

每个 skill 都是独立的 `skills/<name>/` 目录。

### 贡献 humanizer 作品风格

1. 先开 issue 确认：说明要新增的作品风格，确认没有其他人正在做。
2. 准备长篇小说原文：中文、至少 20 章、至少 10 万字，且你有权使用。
3. 使用元生成器生成风格：安装 `humanizer-zh-novel-meta` 后，调用：
   ```text
   请用 humanizer-zh-novel-meta 从 <小说路径或文本> 生成 humanizer-zh-<slug> 风格。
   ```
4. 本地验证：确保 `skills/humanizer-zh-novel-meta/scripts/validate_skill.py` 通过，并实际改写 1–2 段 AI 味文本检查效果。
5. 提交 PR：把 `skills/humanizer-zh-<slug>/SKILL.md` 和 `_meta.json` 作为最小集合提交。不要把小说原文、本地分析文件或工作产物提交到 Git。

### 贡献其他创作辅助 skill

非 humanizer 的 skill（如创作结构教练、工具脚本等）也可以提交。每个 skill 独立成目录，包含自己的 `SKILL.md`，可选 `_meta.json` 和 `LICENSE`。提交前说明它解决什么创作问题、如何触发、依赖什么环境。

### 版权说明

- 每个 skill 目录的 LICENSE 由贡献者自己定；没写就默认沿用根项目 SATA-2.0 License。
- `_meta.json` 里可以放作者、来源说明，但原文路径和本地私有路径不能写进去。

## 协议

- 根项目（元生成器、校验脚本、公共模板、风格发现器、grill-your-novel 等）采用 [SATA-2.0 License](LICENSE)。
- 每个 `skills/<name>/` 目录由不同贡献者提交，其 LICENSE 由该目录下的 `LICENSE` 或 `_meta.json` 中的 `license` 字段说明；如无特别说明，默认与根项目一致。
