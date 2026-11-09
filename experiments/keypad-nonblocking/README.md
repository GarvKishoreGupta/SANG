# Experimental non-blocking keypad scanner

This is a proposed replacement for Keypad_GetKey() in [alpha code.txt](../../alpha%20code.txt), not an integrated or hardware-validated firmware release. The original uploaded source is unchanged.

## Design

The routine selects one row, returns to its caller, and samples that row on a later call once at least 2 ms have elapsed. A complete four-row frame is used to form a candidate key. A candidate must be observed unchanged for at least 20 ms at frame boundaries before generating an event. A stable release is required before another event; observed multiple keys inhibit events until release.

There are no HAL_Delay calls or waits for GPIO transitions. Each invocation performs at most five GPIO reads/writes. A held key therefore does not trap the foreground loop inside this routine.

This changes the event semantics: a key is reported after debounced press, rather than after release as in the original routine.

## Try it in a working copy

1. Retain the existing keypad pin arrays, key map, and initialization from alpha code.txt.
2. Replace only the definition of Keypad_GetKey() with the contents of keypad_nonblocking.inc; do not keep both definitions.
3. Call it repeatedly from the existing foreground loop. It uses HAL_GetTick and the existing HAL GPIO calls. The static state assumes one foreground caller and is initialized once after reset.
4. Rebuild the full STM32 project and validate on the actual keypad before adopting the change.

The repository still lacks the complete STM32 build project. This proposal has not been compiled against STM32 HAL or flashed.

## Host validation

Run from the repository root:

```sh
python3 experiments/keypad-nonblocking/test_keypad_nonblocking.py
```

Requirements: Python 3 and a C99 compiler; CC defaults to cc. The test compiles the proposed routine with -Wall -Wextra -Werror against simulated GPIO and ticks.

The suite contains fifteen test methods. The original nine cover idle, continuous hold, release/repress, brief bounce, bounce followed by hold, multiple-key lockout, sliding between keys without release, 32-bit tick wrap, and 10 ms polling. Three additional methods define 72 subcases:

- Each of the twelve row/column positions held at 1 ms polling (12 cases).
- Each key released and pressed again at 10 ms polling (12 cases).
- Each key held or released/repressed with repeating 1, 7, 2, 13, 3, 5, 1, 11 ms polling intervals, both before and across 32-bit tick wrap (48 cases).

The new cases assert the expected key identity, exactly one event per press, an initial event between 20 and 199 simulated milliseconds, and no second event before the repress at 400 ms. These bounds describe the supplied test inputs, not a hardware latency guarantee. The mask bit for a key is its row-major position in the existing 4-by-3 key map.

A GPIO-operation budget checks bounded work in every simulated call. The harness does not provide HAL_Delay, so a newly introduced call to it fails compilation.

Three further methods characterize slow polling: all twelve keys at 20, 50 and 100 ms intervals (36 subcases), a release/repress missed at 100 ms polling, and a brief press detected at 1 ms but missed at 200 ms polling.

Validation status: on 9 November 2026, all fifteen test methods passed, including the previous 72 subcases and the 36 slow-polling subcases. The harness compiled with GCC 14.2.0 using `-std=c99 -Wall -Wextra -Werror`. These are simulated GPIO/tick checks, not STM32 HAL compilation or hardware validation.

### Observed slow-polling limits

With a key held from simulated time zero, the first event occurred at:

| Poll interval | First event |
| --- | --- |
| 20 ms | 160 ms |
| 50 ms | 400 ms |
| 100 ms | 800 ms |

These results were checked for all twelve keys. Each full frame takes four polls; in these cases the candidate is accepted at the second frame boundary.

At 100 ms polling, the supplied release/repress scenario (pressed before 200 ms, released from 200 to 399 ms, pressed again at 400 ms) produces only one event, at 800 ms. The release does not form a stable empty frame. Separately, a press from 50 to 149 ms is detected with 1 ms polling but is entirely missed when calls occur only every 200 ms.

These tests intentionally assert missed-input behavior to characterize a limitation; passing them does not make slow polling acceptable. Integration must establish a suitable maximum interval between calls, including worst-case peripheral work, and verify the intended shortest press/release on hardware. The current source still calls blocking peripheral routines before keypad scanning.


## Limits and hardware checklist

- Debouncing is sampled per complete frame, not continuous observation. Short transitions between samples may be missed.
- At 10 ms polling, a full frame takes approximately 40 ms; debounce decisions occur at those frame boundaries. Slower polling increases latency and can miss brief presses/releases.
- Other blocking routines in SANG, including the buzzer and some peripheral transfers, are not changed by this proposal.
- The mock does not model electrical settling, key ghosting, or output contention. The scan retains the original push-pull row convention. Multi-key hardware use needs electrical review; software lockout does not prevent contention.
- Verify all twelve keys and row/column wiring on hardware.
- Check held keys, quick releases/represses, and bouncing contacts while door/garage timers and sensors run.
- Confirm acceptable latency with OLED updates and the buzzer active.
- Record hardware results before promoting this experiment into the integrated source.

The earlier [characterization PR](https://github.com/GarvKishoreGupta/SANG/pull/1) captures the original blocking behavior. These tests validate the proposed routine separately.
