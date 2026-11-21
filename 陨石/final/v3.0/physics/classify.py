# -*- coding: utf-8 -*-
"""
灾害等级分类（文档第六章）
国际小行星撞击风险分级体系

等级与模板库 L1~L5 使用同一套 TNT 当量阈值，避免右侧面板与 AI 叙事等级冲突。
"""

# (等级码, 下界吨TNT, 上界吨TNT, 标题, 说明)
DISASTER_LEVELS = [
    ("L1", 0.0,      1e5,  "微型撞击",   "能量低于 10 万吨 TNT，多在高空烧蚀，无显著地面损伤"),
    ("L2", 1e5,      1e9,  "小型灾害",   "能量 10 万–10 亿吨 TNT，局部城市或森林损毁"),
    ("L3", 1e9,      1e12, "中型灾难",   "能量 10 亿–1 万亿吨 TNT，城市群或区域尺度毁灭"),
    ("L4", 1e12,     1e14, "大型灾变",   "能量 1 万亿–100 万亿吨 TNT，区域性生态崩溃"),
    ("L5", 1e14,     float("inf"), "灭绝级撞击", "能量 ≥100 万亿吨 TNT，全球气候与生物圈破坏"),
]


def classify_disaster(diameter_m, tnt_tons):
    """按释放能量（吨 TNT）定级，与模板库 L1~L5 完全一致。

    diameter_m 仅为保持接口兼容，不参与定级。
    """
    t = float(tnt_tons or 0.0)
    for code, lo, hi, title, desc in DISASTER_LEVELS:
        if lo <= t < hi:
            return {"level": title, "code": code, "description": desc}
    # 兜底（NaN 或负值）
    return {"level": "微型撞击", "code": "L1", "description": "无有效能量数据"}


def observer_damage(observer_distance_km, shock, thermal):
    """观测点损毁评估：核心/次级按冲击波判定，外围区与烧伤区分别判断后合并。

    烧伤半径通常大于外围区半径：若只按半径升序取第一个命中，
    就会出现「在外围区内、也在 20 km 烧伤半径内，却只报玻璃震碎」的漏报。
    """
    d = observer_distance_km
    if d <= shock["core_radius_km"]:
        return "位于核心摧毁区：地面汽化、完全毁灭"
    if d <= shock["secondary_radius_km"]:
        return "位于次级区：建筑完全坍塌、林木焚毁"

    effects = []
    if d <= shock["outer_radius_km"]:
        effects.append("外围区：玻璃震碎、轻度损毁")
    if d <= thermal["burn_radius_km"]:
        effects.append("热辐射烧伤区：三度烧伤、可燃物起火")
    if effects:
        return "位于" + "；同时".join(effects)
    return "位于安全区：基本无影响"
