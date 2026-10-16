# -*- coding: utf-8 -*-
"""
陨石撞击模拟器模板生成引擎
===========================
枚举全部 78 条 rule 组合 → 调用 DeepSeek API 生成模板 →
逐条校验字段 → 输出标准 JSON 数组文件。

用法:
    python template_generator.py --output Aug12/impact_templates_v1.json --workers 5
"""
import argparse
import json
import math
import os
import re
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

# ──────────────────── 常量 ────────────────────
LEVELS = [
    ("L1", 0.0,        1e6,  False),   # 无 angle 分组
    ("L2", 1e6,        1e9,  True),
    ("L3", 1e9,        1e12, True),
    ("L4", 1e12,       1e15, True),
    ("L5", 1e15,       9e18, False),   # 无 angle 分组
]
IMPACT_TYPES = ["airburst", "surface"]
MATERIALS = ["ice", "rock", "iron"]
TARGETS = ["land", "ocean"]
ANGLE_GROUPS = ["G1", "G2", "G3"]          # G1 5~30°, G2 30~60°, G3 60~90°

DISASTER_NAMES = {
    "L1": "微型撞击",
    "L2": "小型灾害",
    "L3": "中型灾难",
    "L4": "大型灾变",
    "L5": "灭绝级撞击",
}

REQUIRED_KEYS = [
    "rule_id", "level", "impact_type", "material", "target", "angle_group",
    "e_min", "e_max", "disaster_title", "main_text", "angle_desc",
    "airburst_only", "surface_only", "land_extra", "ocean_extra",
    "visual_cue", "warning_note",
]


def load_api_key():
    cfg1 = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "Aug11", "v2.1.1", "config.json",
    )
    cfg2 = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "config.json",
    )
    for p in (cfg1, cfg2):
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f).get("deepseek_api_key", "")
            except Exception:
                continue
    return ""


# ──────────────────── 枚举规则 ────────────────────
def enumerate_rules():
    rules = []
    for level, e_min, e_max, has_angle in LEVELS:
        for it in IMPACT_TYPES:
            for mat in MATERIALS:
                for tgt in TARGETS:
                    if has_angle:
                        for ag in ANGLE_GROUPS:
                            rid = f"{level}-{it}-{mat}-{tgt}-{ag}"
                            rules.append(_make_rule(rid, level, it, mat, tgt, ag, e_min, e_max))
                    else:
                        rid = f"{level}-{it}-{mat}-{tgt}-null"
                        rules.append(_make_rule(rid, level, it, mat, tgt, None, e_min, e_max))
    return rules


def _make_rule(rid, level, it, mat, tgt, ag, e_min, e_max):
    return {
        "rule_id": rid,
        "level": level,
        "impact_type": it,
        "material": mat,
        "target": tgt,
        "angle_group": ag,
        "e_min": e_min,
        "e_max": e_max,
    }


AIRBURST_BAD_REPLACEMENTS = [
    # 顺序敏感：长匹配在前
    ("撞击坑形成", "高空解体冲击波扩散"),
    ("撞击坑产生", "高空爆炸冲击波扩散"),
    ("撞击坑出现", "解体云团扩散"),
    ("撞击坑的", "解体碎块云的"),
    ("撞击坑，", "空中冲击波，"),
    ("撞击坑。", "空中冲击。"),
    ("撞击坑", "冲击波扩散区"),
    ("岩层凿坑", "高空大气压缩层"),
    ("地面凿洞", "高空冲击波压缩区"),
    ("地表坑", "冲击波扩散范围"),
    ("坑洞", "高空火球作用区"),
    ("地面坑", "火球冲击区"),
    ("地表凿坑", "高空冲击波扩散"),
    ("凿坑", "高空压缩"),
    ("砸进地底", "高空解体"),
    ("凿入地面", "冲入大气层压缩"),
    ("砸向地面", "向地面方向扩散的冲击波"),
    ("砸入地面", "进入低层大气并猛烈扩散"),
    ("撞向地面", "向下穿透至大气底层"),
    ("落到地面", "低空爆炸"),
    ("砸落地面", "低空解体爆炸"),
    ("撞进地面", "向下方冲击大气"),
    ("砸穿地表", "穿透深层大气"),
    ("坠入地面", "大气层内解体爆炸"),
    ("撞击地面", "在大气层内剧烈爆炸"),
    ("岩层冲击", "高层大气压缩效应"),
    ("坑体", "爆炸球壳"),
    ("弹坑", "火球作用范围"),
    ("触地", "低空爆炸"),
]


