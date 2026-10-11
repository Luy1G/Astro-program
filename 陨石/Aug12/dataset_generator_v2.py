# -*- coding: utf-8 -*-
"""
陨石撞击仿真批量数据集生成引擎 (DeepSeek API 版)
====================================================
调用本地 /api/simulate 获取物理结果，调用 DeepSeek API 生成 AI 推演报告。
使用多线程并发加速。

用法:
    python dataset_generator_v2.py --count 5000 --port 5003 --output impact_db_v3.json

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
import os
import random
import sys
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ────────────────────── 常量映射 ──────────────────────
MATERIAL_CN = {"ice": "冰彗星", "rock": "岩石陨石", "iron": "铁陨石"}
TARGET_CN = {"land": "陆地", "ocean": "海洋"}

DISASTER_TEXT = {
    "微型撞击": "天体大多在大气中解体燃烧，难以对地表造成有效破坏",
    "小型灾害": "可造成局部城镇严重损毁，有限范围人员伤亡",
    "中型灾难": "大范围城市群遭到毁灭性打击，区域性灾难",
    "大型灾变": "引发广泛生态破坏，跨区域长期环境影响",
    "灭绝级撞击": "诱发全球性气候扰动，威胁生物圈生存",
}

# ────────────────────── 加载 API Key ──────────────────────
def load_api_key():
    """从 config.json 加载 DeepSeek API Key"""
    config_paths = [
        os.path.join(os.path.dirname(__file__), "..", "Aug11", "v2.1.1", "config.json"),
        os.path.join(os.path.dirname(__file__), "config.json"),
        "config.json",
    ]
    for p in config_paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                key = cfg.get("deepseek_api_key")
                if key:
                    print(f"✓ 从 {p} 加载 API Key: {key[:8]}...{key[-4:]}")
                    return key
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    print("[ERROR] 未找到 config.json 或 API Key", file=sys.stderr)
    sys.exit(1)

# ────────────────────── 参数生成 ──────────────────────
def gen_diameter():
    """75% 概率落在 5~800m, 25% 概率落在 800~5000m"""
    if random.random() < 0.75:
        val = random.uniform(5.0, 800.0)
    else:
        val = random.uniform(800.0, 5000.0)
    return round(val, random.choice([1, 2, 3]))

def gen_velocity():
    return round(random.uniform(12.0, 70.0), random.choice([1, 2]))

def gen_angle():
    return round(random.uniform(5.0, 90.0), random.choice([1, 2]))

def gen_depth():
    return round(random.uniform(100.0, 11000.0), random.choice([1, 2]))

def gen_observer():
    return round(random.uniform(1.0, 5000.0), random.choice([1, 2]))

def gen_input():
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

# ────────────────────── 本地仿真 API ──────────────────────
def call_simulate_api(port, inp):
    """调用本地仿真 API"""
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
        return None

# ────────────────────── DeepSeek API ──────────────────────
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

def build_report_prompt(inp, physics):
    """构建发送给 DeepSeek 的 prompt，包含物理仿真结果"""
    init = physics.get("initial", {})
    mode = physics.get("mode", {})
    release = physics.get("release", {})
    shock = physics.get("shockwave", {})
    thermal = physics.get("thermal", {})
    crater_info = physics.get("crater", {})
    tsunami_info = physics.get("tsunami", {})
    disaster = physics.get("disaster_level", {})

    mat_cn = MATERIAL_CN[inp["material"]]
    tgt_cn = TARGET_CN[inp["target"]]
    disaster_level = disaster.get("level", "未知")
    disaster_desc = DISASTER_TEXT.get(disaster_level, "")

    system_prompt = (
        "你是陨石撞击灾害分析专家。根据给定的物理仿真数据，生成一段完整的撞击推演报告。\n"
        "报告规则：\n"
        "1. 基础信息段：天体参数、初始质量、总TNT当量\n"
        "2. 大气烧蚀与解体段：根据烧蚀比和解体高度描述大气过程\n"
        "3. 固定输出冲击波、火球、热辐射破坏范围\n"
        "4. 陆地撞击增加撞击坑段落；海洋撞击不写撞击坑，启用海啸段落\n"
        "5. 末尾固定输出灾害等级和简短总结\n"
        "6. 数值保留合理有效数字，不要过度冗长小数\n"
        "7. 烧蚀比>95%时重点描述天体几乎完全在大气烧蚀；地面能量接近0时注明无地面撞击能量\n"
        "8. 直接输出报告正文，不要输出任何额外标记、解释或前言\n"
        f"灾害等级参考文本：\n"
        f"微型撞击：{DISASTER_TEXT['微型撞击']}\n"
        f"小型灾害：{DISASTER_TEXT['小型灾害']}\n"
        f"中型灾难：{DISASTER_TEXT['中型灾难']}\n"
        f"大型灾变：{DISASTER_TEXT['大型灾变']}\n"
        f"灭绝级撞击：{DISASTER_TEXT['灭绝级撞击']}"
    )

    user_prompt = (
        f"天体参数：直径{inp['diameter_m']}m，材质{mat_cn}，"
        f"入射速度{inp['velocity_kms']}km/s，入射角{inp['angle_deg']}°，"
        f"撞击目标{tgt_cn}。\n"
        f"物理仿真结果：\n"
        f"- 初始质量: {init.get('mass_kg', 0):.4g} kg\n"
        f"- 初始TNT当量: {init.get('tnt_tons', 0):.4g} 吨\n"
        f"- 撞击模式: {mode.get('mode', '未知')}\n"
        f"- 烧蚀比: {mode.get('ablation_ratio', 0)*100:.2f}%\n"
        f"- 解体高度: {mode.get('breakup_altitude_km', 'N/A')} km\n"
        f"- 释放能量: {release.get('energy_j', 0):.4g} J\n"
        f"- 释放TNT: {release.get('tnt_tons', 0):.4g} 吨\n"
        f"- 冲击波核心区半径: {shock.get('core_radius_km', 0):.4g} km\n"
        f"- 冲击波次级区半径: {shock.get('secondary_radius_km', 0):.4g} km\n"
        f"- 冲击波外围区半径: {shock.get('outer_radius_km', 0):.4g} km\n"
        f"- 火球半径: {thermal.get('fireball_radius_km', 0):.4g} km\n"
        f"- 三度烧伤半径: {thermal.get('burn_radius_km', 0):.4g} km\n"
        f"- 撞击坑直径: {crater_info.get('crater_diameter_km', 0):.4g} km\n"
        f"- 海啸高度: {tsunami_info.get('tsunami_height_m', 0):.4g} m\n"
        f"- 灾害等级: {disaster_level}\n"
        f"请生成完整的撞击推演报告。"
    )

    return system_prompt, user_prompt

def call_deepseek_api(api_key, system_prompt, user_prompt, max_retries=3):
    """调用 DeepSeek API 生成 AI 报告"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": False,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(DEEPSEEK_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"].strip()
            return content
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
            else:
                return None

# ────────────────────── 用户提问模板 ──────────────────────
TEMPLATES = [
    "模拟直径{diameter_m}米{mat_cn}天体，以{velocity_kms}km/s、{angle_deg}度撞击{tgt_cn}，推演撞击后果",
    "分析一颗{diameter_m}m陨石，入射速度{velocity_kms}km/s，入射角{angle_deg}°撞击地球",
    "如果有一颗{diameter_m}米的{mat_cn}冲向地球，速度{velocity_kms}千米每秒，撞击角度{angle_deg}度，会发生什么？",
    "推演本次近地天体撞击场景：直径{diameter_m}m，速度{velocity_kms}km/s，倾角{angle_deg}°，撞击{tgt_cn}",
]

def gen_user_query(inp):
    tpl = random.choice(TEMPLATES)
    return tpl.format(
        diameter_m=inp["diameter_m"],
        velocity_kms=inp["velocity_kms"],
        angle_deg=inp["angle_deg"],
        mat_cn=MATERIAL_CN[inp["material"]],
        tgt_cn=TARGET_CN[inp["target"]],
    )

# ────────────────────── 单样本处理 ──────────────────────
def process_one_sample(sample_id, port, api_key):
    """处理单个样本：生成参数 → 调用仿真API → 调用DeepSeek → 组装"""
    inp = gen_input()

    # 1. 调用本地仿真 API
    physics = call_simulate_api(port, inp)
    if physics is None:
        return None, "simulate_api_failed"

    # 2. 调用 DeepSeek API 生成 AI 报告
    sys_prompt, user_prompt = build_report_prompt(inp, physics)
    ai_report = call_deepseek_api(api_key, sys_prompt, user_prompt)
    if ai_report is None:
        return None, "deepseek_api_failed"

    # 3. 组装样本
    user_query = gen_user_query(inp)
    sample = {
        "sample_id": sample_id,
        "input": inp,
        "physics": physics,
        "user_query": user_query,
        "ai_report": ai_report,
    }
    return sample, None

# ────────────────────── 主流程 ──────────────────────
def main():
    parser = argparse.ArgumentParser(description="陨石撞击仿真批量数据集生成引擎 (DeepSeek API版)")
    parser.add_argument("--count", type=int, default=5000, help="生成样本总数")
    parser.add_argument("--port", type=int, default=5003, help="本地仿真API端口")
    parser.add_argument("--output", type=str, default="impact_db_v3.json", help="输出文件路径")
    parser.add_argument("--workers", type=int, default=5, help="并发线程数")
    args = parser.parse_args()

    total = args.count
    port = args.port
    output_path = args.output
    workers = args.workers

    # 加载 API Key
    api_key = load_api_key()

    print(f"=== 陨石撞击仿真数据集生成引擎 (DeepSeek API版) ===")
    print(f"目标样本数: {total}")
    print(f"仿真API端口: {port}")
    print(f"DeepSeek API: {DEEPSEEK_URL}")
    print(f"并发线程数: {workers}")
    print(f"输出文件: {output_path}")
    print()

    dataset = []
    fail_count = 0
    start_time = time.time()
    completed = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # 提交所有任务
        futures = {}
        for sid in range(1, total + 1):
            future = executor.submit(process_one_sample, sid, port, api_key)
            futures[future] = sid

        # 收集结果
        for future in as_completed(futures):
            completed += 1
            sample, error = future.result()
            if sample is not None:
                dataset.append(sample)
            else:
                fail_count += 1

            if completed % 100 == 0:
                elapsed = time.time() - start_time
                rate = completed / elapsed if elapsed > 0 else 0
                eta = (total - completed) / rate if rate > 0 else 0
                success = len(dataset)
                print(f"  进度: {completed}/{total} ({completed/total*100:.1f}%) "
                      f"成功: {success} 失败: {fail_count} "
                      f"速率: {rate:.1f}/s ETA: {eta:.0f}s", flush=True)

    # 排序
    dataset.sort(key=lambda x: x["sample_id"])

    # 输出 JSON
    elapsed = time.time() - start_time
    print(f"\n=== 生成完成 ===")
    print(f"总样本: {len(dataset)}/{total}")
    print(f"失败数: {fail_count}")
    print(f"耗时: {elapsed:.1f}s ({elapsed/60:.1f}分钟)")
    print(f"平均速率: {len(dataset)/elapsed:.1f} samples/s")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"输出文件: {output_path}")
    print(f"文件大小: {file_size:.1f} MB")

    # 预览首条样本
    if dataset:
        print(f"\n=== 首条样本预览 ===")
        s = dataset[0]
        print(f"sample_id: {s['sample_id']}")
        print(f"input: {json.dumps(s['input'], ensure_ascii=False)}")
        print(f"user_query: {s['user_query']}")
        print(f"ai_report (前300字):")
        print(s['ai_report'][:300])

if __name__ == "__main__":
    main()
