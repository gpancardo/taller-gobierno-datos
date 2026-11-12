#!/usr/bin/env bash
# Genera salida/pilares.mp4 (con voz), pilares_sin_voz.mp4, narracion.mp3 y pilares.srt.
# Requiere: uv, ffmpeg y las fuentes de ../laboratorio/fuentes instaladas en el sistema.
set -euo pipefail
cd "$(dirname "$0")"
[ -d .venv ] || { uv venv -q .venv && uv pip install -q --python .venv manim edge-tts; }

.venv/bin/python pilares.py voz
.venv/bin/manim -qh --fps 30 --disable_caching --media_dir salida/media pilares.py Pilares
.venv/bin/python pilares.py srt

ffmpeg -nostdin -v error -y -i salida/media/videos/pilares/1080p30/Pilares.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5 -ar 48000 -c:a aac -b:a 192k salida/pilares.mp4
ffmpeg -nostdin -v error -y -i salida/pilares.mp4 -an -c:v copy salida/pilares_sin_voz.mp4
ffmpeg -nostdin -v error -y -i salida/pilares.mp4 -vn -c:a libmp3lame -q:a 2 salida/narracion.mp3
echo "listo: salida/pilares.mp4"
