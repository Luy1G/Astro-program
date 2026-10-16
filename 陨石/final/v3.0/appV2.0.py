# -*- coding: utf-8 -*-
"""
陆地陨石撞击模拟器 v3.0 — Flask 入口（模板库驱动，无需 API）
启动：python appV2.0.py
访问：http://127.0.0.1:5003

AI 功能由 impact_templates_v1.json 模板库驱动：
    1. 动态场景叙事      → 模板 main_text + airburst_only/surface_only + target_extra
    2. 趣味能量对标      → physics.initial.fun_references 实时计算
    3. 灾害分析报告      → 模板全套 + physics 数据
    4. 科学问答          → 基于模板与 physics 的关键词回答
    5. 自然语言参数解析  → 关键词匹配
"""
import os
import json
import re
from flask import Flask, request, jsonify, render_template

from simulation import run_simulation

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


# ============== 加载 impact_templates_v1.json ==============
_DB_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_DB_DIR, 'Aug12', 'impact_templates_v1.json')
IMPACT_TEMPLATES = []

def load_impact_templates():
    """加载预计算模板库"""
    global IMPACT_TEMPLATES
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            IMPACT_TEMPLATES = json.load(f)
        print(f'[DB] 已加载 {len(IMPACT_TEMPLATES)} 条模板: {DB_PATH}')
    except Exception as e:
        print(f'[DB] 加载失败: {e}')
        IMPACT_TEMPLATES = []

load_impact_templates()


# ============== 等级 / 模式 / 材质 / 目标 / 角度 映射 ==============
LEVEL_BOUNDS = [
    ("L1", 0.0,   1e6),
    ("L2", 1e6,   1e9),
    ("L3", 1e9,   1e12),
    ("L4", 1e12,  1e15),
    ("L5", 1e15,  9e18),
]

MATERIAL_CN2EN = {
    '冰彗星': 'ice', 'ice': 'ice',
    '岩石陨石': 'rock', 'rock': 'rock',
    '铁陨石': 'iron', 'iron': 'iron',
}

TARGET_CN2EN = {
    '陆地': 'land',
    'land': 'land',
}


def classify_level(final_tnt_tons):
    """根据终态 TNT 当量（吨）判定 L1~L5"""
    for level, lo, hi in LEVEL_BOUNDS:
        if lo <= final_tnt_tons < hi:
            return level
    return "L5"  # 兜底


def classify_impact_type(mode_str):
    """根据 mode 字段判定 airburst / surface"""
    if "地表撞击" in mode_str or "地撞" in mode_str:
        return "surface"
    # 空爆（通古斯模式） + 大气烧毁（无地面影响） → airburst
    return "airburst"


def classify_angle_group(angle_deg, level):
    """L1/L5 返回 null；L2/L3/L4 按角度返回 G1/G2/G3"""
    if level in ("L1", "L5"):
        return None
    if angle_deg < 30:
        return "G1"
    if angle_deg < 60:
        return "G2"
    return "G3"


# ============== 模板匹配 ==============
def match_template(level, impact_type, material, target, angle_group):
    """精确匹配模板库中的 rule"""
    for t in IMPACT_TEMPLATES:
        if (t["level"] == level
            and t["impact_type"] == impact_type
            and t["material"] == material
            and t["target"] == target
            and t["angle_group"] == angle_group):
            return t
    return None


def lookup_template_by_result(result):
    """根据 simulation 结果匹配模板"""
    if not IMPACT_TEMPLATES:
        return None
    try:
        echo = result.get("input_echo", {})
        mode_info = result.get("mode", {})
        release = result.get("release", {})

        material = MATERIAL_CN2EN.get(echo.get("material", "岩石陨石"), "rock")
        target = TARGET_CN2EN.get(echo.get("target", "陆地"), "land")
        angle = float(echo.get("angle_deg", 45))
        final_tnt = float(release.get("tnt_tons", 0))
        impact_type = classify_impact_type(mode_info.get("mode", ""))

        level = classify_level(final_tnt)
        ag = classify_angle_group(angle, level)

        return match_template(level, impact_type, material, target, ag)
    except Exception as e:
        print(f"[WARN] lookup_template_by_result 失败: {e}")
        return None


