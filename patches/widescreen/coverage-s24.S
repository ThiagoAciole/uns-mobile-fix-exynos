.text
.balign 4
// Dynamic responsive widescreen bounds for any aspect ratio > 16:9.
// Returns with condition GT/HI when wider than 16:9:
//   s4 = W_logical = displayWidth * 720.0f / displayHeight
//   s5 = scale     = displayHeight / 720.0f
//   s6 = X_left    = 640.0f - 0.5f * W_logical
//   s7 = X_right   = 640.0f + 0.5f * W_logical
// Returns with condition LS/EQ when <= 16:9 or uninitialized.
calc_widescreen_bounds:
    adrp x8,nucc_sys_got
    ldr x8,[x8,:lo12:nucc_sys_got]
    ldr x8,[x8]
    cbz x8,1f
    ldrh w9,[x8,#0x488]
    ldrh w10,[x8,#0x48a]
    cbz w10,1f
    ucvtf s4,w9
    ucvtf s5,w10
    mov w8,#0x44340000 // 720.0f
    fmov s6,w8
    fdiv s5,s5,s6      // s5 = scale = displayHeight / 720.0f
    fdiv s4,s4,s5      // s4 = W_logical = displayWidth / scale
    mov w8,#0x44a00000 // 1280.0f
    fmov s6,w8
    fcmp s4,s6
    b.ls 2f
    fsub s6,s6,s4      // 1280.0f - W_logical
    fmov s7,#0.5
    fmul s6,s6,s7      // s6 = X_left = 640.0f - 0.5f * W_logical
    fadd s7,s6,s4      // s7 = X_right = X_left + W_logical
    ret
1:  fmov s4,wzr
    fcmp s4,s4
2:  ret

.global filter_coverage
filter_coverage:
    str q1,[x0,#0x120] // Displaced store; preserve the last vertex color.
    bl calc_widescreen_bounds
    b.ls 1f
    str s6,[x0,#0x80]
    str s6,[x0,#0xe0]
    str s7,[x0,#0xb0]
    str s7,[x0,#0x110]
1:  b resume_filter

.global fade_coverage
fade_coverage:
    bl calc_widescreen_bounds
    b.ls 2f
    str s6,[x19,#0xbc]
    str s4,[x19,#0xdc]
    mov w8,#0x44340000 // 720.0f
    str w8,[x19,#0xe0]
    b resume_fade_done
2:  bl original_ui_width
    b resume_fade_original

.global startmenu_layer
startmenu_layer:
    movi d0,#0
    movi d1,#0
    fmov s2,s8
    bl calc_widescreen_bounds
    b.ls 3f
    fmov s0,s6         // X_left
    fmov s2,s4         // W_logical
3:  b resume_startmenu

.global pushlayer_coverage
pushlayer_coverage:
    mov w9,#0x44a00000 // 1280.0f
    fmov s2,w9
    fneg s4,s6         // s4 = scale = displayHeight / 720.0f
    stp s4,s5,[x0,#0x30]
    fcmp s11,s2        // lw >= 1280.0f -> fullscreen layer
    fmul s2,s2,s4      // s2 = 1280.0f * scale
    b.lt 4f
    fmul s7,s2,s7      // s7 = -640.0f * scale
    fmov s2,s0         // w_frame = displayWidth
    movi d0,#0         // x_frame = 0.0f
    b 5f
4:  fsub s0,s0,s2      // displayWidth - 1280.0f * scale
    fmul s0,s0,s16     // offsetX = 0.5f * (displayWidth - 1280.0f * scale)
    fmadd s0,s9,s4,s0  // x_frame = offsetX + lx * scale
    fmul s2,s11,s4     // w_frame = lw * scale
    fmul s7,s2,s7      // trans_X = -0.5f * w_frame
5:  movi d4,#0
    b resume_pushlayer

