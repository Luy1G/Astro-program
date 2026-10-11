# -*- coding: utf-8 -*-
"""
模拟编排器（陆地陨石撞击模拟器 v3.0）
负责串联各物理模块，从输入参数生成完整模拟结果（含轨迹采样用于动画）
已移除海洋撞击 / 海啸 全部逻辑，强制 target=陆地
"""
from physics import (constants, meteoroid, trajectory,
                     breakup, crater, shockwave, thermal, classify)


def run_simulation(params):
    """
    输入参数：
        diameter 直径（米）, material 材质, velocity 速度（千米/秒）,
        angle 入射角（度）, target 撞击目标（固定=陆地）,
        observer_distance 观测距离（千米）
    输出：完整模拟结果 dict
    """
    diameter = float(params["diameter"])
    material = params["material"]
    velocity = float(params["velocity"])
    angle    = float(params["angle"])
    # v3.0：固定为陆地撞击，忽略 target 和深度 参数
    target   = "陆地"
    obs_dist = float(params.get("observer_distance", 0))

    # 1. 初始质量（千克）与动能（焦耳）
    mass0 = meteoroid.compute_mass(diameter, material)
    e0 = meteoroid.compute_kinetic_energy(mass0, velocity)
    tnt0_tons = meteoroid.joule_to_tnt_ton(e0)
    tnt0_kg = meteoroid.joule_to_tnt_kg(e0)
    fun_refs = meteoroid.compute_fun_references(tnt0_kg)

    # 2. ★ 大气轨迹积分（Chyba 1993 + ReVelle 1979 模型）
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

    # 5. 撞击坑（仅陆地）
    crater_info = crater.compute_crater(
        diameter, material, velocity, target, release_e, mode_info["mode"]
    )

    # 6. 冲击波（基于真实释放能量，焦耳）
    shock = shockwave.compute_shockwave(release_e, ground_eff)

    # 7. 热辐射（基于真实释放能量，焦耳）
    ther = thermal.compute_thermal(release_e, ground_eff)

    # 8. 灾害等级（用真实释放能量定级，单位=吨TNT）
    disaster = classify.classify_disaster(diameter, tnt_release_tons)

    # 9. 观测点损毁评估（观测距离，千米）
    obs = classify.observer_damage(obs_dist, shock, ther)

    return {
        "input_echo": {
            "diameter_m": diameter,          # 米
            "material": material,
            "velocity_kms": velocity,       # 千米/秒
            "angle_deg": angle,             # 度
            "target": target,               # 固定=陆地
            "observer_distance_km": obs_dist,  # 千米
        },
        "initial": {
            "mass_kg": mass0,               # 千克
            "mass_tons": mass0 / 1000.0,    # 吨
            "density_kg_m3": constants.MATERIALS[material]["density"],  # 千克/立方米
            "kinetic_energy_j": e0,         # 焦耳
            "tnt_tons": tnt0_tons,          # 吨TNT当量
            "tnt_mt": tnt0_tons / 1e6,      # 百万吨TNT当量
            "fun_references": fun_refs,
        },
        "trajectory": traj,
        "mode": mode_info,
        "release": {
            "energy_j": release_e,          # 焦耳
            "tnt_tons": tnt_release_tons,   # 吨TNT当量
            "tnt_mt": tnt_release_tons / 1e6,  # 百万吨TNT当量
            "ground_efficiency": ground_eff,
        },
        "crater": crater_info,
        "shockwave": shock,
        "thermal": ther,
        # v3.0：已移除 tsunami（海啸）字段
        "disaster_level": disaster,
        "observer_damage": obs,
    }
