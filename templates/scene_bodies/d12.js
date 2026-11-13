  // Народний календар: полотно, вишивка, відривний календар
  const RED = '#c8102e', INK = '#2b1d16', MUT = '#7a6656', PAPER = '#f6efe2', CARD = '#fffaf1', BLUE = '#3a7bd5', GR = '#2e9e5b', YE = '#f5b301';
  const bg = () => P.cached('d12_bg', W, H, (g) => { g.fillStyle = PAPER; g.fillRect(0, 0, W, H);
    for (const y0 of [200, 1240]) { for (let x = 0; x < W; x += 60) { g.fillStyle = RED; g.save(); g.translate(x + 30, y0); g.rotate(Math.PI / 4); g.fillRect(-14, -14, 28, 28); g.restore(); g.fillStyle = INK; g.save(); g.translate(x + 30, y0); g.rotate(Math.PI / 4); g.fillRect(-6, -6, 12, 12); g.restore(); } }
    g.fillStyle = 'rgba(43,29,22,1)'; darkBottom(g, 'rgba(43,29,22,1)'); });
  const frame = tagFrame('d12_frame', 'НАРОДНИЙ КАЛЕНДАР', RED, '#fff');
  const S = mkS(bg, frame);
  const card = (c, x, y, w, h) => { c.save(); c.shadowColor = 'rgba(60,30,20,.25)'; c.shadowBlur = 30; c.shadowOffsetY = 12; c.fillStyle = CARD; c.fill(rr(x, y, w, h, 26)); c.restore(); };
  function tit(c, x, y, s, t) { c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = '#5b7f3a'; c.beginPath(); c.ellipse(-20, 10, 90, 60, -0.2, 0, 7); c.fill(); c.fillStyle = YE; c.beginPath(); c.ellipse(-10, 30, 62, 46, -0.2, 0, 7); c.fill(); c.fillStyle = '#1b2433'; c.beginPath(); c.arc(60, -40, 46, 0, 7); c.fill(); c.fillStyle = '#fff'; c.beginPath(); c.ellipse(66, -32, 24, 18, 0, 0, 7); c.fill(); c.fillStyle = '#1b2433'; c.fillRect(-14, 0, 14, 78); c.fillStyle = '#111'; c.beginPath(); c.arc(80, -50, 6, 0, 7); c.fill(); c.fillStyle = '#333'; c.beginPath(); c.moveTo(104, -42); c.lineTo(124, -36); c.lineTo(104, -30); c.fill(); c.fillStyle = '#3d5a2a'; c.beginPath(); c.moveTo(-100, 0); c.lineTo(-170, -10 + 6 * Math.sin(t * 6)); c.lineTo(-100, 30); c.fill(); c.strokeStyle = '#5a4a3a'; c.lineWidth = 6; c.beginPath(); c.moveTo(-10, 70); c.lineTo(-20, 100); c.moveTo(20, 70); c.lineTo(20, 100); c.stroke(); c.restore(); }
  function flake(c, x, y, s, rot, col = BLUE) { c.save(); c.translate(x, y); c.scale(s, s); c.rotate(rot); c.strokeStyle = col; c.lineWidth = 10; c.lineCap = 'round'; for (let i = 0; i < 6; i++) { c.rotate(Math.PI / 3); c.beginPath(); c.moveTo(0, 0); c.lineTo(0, -60); c.moveTo(0, -36); c.lineTo(-16, -50); c.moveTo(0, -36); c.lineTo(16, -50); c.stroke(); } c.restore(); }
  function sun(c, x, y, s, t) { c.save(); c.translate(x, y); c.scale(s, s); c.rotate(t * .4); c.strokeStyle = YE; c.lineWidth = 12; c.lineCap = 'round'; for (let i = 0; i < 8; i++) { c.rotate(Math.PI / 4); c.beginPath(); c.moveTo(62, 0); c.lineTo(88, 0); c.stroke(); } c.fillStyle = YE; c.beginPath(); c.arc(0, 0, 48, 0, 7); c.fill(); c.restore(); }
  function flower(c, x, y, s) { if (s <= 0) return; c.save(); c.translate(x, y); c.scale(s, s); c.strokeStyle = GR; c.lineWidth = 10; c.beginPath(); c.moveTo(0, 0); c.lineTo(0, 140); c.stroke(); for (let i = 0; i < 6; i++) { c.save(); c.rotate(i * Math.PI / 3); c.fillStyle = '#ff7aa8'; c.beginPath(); c.ellipse(0, -40, 20, 36, 0, 0, 7); c.fill(); c.restore(); } c.fillStyle = YE; c.beginPath(); c.arc(0, 0, 22, 0, 7); c.fill(); c.restore(); }

  S('n_hook', (c, lt) => {
    const q = back(at(lt, 0, 0.4)); c.save(); c.translate(540, 700); c.scale(q, q); c.rotate(-0.03); card(c, -280, -330, 560, 620); c.fillStyle = RED; c.fill(rr(-280, -330, 560, 150, [26, 26, 0, 0])); txt(c, 'ЛИСТОПАД', 0, -235, 70, '#fff'); txt(c, '12', 0, 150, 330, INK); c.restore();
    for (let i = 0; i < 6; i++) { c.fillStyle = '#9a8a7a'; c.beginPath(); c.arc(330 + i * 84, 380, 12, 0, 7); c.fill(); }
    chip(c, 'що каже народ?', 540, 1120, at(lt, L(0, 2) - 0.2, 0.3), INK, '#fff', 56);
  }, lt => ({ z: 1.05 - 0.05 * eo(at(lt, 0, 1)) }));
  S('n_bird', (c, lt, t) => {
    card(c, 160, 300, 760, 620); c.save(); c.beginPath(); c.roundRect(200, 340, 680, 540, 14); c.clip(); const g = c.createLinearGradient(0, 340, 0, 880); g.addColorStop(0, '#9ec7ef'); g.addColorStop(1, '#dfeefb'); c.fillStyle = g; c.fillRect(200, 340, 680, 540); c.restore();
    c.strokeStyle = '#fff'; c.lineWidth = 22; c.strokeRect(200, 340, 680, 540); c.beginPath(); c.moveTo(540, 340); c.lineTo(540, 880); c.stroke(); c.fillStyle = '#e8ddd0'; c.fillRect(150, 880, 780, 40);
    const fl = eo(at(lt, L(1, 8) - 0.4, 0.8)); tit(c, 1200 - 660 * fl, 520 + 300 * fl - 120 * Math.sin(fl * Math.PI), 1.0, t);
    const sn = at(lt, L(1, 13) - 0.3, 0.4); if (sn > 0) for (let i = 0; i < 6; i++) flake(c, 230 + i * 120, 1010 + 20 * Math.sin(lt * 2 + i), 0.55 * back(sn), lt + i, BLUE);
    if (lt > L(1, 13) - 0.3) txt(c, 'СНІГ АБО МОРОЗ', 540, 1180, 84, BLUE, { scale: back(at(lt, L(1, 13) - 0.1, 0.3)) });
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('n_frost', (c, lt, t) => {
    card(c, 110, 330, 380, 520); card(c, 590, 330, 380, 520);
    flake(c, 300, 520, 1.4 * back(at(lt, 0, 0.4)), lt * .5, BLUE); txt(c, 'морозний ранок', 300, 760, 44, MUT, { font: 'Oswald-400', alpha: at(lt, 0.2, 0.3) });
    const q = at(lt, L(2, 19) - 0.3, 0.3); sun(c, 780, 470, 0.9 * back(q), t); flower(c, 780, 600, 0.9 * back(at(lt, L(2, 21) - 0.3, 0.3)));
    txt(c, '→', 540, 620, 110, RED, { alpha: q });
    if (lt > L(2, 21) - 0.3) txt(c, 'РАННЯ ТЕПЛА ВЕСНА', 540, 1100, 84, GR, { scale: back(at(lt, L(2, 21) - 0.2, 0.35)) });
  }, lt => ({ z: 1.0 + lt * 0.012 }));
  S('n_thaw', (c, lt, t) => {
    c.save(); c.translate(540, 560); c.scale(back(at(lt, 0, 0.4)), back(at(lt, 0, 0.4))); c.fillStyle = '#8d9ab3'; for (const [a, b, r] of [[-110, 10, 80], [-20, -40, 110], [90, 0, 90], [0, 40, 90]]) { c.beginPath(); c.arc(a, b, r, 0, 7); c.fill(); }
    c.strokeStyle = BLUE; c.lineWidth = 10; c.lineCap = 'round'; for (let i = 0; i < 6; i++) { const o = ((lt * 2 + i * .2) % 1) * 120; c.beginPath(); c.moveTo(-130 + i * 52, 120 + o); c.lineTo(-140 + i * 52, 150 + o); c.stroke(); } c.restore();
    const th = eio(at(lt, L(3, 30) - 0.3, 0.8)); c.save(); c.translate(860, 820); c.fillStyle = '#fff'; c.fill(rr(-26, -200, 52, 230, 26)); c.beginPath(); c.arc(0, 50, 46, 0, 7); c.fill(); c.fillStyle = RED; c.beginPath(); c.arc(0, 50, 34, 0, 7); c.fill(); c.fillRect(-13, 30 - (40 + 130 * th), 26, 40 + 130 * th); c.restore();
    if (lt > L(3, 30) - 0.3) txt(c, 'ШВИДКА ВІДЛИГА', 540, 1120, 92, RED, { scale: back(at(lt, L(3, 31) - 0.3, 0.35)) });
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('n_names', (c, lt) => {
    txt(c, 'ІМЕНИНИ', 540, 340, 110, RED, { scale: back(at(lt, 0, 0.35)) });
    const N = [[34, 'Олександр'], [35, 'Олена'], [36, 'Максим'], [37, 'Анастасія'], [38, 'Артем'], [40, 'Степан']];
    N.forEach(([w, n], i) => { const k = at(lt, L(4, w) - 0.25, 0.3); if (k <= 0) return; const x = i % 2 ? 760 : 320, y = 520 + Math.floor(i / 2) * 170; c.save(); c.translate(x, y); c.scale(back(k), back(k)); card(c, -200, -62, 400, 124); txt(c, n, 0, 22, 62, INK); c.restore(); });
    if (lt > L(4, 41) - 0.2) chip(c, 'привітайте своїх!', 540, 1120, at(lt, L(4, 41) - 0.2, 0.3), RED, '#fff', 60);
  }, lt => ({ z: 1.0 + lt * 0.008 }));
  S('n_end', (c, lt, t) => { tit(c, 540, 620, 1.3 * back(at(lt, 0, 0.4)), t); txt(c, 'ЦІКАВЕ ЩОДНЯ', 540, 900, 84, RED, { alpha: at(lt, 0.2, 0.3) }); subBtn(c, lt, L(5, 43) - 0.15, '#5a4a40'); }, lt => ({ z: 1.0 + lt * 0.01 }));
