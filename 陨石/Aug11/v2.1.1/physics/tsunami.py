# -*- coding: utf-8 -*-
"""
海洋撞击海啸高度（文档第五章第4节）
简化正相关模型：H ≈ 0.07 × E^(1/2) / d^(1/4)
E 单位 J，d 单位 m，H 单位 m
"""
import math


def compute_tsunami(release_energy_j, depth_m, target):
    if target != "海洋" or release_energy_j <= 0:
        return {"tsunami_height_m": 0.0, "note": "陆地撞击或无能量释放，无海啸"}
    if depth_m <= 0:
        depth_m = 1.0
    H = 0.07 * math.sqrt(release_energy_j) / (depth_m ** 0.25)
    return {"tsunami_height_m": H, "note": ""}
