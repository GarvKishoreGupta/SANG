"""Explore sampled press/release timing; not a hardware acceptance test."""
from pathlib import Path
import json
import os
import shlex
import subprocess
import tempfile

from test_keypad_nonblocking import HARNESS


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError("Harness changed; review the phase-sweep adaptation")
    return source.replace(old, new)


def main():
    root = Path(__file__).resolve().parent
    source = replace_once(HARNESS, "if(argc!=5)", "if(argc!=8)")
    source = replace_once(
        source, "unsigned key_mask=1U<<key_index;",
        "unsigned key_mask=1U<<key_index; "
        "unsigned onset=atoi(argv[5]), duration=atoi(argv[6]), gap=atoi(argv[7]);",
    )
    source = replace_once(source, "t>=50 && t<150",
                          "t>=onset && t<onset+duration")
    source = replace_once(
        source, "tick=start+t; calls=0;",
        "if(scenario==8 && ((t>=onset && t<onset+duration) || "
        "(t>=onset+duration+gap && t<onset+2*duration+gap))) { mask=key_mask; }\n        "
        "tick=start+t; calls=0;",
    )
    source = replace_once(source, "/* SCANNER */",
                          (root / "keypad_nonblocking.inc").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        c = Path(tmp) / "phase.c"
        exe = Path(tmp) / "phase"
        c.write_text(source)
        subprocess.run(shlex.split(os.environ.get("CC", "cc")) + [
            "-std=c99", "-Wall", "-Wextra", "-Werror", str(c), "-o", str(exe)
        ], check=True)
        for duration in (50, 100, 200):
            missed = late = 0
            latencies = []
            for index, key in enumerate("123456789*0#"):
                for onset in range(40):
                    lines = subprocess.check_output([
                        str(exe), "7", "0", "10", str(index),
                        str(onset), str(duration), "0",
                    ], text=True, timeout=5).splitlines()
                    if not lines:
                        missed += 1
                        continue
                    if len(lines) != 1 or lines[0].split()[0] != key:
                        raise RuntimeError("Unexpected event identity or count")
                    event_time = int(lines[0].split()[1])
                    latencies.append(event_time - onset)
                    late += event_time >= onset + duration
            print(json.dumps({
                "press_ms": duration, "cases": 480, "missed": missed,
                "event_at_or_after_release": late,
                "latency_ms": [min(latencies), max(latencies)] if latencies else None,
            }))

        # Two 200 ms presses of the same key, with a variable release gap.
        # Each case still begins with a fresh scanner; this is not an
        # arbitrary-length or mixed-key sequence test.
        for gap in (50, 100, 200):
            counts = {0: 0, 1: 0, 2: 0}
            for index, key in enumerate("123456789*0#"):
                for onset in range(40):
                    lines = subprocess.check_output([
                        str(exe), "8", "0", "10", str(index),
                        str(onset), "200", str(gap),
                    ], text=True, timeout=5).splitlines()
                    if len(lines) > 2 or any(line.split()[0] != key for line in lines):
                        raise RuntimeError("Unexpected repeated-press event identity/count")
                    counts[len(lines)] += 1
            print(json.dumps({
                "sequence": "two_same_key_presses", "press_ms": 200,
                "release_ms": gap, "cases": 480, "event_counts": counts,
            }))


if __name__ == "__main__":
    main()