# ============== 数值格式化 ==============
def _fmt_num(val, digits=2):
    if val is None:
        return "N/A"
    try:
        v = float(val)
    except (TypeError, ValueError):
        return str(val)
    if v == 0:
        return "0"
    if abs(v) >= 1e12:
        return f"{v:.2e}"
    if abs(v) >= 1e6:
        return f"{v:,.0f}"
    if abs(v) >= 1:
        return f"{v:,.{digits}f}"
    return f"{v:.{digits+2}f}"


def _fmt_tnt(tons):
    if tons is None:
        return "N/A"
    try:
        t = float(tons)
    except (TypeError, ValueError):
        return str(tons)
    if t >= 1e9:
        return f"{t/1e9:.2f} 十亿吨"
    if t >= 1e6:
        return f"{t/1e6:.2f} 百万吨"
    if t >= 1e3:
        return f"{t/1e3:.2f} 千吨"
    return f"{t:.2f} 吨"


# ============== 模板插槽填充 ==============
SLOT_KEYS = [
    "diameter", "velocity", "angle", "final_tnt", "remain_mass_ratio",
    "breakup_altitude", "fireball_r", "blast_core_r", "blast_outer_r",
    "burn_r", "crater_r",
]


def build_slot_values(result):
    """从 simulation 结果构造 {{xxx}} 插槽的实际值字典"""
    echo = result.get("input_echo", {})
    traj = result.get("trajectory", {})
    mode_info = result.get("mode", {})
    release = result.get("release", {})
    thermal = result.get("thermal", {})
    shock = result.get("shockwave", {})
    crater_info = result.get("crater", {})

    breakup_alt = mode_info.get("breakup_altitude_km")
    if breakup_alt is None:
        breakup_alt = traj.get("breakup", {}).get("altitude_km", 0)

    ablation_ratio = mode_info.get("ablation_ratio", traj.get("ablation_ratio", 0))
    remain_ratio = max(1.0 - ablation_ratio, 0.0)

    crater_d = float(crater_info.get("crater_diameter_km", 0) or 0)
    crater_r = crater_d / 2.0 if crater_d > 0 else 0.0

    return {
        "diameter":         _fmt_num(echo.get("diameter_m", 0)),
        "velocity":         _fmt_num(echo.get("velocity_kms", 0)),
        "angle":            _fmt_num(echo.get("angle_deg", 0), 1),
        "final_tnt":        _fmt_tnt(release.get("tnt_tons", 0)),
        "remain_mass_ratio": f"{remain_ratio*100:.1f}%",
        "breakup_altitude": _fmt_num(breakup_alt, 2),
        "fireball_r":       _fmt_num(thermal.get("fireball_radius_km", 0)),
        "blast_core_r":     _fmt_num(shock.get("core_radius_km", 0)),
        "blast_outer_r":    _fmt_num(shock.get("outer_radius_km", 0)),
        "burn_r":           _fmt_num(thermal.get("burn_radius_km", 0)),
        "crater_r":         _fmt_num(crater_r),
    }


def fill_template(template, result):
    """把模板的 {{xxx}} 插槽替换成实际数值"""
    slots = build_slot_values(result)
    out = dict(template)  # 浅拷贝
    text_fields = ["main_text", "angle_desc", "airburst_only", "surface_only",
                   "land_extra", "visual_cue", "warning_note"]
    for f in text_fields:
        if isinstance(out.get(f), str):
            s = out[f]
            for k, v in slots.items():
                s = s.replace("{{" + k + "}}", str(v))
            out[f] = s
    return out


# ============== 路由 ==============
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/simulate', methods=['POST'])
def api_simulate():
    params = request.get_json(force=True)
    params["target"] = "陆地"
    result = run_simulation(params)
    return jsonify(result)


@app.route('/api/db-info', methods=['GET'])
def api_db_info():
    """模板库信息"""
    levels = sorted(set(t["level"] for t in IMPACT_TEMPLATES))
    impact_types = sorted(set(t["impact_type"] for t in IMPACT_TEMPLATES))
    materials = sorted(set(t["material"] for t in IMPACT_TEMPLATES))
    targets = sorted(set(t["target"] for t in IMPACT_TEMPLATES if t["target"] != "ocean"))
    angle_groups = sorted(set(str(t["angle_group"]) for t in IMPACT_TEMPLATES))
    return jsonify({
        'status': 'ok',
        'total_records': len(IMPACT_TEMPLATES),
        'levels': levels,
        'impact_types': impact_types,
        'materials': materials,
        'targets': targets,
        'angle_groups': angle_groups,
    })


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app.run(debug=True, host='127.0.0.1', port=5003)
