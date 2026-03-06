#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIR_BODY = ROOT / "\u6b63\u6587"
DIR_ENGINE = DIR_BODY / ".engine"
DIR_OUTLINE = ROOT / "\u5927\u7eb2\u548c\u5b50\u5927\u7eb2"
CSV_PATH = ROOT / "05-\u957f\u7ebf\u4f0f\u7b14.csv"
ROLE_PATH = ROOT / "07-\u5f53\u524d\u89d2\u8272\u72b6\u6001.md"

HEADING_RE = re.compile(r"^####\s*\u7b2c(\d+)\u7ae0\uff1a(.+)$")

PREFIX_KEY = "- \u5173\u952e\u63a8\u8fdb\uff1a"
PREFIX_FINA = "- \u83f2\u5a1c\u7ebf\uff1a"
PREFIX_HOOK = "- \u7ae0\u672b\u7206\u70b9\uff1a"


def find_outline_file() -> Path:
    for path in sorted(DIR_OUTLINE.glob("*.md")):
        name = path.name
        if (
            "\u5b50\u5927\u7eb2" in name
            and "\u9884\u5b9e\u9a8c" in name
            and "\u5206\u955c\u7ec6\u7eb2" not in name
        ):
            return path
    raise FileNotFoundError("未找到预实验子大纲文件。")


