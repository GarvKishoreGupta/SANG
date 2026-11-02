# SANG

STM32 embedded-system examples for access control and sensor monitoring. The repository currently contains separate C source snapshots stored as `.txt` files and four PNG images; it is not yet a complete, reproducible firmware project.

## Source files

| File | Implementation | Current scope |
| --- | --- | --- |
| [gar.txt](gar.txt) | Register-level STM32F401CE keypad and USART1 | Scans a 4×4 keypad and checks a simulated RFID identifier entered through a serial terminal. |
| [ash.txt](ash.txt) | STM32 HAL keypad, DHT22, and ADC example | Intended to start temperature, humidity, and analog sensor monitoring after password entry. The text snapshot contains syntax corruption and needs recovery from the original project. |
| [nya.txt](nya.txt) | Register-level ADC, PIR, LCD, and USART1 | Compares an analog input with a raw ADC threshold, monitors motion, and updates an LCD, serial output, LED, and buzzer. |

Each source contains its own `main()` and should be treated as a separate example. Do not compile all three together.

## Keypad and virtual RFID example

The pin mapping below comes from `gar.txt`.

| Function | STM32 pin(s) |
| --- | --- |
| Keypad rows | PA0–PA3 |
| Keypad columns, internal pull-ups | PA4–PA7 |
| USART1 TX → terminal RX | PA9, AF7 |
| USART1 RX ← terminal TX | PA10, AF7 |

Configure the serial terminal for **9600 baud, 8 data bits, no parity, 1 stop bit**, with local echo disabled. The baud-rate register assumes a **16 MHz USART1 peripheral clock**.

The demonstration identifier is `1234567890`. Enter it followed by carriage return (Enter) or `#` to request access. A different ten-character identifier produces `ACCESS DENIED`; a shorter identifier produces an invalid-length message. LF is ignored. Backspace and Delete remove the last buffered character.

This example simulates RFID input over UART. It does not implement an RC522 reader driver. Relay/servo and alarm actions are placeholders. Keypad presses are reported over UART; they do not implement password authentication in this example.

### Known limitations

- Characters beyond the first ten are discarded, so an overlong input starting with the demonstration identifier can still be accepted. Explicit overflow rejection is a pending fix.
- Key scanning waits for key release, and the main loop uses busy-wait delays. These can delay UART servicing and cause received data to be lost.
- The software delay is not calibrated against a hardware timer.

## Sensor and LCD example

The mapping below comes from `nya.txt` and is separate from the keypad example.

| Function | STM32 pin(s) |
| --- | --- |
| Analog sensor input / ADC1 channel 0 | PA0 |
| LED / buzzer | PA1 / PA2 |
| PIR input, internal pull-down | PA3 |
| USART1 TX | PA9 |
| LCD RS / enable | PB0 / PB1 |
| LCD data D4–D7 | PB4–PB7 |

The program treats an ADC reading above `3000` as a smoke indication. This is a raw demonstration threshold, not a calibrated concentration measurement. Either a smoke indication or motion activates both outputs. LCD and UART messages update when the detection state changes.

## Build and validation status

These files were reviewed as source text. No firmware build, Proteus simulation, or physical hardware test has been performed as part of this documentation update.

To reproduce an example, the repository still needs the original MCU project, device headers/libraries, startup code, linker configuration, compiler settings, and applicable circuit or simulation files. The HAL example additionally needs its generated support files and recovery of corrupted comments, pointer declarations, and register-member expressions. Renaming that snapshot to `.c` alone will not make it buildable.

## Next steps

- Recover the original IDE projects and document exact device and toolchain versions.
- Organize verified examples into separate directories with their own build instructions and pin maps.
- Add circuit/simulation files and label images with their corresponding example and test conditions.
- Fix virtual RFID overflow handling and verify valid, invalid, short, and overlong input cases.
- Record observed results separately from expected behavior.

## Images

The repository includes [week2_as.png](week2_as.png), [week2_ga.png](week2_ga.png), [week2_ny.png](week2_ny.png), and [week2_sh.png](week2_sh.png). Their contents and association with specific runs have not yet been verified.
