#!/usr/bin/env python3
"""
multicam.py - turn one talking-head clip into a hard-cut "multi-camera" edit.

Follows the shot list from the prompt:
  00:00-01.2 original | 01.2-02.4 left 45 | 02.4-03.6 high-angle MCU
  03.6-04.8 right 45  | 04.8-06.0 extreme CU (eyes) | 06.0-07.2 low-angle CU
  07.2-08.6 over-the-shoulder (behind left) | 08.6-10.0 original

Guarantees (by construction):
  * Audio is stream-copied from the source - speech, timing and lip sync untouched.
  * Only hard cuts: cut points are contiguous, no fades, blends or zoom animation.
  * Each shot is a static crop of the source (no motion, no AI generation), so the
    person, room, lighting and clothing are pixel-identical to the source.

Limitation: a crop cannot change the real viewing angle. "Left 45", "high",
"low" and "over-the-shoulder" are approximated with different framing offsets.
True new angles need a generative/3D video model.

Usage:
  python3 multicam.py input.mp4 output.mp4
  python3 multicam.py input.mp4 output.mp4 --face-x 0.5 --face-y 0.33
  python3 multicam.py input.mp4 output.mp4 --shots my_shots.json
"""
import argparse, json, subprocess, sys

# (start, end, zoom, x_center, y_center, label)
# x/y centres are offsets relative to the face position (fractions of frame).
DEFAULT_SHOTS = [
    (0.0, 1.2, 1.00,  0.00,  0.00, "original medium"),
    (1.2, 2.4, 1.25, -0.10,  0.00, "left 45 (approx)"),
    (2.4, 3.6, 1.60,  0.00, -0.04, "high-angle medium close-up (approx)"),
    (3.6, 4.8, 1.25,  0.10,  0.00, "right 45 (approx)"),
    (4.8, 6.0, 2.80,  0.00,  0.00, "extreme close-up eyes/upper face"),
    (6.0, 7.2, 1.80,  0.00,  0.05, "low-angle close-up (approx)"),
    (7.2, 8.6, 1.45,  0.14,  0.00, "over-the-shoulder behind left (approx)"),
    (8.6, 10.0, 1.00, 0.00,  0.00, "original medium"),
]


def probe(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height:format=duration",
        "-of", "json", path])
    d = json.loads(out)
    return d["streams"][0]["width"], d["streams"][0]["height"], float(d["format"]["duration"])


def even(n):
    return max(2, int(n) // 2 * 2)


def build_filter(shots, W, H, dur, fx, fy):
    parts, labels = [], []
    for i, (a, b, zoom, dx, dy, _) in enumerate(shots):
        if a >= dur:
            break
        b = min(b, dur)
        cw, ch = even(W / zoom), even(H / zoom)
        # centre on face (+ per-shot offset), clamped inside the frame
        cx = (fx + dx) * W
        cy = (fy + dy) * H
        x = int(min(max(cx - cw / 2, 0), W - cw))
        y = int(min(max(cy - ch / 2, 0), H - ch))
        crop = "" if zoom == 1.0 else f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,"
        parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS,{crop}setsar=1[v{i}]")
        labels.append(f"[v{i}]")
    parts.append("".join(labels) + f"concat=n={len(labels)}:v=1:a=0[out]")
    return ";".join(parts), len(labels)


def main():
    p = argparse.ArgumentParser(description="Hard-cut multi-camera reframer")
    p.add_argument("input")
    p.add_argument("output")
    p.add_argument("--face-x", type=float, default=0.5, help="face centre, 0-1 across (default 0.5)")
    p.add_argument("--face-y", type=float, default=0.38, help="face centre, 0-1 down (default 0.38)")
    p.add_argument("--shots", help="JSON list of [start,end,zoom,dx,dy,label] to override the shot list")
    a = p.parse_args()

    shots = [tuple(s) for s in json.load(open(a.shots))] if a.shots else DEFAULT_SHOTS
    W, H, dur = probe(a.input)
    flt, n = build_filter(shots, W, H, dur, a.face_x, a.face_y)

    cmd = ["ffmpeg", "-y", "-i", a.input, "-filter_complex", flt,
           "-map", "[out]", "-map", "0:a?", "-c:a", "copy",
           "-c:v", "libx264", "-crf", "16", "-preset", "medium",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.output]
    print(f"{W}x{H}, {dur:.2f}s, {n} shots", file=sys.stderr)
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()

