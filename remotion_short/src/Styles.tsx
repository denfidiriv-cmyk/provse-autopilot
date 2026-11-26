// Alternative looks for the Short composition. Each style supplies its own card scene,
// photo/video scene, subtitle look and outro, so videos on different channels do not look alike.
import React from "react";
import {
  AbsoluteFill,
  Img,
  OffthreadVideo,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import type { Card, Scene } from "./Short";

export const W = 1080;
export const H = 1920;
export const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
export const norm = (s: string) => s.toLowerCase().replace(/[.,!?:;«»"()]/g, "");
const countable = (s: string) => /^[+-]?\d[\d ]*$/.test(s.trim());

// number count-up shared by styles ("945" ticks up from 0, "+1:20" stays as is)
export const useCount = (txt: string, f: number, frames = 16) => {
  if (!countable(txt)) return txt;
  const target = parseInt(txt.replace(/[^\d]/g, ""), 10);
  const v = Math.round(target * interpolate(f, [0, frames], [0, 1], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) }));
  const sign = txt.trim().startsWith("+") ? "+" : "";
  return sign + (target >= 10000 ? v.toLocaleString("uk-UA").replace(/ /g, " ") : String(v));
};

// photo or stock clip filling a box
export const Media: React.FC<{ s: Scene; style?: React.CSSProperties }> = ({ s, style }) =>
  s.video ? (
    <OffthreadVideo src={staticFile(s.video)} muted style={{ width: "100%", height: "100%", objectFit: "cover", ...style }} />
  ) : (
    <Img src={staticFile(s.src!)} style={{ width: "100%", height: "100%", objectFit: "cover", ...style }} />
  );

const Noise: React.FC<{ seed: number; opacity: number; blend?: React.CSSProperties["mixBlendMode"] }> = ({ seed, opacity, blend = "multiply" }) => (
  <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity, mixBlendMode: blend, pointerEvents: "none" }}>
    <filter id={`n${seed}`}>
      <feTurbulence type="fractalNoise" baseFrequency="0.75" numOctaves="3" seed={seed} />
      <feColorMatrix type="saturate" values="0" />
    </filter>
    <rect width={W} height={H} filter={`url(#n${seed})`} />
  </svg>
);

// =====================================================================================
// PAPER: investigator's desk / newspaper clippings
// =====================================================================================
const PAPER = "#ece3cf";
const INK = "#16130f";
const RED = "#c8211b";

