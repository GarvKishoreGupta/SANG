"""Host tests for the experimental scanner; no HAL or hardware required."""
from pathlib import Path
import os
import shlex
import subprocess
import tempfile
import unittest

HARNESS = r'''
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
typedef int GPIO_TypeDef;
typedef enum { GPIO_PIN_RESET, GPIO_PIN_SET } GPIO_PinState;
static GPIO_TypeDef port;
static GPIO_TypeDef *rowPort[4] = {&port,&port,&port,&port};
static GPIO_TypeDef *colPort[3] = {&port,&port,&port};
static const uint16_t rowPin[4] = {1,2,4,8};
static const uint16_t colPin[3] = {16,32,64};
static const char keyMap[4][3] = {
    {'1','2','3'}, {'4','5','6'}, {'7','8','9'}, {'*','0','#'}
};
static uint32_t tick;
static unsigned mask, calls;
static int active = -1;
static uint32_t HAL_GetTick(void) { return tick; }
static void HAL_GPIO_WritePin(GPIO_TypeDef *p, uint16_t pin, GPIO_PinState v) {
    (void)p; ++calls;
    for (int r=0;r<4;++r) if (rowPin[r]==pin) {
        if (v==GPIO_PIN_RESET) active=r;
        else if(active==r) active=-1;
    }
}
static GPIO_PinState HAL_GPIO_ReadPin(GPIO_TypeDef *p, uint16_t pin) {
    (void)p; ++calls;
    for (int c=0;c<3;++c)
        if (colPin[c]==pin && active>=0 && (mask & (1U<<(3*active+c))))
            return GPIO_PIN_RESET;
    return GPIO_PIN_SET;
}
/* SCANNER */
int main(int argc, char **argv) {
    if(argc!=4) return 2;
    int scenario=atoi(argv[1]);
    uint32_t start=(uint32_t)strtoul(argv[2],NULL,10);
    unsigned step=(unsigned)strtoul(argv[3],NULL,10);
    for(unsigned t=0;t<1000;t+=step) {
        mask=0;
        if(scenario==1) mask=1; /* hold */
        if(scenario==2 && (t<200 || t>=400)) mask=1; /* repress */
        if(scenario==3 && t<16) mask=(t/2)%2; /* brief bounce */
        if(scenario==4) mask=t<24 ? ((t/4)%2) : 1; /* bounce then hold */
        if(scenario==5) mask=t<200 ? 3 : (t<400 ? 1 : (t<600 ? 0 : 1));
        if(scenario==6) mask=t<300 ? 1 : 2; /* slide without release */
        tick=start+t; calls=0;
        char event=Keypad_GetKey();
        if(calls>5) return 3; /* bounded GPIO work per call */
        if(event) printf("%c %u\n",event,t);
    }
    return 0;
}
'''

class ScannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        root = Path(__file__).resolve().parent
        source = HARNESS.replace('/* SCANNER */', (root/'keypad_nonblocking.inc').read_text())
        c = Path(cls.tmp.name)/'scanner.c'
        c.write_text(source)
        cls.exe = c.with_suffix('')
        subprocess.run(shlex.split(os.environ.get('CC','cc')) + [
            '-std=c99','-Wall','-Wextra','-Werror',str(c),'-o',str(cls.exe)
        ],check=True)

    def events(self, scenario, start=0, step=1):
        output = subprocess.check_output([str(self.exe),str(scenario),str(start),str(step)],text=True,timeout=5)
        return [line.split() for line in output.splitlines()]

    def test_idle(self):
        self.assertEqual(self.events(0), [])
    def test_held_key_once(self):
        events=self.events(1)
        self.assertEqual([e[0] for e in events], ['1'])
        self.assertLess(int(events[0][1]),100)
    def test_release_and_repress(self):
        self.assertEqual([e[0] for e in self.events(2)], ['1','1'])
    def test_short_bounce_ignored(self):
        self.assertEqual(self.events(3), [])
    def test_bounce_then_hold_once(self):
        self.assertEqual([e[0] for e in self.events(4)], ['1'])
    def test_multiple_keys_require_release(self):
        events=self.events(5)
        self.assertEqual([e[0] for e in events], ['1'])
        self.assertGreaterEqual(int(events[0][1]),600)
    def test_slide_does_not_repeat(self):
        self.assertEqual([e[0] for e in self.events(6)], ['1'])
    def test_tick_wrap(self):
        self.assertEqual(self.events(2,0xfffffff0),self.events(2))
    def test_ten_ms_polling(self):
        events=self.events(2,step=10)
        self.assertEqual([e[0] for e in events], ['1','1'])

if __name__=='__main__':
    unittest.main(verbosity=2)
