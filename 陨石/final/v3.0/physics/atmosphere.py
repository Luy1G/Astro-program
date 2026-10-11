# -*- coding: utf-8 -*-
"""
标准大气密度模型
文档第四章第1节：高速天体在大气中受到气动压力、摩擦生热、质量持续损耗
"""
import math
from .constants import RHO_AIR_SEA, SCALE_HEIGHT


def air_density(altitude_m):
    """指数大气模型：ρ(h) = ρ0 × exp(-h/H)，h < 0 时取海平面值"""
    if altitude_m < 0:
        altitude_m = 0.0
    return RHO_AIR_SEA * math.exp(-altitude_m / SCALE_HEIGHT)


def air_density_with_gradient(altitude_m):
    """
    带垂直梯度的多层近似（更贴合 100km 以下真实大气）
    - 0-25km:   指数模型，标高 8500m
    - 25-100km: 衰减更慢，标高 6000m（高层稀薄化）
    """
    if altitude_m < 0:
        altitude_m = 0.0
    if altitude_m < 25_000:
        return RHO_AIR_SEA * math.exp(-altitude_m / 8500.0)
    rho_25 = RHO_AIR_SEA * math.exp(-25_000 / 8500.0)
    return rho_25 * math.exp(-(altitude_m - 25_000) / 6000.0)
