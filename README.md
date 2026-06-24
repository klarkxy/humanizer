# humanizer

安装和 agent 接入方式请先看 [SETUP.md](./SETUP.md)。

中文小说 `humanizer-zh-novel` skill 仓库。

本仓库采用一个根调度 skill 加多个 reference skill 的结构：

```text
humanizer/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── humanizer-zh-novel-meta/
│   │   ├── SKILL.md
│   │   ├── agents/
│   │   ├── references/
│   │   └── scripts/
│   └── humanizer-zh-<slug>/
│       ├── SKILL.md
│       └── _meta.json
└── tmp/
```

## 目录角色

- `SKILL.md`：根调度入口。它只从内置 YAML 索引里选择已有风格，或在用户显式要求新建时引导读取元 skill。
- `references/humanizer-zh-novel-meta/`：元生成 skill。从用户提供的长篇中文小说路径或文本生成本地草案。
- `references/humanizer-zh-<slug>/`：作品风格成品 skill。每个目录都是一个符合 skill-creator 结构的独立 skill。

## 核心规则

- 未索引风格不能自动新建。新建必须由用户显式提出，并提供原文路径或原文文本。
- 新建成品必须先生成到 `tmp/humanizer-zh-<slug>/draft/`，经用户确认后才进入 `references/`。
- 成品目录进入 Git 时只包含 `SKILL.md` 和 `_meta.json`。
- 本地原文、证据、分析和 PR 草稿都放在 `tmp/`，由 `.gitignore` 排除。
- 成品 skill 默认做重度作品风改写，但不新增剧情事实，不迁移世界观术语。

## 长篇输入门槛

元 skill 只接受稳定长篇输入：

- 至少 20 个可识别正文章节。
- 至少 100000 个中文字符。
- 必须有稳定章节标记；不会把无章节长文按字数硬切。

## 公开元数据

`_meta.json` 只记录公开摘要，不记录原文路径、本地证据路径、规则快照路径或任何可误认为可复现的私有信息。
