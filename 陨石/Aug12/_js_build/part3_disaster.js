// ============================================================
// Part 3: Disaster Modules + run_simulation Orchestrator
// 翻译对应：breakup / crater / shockwave / thermal / tsunami / classify + simulation
// 依赖：C (constants) 及 meteoroid/trajectory 等之前的全局函数
// ============================================================

// -------------------- breakup: determine_mode --------------------
function determine_mode(trajectory_result, diameter_m, material_key) {
    var term = trajectory_result["terminal"];
    var brk = trajectory_result["breakup"];
    var init_e = trajectory_result["initial"]["kinetic_energy_j"];

    var impact = term["impact_happened"];
    var triggered = brk["triggered"];

    var mode, ground_efficiency, release_energy, release_altitude_km;

    if (impact) {
        if (triggered) {
            mode = "地表撞击（解体后碎片云撞击）";
        } else {
            mode = "地表撞击（完整硬撞击）";
        }
        ground_efficiency = 1.0;
        release_energy = term["e_kinetic_j"];
        release_altitude_km = 0.0;
    } else if (triggered) {
        mode = "空爆（通古斯模式）";
        ground_efficiency = 0.85;
        release_energy = term["e_kinetic_j"];
        release_altitude_km = brk["altitude_km"];
    } else {
        mode = "大气烧毁（无地面影响）";
        ground_efficiency = 0.0;
        release_energy = 0.0;
        release_altitude_km = trajectory_result["energy_peak_h_km"];
    }

    var rho_body = C.MATERIALS[material_key]["density"];
    var r = diameter_m / 2.0;
    var mass_per_area = (4.0 / 3.0) * r * rho_body;
    var penetration_ratio = mass_per_area / C.ATM_COLUMN_MASS;

    return {
        "mode": mode,
        "ground_efficiency": ground_efficiency,
        "release_energy_j": release_energy,
        "release_altitude_km": release_altitude_km,
        "energy_atm_ratio": trajectory_result["energy_atm_ratio"],
        "ablation_ratio": trajectory_result["ablation_ratio"],
        "penetration_ratio": penetration_ratio,
        "material_strength_MPa":
            C.MATERIALS[material_key]["strength"] / 1.0e6,
        "breakup_altitude_km": triggered ? brk["altitude_km"] : null,
        "initial_kinetic_energy_j": init_e,
    };
}

// -------------------- crater: compute_crater --------------------
function compute_crater(diameter_m, material_key, velocity_kms, target,
                        impact_energy_j, mode) {
    if (target === "海洋") {
        return {"crater_diameter_km": 0.0, "note": "海洋撞击不形成硬质坑体，转为海啸模型"};
    }
    if (mode.indexOf("空爆") !== -1 || mode.indexOf("烧毁") !== -1) {
        return {"crater_diameter_km": 0.0, "note": "空爆/烧毁模式无实体撞击，不形成撞击坑"};
    }

    var rho_i = C.MATERIALS[material_key]["density"];
    var rho_t = C.TARGET_DENSITY[target];
    var v_ms = velocity_kms * 1000.0;
    var sin_theta = 1.0;

    var D_t = 1.161 * Math.pow(rho_i / rho_t, 1.0 / 3.0)
          * Math.pow(diameter_m, 0.78) * Math.pow(v_ms, 0.44) * Math.pow(sin_theta, 1.0 / 3.0);
    var D_final = D_t * 1.25;
    return {"crater_diameter_km": D_final / 1000.0, "note": ""};
}

// -------------------- shockwave: compute_shockwave --------------------
function compute_shockwave(release_energy_j, ground_efficiency) {
    var e = release_energy_j * ground_efficiency;
    var tnt_kg = e * C.TNT_KG_PER_JOULE;
    var w13 = tnt_kg > 0 ? Math.pow(tnt_kg, 1.0 / 3.0) : 0.0;
    return {
        "core_radius_km":      (C.OVERPRESSURE_SCALED_DIST["core"]      * w13) / 1000.0,
        "secondary_radius_km": (C.OVERPRESSURE_SCALED_DIST["secondary"] * w13) / 1000.0,
        "outer_radius_km":     (C.OVERPRESSURE_SCALED_DIST["outer"]     * w13) / 1000.0,
        "tnt_kg": tnt_kg,
    };
}

// -------------------- thermal: compute_thermal --------------------
function compute_thermal(release_energy_j, ground_efficiency) {
    var e = release_energy_j * ground_efficiency;
    if (e <= 0) {
        return {"fireball_radius_km": 0.0, "burn_radius_km": 0.0};
    }
    var r_fireball = C.FIREBALL_COEFF * Math.pow(e, 1.0 / 3.0);
    var r_burn = Math.sqrt(e / (4.0 * Math.PI * C.THIRD_DEGREE_BURN_FLUENCE));
    return {
        "fireball_radius_km": r_fireball / 1000.0,
        "burn_radius_km": r_burn / 1000.0,
    };
}

