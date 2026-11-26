import React from "react";
import { BoardBg, BoardCard, BoardPhoto, KineticCard, KineticPhoto, Media, PaperBg, PaperCard, PaperPhoto, RadarBg, RadarCard, RadarPhoto, subLook, SubLook } from "./Styles";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

// ---- props -------------------------------------------------------------
export type Card = {
  big: string;
  unit?: string;
  label?: string;
  bg: string;
  fg: string;
  accent: string;
};
export type Scene = {
  start: number; // seconds
  end: number;
  kind: "photo" | "card";
  src?: string; // photo path inside public/
  cutout?: string; // optional transparent png drawn over the photo
  title?: string; // big text over the photo (then no subtitles here)
  titleAcc?: string;
  card?: Card;
  video?: string; // stock clip path inside public/ (replaces src)
};
export type Word = { text: string; start: number; end: number };
export type ShortProps = {
  audio: string;
  duration: number;
  accent: string;
  keywords: string[];
  scenes: Scene[];
  words: Word[];
  outro: { top: string; acc: string; bg: string; bg2: string; start: number };
  style?: "cards" | "paper" | "kinetic" | "board" | "radar";
  bgSrc?: string; // radar backdrop
};

const W = 1080;
const H = 1920;

const fontFaces = `
@font-face{font-family:'InterB';src:url(${staticFile("fonts/Inter-Black.otf")});}
@font-face{font-family:'InterX';src:url(${staticFile("fonts/Inter-ExtraBold.otf")});}
@font-face{font-family:'InterS';src:url(${staticFile("fonts/Inter-SemiBold.otf")});}
@font-face{font-family:'Osw';src:url(${staticFile("fonts/Oswald-700.woff")});}
@font-face{font-family:'Lora';font-weight:700;src:url(${staticFile("fonts/Lora-Bold.ttf")});}
@font-face{font-family:'PlexSerif';src:url(${staticFile("fonts/IBMPlexSerif-Bold.ttf")});}
@font-face{font-family:'Tektur';src:url(${staticFile("fonts/Tektur-Medium.ttf")});}
@font-face{font-family:'Geist';src:url(${staticFile("fonts/GeistMono-Bold.ttf")});}
@font-face{font-family:'JBMono';src:url(${staticFile("fonts/JetBrainsMono-Bold.ttf")});}
`;

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;
const norm = (s: string) => s.toLowerCase().replace(/[.,!?:;«»"()]/g, "");

// film grain + vignette shared by every scene
const Grain: React.FC<{ seed: number }> = ({ seed }) => (
  <AbsoluteFill style={{ pointerEvents: "none" }}>
    <svg width={W} height={H} style={{ position: "absolute", opacity: 0.09, mixBlendMode: "overlay" }}>
      <filter id={`g${seed}`}>
        <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={seed} />
      </filter>
      <rect width={W} height={H} filter={`url(#g${seed})`} />
    </svg>
    <AbsoluteFill
      style={{ background: "radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 55%, rgba(0,0,0,.45) 100%)" }}
    />
  </AbsoluteFill>
);

// ---- big text that slams in word by word --------------------------------
const Slam: React.FC<{ text: string; acc?: string; color: string; accColor: string; size: number; delay?: number; skipIntro?: boolean }> = ({
  text, acc, color, accColor, size, delay = 0, skipIntro,
}) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");
  return (
    <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "center", gap: `0 ${size * 0.22}px`, lineHeight: 1.02 }}>
      {words.map((w, i) => {
        const p = skipIntro ? 1 : spring({ frame: f - delay - i * 3, fps, config: { damping: 11, stiffness: 190, mass: 0.6 } });
        const isAcc = acc && norm(w).includes(norm(acc));
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              fontFamily: "Osw",
              fontSize: size,
              color: isAcc ? accColor : color,
              textTransform: "uppercase",
              transform: `scale(${interpolate(p, [0, 1], [1.7, 1])})`,
              opacity: interpolate(p, [0, 0.35], [0, 1], clamp),
              textShadow: "0 8px 30px rgba(0,0,0,.55)",
              WebkitTextStroke: "3px rgba(0,0,0,.35)",
            }}
          >
            {w}
          </span>
        );
      })}
    </div>
  );
};

