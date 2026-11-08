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

The suite contains twelve test methods. The original nine cover idle, continuous hold, release/repress, brief bounce, bounce followed by hold, multiple-key lockout, sliding between keys without release, 32-bit tick wrap, and 10 ms polling. Three additional methods define 72 subcases:

- Each of the twelve row/column positions held at 1 ms polling (12 cases).
- Each key released and pressed again at 10 ms polling (12 cases).
- Each key held or released/repressed with repeating 1, 7, 2, 13, 3, 5, 1, 11 ms polling intervals, both before and across 32-bit tick wrap (48 cases).

The new cases assert the expected key identity, exactly one event per press, an initial event between 20 and 199 simulated milliseconds, and no second event before the repress at 400 ms. These bounds describe the supplied test inputs, not a hardware latency guarantee. The mask bit for a key is its row-major position in the existing 4-by-3 key map.

A GPIO-operation budget checks bounded work in every simulated call. The harness does not provide HAL_Delay, so a newly introduced call to it fails compilation.

Validation status: on 8 November 2026, all twelve test methods passed, including all 72 added subcases, using the exact scanner and harness from commit [b66022d](https://github.com/GarvKishoreGupta/SANG/commit/b66022db23a496ca9738cd81e5c3584637f90c48). The harness compiled with GCC 14.2.0 using `-std=c99 -Wall -Wextra -Werror`. The execution environment had been unavailable on 7 November; this run resolves that host-test gap. These are simulated GPIO/tick checks, not STM32 HAL compilation or hardware validation.

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
