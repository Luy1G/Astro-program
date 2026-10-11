# -*- coding: utf-8 -*-
"""
模拟编排器
负责串联各物理模块，从输入参数生成完整模拟结果（含轨迹采样用于动画）
"""
from physics import (constants, meteoroid, trajectory,
                     breakup, crater, shockwave, thermal, tsunami, classify)


def run_simulation(params):
    """
    输入参数：
        diameter, material, velocity, angle, target, depth, observer_distance
    输出：完整模拟结果 dict
    """
    diameter = float(params["diameter"])
    material = params["material"]
    velocity = float(params["velocity"])
    angle    = float(params["angle"])
    target   = params["target"]
    depth    = float(params.get("depth", 0))
    obs_dist = float(params.get("observer_distance", 0))

    # 1. 初始质量与动能
    mass0 = meteoroid.compute_mass(diameter, material)
    e0 = meteoroid.compute_kinetic_energy(mass0, velocity)
    tnt0_tons = meteoroid.joule_to_tnt_ton(e0)
    tnt0_kg = meteoroid.joule_to_tnt_kg(e0)
    fun_refs = meteoroid.compute_fun_references(tnt0_kg)

    # 2. ★ 大气轨迹积分（V1.1 核心）
    traj = trajectory.integrate_trajectory(
        diameter, material, velocity, angle,
        dt=0.01, sample_every=50,
    )

    # 3. 空爆/地撞判定（基于 trajectory 终态）
    mode_info = breakup.determine_mode(traj, diameter, material)
    release_e = mode_info["release_energy_j"]
    ground_eff = mode_info["ground_efficiency"]

    # 4. 实际释放能量的 TNT 当量
    tnt_release_tons = meteoroid.joule_to_tnt_ton(release_e)
    tnt_release_kg = meteoroid.joule_to_tnt_kg(release_e)

    # 5. 撞击坑
    crater_info = crater.compute_crater(
        diameter, material, velocity, target, release_e, mode_info["mode"]
    )

    # 6. 冲击波（基于真实释放能量）
    shock = shockwave.compute_shockwave(release_e, ground_eff)

    # 7. 热辐射
    ther = thermal.compute_thermal(release_e, ground_eff)

    # 8. 海啸
    tsu = tsunami.compute_tsunami(release_e, depth, target)

    # 9. 灾害等级（用真实释放能量定级）
    disaster = classify.classify_disaster(diameter, tnt_release_tons)

    # 10. 观测点损毁评估
    obs = classify.observer_damage(obs_dist, shock, ther)

    return {
        "input_echo": {
            "diameter_m": diameter,
            "material": material,
            "velocity_kms": velocity,
            "angle_deg": angle,
            "target": target,
            "ocean_depth_m": depth if target == "海洋" else None,
            "observer_distance_km": obs_dist,
        },
        "initial": {
            "mass_kg": mass0,
            "mass_tons": mass0 / 1000.0,
            "density_kg_m3": constants.MATERIALS[material]["density"],
            "kinetic_energy_j": e0,
            "tnt_tons": tnt0_tons,
            "tnt_mt": tnt0_tons / 1e6,
            "fun_references": fun_refs,
        },
        "trajectory": traj,
        "mode": mode_info,
        "release": {
            "energy_j": release_e,
            "tnt_tons": tnt_release_tons,
            "tnt_mt": tnt_release_tons / 1e6,
            "ground_efficiency": ground_eff,
        },
        "crater": crater_info,
        "shockwave": shock,
        "thermal": ther,
        "tsunami": tsu,
        "disaster_level": disaster,
        "observer_damage": obs,
    }
