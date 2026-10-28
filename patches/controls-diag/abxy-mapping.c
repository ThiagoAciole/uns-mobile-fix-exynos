/*
 * Map one internal face-button mask to a verified cmn_button00 sprite.
 * A zero result means that no controller glyph should be displayed.
 * This helper is not yet connected to the game's UI.
 */
unsigned int abxy_icon_for_mask(unsigned int mask, unsigned int controller_status)
{
    if (controller_status != 1)
        return 0;

    switch (mask) {
    case 0x4000: return 0x10; /* A: xcmn_batsu */
    case 0x2000: return 0x12; /* B: xcmn_circle */
    case 0x8000: return 0x11; /* X: xcmn_square */
    case 0x1000: return 0x0f; /* Y: xcmn_triangle */
    default: return 0;
    }
}
