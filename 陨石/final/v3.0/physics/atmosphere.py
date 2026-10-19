# -*- coding: utf-8 -*-
"""
标准五层大气密度模型

按真实大气的五个命名层（对流层 / 平流层 / 中间层 / 热层 / 外逸层）分段建模，
每层采用指数模型 ρ(h) = ρ_base · exp(-(h - h_base) / H)，界面处密度连续衔接。

各层标高 H 按美国标准大气（USSA 1976）密度锚点拟合：
    12 km → 0.312    50 km → 1.03e-3    85 km → 8.2e-6    200 km → 2.5e-10  (kg/m³)
"""
import math
from .constants import RHO_AIR_SEA, SCALE_HEIGHT

# ---------------- 五层定义（层名 / 底界高度 m / 标高 m）----------------
ATMOSPHERE_LAYERS = [
    {"name": "对流层", "base": 0.0,       "H": 8500.0},
    {"name": "平流层", "base": 12_000.0,  "H": 6710.0},
    {"name": "中间层", "base": 50_000.0,  "H": 7240.0},
    {"name": "热层",   "base": 85_000.0,  "H": 11060.0},
    {"name": "外逸层", "base": 600_000.0, "H": 50_000.0},
]


def _build_layer_bases():
    """计算各层底界密度：由上一层在界面处的密度直接衔接，保证全程连续"""
    bases = []
    rho = RHO_AIR_SEA
    prev_top, prev_H = 0.0, None
    for layer in ATMOSPHERE_LAYERS:
        if prev_H is not None:
            rho = rho * math.exp(-(layer["base"] - prev_top) / prev_H)
        bases.append((layer["base"], layer["H"], rho))
        prev_top, prev_H = layer["base"], layer["H"]
    return bases


_LAYER_BASES = _build_layer_bases()


def air_density_standard(altitude_m):
    """
    五层标准大气密度（kg/m³）
    h 落在哪一层，就用该层的底界密度与标高做指数衰减
    """
    h = max(altitude_m, 0.0)
    last = _LAYER_BASES[0]
    for base, H, rho_base in _LAYER_BASES:
        if h < base:
            break
        last = (base, H, rho_base)
    base, H, rho_base = last
    return rho_base * math.exp(-(h - base) / H)


def layer_at(altitude_m):
    """返回给定高度所在大气层名称（供展示与解释）"""
    h = max(altitude_m, 0.0)
    name = ATMOSPHERE_LAYERS[0]["name"]
    for layer in ATMOSPHERE_LAYERS:
        if h < layer["base"]:
            break
        name = layer["name"]
    return name


def air_density_with_gradient(altitude_m):
    """兼容旧接口：已升级为五层标准大气模型"""
    return air_density_standard(altitude_m)


def air_density(altitude_m):
    """旧单层指数模型（保留供对照，运行时不再使用）"""
    if altitude_m < 0:
        altitude_m = 0.0
    return RHO_AIR_SEA * math.exp(-altitude_m / SCALE_HEIGHT)
