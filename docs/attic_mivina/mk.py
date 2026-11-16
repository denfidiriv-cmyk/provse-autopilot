import json, sys, os
A = "/tmp/claude-0/-home-claude/1aa8b6ad-0ff9-5c05-a29e-50e8238d6250/scratchpad/miv"
M = "/home/claude/provse-autopilot/assets_cache/music_cc/"
def mk(job, theme, beats, musics, tail=.8, **kw):
    os.makedirs(f"{A}/full/{job}", exist_ok=True)
    cfg = {"job": f"{A}/full/{job}", "img": A + "/img", "vid": A + "/vid", "theme": theme, "tail": tail, "beats": beats,
           "musics": [[i, M + f, o, v] for i, f, o, v in musics], **kw}
    json.dump(cfg, open(f"{A}/full/{job}/chapter.json", "w"), ensure_ascii=False, indent=1)
    json.dump(cfg, open(os.path.join(os.path.dirname(__file__), f"{job}.json"), "w"), ensure_ascii=False, indent=1)
def B(theme):
    def b(anc, typ, **p):
        return [anc, typ, {"theme": theme, **p}]
    return b
