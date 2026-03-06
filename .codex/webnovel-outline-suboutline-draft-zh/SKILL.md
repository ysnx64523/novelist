---
name: webnovel-outline-suboutline-draft-zh
description: 使用中文推进网文创作的分层工作流与章节门禁引擎：先生成总大纲，再拆解子大纲，在正文前强制生成章节分镜纲中间件，基于风格参考提炼风格卡后产出正文，并在同一项目文件夹内同步维护设定集、角色状态与长线伏笔统计。支持通过 scripts/narrative_engine.py 执行项目体检、章节上下文生成、章节分镜纲生成、交付前门禁验收。当用户要求写网文、扩写章节、搭建剧情结构、保持文风一致、按样文仿写风格、维护世界观设定、维护角色行动逻辑或追踪伏笔回收时使用此技能。
---

# 网文分层写作（中文）

## 目标
在一个单独项目文件夹中维护完整链路：
- `总大纲`：故事骨架与长线设计。
- `子大纲`：章节级拆解与场景推进。
- `风格参考`：样文、风格卡与执行约束。
- `正文`：最终可直接阅读的章节内容。
- `设定集`：人物、世界、势力、规则等持续更新。
- `角色状态`：角色健康、情报掌握与行动模式切换。
- `伏笔统计`：长线事件埋设、回收、完成率、逾期项。

## 单文件夹约束
先运行脚本初始化工作区，再在该目录内完成所有写作与更新：

```bash
python scripts/init_story_workspace.py --root <父目录> --name <作品名>
```

初始化后只在该目录工作，默认文件如下：
- `00-项目说明.md`
- `01-总大纲.md`
- `02-子大纲.md`
- `04-设定集.md`
- `05-长线伏笔.csv`
- `06-长线统计.md`
- `07-当前角色状态.md`
- `09-读者面信息.md`
- `风格参考/`
- `风格参考/01-样文摘录.md`
- `风格参考/02-风格卡.md`
- `正文/`（正文章节目录）
- `正文/第001章.md`（首章模板）

初始化后，先执行一次项目体检：

```bash
python scripts/narrative_engine.py doctor --project <项目目录>
```

## 叙事引擎入口命令（必须执行）
以下命令组成“写前准备 -> 分镜中间件 -> 成稿验收”的强制闭环：

1) 项目体检（每次开工前）

```bash
python scripts/narrative_engine.py doctor --project <项目目录>
```

2) 生成本章上下文（写章前）

```bash
python scripts/narrative_engine.py context --project <项目目录> --chapter <章节号> --create-chapter
```

生成文件：`正文/.engine/第NNN章-上下文.md`，其中包含：
- 本章子大纲摘录
- 上一章结尾参考
- 活跃伏笔清单
- 角色行动记录（最近5条）

3) 生成本章分镜纲（写章前，必须）

```bash
python scripts/narrative_engine.py storyboard --project <项目目录> --chapter <章节号> --target-chars 3500 --create-context
```

生成文件：`正文/.engine/第NNN章-分镜纲.md`，其中包含：
- 场景数量建议（随目标字数自动估算）
- 场景级执行骨架（目的/冲突/动作链/信息投放/钩子）
- 章节描写硬约束（开头强冲突、对话占比、章末推进）

4) 章节门禁验收（交付前）

```bash
python scripts/narrative_engine.py gate --project <项目目录> --chapter <章节号>
```

门禁会自动：
- 刷新 `06-长线统计.md`
- 生成 `08-叙事引擎报告.md`
- 对“占位符未清理、子大纲缺失、伏笔ID未登记、角色状态未回写”等问题给出 FAIL/WARN/PASS

### 门禁规则
- 只要出现 `FAIL`，该章不得交付，必须修复后重跑 `gate`。
- `WARN` 允许交付，但需要在“本轮同步更新”中说明风险。
- 如果用户明确要求“先看草稿”，可先给草稿，但必须标注“未过门禁”。

## 标准流程

### 1) 产出总大纲
使用 `references/outline-template.md` 的结构填写：
- 明确核心卖点、主线冲突、阶段转折、结局兑现。
- 在总大纲里预先标注可追踪的长线事件 ID（如 `F001`）。
- 需要更多剧情结构方案时，补充读取 `references/writing-techniques/plot-structures.md`。

