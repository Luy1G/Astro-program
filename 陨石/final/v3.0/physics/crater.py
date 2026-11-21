# -*- coding: utf-8 -*-
"""
撞击坑直径计算（文档第五章第1节）
基于 Collins et al. 2005 简化版：D_t = 1.161 × (ρ_i/ρ_t)^(1/3) × L^0.78 × v^0.44 × (sinθ)^(1/3)
"""
import math

from . import constants as C


def compute_crater(diameter_m, material_key, velocity_kms, target,
                   impact_energy_j, mode, angle_deg=90.0, impactor_mass_kg=None):
    """
    空爆/烧毁模式下坑径设为 0（无实体撞击）。
    地撞模式下用 Collins 公式计算最终坑径（含 1.25 倍重力塌陷修正）。

    Args:
        diameter_m:        初始直径（米），仅在未提供终端质量时使用
        velocity_kms:      撞击瞬间速度（千米/秒，应传终端速度）
        angle_deg:         入射角（度，与地面夹角），影响 sinθ 项
        impactor_mass_kg:  撞击瞬间剩余质量（千克）；提供时用等效直径替代初始直径
    """
    if "空爆" in mode or "烧毁" in mode:
        return {"crater_diameter_km": 0.0, "note": "空爆/烧毁模式无实体撞击，不形成撞击坑"}

    rho_i = C.MATERIALS[material_key]["density"]
    rho_t = C.TARGET_DENSITY[target]
    v_ms = max(velocity_kms, 0.0) * 1000.0

    # 撞击体尺寸：优先用终端剩余质量反推等效直径（烧蚀/解体后尺寸已缩小）
    if impactor_mass_kg and impactor_mass_kg > 0:
        d_eff = 2.0 * ((3.0 * impactor_mass_kg) / (4.0 * math.pi * rho_i)) ** (1.0 / 3.0)
    else:
        d_eff = diameter_m

    sin_theta = max(math.sin(math.radians(max(angle_deg, 5.0))), 1e-3)

    D_t = 1.161 * (rho_i / rho_t) ** (1.0 / 3.0) \
          * (d_eff ** 0.78) * (v_ms ** 0.44) * (sin_theta ** (1.0 / 3.0))
    D_final = D_t * 1.25  # 重力塌陷修正
    return {"crater_diameter_km": D_final / 1000.0, "note": ""}
