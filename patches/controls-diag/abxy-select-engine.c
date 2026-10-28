/* Adapta o overlay de selecao aos sprites e coordenadas do motor Android. */
#include <stdint.h>

struct AbxyHandle { void *object; void *strong; void *weak; };
extern uint32_t game_button_is_shown(void *button);
extern void *game_sprite_create(uint32_t id);
extern void game_sprite_assign(struct AbxyHandle *handle, void *sprite);
extern void game_sprite_release(struct AbxyHandle *handle);
extern void game_sprite_set_pos(void *sprite, float x, float y);
extern void game_sprite_set_scale(void *sprite, float x, float y);
extern void game_sprite_draw(void *sprite, uint32_t layer);
extern void *game_font_create(uint32_t id);
extern void game_font_print(void *font, const char *text);
extern void game_font_assign(struct AbxyHandle *handle, void *font);
extern void game_font_release(struct AbxyHandle *handle);
extern void game_font_draw(void *font);
extern const char abxy_start_label[];

static unsigned char *text_matrix(void *button)
{
    if (!button)
        return 0;
    unsigned char *coordinate = *(unsigned char **)((unsigned char *)button + 0x2d0);
    return coordinate ? coordinate + (unsigned int)coordinate[0x120] * 0x40 : 0;
}

uint32_t abxy_game_button_shown(void *button)
{
    return button ? game_button_is_shown(button) : 0;
}

void *abxy_game_create_sprite(uint32_t id)
{
    return id ? game_sprite_create(id) : 0;
}

void abxy_game_assign_sprite(struct AbxyHandle *handle, void *sprite)
{
    game_sprite_assign(handle, sprite);
}

void abxy_game_release_sprite(struct AbxyHandle *handle)
{
    game_sprite_release(handle);
}

void abxy_game_draw_at_button(void *sprite, void *button)
{
    if (!sprite || !button)
        return;
    unsigned char *matrix = text_matrix(button);
    if (!matrix)
        return;
    float x = *(float *)(matrix + 0x88);
    float y = *(float *)(matrix + 0x98);
    game_sprite_set_pos(sprite, x, y - 28.0f);
    game_sprite_set_scale(sprite, 0.5f, 0.5f);
    game_sprite_draw(sprite, 1);
}

void *abxy_game_create_start_font(void)
{
    void *font = game_font_create(0);
    if (font)
        game_font_print(font, abxy_start_label);
    return font;
}

void abxy_game_assign_font(struct AbxyHandle *handle, void *font)
{
    game_font_assign(handle, font);
}

void abxy_game_release_font(struct AbxyHandle *handle)
{
    game_font_release(handle);
}

void abxy_game_draw_start_at_button(void *font, void *button)
{
    if (!font)
        return;
    unsigned char *matrix = text_matrix(button);
    if (!matrix)
        return;
    unsigned char *data = (unsigned char *)font;
    *(float *)(data + 0x60) = *(float *)(matrix + 0x88);
    *(float *)(data + 0x64) = *(float *)(matrix + 0x98) - 28.0f;
    *(float *)(data + 0x68) = -*(float *)(matrix + 0xa8);
    *(float *)(data + 0x74) = 0.5f;
    *(float *)(data + 0x78) = 0.5f;
    game_font_draw(font);
}
