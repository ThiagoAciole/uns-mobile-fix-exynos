/* Wrapper para AInputQueue_finishEvent; nao altera a entrega original do evento. */
.text
.global gamepad_b_finish_hook
gamepad_b_finish_hook:
    stp x29, x30, [sp, #-64]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    stp x21, x22, [sp, #32]
    stp x23, x24, [sp, #48]
    mov x19, x0
    mov x20, x1
    mov w21, w2
    mov x0, x20
    bl game_event_type
    mov w22, w0
    cmp w22, #1
    b.ne 1f
    mov x0, x20
    bl game_event_source
    mov w23, w0
    mov x0, x20
    bl game_key_code
    mov w2, w0
    mov w0, w22
    mov w1, w23
    mov w3, w21
    bl controller_b_handled
    mov w21, w0
1:
    mov x0, x19
    mov x1, x20
    mov w2, w21
    bl game_finish_event
    ldp x23, x24, [sp, #48]
    ldp x21, x22, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #64
    ret
