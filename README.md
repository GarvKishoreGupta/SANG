# SANG

STM32 HAL source snapshots for access control, OLED displays, and environmental monitoring.

## Source files

| File | Scope |
| --- | --- |
| [alpha code.txt](alpha%20code.txt) | Integrated application containing keypad/password access, RFID, servo control, MQ-2 sensing, DHT22 sensing, fan control, and OLED output. |
| [RFID and SERVO and OLED.txt](RFID%20and%20SERVO%20and%20OLED.txt) | RC522 RFID reader, garage servo control, and OLED status display. |
| [MQ-2 + OLED + PASSIVE BUZZER.txt](MQ-2%20%2B%20OLED%20%2B%20PASSIVE%20BUZZER.txt) | MQ-2 analog sensing with OLED output and a passive buzzer. |

The uploaded source files are preserved byte-for-byte with their original filenames. Each is a separate application snapshot; do not compile their `main()` functions together.

## Build and validation

These snapshots require the matching STM32 project, HAL/device support files, startup code, linker configuration, and correct board wiring. A complete reproducible IDE project is not included here. No build, simulation, or hardware test was performed during this file replacement.

Pin assignments and configuration values must be taken from the particular source being used. The integrated application and standalone examples may use different settings. Sensor thresholds and servo endpoints need validation for the connected hardware.

## Repository history

The earlier `ash.txt`, `gar.txt`, `nya.txt`, and four `week2_*.png` files were removed from the current tree at the owner's request. They remain available in Git history.
