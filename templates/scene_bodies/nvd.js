  // Nvidia без Хуанга: темний техно-фон, зелені схеми, графік акцій
  const BG = '#07100a', CARD = '#0f1d12', INK = '#f1f6ef', MUT = '#9fb3a2', GRN = '#7ed321', RED = '#ff4d4d', YE = '#ffd34d';
  const bg = () => P.cached('nvd_bg', W, H, (g) => { g.fillStyle = BG; g.fillRect(0, 0, W, H); g.strokeStyle = 'rgba(126,211,33,.08)'; g.lineWidth = 3; for (let i = 0; i < 26; i++) { let x = (i * 137) % W, y = (i * 211) % 1300; g.beginPath(); g.moveTo(x, y); for (let k = 0; k < 4; k++) { if (k % 2) y += 80 + (i * 13 % 60); else x += (i % 2 ? 1 : -1) * (90 + i * 7 % 80); g.lineTo(x, y); } g.stroke(); g.fillStyle = 'rgba(126,211,33,.15)'; g.beginPath(); g.arc(x, y, 6, 0, 7); g.fill(); } darkBottom(g, 'rgba(4,8,5,1)'); });
  const frame = () => P.cached('nvd_noframe', W, H, () => {});
  const S = mkS(bg, frame);
  const card = (c, x, y, w, h, edge = 'rgba(126,211,33,.35)') => { c.save(); c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 36; c.shadowOffsetY = 14; c.fillStyle = CARD; c.fill(rr(x, y, w, h, 28)); c.restore(); c.strokeStyle = edge; c.lineWidth = 3; c.stroke(rr(x, y, w, h, 28)); };
  function chair(c, x, y, s, rot = 0) { c.save(); c.translate(x, y); c.scale(s, s); c.rotate(rot); c.fillStyle = '#26332a'; c.fill(rr(-120, -260, 240, 260, 40)); c.fill(rr(-150, 0, 300, 70, 30)); c.fillStyle = '#3a4a3e'; c.fillRect(-12, 70, 24, 110); for (const a of [-1, -.4, .4, 1]) { c.save(); c.translate(0, 180); c.rotate(a * .9); c.fillRect(-8, 0, 16, 90); c.beginPath(); c.arc(0, 95, 14, 0, 7); c.fill(); c.restore(); } c.restore(); }
  function gpu(c2, x, y, s) { const c = c2; c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = '#1a2a1d'; c.fill(rr(-110, -110, 220, 220, 20)); c.strokeStyle = GRN; c.lineWidth = 6; c.stroke(rr(-110, -110, 220, 220, 20)); c.fillStyle = GRN; for (let i = -3; i <= 3; i++) { c.fillRect(i * 28 - 5, -140, 10, 30); c.fillRect(i * 28 - 5, 110, 10, 30); c.fillRect(-140, i * 28 - 5, 30, 10); c.fillRect(110, i * 28 - 5, 30, 10); } c.fillStyle = 'rgba(126,211,33,.25)'; c.fill(rr(-60, -60, 120, 120, 12)); c.restore(); }

  // Стилізований портрет: сиве коротке волосся, окуляри, чорна шкіряна куртка (лише код)
  function portrait(c, x, y, s, gray = 0) { c.save(); c.translate(x, y); c.scale(s, s);
    c.save(); c.beginPath(); c.arc(0, 0, 260, 0, 7); c.clip(); const g = c.createLinearGradient(0, -260, 0, 260); g.addColorStop(0, '#1d3a22'); g.addColorStop(1, '#0c1a0f'); c.fillStyle = g; c.fillRect(-260, -260, 520, 520);
    // куртка
    c.fillStyle = '#121212'; c.beginPath(); c.moveTo(-250, 260); c.quadraticCurveTo(-240, 110, -120, 80); c.lineTo(120, 80); c.quadraticCurveTo(240, 110, 250, 260); c.closePath(); c.fill();
    c.fillStyle = '#2a2a2a'; c.beginPath(); c.moveTo(-120, 80); c.lineTo(-40, 90); c.lineTo(-70, 200); c.closePath(); c.fill(); c.beginPath(); c.moveTo(120, 80); c.lineTo(40, 90); c.lineTo(70, 200); c.closePath(); c.fill();
    c.strokeStyle = 'rgba(255,255,255,.18)'; c.lineWidth = 4; c.beginPath(); c.moveTo(-150, 120); c.quadraticCurveTo(-170, 190, -165, 260); c.stroke();
    // футболка під курткою
    c.fillStyle = '#1b1b1b'; c.beginPath(); c.moveTo(-40, 90); c.lineTo(40, 90); c.lineTo(60, 260); c.lineTo(-60, 260); c.closePath(); c.fill();
    // шия і обличчя
    c.fillStyle = '#d9a982'; c.fill(rr(-36, 30, 72, 70, 20));
    c.beginPath(); c.ellipse(0, -40, 92, 112, 0, 0, 7); c.fill();
    c.fillStyle = '#c99773'; c.beginPath(); c.ellipse(-92, -36, 16, 26, 0, 0, 7); c.fill(); c.beginPath(); c.ellipse(92, -36, 16, 26, 0, 0, 7); c.fill();
    // сиве волосся
    c.fillStyle = '#d8d8d8'; c.beginPath(); c.moveTo(-96, -60); c.quadraticCurveTo(-104, -150, -30, -160); c.quadraticCurveTo(40, -172, 92, -130); c.quadraticCurveTo(108, -100, 96, -60); c.quadraticCurveTo(70, -120, 0, -122); c.quadraticCurveTo(-70, -124, -96, -60); c.fill();
    c.fillStyle = '#bdbdbd'; c.beginPath(); c.moveTo(-96, -60); c.quadraticCurveTo(-100, -95, -84, -112); c.lineTo(-82, -50); c.fill(); c.beginPath(); c.moveTo(96, -60); c.quadraticCurveTo(100, -95, 84, -112); c.lineTo(82, -50); c.fill();
    // окуляри
    c.strokeStyle = '#1a1a1a'; c.lineWidth = 7; c.beginPath(); c.roundRect(-74, -58, 60, 40, 12); c.stroke(); c.beginPath(); c.roundRect(14, -58, 60, 40, 12); c.stroke(); c.beginPath(); c.moveTo(-14, -42); c.lineTo(14, -42); c.stroke();
    c.fillStyle = '#2a2a2a'; c.beginPath(); c.arc(-44, -38, 6, 0, 7); c.fill(); c.beginPath(); c.arc(44, -38, 6, 0, 7); c.fill();
    // брови, ніс, усмішка
    c.strokeStyle = '#8a8a8a'; c.lineWidth = 7; c.lineCap = 'round'; c.beginPath(); c.moveTo(-70, -72); c.lineTo(-24, -76); c.moveTo(24, -76); c.lineTo(70, -72); c.stroke();
    c.strokeStyle = '#b8846a'; c.lineWidth = 5; c.beginPath(); c.moveTo(0, -20); c.lineTo(-8, 10); c.lineTo(6, 12); c.stroke();
    c.strokeStyle = '#7a4a3a'; c.lineWidth = 6; c.beginPath(); c.arc(0, 18, 34, 0.25 * Math.PI, 0.75 * Math.PI); c.stroke();
    c.restore();
    if (gray > 0) { c.save(); c.globalAlpha = gray; c.fillStyle = 'rgba(7,16,10,.55)'; c.beginPath(); c.arc(0, 0, 260, 0, 7); c.fill(); c.restore(); }
    c.strokeStyle = GRN; c.lineWidth = 8; c.beginPath(); c.arc(0, 0, 262, 0, 7); c.stroke(); c.restore(); }
  const pill = (c, s, x, y, k, col, fg, size) => { if (k <= 0) return; c.save(); c.translate(x, y); c.scale(back(k), back(k)); c.font = `${size}px "Oswald-700"`; const w = c.measureText(s).width + 60; c.fillStyle = col; c.fill(rr(-w / 2, -size * 0.85, w, size * 1.5, size * 0.75)); txt(c, s, 0, size * 0.32, size, fg); c.restore(); };
  // ХУК: з першого кадру графік обвалюється і вилітає −10%
  S('m_hook', (c, lt) => {
    const kick = Math.max(0, 1 - lt / 0.35) * Math.sin(lt * 90) * 18; c.save(); c.translate(kick, -kick * 0.6);
    const fl = Math.max(0, 1 - lt / 0.25); if (fl > 0) { c.fillStyle = `rgba(255,77,77,${0.35 * fl})`; c.fillRect(0, 0, W, H); }
    txt(c, 'NVIDIA', 540, 250, 90, GRN, { font: 'JBMono-700' });
    card(c, 90, 330, 900, 560, 'rgba(255,77,77,.45)');
    c.save(); c.beginPath(); c.rect(90, 330, 900, 560); c.clip(); c.lineJoin = 'round'; c.lineCap = 'round';
    const pts = [0.42, 0.47, 0.45, 0.52, 0.5, 0.56, 0.55]; const X = i => 150 + i * 80, Y = v => 880 - v * 820;
    c.lineWidth = 10; c.strokeStyle = GRN; c.beginPath(); pts.forEach((v, i) => i ? c.lineTo(X(i), Y(v)) : c.moveTo(X(i), Y(v))); c.stroke();
    const d = eio(clamp(lt / 0.9)); const x0 = X(6), y0 = Y(0.55), x1 = x0 + 300 * d, y1 = y0 + 420 * d;
    c.strokeStyle = RED; c.lineWidth = 14; c.beginPath(); c.moveTo(x0, y0); c.lineTo(x0 + 70 * d, y0 + 160 * d); c.lineTo(x0 + 120 * d, y0 + 120 * d); c.lineTo(x1, y1); c.stroke();
    c.fillStyle = RED; c.beginPath(); c.arc(x1, y1, 16 + 6 * Math.sin(lt * 10), 0, 7); c.fill(); c.restore();
    const big = back(at(lt, 0.05, 0.3)); txt(c, '−10%', 540, 1110, 260, RED, { scale: big * (1 + 0.03 * Math.sin(lt * 6)) });
    if (lt > L(0, 3) - 0.25) pill(c, 'ще до відкриття біржі', 540, 1235, at(lt, L(0, 3) - 0.25, 0.3), INK, '#07100a', 56);
    c.restore();
  }, lt => ({ z: 1.06 - 0.06 * eo(clamp(lt / 0.5)) + lt * 0.012 }));
  S('n_hook', (c, lt) => {
    const out = eio(at(lt, L(1, 15) - 0.2, 0.6)); portrait(c, 540, 640, 1.0 * back(at(lt, 0, 0.4)), out);
    const q = back(at(lt, 0.1, 0.35)); c.save(); c.translate(540, 1000); c.scale(q, q); card(c, -330, -90, 660, 180); txt(c, 'CEO NVIDIA', 0, -18, 46, MUT, { font: 'Oswald-400' }); txt(c, 'Дженсен Хуанг', 0, 56, 70, INK); c.restore();
    if (lt > L(1, 14) - 0.2) { const p = eo(at(lt, L(1, 14) - 0.2, 0.35)); c.save(); c.strokeStyle = RED; c.lineWidth = 12; c.lineCap = 'round'; c.beginPath(); c.moveTo(290, 1056); c.lineTo(290 + 500 * p, 1056); c.stroke(); c.restore(); }
    txt(c, 'БІЛЬШЕ НЕ КЕРУЄ', 540, 300, 96, GRN, { scale: back(at(lt, L(1, 13) - 0.3, 0.35)) });
  }, lt => ({ z: 1.0 + lt * 0.015 }));
  S('n_out', (c, lt) => {
    txt(c, 'ЗАСНОВНИК · з 1993', 540, 260, 72, INK, { scale: back(at(lt, 0, 0.35)) });
    portrait(c, 540, 600, 0.9, 1);
    const s = back(at(lt, L(2, 21) - 0.3, 0.35)); if (s > 0) { c.save(); c.translate(540, 560); c.rotate(-0.1); c.scale(s, s); c.strokeStyle = RED; c.lineWidth = 14; c.strokeRect(-330, -90, 660, 180); txt(c, 'ВІДСТАВКА', 0, 40, 120, RED); c.restore(); }
    pill(c, 'скандал', 320, 1040, at(lt, L(2, 24) - 0.25, 0.3), YE, '#07100a', 54); pill(c, 'внутрішнє розслідування', 640, 1160, at(lt, L(2, 26) - 0.3, 0.3), INK, '#07100a', 50);
  }, lt => ({ z: 1.0 + lt * 0.015 }));
  S('n_interim', (c, lt) => {
    txt(c, 'ТИМЧАСОВО', 540, 300, 96, GRN, { scale: back(at(lt, 0, 0.35)) });
    const q = eo(at(lt, L(3, 33) - 0.4, 0.45)); if (q > 0) { c.save(); c.globalAlpha = q; c.translate(0, (1 - q) * 60); card(c, 110, 420, 860, 320); txt(c, 'Колетт Кресс', 540, 560, 96, INK); txt(c, 'фінансова директорка → тимчасова CEO', 540, 660, 44, MUT, { font: 'Oswald-400' }); c.restore(); }
    const m = at(lt, L(3, 36) - 0.3, 0.3); if (m > 0) { c.save(); c.globalAlpha = m; card(c, 110, 820, 860, 280, 'rgba(255,211,77,.4)'); c.translate(250, 960); c.rotate(Math.sin(lt * 3) * .15); c.strokeStyle = YE; c.lineWidth = 14; c.beginPath(); c.arc(0, -10, 50, 0, 7); c.stroke(); c.lineCap = 'round'; c.beginPath(); c.moveTo(36, 26); c.lineTo(80, 70); c.stroke(); c.restore(); c.save(); c.globalAlpha = m; txt(c, 'рада директорів', 360, 940, 52, INK, { align: 'left' }); txt(c, 'шукає нового CEO', 360, 1010, 52, YE, { align: 'left' }); c.restore(); }
  }, lt => ({ z: 1.0 + lt * 0.012 }));
  S('n_end', (c, lt) => { gpu(c, 540, 560, 0.9 * back(at(lt, 0, 0.4))); txt(c, 'ВСЕ ПРО ЕКОНОМІКУ', 540, 900, 84, GRN, { alpha: at(lt, 0.2, 0.3) }); subBtn(c, lt, L(4, 41) - 0.15, '#22302a'); }, lt => ({ z: 1.0 + lt * 0.01 }));