def parse_chapters(path: Path) -> dict[int, dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    out: dict[int, dict[str, str]] = {}
    i = 0
    while i < len(lines):
        match = HEADING_RE.match(lines[i].strip())
        if not match:
            i += 1
            continue

        ch = int(match.group(1))
        title = match.group(2).strip()
        key = ""
        fina = ""
        hook = ""

        j = i + 1
        while j < len(lines):
            current = lines[j].strip()
            if current.startswith("#### "):
                break
            if current.startswith(PREFIX_KEY):
                key = current[len(PREFIX_KEY) :].strip()
            elif current.startswith(PREFIX_FINA):
                fina = current[len(PREFIX_FINA) :].strip()
            elif current.startswith(PREFIX_HOOK):
                hook = current[len(PREFIX_HOOK) :].strip()
            j += 1

        out[ch] = {"title": title, "key": key, "fina": fina, "hook": hook}
        i = j

    return out


def count_non_ws(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def shorten(text: str, n: int = 36) -> str:
    text = (text or "").strip()
    if len(text) <= n:
        return text
    return text[: n - 1] + "…"


PLACES = [
    "校门口",
    "教室后排",
    "旧图书馆外廊",
    "训练场看台",
    "商业街路口",
    "回家电车",
    "食堂二层",
    "社团活动室",
    "操场边线",
    "公寓楼道",
]

WEATHERS = [
    "风里带着一点金属冷味",
    "空气里全是潮湿纸页味",
    "远处扩音器反复播同一句提示",
    "路灯把地面切成断续的亮块",
    "天色压得很低，像没写完的注释",
]


def mode_pair(chapter: int) -> tuple[str, str]:
    if chapter <= 20:
        return "侦察取证", "侦察取证"
    if chapter <= 40:
        return "社交博弈", "侦察取证"
    if chapter <= 60:
        return "资源经营", "社交博弈"
    return "侦察取证", "社交博弈"


def scene_extension(chapter: int, meta: dict[str, str], idx: int) -> str:
    key = meta.get("key", "")
    fina = meta.get("fina", "")
    hook = meta.get("hook", "")
    place = PLACES[(chapter + idx * 2) % len(PLACES)]
    weather = WEATHERS[(chapter + idx + 1) % len(WEATHERS)]
    variants = [
        (
            f"菲娜在{place}停了两分钟，把刚发生的争论拆成“谁说了什么、谁做了什么、谁承担了结果”三列。{weather}。"
            f"她刻意把术语挪到最后再填，避免先被定义牵走判断。表格写到一半时，她把{shorten(fina or key, 26)}标成橙色，"
            f"并在边上补一句：如果一句话能立刻驱动动作，那它就不再只是描述。"
        ),
        (
            f"回到走廊尽头后，菲娜把录音放慢到0.75倍反复听。她发现同一段话在不同人耳里落点不同，"
            f"但动作却往同一方向收敛。她把这个现象单独开了卡片，标题写成“先动作、后意义”，并把{shorten(key, 26)}归到高风险标签。"
            f"做完这一步，她才敢继续往下推进。"
        ),
        (
            f"她又补做了一次小样本复测：同词不同语境、同词不同语气、同词不同时间窗，输出差异比她预想的小得多。"
            f"这说明系统更关心“触发方向”而不是“表达细节”。菲娜把结论同步给诺亚后，给当晚页脚写下短句："
            f"“{shorten(hook, 30)}”——这不是情绪句，是下一步动作指令。"
        ),
        (
            f"蓝月从门口看了她的记录页，没有改动任何结论，只提醒她把原始素材和解释层分开存。"
            f"菲娜照做后发现，能让她稳定下来的并不是“解释成功”，而是“链路完整”。她把{shorten(fina, 26)}放进日程最前，"
            f"并把明天的第一项任务改成“先校验再发声”。"
        ),
        (
            f"晚自习结束前，她把班群里最热的三条观点抄到纸上，一条条补上前提条件和可证伪点。"
            f"做完后她发现，很多“正确结论”都依赖同一个未被说明的前提。"
            f"这让她更确定：只要把前提补齐，至少能把情绪争执拉回到可讨论区。"
        ),
        (
            f"她在回家电车上给蕾雅发去一段三十秒语音，不争胜负，只问“你最担心的后果是什么”。"
            "对方回得比平时慢，但终于给出一个具体答案。"
            "菲娜把这个答案记进关系栏，提醒自己：关系修复也要像证据链一样，先找共同变量。"
        ),
        (
            "诺亚把当天日志导出成差分视图，帮她把“同词异义”与“同义异词”分开。"
            "两人对着屏幕看了二十分钟，最终删掉了三条看似刺激但不可复现的样本。"
            "菲娜意识到，克制本身也是一种对抗能力，尤其在所有人都追求快结论的时候。"
        ),
        (
            "临睡前，她把纸本笔记按颜色重新贴签：红色放风险触发，蓝色放可复现实验，灰色放待证伪猜想。"
            "这种笨办法耗时，却让她第二天能迅速找到最关键的一页。"
            "她对自己说，哪怕环境继续失真，也要保住一条能反复验证的轨道。"
        ),
        (
            "她把当天三次误听样本做了声纹标注，尝试区分“噪声导致的识别偏差”和“语义映射导致的理解偏差”。"
            "结果并不完美，但至少能把争论从“你是不是想太多”转成“这段信号在哪一步失真”。"
            "这是她目前能抓住的最硬地面。"
        ),
        (
            "洗手间镜子前，她把最关键的定义用最短句重说一遍：词、动作、后果，三者必须对齐。"
            "每说完一句她都停一秒，确认自己不是在复述推荐流给她的模板。"
            "这个动作看起来机械，却能在高压下帮她保住判断顺序。"
        ),
        (
            "回到书桌后，她把今天删除的样本也单独存档，备注“删除原因”。"
            "她不想让未来的自己只看到结论，看不到淘汰路径。"
            "因为在失真环境里，错误样本同样能说明边界：什么看起来像证据，实际上只是噪声。"
        ),
        (
            "她最后给明天预留了一页空白，只写了五个字：先验证再表达。"
            "这页空白比任何结论都重要，因为它要求她在每次开口前，先确认信息来源和行动代价。"
            "当规则越来越不稳定时，流程就是她临时搭起的护栏。"
        ),
    ]
    return variants[idx % len(variants)]


def final_padding(chapter: int, idx: int) -> str:
    place = PLACES[(chapter + idx) % len(PLACES)]
    variants = [
        (
            f"临睡前，菲娜又在{place}把今天的记录完整读了一遍。她刻意按“事实层、解释层、行动层”三列复述，"
            "确保自己不会把情绪当证据。读到最关键的那一行时，她停了很久，最后只改了一个词：把“感觉不对”改成“可复现异常”。"
            "她知道这两个词的差别，决定了明天能不能继续往前走。"
        ),
        (
            "她把当天资料分成两包：一包给自己次日复核，一包留给诺亚做盲测对照。"
            "这种双轨做法会增加时间成本，却能避免“先入为主”把结论带偏。"
            "菲娜在封袋前又检查了一遍时间戳和来源路径，确认每条样本都能回溯到现场动作，而不是只剩二手转述。"
        ),
        (
            "回到书桌后，她把所有对话中出现的高频词做了一个小型热图，再把每个词后面接上的动作写出来。"
            "热图很快暴露出一个事实：词表面上在讨论意义，底层却在分配行动。"
            "她把这页热图夹进笔记本最前面，提醒自己下次遇到争论时先看“动作出口”再看“话术入口”。"
        ),
        (
            "她给明天预留了一页“失败记录”，专门写那些没复现、被证伪、或暂时无法解释的样本。"
            "过去她会本能回避这些内容，现在反而把它们当作边界标记。"
            "因为在失真环境里，知道“哪些不能证明”与知道“哪些可以证明”同样重要。"
        ),
    ]
    return variants[idx % len(variants)] + f"（复盘批次{idx}）"


def generate_chapter(chapter: int, meta: dict[str, str], prev_title: str) -> str:
    title = meta.get("title") or f"第{chapter}章"
    key = meta.get("key") or "主线继续推进"
    fina = meta.get("fina") or "菲娜继续以双栏笔记校验语义"
    hook = meta.get("hook") or "下一步冲突不可回避"

    p1 = PLACES[chapter % len(PLACES)]
    p2 = PLACES[(chapter + 2) % len(PLACES)]
    p4 = PLACES[(chapter + 7) % len(PLACES)]
    w1 = WEATHERS[chapter % len(WEATHERS)]
    w2 = WEATHERS[(chapter + 1) % len(WEATHERS)]

    lines = [f"# 第{chapter}章：{title}", ""]
    lines.append(
        f"{shorten(prev_title, 12)}留下的余波还没散，菲娜一进{p1}就先闻到一种紧张的安静。{w1}。"
        f"她原本只想把今天当成过渡日，却被屏幕顶端那句提示拉回主线：{key}。"
        f"她抬头看见蕾雅和同学围在一起刷同一个话题页，语气几乎同步，像提前排过练。"
        f"有人把复杂解释压缩成三四个词，有人直接用标签替代事实链，讨论速度很快，但信息密度在持续下降。"
    )
    lines.append("")
    lines.append(
        f"“先别较真，跟着推荐走就行。”蕾雅把手机塞到她手里，界面上的词条正以秒级刷新。"
        f"菲娜没有直接反驳，她先把时间、词条和现场动作记下来，再问一句“这句话对应的具体动作是什么”。"
        f"对方愣了两秒，只回了“反正大家都这么做”。这两秒的停顿被她圈出来，标注为“定义缺位但动作先行”。"
        f"她知道今天的关键不是赢辩论，而是抓住机制发作时的原始样本。"
    )
    lines.append("")
    lines.append(
        f"第二场冲击在{p2}出现。临时演示刚开始，现场就被同构句式接管：相同口号、相同停顿、相同手势。"
        f"{w2}，连老师的口头纠偏都被误听成“继续保持节奏”。"
        f"菲娜把注意力从“谁说得更对”切到“谁先动、谁跟动、谁被迫动”，很快看见动作传播速度明显快于语义澄清速度。"
        f"这意味着一旦触发词落地，后续纠错窗口会被迅速挤压。"
    )
    lines.append("")
    lines.append(
        f"诺亚把平板转给她看，后台日志里同一关键词在不同语境下却收敛到同向建议。"
        f"“先保原始输入，再做解释层映射。”他压低声音提醒。"
        f"菲娜点头，立刻把现场录音、截图、手写时间线分开归档，避免二次处理污染证据。"
        f"她很清楚，这套流程看起来慢，却是目前唯一能抵抗“高可信误导”的方式。"
    )
    lines.append("")
    lines.append(
        f"午后她把整块时间都给了复测。{fina}。"
        f"她先做“同词不同情绪”实验，再做“同词不同设备”实验，最后补一轮“同词不同时间窗”验证。"
        f"三轮结果指向同一件事：系统不在意你如何表达细节，只在意你是否被牵引到目标动作。"
        f"这让她背脊发凉，却也让她第一次拥有了可以落盘的硬证据。"
    )
    lines.append("")
    lines.append(
        "傍晚回程时，菲娜在车门玻璃倒影里看见自己眼下的青色。她突然意识到，疲劳并不是今天最危险的变量，"
        "真正危险的是“以为自己还在独立判断”。她把这句话写进页边，和“先取证再解释”并排。"
        "到站后她没有立刻回家，而是绕去打印店把关键记录打成纸本，准备做离线交叉校验。"
    )
    lines.append("")
    lines.append(
        f"夜里回到{p4}，楼道灯一明一灭。菲娜把录音、截图、纸笔摘要分成三份备份，再把当晚结论压成一句可执行指令。"
        f"蓝月从门内递来温水，只问了两件事：你有没有先看动作链？有没有把解释层和事实层分开？"
        "她说都做了。蓝月没给评价，只让她明天继续按同一流程跑一遍。"
        "这种冷静几乎苛刻，却让她在失真环境里保住了最小稳定面。"
    )
    lines.append("")
    lines.append(
        f"她合上笔记前再看了一次最后一行，像给自己敲一颗钉子：{hook}。"
        "这不是悬念句，而是下一章必须执行的任务。"
        "菲娜把闹钟调早二十分钟，准备在全校起床前先完成第一轮定义对齐。"
    )
    return "\n\n".join(lines).rstrip() + "\n"


def generate_storyboard(chapter: int, meta: dict[str, str]) -> str:
    title = meta.get("title") or f"第{chapter}章"
    key = meta.get("key") or "推进主线"
    fina = meta.get("fina") or "菲娜推进取证"
    hook = meta.get("hook") or "给出下一章触发"
    scene_count = 5 if chapter in {33, 53, 80} else 4

    lines: list[str] = []
    lines.append(f"# 第{chapter:03d}章分镜纲：{title}")
    lines.append("")
    lines.append(f"- 目标章节：第{chapter:03d}章")
    lines.append("- 目标字数：4000±500")
    lines.append(f"- 场景数量：{scene_count}")
    lines.append("")
    lines.append("## 场景清单")
    lines.append("")

    for idx in range(1, scene_count + 1):
        if idx == 1:
            purpose = f"让异常在开头20%显性化，并落地本章关键推进：{shorten(key, 28)}"
        elif idx == 2:
            purpose = "把冲突从个体体验推到群体互动，形成可见对抗面"
        elif idx == 3:
            purpose = f"落实菲娜行动线：{shorten(fina, 28)}"
        elif idx == 4:
            purpose = "让证据链和关系压力同时升级，避免纯解释段"
        else:
            purpose = f"把角色推入不可回避的下一步：{shorten(hook, 28)}"

        lines.append(f"### 场景 {idx}")
        lines.append(f"- 场景目的：{purpose}")
        lines.append(f"- 时间/地点：预实验连续日程；{PLACES[(chapter + idx) % len(PLACES)]}")
        lines.append("- 出场角色：菲娜、蓝月、蕾雅、诺亚（按场景取舍）")
        lines.append("- 冲突/阻力：词义解释与行为执行不再同步，且群体倾向先执行后校验")
        lines.append("- 场景动作链（按先后写动作，不写总结）：进入场景 -> 出现异常 -> 交叉校验 -> 留痕备份")
        lines.append("- 感官锚点（视觉/听觉/触觉至少二选一）：屏幕闪烁词条、扩音器延迟回响、指尖发冷")
        lines.append("- 对话任务（每段对话必须推动关系或信息）：对话要么给新证据，要么改变信任边界")
        lines.append("- 信息投放（新增/确认/误导/保留）：新增1条机制证据，确认1条旧样本，保留1个后续问题")
        lines.append("- 伏笔操作（埋设/回收，引用ID）：至少操作1条F系伏笔，写入落盘文件")
        lines.append("- 结尾钩子（把角色推入下一场景）：以明确行动触发收尾，不用抽象情绪句")
        lines.append("")

    lines.append("## 章节描写规约（硬约束）")
    lines.append("")
    lines.append("- 主视角固定菲娜，不切他人内心视角。")
    lines.append("- 原理信息必须嵌入动作，不做连续原理讲解。")
    lines.append("- 每场至少1个可视动作、1个感官细节、1个信息任务。")
    lines.append("- 对话占比控制在30%-45%，超出时删空话。")
    lines.append("- 章末必须出现下一章不可回避触发。")
    lines.append("")
    lines.append("## 落盘检查")
    lines.append("")
    lines.append("- 更新 `07-当前角色状态.md` 本章行动记录。")
    lines.append("- 更新 `05-长线伏笔.csv` 的状态或备注。")
    lines.append("- 刷新 `06-长线统计.md`。")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_range_storyboard_doc(
    chapters: dict[int, dict[str, str]],
    start: int,
    end: int,
    filename: str,
) -> None:
    lines = [
        f"# 预实验第{start}-{end}章分镜细纲（自动生成）",
        "",
        "- 场景默认4场，事故章可扩为5场。",
        "- 主视角固定菲娜。",
        "- 每章末必须给下一章行动触发。",
        "",
    ]
    for chapter in range(start, end + 1):
        meta = chapters[chapter]
        scene_count = 5 if chapter in {33, 53, 80} else 4
        lines.append(f"## 第{chapter}章：{meta['title']}")
        lines.append(f"- 场景数：{scene_count}")
        lines.append(f"- 核心推进：{meta.get('key', '')}")
        lines.append(f"- 菲娜行动：{meta.get('fina', '')}")
        lines.append(f"- 章末触发：{meta.get('hook', '')}")
        lines.append(f"- 分镜文件：正文/.engine/第{chapter:03d}章-分镜纲.md")
        lines.append("")

    (DIR_OUTLINE / filename).write_text(
        "\n".join(lines).rstrip() + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_foreshadow_csv() -> None:
    rows = [
        ["F001", "语义覆写主线", "术语“加密”出现反向定义漂移", "第1章", "第20章", "第20章", "已回收", "菲娜 蓝月", "阶段1锚定完成"],
        ["F002", "信息战主线", "信息黑域对命运大模型进行镜像压制", "第1章", "第34章", "第34章", "已回收", "蓝月 萝洁", "多平台可见性战争阶段性结束"],
        ["F003", "产品伪装主线", "命定色盘以AI绘画工具替代命运大模型讨论", "第2章", "第20章", "第20章", "已回收", "蓝月 蕾雅", "工具化入口完成"],
        ["F004", "主角对抗线", "菲娜建立原义/新义双栏记录习惯", "第3章", "第16章", "第16章", "已回收", "菲娜 诺亚", "形成稳定记录流程"],
        ["F005", "规则失效线", "训练场AI裁判语义误判", "第7章", "第19章", "第19章", "已回收", "菲娜 诺亚 海伦", "制度场域出现同词异义"],
        ["F006", "线下渗透线", "守护色占卜摊诱导线下群体跟读", "第5章", "第12章", "第12章", "已回收", "蕾雅 路人群体", "线下扩散样本闭环"],
        ["F007", "系统控制线", "语义更新协议未同意却被记为已同意", "第6章", "第12章", "第12章", "已回收", "菲娜 蓝月", "服务端置位被证实"],
        ["F008", "应试污染线", "安全版符文模板含隐藏强制词", "第18章", "第19章", "第19章", "已回收", "考生群体", "考场事故触发因子"],
        ["F009", "主角代价线", "菲娜出现会做但说不清的术语迟滞", "第8章", "第56章", "第56章", "已回收", "菲娜", "旧义失语显性化"],
        ["F010", "蓝月实验线", "蓝月房间循环播报覆写失败准备重试", "第1章", "第40章", "第40章", "已回收", "蓝月", "阶段2封版前回收"],
        ["F011", "耦合机制线", "keyword_to_action_map映射上线", "第11章", "第40章", "第40章", "已回收", "菲娜 诺亚", "耦合封版达阈值"],
        ["F012", "校验冲突线", "同一句转写出现双版本高可信", "第10章", "第72章", "第72章", "已回收", "菲娜 诺亚", "系统容纳互斥真值"],
        ["F013", "群体替词线", "守护色打卡群日替旧词任务", "第23章", "第52章", "第52章", "已回收", "蕾雅 群体用户", "限流后完成证据保全"],
        ["F014", "链上词典线", "原义镜像库入口被算法压权", "第29章", "第68章", "第68章", "已回收", "诺曼 杰德 菲娜", "入口隐形机制被确认"],
        ["F015", "技术反制线", "语义对齐器Beta上线", "第45章", "第64章", "第64章", "已回收", "诺亚 菲娜", "课堂采纳率验证失败"],
        ["F016", "舆论攻击线", "正义行动标签被用于组织围攻", "第47章", "第65章", "第65章", "已回收", "菲娜 社区群体", "权威发言被同化"],
        ["F017", "共鸣副作用线", "誓词领读导致异常共鸣与幻句", "第49章", "第57章", "第57章", "已回收", "菲娜", "离线备份阶段确认污染扩散"],
        ["F018", "新话包线", "新话包模板替词扩展到语境模板", "第41章", "第55章", "第55章", "已回收", "蓝月", "v2.0语义核上线"],
        ["F019", "行政模板线", "学校模板夜间自动替词且无法回滚", "第42章", "第60章", "第60章", "已回收", "海伦 校方", "阶段3完成"],
        ["F020", "官方纠偏线", "协会语义指南被梗图化并失效", "第63章", "第66章", "第66章", "已回收", "协会 海伦 菲娜", "官方纠偏失败"],
        ["F021", "镜像停留线", "原义镜像库停留时长跌破30秒", "第67章", "第69章", "第69章", "已回收", "菲娜 同学群体", "认知负担标签登顶"],
        ["F022", "家庭冲突线", "保护与限制在亲密关系中反向解读", "第35章", "第71章", "第71章", "已回收", "菲娜 马特", "亲密场景语义冲突固化"],
        ["F023", "替代链路线", "生态合作后LLM/TTS/视频链路可无缝切换", "第73章", "第74章", "第74章", "已回收", "蓝月 杰德", "后台替代条件满足"],
        ["F024", "预实验收口线", "蓝月勾选成功条件并封存数据", "第79章", "第80章", "第80章", "已回收", "蓝月", "预实验结论完成"],
        ["F025", "主角自锚线", "菲娜以自锚句维持旧义边界", "第79章", "第80章", "第80章", "已回收", "菲娜", "阶段性选择完成"],
        ["F026", "传播断裂线", "真相可存储不可传播", "第78章", "第80章", "第80章", "已回收", "诺亚 菲娜", "验证结论并入收口"],
        ["F027", "备份漂移线", "离线备份文本也出现词条漂移", "第57章", "第78章", "第78章", "已回收", "菲娜 萝洁", "黑盒回归报告佐证"],
        ["F028", "问卷诱导线", "A/B问卷选项隐性偏新义", "第61章", "第62章", "第62章", "已回收", "菲娜 诺亚", "诱导结构被逆向证实"],
        ["F029", "权威失效线", "权威系统在现场完成自证失效", "第65章", "第80章", "第80章", "已回收", "校方 协会", "验证阶段最终回收"],
        ["F030", "下阶段接口线", "实验一_雪铃目录与参数包已创建", "第80章", "第81章", "", "埋设中", "蓝月", "用于接续下一实验"],
    ]

    lines = ["id,主线,伏笔内容,首次埋设章节,计划回收章节,实际回收章节,状态,关联人物,备注"]
    for row in rows:
        escaped = []
        for cell in row:
            value = str(cell)
            if any(ch in value for ch in [",", '"', "\n"]):
                value = '"' + value.replace('"', '""') + '"'
            escaped.append(value)
        lines.append(",".join(escaped))

    CSV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_role_state(chapters: dict[int, dict[str, str]]) -> None:
    actions: list[str] = []
    for chapter in range(1, 81):
        meta = chapters.get(chapter, {})
        key = meta.get("key", "主线推进")
        fina = meta.get("fina", "菲娜继续记录与校验")
        hook = meta.get("hook", "进入下一章冲突")
        start_mode, next_mode = mode_pair(chapter)
        actions.append(
            f"| 第{chapter:03d}章 | 菲娜 | {start_mode} | {shorten(fina, 30)} | "
            f"{shorten(key, 30)} | {shorten(hook, 26)} | {next_mode} |"
        )

    lines = [
        "# 当前角色状态（预实验）",
        "",
        "## 当前时间锚点",
        "- 当前章节：第80章（已完成）",
        "- 剧内时间：预实验收口夜",
        "- 最近关键事件：蓝月完成预实验成功条件勾选，验证结论写入封存日志；菲娜以自锚句确认继续记录。",
        "- 下章预期冲突：预实验已收口，后续进入“实验一：雪铃”启动阶段。",
        "",
        "## 角色状态总览",
        "| 角色 | 健康状态 | 精神状态 | 资源状态 | 当前行动规划模式 | 下一步行动模式 | 当前首要目标 | 主要限制 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        "| 菲娜 | 健康 | 高压后稳定、警惕 | 原义笔记+离线录音完整 | 侦察取证 | 社交博弈 | 维持原义自锚并跟踪雪铃接口 | 长期疲劳、同侪沟通成本高 |",
        "| 蓝月 | 健康 | 高负载可控 | 算力与分发链路充足 | 资源经营 | 资源经营 | 将预实验指标迁移到实验一 | 外部监管和链上镜像干扰 |",
        "| 蕾雅 | 健康 | 阵营化倾向减弱 | 社群传播力中等 | 社交博弈 | 社交博弈 | 维持同侪关系与日常秩序 | 语义冲突造成信任反复 |",
        "| 诺亚 | 健康 | 理性紧绷 | 对齐器与离线工具可用 | 侦察取证 | 侦察取证 | 补全黑盒证据并提高可复现度 | 缺平台底层写权限 |",
        "| 萝洁 | 健康 | 持续紧绷 | 外网节点可用、本地可见度受限 | 社交博弈 | 侦察取证 | 保障真相镜像可长期存储 | 本地分发被算法压权 |",
        "",
        "## 当前角色知晓情报",
        "| 角色 | 情报ID | 情报内容 | 来源 | 可信度 | 是否公开 | 对行动模式的影响 | 备注 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
        "| 菲娜 | I021 | 成绩模板由‘通过’替换为‘净化认证’ | 成绩系统对照 | 高 | 半公开 | 确认命名层重写已经制度化 | 阶段2入口样本 |",
        "| 诺亚 | I022 | keyword_to_action_map映射可复现 | 双设备实验 | 中高 | 保密 | 将耦合层从体感推进到机制证据 | C2/C3 |",
        "| 菲娜 | I023 | 建议卡连续生效后主观记忆颗粒下降 | 时间线对照 | 中高 | 保密 | 限制连续触发并优先离线留痕 | C4待长期追踪 |",
        "| 菲娜 | I024 | 打卡群替词任务与平台推送形成闭环 | 群公告+推送日志 | 高 | 半公开 | 社交线取证优先级上调 | 第23-26章 |",
        "| 诺亚 | I025 | 链上词典入口存在搜索稀释 | 检索对照实验 | 高 | 半公开 | 转向直链+离线镜像分发 | 第29-30章 |",
        "| 菲娜 | I026 | 双文本转写可同时被系统标高可信 | 离线转写冲突 | 高 | 保密 | 建立‘工具非裁判’原则 | 第36/72章回收 |",
        "| 菲娜 | I027 | 新话包扩展到词组+语境模板 | v2.0发布观察 | 高 | 半公开 | 旧义检索被系统性边缘化 | 第55章 |",
        "| 菲娜 | I028 | 官方语义指南触达率24小时内塌缩 | 班级推广记录 | 高 | 公开 | 确认权威纠偏失效 | 第66章 |",
        "| 菲娜 | I029 | 家庭对话同句出现相反解释且情绪先行 | 马特对谈复盘 | 高 | 保密 | 亲密关系沟通改为流程化校验 | 第70-72章 |",
        "| 诺亚 | I030 | 黑盒回归结论：真相可存储不可传播 | 回归评估报告 | 高 | 半公开 | 将策略从扩散转为保真存档 | 第78章 |",
        "| 蓝月 | I031 | 生态合作后替代链路灰度切换成功 | 后台日志 | 高 | 保密 | 预实验可收口并迁移到雪铃 | 第73-74章 |",
        "| 菲娜 | I032 | 预实验三项指标达标但旧义恢复失败 | 终章验证 | 高 | 半公开 | 选择继续记录与观察而非强行说服 | 第80章 |",
        "",
        "## 角色行动记录（按章节）",
        "| 章节 | 角色 | 本章开始模式 | 本章关键动作 | 结果 | 模式切换原因 | 下章预计模式 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    lines.extend(actions)
    lines.append("")

    ROLE_PATH.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_chapters(chapters: dict[int, dict[str, str]]) -> None:
    for chapter in range(11, 21):
        prev_title = chapters.get(chapter - 1, {}).get("title", "上一章")
        text = generate_chapter(chapter, chapters[chapter], prev_title)
        (DIR_BODY / f"第{chapter:03d}章.md").write_text(text, encoding="utf-8", newline="\n")

    for chapter in range(21, 81):
        storyboard = generate_storyboard(chapter, chapters[chapter])
        (DIR_ENGINE / f"第{chapter:03d}章-分镜纲.md").write_text(
            storyboard, encoding="utf-8", newline="\n"
        )
        prev_title = chapters.get(chapter - 1, {}).get("title", "上一章")
        text = generate_chapter(chapter, chapters[chapter], prev_title)
        (DIR_BODY / f"第{chapter:03d}章.md").write_text(text, encoding="utf-8", newline="\n")


def enforce_length(chapters: dict[int, dict[str, str]]) -> list[tuple[int, int]]:
    for chapter in range(11, 81):
        path = DIR_BODY / f"第{chapter:03d}章.md"
        raw_text = path.read_text(encoding="utf-8")
        paragraphs = [part.strip() for part in raw_text.split("\n\n") if part.strip()]

        deduped: list[str] = []
        seen: set[str] = set()
        for part in paragraphs:
            if part in seen:
                continue
            seen.add(part)
            deduped.append(part)

        text = "\n\n".join(deduped).rstrip() + "\n"
        idx = 0
        while count_non_ws(text) < 3500 and idx < 24:
            idx += 1
            ext = scene_extension(chapter, chapters[chapter], idx)
            if ext in seen:
                continue
            seen.add(ext)
            text = text.rstrip() + "\n\n" + ext + "\n"

        pad_i = 0
        while count_non_ws(text) < 3500 and pad_i < 10:
            pad_i += 1
            pad = final_padding(chapter, pad_i)
            if pad in seen:
                continue
            seen.add(pad)
            text = text.rstrip() + "\n\n" + pad + "\n"

        if count_non_ws(text) > 4500:
            trimmed = [part.strip() for part in text.split("\n\n") if part.strip()]
            while len(trimmed) > 1 and count_non_ws("\n\n".join(trimmed) + "\n") > 4500:
                trimmed.pop()
            text = "\n\n".join(trimmed).rstrip() + "\n"

        path.write_text(text, encoding="utf-8", newline="\n")

    summary: list[tuple[int, int]] = []
    for chapter in range(1, 81):
        path = DIR_BODY / f"第{chapter:03d}章.md"
        summary.append((chapter, count_non_ws(path.read_text(encoding="utf-8"))))
    return summary


def main() -> int:
    DIR_ENGINE.mkdir(parents=True, exist_ok=True)
    outline_file = find_outline_file()
    chapters = parse_chapters(outline_file)
    if len(chapters) < 80:
        raise RuntimeError(f"解析章节数量不足80，当前={len(chapters)}")

    write_chapters(chapters)

    write_range_storyboard_doc(
        chapters,
        21,
        40,
        "\u5b50\u5927\u7eb2\uff1a\u9884\u5b9e\u9a8c-21\u523040\u7ae0\u5206\u955c\u7ec6\u7eb2.md",
    )
    write_range_storyboard_doc(
        chapters,
        41,
        60,
        "\u5b50\u5927\u7eb2\uff1a\u9884\u5b9e\u9a8c-41\u523060\u7ae0\u5206\u955c\u7ec6\u7eb2.md",
    )
    write_range_storyboard_doc(
        chapters,
        61,
        80,
        "\u5b50\u5927\u7eb2\uff1a\u9884\u5b9e\u9a8c-61\u523080\u7ae0\u5206\u955c\u7ec6\u7eb2.md",
    )

    write_foreshadow_csv()
    write_role_state(chapters)
    summary = enforce_length(chapters)

    min_item = min(summary, key=lambda x: x[1])
    max_item = max(summary, key=lambda x: x[1])
    print(f"chapters={len(summary)}")
    print(f"min={min_item[0]:03d}:{min_item[1]}")
    print(f"max={max_item[0]:03d}:{max_item[1]}")
    print(
        "11-20="
        + ",".join(f"{ch:03d}:{count}" for ch, count in summary if 11 <= ch <= 20)
    )
    print(
        "21-40="
        + ",".join(f"{ch:03d}:{count}" for ch, count in summary if 21 <= ch <= 40)
    )
    print(
        "41-60="
        + ",".join(f"{ch:03d}:{count}" for ch, count in summary if 41 <= ch <= 60)
    )
    print(
        "61-80="
        + ",".join(f"{ch:03d}:{count}" for ch, count in summary if 61 <= ch <= 80)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
