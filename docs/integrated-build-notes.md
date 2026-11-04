# Integrated source: setup and verification notes

These notes describe [alpha code.txt](../alpha%20code.txt) at [commit 99b21b4](https://github.com/GarvKishoreGupta/SANG/blob/99b21b44590506026cab5ba2a32f0f6c8260c171/alpha%20code.txt). They are based on source inspection, not a successful build or hardware run.

## What this snapshot implements

The file combines keypad access, two servo outputs, RC522 RFID, DHT22/fan control, MQ-2/buzzer handling, PIR/LDR lighting, and an OLED. It includes its own main(), clock setup, peripheral initialization functions, and peripheral handles.

The [project report](MESP%20Report.pdf) describes a broader system. In this source, huart2 is declared for compatibility with generated interrupt code, but the accompanying comment explicitly says UART2 is not initialized or used. There is no UART initialization, telemetry transmission, or remote-command parser in this snapshot. The report's Bluetooth/dashboard behavior therefore cannot be reproduced from this file alone.

Other source-specific behavior:

- MQ2_THRESHOLD is 300 raw ADC counts; the alarm comparison is >=. Use this source value when inspecting this snapshot.
- Fan control is updated after successful DHT22 reads; a failed read retains the previous fan setting.
- The room LED follows the current PIR-high AND LDR-high condition on each loop; this snapshot has no ten-second room-light hold timer.
- Door and garage deadlines use timestamps, but the loop is not fully non-blocking: keypad handling waits for release, Buzzer_Tone() uses 100 pairs of 1 ms delays, and peripheral calls may wait.
- The initial 30-second PIR stabilization loop updates MQ-2 readings and the display, but does not process keypad or RFID access.

## Pin map for the integrated snapshot

| Function | Pins / peripheral |
| --- | --- |
| Keypad rows | PB0, PB1, PB2, PB3 |
| Keypad columns | PA15, PB12, PB13; pull-ups |
| Main door servo | PA8, TIM1_CH1, AF1 |
| Garage servo | PA9, TIM1_CH2, AF1 |
| RC522 SPI | PA5 SCK, PA6 MISO, PA7 MOSI; SPI1, AF5 |
| RC522 select / reset | PA4 / PB10 |
| OLED | PB6 SCL, PB7 SDA; I2C1, AF4 |
| DHT22 | PB14; configured dynamically by its driver |
| Fan control | PB4, TIM3_CH1, AF2 |
| MQ-2 analog input | PA0, ADC1 channel 0 |
| PIR / LDR digital input | PA1 / PB15 |
| Room LED / buzzer | PB8 / PB9 |

This map is specific to the integrated file. Use the [standalone guide](standalone-modules.md) for the separate examples. Motor control pins are signals to suitable drivers, not motor power supplies.

## Recovering a reproducible build

The repository does not contain a complete STM32CubeIDE/CubeMX project. The original project is the preferred starting point; creating a new project is a reconstruction that still needs validation.

1. Target STM32F411CEU6 with matching STM32F4 HAL/CMSIS support. Retain the project-generated main.h, HAL configuration, device startup code, system file, linker script, and required interrupt/MSP support.
2. Import a working copy of alpha code.txt as the application's main.c. Exclude other application snapshots from the build. Avoid duplicate definitions of main(), SystemClock_Config(), Error_Handler(), peripheral handles, and initialization functions.
3. Match the source clock tree: HSI, PLL disabled, AHB/APB1/APB2 dividers all 1. With the intended 16 MHz clock, TIM1 prescaler 15 / period 19999 gives 50 Hz; TIM3 prescaler 15 / period 999 gives 1 kHz.
4. Check generated MSP and post-initialization code against the pin map. The snapshot configures several alternate-function pins directly; generated code must not reassign them.
5. Review generated USART2 interrupt support. A declared huart2 is not an initialized UART. Do not enable USART2 interrupts or expect Bluetooth operation without a complete UART implementation.
6. Build with warnings enabled. Record the exact IDE/compiler/HAL versions and attach the build log before marking the firmware buildable.
7. Flash and test each subsystem, then test combined behavior. Record actual observations separately from expected behavior.

## Validation checklist

All items below are pending hardware/build validation, not recorded passes.

- [ ] Complete project builds and links for STM32F411CEU6.
- [ ] OLED initializes with the connected controller and correct address.
- [ ] Keypad correct/incorrect entries and clear/submit keys behave as expected.
- [ ] Main door relocks and garage closes with the actual servo endpoints.
- [ ] Fan changes state at the configured temperature/humidity boundaries.
- [ ] A failed DHT22 read produces the documented retained fan state.
- [ ] MQ-2 readings below/at/above 300 exercise the alarm boundary.
- [ ] PIR/LDR combinations give the expected room LED state.
- [ ] Holding a keypad key and sounding the buzzer are checked for delayed servicing of other modules.

No telemetry, response-time, sensor-accuracy, or safety performance claim is established by this source review.