def _sanitize_airburst_text(obj):
    """airburst 模式：自动清洗所有文本字段中的违禁坑体词，保持语义与插槽完整。"""
    fields = ("main_text", "airburst_only", "land_extra", "ocean_extra",
              "angle_desc", "visual_cue", "warning_note")
    for f in fields:
        if not isinstance(obj[f], str):
            continue
        s = obj[f]
        for bad, good in AIRBURST_BAD_REPLACEMENTS:
            s = s.replace(bad, good)
        obj[f] = s
    return obj


def _detect_airburst_bad(obj):
    """清洗后再复检，返回残留违禁词列表（空=通过）。"""
    fields = ("main_text", "airburst_only", "land_extra", "ocean_extra",
              "angle_desc", "visual_cue", "warning_note")
    text = "".join(obj[f] for f in fields if isinstance(obj[f], str))
    # 只查短词：长词在两次清洗后不会残留
    probe = ["撞击坑", "凿坑", "坑洞", "弹坑", "坑体"]
    return [w for w in probe if w in text]


# ──────────────────── DeepSeek API ────────────────────
API_URL = "https://api.deepseek.com/chat/completions"

SYSTEM_PROMPT = """你是一名专业的灾变科幻叙事撰写者，负责为陨石撞击模拟器生成规则化模板文案。
请严格按照用户给出的JSON结构输出**纯JSON**，不要任何额外文字、不要Markdown代码块、不要说明注释。
只输出一个JSON对象（即一条模板）。

【严格遵守下列约束】

1. 动态数据使用双大括号插槽，禁止写死具体数值：
   {{diameter}} {{velocity}} {{angle}} {{final_tnt}} {{remain_mass_ratio}} {{breakup_altitude}}
   {{fireball_r}} {{blast_core_r}} {{blast_outer_r}} {{burn_r}} {{crater_r}} {{tsunami_h}}

2. impact_type 语义绝对不能矛盾（**最高优先级，严禁违反**）：
   - airburst（空爆）：这是"高空爆炸"，天体在空中解体烧蚀，**完全不会接触地面形成坑体**。
     在 main_text / airburst_only / land_extra / ocean_extra / angle_desc / visual_cue / warning_note
     全部字段中，绝对严禁出现以下任何词汇：
       撞击坑、岩层凿坑、地面凿洞、地表坑、弹坑、岩层冲击、地表凿坑、凿坑、坑体、弹坑、坑洞、
       地面坑、撞击地面、砸向地面、砸入地面、撞向地面、落到地面、砸进地底、凿入地面。
     只能描述：空中火球、冲击波扩散、热辐射、天空闪光、高层大气解体碎块云等高空效应。
   - surface（地表撞击）：这是"落地撞击"，必须在 main_text 或 surface_only 中明确出现
     "撞击地面"或"撞击坑"或"砸入地面"至少一次。

3. 材质差异化文案（必须体现）：
   - ice（冰彗星）：结构疏松，更易提前烧蚀解体，能量偏分散、易高空释放。
   - rock（岩石陨石）：结构中等，空爆与地表撞击均有可能，冲击效果均衡。
   - iron（铁陨石）：致密坚固，抗大气烧蚀能力强，更易集中穿透形成集中地表冲击。

4. angle_group 差异化（L2/L3/L4，G1浅角 5~30° / G2中等 30~60° / G3陡角 60~90°）：
   - G1：斜掠大气层，能量易横向扩散、纵向集中弱。
   - G2：标准倾斜入射，冲击分布均衡。
   - G3：接近垂直入射，能量纵向集中、穿透更深。
   L1/L5 angle_group=null 时 angle_desc 写通用描述即可。

5. target 差异化：
   - land：land_extra 必须写陆地特有的建筑/森林/地震效果；ocean_extra 必须是空字符串。
   - ocean：ocean_extra 必须写海啸内容，并预留 {{tsunami_h}} 插槽；land_extra 必须是空字符串。
     ocean 且 surface 时，surface_only 仍必须提及撞击坑（海洋海床亦可），但海洋主效应是海啸。

6. main_text 必须嵌入至少 {{remain_mass_ratio}} 和 {{breakup_altitude}} 两个插槽。
   airburst_only / surface_only 二选一填空，另一个必须是空字符串。

7. disaster_title 用中文规范名称：
   L1微型撞击、L2小型灾害、L3中型灾难、L4大型灾变、L5灭绝级撞击

8. visual_cue 写画面特效提示文字（5~15字），如"橙红火球笼罩天空""巨型蘑菇云升腾"等，供前端画面参考。

9. warning_note 简述本条模板适用边界，例："E<100万吨TNT，L1级别，适用于通古斯级以下空中解体事件"。

10. 所有插槽均使用双大括号 {{xxx}}，不要用单大括号或花括号错写。
11. 灾难画面叙事风格，避免过度学术化、避免堆砌固定数字，尽量用插槽交给模拟实时填充。
"""


