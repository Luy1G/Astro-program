# -*- coding: utf-8 -*-
import sys, os
V22 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "v2.2")
sys.path.insert(0, V22)
os.chdir(V22)
from simulation import run_simulation

# 测试1 通古斯式
r = run_simulation({'diameter':60,'material':'岩石陨石','velocity':27,'angle':45,'target':'陆地','depth':0,'observer_distance':100})
print('--- PY 测试1 ---')
print('mode:', r['mode']['mode'])
print('release_tnt_tons:', r['release']['tnt_tons'])
print('ablation_ratio:', r['trajectory']['ablation_ratio'])
print('core_radius_km:', r['shockwave']['core_radius_km'])
print('crater_diameter_km:', r['crater']['crater_diameter_km'])
print('disaster_level:', r['disaster_level']['level'])
print('samples:', len(r['trajectory']['samples']))

# 测试2 200m陆地
r2 = run_simulation({'diameter':200,'material':'岩石陨石','velocity':25,'angle':45,'target':'陆地','depth':0,'observer_distance':50})
print('--- PY 测试2 ---')
print('mode:', r2['mode']['mode'])
print('mass_tons:', r2['initial']['mass_tons'])
print('release_tnt_tons:', r2['release']['tnt_tons'])
print('fireball_r:', r2['thermal']['fireball_radius_km'])
print('burn_r:', r2['thermal']['burn_radius_km'])
print('core_r:', r2['shockwave']['core_radius_km'])
print('outer_r:', r2['shockwave']['outer_radius_km'])
print('crater_d:', r2['crater']['crater_diameter_km'])
print('disaster:', r2['disaster_level']['level'])

# 测试3 冰彗星海洋
r4 = run_simulation({'diameter':300,'material':'冰彗星','velocity':35,'angle':15,'target':'海洋','depth':4000,'observer_distance':500})
print('--- PY 测试4 ---')
print('mode:', r4['mode']['mode'])
print('tsunami_h:', r4['tsunami']['tsunami_height_m'])
print('crater_d:', r4['crater']['crater_diameter_km'])
print('ablation_ratio:', r4['trajectory']['ablation_ratio'])
