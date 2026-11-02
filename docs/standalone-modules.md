# Standalone STM32 module guide

These notes describe the two newly uploaded source snapshots. Each contains its own main(), clock configuration, peripheral setup, and OLED helpers; build only one snapshot at a time. They use STM32 HAL, a 16 MHz HSI clock without PLL, and an SH1106-compatible OLED at 7-bit I2C address 0x3C (shifted left for HAL).

## Connections

| Function | MCU connection | Configuration |
| --- | --- | --- |
| OLED SCL / SDA | PB6 / PB7 | I2C1, AF4, 100 kHz |
| DHT22 data | PB14 | GPIO with pull-up; DWT-based microsecond timing |
| Fan control | PB4 | TIM3_CH1, AF2, 1 kHz PWM |
| Keypad rows R1–R4 | PB0, PB1, PB2, PB3 | Row outputs |
| Keypad columns C1–C3 | PA15, PB12, PB13 | Inputs with pull-ups |
| SG90 servo signal | PA8 | TIM1_CH1, AF1, 50 Hz PWM |

Use appropriate peripheral power supplies and a common ground. The fan PWM pin is a control signal for a suitable driver, not a motor power output. Verify the wiring and voltage levels against the actual modules.

## DHT22, fan, and OLED

Temperature and humidity are stored in tenths of a unit. A successful reading updates the OLED and selects the highest matching speed:

| State | Condition | PWM compare / duty |
| --- | --- | --- |
| OFF | Temperature < 25 °C **or** humidity < 80% RH | 0 / 0% |
| HIGH | Temperature ≥ 31 °C **and** humidity ≥ 90% RH | 1000 / 100% |
| MEDIUM | Otherwise, temperature ≥ 28 °C **and** humidity ≥ 85% RH | 650 / 65% |
| LOW | Both minimum limits met, but neither higher state matches | 350 / 35% |

TIM3 uses prescaler 15 and period 999 with a 16 MHz timer clock. The loop delays 2500 ms after each attempt, so reads occur slightly more than 2.5 seconds apart. Timing timeouts or a checksum failure turn the fan off and display DHT22 ERROR / CHECK DATA WIRE. This differs from the integrated behavior described in the report, which retains the previous fan setting.

## Keypad, password, and servo

- Key layout: rows 123, 456, 789, and *0#.
- The demonstration password is 1234, defined by PASSWORD.
- Enter digits, press # to submit, or * to clear the entire entry.
- The OLED masks entered digits. Up to eight digits can be entered.
- A correct password displays ACCESS GRANTED, applies a 2000 µs servo pulse for 3 seconds, then returns to the 1000 µs locked pulse.
- An incorrect password displays ACCESS DENIED for 2 seconds.
- TIM1 uses prescaler 15 and period 19999, giving a 20 ms period at a 16 MHz timer clock.

The example uses blocking delays and waits for key release. It is a standalone demonstration; its fixed password and lack of attempt limiting are not production access-control features.

## Build and run

1. Create or use an STM32CubeIDE / STM32CubeMX project targeting STM32F411CEU6 with matching STM32F4 HAL and device support.
2. Copy one selected TXT snapshot into the application's main.c. Keep the project's required main.h, startup code, linker script, HAL configuration, and interrupt support.
3. Match peripheral and clock configuration to the selected snapshot. Avoid duplicate main functions, peripheral handles, and initialization functions in generated files.
4. Connect that module according to the table, build, and flash with a compatible debugger.
5. Check the OLED, sensor readings and fan thresholds, or correct/incorrect keypad entries and timed servo relocking.

A complete IDE project and hardware are not available here, so compilation and hardware behavior have not been verified in this update. Source files are preserved byte-for-byte.
