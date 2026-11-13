/* PROВсе motion kit: субтитри-караоке, входи, склейки, лічильники, рух камери. Потрібен GSAP.
   Усе вішається на ОДНУ паузовану таймлінію tl (hyperframes рендерить її покадрово), жодних setTimeout/Date.now.
   Час завжди в секундах від початку ролика. T(i) = час початку i-го слова з words.json.            */
(function () {
  const $ = (s) => (typeof s === "string" ? document.querySelectorAll(s) : s);
  const one = (s) => (typeof s === "string" ? document.querySelector(s) : s);
  const Kit = {};
  let WORDS = [];

  Kit.init = function (words) { WORDS = words || []; return Kit; };
  /** Час слова i (секунди). Поза межами повертає край. */
  Kit.T = (i) => WORDS.length ? WORDS[Math.max(0, Math.min(i, WORDS.length - 1))][1] : 0;
  /** Індекс першого слова, що починається з prefix (без регістру), шукаючи від from. */
  Kit.find = function (prefix, from = 0) {
    const p = prefix.toLowerCase();
    for (let i = from; i < WORDS.length; i++) if (WORDS[i][0].toLowerCase().replace(/[^\p{L}\p{N}]/gu, "").startsWith(p)) return i;
    return -1;
  };

  /* ---------------- СУБТИТРИ ----------------
     Сторінки по 1–3 слова (розрив на розділовому знаку, паузі > .35 с або > maxChars символів).
     Кожне слово вистрибує в момент вимови (back.out), активне слово підсвічене, ключові лишаються кольоровими.
     opts: keywords: ["слово", ...] (без регістру, за початком), accent, key, plate (bool), maxWords, maxChars, end (кінець ролика). */
  Kit.captions = function (tl, opts = {}) {
    const o = Object.assign({ keywords: [], accent: "#FFD43B", key: "#FF4545", plate: false, maxWords: 3, maxChars: 15, end: null }, opts);
    const host = one("#caps") || (() => { const d = document.createElement("div"); d.id = "caps"; one("#root").appendChild(d); return d; })();
    const isKey = (w) => { const c = w.toLowerCase().replace(/[^\p{L}\p{N}]/gu, ""); return o.keywords.some((k) => c.startsWith(k.toLowerCase())); };
    const pages = []; let cur = [];
    WORDS.forEach((w, i) => {
      const chars = cur.reduce((n, j) => n + WORDS[j][0].length + 1, 0) + w[0].length;
      const gap = i > 0 ? w[1] - WORDS[i - 1][1] : 0;
      if (cur.length && (cur.length >= o.maxWords || chars > o.maxChars || gap > .62 || /[.,!?:;…]$/.test(WORDS[i - 1][0]))) { pages.push(cur); cur = []; }
      cur.push(i);
    });
    if (cur.length) pages.push(cur);
    const endT = o.end || (Kit.T(WORDS.length - 1) + 1);
    pages.forEach((idx, p) => {
      const pg = document.createElement("div"); pg.className = "cap-page" + (o.plate ? " plate" : "");
      idx.forEach((i) => {
        const s = document.createElement("span"); s.className = "cap-w";
        s.textContent = WORDS[i][0].replace(/[,;:]$/, "");
        if (isKey(WORDS[i][0])) s.dataset.key = "1";
        pg.appendChild(s);
      });
      host.appendChild(pg);
      const t0 = Kit.T(idx[0]) - .06;
      const t1 = p + 1 < pages.length ? Kit.T(pages[p + 1][0]) - .06 : Math.min(endT - .55, Kit.T(idx[idx.length - 1]) + 1.2);
      tl.set(pg, { opacity: 1, visibility: "visible" }, t0);
      if (o.plate) tl.fromTo(pg, { scaleX: .85, opacity: 0 }, { scaleX: 1, opacity: 1, duration: .14, ease: "power2.out" }, t0);
      [...pg.children].forEach((s, k) => {
        const i = idx[k], ti = Kit.T(i), tn = i + 1 < WORDS.length ? Kit.T(i + 1) : ti + .4, key = s.dataset.key;
        if (o.plate) {  // на плашці вся фраза видна приглушено, слово спалахує в момент вимови
          tl.set(s, { opacity: .38 }, t0);
          tl.fromTo(s, { opacity: .38, scale: .82 }, { opacity: 1, scale: 1, duration: .16, ease: "back.out(2.6)", immediateRender: false }, ti - .03);
        } else {
          tl.fromTo(s, { opacity: 0, scale: .5, y: 34 }, { opacity: 1, scale: 1, y: 0, duration: .17, ease: "back.out(2.6)" }, ti - .03);
        }
        tl.set(s, { color: key ? o.key : o.accent }, ti - .03);
        tl.to(s, { scale: 1.06, duration: .08, ease: "power1.out", yoyo: true, repeat: 1 }, ti + .1);
        if (!key) tl.set(s, { color: "var(--cap-fg,#fff)" }, Math.max(ti + .12, tn - .03));
      });
      tl.to(pg, { opacity: 0, duration: .07, ease: "power1.in" }, t1 - .08);   // стара фраза зникає ДО появи нової
      tl.set(pg, { visibility: "hidden" }, t1);
    });
    return pages;
  };

  /* ---------------- ВХОДИ / ВИХОДИ ----------------
     kind: pop | rise | drop | slideL | slideR | wipe | wipeUp | blur | stamp | zoomIn | flip | lines (рядки .mask>.line)  */
  const IN = {
    pop: [{ scale: .3, opacity: 0 }, { scale: 1, opacity: 1, duration: .38, ease: "back.out(2.2)" }],
    rise: [{ y: 90, opacity: 0 }, { y: 0, opacity: 1, duration: .42, ease: "expo.out" }],
    drop: [{ y: -140, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: "bounce.out" }],
    slideL: [{ x: -1100 }, { x: 0, duration: .45, ease: "expo.out" }],
    slideR: [{ x: 1100 }, { x: 0, duration: .45, ease: "expo.out" }],
    wipe: [{ clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: .45, ease: "power3.inOut" }],
    wipeUp: [{ clipPath: "inset(100% 0 0 0)" }, { clipPath: "inset(0% 0 0 0)", duration: .45, ease: "power3.out" }],
    blur: [{ filter: "blur(28px)", opacity: 0, scale: 1.15 }, { filter: "blur(0px)", opacity: 1, scale: 1, duration: .5, ease: "power2.out" }],
    stamp: [{ scale: 2.6, opacity: 0, rotation: -14 }, { scale: 1, opacity: 1, rotation: -6, duration: .26, ease: "power4.in" }],
    zoomIn: [{ scale: 1.6, opacity: 0 }, { scale: 1, opacity: 1, duration: .45, ease: "expo.out" }],
    flip: [{ rotationX: -90, opacity: 0, transformPerspective: 900 }, { rotationX: 0, opacity: 1, duration: .5, ease: "back.out(1.6)" }],
  };
  Kit.in = function (tl, sel, t, kind = "rise", opts = {}) {
    if (kind === "lines") {
      $(sel).forEach((el) => tl.fromTo(el.querySelectorAll(".line"), { yPercent: 110 }, { yPercent: 0, duration: .5, ease: "expo.out", stagger: opts.stagger ?? .08 }, t));
      return;
    }
    const [a, b] = IN[kind];
    tl.fromTo(sel, a, Object.assign({}, b, opts, { stagger: opts.stagger ?? 0 }), t);
    // тряску на штамп додавай окремо (Kit.shake), якщо справді потрібен удар
  };
  Kit.out = function (tl, sel, t, kind = "fade") {
    const v = { fade: { opacity: 0, duration: .2 }, up: { y: -120, opacity: 0, duration: .3, ease: "power2.in" },
      down: { y: 120, opacity: 0, duration: .3, ease: "power2.in" }, shrink: { scale: .6, opacity: 0, duration: .25, ease: "back.in(2)" },
      left: { x: -1100, duration: .35, ease: "power3.in" }, right: { x: 1100, duration: .35, ease: "power3.in" } }[kind];
    tl.to(sel, v, t);
  };
  /** Поява групи елементів по черзі. */
  Kit.stagger = (tl, sel, t, kind = "rise", gap = .09) => Kit.in(tl, sel, t, kind, { stagger: gap });

  /* ---------------- СКЛЕЙКИ МІЖ СЦЕНАМИ ----------------
     Сцени це .scene всередині #cam. Kit.cut показує toSel у момент t і ховає fromSel.
     kind: hard | whip | zoom | push | slideUp | flash | iris                                  */
  Kit.cut = function (tl, fromSel, toSel, t, kind = "whip") {
    const from = fromSel ? one(fromSel) : null, to = one(toSel);
    const d = { whip: .34, zoom: .42, push: .5, slideUp: .5, flash: .2, iris: .55, hard: 0 }[kind] ?? .35;
    const mid = t - d / 2;
    tl.set(to, { x: 0, y: 0, xPercent: 0, yPercent: 0, scale: 1, opacity: 1, filter: "none", clipPath: "none" }, mid - .001);
    tl.set(to, { visibility: "visible" }, ["hard", "flash", "zoom", "whip"].includes(kind) ? t : mid);
    if (kind === "whip") {
      if (from) tl.to(from, { x: -700, opacity: .4, duration: d / 2, ease: "power2.in" }, mid);
      tl.fromTo(to, { x: 700 }, { x: 0, duration: d / 2 + .08, ease: "power2.out", immediateRender: false }, t);
    } else if (kind === "zoom") {
      if (from) tl.to(from, { scale: 1.25, opacity: 0, duration: d / 2, ease: "power2.in" }, mid);
      tl.fromTo(to, { scale: .92, opacity: 0 }, { scale: 1, opacity: 1, duration: d / 2 + .1, ease: "power3.out", immediateRender: false }, t);
    } else if (kind === "push") {
      if (from) tl.to(from, { xPercent: -100, duration: d, ease: "power3.inOut" }, mid);
      tl.fromTo(to, { xPercent: 100 }, { xPercent: 0, duration: d, ease: "power3.inOut", immediateRender: false }, mid);
    } else if (kind === "slideUp") {
      if (from) tl.to(from, { yPercent: -100, duration: d, ease: "power3.inOut" }, mid);
      tl.fromTo(to, { yPercent: 100 }, { yPercent: 0, duration: d, ease: "power3.inOut", immediateRender: false }, mid);
    } else if (kind === "iris") {
      tl.fromTo(to, { clipPath: "circle(0% at 50% 42%)" }, { clipPath: "circle(80% at 50% 42%)", duration: d, ease: "power2.inOut", immediateRender: false }, mid);
    } else if (kind === "flash") {
      Kit.flash(tl, t);
    }
    if (from) tl.set(from, { visibility: "hidden" }, t + (kind === "push" || kind === "slideUp" || kind === "iris" ? d / 2 : 0));
  };
  Kit.flash = (tl, t, a = .85) => { const f = one("#flash"); if (f) tl.fromTo(f, { opacity: a }, { opacity: 0, duration: .22, ease: "power1.out", immediateRender: false }, t); };

  /* ---------------- ДРІБНИЙ РУХ (щоб кадр ніколи не стояв) ---------------- */
  /** Повільний наїзд/зсув протягом [t0, t1]: фото, фон, вся сцена. */
  Kit.drift = (tl, sel, t0, t1, o = {}) =>
    tl.fromTo(sel, { scale: o.from ?? 1, x: 0, y: 0 }, { scale: o.to ?? 1.08, x: o.x ?? 0, y: o.y ?? -20, duration: Math.max(.1, t1 - t0), ease: "none" }, t0);
  /** Різкий наїзд камери на акцентному слові. */
  Kit.punch = (tl, t, amt = 1.04, sel = "#cam") =>
    tl.fromTo(sel, { scale: 1 }, { scale: amt, duration: .3, ease: "power2.out" }, t).to(sel, { scale: 1, duration: .5, ease: "power2.inOut" }, t + .5);
  /** Тряска на удар, затухає за ~0,25 с. */
  Kit.shake = function (tl, sel = "#cam", t, amp = 12) {
    [1, -.8, .6, -.4, .2, 0].forEach((k, n) => tl.to(sel, { x: amp * k, y: -amp * k * .5, duration: .04, ease: "none" }, t + n * .04));
  };
  /** Лічильник: число від from до to. fmt: (v)=>рядок. */
  Kit.count = function (tl, sel, from, to, t, dur = .9, fmt) {
    const el = one(sel), obj = { v: from }, f = fmt || ((v) => Math.round(v).toLocaleString("uk-UA"));
    tl.set(el, { textContent: f(from) }, t - .001);
    tl.to(obj, { v: to, duration: dur, ease: "power2.out", onUpdate: () => { el.textContent = f(obj.v); } }, t);
  };
  /** Маркер-виділення під словом: <span style="position:relative">слово<i class="marker"></i></span> */
  Kit.mark = (tl, sel, t) => tl.to(sel, { scaleX: 1, duration: .3, ease: "power2.out" }, t);
  /** Стовпчики графіка: висоти в px. */
  Kit.bars = (tl, sel, t, gap = .08) => tl.fromTo(sel, { scaleY: 0 }, { scaleY: 1, duration: .55, ease: "back.out(1.4)", stagger: gap }, t);
  /** Лінія, що малюється (SVG path з stroke). */
  Kit.draw = function (tl, sel, t, dur = .8) {
    $(sel).forEach((p) => { const L = p.getTotalLength(); tl.fromTo(p, { strokeDasharray: L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: dur, ease: "power2.inOut" }, t); });
  };
  /** Петля: за loopDur до кінця повертає першу сцену так, щоб останній кадр збігався з першим. */
  Kit.loop = function (tl, lastSel, firstSel, end, kind = "zoom") {
    // Повертає першу сцену в її початковий стан (усі трансформації скинуті), щоб останній кадр збігся з першим
    tl.set(firstSel, { x: 0, y: 0, xPercent: 0, yPercent: 0, scale: 1, opacity: 1, filter: "none", clipPath: "none" }, end - .5);
    Kit.cut(tl, lastSel, firstSel, end - .35, kind);
  };


  /* ---------------- ТЕКСТ У КАДРІ = СУБТИТРИ ----------------
     Kit.say(tl, "#box", i0, i1, opts): слова з i0 по i1 (включно) з'являються в елементі #box рівно тоді, коли диктор
     їх вимовляє. Так текст на картинці і є субтитрами, без дублювання внизу.
     opts.map: {індекс: "текст"} заміна показу (напр. {11: "100%", 12: ""} для «сто відсотків»; "" = слово не показувати),
     opts.keys: основи ключових слів (фарбуються в --say-key), opts.kind: pop | rise | slam, opts.cls: клас для спанів.   */
  Kit.say = function (tl, sel, i0, i1, o = {}) {
    const box = one(sel), map = o.map || {}, keys = (o.keys || []).map((k) => k.toLowerCase());
    const kind = o.kind || "pop";
    // Спокійна поява без стрибків: слово проявляється на місці з легким підйомом; slam для великих цифр м'якший
    const from = { pop: { opacity: 0, y: 14 }, rise: { opacity: 0, y: 26 }, slam: { opacity: 0, scale: 1.25 } }[kind];
    const ease = { pop: "power2.out", rise: "power2.out", slam: "power3.out" }[kind];
    for (let i = i0; i <= i1 && i < WORDS.length; i++) {
      const txt = (i in map) ? map[i] : WORDS[i][0].replace(/[,;:]$/, "");
      if (!txt) continue;
      const s = document.createElement("span"); s.className = "say-w" + (o.cls ? " " + o.cls : "");
      s.textContent = txt;
      const c = txt.toLowerCase().replace(/[^\p{L}\p{N}%]/gu, "");
      if (keys.some((k) => c.startsWith(k)) || /\d/.test(txt)) s.classList.add("key");
      box.appendChild(s);
      tl.fromTo(s, from, { opacity: 1, scale: 1, y: 0, duration: .34, ease }, Kit.T(i) - .08);
    }
  };

  window.Kit = Kit;
})();