def build_user_prompt(rule):
    mat_cn = {"ice": "冰彗星", "rock": "岩石陨石", "iron": "铁陨石"}[rule["material"]]
    tgt_cn = {"land": "陆地", "ocean": "海洋"}[rule["target"]]
    it_cn = {"airburst": "空爆", "surface": "地表撞击"}[rule["impact_type"]]
    ag_cn = {
        "G1": "G1浅角度（5~30°，斜掠入射）",
        "G2": "G2中等角度（30~60°，标准倾斜）",
        "G3": "G3陡角度（60~90°，近垂直入射）",
    }.get(rule["angle_group"], "不区分角度")
    dn = DISASTER_NAMES[rule["level"]]

    return f"""请生成如下 rule 的单条模板JSON对象：
rule_id = {rule['rule_id']}
level = {rule['level']}（{dn}）
TNT当量区间：{rule['e_min']:.1e} ≤ E 吨 ＜ {rule['e_max']:.1e}
impact_type = {rule['impact_type']}（{it_cn}）
material = {rule['material']}（{mat_cn}）
target = {rule['target']}（{tgt_cn}）
angle_group = {rule['angle_group']}（{ag_cn}）

输出JSON对象必须包含且仅包含下列key，value类型严格对应：
- rule_id       string  严格等于 "{rule['rule_id']}"
- level         string  严格等于 "{rule['level']}"
- impact_type   string  严格等于 "{rule['impact_type']}"
- material      string  严格等于 "{rule['material']}"
- target        string  严格等于 "{rule['target']}"
- angle_group   string/null  L2/L3/L4 填 G1/G2/G3；L1/L5 填 null
- e_min         number  {rule['e_min']:.5e}
- e_max         number  {rule['e_max']:.5e}
- disaster_title string 中文灾害名（如"中型灾难"）
- main_text     string  主体叙事，必须嵌入 {{remain_mass_ratio}} 和 {{breakup_altitude}} 两个插槽
- angle_desc    string  angle_group 的文字修饰；无角度时写通用描述
- airburst_only string  impact_type=airburst 时填专属段落（禁止坑体词），否则空串
- surface_only  string  impact_type=surface 时填专属段落（必须提撞击坑），否则空串
- land_extra    string  target=land 时填陆地补充，否则空串
- ocean_extra   string  target=ocean 时填海啸补充，必须有 {{tsunami_h}} 插槽，否则空串
- visual_cue    string  画面特效提示文字（5~15字）
- warning_note  string  本条模板适用场景边界说明

请只输出这一个JSON对象，不要任何其他文字或代码块。"""


def call_deepseek(api_key, rule, max_retries=3):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    last_err = None
    for attempt in range(1, max_retries + 1):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(rule)},
        ]
        if last_err is not None:
            # 把上次的校验错误作为修正提示
            messages.append({
                "role": "user",
                "content": f"上一次输出未通过校验，错误信息：【{last_err}】。"
                           f"请严格按该错误修正后，重新输出完整的单条JSON对象（仅JSON）。",
            })
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.85,
            "max_tokens": 2048,
            "stream": False,
            "response_format": {"type": "json_object"},
        }
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=90)
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"].strip()
            return _parse_and_validate(text, rule)
        except Exception as e:
            last_err = str(e)
            wait = 2 ** attempt
            print(f"  [RETRY {attempt}/3] {rule['rule_id']}: {e}, 等待 {wait}s", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"{rule['rule_id']} 重试耗尽: {last_err}")


