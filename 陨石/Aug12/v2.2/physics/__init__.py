# -*- coding: utf-8 -*-
"""
陨石撞击模拟 V1.1 物理模块包

模块分工：
    constants  : 物理常数、材质密度、TNT 当量基准、趣味对标
    atmosphere : 标准大气密度模型
    meteoroid  : 质量 / 动能 / TNT 当量
    trajectory : ★ 大气烧蚀+减速轨迹积分器（V1.1 新增，核心物理）
    breakup    : 空爆/地撞判定（结合 trajectory 结果）
    crater     : 撞击坑直径（Collins et al. 2005）
    shockwave  : 冲击波三区半径（Sachs 缩放）
    thermal    : 火球半径 + 热辐射烧伤半径
    tsunami    : 海洋撞击海啸高度
    classify   : 灾害等级分类
"""

from . import constants
from . import atmosphere
from . import meteoroid
from . import trajectory
from . import breakup
from . import crater
from . import shockwave
from . import thermal
from . import tsunami
from . import classify

__all__ = [
    "constants", "atmosphere", "meteoroid", "trajectory",
    "breakup", "crater", "shockwave", "thermal", "tsunami", "classify",
]
