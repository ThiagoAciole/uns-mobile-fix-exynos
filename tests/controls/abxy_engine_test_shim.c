#include <stdint.h>
#include <string.h>

struct AbxyHandle { void *object; void *strong; void *weak; };
static unsigned char button[0x360], coord[0x200], font[0x100];
static float draw_x, draw_y, scale_x, scale_y;
static uint32_t draw_count, font_draw_count;
static char font_text[16];
const char abxy_start_label[] = "START";

uint32_t game_button_is_shown(void *p) { return p == button; }
void *game_sprite_create(uint32_t id) { return (void *)(uintptr_t)(id + 1); }
void game_sprite_assign(struct AbxyHandle *h, void *p) { h->object = p; }
void game_sprite_release(struct AbxyHandle *h) { h->object = 0; }
void game_sprite_set_pos(void *sprite, float x, float y) { (void)sprite; draw_x = x; draw_y = y; }
void game_sprite_set_scale(void *sprite, float x, float y) { (void)sprite; scale_x = x; scale_y = y; }
void game_sprite_draw(void *sprite, uint32_t layer) { (void)sprite; (void)layer; draw_count++; }
void *game_font_create(uint32_t id) { return id == 0 ? font : 0; }
void game_font_print(void *object, const char *text) { (void)object; strncpy(font_text, text, sizeof(font_text) - 1); }
void game_font_assign(struct AbxyHandle *h, void *p) { h->object = p; }
void game_font_release(struct AbxyHandle *h) { h->object = 0; }
void game_font_draw(void *object) { (void)object; font_draw_count++; }
void mock_engine_reset(void) {
    memset(button, 0, sizeof(button)); memset(coord, 0, sizeof(coord)); memset(font, 0, sizeof(font));
    memset(font_text, 0, sizeof(font_text));
    draw_count = font_draw_count = 0; draw_x = draw_y = scale_x = scale_y = 0;
}
void mock_engine_coordinates(float x, float y) {
    void *p = coord;
    memcpy(button + 0x2d0, &p, sizeof(p));
    coord[0x120] = 1;
    memcpy(coord + 0x40 + 0x88, &x, sizeof(x));
    memcpy(coord + 0x40 + 0x98, &y, sizeof(y));
}
void *mock_engine_button(void) { return button; }
float mock_engine_x(void) { return draw_x; }
float mock_engine_y(void) { return draw_y; }
float mock_engine_scale_x(void) { return scale_x; }
float mock_engine_scale_y(void) { return scale_y; }
uint32_t mock_engine_draws(void) { return draw_count; }
uint32_t mock_font_draws(void) { return font_draw_count; }
const char *mock_font_text(void) { return font_text; }
float mock_font_x(void) { float v; memcpy(&v, font + 0x60, sizeof(v)); return v; }
float mock_font_y(void) { float v; memcpy(&v, font + 0x64, sizeof(v)); return v; }
