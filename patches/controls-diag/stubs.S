// Diagnóstico de controle externo (uso pessoal). Não é patch de jogabilidade.
// Registra no logcat (tag CTRLDIAG):
//   ctrl_fields_hook: campos de nummInputManager::IsControllerConnected na entrada;
//   nie_hook: ponteiro de cada AInputEvent entregue a Paddleboat_processInputEvent.
// Endereços e GOT chegam por --defsym no patch-controls-diag.py.

    .text

    .globl ctrl_fields_hook
ctrl_fields_hook:
    // Substitui a instrução 'ldr w8, [x0, #0x74]' de nummInputManager::IsControllerConnected.
    stp x29, x30, [sp, #-48]!
    mov x29, sp
    str x0, [sp, #16]
    ldr w3, [x0, #0x74]
    ldr w4, [x0, #0x134]
    ldr w5, [x0, #0x1f4]
    ldr w6, [x0, #0x2b4]
    mov w0, #4
    adr x1, tag
    adr x2, fmt_a
    adrp x16, GOT_LOG
    ldr x16, [x16, :lo12:GOT_LOG]
    blr x16
    ldr x0, [sp, #16]
    ldr w3, [x0, #0x374]
    ldr w4, [x0, #0x434]
    ldr w5, [x0, #0x4f4]
    ldr w6, [x0, #0x5b4]
    mov w0, #4
    adr x1, tag
    adr x2, fmt_b
    adrp x16, GOT_LOG
    ldr x16, [x16, :lo12:GOT_LOG]
    blr x16
    ldr x0, [sp, #16]
    ldp x29, x30, [sp], #48
    ldr w8, [x0, #0x74]
    b ENTRY_CONT

    .globl nie_hook
nie_hook:
    // Substitui a 'bl' de NotifyInputEvent para Paddleboat_processInputEvent.
    stp x29, x30, [sp, #-32]!
    mov x29, sp
    str x0, [sp, #16]
    mov w0, #4
    adr x1, tag
    adr x2, fmt_evt
    ldr x3, [sp, #16]
    adrp x16, GOT_LOG
    ldr x16, [x16, :lo12:GOT_LOG]
    blr x16
    ldr x0, [sp, #16]
    ldp x29, x30, [sp], #32
    b PI_PLT

tag:
    .asciz "CTRLDIAG"
fmt_a:
    .asciz "ctrl_fields a=%d %d %d %d"
fmt_b:
    .asciz "ctrl_fields b=%d %d %d %d"
fmt_evt:
    .asciz "input_event ptr=%p"
