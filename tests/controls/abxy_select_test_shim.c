#include <stdint.h>

struct AbxyHandle { void *object; void *strong; void *weak; };
struct AbxyState { void *owner; struct AbxyHandle icons[3]; uint32_t ids[3]; struct AbxyHandle start_font; };
static struct AbxyState state;
static uintptr_t base;
static uintptr_t button_offset = 0x1a20;
static uint32_t shown[4];
static uint32_t creates, releases, draws, fail_create, drawn_id[8], drawn_slot[8];
static uint32_t font_creates, font_releases;
extern void abxy_select_update(struct AbxyState *, void *, uint32_t, uint32_t);
extern void abxy_stage_update(struct AbxyState *, void *, uint32_t, uint32_t);
extern void abxy_select_release(struct AbxyState *, void *);

uint32_t abxy_game_button_shown(void *button) {
    uintptr_t delta = (uintptr_t)button - base - button_offset;
    return delta % 0x360 == 0 && delta / 0x360 < 4 ? shown[delta / 0x360] : 0;
}
void *abxy_game_create_sprite(uint32_t id) { creates++; return fail_create ? 0 : (void *)(uintptr_t)(id + 1); }
void abxy_game_assign_sprite(struct AbxyHandle *h, void *p) { h->object = p; }
void abxy_game_release_sprite(struct AbxyHandle *h) { if (h->object) releases++; h->object = 0; }
void abxy_game_draw_at_button(void *sprite, void *button) {
    drawn_id[draws] = (uint32_t)(uintptr_t)sprite - 1;
    drawn_slot[draws] = (uint32_t)(((uintptr_t)button - base - button_offset) / 0x360);
    draws++;
}
void *abxy_game_create_start_font(void) { font_creates++; return (void *)(uintptr_t)0x100; }
void abxy_game_assign_font(struct AbxyHandle *h, void *p) { h->object = p; }
void abxy_game_release_font(struct AbxyHandle *h) { if (h->object) font_releases++; h->object = 0; }
void abxy_game_draw_start_at_button(void *font, void *button) {
    (void)font;
    drawn_id[draws] = 0x100;
    drawn_slot[draws] = (uint32_t)(((uintptr_t)button - base - button_offset) / 0x360);
    draws++;
}
void mock_reset(void) {
    abxy_select_release(&state, state.owner);
    base = 0; button_offset = 0x1a20; creates = releases = draws = fail_create = font_creates = font_releases = 0;
    for (int i = 0; i < 4; i++) shown[i] = 0;
}
void mock_set_pad(uintptr_t pad) { base = pad; }
void mock_show(uint32_t slot, uint32_t value) { if (slot < 4) shown[slot] = value; }
void mock_fail_create(uint32_t value) { fail_create = value; }
void mock_update(uint32_t status, uint32_t mask) {
    draws = 0;
    abxy_select_update(&state, (void *)base, status, mask);
}
void mock_release(uintptr_t pad) { abxy_select_release(&state, (void *)pad); }
uint32_t mock_creates(void) { return creates; }
uint32_t mock_releases(void) { return releases; }
uint32_t mock_draws(void) { return draws; }
uint32_t mock_font_creates(void) { return font_creates; }
uint32_t mock_font_releases(void) { return font_releases; }
uint32_t mock_drawn_id(uint32_t i) { return drawn_id[i]; }
uint32_t mock_drawn_slot(uint32_t i) { return drawn_slot[i]; }

void mock_stage_update(uint32_t status, uint32_t mask) {
    button_offset = 0xb0;
    draws = 0;
    abxy_stage_update(&state, (void *)base, status, mask);
}
