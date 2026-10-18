# -*- coding: utf-8 -*-
"""
构建 v3.0 独立 HTML（陆地陨石撞击模拟器）
  1. 读取 part1+part2+part3 JS 源码（从 Aug12/_js_build）
  2. 从 part1/part3 删除所有海洋相关代码
  3. 读取 impact_templates_v1.json 内联
  4. 加入模板匹配/插槽填充 JS（删除 tsunami_h 插槽、ocean_extra）
  5. 读取 final/v3.0/templates/index.html 骨架
  6. 替换 fetch 调成本地函数调用
  7. 输出到 陨石/JAVA版html.html（覆盖）
"""
import os, json, re

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, "Aug12", "_js_build")
HTML_IN = os.path.join(ROOT, "final", "v3.0", "templates", "index.html")
TPL_JSON = os.path.join(ROOT, "Aug12", "impact_templates_v1.json")
OUT = os.path.join(ROOT, "JAVA版html.html")

# ---------- 1. 读取 3 段 JS ----------
with open(os.path.join(BUILD, "part1_base.js"), encoding="utf-8") as f:
    js1 = f.read()
with open(os.path.join(BUILD, "part2_trajectory.js"), encoding="utf-8") as f:
    js2 = f.read()
with open(os.path.join(BUILD, "part3_disaster.js"), encoding="utf-8") as f:
    js3 = f.read()

# ---------- 2. 删除海洋相关 JS ----------
# part1: TARGET_DENSITY 移除 "海洋" 条目
js1 = js1.replace(
    'const TARGET_DENSITY = {\n    "陆地": 2700.0,\n    "海洋": 1025.0,\n};',
    'const TARGET_DENSITY = {\n    "陆地": 2700.0,\n};'
)
# 防御性：若格式略不同，用更宽松的删除
js1 = js1.replace('    "海洋": 1025.0,\n', '')

# part3: 注释中去掉 tsunami
js3 = js3.replace(
    '// 翻译对应：breakup / crater / shockwave / thermal / tsunami / classify + simulation',
    '// 翻译对应：breakup / crater / shockwave / thermal / classify + simulation（v3.0 已移除 tsunami）'
)

# part3: 删除 compute_crater 中的海洋分支
js3 = js3.replace(
    '''    if (target === "海洋") {
        return {"crater_diameter_km": 0.0, "note": "海洋撞击不形成硬质坑体，转为海啸模型"};
    }
''',
    ''
)

# part3: 删除整个 compute_tsunami 函数（正则一次性删除：从 tsunami 注释行到 classify 注释行之前）
js3 = re.sub(
    r'// -+ tsunami: compute_tsunami -+\n.*?(?=// -+ classify:)',
    '',
    js3,
    flags=re.S
)

# part3: run_simulation 中删除海啸调用与字段
js3 = js3.replace(
    '    // 8. 海啸\n    var tsu = compute_tsunami(release_e, depth, target);\n\n',
    ''
)
js3 = js3.replace(
    '        "tsunami": tsu,\n',
    ''
)
# input_echo 中删除 ocean_depth_m
js3 = js3.replace(
    '            "ocean_depth_m": target === "海洋" ? depth : null,\n',
    ''
)
# 强制 target = "陆地"（忽略前端传入）
js3 = js3.replace(
    '    var target   = params["target"];\n',
    '    var target   = "陆地";  // v3.0：强制陆地，忽略传入\n'
)

# part1 需要把常量包成 C 对象（供 part2/part3 通过 C.xxx 引用）
CONST_C_WRAP = r"""
// ---- Constants Namespace (for part2/part3) ----
const C = {
  MATERIALS: MATERIALS,
  FUN_REFERENCES: FUN_REFERENCES,
  JOULES_PER_TNT_TON: JOULES_PER_TNT_TON,
  JOULES_PER_TNT_KG: JOULES_PER_TNT_KG,
  TNT_TON_PER_JOULE: TNT_TON_PER_JOULE,
  TNT_KG_PER_JOULE: TNT_KG_PER_JOULE,
  RHO_AIR_SEA: RHO_AIR_SEA,
  SCALE_HEIGHT: SCALE_HEIGHT,
  ATM_COLUMN_MASS: ATM_COLUMN_MASS,
  ATMOSPHERE_TOP: ATMOSPHERE_TOP,
  DRAG_COEFFICIENT: DRAG_COEFFICIENT,
  HEAT_TRANSFER_COEFF: HEAT_TRANSFER_COEFF,
  ABLATION_HEAT: ABLATION_HEAT,
  PANCAKE_FACTOR: PANCAKE_FACTOR,
  TARGET_DENSITY: TARGET_DENSITY,
  OVERPRESSURE_SCALED_DIST: OVERPRESSURE_SCALED_DIST,
  FIREBALL_COEFF: FIREBALL_COEFF,
  THIRD_DEGREE_BURN_FLUENCE: THIRD_DEGREE_BURN_FLUENCE,
};
"""

