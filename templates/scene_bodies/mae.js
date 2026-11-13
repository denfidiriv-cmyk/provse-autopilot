  // Маєток за $4 млн: чорне золото, будинок, цінники
  const BG = '#0d0d0f', CARD = '#1a1a1e', INK = '#f5f1e6', MUT = '#a59f90', GOLD = '#d9b45a', RED = '#ff4d5a', GR = '#47d18c';
  const bg = () => P.cached('mae_bg', W, H, (g) => { g.fillStyle = BG; g.fillRect(0, 0, W, H); const r = g.createRadialGradient(540, 650, 50, 540, 650, 760); r.addColorStop(0, 'rgba(217,180,90,.14)'); r.addColorStop(1, 'rgba(217,180,90,0)'); g.fillStyle = r; g.fillRect(0, 0, W, 1400); darkBottom(g, 'rgba(6,6,8,1)'); });
  const frame = tagFrame('mae_frame', 'ГРОШІ · РОЗСЛІДУВАННЯ', GOLD, '#0d0d0f');
  const S = mkS(bg, frame);
  const card = (c, x, y, w, h, edge = 'rgba(217,180,90,.35)') => { c.save(); c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 36; c.shadowOffsetY = 14; c.fillStyle = CARD; c.fill(rr(x, y, w, h, 28)); c.restore(); c.strokeStyle = edge; c.lineWidth = 3; c.stroke(rr(x, y, w, h, 28)); };
  function mansion(c, x, y, s) { if (s <= 0) return; c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = '#e9e1cf'; c.fillRect(-300, -120, 600, 260); c.fillRect(-120, -220, 240, 100); c.fillStyle = '#5a4630'; c.beginPath(); c.moveTo(-330, -120); c.lineTo(0, -320); c.lineTo(330, -120); c.closePath(); c.fill(); c.fillStyle = '#e9e1cf'; for (let i = -2; i <= 2; i++) c.fillRect(i * 110 - 12, -100, 24, 240); c.fillStyle = '#2b3a55'; for (const [a, b] of [[-240, -60], [-240, 40], [200, -60], [200, 40], [-80, -60], [60, -60]]) c.fillRect(a, b, 40, 60); c.fillStyle = '#5a4630'; c.fillRect(-36, 40, 72, 100); c.fillStyle = '#c9c2b0'; c.fillRect(-340, 140, 680, 24); c.restore(); }
  function tag(c, x, y, s, a, b, col) { if (s <= 0) return; c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-0.05); c.fillStyle = col; c.beginPath(); c.moveTo(-200, -90); c.lineTo(160, -90); c.lineTo(220, 0); c.lineTo(160, 90); c.lineTo(-200, 90); c.closePath(); c.fill(); c.fillStyle = BG; c.beginPath(); c.arc(150, 0, 16, 0, 7); c.fill(); txt(c, a, -20, -20, 44, '#0d0d0f', { font: 'Oswald-400' }); txt(c, b, -20, 54, 72, '#0d0d0f'); c.restore(); }
  S('m_hook', (c, lt) => {
    mansion(c, 540, 640, 1.1 * back(at(lt, 0, 0.4)));
    const v = 4000000 * eio(at(lt, L(0, 4) - 0.4, 1.0)); txt(c, '$' + Math.round(v).toLocaleString('uk-UA').replace(/ /g, ' '), 540, 1060, 130, GOLD, { alpha: at(lt, L(0, 3) - 0.4, 0.2) });
    txt(c, 'під Києвом', 540, 1160, 56, MUT, { font: 'Oswald-400', alpha: at(lt, L(0, 2) - 0.3, 0.3) });
  }, lt => ({ z: 1.06 - 0.06 * eo(at(lt, 0, 1)) }));
  S('m_who', (c, lt) => {
    chip(c, 'Слідство.Інфо', 540, 320, at(lt, L(1, 8) - 0.3, 0.3), INK, '#0d0d0f', 52);
    const facts = [[14, '843 м²', 'площа будинку'], [20, 'Іванковичі', 'Київщина']]; facts.forEach(([w, a, b], i) => { const k = back(at(lt, L(1, w) - 0.3, 0.35)); if (k <= 0) return; c.save(); c.translate(i ? 770 : 310, 500); c.scale(k, k); card(c, -200, -100, 400, 200); txt(c, a, 0, 10, 72, GOLD); txt(c, b, 0, 70, 40, MUT, { font: 'Oswald-400' }); c.restore(); });
    const o = eo(at(lt, L(1, 21) - 0.35, 0.45)); if (o > 0) { c.save(); c.globalAlpha = o; c.translate(0, (1 - o) * 60); card(c, 90, 660, 900, 300); txt(c, 'ВЛАСНИК', 540, 730, 44, MUT, { font: 'Oswald-400' }); pirate(c, 230, 840, 150, 96); txt(c, 'Валерій Канюка', 350, 860, 68, INK, { align: 'left' }); c.restore(); }
    if (lt > L(1, 25) - 0.3) { const q = back(at(lt, L(1, 25) - 0.3, 0.35)); c.save(); c.translate(540, 1120); c.scale(q, q); card(c, -380, -90, 760, 180, GOLD); txt(c, '15+ років', 0, -2, 70, GOLD); txt(c, 'керівні посади в структурах Газпрому', 0, 58, 38, INK, { font: 'Oswald-400' }); c.restore(); }
  }, lt => ({ z: 1.0 + lt * 0.005 }));
  S('m_price', (c, lt) => {
    mansion(c, 540, 560, 0.75);
    tag(c, 330, 950, back(at(lt, L(2, 37) - 0.3, 0.35)), 'продаж', '$4 млн', GOLD);
    tag(c, 760, 1130, back(at(lt, L(2, 40) - 0.3, 0.35)), 'оренда / міс', '$7 500', INK);
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('m_after', (c, lt) => {
    c.save(); c.translate(540, 620); card(c, -360, -260, 720, 520); mansion(c, 0, -40, 0.55); txt(c, 'ОРЕНДА · $7 500 / міс', 0, 200, 50, INK); c.restore();
    const x = eo(at(lt, L(3, 55) - 0.35, 0.4)); if (x > 0) { c.save(); c.strokeStyle = RED; c.lineWidth = 22; c.lineCap = 'round'; c.beginPath(); c.moveTo(220, 400); c.lineTo(220 + 640 * x, 400 + 440 * x); c.moveTo(860, 400); c.lineTo(860 - 640 * x, 400 + 440 * x); c.stroke(); c.restore(); }
    chip(c, 'оголошення зняли', 540, 1000, at(lt, L(3, 55) - 0.1, 0.3), RED, '#fff', 60);
    chip(c, 'власник не відповів', 540, 1180, at(lt, L(3, 60) - 0.3, 0.3), INK, '#0d0d0f', 56);
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('m_end', (c, lt) => { mansion(c, 540, 600, 0.9 * back(at(lt, 0, 0.4))); txt(c, 'ВСЕ ПРО ЕКОНОМІКУ', 540, 940, 84, GOLD, { alpha: at(lt, 0.2, 0.3) }); subBtn(c, lt, L(4, 62) - 0.15, '#2a2a30'); }, lt => ({ z: 1.0 + lt * 0.01 }));
