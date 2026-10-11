# -*- coding: utf-8 -*-
"""
大气烧蚀 + 减速轨迹积分器（V1.1 核心新增模块）

复刻文档第四章第1节"大气阻力烧蚀理论"：
    高速天体在大气中受到气动压力、摩擦生热，质量持续损耗、结构受压。
    体积小、密度低、材质松散的天体，会在落地前彻底解体爆炸。

物理模型：Chyba, Thomas & Zahn (1993) + ReVelle (1979) 的简化欧拉积分。

控制方程（完整版，含重力与弹道倾角动态演化）：
    (1) 阻力：     m·dv/dt = -½·ρ_a·v²·C_D·A   （沿速度反方向）
    (2) 重力：     切向分量 a_g = -g(h)·sin(θ)，加入速度迭代
    (3) 烧蚀：     dm/dt = -½·ρ_a·v³·C_H·A / Q_abl  （仅 v > 3 km/s）
    (4) 高度：     dh/dt = -v·sin(θ)
    (5) 倾角演化： θ 由水平/垂直速度分量动态更新
                   dv_x = a_drag_x·dt
                   dv_y = (a_drag_y + g)·dt   （g 向下，v_y 正方向向下）
                   θ = atan2(v_y, v_x)
                   陨石减速时水平速度衰减更快，倾角持续变陡——真实弯曲弹道。

能量沉积模型（标准学术算法）：
    大气沉积能量 = 阻力做功功率 × dt = ½·ρ_a·v³·C_D·A·dt
    烧蚀质量损失仅消耗汽化内能（Q_abl），不直接计入大气冲击波能量。
    严格分离三类能量：初始动能 / 大气沉积 / 地面终端动能。

解体（pancake）模型：
    单次解体触发：当动压 q = ½·ρ_a·v² ≥ 材料强度 σ 时，物体横向破碎，
    横截面积瞬时放大 PANCAKE_FACTOR 倍 → 阻力与烧蚀激增 → 能量快速沉积到大气。
    本模型为单块体近似，不做多级碎块分裂；解体仅触发一次，通过
    breakup_triggered 标志位杜绝重复触发。

输出：
    - 沿轨迹采样（供前端动画绘制）
    - 解体点高度与触发时刻
    - 终态：到达地面时的剩余质量、速度、动能
    - 累积烧蚀质量与累积大气能量沉积
    - 沿轨迹能量沉积剖面峰值高度
    - 三类能量分离与分配占比（对标 NASA 撞击模拟器数据口径）
"""
import math

from . import constants as C
from .atmosphere import air_density_with_gradient
from .meteoroid import compute_mass, compute_radius_from_mass

# ───── 物理常数（本模块内部使用）─────
G0 = 9.81                          # 海平面重力加速度 m/s²
R_EARTH = 6_371_000.0              # 地球半径 m
ABLATION_SPEED_CUTOFF = 3000.0     # 烧蚀有效速度下限 m/s（暗飞行阶段阈值）


def _gravity_at_altitude(h):
    """高度 h (m) 处的重力加速度 m/s²，g(h) = g0 × (R / (R+h))²"""
    return G0 * (R_EARTH / (R_EARTH + h)) ** 2


