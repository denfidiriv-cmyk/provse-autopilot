  // Відключення світла: темна кімната, жовта лампа, графік черг
  const BG = '#121418', CARD = '#1e2229', INK = '#f4f4f0', MUT = '#9aa1ad', YE = '#ffd43b', RED = '#ff4d4d', GR = '#3ddc84', BL = '#4aa8ff';
  const bg = () => P.cached('svt_bg', W, H, (g) => { g.fillStyle = BG; g.fillRect(0, 0, W, H); darkBottom(g, 'rgba(8,9,12,1)'); });
  const frame = tagFrame('svt_frame', 'СВІТЛО СЬОГОДНІ', YE, '#121418');
  const S = mkS(bg, frame);
  const card = (c, x, y, w, h, edge = 'rgba(255,255,255,.08)') => { c.save(); c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 36; c.shadowOffsetY = 14; c.fillStyle = CARD; c.fill(rr(x, y, w, h, 28)); c.restore(); c.strokeStyle = edge; c.lineWidth = 3; c.stroke(rr(x, y, w, h, 28)); };
  function bulb(c, x, y, s, on) { c.save(); c.translate(x, y); c.scale(s, s); if (on > 0) { const r = c.createRadialGradient(0, -40, 20, 0, -40, 360); r.addColorStop(0, `rgba(255,212,59,${0.45 * on})`); r.addColorStop(1, 'rgba(255,212,59,0)'); c.fillStyle = r; c.beginPath(); c.arc(0, -40, 360, 0, 7); c.fill(); }
    c.fillStyle = on > 0.5 ? YE : '#3a3f48'; c.beginPath(); c.arc(0, -60, 120, Math.PI * 0.8, Math.PI * 2.2); c.lineTo(50, 90); c.lineTo(-50, 90); c.closePath(); c.fill(); c.fillStyle = '#8a9099'; c.fill(rr(-56, 90, 112, 26, 8)); c.fill(rr(-50, 122, 100, 22, 8)); c.fill(rr(-40, 148, 80, 22, 10)); c.restore(); }
  S('s_hook', (c, lt) => {
    const on = lt < 0.4 ? 1 : (Math.sin(lt * 18) > 0 && lt < 1.4 ? 1 : 0); bulb(c, 540, 560, 1.2 * back(at(lt, 0, 0.4)), on);
    const q = back(at(lt, L(0, 6) - 0.3, 0.35)); if (q > 0) { c.save(); c.translate(540, 920); c.scale(q, q); card(c, -330, -80, 660, 160); txt(c, 'ЦІЛУ ДОБУ', 0, 30, 92, YE); c.restore(); }
    if (lt > L(0, 8) - 0.3) { txt(c, '1–3', 540, 1150, 150, INK, { scale: back(at(lt, L(0, 9) - 0.3, 0.35)) }); txt(c, 'черги одночасно', 540, 1240, 54, MUT, { font: 'Oswald-400', alpha: at(lt, L(0, 12) - 0.3, 0.3) }); }
  }, lt => ({ z: 1.04 - 0.04 * eo(at(lt, 0, 1)) + lt * 0.004 }));
  S('s_why', (c, lt) => {
    c.save(); c.translate(540, 700); c.strokeStyle = '#7a8290'; c.lineWidth = 14; c.lineJoin = 'round'; c.beginPath(); c.moveTo(-160, 320); c.lineTo(-40, -280); c.lineTo(40, -280); c.lineTo(160, 320); c.moveTo(-200, -180); c.lineTo(200, -180); c.moveTo(-150, -60); c.lineTo(150, -60); c.moveTo(-110, 80); c.lineTo(110, 80); c.moveTo(-120, -60); c.lineTo(110, 80); c.moveTo(120, -60); c.lineTo(-110, 80); c.stroke();
    const hit = at(lt, L(1, 17) - 0.3, 0.2); if (hit > 0) { c.fillStyle = RED; c.globalAlpha = 0.8 * (1 - at(lt, L(1, 17), 1.5)) + 0.2; c.beginPath(); for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2, r = i % 2 ? 60 : 150; i ? c.lineTo(Math.cos(a) * r, -180 + Math.sin(a) * r) : c.moveTo(Math.cos(a) * r, -180 + Math.sin(a) * r); } c.closePath(); c.fill(); } c.restore();
    if (lt > L(1, 18) - 0.3) { const k = back(at(lt, L(1, 18) - 0.3, 0.3)); pirate(c, 540, 1130, 200 * k, 130 * k); }
    txt(c, 'АТАКИ НА ЕНЕРГЕТИКУ', 540, 340, 70, RED, { alpha: at(lt, L(1, 17) - 0.2, 0.3) });
  }, lt => ({ z: 1.0 + lt * 0.012 }));
  S('s_change', (c, lt) => {
    txt(c, 'ГРАФІКИ ЗМІНЮЮТЬСЯ', 540, 330, 76, YE, { scale: back(at(lt, 0, 0.35)) });
    card(c, 90, 400, 900, 560); const rows = 4, cols = 12; const sh = Math.floor(lt * 3);
    for (let r = 0; r < rows; r++) { txt(c, `черга ${r + 1}`, 130, 490 + r * 120, 34, MUT, { align: 'left', font: 'Oswald-400' }); for (let k = 0; k < cols; k++) { const off = ((k * 7 + r * 3 + (lt > L(2, 24) - 0.3 ? sh : 0)) % 5) < 2; c.fillStyle = off ? '#3a3f48' : YE; c.fill(rr(290 + k * 56, 455 + r * 120, 46, 60, 8)); } }
    if (lt > L(2, 26) - 0.3) { const q = back(at(lt, L(2, 26) - 0.3, 0.35)); c.save(); c.translate(540, 1100); c.scale(q, q); card(c, -380, -90, 760, 180, RED); txt(c, 'кілька разів на годину', 0, 22, 66, INK); c.restore(); }
    if (lt > L(2, 31) - 0.3) txt(c, 'перевіряйте частіше', 540, 1260, 56, YE, { alpha: at(lt, L(2, 31) - 0.3, 0.3) });
  }, lt => ({ z: 1.0 + lt * 0.006 }));
  S('s_where', (c, lt) => {
    c.save(); c.translate(540, 720); const q = back(at(lt, 0, 0.4)); c.scale(q, q); c.fillStyle = '#0a0c10'; c.fill(rr(-220, -400, 440, 800, 60)); c.strokeStyle = '#3a3f48'; c.lineWidth = 10; c.stroke(rr(-220, -400, 440, 800, 60)); c.fillStyle = CARD; c.fill(rr(-190, -360, 380, 720, 40));
    [[42, 'обленерго', -140], [44, 'ДТЕК', 20]].forEach(([w, s, y]) => { const k = back(at(lt, L(3, w) - 0.3, 0.3)); if (k <= 0) return; c.save(); c.translate(0, y); c.scale(k, k); c.fillStyle = YE; c.fill(rr(-160, -60, 320, 120, 24)); txt(c, s, 0, 22, 60, '#121418'); c.restore(); });
    c.restore(); txt(c, 'АКТУАЛЬНІ ГРАФІКИ', 540, 300, 70, INK, { alpha: at(lt, 0, 0.3) });
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('s_prep', (c, lt) => {
    const ch = eio(at(lt, L(4, 48) - 0.3, 1.2)); c.save(); c.translate(330, 680); c.fillStyle = '#2c313a'; c.fill(rr(-120, -220, 240, 440, 36)); c.fillStyle = '#0a0c10'; c.fill(rr(-90, -180, 180, 360, 20)); c.fillStyle = ch > .99 ? GR : YE; c.fill(rr(-80, 170 - 340 * ch, 160, 340 * ch, 14)); txt(c, `${Math.round(100 * ch)}%`, 0, 20, 64, INK); c.restore(); txt(c, 'павербанк', 330, 960, 48, MUT, { font: 'Oswald-400' });
    const fl = at(lt, L(4, 50) - 0.3, 0.3); c.save(); c.translate(760, 600); c.rotate(-0.4); c.fillStyle = '#5a606b'; c.fill(rr(-40, 0, 80, 220, 20)); c.fillStyle = '#7a8290'; c.beginPath(); c.moveTo(-60, 0); c.lineTo(60, 0); c.lineTo(40, -60); c.lineTo(-40, -60); c.fill(); if (fl > 0) { c.fillStyle = `rgba(255,212,59,${0.35 * fl})`; c.beginPath(); c.moveTo(-40, -60); c.lineTo(-180, -420); c.lineTo(180, -420); c.lineTo(40, -60); c.fill(); } c.restore(); txt(c, 'ліхтарик', 760, 960, 48, MUT, { font: 'Oswald-400' });
    txt(c, 'ЗАРЯДІТЬ ЗАРАЗ', 540, 1150, 90, YE, { scale: back(at(lt, L(4, 47) - 0.3, 0.35)) });
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('s_end', (c, lt) => { bulb(c, 540, 600, 1.0 * back(at(lt, 0, 0.4)), 1); txt(c, 'БУДЬТЕ В КУРСІ', 540, 960, 84, YE, { alpha: at(lt, 0.2, 0.3) }); subBtn(c, lt, L(5, 51) - 0.15, '#3a3f48'); }, lt => ({ z: 1.0 + lt * 0.01 }));
