# 中文长篇小说写作 AI Skill

一个面向 AI Agent 的网文长篇写作技能包，提供从立项到连载的分层工作流：

`总大纲 -> 子大纲 -> 风格卡 -> 正文 -> 设定集 -> 伏笔统计`

并提供章节级“叙事引擎”脚本，支持项目体检、写前上下文构建、交付前门禁验收。

## 适用场景

- 写中文长篇网文/小说
- 从 0 搭建剧情结构和章节规划
- 按样文抽取风格并保持文风一致
- 持续维护世界观与角色设定
- 追踪长线伏笔并统计回收进度

## 核心能力

- 分层创作：先大纲、后子大纲、再正文，降低长篇失控风险
- 风格管控：通过“样文摘录 + 风格卡”稳定文风
- 设定同步：写作过程中同步更新人物、势力、术法、术语等
- 伏笔闭环：用 CSV 跟踪伏笔状态并自动生成统计报告

## 仓库结构

```text
novelist/
├── webnovel-outline-suboutline-draft-zh/   # Skill 本体（SKILL.md、scripts、templates）
├── references/                             # 补充写作技法参考
├── 大纲和子大纲/                            # 你的项目内容（示例）
├── 设定集/                                  # 你的项目内容（示例）
├── 风格参考/                                # 你的项目内容（示例）
└── 正文/                                    # 你的项目内容（示例）
```

## 快速开始（人类阅读）

> 人类需要阅读本节，LLM 不需要。

经过个人测试，个人推荐使用如下指令：

```plaintext
现在，先为我生成 1~8 章的内容。对于每一章均要求：
需要逐章节生成。在每一章生成结束后，必须保证所有状态、伏笔及读者面信息被落盘。如果章节情况不满足全局设置，则迭代这些章节、扩增字数，直到满足。
这会是一个很漫长的工作。
上述条件全部满足后进入下一章。
```

建议一次生成的章节数不要太多，否则会翻车。

## 快速开始（LLM 阅读）

> LLM 需要阅读本节，人类不需要。

1. 准备环境：`Python 3.9+`
2. 初始化一个新作品目录：

```bash
python webnovel-outline-suboutline-draft-zh/scripts/init_story_workspace.py --root . --name 我的作品
```

3. 在生成的作品目录中按以下顺序创作：
- `01-总大纲.md`
- `02-子大纲.md`
- `风格参考/01-样文摘录.md`
- `风格参考/02-风格卡.md`
- `正文/第NNN章.md`
- `04-设定集.md`
- `05-长线伏笔.csv`
- `09-读者面信息.md`

4. 使用叙事引擎命令形成闭环：

```bash
# 项目体检
python webnovel-outline-suboutline-draft-zh/scripts/narrative_engine.py doctor --project <项目目录>

# 写前准备（自动生成本章上下文）
python webnovel-outline-suboutline-draft-zh/scripts/narrative_engine.py context --project <项目目录> --chapter <章节号> --create-chapter

# 交付前门禁（自动刷新长线统计并生成门禁报告）
python webnovel-outline-suboutline-draft-zh/scripts/narrative_engine.py gate --project <项目目录> --chapter <章节号>
```

`gate` 会输出 `08-叙事引擎报告.md`。只要有 `FAIL`，建议先修复再交付。

## 伏笔统计命令（LLM 阅读）

> LLM 需要阅读本节，人类不需要。下同。

更新 `05-长线伏笔.csv` 后执行：

```bash
python webnovel-outline-suboutline-draft-zh/scripts/foreshadow_stats.py \
  --csv <项目目录>/05-长线伏笔.csv \
  --out <项目目录>/06-长线统计.md \
  --current-chapter <当前章节号>
```

会生成：

- 状态分布（埋设中/回收中/已回收/弃用）
- 活跃伏笔完成率
- 未完成清单
- 逾期待回收清单（提供 `--current-chapter` 时）

## 伏笔 CSV 字段（LLM 阅读）

表头固定为：

`id,主线,伏笔内容,首次埋设章节,计划回收章节,实际回收章节,状态,关联人物,备注`

建议状态值只使用：

- `埋设中`
- `回收中`
- `已回收`
- `弃用`

## 建议工作方式（LLM 阅读）

- 每新增一章就同步更新一次设定与伏笔
- 每次改动 `05-长线伏笔.csv` 后立即重建 `06-长线统计.md`
- 长篇过程中优先“先结构后文采”，避免返工

## 来源

Powered by: https://github.com/PenglongHuang/chinese-novelist-skill.git
