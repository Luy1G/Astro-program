# -*- coding: utf-8 -*-
"""
撞击坑直径计算（文档第五章第1节）
基于 Collins et al. 2005 简化版：D_t = 1.161 × (ρ_i/ρ_t)^(1/3) × L^0.78 × v^0.44 × (sinθ)^(1/3)
"""
import math

from . import constants as C


def compute_crater(diameter_m, material_key, velocity_kms, target,
                   impact_energy_j, mode):
    """
    空爆/烧毁模式下坑径设为 0（无实体撞击）。
    地撞模式下用 Collins 公式计算最终坑径（含 1.25 倍重力塌陷修正）。
    """
    if "空爆" in mode or "烧毁" in mode:
        return {"crater_diameter_km": 0.0, "note": "空爆/烧毁模式无实体撞击，不形成撞击坑"}

    rho_i = C.MATERIALS[material_key]["density"]
    rho_t = C.TARGET_DENSITY[target]
    v_ms = velocity_kms * 1000.0
    sin_theta = 1.0  # 简化为垂直撞击

    D_t = 1.161 * (rho_i / rho_t) ** (1.0 / 3.0) \
          * (diameter_m ** 0.78) * (v_ms ** 0.44) * (sin_theta ** (1.0 / 3.0))
    D_final = D_t * 1.25  # 重力塌陷修正
    return {"crater_diameter_km": D_final / 1000.0, "note": ""}
