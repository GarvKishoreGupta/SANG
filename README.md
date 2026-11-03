# SANG

Smart-home automation prototype built around the STM32F411CEU6 (Black Pill), with STM32 HAL C source snapshots for access control, OLED displays, and environmental monitoring.

The [project report](docs/MESP%20Report.pdf) describes the complete model: keypad door access, RFID garage access, temperature/humidity-based ventilation, MQ-2 alerts, PIR/LDR lighting, and HC-05 telemetry through a PC bridge, Java server, dashboard, and ThingSpeak. The bridge, server, and dashboard sources are not included in this repository.

## Source files

| File | Scope |
| --- | --- |
| [alpha code.txt](alpha%20code.txt) | Integrated application containing keypad/password access, RFID, servo control, MQ-2 sensing, DHT22 sensing, fan control, and OLED output. |
| [RFID and SERVO and OLED.txt](RFID%20and%20SERVO%20and%20OLED.txt) | RC522 RFID reader, garage servo control, and OLED status display. |
| [MQ-2 + OLED + PASSIVE BUZZER.txt](MQ-2%20%2B%20OLED%20%2B%20PASSIVE%20BUZZER.txt) | MQ-2 analog sensing with OLED output and a passive buzzer. |
| [DHT22 WITH FAN AND OLED WORKING WITH DIFFERENT FAN SPEEDS(1).txt](DHT22%20WITH%20FAN%20AND%20OLED%20WORKING%20WITH%20DIFFERENT%20FAN%20SPEEDS%281%29.txt) | Standalone DHT22 readings, OLED display, and four-state PWM fan control. |
| [KEYPAD WITH PASSWORD WITH MOTOR WORKING(2).txt](KEYPAD%20WITH%20PASSWORD%20WITH%20MOTOR%20WORKING%282%29.txt) | Standalone keypad password entry, OLED feedback, and SG90 door-servo control. |

The uploaded source files are preserved byte-for-byte with their original filenames. Each is a separate application snapshot; do not compile their `main()` functions together.

## Report and demonstration

- [MESP project report (PDF)](docs/MESP%20Report.pdf): methodology, hardware, system behavior, reported results, limitations, and future work. Uploaded without content changes; its filename is simplified for the repository.
- [Standalone module guide](docs/standalone-modules.md): wiring, control thresholds, keypad operation, and setup.
- [Project demonstration video (MP4)](videos/MESP%20video.mp4): uploaded project recording (18.6 MB). See the [video guide](videos/README.md) for viewing and download links.

The report's integrated-system results are the authors' reported observations; they were not independently reproduced during this repository update. In particular, the report describes retaining the previous fan setting on a failed sensor read, while the standalone DHT22 example switches the fan off.

## Build and validation

These snapshots require the matching STM32 project, HAL/device support files, startup code, linker configuration, and correct board wiring. A complete reproducible IDE project is not included here. No build, simulation, or hardware test was performed during this documentation and file update.

Pin assignments and configuration values must be taken from the particular source being used. The integrated application and standalone examples may use different settings. Sensor thresholds and servo endpoints need validation for the connected hardware.

## Repository history

The earlier `ash.txt`, `gar.txt`, `nya.txt`, and four `week2_*.png` files were removed from the current tree at the owner's request. They remain available in Git history.
