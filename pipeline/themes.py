"""Каталог стилів оформлення: 30 палітр × 5 варіантів подачі = 150 стилів.

Стиль не прив'язаний до каналу. Під кожну новину Claude обирає з короткого списку той стиль,
що найкраще пасує до історії, а код не дає повторювати стилі, використані нещодавно.
"""
from __future__ import annotations

import random

# назва: (опис для Claude, bg, fg, sub, acc, acc2, теги)
PALETTES = {
    "newsroom_red": ("червоно-чорний терміновий випуск новин", "#141414", "#ffffff", "#bdbdbd", "#e8352e", "#ffd23f", "urgent news politics"),
    "blueprint": ("синє технічне креслення з неоном", "#0b1f3a", "#eaf6ff", "#7fd3ff", "#ff8a3d", "#4be08a", "tech home energy explain"),
    "chalkboard": ("зелена крейдяна дошка в рамці", "#1f2d25", "#f3efe2", "#b8c4bb", "#ffc93c", "#58c27d", "food school prices explain"),
    "sunny_cards": ("сонячний жовтий з картками-наліпками", "#ffe9b8", "#1d2a3a", "#8a5a20", "#e8463c", "#2b7de9", "good news kids summer"),
    "old_paper": ("старий папір, газетна верстка", "#efe6d2", "#1b1b1b", "#6b5a3e", "#d4372c", "#1f5aa6", "history politics investigation"),
    "money_green": ("купюрна зелень з гільйошем", "#0f3b2e", "#f2ecd8", "#9cc3a9", "#e8c25a", "#ffffff", "money economy salary"),
    "receipt": ("білий касовий чек, моно-шрифт", "#f7f7f2", "#202020", "#777777", "#d93a2b", "#2c7a4b", "prices economy shopping"),
    "stadium_night": ("нічний стадіон, прожектори", "#071226", "#ffffff", "#8fb3ff", "#39ff88", "#ffcc00", "sport match victory"),
    "scoreboard": ("LED-табло, жовті цифри", "#0a0a0a", "#ffd400", "#9a8a2a", "#ff3b30", "#ffffff", "sport score numbers"),
    "asphalt": ("асфальт і жовта дорожня розмітка", "#2a2c30", "#ffffff", "#b0b4ba", "#ffcf1a", "#ff5a36", "cars road fuel drivers"),
    "dashboard": ("приладова панель авто, неон", "#0d0f14", "#e8f1ff", "#6c7a91", "#00e0ff", "#ff2e63", "cars tech speed"),
    "ocean": ("глибокий океан, бірюза", "#03263a", "#e6fbff", "#7cc7d9", "#2ee6c5", "#ffd166", "nature sea animals good"),
    "forest": ("лісова зелень, природа", "#16301f", "#f1f7ec", "#a6c7a0", "#9be564", "#ffb347", "nature animals ecology good"),
    "space": ("космос, зорі, фіолет", "#0b0620", "#f2ecff", "#9f8fd6", "#ff6ad5", "#5ee7ff", "space science discovery"),
    "lab_white": ("біла лабораторія, наука", "#f4f7fb", "#10213a", "#5b6b82", "#2f6bff", "#00b894", "science health discovery"),
    "kitchen_warm": ("тепла кухня, теракота", "#f6e7d7", "#3a2418", "#8c6a54", "#d9572b", "#4f8a3c", "food recipe home"),
    "market_bright": ("яскравий ринок, фрукти", "#fff4e0", "#26201a", "#8a7a63", "#ff4f5e", "#2bb673", "food prices market"),
    "winter_frost": ("морозний ранок, крижаний", "#e9f3fb", "#12263a", "#6a8aa6", "#2d8cff", "#ff6b6b", "weather winter energy home"),
    "storm": ("штормове небо, попередження", "#1b2333", "#f5f7fa", "#8b97ab", "#ffb020", "#5ac8fa", "weather warning nature"),
    "night_city": ("нічне місто, вогні", "#10101e", "#f5f5ff", "#8888aa", "#ffcc33", "#ff4dc4", "city energy lifestyle"),
    "retro_80s": ("ретро 80-х, неонова сітка", "#1a0b2e", "#fff3ff", "#b48ad9", "#ff2e97", "#00f0ff", "fun nostalgia music"),
    "pop_comic": ("комікс поп-арт, точки", "#ffde3b", "#111111", "#5a4a00", "#ff2d55", "#1e6bff", "fun facts funny"),
    "minimal_white": ("мінімалізм, багато повітря", "#ffffff", "#111111", "#888888", "#ff4d00", "#111111", "explain facts clean"),
    "noir": ("нуар, чорно-біле з червоним", "#0c0c0c", "#f0f0f0", "#8a8a8a", "#ff2b2b", "#f0f0f0", "crime investigation politics"),
    "parliament": ("строгий синій, державний", "#0e2347", "#f4f6fb", "#9fb0cf", "#ffd23f", "#e8352e", "politics law government"),
    "map_room": ("штабна карта, хакі", "#2b2f22", "#efe9d6", "#a8a284", "#e85d2a", "#d9c35b", "politics geography regions"),
    "sunrise": ("світанок, рожево-помаранчевий", "#ffe1d0", "#2b1d2f", "#8a6a7a", "#ff6a3d", "#7b5cff", "good news hope lifestyle"),
    "ice_cream": ("пастель, морозиво", "#fdf0f6", "#2a2140", "#8d7fa8", "#ff5fa2", "#38c6b2", "kids fun food good"),
    "gold_luxury": ("чорне золото, преміум", "#111111", "#f6efe0", "#a8996f", "#e8c25a", "#ffffff", "money records luxury"),
    "eco_paper": ("крафтовий картон, еко", "#d9c4a0", "#2b2116", "#6f5a3c", "#3f8f3a", "#c4452b", "ecology home diy"),
}

