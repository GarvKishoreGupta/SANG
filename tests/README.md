# Host keypad timing characterization

Run from the repository root:

```sh
python3 tests/test_keypad_timing.py
```

Requirements: Python 3 and a C99 compiler, default `cc`. Set `CC` to choose another compiler.

The script extracts the actual `Keypad_GetKey()` definition from `alpha code.txt`, compiles it with `-std=c99 -Wall -Wextra -Werror`, and supplies simulated GPIO and HAL delay functions. It does not copy a separately maintained implementation of the keypad routine. Compilation outputs are temporary.

## Cases

| Input | Expected current behavior |
| --- | --- |
| No key | Returns no character after four 2 ms row delays |
| Pulse ending at 10 ms | Rejected by the debounce recheck; no character returned |
| Row 1 / column 1 held until 500 ms | Returns '1' only after release and the final 30 ms delay |
| Row 1 / column 1 continuously held | Does not return before the mock reaches its 2000 ms budget |

The held-key case deliberately interrupts execution using a test-only budget. A passing test means the existing blocking behavior was reproduced; it does not mean the blocking behavior has been fixed.

## Implication and limits

The integrated main loop calls this routine before its door-relock, room-light, garage-close, and RFID checks. Those checks cannot execute while this call waits for release. This is a source-level consequence; the test does not measure actual actuator timing.

This is a host characterization test, not a firmware build or hardware simulation. It models one key, deterministic GPIO levels, and elapsed HAL delays. It does not validate electrical behavior, multiple keys, all bounce patterns, interrupt behavior, real wall-clock timing, or other subsystems.

A future non-blocking scan change should replace the held-key expectation with bounded-return and one-event-per-press checks, and add release/repress, bounce, and timer-wrap cases before hardware validation.