# ---------- 3. 读取模板库（v3.0 仅保留陆地模板）----------
with open(TPL_JSON, encoding="utf-8") as f:
    tpl_data_full = json.load(f)
tpl_data = [t for t in tpl_data_full if t.get("target") != "ocean"]
tpl_json_str = json.dumps(tpl_data, ensure_ascii=False)
print(f"[OK] 模板总数 {len(tpl_data_full)}，v3.0 陆地模板 {len(tpl_data)}（已过滤海洋）")

# ---------- 4. 模板匹配 / 填充逻辑（v3.0 删除海洋）----------
TEMPLATE_LOGIC = r"""
// ============================================================
// Template Matching & Slot Filling (v3.0 陆地版 — 移除海洋)
// ============================================================
const IMPACT_TEMPLATES = __TEMPLATE_JSON_PLACEHOLDER__;

const LEVEL_BOUNDS = [
  ["L1", 0.0,   1e6],
  ["L2", 1e6,   1e9],
  ["L3", 1e9,   1e12],
  ["L4", 1e12,  1e15],
  ["L5", 1e15,  9e18],
];
const MATERIAL_CN2EN = {"冰彗星":"ice","ice":"ice","岩石陨石":"rock","rock":"rock","铁陨石":"iron","iron":"iron"};
// v3.0：target 固定 land
const TARGET_CN2EN   = {"陆地":"land","land":"land"};

function classify_level(final_tnt_tons) {
  for (let i=0;i<LEVEL_BOUNDS.length;i++) {
    const [lv, lo, hi] = LEVEL_BOUNDS[i];
    if (final_tnt_tons >= lo && final_tnt_tons < hi) return lv;
  }
  return "L5";
}
function classify_impact_type(mode_str) {
  if (mode_str.indexOf("地表撞击") !== -1 || mode_str.indexOf("地撞") !== -1) return "surface";
  return "airburst";
}
function classify_angle_group(angle_deg, level) {
  if (level === "L1" || level === "L5") return null;
  if (angle_deg < 30) return "G1";
  if (angle_deg < 60) return "G2";
  return "G3";
}
function match_template(level, impact_type, material, target, angle_group) {
  for (let i=0;i<IMPACT_TEMPLATES.length;i++) {
    const t = IMPACT_TEMPLATES[i];
    if (t["level"] === level && t["impact_type"] === impact_type && t["material"] === material
        && t["target"] === target && t["angle_group"] === angle_group) return t;
  }
  return null;
}
function lookup_template_by_result(result) {
  const echo = result["input_echo"] || {};
  const mode_info = result["mode"] || {};
  const release = result["release"] || {};
  const material = MATERIAL_CN2EN[echo["material"]] || "rock";
  const target   = "land";  // v3.0 固定
  const angle    = parseFloat(echo["angle_deg"]) || 45;
  const final_tnt = parseFloat(release["tnt_tons"]) || 0;
  const impact_type = classify_impact_type(mode_info["mode"] || "");
  const level = classify_level(final_tnt);
  const ag = classify_angle_group(angle, level);
  return match_template(level, impact_type, material, target, ag);
}
function _fmt_num(val, digits) {
  digits = digits == null ? 2 : digits;
  if (val == null) return "N/A";
  const v = Number(val);
  if (isNaN(v)) return String(val);
  if (v === 0) return "0";
  if (Math.abs(v) >= 1e12) return v.toExponential(2);
  if (Math.abs(v) >= 1e6)  return Math.round(v).toLocaleString("en-US");
  if (Math.abs(v) >= 1)    return v.toFixed(digits).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return v.toFixed(digits+2);
}
function _fmt_tnt(tons) {
  const t = Number(tons) || 0;
  if (t >= 1e9) return (t/1e9).toFixed(2)+" 十亿吨";
  if (t >= 1e6) return (t/1e6).toFixed(2)+" 百万吨";
  if (t >= 1e3) return (t/1e3).toFixed(2)+" 千吨";
  return t.toFixed(2)+" 吨";
}
// v3.0：删除 tsunami_h 插槽
const SLOT_KEYS = ["diameter","velocity","angle","final_tnt","remain_mass_ratio",
                   "breakup_altitude","fireball_r","blast_core_r","blast_outer_r",
                   "burn_r","crater_r"];
function build_slot_values(result) {
  const echo    = result["input_echo"] || {};
  const traj    = result["trajectory"] || {};
  const mode_m  = result["mode"] || {};
  const release = result["release"] || {};
  const thermal = result["thermal"] || {};
  const shock   = result["shockwave"] || {};
  const crater  = result["crater"] || {};

  let breakup_alt = mode_m["breakup_altitude_km"];
  if (breakup_alt == null) {
    const brk = traj["breakup"] || {};
    breakup_alt = brk["altitude_km"] || 0;
  }
  const ablation_ratio = mode_m["ablation_ratio"] != null ? mode_m["ablation_ratio"] : (traj["ablation_ratio"] || 0);
  const remain_ratio = Math.max(1.0 - ablation_ratio, 0.0);
  const crater_d = parseFloat(crater["crater_diameter_km"]) || 0;
  const crater_r = crater_d > 0 ? crater_d / 2.0 : 0.0;

  return {
    "diameter":          _fmt_num(echo["diameter_m"] || 0),
    "velocity":          _fmt_num(echo["velocity_kms"] || 0),
    "angle":             _fmt_num(echo["angle_deg"] || 0, 1),
    "final_tnt":         _fmt_tnt(release["tnt_tons"] || 0),
    "remain_mass_ratio": (remain_ratio*100).toFixed(1)+"%",
    "breakup_altitude":  _fmt_num(breakup_alt, 2),
    "fireball_r":        _fmt_num(thermal["fireball_radius_km"] || 0),
    "blast_core_r":      _fmt_num(shock["core_radius_km"] || 0),
    "blast_outer_r":     _fmt_num(shock["outer_radius_km"] || 0),
    "burn_r":            _fmt_num(thermal["burn_radius_km"] || 0),
    "crater_r":          _fmt_num(crater_r),
  };
}
function fill_template(template, result) {
  const slots = build_slot_values(result);
  const out = {};
  for (const k in template) out[k] = template[k];
  // v3.0：陆地版仅处理陆地相关文本字段
  const textFields = ["main_text","angle_desc","airburst_only","surface_only",
                      "land_extra","visual_cue","warning_note"];
  for (let i=0;i<textFields.length;i++) {
    const f = textFields[i];
    if (typeof out[f] === "string") {
      let s = out[f];
      for (let k in slots) s = s.split("{{"+k+"}}").join(String(slots[k]));
      out[f] = s;
    }
  }
  return out;
}
function _build_energy_comparison(physics_init) {
  const fun = physics_init["fun_references"] || {};
  const tnt = physics_init["tnt_tons"] || 0;
  const parts = ["初始TNT当量约 " + _fmt_tnt(tnt)];
  for (const name in fun) {
    const val = fun[name];
    if (val && val > 0) parts.push("≈ " + _fmt_num(val, 1) + " 颗" + name);
  }
  return parts.join("，");
}
// 对外接口：返回 {content}
function generate_narrative_local(result) {
  const tmpl = lookup_template_by_result(result);
  if (!tmpl) return {content: "模板库中未找到匹配的模板。"};
  const filled = fill_template(tmpl, result);
  const parts = [filled["main_text"]];
  if (filled["airburst_only"]) parts.push(filled["airburst_only"]);
  if (filled["surface_only"])  parts.push(filled["surface_only"]);
  if (filled["land_extra"])    parts.push(filled["land_extra"]);
  const init = result["initial"] || {};
  parts.push("📊 " + _build_energy_comparison(init));
  parts.push("🎬 " + filled["visual_cue"]);
  return {content: parts.join("\n\n")};
}
"""
TEMPLATE_LOGIC = TEMPLATE_LOGIC.replace("__TEMPLATE_JSON_PLACEHOLDER__", tpl_json_str)

