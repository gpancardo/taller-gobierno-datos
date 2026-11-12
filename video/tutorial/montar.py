"""Arma el video del paso a paso: capturas reales del laboratorio + voz.

    node capturar.mjs                      # captura el laboratorio
    ../.venv/bin/python montar.py          # voz, clips, subtítulos y mp4
"""
import asyncio, json, subprocess
from pathlib import Path

import edge_tts

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent / "salida"
TMP = SALIDA / "tutorial"
TMP.mkdir(parents=True, exist_ok=True)
VOZ, RITMO, COLCHON = "es-MX-DaliaNeural", "+8%", 0.6
pasos = json.loads((AQUI / "pasos.json").read_text())


def duracion(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(f)], capture_output=True, text=True, check=True)
    return float(r.stdout)


def ffmpeg(*a):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *a], check=True)


def hms(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


async def voz(p):
    await edge_tts.Communicate(p["texto"], VOZ, rate=RITMO).save(str(TMP / f"{p['id']}.mp3"))

async def todas():
    for p in pasos:
        await voz(p)
asyncio.run(todas())

lista, srt, t = [], [], 0.0
for i, p in enumerate(pasos, 1):
    mp3 = TMP / f"{p['id']}.mp3"
    d = duracion(mp3) + COLCHON
    clip = TMP / f"{p['id']}.mp4"
    # imagen fija + audio; el colchón final es silencio
    ffmpeg("-loop", "1", "-framerate", "30", "-i", str(AQUI / "capturas" / f"{p['id']}.png"),
           "-i", str(mp3), "-t", f"{d:.3f}", "-af", f"apad=pad_dur={COLCHON}",
           "-vf", "scale=1920:1080,format=yuv420p,fade=t=in:d=0.25",
           "-c:v", "libx264", "-r", "30", "-c:a", "aac", "-ar", "48000", str(clip))
    lista.append(f"file '{clip.name}'")
    srt.append(f"{i}\n{hms(t + 0.1)} --> {hms(t + d - COLCHON)}\n{p['sub']}\n")
    t += d
(TMP / "lista.txt").write_text("\n".join(lista))
ffmpeg("-f", "concat", "-safe", "0", "-i", str(TMP / "lista.txt"),
       "-af", "loudnorm=I=-16:TP=-1.5", "-c:v", "libx264", "-c:a", "aac", "-b:a", "192k",
       str(SALIDA / "tutorial_laboratorio.mp4"))
(SALIDA / "tutorial_laboratorio.srt").write_text("\n".join(srt), encoding="utf-8")
ffmpeg("-i", str(SALIDA / "tutorial_laboratorio.mp4"), "-an", "-c:v", "copy",
       str(SALIDA / "tutorial_laboratorio_sin_voz.mp4"))
print(f"listo: {t:.1f} s")
