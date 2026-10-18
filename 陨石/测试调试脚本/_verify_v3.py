# -*- coding: utf-8 -*-
"""v3.0 陆地模式验证脚本"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "final", "v3.0"))

from simulation import run_simulation

print("=" * 60)
print("陆地陨石撞击模拟器 v3.0 验证测试")
print("=" * 60)
print()

def 运行单个测试(标题, 参数, 断言):
    print(f"--- {标题} ---")
    try:
        r = run_simulation(参数)
        # 检查 key
        海啸字段 = r.get("tsunami")
        if 海啸字段 is not None:
            print(f"  ❌ 仍存在 tsunami 字段: {海啸字段}")
            return False
        # 检查 target
        echo = r["input_echo"]
        if echo["target"] != "陆地":
            print(f"  ❌ input_echo.target = {echo['target']}，应为'陆地'")
            return False
        if echo.get("ocean_depth_m") is not None and echo.get("ocean_depth_m") != 0:
            print(f"  ❌ ocean_depth_m 应为 None/0: {echo.get('ocean_depth_m')}")
            return False
        # 检查撞击坑
        if "海洋" in r["crater"].get("note", ""):
            print(f"  ❌ 撞击坑 note 中有海洋: {r['crater']['note']}")
            return False
        # 用户断言
        ok, msg = 断言(r)
        if not ok:
            print(f"  ❌ {msg}")
            return False
        print(f"  ✅ 核心区 {r['shockwave']['core_radius_km']:.1f} 千米，"
              f"次级区 {r['shockwave']['secondary_radius_km']:.1f} 千米，"
              f"撞击坑 {r['crater']['crater_diameter_km']:.1f} 千米，"
              f"灾害等级 {r['disaster_level'].get('level', r['disaster_level'].get('disaster_class','?'))}")
        return True
    except Exception as e:
        print(f"  ❌ 异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

# 测试1：用户反馈场景 —— 1000米岩石陨石 30km/s 45° 陆地
def 断言1(r):
    sw = r["shockwave"]
    # 核心区约 394.67 千米（之前已算过）
    if abs(sw["core_radius_km"] - 394.67) > 50:
        return False, f"核心区 {sw['core_radius_km']:.1f} 千米 ≠ 预期 ~395 千米"
    return True, ""

t1 = 运行单个测试("1000米 岩石陨石 30千米每秒 45度 陆地", {
    "diameter": 1000, "velocity": 30, "angle": 45,
    "material": "岩石陨石", "target": "陆地",
    "depth": 0, "observer_distance": 500
}, 断言1)
print()

# 测试2：海洋 target 输入是否被强制转换为陆地
def 断言2(r):
    if r["input_echo"]["target"] != "陆地":
        return False, "target 未被强制转换为陆地"
    if "tsunami" in r and r["tsunami"].get("tsunami_height_m", 0) > 0:
        return False, "不应产生海啸"
    return True, ""

t2 = 运行单个测试("输入 target=海洋 看是否强制转换陆地", {
    "diameter": 500, "velocity": 20, "angle": 30,
    "material": "岩石陨石", "target": "海洋",
    "depth": 4000, "observer_distance": 100
}, 断言2)
print()

# 测试3：微型撞击
def 断言3(r):
    ok = r["shockwave"]["outer_radius_km"] > 0.5
    return ok, "冲击波半径应>0.5千米" if not ok else ""

t3 = 运行单个测试("微型：50米 岩石陨石 15千米每秒 60度 陆地", {
    "diameter": 50, "velocity": 15, "angle": 60,
    "material": "岩石陨石", "target": "陆地",
    "observer_distance": 10
}, 断言3)
print()

# 测试4：铁陨石大撞击
def 断言4(r):
    d = r["disaster_level"].get("level", "")
    return d in ("大型灾变", "灭绝级撞击"), f"灾害等级={d}, 应为大型或灭绝级"

t4 = 运行单个测试("灭绝级：3000米 铁陨石 50千米每秒 70度 陆地", {
    "diameter": 3000, "velocity": 50, "angle": 70,
    "material": "铁陨石", "target": "陆地",
    "observer_distance": 1000
}, 断言4)
print()

print("=" * 60)
结果 = [t1, t2, t3, t4]
print(f"测试通过: {sum(结果)}/{len(结果)}")
if all(结果):
    print("✅ v3.0 陆地陨石撞击模拟器全部测试通过")
else:
    print("❌ 有测试失败，请查看上方日志")
print("=" * 60)

sys.exit(0 if all(结果) else 1)
