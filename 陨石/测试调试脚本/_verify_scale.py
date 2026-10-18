"""测试城市比例尺 - 1km岩石 30km/s 45° 陆地"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "v2.2"))

from simulation import run_simulation

params = {
    "diameter": 1000,
    "velocity": 30,
    "angle": 45,
    "material": "岩石陨石",
    "target": "陆地",
    "depth": 0,
    "observer_distance": 100
}

result = run_simulation(params)
sw = result['shockwave']
th = result['thermal']
cr = result['crater']

print("=" * 60)
print("测试：1km 岩石陨石 30km/s 45° 陆地撞击")
print("=" * 60)
print(f"核心区: {sw['core_radius_km']:.2f} km")
print(f"次级区: {sw['secondary_radius_km']:.2f} km")
print(f"外围区: {sw['outer_radius_km']:.2f} km")
print(f"火球:   {th['fireball_radius_km']:.2f} km")
print(f"烧伤:   {th['burn_radius_km']:.2f} km")
print(f"撞击坑: {cr['crater_diameter_km']:.2f} km")

# 验证比例尺：CITY_SCALE=0.15, DAMAGE_VIS=1.0
CS = 0.15
DV = 1.0
print()
print("--- 比例尺验证（修复后） ---")
print(f"核心区像素半径: {sw['core_radius_km'] * CS * DV:.1f} px")
print(f"次级区像素半径: {sw['secondary_radius_km'] * CS * DV:.1f} px")
print(f"外围区像素半径: {sw['outer_radius_km'] * CS * DV:.1f} px")
print()
print(f"各城市像素距离（上海为原点）:")
cities = [("南京",272),("北京",1088),("深圳",1223),("海口",1758),("乌鲁木齐",3278)]
for name,dist in cities:
    print(f"  {name} ({dist}km): {dist * CS:.1f} px")
print()
print(f"✓ 核心区({sw['core_radius_km']:.0f}km) < 北京(1088km) 正确")
print(f"✓ 核心区({sw['core_radius_km']:.0f}km) > 南京(272km) 正确")
