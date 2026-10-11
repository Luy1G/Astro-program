# -*- coding: utf-8 -*-
"""
灾害等级分类（文档第六章）
国际小行星撞击风险分级体系
"""


def classify_disaster(diameter_m, tnt_tons):
    if diameter_m < 20 or tnt_tons < 1e3:
        return {"level": "微型撞击", "description": "10m级，大气消耗，无地面损伤"}
    if diameter_m < 50 or tnt_tons < 1e6:
        return {"level": "小型灾害", "description": "20–50m，局部城市损毁"}
    if diameter_m < 500 or tnt_tons < 1e9:
        return {"level": "中型灾难", "description": "100m级，城市群毁灭"}
    if diameter_m < 2000 or tnt_tons < 1e12:
        return {"level": "大型灾变", "description": "1km级，区域性生态崩溃"}
    return {"level": "灭绝级撞击", "description": "10km+，全球圈层破坏、生物大灭绝"}


def observer_damage(observer_distance_km, shock, thermal):
    d = observer_distance_km
    if d <= shock["core_radius_km"]:
        return "位于核心摧毁区：地面汽化、完全毁灭"
    if d <= shock["secondary_radius_km"]:
        return "位于次级区：建筑完全坍塌、林木焚毁"
    if d <= thermal["burn_radius_km"]:
        return "位于热辐射烧伤区：三度烧伤、可燃物起火"
    if d <= shock["outer_radius_km"]:
        return "位于外围区：玻璃震碎、轻度损毁"
    return "位于安全区：基本无影响"
