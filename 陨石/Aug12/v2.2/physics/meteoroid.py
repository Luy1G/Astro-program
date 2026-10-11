# -*- coding: utf-8 -*-
"""
陨石基础物理量：质量 / 动能 / TNT 当量 / 趣味对标
文档第二章第3节、第三章第1-3节
"""
import math

from . import constants as C


def radius_from_diameter(diameter_m):
    return diameter_m / 2.0


def cross_section_area(diameter_m):
    """横截面积 A = π r²"""
    r = radius_from_diameter(diameter_m)
    return math.pi * r * r


def compute_mass(diameter_m, material_key):
    """
    球体质量公式（文档第二章第3节）：
        M = (4/3) × π × r³ × ρ
    """
    r = radius_from_diameter(diameter_m)
    rho = C.MATERIALS[material_key]["density"]
    return (4.0 / 3.0) * math.pi * (r ** 3) * rho


def compute_radius_from_mass(mass_kg, density):
    """由质量反推当前半径（质量因烧蚀减少时半径随之收缩）"""
    if mass_kg <= 0 or density <= 0:
        return 0.0
    return ((3.0 * mass_kg) / (4.0 * math.pi * density)) ** (1.0 / 3.0)


def compute_kinetic_energy(mass_kg, velocity_kms):
    """
    动能公式（文档第三章第1节）：
        E = ½ × M × v²   (v 需转为 m/s)
    """
    v_ms = velocity_kms * 1000.0
    return 0.5 * mass_kg * v_ms * v_ms


def joule_to_tnt_ton(energy_j):
    """J → 吨 TNT"""
    return energy_j * C.TNT_TON_PER_JOULE


def joule_to_tnt_kg(energy_j):
    """J → kg TNT"""
    return energy_j * C.TNT_KG_PER_JOULE


def compute_fun_references(tnt_kg):
    """趣味对标（文档第三章第3节）"""
    return {name: tnt_kg / kg for name, kg in C.FUN_REFERENCES.items()}
