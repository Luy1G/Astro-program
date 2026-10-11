# -*- coding: utf-8 -*-
"""
物理常数与基准数据（文档第二章第1节、第三章第2-3节）
"""

# ---------------- 材质密度与结构强度 ----------------
# 文档：岩石 ~3000, 铁 ~7800, 冰彗星 ~1000 kg/m³
# 强度为通用经验值（NASA Earth Impact Effects Program 推荐区间）
MATERIALS = {
    "冰彗星":   {"density": 1000.0, "strength": 1.0e6,  "desc": "质地松散，极易在大气中解体"},
    "岩石陨石": {"density": 3000.0, "strength": 5.0e6,  "desc": "普通球粒陨石，常见近地小行星"},
    "铁陨石":   {"density": 7800.0, "strength": 2.0e8,  "desc": "金属小行星碎片，穿透性极强"},
}

# ---------------- TNT 当量换算基准 ----------------
# 文档第三章第2节：1 吨 TNT = 4.184×10⁹ J
JOULES_PER_TNT_TON = 4.184e9
JOULES_PER_TNT_KG = 4.184e6
TNT_TON_PER_JOULE = 1.0 / JOULES_PER_TNT_TON
TNT_KG_PER_JOULE = 1.0 / JOULES_PER_TNT_KG

# ---------------- 趣味对标基准（kg TNT）----------------
# 文档第三章第3节
FUN_REFERENCES = {
    "标准军用手榴弹": 0.05,
    "普通航空炸弹":   500.0,
    "广岛原子弹":     1.5e7,           # 1.5 万吨 = 1.5×10⁷ kg
}

# ---------------- 大气动力学常数 ----------------
# 用于 trajectory.py 与 breakup.py
RHO_AIR_SEA = 1.225          # 海平面空气密度 kg/m³
SCALE_HEIGHT = 8500.0        # 大气标高 m
ATM_COLUMN_MASS = 1.0e4      # 整层大气柱质量 kg/m²
ATMOSPHERE_TOP = 200_000.0   # 大气模型顶 m（200km，覆盖热层大部分）

# 流星体气动系数（Chyba et al. 1993 / ReVelle 1979 推荐区间）
DRAG_COEFFICIENT = 1.0       # 球体阻力系数 C_D
HEAT_TRANSFER_COEFF = 0.1    # 传热系数 C_H
ABLATION_HEAT = 5.0e6        # 烧蚀热 J/kg（岩石/金属熔融汽化能耗）
PANCAKE_FACTOR = 5.0         # 解体后横截面瞬时放大倍数（pancake 模型）

# ---------------- 撞击目标介质 ----------------
TARGET_DENSITY = {
    "陆地": 2700.0,           # 地壳岩石密度 kg/m³
    "海洋": 1025.0,           # 海水密度 kg/m³
}

# ---------------- 冲击波超压缩放系数（Sachs）----------------
# 文档第五章第2节，单位 m/kg^(1/3)
OVERPRESSURE_SCALED_DIST = {
    "core":     2.0,         # 20 psi ≈ 138 kPa  地面汽化
    "secondary": 3.0,        # 10 psi ≈ 69  kPa  建筑坍塌
    "outer":    8.0,         # 1  psi ≈ 6.9 kPa  玻璃震碎
}

# ---------------- 热辐射常数 ----------------
# 文档第五章第3节
FIREBALL_COEFF = 0.0023                  # r_fireball = c × E^(1/3)
THIRD_DEGREE_BURN_FLUENCE = 4.184e5      # 10 cal/cm² J/m²