// ---- photo scene ---------------------------------------------------------
const PhotoScene: React.FC<{ s: Scene; dur: number; idx: number; accent: string; first: boolean }> = ({ s, dur, idx, accent, first }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const punch = first ? 0 : 1 - spring({ frame: f, fps, config: { damping: 14, stiffness: 160 } });
  const drift = interpolate(f, [0, dur], [1.06, 1.17]);
  const dir = idx % 2 ? 1 : -1;
  const cut = s.cutout ? spring({ frame: f - 4, fps, config: { damping: 12, stiffness: 120 } }) : 0;
  return (
    <AbsoluteFill style={{ background: "#000", overflow: "hidden" }}>
      <Media
        s={s}
        style={{
          width: W, height: H, objectFit: "cover",
          transform: `scale(${drift + punch * 0.14}) translateX(${dir * interpolate(f, [0, dur], [-14, 14])}px)`,
          filter: s.cutout ? "blur(6px) brightness(.55)" : "brightness(.92) contrast(1.06) saturate(1.08)",
        }}
      />
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(0,0,0,.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 52%, rgba(0,0,0,.6) 100%)" }} />
      {s.cutout ? (
        <AbsoluteFill style={{ alignItems: "center", justifyContent: "center" }}>
          <Img
            src={staticFile(s.cutout)}
            style={{
              width: 1040, maxHeight: 1000, objectFit: "contain",
              transform: `translateY(${interpolate(cut, [0, 1], [380, 60]) + Math.sin(f / 14) * 8}px) scale(${interpolate(cut, [0, 1], [0.7, 1]) + f * 0.0007})`,
              filter: "drop-shadow(0 40px 50px rgba(0,0,0,.6))",
            }}
          />
        </AbsoluteFill>
      ) : null}
      {s.title ? (
        <div style={{ position: "absolute", top: 560, left: 90, width: W - 210 }}>
          <Slam text={s.title} acc={s.titleAcc} color="#fff" accColor={accent} size={124} skipIntro={first} />
        </div>
      ) : null}
      <Grain seed={idx + 3} />
    </AbsoluteFill>
  );
};

// ---- card scene ----------------------------------------------------------
const countable = (s: string) => /^[+-]?\d[\d ]*$/.test(s.trim());
const CardScene: React.FC<{ c: Card; dur: number; idx: number; first: boolean }> = ({ c, dur, idx, first }) => {
  const f0 = useCurrentFrame();
  const f = first ? f0 + 30 : f0;
  const { fps } = useVideoConfig();
  const pBig = spring({ frame: f, fps, config: { damping: 10, stiffness: 170, mass: 0.7 } });
  const pUnit = spring({ frame: f - 6, fps, config: { damping: 14, stiffness: 160 } });
  const pLab = interpolate(f, [11, 21], [0, 100], clamp);
  let big = c.big;
  if (countable(c.big)) {
    const target = parseInt(c.big.replace(/[^\d]/g, ""), 10);
    const v = Math.round(target * interpolate(f, [0, 16], [0, 1], { ...clamp, easing: (t) => 1 - Math.pow(1 - t, 3) }));
    const sign = c.big.trim().startsWith("+") ? "+" : "";
    big = sign + (target >= 10000 ? v.toLocaleString("uk-UA").replace(/ /g, " ") : String(v));
  }
  const bigSize = Math.min(330, Math.floor((W - 140) / Math.max(2.2, c.big.length * 0.74)));
  const push = interpolate(f0, [0, dur], [1, 1.05]);
  return (
    <AbsoluteFill style={{ background: c.bg, overflow: "hidden" }}>
      <AbsoluteFill style={{ background: `radial-gradient(circle at ${30 + (idx % 3) * 20}% 30%, rgba(255,255,255,.16), rgba(0,0,0,0) 60%), linear-gradient(180deg, rgba(0,0,0,0) 55%, rgba(0,0,0,.28))` }} />
      <div
        style={{
          position: "absolute", left: -200, top: 300 + (idx % 2) * 900, width: 1500, height: 46,
          background: c.accent, opacity: 0.16, transform: `rotate(-8deg) translateX(${interpolate(f0, [0, dur], [-60, 60])}px)`,
        }}
      />
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 560, transform: `scale(${push})` }}>
        <div
          style={{
            fontFamily: "InterB", fontSize: bigSize, color: c.fg, letterSpacing: -bigSize * 0.03, lineHeight: 1,
            transform: `scale(${interpolate(pBig, [0, 1], [0.4, 1])}) rotate(${interpolate(pBig, [0, 1], [-6, 0])}deg)`,
            opacity: interpolate(pBig, [0, 0.3], [0, 1], clamp), textShadow: "0 18px 40px rgba(0,0,0,.25)",
            whiteSpace: "nowrap",
          }}
        >
          {big}
        </div>
        {c.unit ? (
          <div
            style={{
              fontFamily: "InterB", fontSize: Math.min(76, Math.floor(1700 / Math.max(10, c.unit.length))), color: c.accent,
              marginTop: 18, transform: `translateY(${interpolate(pUnit, [0, 1], [60, 0])}px)`, opacity: pUnit, textAlign: "center",
            }}
          >
            {c.unit}
          </div>
        ) : null}
        {c.label ? (
          <div
            style={{
              marginTop: 30, padding: "12px 26px", background: c.fg, color: c.bg, fontFamily: "InterX", fontSize: 44,
              clipPath: `inset(0 ${100 - pLab}% 0 0)`, borderRadius: 8, maxWidth: 880, textAlign: "center",
            }}
          >
            {c.label}
          </div>
        ) : null}
      </AbsoluteFill>
      <Grain seed={idx + 11} />
    </AbsoluteFill>
  );
};

