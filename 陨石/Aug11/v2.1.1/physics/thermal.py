# -*- coding: utf-8 -*-
"""
热辐射毁伤计算（文档第五章第3节）
- 火球半径：r_fireball = c × E^(1/3)   (核爆经验值 c=0.0023)
- 三度烧伤半径：10 cal/cm² ≈ 4.184×10^5 J/m² 临界辐照
"""
import math

from . import constants as C


def compute_thermal(release_energy_j, ground_efficiency):
    e = release_energy_j * ground_efficiency
    if e <= 0:
        return {"fireball_radius_km": 0.0, "burn_radius_km": 0.0}
    r_fireball = C.FIREBALL_COEFF * (e ** (1.0 / 3.0))
    r_burn = math.sqrt(e / (4.0 * math.pi * C.THIRD_DEGREE_BURN_FLUENCE))
    return {
        "fireball_radius_km": r_fireball / 1000.0,
        "burn_radius_km": r_burn / 1000.0,
    }
