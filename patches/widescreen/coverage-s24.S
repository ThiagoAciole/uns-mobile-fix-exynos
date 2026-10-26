.text
.balign 4
// shortcut: only 2340x1080; keep the original path on all other render sizes.
.macro check_s24 fallback
    adrp x8,nucc_sys_got
    ldr x8,[x8,:lo12:nucc_sys_got]
    ldr x8,[x8]
    cbz x8,\fallback
    ldr w9,[x8,#0x488]
    mov w10,#0x0924
    movk w10,#0x0438,lsl #16
    cmp w9,w10
    b.ne \fallback
.endm

.global filter_coverage
filter_coverage:
    str q1,[x0,#0x120] // Displaced store; preserve the last vertex color.
    check_s24 1f
    mov w8,#0xc30c0000 // -140.0f
    str w8,[x0,#0x80]
    str w8,[x0,#0xe0]
    mov w8,#0x8000
    movk w8,#0x44b1,lsl #16 // 1420.0f
    str w8,[x0,#0xb0]
    str w8,[x0,#0x110]
1:  b resume_filter

.global fade_coverage
fade_coverage:
    check_s24 2f
    mov w8,#0xc30c0000 // Top-left anchor remains unchanged; move origin left.
    str w8,[x19,#0xbc]
    mov w8,#0x44c30000 // 1560.0f
    str w8,[x19,#0xdc]
    mov w8,#0x44340000 // 720.0f
    str w8,[x19,#0xe0]
    b resume_fade_done
2:  bl original_ui_width
    b resume_fade_original

.global startmenu_layer
startmenu_layer:
    adrp x9,nucc_sys_got
    ldr x9,[x9,:lo12:nucc_sys_got]
    ldr x9,[x9]
    cbz x9,3f
    ldrh w10,[x9,#0x488]
    mov w11,#2340
    cmp w10,w11
    b.ne 3f
    ldrh w10,[x9,#0x48a]
    mov w11,#1080
    cmp w10,w11
    b.ne 3f
    mov w8,#0xc30c0000 // -140.0 logical X
    fmov s0,w8
    movi d1,#0
    mov w8,#0x44c30000 // 1560.0 logical width
    fmov s2,w8
    b resume_startmenu
3:
    movi d0,#0
    movi d1,#0
    fmov s2,s8
    b resume_startmenu

