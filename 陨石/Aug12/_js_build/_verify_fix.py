"""全面修复后验证脚本"""
import sys, os
# 将 v2.2 目录加入 sys.path（不是包，所以直接加父目录）
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2.2"))

from physics.tsunami import compute_tsunami
from physics.thermal import compute_thermal
from physics.shockwave import compute_shockwave

print("=" * 60)
print("测试1: 3483m冰彗星 52km/s 68° 海洋")
e_release = 5.61e21  # 灭绝级能量
depth = 4000

t = compute_tsunami(e_release, depth, "海洋")
th = compute_thermal(e_release, 0.6)
sw = compute_shockwave(e_release, 0.6)

print(f"  海啸高度: {t['tsunami_height_m']:.1f} m")
print(f"  火球半径: {th['fireball_radius_km']:.2f} km")
print(f"  烧伤半径: {th['burn_radius_km']:.2f} km")
print(f"  冲击波核心: {sw['core_radius_km']:.2f} km")
print(f"  冲击波二级: {sw['secondary_radius_km']:.2f} km")
print(f"  冲击波外层: {sw['outer_radius_km']:.2f} km")
if t.get("note"):
    print(f"  备注: {t['note']}")
print()

print("=" * 60)
print("测试2: 200m岩石 25km/s 45° 海洋（中型）")
e2 = 2.38e14
t2 = compute_tsunami(e2, depth, "海洋")
th2 = compute_thermal(e2, 0.6)
sw2 = compute_shockwave(e2, 0.6)

print(f"  海啸高度: {t2['tsunami_height_m']:.1f} m")
print(f"  火球半径: {th2['fireball_radius_km']:.2f} km")
print(f"  烧伤半径: {th2['burn_radius_km']:.2f} km")
print(f"  冲击波核心: {sw2['core_radius_km']:.2f} km")
if t2.get("note"):
    print(f"  备注: {t2['note']}")
print()

print("=" * 60)
print("测试3: 50m岩石 20km/s 45° 海洋（小型）")
e3 = 5.6e12
t3 = compute_tsunami(e3, depth, "海洋")
th3 = compute_thermal(e3, 0.6)
sw3 = compute_shockwave(e3, 0.6)

print(f"  海啸高度: {t3['tsunami_height_m']:.1f} m")
print(f"  火球半径: {th3['fireball_radius_km']:.2f} km")
print(f"  烧伤半径: {th3['burn_radius_km']:.2f} km")
print(f"  冲击波核心: {sw3['core_radius_km']:.2f} km")
print()

print("=" * 60)
print("测试4: 10m岩石 15km/s 45° 海洋（微型）")
e4 = 2.5e10
t4 = compute_tsunami(e4, depth, "海洋")
th4 = compute_thermal(e4, 0.6)
sw4 = compute_shockwave(e4, 0.6)

print(f"  海啸高度: {t4['tsunami_height_m']:.1f} m")
print(f"  火球半径: {th4['fireball_radius_km']:.2f} km")
print(f"  烧伤半径: {th4['burn_radius_km']:.2f} km")
print(f"  冲击波核心: {sw4['core_radius_km']:.2f} km")
print()

print("=" * 60)
print("测试5: 1kt 核武器（参考基准）")
e5 = 4.184e12  # 1kt TNT
t5 = compute_tsunami(e5, depth, "海洋")
th5 = compute_thermal(e5, 0.6)
sw5 = compute_shockwave(e5, 0.6)

print(f"  海啸高度: {t5['tsunami_height_m']:.1f} m")
print(f"  火球半径: {th5['fireball_radius_km']:.2f} km")
print(f"  烧伤半径: {th5['burn_radius_km']:.2f} km")
print(f"  冲击波核心: {sw5['core_radius_km']:.2f} km")
print()

print("=" * 60)
print("测试6: 广岛原子弹 15kt")
e6 = 6.276e13  # 15kt TNT
t6 = compute_tsunami(e6, depth, "海洋")
th6 = compute_thermal(e6, 0.6)
sw6 = compute_shockwave(e6, 0.6)

print(f"  海啸高度: {t6['tsunami_height_m']:.1f} m")
print(f"  火球半径: {th6['fireball_radius_km']:.2f} km")
print(f"  烧伤半径: {th6['burn_radius_km']:.2f} km")
print(f"  冲击波核心: {sw6['core_radius_km']:.2f} km")
print()

print("✅ 所有测试完成")
