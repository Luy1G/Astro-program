# -*- coding: utf-8 -*-
"""
热辐射毁伤计算（文档第五章第3节）

- 火球半径：r = c × E^(1/3)，上限 100 千米
- 三度烧伤半径：按通量阈值求解，并计入热辐射效率与大气衰减

      F(r) = η·E·exp(-r/L) / (4πr²) = F_th

  η 为转化为热辐射的能量份额，L 为大气衰减特征长度。
  近距离退化为 sqrt(ηE/4πF)，远距离因指数衰减自然饱和；
  纯 sqrt 公式在 Gt 级会把烧伤半径放大到数千千米，且不同级别全部撞上限。
"""
import math

from . import constants as C

BURN_RADIUS_MAX_KM = 2000.0    # 三度烧伤半径物理上限（千米）
FIREBALL_MAX_KM = 100.0        # 火球半径物理上限（千米）
THERMAL_EFFICIENCY = 0.35      # 能量中转化为热辐射的份额（空爆经验值）
ATTENUATION_KM = 40.0          # 大气衰减特征长度（千米）


def _solve_burn_radius_m(E):
    """求解 η·E·exp(-r/L)/(4πr²) = F_th 的 r（米）；左边随 r 单调递减，二分求解。"""
    if E <= 0:
        return 0.0
    target = (THERMAL_EFFICIENCY * E /
              (4.0 * math.pi * C.THIRD_DEGREE_BURN_FLUENCE))
    if target <= 0:
        return 0.0
    lo, hi = 0.0, BURN_RADIUS_MAX_KM * 1000.0
    L = ATTENUATION_KM * 1000.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if mid * mid * math.exp(mid / L) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def compute_thermal(release_energy_j, ground_efficiency):
    e = release_energy_j * ground_efficiency
    if e <= 0:
        return {"fireball_radius_km": 0.0, "burn_radius_km": 0.0}

    # 火球半径（单位：米）
    r_fireball = min(C.FIREBALL_COEFF * (e ** (1.0 / 3.0)),
                     FIREBALL_MAX_KM * 1000.0)

    # 三度烧伤半径（单位：米）
    r_burn = _solve_burn_radius_m(e)

    return {
        "fireball_radius_km": r_fireball / 1000.0,
        "burn_radius_km": r_burn / 1000.0,
    }
