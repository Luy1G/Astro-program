# -*- coding: utf-8 -*-
"""
冲击波破坏半径（文档第五章第2节）
Sachs 缩放：r = Z × W^(1/3)   (W 单位：千克TNT当量，Z 单位：米/千克^(1/3))
NASA 超压阈值：1磅力/平方英寸 玻璃碎裂 / 10磅力/平方英寸 建筑坍塌 / 20磅力/平方英寸 严重摧毁

极端能量下直接用物理上限截断，不再做对数插值：
插值会把 1e15 J（约 24 万吨）以上的结果迅速放大到数百千米，导致中等当量也出现
“核心区上百千米”的错误结果。
"""
import math

from . import constants as C

CORE_MAX_KM = 500.0        # 核心区半径显示上限（千米）
SECONDARY_MAX_KM = 1500.0  # 次级区半径显示上限（千米）
OUTER_MAX_KM = 5000.0      # 外围区半径显示上限（千米）


def compute_shockwave(release_energy_j, ground_efficiency):
    e = release_energy_j * ground_efficiency
    if e <= 0:
        return {"core_radius_km": 0.0, "secondary_radius_km": 0.0,
                "outer_radius_km": 0.0, "tnt_kg": 0.0}

    tnt_kg = e * C.TNT_KG_PER_JOULE
    w13 = tnt_kg ** (1.0 / 3.0) if tnt_kg > 0 else 0.0

    core = min(C.OVERPRESSURE_SCALED_DIST["core"] * w13 / 1000.0, CORE_MAX_KM)
    sec = min(C.OVERPRESSURE_SCALED_DIST["secondary"] * w13 / 1000.0, SECONDARY_MAX_KM)
    outer = min(C.OVERPRESSURE_SCALED_DIST["outer"] * w13 / 1000.0, OUTER_MAX_KM)

    return {
        "core_radius_km": core,
        "secondary_radius_km": sec,
        "outer_radius_km": outer,
        "tnt_kg": tnt_kg,
    }