// -------------------- tsunami: compute_tsunami --------------------
function compute_tsunami(release_energy_j, depth_m, target) {
    if (target !== "海洋" || release_energy_j <= 0) {
        return {"tsunami_height_m": 0.0, "note": "陆地撞击或无能量释放，无海啸"};
    }
    if (depth_m <= 0) {
        depth_m = 1.0;
    }
    var H = 0.07 * Math.sqrt(release_energy_j) / Math.pow(depth_m, 0.25);
    return {"tsunami_height_m": H, "note": ""};
}

// -------------------- classify: classify_disaster + observer_damage --------------------
function classify_disaster(diameter_m, tnt_tons) {
    if (diameter_m < 20 || tnt_tons < 1e3) {
        return {"level": "微型撞击", "description": "10m级，大气消耗，无地面损伤"};
    }
    if (diameter_m < 50 || tnt_tons < 1e6) {
        return {"level": "小型灾害", "description": "20–50m，局部城市损毁"};
    }
    if (diameter_m < 500 || tnt_tons < 1e9) {
        return {"level": "中型灾难", "description": "100m级，城市群毁灭"};
    }
    if (diameter_m < 2000 || tnt_tons < 1e12) {
        return {"level": "大型灾变", "description": "1km级，区域性生态崩溃"};
    }
    return {"level": "灭绝级撞击", "description": "10km+，全球圈层破坏、生物大灭绝"};
}

function observer_damage(observer_distance_km, shock, thermal) {
    var d = observer_distance_km;
    if (d <= shock["core_radius_km"]) {
        return "位于核心摧毁区：地面汽化、完全毁灭";
    }
    if (d <= shock["secondary_radius_km"]) {
        return "位于次级区：建筑完全坍塌、林木焚毁";
    }
    if (d <= thermal["burn_radius_km"]) {
        return "位于热辐射烧伤区：三度烧伤、可燃物起火";
    }
    if (d <= shock["outer_radius_km"]) {
        return "位于外围区：玻璃震碎、轻度损毁";
    }
    return "位于安全区：基本无影响";
}

// -------------------- simulation: run_simulation 编排器 --------------------
function run_simulation(params) {
    var diameter = parseFloat(params["diameter"]);
    var material = params["material"];
    var velocity = parseFloat(params["velocity"]);
    var angle    = parseFloat(params["angle"]);
    var target   = params["target"];
    var depth    = parseFloat(params["depth"] !== undefined ? params["depth"] : 0);
    var obs_dist = parseFloat(params["observer_distance"] !== undefined ? params["observer_distance"] : 0);

    // 1. 初始质量与动能
    var mass0 = compute_mass(diameter, material);
    var e0 = compute_kinetic_energy(mass0, velocity);
    var tnt0_tons = joule_to_tnt_ton(e0);
    var tnt0_kg = joule_to_tnt_kg(e0);
    var fun_refs = compute_fun_references(tnt0_kg);

    // 2. 大气轨迹积分
    var traj = integrate_trajectory(
        diameter, material, velocity, angle,
        0.01, 50
    );

    // 3. 空爆/地撞判定
    var mode_info = determine_mode(traj, diameter, material);
    var release_e = mode_info["release_energy_j"];
    var ground_eff = mode_info["ground_efficiency"];

    // 4. 实际释放能量的 TNT 当量
    var tnt_release_tons = joule_to_tnt_ton(release_e);
    var tnt_release_kg = joule_to_tnt_kg(release_e);

    // 5. 撞击坑
    var crater_info = compute_crater(
        diameter, material, velocity, target, release_e, mode_info["mode"]
    );

    // 6. 冲击波
    var shock = compute_shockwave(release_e, ground_eff);

    // 7. 热辐射
    var ther = compute_thermal(release_e, ground_eff);

    // 8. 海啸
    var tsu = compute_tsunami(release_e, depth, target);

    // 9. 灾害等级
    var disaster = classify_disaster(diameter, tnt_release_tons);

    // 10. 观测点损毁评估
    var obs = observer_damage(obs_dist, shock, ther);

    return {
        "input_echo": {
            "diameter_m": diameter,
            "material": material,
            "velocity_kms": velocity,
            "angle_deg": angle,
            "target": target,
            "ocean_depth_m": target === "海洋" ? depth : null,
            "observer_distance_km": obs_dist,
        },
        "initial": {
            "mass_kg": mass0,
            "mass_tons": mass0 / 1000.0,
            "density_kg_m3": C.MATERIALS[material]["density"],
            "kinetic_energy_j": e0,
            "tnt_tons": tnt0_tons,
            "tnt_mt": tnt0_tons / 1e6,
            "fun_references": fun_refs,
        },
        "trajectory": traj,
        "mode": mode_info,
        "release": {
            "energy_j": release_e,
            "tnt_tons": tnt_release_tons,
            "tnt_mt": tnt_release_tons / 1e6,
            "ground_efficiency": ground_eff,
        },
        "crater": crater_info,
        "shockwave": shock,
        "thermal": ther,
        "tsunami": tsu,
        "disaster_level": disaster,
        "observer_damage": obs,
    };
}
