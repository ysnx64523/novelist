#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "05-长线伏笔.csv"
STAT_PATH = ROOT / "06-长线统计.md"
ROLE_PATH = ROOT / "07-当前角色状态.md"
READER_PATH = ROOT / "09-读者面信息.md"

BASE_IDS = [f"F{n:03d}" for n in range(1, 21)]

CH_META = {
    21: {
        "title": "成绩公布",
        "action": "完成广播三元组首轮实战取证，并在成绩界面发现措辞重命名",
        "result": "‘通过’在部分端口显示为‘净化认证’，命定色盘护符热榜登顶",
        "hook": "马特提出当面谈话请求，要求她暂停追查",
    },
    22: {
        "title": "父亲来访",
        "action": "与马特线下对谈并全程离线录音",
        "result": "‘远离蓝月’在听感层再度被反向误听，亲密场景冲突升级",
        "hook": "蕾雅发来守护色打卡群邀请，要求当天入群",
    },
    23: {
        "title": "打卡群",
        "action": "进入守护色打卡群并记录替词积分规则",
        "result": "群任务与平台推送完成绑定，零点词条自动生成",
        "hook": "次日将执行替换任务，系统开始按‘词义表现’评分",
    },
    24: {
        "title": "替换任务",
        "action": "执行围观对照实验并验证‘未动作判参与’",
        "result": "系统发放‘词义表现优异’勋章，静默参与被制度化",
        "hook": "城区快闪志愿者招募开启，要求线下到场",
    },
    25: {
        "title": "快闪招募",
        "action": "与诺亚潜入快闪招募现场做隐蔽记录",
        "result": "站位按词义评分分配，触发前缀进入公开流程",
        "hook": "次日口号联动测试将与校园广播联动",
    },
    26: {
        "title": "口号联动",
        "action": "完成‘词语+情绪+动作’三组耦合样本采集",
        "result": "同一句口号可稳定触发同向动作，广播再现‘撤离/集合’分叉",
        "hook": "菲娜决定公开发布原始片段，验证平台处置逻辑",
    },
    27: {
        "title": "事故改写",
        "action": "分层发布原始片段并同步链上存证",
        "result": "平台将事故叙事重写为沉浸式演出，原链路持续降权",
        "hook": "萝洁邀请加入语义对齐互助群，要求提交原义卡样本",
    },
    28: {
        "title": "对齐互助群",
        "action": "加入互助群并启动日更新义/旧义对照表",
        "result": "词条漂移速率可量化，同词24小时内出现多次改写",
        "hook": "诺曼与杰德将上线链上词典，菲娜需做首批测试",
    },
    29: {
        "title": "链上词典",
        "action": "参与原义镜像库内测并建立手写备份词典",
        "result": "直链可达但搜索入口压权明显，停留时长持续偏低",
        "hook": "平台将以‘认知负担’标签对词典传播做反制",
    },
    30: {
        "title": "反向标签",
        "action": "实测‘认知负担’标签对传播链路的削弱效果",
        "result": "多数同学30秒内跳出词典，热榜出现#原义党在制造焦虑#",
        "hook": "海伦拟发起校内公开辩论，菲娜需准备纸卡兜底方案",
    },
}

NEW_FORESHADOWS = {
    "F021": ("命名重写线", "成绩界面‘通过’改写为‘净化认证’", "第21章", "第21章", "菲娜", "阶段2命名层验证"),
    "F022": ("亲密误听线", "父女关键句在高压下反向误听复发", "第22章", "第36章", "菲娜 马特", "亲密场景冲突累积"),
    "F023": ("打卡闭环线", "守护色打卡群日替词任务绑定积分", "第23章", "第24章", "菲娜 蕾雅", "任务规则可复现"),
    "F024": ("静默参与线", "围观状态被判定为已参与并发勋章", "第24章", "第24章", "菲娜 诺亚", "参与边界重写"),
    "F025": ("招募分流线", "快闪按词义评分自动分配站位", "第25章", "第27章", "菲娜 诺亚", "动作层分流"),
    "F026": ("口号耦合线", "同口号同向动作与撤离/集合分叉并存", "第26章", "第34章", "菲娜 校方", "跨场景复现"),
    "F027": ("改写处置线", "事故原始片段被系统改写并降权", "第27章", "第32章", "菲娜 萝洁", "处置链路留痕"),
    "F028": ("互助群线", "原义卡日更机制与双轨分发建立", "第28章", "第32章", "萝洁 菲娜", "组织化反制"),
    "F029": ("词典入口线", "链上词典可达但搜索权重被压低", "第29章", "第68章", "诺曼 杰德 菲娜", "可见性战争"),
    "F030": ("标签反制线", "‘认知负担’标签将纠偏行为污名化", "第30章", "第65章", "菲娜 群体用户", "反向叙事成型"),
}


