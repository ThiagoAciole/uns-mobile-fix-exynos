/*
 * Presentation policy for the Android character-selection pad.
 * Native adapters must provide sprite ownership, positioning and drawing.
 * No hook or APK currently uses this component.
 */
#include <stdint.h>

struct AbxyHandle { void *object; void *strong; void *weak; };
struct AbxyState { void *owner; struct AbxyHandle icons[3]; uint32_t ids[3]; struct AbxyHandle start_font; };

extern uint32_t abxy_icon_for_mask(uint32_t mask, uint32_t status);
extern uint32_t abxy_game_button_shown(void *button);
extern void *abxy_game_create_sprite(uint32_t id);
extern void abxy_game_assign_sprite(struct AbxyHandle *handle, void *sprite);
extern void abxy_game_release_sprite(struct AbxyHandle *handle);
extern void abxy_game_draw_at_button(void *sprite, void *button);
extern void *abxy_game_create_start_font(void);
extern void abxy_game_assign_font(struct AbxyHandle *handle, void *font);
extern void abxy_game_release_font(struct AbxyHandle *handle);
extern void abxy_game_draw_start_at_button(void *font, void *button);

void abxy_select_release(struct AbxyState *state, void *owner)
{
    if (state->owner != owner)
        return;
    for (unsigned int i = 0; i < 3; i++) {
        if (state->icons[i].object)
            abxy_game_release_sprite(&state->icons[i]);
        state->ids[i] = 0;
    }
    if (state->start_font.object)
        abxy_game_release_font(&state->start_font);
    state->owner = 0;
}

static void draw_slot(struct AbxyState *state, void *button, unsigned int index, uint32_t id)
{
    if (!id || !abxy_game_button_shown(button))
        return;
    if (state->icons[index].object && state->ids[index] != id) {
        abxy_game_release_sprite(&state->icons[index]);
        state->ids[index] = 0;
    }
    if (!state->icons[index].object) {
        void *sprite = abxy_game_create_sprite(id);
        if (!sprite)
            return;
        abxy_game_assign_sprite(&state->icons[index], sprite);
        if (!state->icons[index].object)
            return;
        state->ids[index] = id;
    }
    abxy_game_draw_at_button(state->icons[index].object, button);
}

void abxy_select_update(struct AbxyState *state, void *pad, uint32_t status, uint32_t confirm_mask)
{
    if (!state || !pad)
        return;
    if (state->owner != pad) {
        if (state->owner)
            abxy_select_release(state, state->owner);
        state->owner = pad;
    }
    if (status != 1)
        return;

    /* Slots: 0 Random, 1 Settings, 2/3 Select. */
    unsigned char *buttons = (unsigned char *)pad + 0x1a20;
    draw_slot(state, buttons, 0, abxy_icon_for_mask(0x1000, status));
    void *settings = buttons + 0x360;
    if (abxy_game_button_shown(settings)) {
        if (!state->start_font.object) {
            void *font = abxy_game_create_start_font();
            if (font)
                abxy_game_assign_font(&state->start_font, font);
        }
        if (state->start_font.object)
            abxy_game_draw_start_at_button(state->start_font.object, settings);
    }
    uint32_t confirm = abxy_icon_for_mask(confirm_mask, status);
    draw_slot(state, buttons + 2 * 0x360, 1, confirm);
    draw_slot(state, buttons + 3 * 0x360, 2, confirm);
}

/* Stage buttons use the same touch text button type as character select. */
void abxy_stage_update(struct AbxyState *state, void *pad, uint32_t status, uint32_t confirm_mask)
{
    if (!state || !pad)
        return;
    if (state->owner != pad) {
        if (state->owner)
            abxy_select_release(state, state->owner);
        state->owner = pad;
    }
    if (status != 1)
        return;
    unsigned char *buttons = (unsigned char *)pad;
    draw_slot(state, buttons + 0xb0, 0, abxy_icon_for_mask(confirm_mask, status));
    draw_slot(state, buttons + 0x410, 1, abxy_icon_for_mask(0x1000, status));
}