def _parse_and_validate(raw_text, rule):
    """解析 JSON 并做字段/类型/插槽 校验，不满足则抛错触发重试"""
    # 清洗可能被包裹的 markdown 代码块
    text = raw_text
    if "```json" in text:
        text = text.split("```json", 1)[1].rsplit("```", 1)[0]
    elif "```" in text:
        text = text.split("```", 1)[1].rsplit("```", 1)[0]
    text = text.strip()

    obj = json.loads(text)

    # 1) key 完整
    missing = [k for k in REQUIRED_KEYS if k not in obj]
    if missing:
        raise ValueError(f"缺失key: {missing}")
    extra = [k for k in obj if k not in REQUIRED_KEYS]
    if extra:
        raise ValueError(f"多余key: {extra}")

    # 2) 字符串/数字/null 类型
    def _must(k, types, allow_none=False):
        v = obj[k]
        if v is None and allow_none:
            return
        if not isinstance(v, types):
            raise ValueError(f"{k} 类型错误: {type(v).__name__}, 期望 {types}")

    _must("rule_id", str)
    _must("level", str)
    _must("impact_type", str)
    _must("material", str)
    _must("target", str)
    _must("e_min", (int, float))
    _must("e_max", (int, float))
    _must("disaster_title", str)
    _must("main_text", str)
    _must("angle_desc", str)
    _must("airburst_only", str)
    _must("surface_only", str)
    _must("land_extra", str)
    _must("ocean_extra", str)
    _must("visual_cue", str)
    _must("warning_note", str)
    # angle_group: L2/L3/L4 必须是 G1/G2/G3；L1/L5 必须是 null
    if rule["level"] in ("L2", "L3", "L4"):
        if obj["angle_group"] not in ("G1", "G2", "G3"):
            raise ValueError(f"angle_group={obj['angle_group']} 非G1/G2/G3")
    else:
        if obj["angle_group"] is not None:
            # DeepSeek 可能会返回字符串 "null"
            if isinstance(obj["angle_group"], str) and obj["angle_group"].lower() == "null":
                obj["angle_group"] = None
            else:
                raise ValueError(f"angle_group={obj['angle_group']} 应为 null")

    # 3) 枚举值严格匹配 rule
    for k in ("level", "impact_type", "material", "target"):
        if obj[k] != rule[k]:
            raise ValueError(f"{k}={obj[k]} 不匹配 {rule[k]}")
    if obj["rule_id"] != rule["rule_id"]:
        raise ValueError(f"rule_id={obj['rule_id']} 不匹配 {rule['rule_id']}")
    # e_min/e_max
    if abs(obj["e_min"] - rule["e_min"]) / max(rule["e_min"], 1) > 1e-4:
        raise ValueError(f"e_min={obj['e_min']} 不匹配 {rule['e_min']}")
    if abs(obj["e_max"] - rule["e_max"]) / max(rule["e_max"], 1) > 1e-4:
        raise ValueError(f"e_max={obj['e_max']} 不匹配 {rule['e_max']}")

    # 4) 插槽校验
    # main_text 必须有 {{remain_mass_ratio}} 和 {{breakup_altitude}}
    for slot in ("{{remain_mass_ratio}}", "{{breakup_altitude}}"):
        if slot not in obj["main_text"]:
            raise ValueError(f"main_text 缺少插槽 {slot}")
    # ocean_extra 必须有 {{tsunami_h}}（target=ocean 时）
    if rule["target"] == "ocean":
        if "{{tsunami_h}}" not in obj["ocean_extra"]:
            raise ValueError("ocean_extra 缺少 {{tsunami_h}} 插槽")
        if obj["land_extra"] != "":
            raise ValueError("target=ocean 但 land_extra 非空")
    else:
        if obj["ocean_extra"] != "":
            raise ValueError("target=land 但 ocean_extra 非空")

    # 5) airburst/surface 矛盾校验（airburst 先自动清洗）
    if rule["impact_type"] == "airburst":
        if obj["surface_only"] != "":
            raise ValueError("airburst 但 surface_only 非空")
        obj = _sanitize_airburst_text(obj)
        still_bad = _detect_airburst_bad(obj)
        if still_bad:
            raise ValueError(f"airburst 清洗后仍有违禁词: {still_bad}")
    else:  # surface
        if obj["airburst_only"] != "":
            raise ValueError("surface 但 airburst_only 非空")
        combined = obj["main_text"] + obj["surface_only"]
        if "撞击坑" not in combined and "撞击地面" not in combined and "砸入地面" not in combined and "砸向地面" not in combined:
            raise ValueError("surface 文本必须明确提及撞击/撞击坑")

    # 6) 材质差异化（简单关键词检测，保证出现材质特性描述）
    mat = rule["material"]
    mat_keywords = {
        "ice": ["疏松", "冰", "彗", "提前烧蚀", "解", "散"],
        "rock": ["岩", "石", "均衡"],
        "iron": ["铁", "致密", "坚", "抗烧", "穿"],
    }
    all_text = obj["main_text"] + obj["airburst_only"] + obj["surface_only"]
    if not any(k in all_text for k in mat_keywords[mat]):
        raise ValueError(f"material={mat} 文案未体现材质特性关键词")

    # 7) disaster_title 中文匹配
    if obj["disaster_title"] != DISASTER_NAMES[rule["level"]]:
        raise ValueError(f"disaster_title={obj['disaster_title']} 不匹配 {DISASTER_NAMES[rule['level']]}")

    return obj