def row_status(fid: str, upto: int):
    if fid == "F021":
        return ("第21章", "已回收" if upto >= 21 else "埋设中")
    if fid == "F022":
        return ("", "埋设中" if upto >= 22 else "埋设中")
    if fid == "F023":
        if upto >= 24:
            return ("第24章", "已回收")
        return ("", "埋设中")
    if fid == "F024":
        if upto >= 24:
            return ("第24章", "已回收")
        return ("", "埋设中")
    if fid == "F025":
        if upto >= 27:
            return ("第27章", "已回收")
        if upto >= 25:
            return ("", "回收中")
        return ("", "埋设中")
    if fid == "F026":
        if upto >= 26:
            return ("", "回收中")
        return ("", "埋设中")
    if fid == "F027":
        if upto >= 27:
            return ("", "回收中")
        return ("", "埋设中")
    if fid == "F028":
        if upto >= 28:
            return ("", "埋设中")
        return ("", "埋设中")
    if fid == "F029":
        if upto >= 29:
            return ("", "埋设中")
        return ("", "埋设中")
    if fid == "F030":
        if upto >= 30:
            return ("", "埋设中")
        return ("", "埋设中")
    return ("", "埋设中")


def update_csv(upto: int):
    rows = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    existing = {r["id"]: r for r in rows}

    # 回收F020（记录方法线）
    if "F020" in existing and upto >= 24:
        existing["F020"]["状态"] = "已回收"
        existing["F020"]["实际回收章节"] = "第24章"
        existing["F020"]["备注"] = "广播三元组记录法完成首轮实战"

    for fid, data in NEW_FORESHADOWS.items():
        mainline, content, first_ch, plan_ch, people, note = data
        actual, status = row_status(fid, upto)
        existing[fid] = {
            "id": fid,
            "主线": mainline,
            "伏笔内容": content,
            "首次埋设章节": first_ch,
            "计划回收章节": plan_ch,
            "实际回收章节": actual,
            "状态": status,
            "关联人物": people,
            "备注": note,
        }

    ordered_ids = [f"F{n:03d}" for n in range(1, 31)]
    fields = ["id", "主线", "伏笔内容", "首次埋设章节", "计划回收章节", "实际回收章节", "状态", "关联人物", "备注"]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for fid in ordered_ids:
            if fid in existing:
                writer.writerow(existing[fid])


