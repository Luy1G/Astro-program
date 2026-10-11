# -*- coding: utf-8 -*-
"""
陨石撞击仿真批量数据集生成引擎
================================
持续生成合法陨石撞击仿真样本，调用本地 /api/simulate 接口获取物理结果，
动态生成用户提问与 AI 推演报告，输出标准 JSON 数组。

用法:
    python dataset_generator.py --count 5000 --port 5003 --output impact_db_v2.json

参数硬性边界:
    diameter_m    5.0 ~ 5000.0 m   (75% 落在 5~800m, 25% 落在 800~5000m)
    velocity_kms  12.0 ~ 70.0 km/s
    angle_deg     5.0 ~ 90.0 °
    material      ice / rock / iron
    target        land / ocean
    ocean_depth_m 100.0 ~ 11000.0 m
    observer_km   1.0 ~ 5000.0 km
"""
import argparse
import json
import math
import random
import sys
import time
import requests

# ────────────────────── 常量映射 ──────────────────────
MATERIAL_CN = {"ice": "冰彗星", "rock": "岩石陨石", "iron": "铁陨石"}
MATERIAL_DESC = {"ice": "冰彗星", "rock": "岩石陨石", "iron": "铁陨石"}
TARGET_CN = {"land": "陆地", "ocean": "海洋"}
TARGET_DESC = {"land": "陆地", "ocean": "海洋"}

DISASTER_TEXT = {
    "微型撞击": "天体大多在大气中解体燃烧，难以对地表造成有效破坏",
    "小型灾害": "可造成局部城镇严重损毁，有限范围人员伤亡",
    "中型灾难": "大范围城市群遭到毁灭性打击，区域性灾难",
    "大型灾变": "引发广泛生态破坏，跨区域长期环境影响",
    "灭绝级撞击": "诱发全球性气候扰动，威胁生物圈生存",
}

# ────────────────────── 参数生成 ──────────────────────
def gen_diameter():
    """75% 概率落在 5~800m, 25% 概率落在 800~5000m, 保留1~3位小数"""
    if random.random() < 0.75:
        val = random.uniform(5.0, 800.0)
    else:
        val = random.uniform(800.0, 5000.0)
    decimals = random.choice([1, 2, 3])
    return round(val, decimals)

def gen_velocity():
    val = random.uniform(12.0, 70.0)
    return round(val, random.choice([1, 2]))

def gen_angle():
    val = random.uniform(5.0, 90.0)
    return round(val, random.choice([1, 2]))

def gen_depth():
    val = random.uniform(100.0, 11000.0)
    return round(val, random.choice([1, 2]))

def gen_observer():
    val = random.uniform(1.0, 5000.0)
    return round(val, random.choice([1, 2]))

def gen_input():
    """生成一组合法输入参数"""
    target = random.choice(["land", "ocean"])
    return {
        "diameter_m": gen_diameter(),
        "velocity_kms": gen_velocity(),
        "angle_deg": gen_angle(),
        "material": random.choice(["ice", "rock", "iron"]),
        "target": target,
        "ocean_depth_m": gen_depth() if target == "ocean" else 0.0,
        "observer_km": gen_observer(),
    }