export const PaperBg: React.FC<{ seed: number }> = ({ seed }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: PAPER }}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${20 + (seed % 3) * 25}% ${70 - (seed % 2) * 40}%, rgba(120,80,30,.18) 0 90px, rgba(120,80,30,.0) 120px),
          repeating-linear-gradient(0deg, rgba(0,0,0,.035) 0 2px, transparent 2px 46px)`,
          transform: `translateY(${-f * 0.4}px)`,
        }}
      />
      <Noise seed={seed} opacity={0.22} />
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 60%, rgba(60,40,10,.35) 100%)" }} />
    </AbsoluteFill>
  );
};

const Tape: React.FC<{ x: number; y: number; r: number }> = ({ x, y, r }) => (
  <div style={{ position: "absolute", left: x, top: y, width: 210, height: 58, background: "rgba(235,225,190,.82)", transform: `rotate(${r}deg)`, boxShadow: "0 2px 6px rgba(0,0,0,.15)" }} />
);

const torn = (seed: number) => {
  const pts: string[] = [];
  const n = 28;
  for (let i = 0; i <= n; i++) pts.push(`${(i / n) * 100}% ${((Math.sin(i * 7.3 + seed) + 1) * 1.1).toFixed(2)}%`);
  for (let i = n; i >= 0; i--) pts.push(`${(i / n) * 100}% ${(100 - (Math.sin(i * 5.1 + seed * 2) + 1) * 1.1).toFixed(2)}%`);
  return `polygon(${pts.join(",")})`;
};

export const PaperCard: React.FC<{ c: Card; idx: number; first: boolean; dur: number }> = ({ c, idx, first }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const { fps } = useVideoConfig();
  const drop = spring({ frame: f, fps, config: { damping: 13, stiffness: 120 } });
  const rot = idx % 2 ? 2.2 : -2.4;
  const big = useCount(c.big, f - 4);
  const circle = interpolate(f, [12, 30], [1, 0], clamp);
  const hi = interpolate(f, [18, 28], [0, 1], clamp);
  const bigSize = Math.min(280, Math.floor(740 / Math.max(2, c.big.length * 0.8)));
  return (
    <AbsoluteFill>
      <PaperBg seed={idx + 2} />
      <div
        style={{
          position: "absolute", left: 90, top: 470, width: 900, padding: "70px 50px 80px", background: "#f8f4ea",
          clipPath: torn(idx), boxShadow: "0 30px 60px rgba(0,0,0,.25)", textAlign: "center",
          transform: `translateY(${interpolate(drop, [0, 1], [-900, 0])}px) rotate(${rot + interpolate(drop, [0, 1], [-8, 0])}deg)`,
        }}
      >
        <div style={{ fontFamily: "PlexSerif", fontSize: 30, letterSpacing: 6, color: "#7a705f", borderBottom: "3px double #7a705f", paddingBottom: 10, marginBottom: 30 }}>
          ВСЕ ПРО · ДОСЬЄ
        </div>
        <div style={{ position: "relative", display: "inline-block" }}>
          <div style={{ fontFamily: "Lora", fontWeight: 700, fontSize: bigSize, color: INK, lineHeight: 1 }}>{big}</div>
          <svg width={bigSize * c.big.length * 0.8 + 120} height={bigSize * 1.35} style={{ position: "absolute", left: -60, top: -bigSize * 0.18 }} viewBox="0 0 100 100" preserveAspectRatio="none">
            <ellipse cx="50" cy="50" rx="47" ry="44" fill="none" stroke={RED} strokeWidth="2.4" pathLength={1} strokeDasharray="1" strokeDashoffset={circle} transform="rotate(-4 50 50)" vectorEffect="non-scaling-stroke" style={{ strokeWidth: 9 }} />
          </svg>
        </div>
        {c.unit ? <div style={{ fontFamily: "InterB", fontSize: Math.min(64, Math.floor(1500 / Math.max(10, c.unit.length))), color: RED, marginTop: 22 }}>{c.unit}</div> : null}
        {c.label ? (
          <div style={{ position: "relative", display: "inline-block", marginTop: 26, fontFamily: "Lora", fontWeight: 700, fontSize: 46, color: INK }}>
            <div style={{ position: "absolute", left: -12, right: -12, top: "38%", height: "56%", background: "#ffe14d", transformOrigin: "left", transform: `scaleX(${hi}) skewX(-8deg)`, opacity: 0.9 }} />
            <span style={{ position: "relative" }}>{c.label}</span>
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

export const PaperPhoto: React.FC<{ s: Scene; idx: number; first: boolean; dur: number; accent: string }> = ({ s, idx, first, dur }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const { fps } = useVideoConfig();
  const drop = spring({ frame: f, fps, config: { damping: 12, stiffness: 110 } });
  const rot = idx % 2 ? -3.5 : 3;
  const zoom = interpolate(f0, [0, dur], [1, 1.1]);
  return (
    <AbsoluteFill>
      <PaperBg seed={idx + 7} />
      {s.title ? (
        <div style={{ position: "absolute", top: 250, left: 70, width: W - 190, fontFamily: "Lora", fontWeight: 700, fontSize: 92, lineHeight: 1.05, color: INK, opacity: interpolate(f, [4, 12], [0, 1], clamp) }}>
          {s.title.split(" ").map((w, i) => (
            <span key={i} style={{ color: s.titleAcc && norm(w).includes(norm(s.titleAcc)) ? RED : INK }}>{w} </span>
          ))}
        </div>
      ) : null}
      <div
        style={{
          position: "absolute", left: 120, top: s.title ? 560 : 420, width: 840, height: 980, background: "#fbfaf6", padding: "26px 26px 110px",
          boxShadow: "0 35px 70px rgba(0,0,0,.35)", transform: `translateY(${interpolate(drop, [0, 1], [1400, 0])}px) rotate(${rot + interpolate(drop, [0, 1], [10, 0])}deg)`,
        }}
      >
        <div style={{ width: "100%", height: "100%", overflow: "hidden", background: "#222" }}>
          <Media s={s} style={{ transform: `scale(${zoom})`, filter: "sepia(.18) contrast(1.05)" }} />
        </div>
        <Tape x={-60} y={-24} r={-28} />
        <Tape x={690} y={-20} r={24} />
      </div>
    </AbsoluteFill>
  );
};

// =====================================================================================
// KINETIC: bold typography on black / accent, photos in an expanding circle
// =====================================================================================
export const KineticCard: React.FC<{ c: Card; idx: number; first: boolean; dur: number; accent: string }> = ({ c, idx, first, accent }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const { fps } = useVideoConfig();
  const inv = idx % 2 === 1;
  const bg = inv ? accent : "#0b0b0b";
  const fg = inv ? "#0b0b0b" : "#ffffff";
  const ac = inv ? "#ffffff" : accent;
  const wipe = interpolate(f, [0, 9], [0, 100], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
  const pBig = spring({ frame: f - 3, fps, config: { damping: 15, stiffness: 140 } });
  const pBar = spring({ frame: f - 9, fps, config: { damping: 16, stiffness: 150 } });
  const typed = Math.floor(interpolate(f, [14, 14 + (c.label?.length ?? 0) * 0.9], [0, c.label?.length ?? 0], clamp));
  const big = useCount(c.big, f - 3);
  const bigSize = Math.min(380, Math.floor(1000 / Math.max(2, c.big.length * 0.7)));
  return (
    <AbsoluteFill style={{ background: inv ? "#0b0b0b" : accent }}>
      <AbsoluteFill style={{ background: bg, clipPath: `polygon(0 0, ${wipe * 1.4}% 0, ${wipe * 1.4 - 40}% 100%, 0 100%)` }} />
      <div style={{ position: "absolute", left: 60, top: 600, width: W - 120 }}>
        <div style={{ fontFamily: "InterB", fontSize: bigSize, lineHeight: 0.92, color: fg, letterSpacing: -bigSize * 0.05, transform: `translateX(${interpolate(pBig, [0, 1], [700, 0])}px) skewX(${interpolate(pBig, [0, 1], [-18, 0])}deg)`, whiteSpace: "nowrap" }}>
          {big}
        </div>
        {c.unit ? (
          <div style={{ display: "inline-block", marginTop: 26, padding: "10px 24px", background: ac, color: bg, fontFamily: "InterB", fontSize: Math.min(70, Math.floor(1600 / Math.max(10, c.unit.length))), transform: `translateX(${interpolate(pBar, [0, 1], [-900, 0])}px)` }}>
            {c.unit}
          </div>
        ) : null}
        {c.label ? (
          <div style={{ marginTop: 34, fontFamily: "JBMono", fontSize: 44, color: fg }}>
            {c.label.slice(0, typed)}
            <span style={{ opacity: Math.floor(f0 / 8) % 2 ? 1 : 0, color: ac }}>▍</span>
          </div>
        ) : null}
      </div>
      <Noise seed={idx + 30} opacity={0.12} blend="overlay" />
    </AbsoluteFill>
  );
};

export const KineticPhoto: React.FC<{ s: Scene; idx: number; first: boolean; dur: number; accent: string }> = ({ s, idx, first, dur, accent }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const r = interpolate(f, [0, 12], [0, 78], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
  const zoom = interpolate(f0, [0, dur], [1.15, 1.02]);
  return (
    <AbsoluteFill style={{ background: "#0b0b0b" }}>
      <AbsoluteFill style={{ clipPath: `circle(${r}% at 50% ${s.title ? 62 : 48}%)` }}>
        <Media s={s} style={{ transform: `scale(${zoom})`, filter: "grayscale(1) contrast(1.15) brightness(.9)" }} />
        <AbsoluteFill style={{ background: accent, mixBlendMode: "multiply", opacity: 0.55 }} />
      </AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, border: `14px solid ${accent}`, clipPath: `circle(${r}% at 50% ${s.title ? 62 : 48}%)`, opacity: 0.0 }} />
      {s.title ? (
        <div style={{ position: "absolute", left: 60, top: 300, width: W - 180 }}>
          {s.title.split(" ").map((w, i) => {
            const x = interpolate(f, [2 + i * 3, 10 + i * 3], [i % 2 ? 600 : -600, 0], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
            const acc = s.titleAcc && norm(w).includes(norm(s.titleAcc));
            return (
              <div key={i} style={{ fontFamily: "InterB", fontSize: 120, lineHeight: 0.98, color: acc ? accent : "#fff", transform: `translateX(${x}px)`, textTransform: "uppercase", letterSpacing: -3, textShadow: "0 8px 30px rgba(0,0,0,.6)" }}>
                {w}
              </div>
            );
          })}
        </div>
      ) : null}
      <Noise seed={idx + 40} opacity={0.1} blend="overlay" />
    </AbsoluteFill>
  );
};

// =====================================================================================
// BOARD: stadium scoreboard, split-flap characters
// =====================================================================================
export const BoardBg: React.FC<{ seed: number; color?: string }> = ({ seed, color = "#071a12" }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: color }}>
      <AbsoluteFill style={{ background: `radial-gradient(ellipse at ${30 + (seed % 3) * 20}% -5%, rgba(255,255,230,.35), rgba(0,0,0,0) 55%)` }} />
      <AbsoluteFill style={{ backgroundImage: "radial-gradient(rgba(255,255,255,.07) 2px, transparent 2.5px)", backgroundSize: "18px 18px", transform: `translateY(${(f * 0.6) % 18}px)` }} />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 60%, rgba(0,0,0,.5))" }} />
    </AbsoluteFill>
  );
};

const Flap: React.FC<{ ch: string; delay: number; size: number; color: string }> = ({ ch, delay, size, color }) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [delay, delay + 7], [0, 1], clamp);
  const pool = "0123456789";
  const shown = p < 1 && /\d/.test(ch) ? pool[(Math.floor(f * 1.7) + delay) % 10] : ch;
  if (ch === " ") return <div style={{ width: size * 0.3 }} />;
  return (
    <div style={{ position: "relative", width: size * 0.68, height: size * 1.05, margin: "0 5px", background: "linear-gradient(180deg,#1d2a24 0 49.5%,#0c1411 50.5% 100%)", borderRadius: 12, boxShadow: "0 10px 24px rgba(0,0,0,.5), inset 0 0 0 2px rgba(255,255,255,.06)", display: "flex", alignItems: "center", justifyContent: "center", transform: `perspective(800px) rotateX(${interpolate(p, [0, 1], [-80, 0])}deg)`, opacity: interpolate(p, [0, 0.2], [0, 1], clamp) }}>
      <span style={{ fontFamily: "Tektur", fontSize: size, color, lineHeight: 1, textShadow: `0 0 18px ${color}88` }}>{shown}</span>
      <div style={{ position: "absolute", left: 0, right: 0, top: "50%", height: 3, background: "rgba(0,0,0,.65)" }} />
    </div>
  );
};

export const BoardCard: React.FC<{ c: Card; idx: number; first: boolean; dur: number; accent: string }> = ({ c, idx, first, accent }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 60 : f0;
  const chars = c.big.split("");
  const size = Math.min(230, Math.floor(880 / Math.max(2, chars.length * 0.78)));
  const pUnit = interpolate(f, [chars.length * 3 + 6, chars.length * 3 + 14], [0, 1], clamp);
  return (
    <AbsoluteFill>
      <BoardBg seed={idx} />
      <AbsoluteFill style={{ alignItems: "center", paddingTop: 620 }}>
        <div style={{ display: "flex" }}>
          {chars.map((ch, i) => (
            <Flap key={i} ch={ch} delay={(first ? -60 : 0) + i * 3} size={size} color={i === 0 && c.big.startsWith("+") ? accent : "#ffe9a8"} />
          ))}
        </div>
        {c.unit ? <div style={{ marginTop: 40, fontFamily: "Tektur", fontSize: 76, letterSpacing: 4, color: accent, opacity: pUnit, transform: `translateY(${(1 - pUnit) * 30}px)` }}>{c.unit}</div> : null}
        {c.label ? <div style={{ marginTop: 22, padding: "10px 30px", border: `3px solid ${accent}`, borderRadius: 10, fontFamily: "InterX", fontSize: 40, color: "#e8f2ec", opacity: pUnit }}>{c.label}</div> : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const BoardPhoto: React.FC<{ s: Scene; idx: number; first: boolean; dur: number; accent: string }> = ({ s, idx, first, dur, accent }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const wipe = interpolate(f, [0, 10], [0, 130], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
  const zoom = interpolate(f0, [0, dur], [1.08, 1.2]);
  const pT = interpolate(f, [8, 16], [0, 1], clamp);
  return (
    <AbsoluteFill style={{ background: "#071a12" }}>
      <AbsoluteFill style={{ clipPath: `polygon(0 0, ${wipe}% 0, ${wipe - 30}% 100%, 0 100%)` }}>
        <Media s={s} style={{ transform: `scale(${zoom}) translateX(${idx % 2 ? 20 : -20}px)`, filter: "contrast(1.08) saturate(1.1)" }} />
        <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(4,18,12,.85))" }} />
      </AbsoluteFill>
      <div style={{ position: "absolute", left: 0, top: 0, width: 26, height: H, background: accent, transform: `scaleY(${interpolate(f, [4, 14], [0, 1], clamp)})`, transformOrigin: "top" }} />
      {s.title ? (
        <div style={{ position: "absolute", left: 70, top: 1000, padding: "18px 34px", background: "rgba(5,20,14,.88)", borderLeft: `14px solid ${accent}`, fontFamily: "Tektur", fontSize: 92, lineHeight: 1.05, color: "#fff", opacity: pT, transform: `translateX(${(1 - pT) * -200}px)`, maxWidth: 860 }}>
          {s.title.split(" ").map((w, i) => (
            <span key={i} style={{ color: s.titleAcc && norm(w).includes(norm(s.titleAcc)) ? accent : "#fff" }}>{w} </span>
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// =====================================================================================
// RADAR: weather/satellite HUD over a persistent satellite backdrop
// =====================================================================================
export const RadarBg: React.FC<{ src?: string; accent: string }> = ({ src, accent }) => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: "#03121a", overflow: "hidden" }}>
      {src ? <Img src={staticFile(src)} style={{ width: W, height: H, objectFit: "cover", opacity: 0.38, transform: `scale(${1.25 + f * 0.0006}) rotate(${f * 0.03}deg)`, filter: "grayscale(.4) hue-rotate(-10deg)" }} /> : null}
      <AbsoluteFill style={{ background: `conic-gradient(from ${f * 4}deg at 50% 46%, ${accent}55 0deg, transparent 40deg, transparent 360deg)`, mixBlendMode: "screen" }} />
      {[260, 480, 700].map((r) => (
        <div key={r} style={{ position: "absolute", left: W / 2 - r, top: H * 0.46 - r, width: r * 2, height: r * 2, borderRadius: "50%", border: `2px solid ${accent}44` }} />
      ))}
      <AbsoluteFill style={{ backgroundImage: `linear-gradient(${accent}14 1px, transparent 1px), linear-gradient(90deg, ${accent}14 1px, transparent 1px)`, backgroundSize: "90px 90px" }} />
      <AbsoluteFill style={{ background: "repeating-linear-gradient(0deg, rgba(0,0,0,.18) 0 2px, transparent 2px 5px)" }} />
    </AbsoluteFill>
  );
};

const Brackets: React.FC<{ color: string; p: number }> = ({ color, p }) => {
  const s = { position: "absolute" as const, width: 70, height: 70, borderColor: color, borderStyle: "solid", opacity: p };
  const o = interpolate(p, [0, 1], [40, 0]);
  return (
    <>
      <div style={{ ...s, left: -o, top: -o, borderWidth: "6px 0 0 6px" }} />
      <div style={{ ...s, right: -o, top: -o, borderWidth: "6px 6px 0 0" }} />
      <div style={{ ...s, left: -o, bottom: -o, borderWidth: "0 0 6px 6px" }} />
      <div style={{ ...s, right: -o, bottom: -o, borderWidth: "0 6px 6px 0" }} />
    </>
  );
};

export const RadarCard: React.FC<{ c: Card; idx: number; first: boolean; dur: number; accent: string; bgSrc?: string }> = ({ c, idx, first, accent, bgSrc }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const p = interpolate(f, [0, 10], [0, 1], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
  const big = useCount(c.big, f - 2, 20);
  const scan = interpolate(f0 % 45, [0, 45], [-10, 110]);
  const size = Math.min(260, Math.floor(860 / Math.max(2, c.big.length * 0.66)));
  return (
    <AbsoluteFill>
      <RadarBg src={bgSrc} accent={accent} />
      <div style={{ position: "absolute", left: 110, top: 560, width: 860, padding: "70px 40px", background: "rgba(2,20,28,.72)", backdropFilter: "blur(6px)", textAlign: "center", transform: `scale(${interpolate(p, [0, 1], [0.9, 1])})`, opacity: p, overflow: "hidden" }}>
        <Brackets color={accent} p={p} />
        <div style={{ position: "absolute", left: 0, right: 0, top: `${scan}%`, height: 3, background: accent, opacity: 0.5, boxShadow: `0 0 20px ${accent}` }} />
        <div style={{ fontFamily: "Geist", fontSize: size, color: "#eafcff", lineHeight: 1, textShadow: `0 0 30px ${accent}aa` }}>{big}</div>
        {c.unit ? <div style={{ marginTop: 20, fontFamily: "Geist", fontSize: 64, letterSpacing: 8, color: accent }}>{c.unit}</div> : null}
        {c.label ? <div style={{ marginTop: 26, fontFamily: "Geist", fontSize: 38, color: "#9fd6e0" }}>{"> " + c.label}</div> : null}
      </div>
    </AbsoluteFill>
  );
};

export const RadarPhoto: React.FC<{ s: Scene; idx: number; first: boolean; dur: number; accent: string; bgSrc?: string }> = ({ s, first, dur, accent, bgSrc }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 40 : f0;
  const p = interpolate(f, [0, 10], [0, 1], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) });
  const zoom = interpolate(f0, [0, dur], [1.05, 1.18]);
  return (
    <AbsoluteFill>
      <RadarBg src={bgSrc} accent={accent} />
      <div style={{ position: "absolute", left: 90, top: s.title ? 640 : 470, width: 900, height: 900, transform: `scale(${interpolate(p, [0, 1], [1.12, 1])})`, opacity: p }}>
        <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
          <Media s={s} style={{ transform: `scale(${zoom})`, filter: "saturate(.85) contrast(1.1)" }} />
          <AbsoluteFill style={{ background: "repeating-linear-gradient(0deg, rgba(0,0,0,.2) 0 2px, transparent 2px 5px)" }} />
        </div>
        <Brackets color={accent} p={p} />
      </div>
      {s.title ? (
        <div style={{ position: "absolute", left: 90, top: 380, width: 900, fontFamily: "Geist", fontSize: 84, lineHeight: 1.08, color: "#eafcff", textShadow: `0 0 24px ${accent}88`, opacity: interpolate(f, [4, 10], [0, 1], clamp) }}>
          {s.title.split(" ").map((w, i) => (
            <span key={i} style={{ color: s.titleAcc && norm(w).includes(norm(s.titleAcc)) ? accent : "#eafcff" }}>{w} </span>
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// =====================================================================================
// per-style subtitle and outro looks
// =====================================================================================
export type SubLook = { font: string; size: number; color: string; active: string; box?: string; boxText?: string; stroke?: string; top: number };
export const subLook = (style: string, accent: string): SubLook => {
  switch (style) {
    case "paper":
      return { font: "InterB", size: 74, color: "#16130f", active: "#16130f", box: "#ffe14d", boxText: "#16130f", top: 1480 };
    case "kinetic":
      return { font: "InterB", size: 92, color: "#fff", active: "#0b0b0b", box: accent, stroke: "10px #000", top: 1380 };
    case "board":
      return { font: "Tektur", size: 86, color: "#fff", active: accent, stroke: "10px #04120c", top: 1240 };
    case "radar":
      return { font: "Geist", size: 70, color: "#eafcff", active: accent, box: "rgba(2,20,28,.8)", top: 1440 };
    default:
      return { font: "Osw", size: 96, color: "#fff", active: accent, stroke: "12px #000", top: 1130 };
  }
};