def update_stats():
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    counts = {"埋设中": 0, "回收中": 0, "已回收": 0, "已弃用": 0}
    for r in rows:
        s = r["状态"]
        counts[s] = counts.get(s, 0) + 1

    active = [r for r in rows if r["状态"] in {"埋设中", "回收中"}]
    lines = [
        f"# 长线统计（当前至第{UPTO}章）",
        "",
        "## 基本信息",
        f"- 当前章节：第{UPTO}章",
        f"- 伏笔总数：{total}",
        "",
        "## 状态分布",
        f"- `埋设中`：{counts.get('埋设中', 0)}",
        f"- `回收中`：{counts.get('回收中', 0)}",
        f"- `已回收`：{counts.get('已回收', 0)}",
        f"- `已弃用`：{counts.get('已弃用', 0)}",
        "",
        "## 当前活跃伏笔（节选）",
    ]
    for r in active[:8]:
        lines.append(f"- `{r['id']}`：{r['伏笔内容']}（状态：{r['状态']}）")
    lines.append("")
    STAT_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def update_role(upto: int):
    lines = [
        "# 当前角色状态（预实验）",
        "",
        "## 当前时间锚点",
        f"- 当前章节：第{upto}章（已完成）",
        "- 主视角：菲娜",
        f"- 下章触发：{CH_META[upto]['hook'] if upto in CH_META else '待生成'}",
        "",
        "## 角色状态总览",
        "| 角色 | 健康状态 | 精神状态 | 资源状态 | 当前行动模式 | 当前首要目标 |",
        "| --- | --- | --- | --- | --- | --- |",
        "| 菲娜 | 轻度疲劳 | 高警惕、流程化执行 | 三元组模板+离线录音+纸本对照 | 侦察取证 | 把原句证据链从单点样本扩展到可复跑体系 |",
        "| 诺亚 | 健康 | 紧绷理性 | 差分工具+双端监听 | 侦察取证 | 锁定机制证据并排除噪声样本 |",
        "| 蕾雅 | 健康 | 摇摆不稳 | 校园触达中等 | 社交博弈 | 在群体压力下维持关系与自我解释一致 |",
        "| 萝洁 | 健康 | 高压持续 | 互助群节点+镜像链路 | 侦察取证 | 保真链不断裂 |",
        "| 蓝月 | 健康 | 高负载稳定 | 算力与分发链路充足 | 资源经营 | 维持耦合扩散效率 |",
        "| 海伦 | 轻度疲劳 | 克制稳定 | 校内公开窗口 | 社交博弈 | 守住最低限公开纠偏空间 |",
        "",
        "## 章节行动记录（第21章起）",
        "| 章节 | 标题 | 菲娜关键动作 | 结果 | 下一触发 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for ch in range(21, upto + 1):
        meta = CH_META[ch]
        lines.append(f"| 第{ch:03d}章 | {meta['title']} | {meta['action']} | {meta['result']} | {meta['hook']} |")
    lines.append("")
    ROLE_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def update_reader(upto: int):
    known = [
        "语义异常已从单点错词升级为动作层耦合问题。",
        "菲娜与诺亚采用‘原句-位置-时间’三元组记录法持续取证。",
        "公开窗口易被同构话术压制，保真链路成为主战场。",
    ]
    if upto >= 24:
        known.append("‘静默参与’与词义勋章证明参与边界被系统重定义。")
    if upto >= 27:
        known.append("事故叙事可被快速改写，原始片段可见性被平台主动压低。")
    if upto >= 29:
        known.append("链上词典可达但搜索入口被稀释，读者停留时长显著下降。")
    if upto >= 30:
        known.append("‘认知负担’标签形成反向叙事，热榜开始污名化纠偏行为。")

    suspense = [
        "`keyword_to_action_map`的完整阈值与触发边界仍未拿到。",
        "显示层替换是否按用户画像差异渲染尚未完全证实。",
        "蓝月在扩散阶段的真实目标（可控扩散/失控验证）仍不透明。",
    ]

    lines = [
        f"# 读者面信息（当前至第{upto}章）",
        "",
        "## 当前时间点",
        f"- 已完成章节：第1章~第{upto}章",
        f"- 当前读者位置：第{upto}章末",
        "",
        "## 读者已明确知道",
    ]
    for i, item in enumerate(known, 1):
        lines.append(f"{i}. {item}")
    lines += ["", "## 核心悬念", *[f"- {x}" for x in suspense], "", "## 下一章触发", f"- {CH_META[upto]['hook'] if upto in CH_META else '待生成'}", ""]
    READER_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--upto", type=int, required=True)
    args = parser.parse_args()
    UPTO = args.upto
    if UPTO < 21 or UPTO > 30:
        raise SystemExit("--upto must be 21..30")

    update_csv(UPTO)
    update_stats()
    update_role(UPTO)
    update_reader(UPTO)
    print(f"updated_state_to={UPTO}")
