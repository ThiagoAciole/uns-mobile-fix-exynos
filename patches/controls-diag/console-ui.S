// Controller-active battle HUD suppression. The caller resumes the exact
// original ccDuelPad::Draw prologue when Paddleboat reports no active device.
    .text
    .globl console_draw
console_draw:
    stp x0, x1, [sp, #-32]!
    stp x29, x30, [sp, #16]
    mov w0, #0
    bl STATUS_TARGET
    cmp w0, #1
    b.eq controller_active

    // Inactive: restore the original arguments and reproduce the displaced
    // function prologue before continuing at its next instruction.
    ldp x29, x30, [sp, #16]
    ldp x0, x1, [sp], #32
    stp x29, x30, [sp, #-32]!
    b DRAW_RESUME

controller_active:
    // Keep the battle item list visible, but omit all touch buttons and sticks.
    // Tail-call the same item-list draw used at the end of the original path.
    ldp x29, x30, [sp, #16]
    ldp x0, x1, [sp], #32
    add x0, x0, #0xc38
    b ITEM_LIST_DRAW
