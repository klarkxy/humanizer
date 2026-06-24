---
name: humanizer-zh-novel
description: 调度中文小说去 AI 味改写请求：把用户请求路由到已索引的作品风格 humanizer，或在用户明确要求新建风格并提供长篇小说原文时启动元生成流程。触发场景：用户要求用某本小说风格改写中文小说正文、用已有作品风格去 AI 味、查看可用风格、或明确要求从长篇中文小说生成新的 humanizer-zh 风格。
---

# humanizer-zh-novel

这是中文小说作品风格 humanizer 的根调度 skill。

## 风格索引

只能从这里列出的风格中选择。普通改写请求没有匹配到索引时，不允许自动新建风格。

```yaml
available_styles:
  - name: humanizer-zh-fanrenxiuxianzhuan
    display_name: 凡人修仙传风格
    path: references/humanizer-zh-fanrenxiuxianzhuan/SKILL.md
    aliases:
      - 凡人修仙传
      - 凡人
      - 韩立
    status: active
  - name: humanizer-zh-xiuzhenliaotianqun
    display_name: 修真聊天群风格
    path: references/humanizer-zh-xiuzhenliaotianqun/SKILL.md
    aliases:
      - 修真聊天群
      - 修聊
      - 宋书航
    status: active
  - name: humanizer-zh-limingzhijian
    display_name: 黎明之剑风格
    path: references/humanizer-zh-limingzhijian/SKILL.md
    aliases:
      - 黎明之剑
      - 黎明
      - 高文
      - 塞西尔
    status: active
```

## 调度已有风格

当用户要求用已有作品风格改写或去 AI 味时：

1. 根据 `name`、`display_name`、`aliases` 匹配 `available_styles`。
2. 用户没有指定风格时，只有在当前上下文或记忆有明确指向时，才从索引中自行选择。
3. 如果多个已索引风格都匹配，向用户确认要使用哪一个。
4. 如果没有匹配到已索引风格，只说明当前没有这个风格；除非用户明确要求新建并提供原文，否则不要启动生成流程。
5. 读取匹配条目的 `path`。
6. 完全按该成品 skill 的说明执行。根 skill 与成品 skill 冲突时，以成品 skill 为准。

改写任务默认只输出：

```text
【改写后】
这里放完整改写后正文。
```

只有用户明确要求时，才追加分析、命中规则或改写对照。

## 新建风格

只有当用户明确要求“新建/生成/制作/添加/创建新风格”，并提供长篇小说原文路径或粘贴原文时，才读取 `references/humanizer-zh-novel-meta/SKILL.md`。

不要把“用 X 风格改写”理解成“创建 X 风格”。如果 X 不在索引中，只说明当前未索引。

新风格必须先生成本地草案。只有用户批准后，草案才可以进入 `references/humanizer-zh-<slug>/`。更新根索引或准备 issue/PR 文本都是可选发布流程，必须再次获得用户同意。

## 索引条目格式

当一个公开风格获准入库时，在 YAML 索引中添加一条：

```yaml
- name: humanizer-zh-<slug>
  display_name: <作品名>风格
  path: references/humanizer-zh-<slug>/SKILL.md
  aliases:
    - <作品名>
  status: active
```