### 2) 拆解子大纲
使用 `references/suboutline-template.md` 按章节拆解：
- 每章写清目标、冲突、转折、钩子。
- 每章必须标记“埋设伏笔/回收伏笔”并引用对应事件 ID。
- 设计章节开头和章节结尾时，补充读取 `references/writing-techniques/chapter-guide.md` 与 `references/writing-techniques/hook-techniques.md`。

### 3) 建立风格参考
优先读取并维护 `风格参考/`：
- `风格参考/01-样文摘录.md`：存放用户给出的参考片段。
- `风格参考/02-风格卡.md`：提炼可执行的风格约束。
- 保证文本内的场景描写和细节描写与 `设定集/微观细节库.md` 内的内容相匹配。

当用户提出“按某作者/某段文字风格写”或“保持已有章节文风一致”时：
- 必须先更新风格卡，再生成正文。
- 仅迁移风格特征，不复写样文原句。

### 4) 生成正文
使用 `references/draft-template.md` 编写正文，并将章节写入 `正文/` 目录：
- 文件命名统一为 `正文/第NNN章.md`（如 `正文/第001章.md`、`正文/第002章.md`）。
- 正文前先读取 `风格参考/02-风格卡.md`，严格执行其中“执行约束”。
- 正文前先读取 `07-当前角色状态.md`，确保角色行为与当前行动规划模式一致。
- 正文前先读取 `09-读者面信息.md` 与 `references/writing-techniques/information-guide.md`，控制本章信息投放密度与悬念节奏。
- 保持与子大纲的事件顺序一致。
- 场景中兑现子大纲承诺的关键信息与节奏。
- 每章完稿后回写 `07-当前角色状态.md` 的健康、情报与模式切换记录。
- 对用户回复时，先给可直接阅读的正文内容，再给更新说明。
- 对话密集场景优先读取 `references/writing-techniques/dialogue-writing.md`。
- 需要扩写时读取 `references/writing-techniques/content-expansion.md`。
- 完稿前读取 `references/writing-techniques/quality-checklist.md` 与 `references/writing-techniques/consistency.md` 做自检。
- 写作前必须先跑一次 `narrative_engine.py context` 生成本章上下文。
- 写作前必须先跑一次 `narrative_engine.py storyboard` 生成本章分镜纲，并按分镜纲逐场景落地。

### 5) 更新设定集
按 `references/setting-bible-template.md` 同步维护：
- 新角色、新地点、新规则、新势力关系出现后立即登记。
- 若设定发生变更，保留“旧设定 -> 新设定 -> 变更原因”。
- 角色塑造不足时补充读取 `references/writing-techniques/character-building.md` 和 `references/writing-techniques/character-template.md`。

### 6) 维护伏笔与统计
手动更新 `05-长线伏笔.csv` 后运行：

```bash
python scripts/foreshadow_stats.py --csv <项目目录>/05-长线伏笔.csv --out <项目目录>/06-长线统计.md --current-chapter <当前章节号>
```

执行后得到：
- 状态分布（埋设中/回收中/已回收/弃用）
- 完成率（已回收占活跃伏笔）
- 未完成清单
- 逾期待回收项（当提供 `--current-chapter` 时）

### 7) 更新角色状态与行动模式
每章写作前后都手动更新 `07-当前角色状态.md`，模板使用 `references/character-state-template.md`：
- 至少维护四类必填信息：健康状态、当前行动规划模式、下一步行动模式、角色记忆、当前角色知晓情报。
- 行动模式优先从模板中的“行动模式词典”选取；新增模式时补充“用途/进入条件/退出条件”。
- 每次模式切换都要记录触发条件与目标，避免角色行为跳变。
- 角色健康或情报变化若影响世界观硬设定，需同步回写 `04-设定集.md`。

### 8) 章节门禁与交付
每章交付前必须运行：

```bash
python scripts/narrative_engine.py gate --project <项目目录> --chapter <章节号>
```

执行要求：
- 若 `08-叙事引擎报告.md` 出现 FAIL：先修复，再重跑。
- 若出现 WARN：在交付说明中明确列出。
- 门禁通过后再按“回复格式”输出正文与同步更新摘要。

