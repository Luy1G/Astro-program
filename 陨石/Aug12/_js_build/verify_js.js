// 验证 standalone JS 物理计算与 Python 后端一致性
// 从生成的 HTML 中提取前3个 script 块（物理模块），拼接成本文件
// 用法：node verify_js.js

const fs = require('fs');
const path = require('path');
const HTML_PATH = path.join(__dirname, '..', '..', 'JAVA版html.html');
const VERIFY_PATH = path.join(__dirname, '_verify.js');
const html = fs.readFileSync(HTML_PATH, 'utf8');
const scripts = [];
let idx = 0;
while (true) {
  const s = html.indexOf('<script>', idx);
  if (s === -1) break;
  const e = html.indexOf('</script>', s);
  if (e === -1) break;
  scripts.push(html.slice(s + 8, e).trim());
  idx = e + 9;
}
console.log('找到 script 数量:', scripts.length);

// 前三个 script 应该是：part1+part2+part3+template (第一个就是我们的大物理引擎)
const physicsJS = scripts[0];
console.log('第0个 script 长度:', physicsJS.length);

// 执行物理代码 + 测试
const test_code = `
${physicsJS}

// 测试1：60m岩石 27km/s 45度 陆地（通古斯场景）
const r1 = run_simulation({
  diameter: 60, material: '岩石陨石', velocity: 27,
  angle: 45, target: '陆地', depth: 0, observer_distance: 100
});
console.log('--- 测试1: 通古斯式 ---');
console.log('mode:', r1.mode.mode);
console.log('release_tnt_tons:', r1.release.tnt_tons);
console.log('ablation_ratio:', r1.trajectory.ablation_ratio);
console.log('core_radius_km:', r1.shockwave.core_radius_km);
console.log('crater_diameter_km:', r1.crater.crater_diameter_km);
console.log('disaster_level:', r1.disaster_level.level);

// 测试2：200m岩石 25km/s 45度 陆地
const r2 = run_simulation({
  diameter: 200, material: '岩石陨石', velocity: 25,
  angle: 45, target: '陆地', depth: 0, observer_distance: 50
});
console.log('--- 测试2: 200m 陆地 ---');
console.log('mode:', r2.mode.mode);
console.log('initial_mass_tons:', r2.initial.mass_tons);
console.log('release_tnt_tons:', r2.release.tnt_tons);
console.log('fireball_radius_km:', r2.thermal.fireball_radius_km);
console.log('burn_radius_km:', r2.thermal.burn_radius_km);
console.log('core_radius_km:', r2.shockwave.core_radius_km);
console.log('outer_radius_km:', r2.shockwave.outer_radius_km);
console.log('crater_diameter_km:', r2.crater.crater_diameter_km);
console.log('disaster_level:', r2.disaster_level.level);

// 测试3：模板匹配 + 填充
const narr = generate_narrative_local(r2);
console.log('--- 测试3: narrative 长度 ---');
console.log('narrative content length:', narr.content.length);
console.log('has {{slots left?}}:', /\\{\\{\\w+\\}\\}/.test(narr.content));
console.log('前150字:', narr.content.slice(0, 150));

// 测试4：海洋 + 冰彗星
const r4 = run_simulation({
  diameter: 300, material: '冰彗星', velocity: 35,
  angle: 15, target: '海洋', depth: 4000, observer_distance: 500
});
console.log('--- 测试4: 冰彗星浅角度海洋 ---');
console.log('mode:', r4.mode.mode);
console.log('tsunami_height_m:', r4.tsunami.tsunami_height_m);
console.log('crater_diameter_km:', r4.crater.crater_diameter_km);
console.log('ablation_ratio:', r4.trajectory.ablation_ratio);
const narr4 = generate_narrative_local(r4);
console.log('narrative len:', narr4.content.length);
`;

fs.writeFileSync(VERIFY_PATH, test_code);
console.log('_verify.js 已写入');

// 用 node 执行
const { execSync } = require('child_process');
try {
  const out = execSync(`node "${VERIFY_PATH}"`, { encoding: 'utf8', stderr: 'inherit' });
  console.log(out);
} catch (e) {
  console.error('Node 执行出错:', e.message);
  console.error('stderr:', e.stdout || '');
  process.exit(1);
}