// ---- subtitles (only where nothing else is written on screen) -----------
type Page = { words: Word[]; start: number; end: number };
const makePages = (ws: Word[]): Page[] => {
  const pages: Page[] = [];
  let cur: Word[] = [];
  const flush = () => {
    if (cur.length) pages.push({ words: cur, start: cur[0].start, end: cur[cur.length - 1].end });
    cur = [];
  };
  for (const w of ws) {
    if (cur.length && (w.start - cur[cur.length - 1].end > 0.35 || cur.length >= 3)) flush();
    cur.push(w);
    if (/[.,!?:;]$/.test(w.text)) flush();
  }
  flush();
  return pages;
};

const Subtitles: React.FC<{ pages: Page[]; look: SubLook; keywords: Set<string> }> = ({ pages, look, keywords }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const page = pages.find((p) => t >= p.start - 0.05 && t < p.end + 0.12);
  if (!page) return null;
  return (
    <div style={{ position: "absolute", top: look.top, left: 80, width: W - 200, display: "flex", flexWrap: "wrap", justifyContent: "center", gap: "10px 18px" }}>
      {page.words.map((w, i) => {
        const p = spring({ frame: f - Math.round(w.start * fps), fps, config: { damping: 12, stiffness: 220, mass: 0.5 } });
        if (t < w.start - 0.02) return null;
        const active = t >= w.start && t < w.end;
        const key = keywords.has(norm(w.text));
        const boxed = !!look.box;
        return (
          <span
            key={i}
            style={{
              fontFamily: look.font, fontSize: look.size, textTransform: "uppercase", lineHeight: 1.05,
              color: key && !boxed ? "#ff3b30" : active ? look.active : look.color,
              background: boxed ? (active && look.box !== look.active ? look.box : look.box) : undefined,
              padding: boxed ? "4px 16px" : undefined,
              boxShadow: boxed && key ? "inset 0 -10px 0 #ff3b30" : undefined,
              transform: `scale(${interpolate(p, [0, 1], [0.55, 1]) * (active ? 1.06 : 1)}) rotate(${boxed ? (i % 2 ? 1.2 : -1.2) : 0}deg)`,
              opacity: interpolate(p, [0, 0.3], [0, 1], clamp),
              WebkitTextStroke: look.stroke, paintOrder: "stroke fill",
              textShadow: look.stroke ? "0 6px 18px rgba(0,0,0,.6)" : undefined,
            }}
          >
            {w.text.replace(/[,:;.]$/, "")}
          </span>
        );
      })}
    </div>
  );
};

