.text
.balign 4
.global camera_hor_plus
camera_hor_plus:
    ldrh w9,[x8,#0x48a]
    ucvtf s11,w9
    fmov s2,#16.0
    fmul s11,s11,s2
    fmov s2,#9.0
    fdiv s11,s11,s2
    b resume_camera

.global ui_uniform
ui_uniform:
    fneg s6,s0
    b resume_ui

.global input_inverse
input_inverse:
    adrp x9,nucc_sys_got
    ldr x9,[x9,:lo12:nucc_sys_got]
    ldr x9,[x9]
    cbz x9,1f
    ldrh w10,[x9,#0x488]
    ldrh w11,[x9,#0x48a]
    cbz w11,1f
    ucvtf s4,w10
    ucvtf s5,w11
    fmov s2,#9.0
    fmov s3,#16.0
    fmul s4,s4,s2
    fmul s5,s5,s3
    fdiv s4,s4,s5
    fmov s2,#1.0
    fcmp s4,s2
    b.ls 1f
    // UI origin is -viewportHalfWidth; invert its scale without a center offset.
    fmul s0,s0,s4
1:  ret
