# -*- coding: utf-8 -*-
"""
海洋撞击海啸高度（文档第五章第4节）
- 常规区 (E ≤ 10^10 J)：H = 0.07 × sqrt(E) / d^0.25（核爆经验公式可靠区间）
- 过渡区 (10^10 < E ≤ 10^22 J)：对数插值，从 H_at_1e10 平滑过渡到 H_MAX
  插值参数 t = log10(E/E_LOW) / log10(E_MAX/E_LOW) ∈ [0, 1]
  H = H_at_1e10 + (H_MAX - H_at_1e10) × t
- 灭绝级区 (E > 10^22 J)：H = H_MAX（物理上限）
E 单位 J，d 单位 m，H 单位 m
"""
import math

E_LOW_J  = 1.0e10       # 常规区上限，核爆经验公式可靠（对应 H ≈ 880 m）
E_MAX_J  = 1.0e22       # 灭绝级能量上限
H_MAX_M  = 8000.0       # 海啸高度物理上限（约海洋深度量级）


def compute_tsunami(release_energy_j, depth_m, target):
    if target != "海洋" or release_energy_j <= 0:
        return {"tsunami_height_m": 0.0, "note": "陆地撞击或无能量释放，无海啸"}
    if depth_m <= 0:
        depth_m = 1.0

    E = release_energy_j

    if E <= E_LOW_J:
        # 常规区：核爆经验公式直接使用（≤880 m）
        H = 0.07 * math.sqrt(E) / (depth_m ** 0.25)
        note = ""
    elif E >= E_MAX_J:
        # 灭绝级上限
        H = H_MAX_M
        note = "灭绝级撞击：海水汽化主导，海啸高度已达物理上限"
    else:
        # 过渡区：对数插值
        H_low = 0.07 * math.sqrt(E_LOW_J) / (depth_m ** 0.25)
        log_ratio = math.log10(E / E_LOW_J) / math.log10(E_MAX_J / E_LOW_J)
        t = max(0.0, min(1.0, log_ratio))
        H = H_low + (H_MAX_M - H_low) * t
        note = "大型撞击：海啸高度已接近物理上限" if t > 0.7 else ""

    return {"tsunami_height_m": H, "note": note}
