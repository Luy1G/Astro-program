"""完整模拟管道验证 - 3483m 冰彗星"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2.2"))

from simulation import run_simulation

params = {
    "diameter": 3483,
    "velocity": 52,
    "angle": 68,
    "material": "冰彗星",
    "target": "海洋",
    "depth": 4000,
    "observer_distance": 100
}

result = run_simulation(params)

print("=" * 60)
print("完整模拟结果: 3483m冰彗星 52km/s 68° 海洋")
print("=" * 60)
print(f"初始质量: {result['initial']['mass_kg']:.2e} kg")
print(f"初始动能: {result['initial']['kinetic_energy_j']:.2e} J")
print(f"初始TNT: {result['initial']['tnt_tons']:.2e} 吨")
print(f"模式: {result['mode']['mode']}")
print(f"烧蚀率: {result['mode'].get('ablation_ratio', 0):.2%}")
print(f"终端释放能量: {result['release']['energy_j']:.2e} J")
print(f"终端TNT: {result['release']['tnt_tons']:.2e} 吨")
print()

tsunami_h = result['tsunami']['tsunami_height_m']
fireball = result['thermal']['fireball_radius_km']
burn = result['thermal']['burn_radius_km']
core = result['shockwave']['core_radius_km']
sec = result['shockwave']['secondary_radius_km']
outer = result['shockwave']['outer_radius_km']

print(f"海啸高度: {tsunami_h:.1f} m")
print(f"火球半径: {fireball:.2f} km")
print(f"烧伤半径: {burn:.2f} km")
print(f"冲击波核心: {core:.2f} km")
print(f"冲击波二级: {sec:.2f} km")
print(f"冲击波外层: {outer:.2f} km")
print()

dl = result['disaster_level']
print(f"灾害等级: {dl.get('level', dl.get('disaster_class', 'N/A'))}")
print(f"灾害描述: {dl.get('label', dl.get('description', 'N/A'))}")
if result['tsunami'].get('note'):
    print(f"海啸备注: {result['tsunami']['note']}")

print()
print("--- 合理性检查 ---")
assert tsunami_h <= 8000, f"海啸高度 {tsunami_h} 超过物理上限 8000m！"
assert tsunami_h > 1000, f"海啸高度 {tsunami_h} 太低"
assert fireball <= 100, f"火球半径 {fireball} 超过 100km！"
assert burn <= 5000, f"烧伤半径 {burn} 超过 5000km！"
print("✅ 所有数值均在物理合理范围内")
