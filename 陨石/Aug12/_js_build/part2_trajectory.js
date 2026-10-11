const G0 = 9.81;
const R_EARTH = 6371000.0;
const ABLATION_SPEED_CUTOFF = 3000.0;

function _gravity_at_altitude(h) {
    return G0 * Math.pow(R_EARTH / (R_EARTH + h), 2);
}

function integrate_trajectory(diameter_m, material_key, velocity_kms,
                              entry_angle_deg, dt = 0.01, sample_every = 20) {
    const m0 = compute_mass(diameter_m, material_key);
    const rho_body = C.MATERIALS[material_key]["density"];
    const strength = C.MATERIALS[material_key]["strength"];

    let m = m0;
    let v = velocity_kms * 1000.0;
    let h = C.ATMOSPHERE_TOP;

    let theta = entry_angle_deg * Math.PI / 180.0;

    let v_x = v * Math.cos(theta);
    let v_y = v * Math.sin(theta);

    let t = 0.0;
    const samples = [];
    let energy_atm = 0.0;
    const energy_profile = [];
    let e_peak_dt_rate = 0.0;
    let e_peak_h = 0.0;

    let breakup_triggered = false;
    let breakup_alt = 0.0;
    let breakup_t = 0.0;
    let breakup_e = 0.0;
    let pancake_mult = 1.0;

    let step = 0;
    while (h > 0 && m > m0 * 0.001) {
        const rho_a = air_density_with_gradient(h);
        const g = _gravity_at_altitude(h);

        const r = compute_radius_from_mass(m, rho_body);
        const A = Math.PI * r * r * pancake_mult;
        const q = 0.5 * rho_a * v * v;

        const e_deposited = 0.5 * rho_a * Math.pow(v, 3) * C.DRAG_COEFFICIENT * A * dt;
        energy_atm += e_deposited;

        if (e_deposited / dt > e_peak_dt_rate) {
            e_peak_dt_rate = e_deposited / dt;
            e_peak_h = h;
        }

        if ((!breakup_triggered) && (q >= strength)) {
            breakup_triggered = true;
            breakup_alt = h;
            breakup_t = t;
            breakup_e = energy_atm;
            pancake_mult = C.PANCAKE_FACTOR;
        }

        const a_drag = (rho_a * v * v * C.DRAG_COEFFICIENT * A) / (2.0 * m);
        let dv_x, dv_y;
        if (v > 0) {
            dv_x = -a_drag * (v_x / v) * dt;
            dv_y = (-a_drag * (v_y / v) + g) * dt;
        } else {
            dv_x = 0.0;
            dv_y = g * dt;
        }
        v_x += dv_x;
        v_y += dv_y;

        v = Math.sqrt(v_x * v_x + v_y * v_y);
        v = Math.max(v, 0.0);

        let sin_theta;
        if (v > 0) {
            theta = Math.atan2(v_y, v_x);
            sin_theta = v_y / v;
        } else {
            sin_theta = 1.0;
        }

        let dm;
        if (v > ABLATION_SPEED_CUTOFF) {
            dm = -(rho_a * Math.pow(v, 3) * C.HEAT_TRANSFER_COEFF * A /
                   C.ABLATION_HEAT) * dt;
        } else {
            dm = 0.0;
        }

        const dh = -v_y * dt;

        m += dm;
        h += dh;
        t += dt;
        step += 1;

        if (v <= 0) {
            break;
        }

        if (step % sample_every === 0) {
            samples.push({
                "t": t,
                "h_km": h / 1000.0,
                "v_kms": v / 1000.0,
                "m_kg": m,
                "q_Pa": q,
                "e_atm_j": energy_atm,
            });
            energy_profile.push([h / 1000.0, energy_atm]);
        }
    }

    const terminal_v = Math.max(v, 0.0);
    const terminal_m = Math.max(m, 0.0);
    const terminal_e_kin = 0.5 * terminal_m * terminal_v * terminal_v;

    const initial_e_kin = 0.5 * m0 * Math.pow(velocity_kms * 1000.0, 2);

    if (h <= 0 && terminal_m > m0 * 0.001) {
        if (samples.length > 0) {
            const s = samples[samples.length - 1];
            const h_last = s["h_km"] * 1000.0;
            let t_ground, v_ground, m_ground;
            if (h_last > 0 && t > s["t"] && (h_last - h) > 0) {
                const frac = h_last / (h_last - h);
                t_ground = s["t"] + (t - s["t"]) * frac;
                const v_s_last = s["v_kms"] * 1000.0;
                v_ground = v_s_last + (v - v_s_last) * frac;
                const m_s_last = s["m_kg"];
                m_ground = Math.max(m_s_last + (terminal_m - m_s_last) * frac, 0.0);
            } else {
                t_ground = t;
                v_ground = terminal_v;
                m_ground = terminal_m;
            }
            samples.push({
                "t": t_ground,
                "h_km": 0.0,
                "v_kms": v_ground / 1000.0,
                "m_kg": m_ground,
                "q_Pa": 0.0,
                "e_atm_j": energy_atm,
            });
            energy_profile.push([0.0, energy_atm]);
        } else {
            samples.push({
                "t": t,
                "h_km": 0.0,
                "v_kms": terminal_v / 1000.0,
                "m_kg": terminal_m,
                "q_Pa": 0.0,
                "e_atm_j": energy_atm,
            });
            energy_profile.push([0.0, energy_atm]);
        }
    }

    const atm_ratio = initial_e_kin > 0 ? energy_atm / initial_e_kin : 0.0;
    const ground_ratio = initial_e_kin > 0 ? terminal_e_kin / initial_e_kin : 0.0;

    return {
        "samples": samples,
        "terminal": {
            "h_km": Math.max(h, 0.0) / 1000.0,
            "v_kms": terminal_v / 1000.0,
            "m_kg": terminal_m,
            "e_kinetic_j": terminal_e_kin,
            "impact_happened": h <= 0 && terminal_m > m0 * 0.001,
        },
        "breakup": {
            "triggered": breakup_triggered,
            "altitude_km": breakup_alt / 1000.0,
            "time_s": breakup_t,
            "energy_before_breakup_j": breakup_e,
        },
        "ablation_kg": m0 - terminal_m,
        "ablation_ratio": m0 > 0 ? (m0 - terminal_m) / m0 : 0.0,
        "energy_atm_j": energy_atm,
        "energy_atm_ratio": atm_ratio,
        "energy_peak_h_km": e_peak_h / 1000.0,
        "energy_profile": energy_profile,
        "initial": {
            "mass_kg": m0,
            "velocity_kms": velocity_kms,
            "kinetic_energy_j": initial_e_kin,
        },
        "energy_distribution": {
            "initial_kinetic_j": initial_e_kin,
            "atmospheric_j": energy_atm,
            "ground_impact_j": terminal_e_kin,
            "atmospheric_ratio": atm_ratio,
            "ground_impact_ratio": ground_ratio,
        },
    };
}
