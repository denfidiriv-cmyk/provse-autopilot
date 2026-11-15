import subprocess
A = "/tmp/claude-0/-home-claude/1aa8b6ad-0ff9-5c05-a29e-50e8238d6250/scratchpad/attic/full"
cs = [f"{A}/c{i}/final.mp4" for i in range(8)]
dur = [float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",c])) for c in cs]
X = .3
ins = sum([["-i", c] for c in cs], [])
fl, v, a, off = [], "[0:v]", "[0:a]", 0.0
starts = [0.0]
for i in range(1, 8):
    off += dur[i - 1] - X
    starts.append(off)
    fl.append(f"{v}[{i}:v]xfade=transition=fade:duration={X}:offset={off:.3f}[v{i}]")
    fl.append(f"{a}[{i}:a]acrossfade=d={X}[a{i}]")
    v, a = f"[v{i}]", f"[a{i}]"
fl.append(f"{a}loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[ao]")
subprocess.run(["ffmpeg","-v","error","-y",*ins,"-filter_complex",";".join(fl),"-map",v,"-map","[ao]","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{A}/attic_energy_full.mp4"],check=True)
print("starts", [f"{int(s//60):02d}:{int(s%60):02d}" for s in starts], "total", sum(dur) - 7 * X)
