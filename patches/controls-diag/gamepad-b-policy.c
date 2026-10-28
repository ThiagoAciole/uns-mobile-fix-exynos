/* Evita fallback BACK somente para BUTTON_B de gamepad, depois de entregar ao motor. */
#include <stdint.h>
int controller_b_handled(int type, int source, int key, int handled) {
    return handled || (type == 1 && (source & 0x401) == 0x401 && key == 97);
}
