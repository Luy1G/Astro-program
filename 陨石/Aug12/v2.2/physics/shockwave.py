# -*- coding: utf-8 -*-
"""
冲击波破坏半径（文档第五章第2节）
Sachs 缩放：r = Z × W^(1/3)   (W 单位 kg TNT, Z 单位 m/kg^(1/3))
NASA 超压阈值：1 psi 玻璃碎 / 10 psi 建筑坍 / 20 psi 严重摧毁
E > 10^12 J 时对数插值抑制，防止极端能量下半径发散
"""
import math

from . import constants as C

E_LOW_J  = 1.0e15     # 常规区上限
E_MAX_J  = 1.0e22     # 灭绝级能量上限
CORE_MAX_KM = 500.0   # 核心区半径物理上限（km）
SECONDARY_MAX_KM = 1500.0
OUTER_MAX_KM = 5000.0


def compute_shockwave(release_energy_j, ground_efficiency):
    e = release_energy_j * ground_efficiency
    if e <= 0:
        return {"core_radius_km": 0.0, "secondary_radius_km": 0.0,
                "outer_radius_km": 0.0, "tnt_kg": 0.0}

    tnt_kg = e * C.TNT_KG_PER_JOULE
    w13 = tnt_kg ** (1.0 / 3.0) if tnt_kg > 0 else 0.0

    # 常规区：直接用 Sachs 缩放
    if e <= E_LOW_J:
        core = (C.OVERPRESSURE_SCALED_DIST["core"] * w13) / 1000.0
        sec = (C.OVERPRESSURE_SCALED_DIST["secondary"] * w13) / 1000.0
        outer = (C.OVERPRESSURE_SCALED_DIST["outer"] * w13) / 1000.0
    else:
        # 对数插值：从 E_LOW 处的半径过渡到上限
        w13_low = (E_LOW_J * C.TNT_KG_PER_JOULE) ** (1.0 / 3.0)
        core_low = (C.OVERPRESSURE_SCALED_DIST["core"] * w13_low) / 1000.0
        sec_low = (C.OVERPRESSURE_SCALED_DIST["secondary"] * w13_low) / 1000.0
        outer_low = (C.OVERPRESSURE_SCALED_DIST["outer"] * w13_low) / 1000.0

        t = math.log10(e / E_LOW_J) / math.log10(E_MAX_J / E_LOW_J)
        t = max(0.0, min(1.0, t))

        core = core_low + (CORE_MAX_KM - core_low) * t
        sec = sec_low + (SECONDARY_MAX_KM - sec_low) * t
        outer = outer_low + (OUTER_MAX_KM - outer_low) * t

    return {
        "core_radius_km": core,
        "secondary_radius_km": sec,
        "outer_radius_km": outer,
        "tnt_kg": tnt_kg,
    }