# ────────────────────── API 调用 ──────────────────────
def call_simulate_api(port, inp):
    """调用本地仿真 API，返回 physics dict 或 None"""
    # 英文→中文映射
    params = {
        "diameter": inp["diameter_m"],
        "material": MATERIAL_CN[inp["material"]],
        "velocity": inp["velocity_kms"],
        "angle": inp["angle_deg"],
        "target": TARGET_CN[inp["target"]],
        "depth": inp["ocean_depth_m"],
        "observer_distance": inp["observer_km"],
    }
    url = f"http://127.0.0.1:{port}/api/simulate"
    try:
        resp = requests.post(url, json=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  [WARN] API调用失败: {e}", file=sys.stderr)
        return None

# ────────────────────── 用户提问生成 ──────────────────────
TEMPLATES = [
    "模拟直径{diameter_m}米{mat_cn}天体，以{velocity_kms}km/s、{angle_deg}度撞击{tgt_cn}，推演撞击后果",
    "分析一颗{diameter_m}m陨石，入射速度{velocity_kms}km/s，入射角{angle_deg}°撞击地球",
    "如果有一颗{diameter_m}米的{mat_cn}冲向地球，速度{velocity_kms}千米每秒，撞击角度{angle_deg}度，会发生什么？",
    "推演本次近地天体撞击场景：直径{diameter_m}m，速度{velocity_kms}km/s，倾角{angle_deg}°，撞击{tgt_cn}",
]

def gen_user_query(inp):
    """随机选取模板并填充参数"""
    tpl = random.choice(TEMPLATES)
    return tpl.format(
        diameter_m=inp["diameter_m"],
        velocity_kms=inp["velocity_kms"],
        angle_deg=inp["angle_deg"],
        mat_cn=MATERIAL_DESC[inp["material"]],
        tgt_cn=TARGET_DESC[inp["target"]],
    )

# ────────────────────── AI 报告生成 ──────────────────────
def _fmt(num, digits=2):
    """格式化数字：大数用科学计数法，小数保留有效位"""
    if num is None:
        return "N/A"
    if num == 0:
        return "0"
    if abs(num) >= 1e12:
        return f"{num:.2e}"
    if abs(num) >= 1e6:
        return f"{num:,.0f}"
    if abs(num) >= 1:
        return f"{num:,.{digits}f}"
    return f"{num:.{digits+2}f}"

def _fmt_tnt(tons):
    """TNT 当量友好格式化"""
    if tons >= 1e9:
        return f"{tons/1e9:.2f} 十亿吨"
    if tons >= 1e6:
        return f"{tons/1e6:.2f} 百万吨"
    if tons >= 1e3:
        return f"{tons/1e3:.2f} 千吨"
    return f"{tons:.2f} 吨"

def gen_ai_report(inp, physics):
    """根据物理仿真结果动态拼接 AI 推演报告"""
    init = physics.get("initial", {})
    mode = physics.get("mode", {})
    traj = physics.get("trajectory", {})
    release = physics.get("release", {})
    shock = physics.get("shockwave", {})
    thermal = physics.get("thermal", {})
    crater_info = physics.get("crater", {})
    tsunami_info = physics.get("tsunami", {})
    disaster = physics.get("disaster_level", {})

    d = inp["diameter_m"]
    v = inp["velocity_kms"]
    ang = inp["angle_deg"]
    mat_cn = MATERIAL_DESC[inp["material"]]
    tgt_cn = TARGET_DESC[inp["target"]]
    mass_kg = init.get("mass_kg", 0)
    tnt_tons = init.get("tnt_tons", 0)
    mode_str = mode.get("mode", "")
    ablation_ratio = mode.get("ablation_ratio", 0)
    breakup_alt = mode.get("breakup_altitude_km")
    release_energy = release.get("energy_j", 0)
    release_tnt = release.get("tnt_tons", 0)
    disaster_level = disaster.get("level", "未知")
    disaster_desc = DISASTER_TEXT.get(disaster_level, "")

    lines = []

    # ── 1. 基础信息段 ──
    lines.append(f"【AI撞击灾害分析】")
    lines.append(f"天体参数：直径{d}m，材质{mat_cn}，入射速度{v}km/s，入射角{ang}°，撞击目标{tgt_cn}。")
    lines.append(f"初始质量约{_fmt(mass_kg)} kg，初始总动能对应TNT当量约{_fmt_tnt(tnt_tons)}。")

    # ── 2. 大气烧蚀与解体段 ──
    if ablation_ratio > 0.95:
        lines.append(f"天体在大气层中几乎完全烧蚀，质量损失率达{ablation_ratio*100:.1f}%，"
                      f"仅极少量残骸可能到达地面。")
    elif ablation_ratio > 0.5:
        lines.append(f"大气烧蚀显著，质量损失约{ablation_ratio*100:.1f}%。")
    elif ablation_ratio > 0.01:
        lines.append(f"大气烧蚀有限，质量损失约{ablation_ratio*100:.1f}%，天体保持较完整结构。")
    else:
        lines.append(f"天体几乎未受大气烧蚀影响，质量损失仅{ablation_ratio*100:.2f}%。")

    if breakup_alt is not None and breakup_alt > 0:
        lines.append(f"解体发生在约{breakup_alt:.1f}km高度，"
                      f"释放能量对应TNT当量约{_fmt_tnt(release_tnt)}。")
    elif "地撞" in mode_str:
        lines.append(f"天体未发生高空解体，以完整结构撞击地表。")

    if release_energy < 1e6:
        lines.append("地面撞击能量极低，不会产生显著地面破坏效应。")

    # ── 3. 冲击波/火球/热辐射段 ──
    core_r = shock.get("core_radius_km", 0)
    sec_r = shock.get("secondary_radius_km", 0)
    outer_r = shock.get("outer_radius_km", 0)
    fireball_r = thermal.get("fireball_radius_km", 0)
    burn_r = thermal.get("burn_radius_km", 0)

    lines.append(f"冲击波破坏范围：核心摧毁区半径约{_fmt(core_r)}km，"
                  f"次级坍塌区约{_fmt(sec_r)}km，外围玻璃碎裂区约{_fmt(outer_r)}km。")
    lines.append(f"火球半径约{_fmt(fireball_r)}km，三度烧伤半径约{_fmt(burn_r)}km。")

    # ── 4. 撞击坑/海啸段（按 target 区分）──
    if inp["target"] == "land":
        crater_d = crater_info.get("crater_diameter_km", 0)
        if crater_d > 0:
            lines.append(f"撞击坑直径约{_fmt(crater_d)}km，"
                          f"坑体永久改变地形地貌。")
        else:
            lines.append("空爆或烧毁模式，未形成实体撞击坑。")
    else:
        tsunami_h = tsunami_info.get("tsunami_height_m", 0)
        if tsunami_h > 0:
            lines.append(f"海洋撞击引发海啸，预估浪高约{_fmt(tsunami_h)}m，"
                          f"沿海地区面临严重洪灾威胁。")
        else:
            lines.append("海洋撞击但能量不足，未引发显著海啸。")

    # ── 5. 灾害等级段 ──
    lines.append(f"灾害等级判定：{disaster_level}。{disaster_desc}")

    return "\n".join(lines)

# ────────────────────── 主流程 ──────────────────────
def main():
    parser = argparse.ArgumentParser(description="陨石撞击仿真批量数据集生成引擎")
    parser.add_argument("--count", type=int, default=5000, help="生成样本总数")
    parser.add_argument("--port", type=int, default=5003, help="本地仿真API端口")
    parser.add_argument("--output", type=str, default="impact_db_v2.json", help="输出文件路径")
    args = parser.parse_args()

    total = args.count
    port = args.port
    output_path = args.output

    print(f"=== 陨石撞击仿真数据集生成引擎 ===")
    print(f"目标样本数: {total}")
    print(f"API端口: {port}")
    print(f"输出文件: {output_path}")
    print()

    dataset = []
    sample_id = 1
    fail_count = 0
    start_time = time.time()

    while sample_id <= total:
        inp = gen_input()

        physics = call_simulate_api(port, inp)
        if physics is None:
            fail_count += 1
            if fail_count > total * 0.1:
                print(f"[ERROR] API失败率过高({fail_count})，终止生成", file=sys.stderr)
                break
            continue

        try:
            user_query = gen_user_query(inp)
            ai_report = gen_ai_report(inp, physics)

            sample = {
                "sample_id": sample_id,
                "input": inp,
                "physics": physics,
                "user_query": user_query,
                "ai_report": ai_report,
            }
            dataset.append(sample)
            sample_id += 1

            if sample_id % 500 == 0:
                elapsed = time.time() - start_time
                rate = sample_id / elapsed if elapsed > 0 else 0
                eta = (total - sample_id) / rate if rate > 0 else 0
                print(f"  进度: {sample_id}/{total} ({sample_id/total*100:.1f}%) "
                      f"速率: {rate:.1f}/s ETA: {eta:.0f}s 失败: {fail_count}")
        except Exception as e:
            print(f"  [WARN] 样本组装失败: {e}", file=sys.stderr)
            fail_count += 1
            continue

    # 输出完整 JSON
    elapsed = time.time() - start_time
    print(f"\n=== 生成完成 ===")
    print(f"总样本: {len(dataset)}/{total}")
    print(f"失败数: {fail_count}")
    print(f"耗时: {elapsed:.1f}s")
    print(f"平均速率: {len(dataset)/elapsed:.1f} samples/s")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    file_size = len(dataset) * 1  # 粗略估算
    print(f"输出文件: {output_path}")
    print(f"文件大小: {file_size}")

    # 验证第一条样本
    if dataset:
        print(f"\n=== 首条样本预览 ===")
        s = dataset[0]
        print(f"sample_id: {s['sample_id']}")
        print(f"input: {json.dumps(s['input'], ensure_ascii=False)}")
        print(f"user_query: {s['user_query'][:80]}...")
        print(f"ai_report (前200字): {s['ai_report'][:200]}...")

if __name__ == "__main__":
    main()