def integrate_trajectory(diameter_m, material_key, velocity_kms,
                         entry_angle_deg, dt=0.01, sample_every=20):
    """
    沿入射路径积分，返回完整轨迹与终态信息

    Args:
        diameter_m:      初始直径 m
        material_key:    材质键
        velocity_kms:    初始入射速度 km/s
        entry_angle_deg: 入射角（与地面夹角）度，由用户输入，不做静默篡改
        dt:              时间步长 s
        sample_every:    每 N 步采样一次轨迹（控制返回数据量）

    Returns:
        dict with keys:
            samples      : 轨迹采样列表 [{t, h, v, m, q, e_atm_cumulative}]
            terminal     : 终态 {h, v, m, e_kinetic}
            breakup      : 解体点 {triggered, altitude, time, energy_so_far}
            ablation_kg  : 累积烧蚀质量
            energy_atm_j : 累积沉积到大气能量 J
            energy_peak_h_km : 沿轨迹能量沉积峰值高度 km
            energy_profile : 沿高度的累积能量沉积（粗采样，供动画）
            energy_distribution : 三类能量分配占比
    """
    # ───── 初始状态 ─────
    m0 = compute_mass(diameter_m, material_key)
    rho_body = C.MATERIALS[material_key]["density"]
    strength = C.MATERIALS[material_key]["strength"]

    m = m0
    v = velocity_kms * 1000.0                # m/s
    h = C.ATMOSPHERE_TOP                     # 200 km 起点

    # 弹道倾角（弧度），输入角度完全由用户决定，不篡改
    theta = math.radians(entry_angle_deg)

    # 分解为水平/垂直速度分量（v_y 正方向向下，用于弹道倾角动态演化）
    v_x = v * math.cos(theta)
    v_y = v * math.sin(theta)

    t = 0.0
    samples = []
    energy_atm = 0.0          # 累积大气能量沉积 J（仅阻力做功）
    energy_profile = []       # [(h_km, cumulative_energy_J)] 用于动画
    e_peak_dt_rate = 0.0      # 峰值能量沉积率 W
    e_peak_h = 0.0            # 峰值能量沉积高度 m

    breakup_triggered = False
    breakup_alt = 0.0
    breakup_t = 0.0
    breakup_e = 0.0
    pancake_mult = 1.0       # 解体后横截面放大倍数（仅触发一次）

    step = 0
    while h > 0 and m > m0 * 0.001:
        # ───── 1. 当前大气与重力环境 ─────
        rho_a = air_density_with_gradient(h)
        g = _gravity_at_altitude(h)

        # ───── 2. 当前几何与气动量 ─────
        r = compute_radius_from_mass(m, rho_body)
        A = math.pi * r * r * pancake_mult  # 解体后横截面积放大
        q = 0.5 * rho_a * v * v             # 动压

        # ───── 3. 大气能量沉积（标准算法：仅阻力做功功率 × dt）─────
        #    P_drag = F_drag × v = ½·ρ_a·v³·C_D·A
        #    dE = P_drag × dt
        #    烧蚀质量损失的能量来自汽化内能 Q_abl，不计入大气冲击波能量
        e_deposited = 0.5 * rho_a * (v ** 3) * C.DRAG_COEFFICIENT * A * dt
        energy_atm += e_deposited

        # 沿高度能量沉积峰值（找最剧烈的能量释放高度）
        if e_deposited / dt > e_peak_dt_rate:
            e_peak_dt_rate = e_deposited / dt
            e_peak_h = h

        # ───── 4. 解体触发判定（单次触发，杜绝重复）─────
        #  pancake 模型：动压 q ≥ 材料强度 σ 时横向破碎
        #  仅触发一次，breakup_triggered 标志位保证不重复
        if (not breakup_triggered) and (q >= strength):
            breakup_triggered = True
            breakup_alt = h
            breakup_t = t
            breakup_e = energy_atm
            pancake_mult = C.PANCAKE_FACTOR  # 横截面瞬时放大（本步生效于下一步）

        # ───── 5. 速度更新（阻力 + 重力切向分量，分解为 x/y）─────
        #  阻力加速度大小：a_drag = ½·ρ_a·v²·C_D·A / m
        #  阻力沿速度反方向分解：a_drag_x = -a_drag·(v_x/v), a_drag_y = -a_drag·(v_y/v)
        #  重力仅作用于垂直分量：a_grav_y = +g（向下为正）
        a_drag = (rho_a * v * v * C.DRAG_COEFFICIENT * A) / (2.0 * m)
        if v > 0:
            dv_x = -a_drag * (v_x / v) * dt
            dv_y = (-a_drag * (v_y / v) + g) * dt
        else:
            # v=0 时无阻力，仅重力
            dv_x = 0.0
            dv_y = g * dt
        v_x += dv_x
        v_y += dv_y

        # 合速度与速度下限保护（杜绝负速度参与运算）
        v = math.sqrt(v_x * v_x + v_y * v_y)
        v = max(v, 0.0)

        # ───── 6. 弹道倾角动态演化 ─────
        #  减速时水平速度衰减更快（阻力 ∝ v²，无重力补偿），
        #  垂直分量受重力持续加速 → v_y/v_x 增大 → 倾角变陡
        #  这是真实火流星弹道弯曲的物理根源
        if v > 0:
            theta = math.atan2(v_y, v_x)   # 新弹道倾角
            sin_theta = v_y / v             # sin(theta) = v_y / |v|
        else:
            sin_theta = 1.0

        # ───── 7. 烧蚀更新（仅高速段 v > 3 km/s，模拟暗飞行阶段截止）─────
        #  低速下气动加热不足以维持有效烧蚀，陨石进入暗飞行阶段
        if v > ABLATION_SPEED_CUTOFF:
            dm = -(rho_a * (v ** 3) * C.HEAT_TRANSFER_COEFF * A /
                   C.ABLATION_HEAT) * dt
        else:
            dm = 0.0  # 暗飞行阶段，停止烧蚀

        # ───── 8. 高度更新（使用当前步 v_y，Forward Euler）─────
        dh = -v_y * dt   # v_y 正方向向下，dh 为负

        # ───── 9. 状态推进 ─────
        m += dm
        h += dh
        t += dt
        step += 1

        if v <= 0:
            break

        # ───── 10. 采样 ─────
        if step % sample_every == 0:
            samples.append({
                "t": t,
                "h_km": h / 1000.0,
                "v_kms": v / 1000.0,
                "m_kg": m,
                "q_Pa": q,
                "e_atm_j": energy_atm,
            })
            energy_profile.append((h / 1000.0, energy_atm))

    # ───── 终态计算 ─────
    terminal_v = max(v, 0.0)
    terminal_m = max(m, 0.0)
    terminal_e_kin = 0.5 * terminal_m * terminal_v * terminal_v

    # 初始总动能（真空理论能量）
    initial_e_kin = 0.5 * m0 * (velocity_kms * 1000.0) ** 2

    # ───── 地面终点插值（优化跨地面步长精度）─────
    #  保留原有补采样机制，保证轨迹与爆炸点严格对齐
    if h <= 0 and terminal_m > m0 * 0.001:
        if samples:
            s = samples[-1]
            h_last = s["h_km"] * 1000.0
            if h_last > 0 and t > s["t"] and (h_last - h) > 0:
                # 线性插值到 h=0：求跨地面比例 frac
                frac = h_last / (h_last - h)
                t_ground = s["t"] + (t - s["t"]) * frac
                # v, m 在上一采样点与当前步末值之间按 frac 线性插值
                v_s_last = s["v_kms"] * 1000.0
                v_ground = v_s_last + (v - v_s_last) * frac
                m_s_last = s["m_kg"]
                m_ground = max(m_s_last + (terminal_m - m_s_last) * frac, 0.0)
            else:
                t_ground = t
                v_ground = terminal_v
                m_ground = terminal_m
        else:
            t_ground = t
            v_ground = terminal_v
            m_ground = terminal_m
        samples.append({
            "t": t_ground,
            "h_km": 0.0,
            "v_kms": v_ground / 1000.0,
            "m_kg": m_ground,
            "q_Pa": 0.0,
            "e_atm_j": energy_atm,
        })
        energy_profile.append((0.0, energy_atm))

    # ───── 三类能量分配占比（对标 NASA 数据口径）─────
    atm_ratio = energy_atm / initial_e_kin if initial_e_kin > 0 else 0.0
    ground_ratio = terminal_e_kin / initial_e_kin if initial_e_kin > 0 else 0.0

    return {
        "samples": samples,
        "terminal": {
            "h_km": max(h, 0.0) / 1000.0,
            "v_kms": terminal_v / 1000.0,
            "m_kg": terminal_m,
            "e_kinetic_j": terminal_e_kin,
            "impact_happened": h <= 0 and terminal_m > m0 * 0.001,
        },
        "breakup": {
            "triggered": breakup_triggered,
            "altitude_km": breakup_alt / 1000.0,
            "time_s": breakup_t,
            "energy_before_breakup_j": breakup_e,
        },
        "ablation_kg": m0 - terminal_m,
        "ablation_ratio": (m0 - terminal_m) / m0 if m0 > 0 else 0.0,
        "energy_atm_j": energy_atm,
        "energy_atm_ratio": atm_ratio,
        "energy_peak_h_km": e_peak_h / 1000.0,
        "energy_profile": energy_profile,
        "initial": {
            "mass_kg": m0,
            "velocity_kms": velocity_kms,
            "kinetic_energy_j": initial_e_kin,
        },
        # 三类能量分离与分配占比
        "energy_distribution": {
            "initial_kinetic_j": initial_e_kin,       # 初始总动能（真空理论能量）
            "atmospheric_j": energy_atm,               # 大气沉积能量（空爆/冲击波/热辐射损耗）
            "ground_impact_j": terminal_e_kin,         # 地面终端撞击动能（真实落地爆炸当量）
            "atmospheric_ratio": atm_ratio,            # 大气沉积占比
            "ground_impact_ratio": ground_ratio,        # 地面撞击占比
        },
    }
