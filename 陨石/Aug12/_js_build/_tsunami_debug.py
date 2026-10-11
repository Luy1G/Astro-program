# -*- coding: utf-8 -*-
import sys, os
V22 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2.2")
sys.path.insert(0, V22)
os.chdir(V22)
from simulation import run_simulation
import math

# 用户参数：冰彗星 3483m 52km/s 68度 海洋
r = run_simulation({
    'diameter': 3483,
    'material': '冰彗星',
    'velocity': 52,
    'angle': 68,
    'target': '海洋',
    'depth': 4000,
    'observer_distance': 500
})

print("=== 全量物理输出 ===")
print("1. 初始质量:")
print(f"   mass_kg: {r['initial']['mass_kg']:.3e} kg")
print(f"   mass_tons: {r['initial']['mass_tons']:.3e} t")
print(f"   density: {r['initial']['density_kg_m3']} kg/m³")
print(f"   kinetic_energy_j: {r['initial']['kinetic_energy_j']:.3e} J")
print(f"   tnt_tons: {r['initial']['tnt_tons']:.3e} t")
print()

print("2. 轨迹终态:")
t = r['trajectory']['terminal']
print(f"   mode: {r['mode']['mode']}")
print(f"   impact_happened: {t['impact_happened']}")
print(f"   v_kms: {t['v_kms']:.3f} km/s")
print(f"   m_kg: {t['m_kg']:.3e} kg")
print(f"   e_kinetic_j: {t['e_kinetic_j']:.3e} J")
print(f"   ablation_ratio: {r['trajectory']['ablation_ratio']:.4f}")
print(f"   ablation_kg: {r['trajectory']['ablation_kg']:.3e} kg")
print(f"   energy_atm_ratio: {r['trajectory']['energy_atm_ratio']:.4f}")
print(f"   breakup: {r['trajectory']['breakup']}")
print()

print("3. 释放能量:")
print(f"   release_energy_j: {r['release']['energy_j']:.3e} J")
print(f"   release_tnt_tons: {r['release']['tnt_tons']:.3e} t")
print(f"   ground_efficiency: {r['release']['ground_efficiency']}")
print()

print("4. 冲击波:")
print(f"   core_radius_km: {r['shockwave']['core_radius_km']:.3f} km")
print(f"   secondary_radius_km: {r['shockwave']['secondary_radius_km']:.3f} km")
print(f"   outer_radius_km: {r['shockwave']['outer_radius_km']:.3f} km")
print(f"   tnt_kg: {r['shockwave']['tnt_kg']:.3e} kg")
print()

print("5. 热辐射:")
print(f"   fireball_radius_km: {r['thermal']['fireball_radius_km']:.3f} km")
print(f"   burn_radius_km: {r['thermal']['burn_radius_km']:.3f} km")
print()

print("6. 海啸:")
print(f"   tsunami_height_m: {r['tsunami']['tsunami_height_m']:.3f} m")
print(f"   note: {r['tsunami']['note']}")
print()

print("7. 撞击坑:")
print(f"   crater_diameter_km: {r['crater']['crater_diameter_km']:.3f} km")
print(f"   note: {r['crater']['note']}")
print()

print("8. 灾害等级:")
print(f"   level: {r['disaster_level']['level']}")
print(f"   description: {r['disaster_level']['description']}")

# ===== 海啸公式溯源分析 =====
print("\n\n=== 海啸公式溯源分析 ===")
release_e = r['release']['energy_j']
depth = 4000
H = 0.07 * math.sqrt(release_e) / (depth ** 0.25)
print(f"release_energy_j = {release_e:.3e}")
print(f"sqrt(release_e) = {math.sqrt(release_e):.3e}")
print(f"depth^0.25 = {depth**0.25:.3f}")
print(f"H = 0.07 * sqrt(E) / d^0.25 = {H:.3f} m")

# 对比：如果用初始动能
init_e = r['initial']['kinetic_energy_j']
H_init = 0.07 * math.sqrt(init_e) / (depth ** 0.25)
print(f"\n如果用初始动能 E0={init_e:.3e}:")
print(f"  H = {H_init:.3f} m")

# 对比：如果用实际释放的 TNT 当量
release_tnt = r['release']['tnt_tons']
H_tnt = 0.07 * math.sqrt(release_tnt * 4.184e9) / (depth ** 0.25)
print(f"\n用 release_tnt={release_tnt:.3e} t:")
print(f"  H = {H_tnt:.3f} m")

# 理论极限分析
print("\n=== 物理合理性分析 ===")
print(f"海啸高度 {H:.0f} m = {H/1000:.2f} km")
if H > 1000:
    print("⚠️  海啸高度 > 1000m，超出合理范围！")
    print("原因：简化公式 H ∝ √E 在 E 极大时严重失真。")
    print("实际物理中，灭绝级撞击的海啸应由浅水长波公式建模，")
    print("且会产生海平面大幅抬升而非简单的点源浪高。")
