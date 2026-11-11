"""Explore cold-start, single-press timing; this is not a hardware acceptance test."""
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
    source = replace_once(HARNESS, "if(argc!=5)", "if(argc!=7)")
    source = replace_once(
        source, "unsigned key_mask=1U<<key_index;",
        "unsigned key_mask=1U<<key_index; "
        "unsigned onset=atoi(argv[5]), duration=atoi(argv[6]);",
    )
    source = replace_once(source, "t>=50 && t<150",
                          "t>=onset && t<onset+duration")
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
                        str(onset), str(duration),
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


if __name__ == "__main__":
    main()