# ──────────────────── 主流程 ────────────────────
def main():
    parser = argparse.ArgumentParser(description="陨石撞击模拟模板生成引擎")
    parser.add_argument("--output", type=str, required=True, help="输出JSON文件路径")
    parser.add_argument("--workers", type=int, default=5, help="并发线程数")
    parser.add_argument("--limit", type=int, default=0, help="仅生成前N条（调试用，0=全部）")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("[ERROR] 未找到 deepseek_api_key", file=sys.stderr)
        sys.exit(1)

    all_rules = enumerate_rules()
    if args.limit > 0:
        all_rules = all_rules[: args.limit]
    total = len(all_rules)
    print(f"=== 陨石模板生成引擎 ===", file=sys.stderr)
    print(f"规则总数: {total}", file=sys.stderr)
    print(f"并发数:   {args.workers}", file=sys.stderr)
    print(f"输出路径: {args.output}", file=sys.stderr)

    results = [None] * total
    failures = []
    start = time.time()
    done = 0

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {
            pool.submit(call_deepseek, api_key, rule): i
            for i, rule in enumerate(all_rules)
        }
        for fut in as_completed(future_map):
            i = future_map[fut]
            rule = all_rules[i]
            try:
                tmpl = fut.result()
                results[i] = tmpl
                done += 1
                if done % 10 == 0 or done == total:
                    rate = done / (time.time() - start)
                    eta = (total - done) / rate if rate > 0 else 0
                    print(f"  进度 {done}/{total} ({done/total*100:.1f}%) "
                          f"速率 {rate:.1f}/min ETA {eta:.0f}s  "
                          f"失败 {len(failures)}", file=sys.stderr)
            except Exception as e:
                failures.append((rule["rule_id"], str(e)))
                print(f"  [FAIL] {rule['rule_id']}: {e}", file=sys.stderr)
                traceback.print_exc()

    # 丢弃失败位置
    templates = [t for t in results if t is not None]

    # ── 再做一次全局唯一性/完整性校验 ──
    rids = set()
    for t in templates:
        if t["rule_id"] in rids:
            print(f"[WARN] 重复 rule_id: {t['rule_id']}", file=sys.stderr)
        rids.add(t["rule_id"])
        miss = [k for k in REQUIRED_KEYS if k not in t]
        if miss:
            print(f"[WARN] {t['rule_id']} 缺失 key: {miss}", file=sys.stderr)

    out_path = args.output
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

    elapsed = time.time() - start
    print(f"\n=== 完成 ===", file=sys.stderr)
    print(f"成功: {len(templates)}/{total}", file=sys.stderr)
    print(f"失败: {len(failures)}", file=sys.stderr)
    if failures:
        print("失败详情:", file=sys.stderr)
        for rid, err in failures[:20]:
            print(f"  - {rid}: {err[:80]}", file=sys.stderr)
    print(f"耗时: {elapsed:.0f}s", file=sys.stderr)
    print(f"输出: {out_path}", file=sys.stderr)
    # 最后一行打印到 stdout，方便调用者快速确认
    print(json.dumps({"status": "ok", "generated": len(templates), "failed": len(failures),
                      "output": out_path}, ensure_ascii=False))


if __name__ == "__main__":
    main()