### 9) 读者方向可获得信息确认
每章写作前后都手动更新 `09-读者面信息.md`（若文件不存在则先创建），并按 `references/writing-techniques/information-guide.md` 控制信息量：
- 写前更新：确认本章计划给读者的“新增信息、确认信息、误导信息、保留信息（不揭示）”。
- 写前更新：给本章设置信息预算，避免一次性解释过多设定或连续抛谜不回收。
- 写前更新：为本章至少设计 1 个“角色记忆点特征”（可视符号/口头禅/反差行为/极端选择/代价性习惯等），并确保其在本章有可感知落地，强度达到“读完可复述、可区分、可传播”，禁止弱记忆点和泛化人设词。
- 写后更新：记录本章实际投放的信息条目和设定内容，并标注“已兑现/延后到下章/废弃”。
- 写后更新：记录本章结尾新增悬念，明确下章优先回应项。
- 保持“每章至少 1 条有效信息推进（世界观/角色关系/主线因果三者之一）”。

### 10) 如果需一次性生成多章内容
逐章节生成。在每一章生成结束后，必须保证：
- 所有状态、伏笔被落盘。
- 章节情况满足全局设置。

如果有任何一条内容不满足，则迭代这些章节、扩增字数，直到满足。 这会是一个很漫长的工作。
上述条件全部满足后进入下一章。

## 写作技法库（必须按需参考）
`references/writing-techniques/` 内的文件为写作技法总库。触发相关任务时必须读取对应文件，而不是只依赖默认模板。

- `information-guide.md`：控制每一章对读者提供的信息量。
- `chapter-guide.md`：章节开头、前20%抓人、开篇错误规避。
- `chapter-template.md`：章节结构底稿（章节概要/正文/备注）。
- `character-building.md`：人物弧光、行为逻辑、关系塑造。
- `character-template.md`：人物档案模板。
- `consistency.md`：跨章节一致性与状态跟踪。
- `content-expansion.md`：扩写手段（细节/内心/感官/支线）。
- `dialogue-writing.md`：对话目的性、简洁度、格式规范。
- `hook-techniques.md`：悬念钩子库与章节收束策略。
- `outline-template.md`：另一套大纲模板（与本技能默认大纲模板并存）。
- `plot-structures.md`：三幕式、英雄之旅等结构框架。
- `quality-checklist.md`：交付前质量检查项。

如果 `references/outline-template.md` 与 `references/writing-techniques/outline-template.md` 冲突：
- 默认优先 `references/outline-template.md`（本技能流程模板）。
- 用户明确要求“按写作技法模板”时，切换为 `references/writing-techniques/outline-template.md`。

## 回复格式
按以下顺序输出，保证用户先拿到正文：
1. `正文成稿`
2. `本轮同步更新`（总大纲/子大纲/设定集）
3. `门禁结果`（引用 `08-叙事引擎报告.md` 的 PASS/WARN/FAIL 总数）
4. `伏笔统计摘要`（引用 `06-长线统计.md` 核心数字）
5. `角色状态更新摘要`（引用 `07-当前角色状态.md` 的关键变化）

如果输出格式不满足用户需求，则迭代直到满足为止。

## 参考文件读取策略
- 需要规划故事框架时读取 `references/outline-template.md`。
- 需要拆章节时读取 `references/suboutline-template.md`。
- 需要控制文风时读取 `风格参考/01-样文摘录.md` 和 `风格参考/02-风格卡.md`。
- 需要维护世界观时读取 `references/setting-bible-template.md`。
- 需要生成章节中间件时读取 `references/storyboard-template.md`。
- 需要理解伏笔字段时读取 `references/foreshadow-schema.md`。
- 需要维护角色状态与行动模式时读取 `references/character-state-template.md`。
- 需要控制章节信息密度、分配揭示节奏时读取 `references/writing-techniques/information-guide.md`，并同步维护 `09-读者面信息.md`。
- 需要写作技法时按任务读取 `references/writing-techniques/*.md` 对应文件。
- 需要执行章节门禁或构建写作上下文时读取 `scripts/narrative_engine.py` 的命令帮助。
