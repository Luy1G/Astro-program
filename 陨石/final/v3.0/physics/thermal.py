# -*- coding: utf-8 -*-
"""
热辐射毁伤计算（文档第五章第3节）
- 火球半径：r = c × E^(1/3)，上限 100 千米
- 三度烧伤半径：r = sqrt(E / (4π × 烧伤阈值通量))，上限 5000 千米

与冲击波一致，采用经验公式 + 物理上限截断；不使用对数插值，
避免中等当量（1e15 J 以上）被插值放大到上千千米。
"""
import math

from . import constants as C

BURN_RADIUS_MAX_KM = 5000.0   # 三度烧伤半径显示上限（千米）
FIREBALL_MAX_KM = 100.0       # 火球半径显示上限（千米）


def compute_thermal(release_energy_j, ground_efficiency):
    e = release_energy_j * ground_efficiency
    if e <= 0:
        return {"fireball_radius_km": 0.0, "burn_radius_km": 0.0}

    E = e

    # 火球半径（单位：米）
    r_fireball = min(C.FIREBALL_COEFF * (E ** (1.0 / 3.0)),
                     FIREBALL_MAX_KM * 1000.0)

    # 三度烧伤半径（单位：米）
    r_burn = min(math.sqrt(E / (4.0 * math.pi * C.THIRD_DEGREE_BURN_FLUENCE)),
                 BURN_RADIUS_MAX_KM * 1000.0)

    return {
        "fireball_radius_km": r_fireball / 1000.0,
        "burn_radius_km": r_burn / 1000.0,
    }
