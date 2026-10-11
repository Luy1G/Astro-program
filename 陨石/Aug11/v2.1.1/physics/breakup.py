# -*- coding: utf-8 -*-
"""
空爆/地撞判定模块（V1.1）
基于 trajectory 积分结果判定模式与释放能量
"""
from . import constants as C


def determine_mode(trajectory_result, diameter_m, material_key):
    """
    根据 trajectory 积分结果判定：
      - 烧毁   ：未触发解体且未到地面（小天体在大气中彻底损耗）
      - 空爆   ：触发解体且解体后能量耗尽（pancake 后未触地）
      - 地撞   ：天体到达地面（无论是否解体）
                - 解体后地撞：pancake 模型，碎片云撞击
                - 完整地撞：未触发解体，硬撞击

    释放能量分配：
      - 地撞模式：终态动能 → 撞击坑与地表灾害
      - 空爆模式：解体后沉积在大气的能量 → 低空冲击波
      - 烧毁模式：几乎全部能量在大气沉积，地面无影响
    """
    term = trajectory_result["terminal"]
    brk = trajectory_result["breakup"]
    init_e = trajectory_result["initial"]["kinetic_energy_j"]

    impact = term["impact_happened"]
    triggered = brk["triggered"]

    if impact:
        # 地表撞击（包含解体后碎片撞击）
        if triggered:
            mode = "地表撞击（解体后碎片云撞击）"
        else:
            mode = "地表撞击（完整硬撞击）"
        ground_efficiency = 1.0
        release_energy = term["e_kinetic_j"]   # 用真实剩余动能
        release_altitude_km = 0.0
    elif triggered:
        # 纯空爆：解体后未到地面，剩余能量沉积在解体高度附近
        mode = "空爆（通古斯模式）"
        ground_efficiency = 0.85                # 空爆杀伤效率高
        release_energy = term["e_kinetic_j"]    # 解体后剩余动能（沉积在低空）
        release_altitude_km = brk["altitude_km"]
    else:
        # 烧毁：未触发解体也未触地（极小天体）
        mode = "大气烧毁（无地面影响）"
        ground_efficiency = 0.0
        release_energy = 0.0
        release_altitude_km = trajectory_result["energy_peak_h_km"]

    # 穿透比（用于解释为何 km 级天体必然地撞）
    rho_body = C.MATERIALS[material_key]["density"]
    r = diameter_m / 2.0
    mass_per_area = (4.0 / 3.0) * r * rho_body
    penetration_ratio = mass_per_area / C.ATM_COLUMN_MASS

    return {
        "mode": mode,
        "ground_efficiency": ground_efficiency,
        "release_energy_j": release_energy,
        "release_altitude_km": release_altitude_km,
        "energy_atm_ratio": trajectory_result["energy_atm_ratio"],
        "ablation_ratio": trajectory_result["ablation_ratio"],
        "penetration_ratio": penetration_ratio,
        "material_strength_MPa":
            C.MATERIALS[material_key]["strength"] / 1.0e6,
        "breakup_altitude_km": brk["altitude_km"] if triggered else None,
        "initial_kinetic_energy_j": init_e,
    }