# ---------- 5. 读取 HTML ----------
with open(HTML_IN, encoding="utf-8") as f:
    html = f.read()

# 标题副标题改为"独立HTML版"
html = html.replace(
    '<title>陆地陨石撞击模拟器 v3.0</title>',
    '<title>陆地陨石撞击模拟器 v3.0 ｜ JS独立版</title>'
)
html = html.replace(
    '陆地陨石撞击模拟器 <span>v3.0</span>',
    '陆地陨石撞击模拟器 <span>v3.0</span> ｜ <span class="ver">JS独立版</span>'
)

# 替换 runSim 中的 fetch(/api/simulate) → 本地调用
old_runsim = """function runSim(){
  const body={material:document.getElementById('material').value,
    diameter:parseFloat(document.getElementById('diameter').value),
    velocity:parseFloat(document.getElementById('velocity').value),
    angle:parseFloat(document.getElementById('angle').value),
    target:'陆地',
    depth:0,
    observer_distance:parseFloat(document.getElementById('observer_distance').value)};
  document.getElementById('animStatus').textContent='计算中…';
  fetch('/api/simulate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
    .then(r=>r.json()).then(d=>{LAST_RESULT=d;renderResults(d);setupAnimation(d);playAnim();document.getElementById("aiFeatureArea").style.display="block";})
    .catch(e=>{document.getElementById('animStatus').textContent='错误: '+e.message;});
}"""
new_runsim = """function runSim(){
  const body={material:document.getElementById('material').value,
    diameter:parseFloat(document.getElementById('diameter').value),
    velocity:parseFloat(document.getElementById('velocity').value),
    angle:parseFloat(document.getElementById('angle').value),
    target:'陆地',
    depth:0,
    observer_distance:parseFloat(document.getElementById('observer_distance').value)};
  document.getElementById('animStatus').textContent='计算中…';
  try {
    setTimeout(function(){
      const d = run_simulation(body);
      LAST_RESULT = d;
      renderResults(d);
      setupAnimation(d);
      playAnim();
      document.getElementById("aiFeatureArea").style.display="block";
      document.getElementById('animStatus').textContent='就绪';
    }, 30);
  } catch(e){
    document.getElementById('animStatus').textContent='错误: '+e.message;
  }
}"""
assert old_runsim in html, "runSim 原文未找到，HTML 结构可能已变"
html = html.replace(old_runsim, new_runsim)

