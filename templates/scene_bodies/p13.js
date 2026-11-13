  // Штормове попередження на п'ятницю 13: карта України з підсвіченими областями
  const INK = '#f2f5fb', MUT = '#a7b3c9', CARD = 'rgba(20,28,45,.85)', YE = '#ffcc33', RED = '#ff5a5f', SNOW = '#e8f3ff', BL = '#6fb2ff', WARM = '#ffb347';
  const MX = 50, MY = 390;
  const WEST = ['Івано-Франківська область', 'Закарпатська область'];
  const WARMR = ['Одеська область', 'Миколаївська область', 'Херсонська область', 'Запорізька область', 'Автономна Республіка Крим', 'Черкаська область', 'Кіровоградська область', 'Вінницька область', 'Полтавська область', 'Дніпропетровська область', 'місто Севастополь'];
  const reg = n => UA.find(o => o.n === n);
  const path = o => { const p = new Path2D(); for (const r of o.r) { r.forEach(([x, y], i) => i ? p.lineTo(MX + x, MY + y) : p.moveTo(MX + x, MY + y)); p.closePath(); } return p; };
  const PATHS = {}; UA.forEach(o => PATHS[o.n] = path(o));
  const ALL = new Path2D(); UA.forEach(o => ALL.addPath(PATHS[o.n]));
  const bg = () => P.cached('p13_bg2', W, H, (g) => { const gr = g.createLinearGradient(0, 0, 0, H); gr.addColorStop(0, '#26314a'); gr.addColorStop(0.55, '#161d2e'); gr.addColorStop(1, '#0b0f1a'); g.fillStyle = gr; g.fillRect(0, 0, W, H); darkBottom(g, 'rgba(8,11,19,1)'); });
  const frame = () => P.cached('p13_noframe', W, H, () => {});
  const S0 = mkS(bg, frame);
  // карта: fill(name)->колір або null
  let Z = [1, 0, 0, 0, 0];
  const zIn = (k) => { const a = reg(WEST[0]).c, b = reg(WEST[1]).c; const fx = MX + (a[0] + b[0]) / 2, fy = MY + (a[1] + b[1]) / 2; Z = [1 + 2.2 * k, fx, fy, fx + (540 - fx) * k, fy + (720 - fy) * k]; };
  const zOff = () => { Z = [1, 0, 0, 0, 0]; };
  const applyZ = c => { if (Z[0] !== 1) { c.translate(Z[3], Z[4]); c.scale(Z[0], Z[0]); c.translate(-Z[1], -Z[2]); } };
  function map(c, fill, a = 1) { c.save(); applyZ(c); c.globalAlpha = a; c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 30; c.fillStyle = '#2f3b57'; c.fill(ALL); c.shadowBlur = 0; for (const o of UA) { const col = fill ? fill(o.n) : null; if (col) { c.fillStyle = col; c.fill(PATHS[o.n]); } } c.strokeStyle = 'rgba(255,255,255,.35)'; c.lineWidth = 1.6; for (const o of UA) c.stroke(PATHS[o.n]); c.restore(); }
  function clipRegions(c, names, fn) { c.save(); applyZ(c); const p = new Path2D(); names.forEach(n => p.addPath(PATHS[n])); c.clip(p); fn(); c.restore(); }
  const cen = n => { const o = reg(n); let x = MX + o.c[0], y = MY + o.c[1]; if (Z[0] !== 1) { x = (x - Z[1]) * Z[0] + Z[3]; y = (y - Z[2]) * Z[0] + Z[4]; } return [x, y]; };
  const bolt = (c, x, y, s, a = 1) => { if (a <= 0) return; c.save(); c.globalAlpha = a; c.translate(x, y); c.scale(s, s); c.fillStyle = YE; c.beginPath(); c.moveTo(20, -120); c.lineTo(-50, 20); c.lineTo(0, 20); c.lineTo(-30, 130); c.lineTo(60, -20); c.lineTo(10, -20); c.lineTo(50, -120); c.closePath(); c.fill(); c.restore(); };
  const warn = (c, x, y, s) => { if (s <= 0) return; c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = YE; c.beginPath(); c.moveTo(0, -80); c.lineTo(92, 70); c.lineTo(-92, 70); c.closePath(); c.fill(); c.fillStyle = '#141a28'; c.fill(rr(-9, -36, 18, 64, 6)); c.beginPath(); c.arc(0, 48, 11, 0, 7); c.fill(); c.restore(); };
  const label = (c, s, x, y, k, bgc = INK, fg = '#141a28', size = 40) => chip(c, s, x, y, k, bgc, fg, size);
  const S = (id, fn, cam) => S0(id, fn, cam);
  S('w_hook', (c, lt) => {
    zOff();
    const fl = lt > 0.5 && lt < 0.7 ? 0.45 : (lt > 1.6 && lt < 1.75 ? 0.35 : 0);
    map(c, null, at(lt, 0, 0.5)); if (fl) { c.fillStyle = `rgba(255,255,255,${fl})`; c.fillRect(0, 0, W, 1340); }
    txt(c, "П'ЯТНИЦЯ, 13", 540, 260, 110, INK, { scale: back(at(lt, 0, 0.35)) }); bolt(c, 900, 230, 0.7, at(lt, 0.5, 0.1));
    txt(c, 'І ПОГОДА НЕ ЖАРТУЄ', 540, 1150, 78, YE, { scale: back(at(lt, L(0, 3) - 0.3, 0.35)) });
  }, lt => ({ z: 1.04 - 0.04 * eo(at(lt, 0, 1)), x: lt < 0.7 && lt > 0.5 ? 6 * Math.sin(lt * 90) : 0 }));
  S('w_warn', (c, lt) => {
    zOff();
    const p = at(lt, L(1, 11) - 0.3, 0.5); map(c, n => WEST.includes(n) ? `rgba(255,204,51,${0.85 * p})` : null);
    const [x, y] = cen('Івано-Франківська область'); warn(c, x - 10, y - 120, back(at(lt, L(1, 11) - 0.2, 0.35)));
    txt(c, 'ШТОРМОВЕ ПОПЕРЕДЖЕННЯ', 540, 260, 78, YE, { scale: back(at(lt, L(1, 11) - 0.3, 0.35)) });
    label(c, 'завтра, 13 листопада', 540, 1150, at(lt, L(1, 8) - 0.2, 0.3), INK, '#141a28', 52);
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('w_west', (c, lt, t) => {
    zIn(eio(at(lt, 0, 1.0)));
    const sn = eo(at(lt, L(2, 20) - 0.4, 1.0));
    map(c, n => WEST.includes(n) ? (sn > 0.5 ? '#cfe3ff' : '#4f7fc4') : null);
    clipRegions(c, WEST, () => { for (let i = 0; i < 80; i++) { const x = 40 + (i * 37) % 330, y = 700 + ((i * 53 + t * (sn > .5 ? 60 : 300)) % 300); if (sn > .5) { c.fillStyle = '#fff'; c.beginPath(); c.arc(x, y, 3 + i % 3, 0, 7); c.fill(); } else { c.strokeStyle = 'rgba(200,225,255,.9)'; c.lineWidth = 2.5; c.beginPath(); c.moveTo(x, y); c.lineTo(x - 5, y + 16); c.stroke(); } } });
    const [ax, ay] = cen('Івано-Франківська область'), [bx, by] = cen('Закарпатська область');
    label(c, 'Прикарпаття', ax + 40, ay - 130, at(lt, L(2, 14) - 0.2, 0.3), INK, '#141a28', 40); label(c, 'Закарпаття', bx - 10, by + 120, at(lt, L(2, 16) - 0.2, 0.3), INK, '#141a28', 40);
    txt(c, 'ДОЩ, ПОТІМ СНІГ', 540, 260, 92, SNOW, { scale: back(at(lt, L(2, 20) - 0.3, 0.35)) });
    [[24, 'мокрий сніг', BL], [28, 'ожеледиця', RED]].forEach(([w, s2, col], i) => label(c, s2, i ? 760 : 320, 1150, at(lt, L(2, w) - 0.25, 0.3), col, '#fff', 50));
  }, lt => ({ z: 1.0 }));
  S('w_wind', (c, lt, t) => {
    zIn(1);
    map(c, n => WEST.includes(n) ? '#4f7fc4' : null);
    c.save(); c.strokeStyle = 'rgba(220,235,255,.55)'; c.lineWidth = 6; c.lineCap = 'round'; for (let i = 0; i < 8; i++) { const y = 420 + i * 80, o = ((lt * (1.2 + (i % 3) * .4) + i * .17) % 1) * 1400 - 300; c.beginPath(); c.moveTo(o, y); c.lineTo(o + 220, y); c.quadraticCurveTo(o + 290, y - 10, o + 280, y - 46); c.stroke(); } c.restore();
    const [ax, ay] = cen('Івано-Франківська область'), [bx, by] = cen('Закарпатська область');
    const v1 = 20 * eio(at(lt, L(3, 32) - 0.5, 0.7)), v2 = 30 * eio(at(lt, L(3, 38) - 0.4, 1.0));
    if (lt > L(3, 31) - 0.6) label(c, `${Math.round(v1)} м/с`, ax + 60, ay - 120, at(lt, L(3, 31) - 0.6, 0.3), YE, '#141a28', 52);
    if (lt > L(3, 38) - 0.1) label(c, `${Math.max(5, Math.round(v2))} м/с`, bx, by + 120, at(lt, L(3, 38) - 0.1, 0.3), RED, '#fff', 52);
    txt(c, 'ПОРИВИ ВІТРУ', 540, 260, 92, INK, { scale: back(at(lt, 0, 0.35)) });
    label(c, 'хуртовини в Карпатах', 540, 1150, at(lt, L(3, 43) - 0.3, 0.3), SNOW, '#141a28', 54);
  }, lt => ({ z: 1.0, x: 3 * Math.sin(lt * 7) }));
  S('w_south', (c, lt, t) => {
    zOff();
    const p = at(lt, L(4, 45) - 0.3, 0.6); map(c, n => WARMR.includes(n) ? `rgba(255,170,60,${0.9 * p})` : null);
    const f = at(lt, L(4, 55) - 0.3, 0.6); if (f > 0) clipRegions(c, WARMR, () => { for (let i = 0; i < 6; i++) { c.fillStyle = `rgba(235,240,250,${0.28 * f})`; c.fill(rr(((lt * 50 + i * 260) % 1400) - 300, 650 + i * 60, 600, 46, 23)); } });
    const [x, y] = cen('Кіровоградська область'); label(c, 'до +20°', x + 20, y, at(lt, L(4, 52) - 0.3, 0.3), WARM, '#141a28', 70);
    txt(c, 'ПІВДЕНЬ І ЦЕНТР', 540, 260, 92, WARM, { scale: back(at(lt, L(4, 46) - 0.3, 0.35)) });
    label(c, 'зранку тумани', 540, 1150, f, MUT, '#141a28', 52);
  }, lt => ({ z: 1.0 + lt * 0.008 }));
  S('w_end', (c, lt) => {
    zOff();
    map(c, n => WEST.includes(n) ? '#cfe3ff' : WARMR.includes(n) ? 'rgba(255,170,60,.8)' : null);
    txt(c, 'БЕРЕЖІТЬ СЕБЕ', 540, 260, 92, YE, { alpha: at(lt, 0.1, 0.3) }); subBtn(c, lt, L(5, 59) - 0.15, '#34405f');
  }, lt => ({ z: 1.0 + lt * 0.01 }));
