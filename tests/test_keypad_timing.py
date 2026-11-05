"""Host characterization of the unmodified integrated keypad routine.

Run: python3 tests/test_keypad_timing.py
Requires a C99 compiler (CC, default cc). No STM32 HAL installation is needed.
"""
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <setjmp.h>
typedef int GPIO_TypeDef;
typedef enum { GPIO_PIN_RESET, GPIO_PIN_SET } GPIO_PinState;
static GPIO_TypeDef port;
static GPIO_TypeDef *rowPort[4] = {&port, &port, &port, &port};
static GPIO_TypeDef *colPort[3] = {&port, &port, &port};
static const uint16_t rowPin[4] = {1, 2, 4, 8};
static const uint16_t colPin[3] = {16, 32, 64};
static const char keyMap[4][3] = {
    {'1','2','3'}, {'4','5','6'}, {'7','8','9'}, {'*','0','#'}
};
static uint32_t tick, release_at;
static int pressed, active_row = -1;
static jmp_buf budget;
static void HAL_GPIO_WritePin(GPIO_TypeDef *p, uint16_t pin, GPIO_PinState state) {
    (void)p;
    for (int i = 0; i < 4; ++i) {
        if (pin == rowPin[i]) {
            if (state == GPIO_PIN_RESET) active_row = i;
            else if (active_row == i) active_row = -1;
        }
    }
}
static GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *p, uint16_t pin) {
    (void)p;
    return pressed && active_row == 0 && pin == colPin[0] && tick < release_at
        ? GPIO_PIN_RESET : GPIO_PIN_SET;
}
static void HAL_Delay(uint32_t ms) {
    tick += ms;
    if (tick >= 2000) longjmp(budget, 1);
}
/* ROUTINE */
int main(int argc, char **argv) {
    if (argc != 3) return 2;
    pressed = atoi(argv[1]);
    release_at = (uint32_t)strtoul(argv[2], NULL, 10);
    if (setjmp(budget)) {
        printf("BLOCKED %u\n", (unsigned)tick);
        return 0;
    }
    unsigned key = (unsigned char)Keypad_GetKey();
    printf("RETURN %u %u\n", key, (unsigned)tick);
    return 0;
}
'''


class KeypadTiming(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (ROOT / 'alpha code.txt').read_text()
        start = source.index('static char Keypad_GetKey(void)\n{')
        end = source.index('\nstatic void Servo_SetPosition', start)
        routine = source[start:end]
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cfile = Path(cls.tmp.name) / 'keypad.c'
        cls.exe = Path(cls.tmp.name) / 'keypad'
        cfile.write_text(HARNESS.replace('/* ROUTINE */', routine))
        subprocess.run(shlex.split(os.environ.get('CC', 'cc')) + [
            '-std=c99', '-Wall', '-Wextra', '-Werror', str(cfile), '-o', str(cls.exe)
        ], check=True)

    def run_case(self, pressed, release_at):
        return subprocess.check_output(
            [str(self.exe), str(pressed), str(release_at)], text=True, timeout=5
        ).strip().split()

    def test_idle_returns_after_four_row_delays(self):
        self.assertEqual(self.run_case(0, 0), ['RETURN', '0', '8'])

    def test_short_pulse_rejected_by_debounce(self):
        self.assertEqual(self.run_case(1, 10), ['RETURN', '0', '28'])

    def test_key_return_waits_until_release(self):
        result = self.run_case(1, 500)
        self.assertEqual(result[:2], ['RETURN', str(ord('1'))])
        self.assertGreaterEqual(int(result[2]), 530)

    def test_held_key_exhausts_budget_without_return(self):
        result = self.run_case(1, 0xffffffff)
        self.assertEqual(result[0], 'BLOCKED')
        self.assertGreaterEqual(int(result[1]), 2000)


if __name__ == '__main__':
    unittest.main(verbosity=2)
