# -*- coding: utf-8 -*-
"""
冲击波破坏半径（文档第五章第2节）
Sachs 缩放：r = Z × W^(1/3)   (W 单位 kg TNT, Z 单位 m/kg^(1/3))
NASA 超压阈值：1 psi 玻璃碎 / 10 psi 建筑坍 / 20 psi 严重摧毁
"""
from . import constants as C


def compute_shockwave(release_energy_j, ground_efficiency):
    """
    基于实际释放能量计算三区半径（不再用初始动能）
    """
    e = release_energy_j * ground_efficiency
    tnt_kg = e * C.TNT_KG_PER_JOULE
    w13 = tnt_kg ** (1.0 / 3.0) if tnt_kg > 0 else 0.0
    return {
        "core_radius_km":      (C.OVERPRESSURE_SCALED_DIST["core"]      * w13) / 1000.0,
        "secondary_radius_km": (C.OVERPRESSURE_SCALED_DIST["secondary"] * w13) / 1000.0,
        "outer_radius_km":     (C.OVERPRESSURE_SCALED_DIST["outer"]     * w13) / 1000.0,
        "tnt_kg": tnt_kg,
    }
