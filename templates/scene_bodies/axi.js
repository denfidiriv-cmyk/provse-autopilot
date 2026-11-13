  // Axios: що США хочуть від Путіна. Новинний синьо-золотий стиль, документ, прапори
  const BG = '#0b1630', CARD = '#13224a', INK = '#f3f5fb', MUT = '#9fb0d6', GOLD = '#f2c14e', RED = '#e8394a', GR = '#39d98a';
  const bg = () => P.cached('axi_bg', W, H, (g) => { g.fillStyle = BG; g.fillRect(0, 0, W, H); g.strokeStyle = 'rgba(159,176,214,.08)'; g.lineWidth = 2; for (let x = 0; x < W; x += 72) { g.beginPath(); g.moveTo(x, 0); g.lineTo(x, 1340); g.stroke(); } for (let y = 0; y < 1340; y += 72) { g.beginPath(); g.moveTo(0, y); g.lineTo(W, y); g.stroke(); } darkBottom(g, 'rgba(6,12,28,1)'); });
  const frame = tagFrame('axi_frame', 'НОВИНИ · AXIOS', RED, '#fff');
  const S = mkS(bg, frame);
  const card = (c, x, y, w, h, edge = 'rgba(159,176,214,.25)') => { c.save(); c.shadowColor = 'rgba(0,0,0,.45)'; c.shadowBlur = 36; c.shadowOffsetY = 14; c.fillStyle = CARD; c.fill(rr(x, y, w, h, 28)); c.restore(); c.strokeStyle = edge; c.lineWidth = 3; c.stroke(rr(x, y, w, h, 28)); };
  function doc(c, x, y, s, rot = 0) { c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.fillStyle = '#fff'; c.fill(rr(-120, -160, 240, 320, 16)); c.fillStyle = '#c9d2e6'; for (let i = 0; i < 6; i++) c.fillRect(-85, -100 + i * 40, i === 0 ? 120 : 170, 14); c.fillStyle = RED; c.beginPath(); c.arc(70, 110, 30, 0, 7); c.fill(); c.restore(); }
  S('x_hook', (c, lt) => {
    usFlag(c, 300, 620, 230 * back(at(lt, 0, 0.35)), 150 * back(at(lt, 0, 0.35))); pirate(c, 780, 620, 230 * back(at(lt, 0.15, 0.35)), 150 * back(at(lt, 0.15, 0.35)));
    txt(c, '→', 540, 650, 120, GOLD, { alpha: at(lt, 0.3, 0.3) });
    txt(c, 'ЩО США ХОЧУТЬ', 540, 900, 100, INK, { scale: back(at(lt, L(0, 1) - 0.2, 0.35)) }); txt(c, 'ВІД ПУТІНА?', 540, 1020, 100, GOLD, { scale: back(at(lt, L(0, 4) - 0.2, 0.35)) });
  }, lt => ({ z: 1.08 - 0.08 * eo(at(lt, 0, 1)) }));
  S('x_ask', (c, lt) => {
    const names = [[10, 'Кушнер', 330], [12, 'Віткофф', 750]]; names.forEach(([w, n, x]) => chip(c, n, x, 330, at(lt, L(1, w) - 0.25, 0.3), INK, '#101a33', 56));
    const tf = at(lt, L(1, 14) - 0.4, 1.0); const x = 220 + 640 * eio(tf), y = 640 - 120 * Math.sin(eio(tf) * Math.PI);
    txt(c, 'Вашингтон', 220, 860, 46, MUT, { alpha: at(lt, L(1, 13) - 0.3, 0.3) }); txt(c, 'Москва', 860, 860, 46, MUT, { alpha: at(lt, L(1, 16) - 0.3, 0.3) });
    c.save(); c.strokeStyle = 'rgba(242,193,78,.5)'; c.lineWidth = 6; c.setLineDash([16, 14]); c.beginPath(); c.moveTo(220, 640); c.quadraticCurveTo(540, 400, 860, 640); c.stroke(); c.restore();
    doc(c, x, y, 0.8 * back(at(lt, L(1, 13) - 0.3, 0.3)), -0.1 + 0.2 * tf);
    if (lt > L(1, 18) - 0.3) { const q = back(at(lt, L(1, 18) - 0.3, 0.35)); c.save(); c.translate(540, 1080); c.scale(q, q); card(c, -420, -110, 840, 220, GOLD); txt(c, 'НОВА ПРОПОЗИЦІЯ', 0, -15, 70, GOLD); txt(c, 'щодо безпеки Європи', 0, 60, 52, INK, { font: 'Oswald-400' }); c.restore(); }
  }, lt => ({ z: 1.0 + lt * 0.008 }));
  S('x_terms', (c, lt) => {
    txt(c, 'ЩО МАЄ БУТИ ВСЕРЕДИНІ', 540, 340, 66, GOLD, { alpha: at(lt, 0, 0.3) });
    const items = [[27, 'конкретні кроки', 'до деескалації'], [32, 'гарантії, що москалі', 'не нападуть на Європу']];
    items.forEach(([w, a, b], i) => { const k = eo(at(lt, L(2, w) - 0.35, 0.45)); if (k <= 0) return; const y = 440 + i * 330; c.save(); c.globalAlpha = k; c.translate((1 - k) * 200, 0); card(c, 90, y, 900, 260); c.fillStyle = GR; c.beginPath(); c.arc(200, y + 130, 54, 0, 7); c.fill(); c.strokeStyle = '#0b1630'; c.lineWidth = 14; c.lineCap = 'round'; c.beginPath(); c.moveTo(175, y + 132); c.lineTo(195, y + 152); c.lineTo(230, y + 108); c.stroke(); txt(c, a, 290, y + 115, 58, INK, { align: 'left' }); txt(c, b, 290, y + 190, 50, MUT, { align: 'left', font: 'Oswald-400' }); c.restore(); });
    if (lt > L(2, 34) - 0.3) { pirate(c, 380, 1150, 160 * back(at(lt, L(2, 34) - 0.3, 0.3)), 104 * back(at(lt, L(2, 34) - 0.3, 0.3))); txt(c, '✕', 540, 1180, 90, RED, { alpha: at(lt, L(2, 36) - 0.3, 0.2) }); euFlag(c, 700, 1150, 160 * back(at(lt, L(2, 38) - 0.3, 0.3)), 104 * back(at(lt, L(2, 38) - 0.3, 0.3))); }
  }, lt => ({ z: 1.0 + lt * 0.008 }));
  S('x_eu', (c, lt) => {
    c.save(); c.translate(540, 700); c.fillStyle = '#1b2f63'; c.beginPath(); c.arc(0, 0, 230, 0, 7); c.fill(); c.strokeStyle = GOLD; c.lineWidth = 6; c.stroke();
    [[-Math.PI / 2, 'ua'], [Math.PI / 6, 'us'], [Math.PI * 5 / 6, 'ru']].forEach(([a, k]) => { const x = Math.cos(a) * 330, y = Math.sin(a) * 300; if (k === 'ua') uaFlag(c, x, y, 150, 96); else if (k === 'us') usFlag(c, x, y, 150, 96); else pirate(c, x, y, 150, 96); });
    const e = back(at(lt, L(3, 44) - 0.3, 0.4)); if (e > 0) { c.save(); c.translate(0, 0); c.scale(e, e); euFlag(c, 0, 0, 200, 130); c.restore(); } c.restore();
    txt(c, 'ЄВРОПА ЗА СТОЛОМ', 540, 1120, 90, GOLD, { scale: back(at(lt, L(3, 45) - 0.2, 0.35)) }); txt(c, 'наступного раунду', 540, 1210, 52, MUT, { font: 'Oswald-400', alpha: at(lt, L(3, 47) - 0.2, 0.3) });
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('x_main', (c, lt) => {
    txt(c, 'ГОЛОВНЕ', 540, 340, 100, RED, { scale: back(at(lt, 0, 0.35)) });
    const q = eo(at(lt, L(4, 55) - 0.4, 0.5)); if (q > 0) { c.save(); c.globalAlpha = q; card(c, 90, 420, 900, 560, GOLD); txt(c, '«Угоди не буде', 540, 560, 84, INK); txt(c, 'без згоди', 540, 680, 84, INK); c.restore(); }
    const f = at(lt, L(4, 61) - 0.3, 0.3); if (f > 0) { uaFlag(c, 380, 840, 200 * back(f), 130 * back(f)); } const f2 = at(lt, L(4, 63) - 0.3, 0.3); if (f2 > 0) euFlag(c, 700, 840, 200 * back(f2), 130 * back(f2));
    txt(c, 'України та Європи»', 540, 1000, 64, GOLD, { alpha: f2 });
    txt(c, 'джерела Axios', 540, 1100, 50, MUT, { font: 'Oswald-400', alpha: at(lt, L(4, 53) - 0.2, 0.3) });
  }, lt => ({ z: 1.0 + lt * 0.01 }));
  S('x_end', (c, lt) => { doc(c, 540, 620, 1.1 * back(at(lt, 0, 0.4)), -0.06); txt(c, 'СТЕЖИМО ЗА НОВИНАМИ', 540, 920, 76, GOLD, { alpha: at(lt, 0.2, 0.3) }); subBtn(c, lt, L(5, 64) - 0.15, '#34405f'); }, lt => ({ z: 1.0 + lt * 0.01 }));
