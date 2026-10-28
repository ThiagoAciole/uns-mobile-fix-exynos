// Experimental character-select prompts; F1.2 is not yet complete.
    .text
    .global abxy_select_draw_hook
    .global abxy_select_destroy_hook
    .global abxy_select_draw_trampoline

abxy_select_draw_hook:
    stp x19, x30, [sp, #-16]!
    mov x19, x0
    bl abxy_select_draw_trampoline
    ldr w8, [x19, #0xa0]
    cbz w8, 1f
    mov w0, #0
    bl game_controller_status
    cmp w0, #1
    b.ne 1f
    adrp x8, game_nucc_global_got
    ldr x8, [x8, :lo12:game_nucc_global_got]
    cbz x8, 1f
    ldr x8, [x8]
    cbz x8, 1f
    ldr w3, [x8, #0x1e0]
    mov w2, #1
    mov x1, x19
    adrp x0, abxy_state_address
    add x0, x0, :lo12:abxy_state_address
    bl abxy_select_update
1:
    ldp x19, x30, [sp], #16
    ret

abxy_select_draw_trampoline:
    stp x29, x30, [sp, #-32]!
    b game_select_draw_resume

abxy_select_destroy_hook:
    stp x19, x30, [sp, #-16]!
    mov x19, x0
    mov x1, x19
    adrp x0, abxy_state_address
    add x0, x0, :lo12:abxy_state_address
    bl abxy_select_release
    mov x0, x19
    ldp x19, x30, [sp], #16
    sub sp, sp, #0x60
    b game_select_destroy_resume

    .global game_font_draw
game_font_draw:
    ldr x8, [x0]
    ldr x8, [x8, #0x60]
    br x8

    .global abxy_start_label
abxy_start_label:
    .asciz "START"
    .balign 4

.global abxy_stage_draw_hook
.global abxy_stage_destroy_hook
abxy_stage_draw_hook:
    stp x19, x30, [sp, #-16]!
    mov x19, x0
    bl abxy_stage_draw_trampoline
    ldr w8, [x19, #0xa0]
    cbz w8, 1f
    mov w0, #0
    bl game_controller_status
    cmp w0, #1
    b.ne 1f
    adrp x8, game_nucc_global_got
    ldr x8, [x8, :lo12:game_nucc_global_got]
    cbz x8, 1f
    ldr x8, [x8]
    cbz x8, 1f
    ldr w3, [x8, #0x1e0]
    mov w2, #1
    mov x1, x19
    adrp x0, abxy_state_address
    add x0, x0, :lo12:abxy_state_address
    bl abxy_stage_update
1:
    ldp x19, x30, [sp], #16
    ret
abxy_stage_draw_trampoline:
    stp x29, x30, [sp, #-32]!
    b game_stage_draw_resume
abxy_stage_destroy_hook:
    stp x19, x30, [sp, #-16]!
    mov x19, x0
    mov x1, x19
    adrp x0, abxy_state_address
    add x0, x0, :lo12:abxy_state_address
    bl abxy_select_release
    mov x0, x19
    ldp x19, x30, [sp], #16
    sub sp, sp, #0x50
    b game_stage_destroy_resume