// ---- outro ----------------------------------------------------------------
const Outro: React.FC<{ o: ShortProps["outro"]; accent: string; style: string; bgSrc?: string }> = ({ o, accent, style, bgSrc }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({ frame: f - 8, fps, config: { damping: 11, stiffness: 150 } });
  const bg =
    style === "paper" ? <PaperBg seed={42} /> : style === "board" ? <BoardBg seed={5} /> : style === "radar" ? <RadarBg src={bgSrc} accent={accent} /> : style === "kinetic" ? <AbsoluteFill style={{ background: "#0b0b0b" }} /> : <AbsoluteFill style={{ background: `linear-gradient(180deg, ${o.bg}, ${o.bg2})` }} />;
  const font = style === "paper" ? "Lora" : style === "board" ? "Tektur" : style === "radar" ? "Geist" : style === "kinetic" ? "InterB" : "Osw";
  const ink = style === "paper" ? "#16130f" : "#fff";
  const acc = style === "paper" ? "#c8211b" : accent;
  return (
    <AbsoluteFill>
      {bg}
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "flex-start", paddingTop: 640 }}>
        <div style={{ fontFamily: font, fontWeight: 700, fontSize: 110, color: ink, opacity: interpolate(f, [0, 6], [0, 1], clamp) }}>{o.top}</div>
        <div style={{ fontFamily: font, fontWeight: 700, fontSize: Math.min(170, Math.floor(920 / (o.acc.length * 0.72))), color: acc, textTransform: "uppercase", transform: `scale(${interpolate(p, [0, 1], [0.3, 1])})`, opacity: p, textShadow: style === "paper" ? undefined : "0 10px 40px rgba(0,0,0,.5)" }}>
          {o.acc}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---- composition ----------------------------------------------------------
export const Short: React.FC<ShortProps> = (props) => {
  const { fps } = useVideoConfig();
  const fr = (s: number) => Math.round(s * fps);
  const quiet: Array<[number, number]> = [];
  props.scenes.forEach((s) => {
    if (s.kind === "photo" && !s.title) quiet.push([s.start, s.end]);
  });
  const subWords = props.words.filter((w) => w.start < props.outro.start && quiet.some(([a, b]) => w.start >= a - 0.05 && w.start < b));
  const pages = makePages(subWords).map((p) => {
    const q = quiet.find(([a, b]) => p.start >= a - 0.05 && p.start < b)!;
    return { ...p, end: Math.min(p.end, q[1] - 0.06) };
  });
  const kw = new Set(props.keywords.map(norm));
  const loopFrames = 10;
  const total = fr(props.duration);
  const st = props.style ?? "cards";
  const renderScene = (s: Scene, i: number, dur: number, first: boolean) => {
    const a = { idx: i, first, dur, accent: props.accent };
    if (s.kind === "card") {
      if (st === "paper") return <PaperCard c={s.card!} {...a} />;
      if (st === "kinetic") return <KineticCard c={s.card!} {...a} />;
      if (st === "board") return <BoardCard c={s.card!} {...a} />;
      if (st === "radar") return <RadarCard c={s.card!} {...a} bgSrc={props.bgSrc} />;
      return <CardScene c={s.card!} dur={dur} idx={i} first={first} />;
    }
    if (st === "paper") return <PaperPhoto s={s} {...a} />;
    if (st === "kinetic") return <KineticPhoto s={s} {...a} />;
    if (st === "board") return <BoardPhoto s={s} {...a} />;
    if (st === "radar") return <RadarPhoto s={s} {...a} bgSrc={props.bgSrc} />;
    return <PhotoScene s={s} dur={dur} idx={i} accent={props.accent} first={first} />;
  };
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <style>{fontFaces}</style>
      {props.scenes.map((s, i) => {
        const from = fr(s.start);
        const dur = Math.max(1, fr(s.end) - from);
        return (
          <Sequence key={i} from={from} durationInFrames={dur}>
            {renderScene(s, i, dur, i === 0)}
          </Sequence>
        );
      })}
      <Sequence from={fr(props.outro.start)} durationInFrames={total - loopFrames - fr(props.outro.start)}>
        <Outro o={props.outro} accent={props.accent} style={st} bgSrc={props.bgSrc} />
      </Sequence>
      {/* loop back to the first frame so the short replays seamlessly */}
      <Sequence from={total - loopFrames} durationInFrames={loopFrames}>
        {renderScene(props.scenes[0], 0, loopFrames, true)}
      </Sequence>
      <Subtitles pages={pages} look={subLook(st, props.accent)} keywords={kw} />
      <Audio src={staticFile(props.audio)} />
    </AbsoluteFill>
  );
};
