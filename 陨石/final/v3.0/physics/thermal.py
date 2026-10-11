# -*- coding: utf-8 -*-
"""
热辐射毁伤计算（文档第五章第3节）
- 火球半径：常规能量 ≤ 10^12 焦耳 用 c × E^(1/3)；过渡区对数插值至 100 千米上限
- 三度烧伤半径：常规能量 ≤ 10^12 焦耳 用 sqrt(E / 4π × 4.184e5)；过渡区对数插值至 5000 千米上限
"""
import math

from . import constants as C

E_LOW_J  = 1.0e15             # 常规区上限（焦耳），经验公式可靠
E_MAX_J  = 1.0e22             # 灭绝级能量上限（焦耳）
BURN_RADIUS_MAX_KM = 5000.0   # 三度烧伤半径物理上限（千米）
FIREBALL_MAX_KM = 100.0       # 火球半径物理上限（千米）


def compute_thermal(release_energy_j, ground_efficiency):
    e = release_energy_j * ground_efficiency
    if e <= 0:
        return {"fireball_radius_km": 0.0, "burn_radius_km": 0.0}

    E = e

    # 火球半径（单位：米）
    if E <= E_LOW_J:
        r_fireball = C.FIREBALL_COEFF * (E ** (1.0 / 3.0))
    elif E >= E_MAX_J:
        r_fireball = FIREBALL_MAX_KM * 1000.0
    else:
        r_fireball_low = C.FIREBALL_COEFF * (E_LOW_J ** (1.0 / 3.0))
        t = math.log10(E / E_LOW_J) / math.log10(E_MAX_J / E_LOW_J)
        t = max(0.0, min(1.0, t))
        r_fireball = r_fireball_low + (FIREBALL_MAX_KM * 1000.0 - r_fireball_low) * t

    # 三度烧伤半径（单位：米）
    if E <= E_LOW_J:
        r_burn = math.sqrt(E / (4.0 * math.pi * C.THIRD_DEGREE_BURN_FLUENCE))
    elif E >= E_MAX_J:
        r_burn = BURN_RADIUS_MAX_KM * 1000.0
    else:
        r_burn_low = math.sqrt(E_LOW_J / (4.0 * math.pi * C.THIRD_DEGREE_BURN_FLUENCE))
        t = math.log10(E / E_LOW_J) / math.log10(E_MAX_J / E_LOW_J)
        t = max(0.0, min(1.0, t))
        r_burn = r_burn_low + (BURN_RADIUS_MAX_KM * 1000.0 - r_burn_low) * t

    return {
        "fireball_radius_km": r_fireball / 1000.0,
        "burn_radius_km": r_burn / 1000.0,
    }