# 替换 narrativeBtn 的 fetch 调用
old_narr = """document.getElementById('narrativeBtn').addEventListener('click', () => {
  if (!LAST_RESULT) return;
  const btn = document.getElementById('narrativeBtn');
  btn.disabled = true;
  aiLoading('narrativeOutput');
  fetch('/api/ai/narrative', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ params: getInputParams(), result: LAST_RESULT })
  }).then(r => r.json()).then(d => {
    setTimeout(() => {
      if (d.error) aiError('narrativeOutput', d.error);
      else aiShow('narrativeOutput', d.content);
    }, 300);
  }).catch(e => aiError('narrativeOutput', e.message))
    .finally(() => btn.disabled = false);
});"""
new_narr = """document.getElementById('narrativeBtn').addEventListener('click', () => {
  if (!LAST_RESULT) return;
  const btn = document.getElementById('narrativeBtn');
  btn.disabled = true;
  aiLoading('narrativeOutput');
  try {
    const d = generate_narrative_local(LAST_RESULT);
    setTimeout(function(){
      if (d.error) aiError('narrativeOutput', d.error);
      else aiShow('narrativeOutput', d.content);
      btn.disabled = false;
    }, 400);
  } catch(e) {
    aiError('narrativeOutput', e.message);
    btn.disabled = false;
  }
});"""
assert old_narr in html, "narrativeBtn 原文未找到"
html = html.replace(old_narr, new_narr)

# ---------- 6. 合成 physics + template 脚本块，插入到现有 <script> 之前 ----------
first_script = html.find("<script>")
if first_script == -1:
    raise SystemExit("HTML 中找不到 <script> 标签")

pre_script = """<!-- ============================================================
     陆地陨石撞击模拟器 v3.0 — 物理仿真 + 模板匹配引擎（内联 JS，独立运行无需后端）
     ============================================================ -->
<script>
""" + js1 + "\n\n" + CONST_C_WRAP + "\n\n" + js2 + "\n\n" + js3 + "\n\n" + TEMPLATE_LOGIC + """
</script>
"""

html = html[:first_script] + pre_script + html[first_script:]

# ---------- 7. 输出 ----------
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(OUT) / 1024
print(f"[OK] 已生成: {OUT}")
print(f"[OK] 文件大小: {size_kb:.1f} KB ({os.path.getsize(OUT)} bytes)")
print(f"[OK] 模板数: {len(tpl_data)}")

# 验证：检查不应再出现的字符串
with open(OUT, encoding="utf-8") as f:
    out = f.read()
forbidden = ["compute_tsunami", "tsunami_height_m", "海啸", "海洋", "ocean_depth_m", '"ocean"', "ocean_extra"]
print("\n[校验] 禁止字符串检查：")
all_ok = True
for s in forbidden:
    n = out.count(s)
    ok = n == 0
    all_ok = all_ok and ok
    print(f"  {'✅' if ok else '❌'} '{s}' 出现 {n} 次")

print(f"\n{'✅ 全部通过' if all_ok else '❌ 存在残留'}")
