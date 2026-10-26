
C:\Users\Thiago Aciole\Projetos\Jogos\naruto-storm-1\naruto-analysis\libultimateninjastorm.so:	file format elf64-littleaarch64

Disassembly of section .text:

0000000000d3783c <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc>:
  d378a0: 94177f60     	bl	0x1317620 <_ZN22mmShaderEffectCompilerC1Ev@plt>
  d378a4: f9000a76     	str	x22, [x19, #0x10]
  d378a8: aa1503e0     	mov	x0, x21
  d378ac: 94177f61     	bl	0x1317630 <_ZN22mmRenderManager_Vulkan20CreateVulkanInstanceEv@plt>
  d378b0: aa1303e0     	mov	x0, x19
  d378b4: 94177acb     	bl	0x13163e0 <_ZN19mmGPUDevice_Android22InitializeVulkanDeviceEv@plt>
  d378b8: 6f00e400     	movi	v0.2d, #0000000000000000
  d378bc: d0003408     	adrp	x8, 0x13b9000
  d378c0: f9462508     	ldr	x8, [x8, #0xc48]
  d378c4: f9001fff     	str	xzr, [sp, #0x38]
  d378c8: b90003ff     	str	wzr, [sp]
  d378cc: f9400108     	ldr	x8, [x8]
  d378d0: f9002bff     	str	xzr, [sp, #0x50]
  d378d4: 3c8283e0     	stur	q0, [sp, #0x28]
  d378d8: 3c8183e0     	stur	q0, [sp, #0x18]
  d378dc: f9400500     	ldr	x0, [x8, #0x8]
  d378e0: f9400008     	ldr	x8, [x0]
  d378e4: f9401508     	ldr	x8, [x8, #0x28]
  d378e8: d63f0100     	blr	x8
  d378ec: f9402808     	ldr	x8, [x0, #0x50]
  d378f0: f9401269     	ldr	x9, [x19, #0x20]
  d378f4: f90023e8     	str	x8, [sp, #0x40]
  d378f8: f9400128     	ldr	x8, [x9]
  d378fc: f9425a69     	ldr	x9, [x19, #0x4b0]
  d37900: a900a7e8     	stp	x8, x9, [sp, #0x8]
  d37904: 52820008     	mov	w8, #0x1000             // =4096
  d37908: 72a00808     	movk	w8, #0x40, lsl #16
  d3790c: b9004be8     	str	w8, [sp, #0x48]
  d37910: 910003e0     	mov	x0, sp
  d37914: 9113c261     	add	x1, x19, #0x4f0
  d37918: 94175d22     	bl	0x130eda0 <vmaCreateAllocator@plt>
  d3791c: 340000e0     	cbz	w0, 0xd37938 <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0xfc>
  d37920: f9400268     	ldr	x8, [x19]
  d37924: f9401108     	ldr	x8, [x8, #0x20]
  d37928: aa1303e0     	mov	x0, x19
  d3792c: d63f0100     	blr	x8
  d37930: 52b00000     	mov	w0, #-0x80000000        // =-2147483648
  d37934: 14000016     	b	0xd3798c <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x150>
  d37938: aa1503e0     	mov	x0, x21
  d3793c: aa1403e1     	mov	x1, x20
  d37940: 94177f40     	bl	0x1317640 <_ZN22mmRenderManager_Vulkan10InitializeERK12mmDeviceDesc@plt>
  d37944: 52802800     	mov	w0, #0x140              // =320
  d37948: aa1f03e1     	mov	x1, xzr
  d3794c: 52800202     	mov	w2, #0x10               // =16
  d37950: 941656b4     	bl	0x12cd420 <_ZnwmP16mmMemoryDummyArgm@plt>
  d37954: aa0003f5     	mov	x21, x0
  d37958: 94177aa6     	bl	0x13163f0 <_ZN23mmComputeManager_VulkanC2Ev@plt>
  d3795c: f94002a8     	ldr	x8, [x21]
  d37960: f9000e75     	str	x21, [x19, #0x18]
  d37964: aa1503e0     	mov	x0, x21
  d37968: f9400908     	ldr	x8, [x8, #0x10]
  d3796c: d63f0100     	blr	x8
  d37970: 36f800e0     	tbz	w0, #0x1f, 0xd3798c <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x150>
  d37974: f9400268     	ldr	x8, [x19]
  d37978: 2a0003f4     	mov	w20, w0
  d3797c: aa1303e0     	mov	x0, x19
  d37980: f9401108     	ldr	x8, [x8, #0x20]
  d37984: d63f0100     	blr	x8
  d37988: 2a1403e0     	mov	w0, w20
  d3798c: f94016e8     	ldr	x8, [x23, #0x28]
  d37990: f9402fe9     	ldr	x9, [sp, #0x58]
  d37994: eb09011f     	cmp	x8, x9
  d37998: 540002a1     	b.ne	0xd379ec <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x1b0>
  d3799c: a9484ff4     	ldp	x20, x19, [sp, #0x80]
  d379a0: a94757f6     	ldp	x22, x21, [sp, #0x70]
  d379a4: a9465ffe     	ldp	x30, x23, [sp, #0x60]
  d379a8: 910243ff     	add	sp, sp, #0x90
  d379ac: d65f03c0     	ret
  d379b0: 14000004     	b	0xd379c0 <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x184>
  d379b4: aa0003f4     	mov	x20, x0
  d379b8: aa1603e0     	mov	x0, x22
  d379bc: 14000003     	b	0xd379c8 <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x18c>
  d379c0: aa0003f4     	mov	x20, x0
  d379c4: aa1503e0     	mov	x0, x21
  d379c8: aa1f03e1     	mov	x1, xzr
  d379cc: 52800202     	mov	w2, #0x10               // =16
  d379d0: 94168df0     	bl	0x12db190 <_ZdlPvP16mmMemoryDummyArgm@plt>
  d379d4: f94016e8     	ldr	x8, [x23, #0x28]
  d379d8: f9402fe9     	ldr	x9, [sp, #0x58]
  d379dc: eb09011f     	cmp	x8, x9
  d379e0: 54000061     	b.ne	0xd379ec <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x1b0>
  d379e4: aa1403e0     	mov	x0, x20
  d379e8: 941622b3     	bl	0x12c04b4 <_ZN15mmRenderManager22WaitReady4RenderThreadEv+0x1ba4>
  d379ec: 9416340d     	bl	0x12c4a20 <__stack_chk_fail@plt>
  d379f0: 7100043f     	cmp	w1, #0x1
  d379f4: aa0003f4     	mov	x20, x0
  d379f8: 54fffee1     	b.ne	0xd379d4 <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x198>
  d379fc: aa1403e0     	mov	x0, x20
  d37a00: 941636f4     	bl	0x12c55d0 <__cxa_begin_catch@plt>
  d37a04: f9400268     	ldr	x8, [x19]
  d37a08: f9401108     	ldr	x8, [x8, #0x20]
  d37a0c: aa1303e0     	mov	x0, x19
  d37a10: d63f0100     	blr	x8
  d37a14: 9416cd5b     	bl	0x12eaf80 <__cxa_end_catch@plt>
  d37a18: 17ffffc6     	b	0xd37930 <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0xf4>
  d37a1c: aa0003f4     	mov	x20, x0
  d37a20: 9416cd58     	bl	0x12eaf80 <__cxa_end_catch@plt>
  d37a24: 17ffffec     	b	0xd379d4 <_ZN19mmGPUDevice_Android22InitializeRenderSystemERK12mmDeviceDesc+0x198>
  d37a28: 97f842ef     	bl	0xb485e4 <_ZN30mmDrawCommand_BindShaderBufferD2Ev+0x90>

0000000000d37a2c <_ZN3ns111emIf_ScrollEPNS_12cmnEventDataE>:
  d37a2c: a9be7bfd     	stp	x29, x30, [sp, #-0x20]!
  d37a30: f9000bf3     	str	x19, [sp, #0x10]
  d37a34: 910003fd     	mov	x29, sp
  d37a38: 52800061     	mov	w1, #0x3                // =3
  d37a3c: aa0003f3     	mov	x19, x0