# варіанти подачі: шрифт заголовків, фон, рамка карток, плашка субтитрів
VARIANTS = {
    "bold": dict(disp="Osw", deco="grid", card="sticker", cap="dark"),
    "editorial": dict(disp="PF", deco="paper", card="frame", cap="bar"),
    "mono": dict(disp="JB", deco="lines", card="flat", cap="box"),
    "hand": dict(disp="Cav", deco="dots", card="tilt", cap="dark"),
    "clean": dict(disp="Osw", deco="none", card="round", cap="pill"),
}

DECO = {
    "grid": "background-image:linear-gradient({line} 2px,transparent 2px),linear-gradient(90deg,{line} 2px,transparent 2px);background-size:120px 120px",
    "paper": "background-image:radial-gradient({line} 1px,transparent 1px);background-size:14px 14px",
    "lines": "background-image:repeating-linear-gradient(0deg,{line} 0 2px,transparent 2px 48px)",
    "dots": "background-image:radial-gradient({line} 3px,transparent 3px);background-size:40px 40px",
    "none": "background:radial-gradient(1100px 900px at 50% 30%,rgba(255,255,255,.07),transparent 70%)",
}
CARD = {
    "sticker": "border:7px solid {fg};border-radius:28px;box-shadow:14px 16px 0 {fg}",
    "frame": "border:3px solid {sub};outline:10px solid {bg};outline-offset:-16px;border-radius:4px",
    "flat": "border:none;border-radius:0",
    "tilt": "border:14px solid #fff;border-bottom-width:60px;transform:rotate(-2deg);box-shadow:0 20px 40px rgba(0,0,0,.35)",
    "round": "border:none;border-radius:40px;box-shadow:0 24px 60px rgba(0,0,0,.35)",
}
CAP = {
    "dark": "background:rgba(6,10,18,.86);border-radius:28px;padding:14px 22px 18px",
    "bar": "background:{acc};border-radius:6px;padding:10px 22px 14px",
    "box": "background:{bg};border:4px solid {acc};border-radius:0;padding:12px 22px 16px",
    "pill": "background:rgba(6,10,18,.86);border-radius:999px;padding:14px 36px 18px",
}

ALL = [f"{p}__{v}" for p in PALETTES for v in VARIANTS]  # 150 стилів


def _dark(hexc: str) -> bool:
    h = hexc.lstrip("#"); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return (0.299 * r + 0.587 * g + 0.114 * b) < 140


def theme(name: str) -> dict:
    pal, var = name.split("__") if "__" in name else (name, "bold")
    if pal not in PALETTES:
        pal = "blueprint"
    if var not in VARIANTS:
        var = "bold"
    _, bg, fg, sub, acc, acc2, _ = PALETTES[pal]
    v = VARIANTS[var]
    dark = _dark(bg)
    line = "rgba(255,255,255,.08)" if dark else "rgba(0,0,0,.07)"
    fmt = dict(bg=bg, fg=fg, sub=sub, acc=acc, acc2=acc2, line=line)
    cap_fg = "#111111" if v["cap"] == "bar" and not _dark(acc) else "#ffffff"
    return dict(bg=bg, fg=fg, sub=sub, acc=acc, acc2=acc2, disp=v["disp"],
                deco=DECO[v["deco"]].format(**fmt), card=CARD[v["card"]].format(**fmt), cap=CAP[v["cap"]].format(**fmt),
                capfg=cap_fg, hl=acc2 if v["cap"] == "bar" else ("#ffd166" if dark else acc),
                stroke="0px" if v["cap"] in ("bar", "box") else "5px")


def shortlist(recent: list[str], n: int = 14, seed: int | None = None) -> list[str]:
    """Різноманітний короткий список для Claude: без нещодавніх палітр і варіантів підряд."""
    rnd = random.Random(seed)
    recent_pal = {r.split("__")[0] for r in recent[-6:]}
    pals = [p for p in PALETTES if p not in recent_pal]
    rnd.shuffle(pals)
    last_var = recent[-1].split("__")[1] if recent else ""
    out = []
    for p in pals[:n]:
        vars_ = [v for v in VARIANTS if v != last_var]
        out.append(f"{p}__{rnd.choice(vars_)}")
    return out


def describe(names: list[str]) -> str:
    vdesc = {"bold": "жирні заголовки", "editorial": "журнальна верстка з засічками", "mono": "моноширинний технічний",
             "hand": "рукописний, живий", "clean": "чистий мінімальний"}
    return "\n".join(f"- {n}: {PALETTES[n.split('__')[0]][0]}; {vdesc[n.split('__')[1]]}" for n in names)
