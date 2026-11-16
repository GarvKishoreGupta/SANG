/* Experimental replacement for Keypad_GetKey in alpha code.txt.
 * Requires existing rowPort/rowPin, colPort/colPin and keyMap arrays.
 * Call repeatedly from the foreground loop; do not call from an ISR.
 */
static char Keypad_GetKey(void)
{
    static uint8_t started, row, hits, armed = 1;
    static char frame_key, candidate;
    static uint32_t selected_at, candidate_at;
    uint32_t now = HAL_GetTick();
    char event = '\0';

    if (!started) {
        for (uint8_t r = 0; r < 4; ++r)
            HAL_GPIO_WritePin(rowPort[r], rowPin[r], GPIO_PIN_SET);
        HAL_GPIO_WritePin(rowPort[0], rowPin[0], GPIO_PIN_RESET);
        selected_at = candidate_at = now;
        started = 1;
        return '\0';
    }
    /* Leave the selected row time to settle without blocking the CPU. */
    if ((uint32_t)(now - selected_at) < 2U) return '\0';

    for (uint8_t col = 0; col < 3; ++col) {
        if (HAL_GPIO_ReadPin(colPort[col], colPin[col]) == GPIO_PIN_RESET) {
            ++hits;
            frame_key = keyMap[row][col];
        }
    }
    HAL_GPIO_WritePin(rowPort[row], rowPin[row], GPIO_PIN_SET);
    row = (uint8_t)((row + 1U) % 4U);

    if (row == 0U) {
        /* '?' is not a keypad key: multiple observed keys inhibit events. */
        char sample = hits == 0U ? '\0' : (hits == 1U ? frame_key : '?');
        if (sample != candidate) {
            candidate = sample;
            candidate_at = now;
        } else if ((uint32_t)(now - candidate_at) >= 20U) {
            if (sample == '\0') armed = 1;
            else if (sample == '?') armed = 0;
            else if (armed) {
                event = sample;
                armed = 0;
            }
        }
        if (sample == '?') armed = 0;
        hits = 0;
        frame_key = '\0';
    }
    HAL_GPIO_WritePin(rowPort[row], rowPin[row], GPIO_PIN_RESET);
    selected_at = now;
    return event;
}
