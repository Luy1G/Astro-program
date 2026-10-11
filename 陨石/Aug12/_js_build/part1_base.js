const MATERIALS = {
    "冰彗星":   {"density": 1000.0, "strength": 1.0e6,  "desc": "质地松散，极易在大气中解体"},
    "岩石陨石": {"density": 3000.0, "strength": 5.0e6,  "desc": "普通球粒陨石，常见近地小行星"},
    "铁陨石":   {"density": 7800.0, "strength": 2.0e8,  "desc": "金属小行星碎片，穿透性极强"},
};

const JOULES_PER_TNT_TON = 4.184e9;
const JOULES_PER_TNT_KG = 4.184e6;
const TNT_TON_PER_JOULE = 1.0 / JOULES_PER_TNT_TON;
const TNT_KG_PER_JOULE = 1.0 / JOULES_PER_TNT_KG;

const FUN_REFERENCES = {
    "标准军用手榴弹": 0.05,
    "普通航空炸弹":   500.0,
    "广岛原子弹":     1.5e7,
};

const RHO_AIR_SEA = 1.225;
const SCALE_HEIGHT = 8500.0;
const ATM_COLUMN_MASS = 1.0e4;
const ATMOSPHERE_TOP = 200000.0;

const DRAG_COEFFICIENT = 1.0;
const HEAT_TRANSFER_COEFF = 0.1;
const ABLATION_HEAT = 5.0e6;
const PANCAKE_FACTOR = 5.0;

const TARGET_DENSITY = {
    "陆地": 2700.0,
    "海洋": 1025.0,
};

const OVERPRESSURE_SCALED_DIST = {
    "core":     2.0,
    "secondary": 3.0,
    "outer":    8.0,
};

const FIREBALL_COEFF = 0.0023;
const THIRD_DEGREE_BURN_FLUENCE = 4.184e5;


function radius_from_diameter(diameter_m) {
    return diameter_m / 2.0;
}

function cross_section_area(diameter_m) {
    const r = radius_from_diameter(diameter_m);
    return Math.PI * r * r;
}

function compute_mass(diameter_m, material_key) {
    const r = radius_from_diameter(diameter_m);
    const rho = MATERIALS[material_key]["density"];
    return (4.0 / 3.0) * Math.PI * Math.pow(r, 3) * rho;
}

function compute_radius_from_mass(mass_kg, density) {
    if (mass_kg <= 0 || density <= 0) {
        return 0.0;
    }
    return Math.pow((3.0 * mass_kg) / (4.0 * Math.PI * density), 1.0 / 3.0);
}

function compute_kinetic_energy(mass_kg, velocity_kms) {
    const v_ms = velocity_kms * 1000.0;
    return 0.5 * mass_kg * v_ms * v_ms;
}

function joule_to_tnt_ton(energy_j) {
    return energy_j * TNT_TON_PER_JOULE;
}

function joule_to_tnt_kg(energy_j) {
    return energy_j * TNT_KG_PER_JOULE;
}

function compute_fun_references(tnt_kg) {
    const result = {};
    for (const [name, kg] of Object.entries(FUN_REFERENCES)) {
        result[name] = tnt_kg / kg;
    }
    return result;
}

function air_density(altitude_m) {
    if (altitude_m < 0) {
        altitude_m = 0.0;
    }
    return RHO_AIR_SEA * Math.exp(-altitude_m / SCALE_HEIGHT);
}

function air_density_with_gradient(altitude_m) {
    if (altitude_m < 0) {
        altitude_m = 0.0;
    }
    if (altitude_m < 25000) {
        return RHO_AIR_SEA * Math.exp(-altitude_m / 8500.0);
    }
    const rho_25 = RHO_AIR_SEA * Math.exp(-25000 / 8500.0);
    return rho_25 * Math.exp(-(altitude_m - 25000) / 6000.0);
}
