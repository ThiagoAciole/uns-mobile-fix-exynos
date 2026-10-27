// Diagnostic only: keep the existing widescreen stubs and caller ABI intact.
// Flow hooks preserve original int returns. ENABLE_GAMEPAD additionally sets
// the local initialization mask bit, without changing the shared constant.
    .text
#ifndef NO_FLOW_LOGS
    .globl flow_event
flow_event:
    stp x30, x19, [sp, #-32]!
    stp x20, x21, [sp, #16]
    mov x19, x0
    bl EVENT_TARGET
    mov w20, w0
    mov x0, x19
    bl SOURCE_TARGET
    mov w21, w0
    mov x0, x19
    bl DEVICE_TARGET
    mov w5, w0
    mov w3, w20
    mov w4, w21
    adr x2, event_format
    b flow_log

    .globl flow_data
flow_data:
    stp x30, x19, [sp, #-32]!
    stp x20, x21, [sp, #16]
    mov x19, x1
    mov w21, w0
    bl DATA_TARGET
    mov w20, w0
    mov w3, w0
    mov w4, w21
    mov w5, wzr
    cbnz w0, data_log
    // On success only: Paddleboat_Controller_Data.buttons is at offset 8.
    ldr w5, [x19, #8]
data_log:
    adr x2, data_format
flow_log:
    mov w0, #4
    adr x1, flow_tag
    adrp x16, GOT_LOG
    ldr x16, [x16, :lo12:GOT_LOG]
    blr x16
    mov w0, w20
    ldp x20, x21, [sp, #16]
    ldp x30, x19, [sp], #32
    ret
flow_tag:
    .asciz "CTRLFLOW"
event_format:
    .asciz "event ret=%d src=%x dev=%d"
data_format:
    .asciz "data ret=%d slot=%d buttons=%x"
    .balign 4
#endif

#ifdef ENABLE_GAMEPAD
    .globl gamepad_enable
gamepad_enable:
    // Reproduce androidMain's store, then enable only the gamepad bit locally.
    // x8 points to the caller's parameter struct; x9 is live at the continuation.
    stur d0, [x8, #0x14]
    str x9, [sp, #-16]!
    ldr w9, [x8, #0x14]
    orr w9, w9, #1
    str w9, [x8, #0x14]
    ldr x9, [sp], #16
    b MASK_RESUME
#endif
