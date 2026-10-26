
work\decoded\lib\arm64-v8a\libultimateninjastorm.so:	file format elf64-littleaarch64

Disassembly of section .text:

0000000000d3e03c <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)>:
  d3e03c: d10243ff     	sub	sp, sp, #0x90
  d3e040: a9065ffe     	stp	x30, x23, [sp, #0x60]
  d3e044: a90757f6     	stp	x22, x21, [sp, #0x70]
  d3e048: a9084ff4     	stp	x20, x19, [sp, #0x80]
  d3e04c: d53bd057     	mrs	x23, TPIDR_EL0
  d3e050: f94016e8     	ldr	x8, [x23, #0x28]
  d3e054: f9002fe8     	str	x8, [sp, #0x58]
  d3e058: b9400028     	ldr	w8, [x1]
  d3e05c: 34000068     	cbz	w8, 0xd3e068 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x2c>
  d3e060: 2a1f03e0     	mov	w0, wzr
  d3e064: 1400004a     	b	0xd3e18c <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x150>
  d3e068: aa0103f4     	mov	x20, x1
  d3e06c: aa0003f3     	mov	x19, x0
  d3e070: 52866500     	mov	w0, #0x3328             // =13096
  d3e074: aa1f03e1     	mov	x1, xzr
  d3e078: 52800202     	mov	w2, #0x10               // =16
  d3e07c: 941656ed     	bl	0x12d3c30 <_ZnwmP16mmMemoryDummyArgm@plt>
  d3e080: aa0003f5     	mov	x21, x0
  d3e084: 94177f67     	bl	0x131de20 <_ZN22mmRenderManager_VulkanC1Ev@plt>
  d3e088: 52800d00     	mov	w0, #0x68               // =104
  d3e08c: aa1f03e1     	mov	x1, xzr
  d3e090: 52800202     	mov	w2, #0x10               // =16
  d3e094: f9000675     	str	x21, [x19, #0x8]
  d3e098: 941656e6     	bl	0x12d3c30 <_ZnwmP16mmMemoryDummyArgm@plt>
  d3e09c: aa0003f6     	mov	x22, x0
  d3e0a0: 94177f64     	bl	0x131de30 <_ZN22mmShaderEffectCompilerC1Ev@plt>
  d3e0a4: f9000a76     	str	x22, [x19, #0x10]
  d3e0a8: aa1503e0     	mov	x0, x21
  d3e0ac: 94177f65     	bl	0x131de40 <_ZN22mmRenderManager_Vulkan20CreateVulkanInstanceEv@plt>
  d3e0b0: aa1303e0     	mov	x0, x19
  d3e0b4: 94177acf     	bl	0x131cbf0 <_ZN19mmGPUDevice_Android22InitializeVulkanDeviceEv@plt>
  d3e0b8: 6f00e400     	movi	v0.2d, #0000000000000000
  d3e0bc: d0003408     	adrp	x8, 0x13c0000
  d3e0c0: f9422d08     	ldr	x8, [x8, #0x458]
  d3e0c4: f9001fff     	str	xzr, [sp, #0x38]
  d3e0c8: b90003ff     	str	wzr, [sp]
  d3e0cc: f9400108     	ldr	x8, [x8]
  d3e0d0: f9002bff     	str	xzr, [sp, #0x50]
  d3e0d4: 3c8283e0     	stur	q0, [sp, #0x28]
  d3e0d8: 3c8183e0     	stur	q0, [sp, #0x18]
  d3e0dc: f9400500     	ldr	x0, [x8, #0x8]
  d3e0e0: f9400008     	ldr	x8, [x0]
  d3e0e4: f9401508     	ldr	x8, [x8, #0x28]
  d3e0e8: d63f0100     	blr	x8
  d3e0ec: f9402808     	ldr	x8, [x0, #0x50]
  d3e0f0: f9401269     	ldr	x9, [x19, #0x20]
  d3e0f4: f90023e8     	str	x8, [sp, #0x40]
  d3e0f8: f9400128     	ldr	x8, [x9]
  d3e0fc: f9425a69     	ldr	x9, [x19, #0x4b0]
  d3e100: a900a7e8     	stp	x8, x9, [sp, #0x8]
  d3e104: 52820008     	mov	w8, #0x1000             // =4096
  d3e108: 72a00808     	movk	w8, #0x40, lsl #16
  d3e10c: b9004be8     	str	w8, [sp, #0x48]
  d3e110: 910003e0     	mov	x0, sp
  d3e114: 9113c261     	add	x1, x19, #0x4f0
  d3e118: 94175d26     	bl	0x13155b0 <vmaCreateAllocator@plt>
  d3e11c: 340000e0     	cbz	w0, 0xd3e138 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0xfc>
  d3e120: f9400268     	ldr	x8, [x19]
  d3e124: f9401108     	ldr	x8, [x8, #0x20]
  d3e128: aa1303e0     	mov	x0, x19
  d3e12c: d63f0100     	blr	x8
  d3e130: 52b00000     	mov	w0, #-0x80000000        // =-2147483648
  d3e134: 14000016     	b	0xd3e18c <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x150>
  d3e138: aa1503e0     	mov	x0, x21
  d3e13c: aa1403e1     	mov	x1, x20
  d3e140: 94177f44     	bl	0x131de50 <_ZN22mmRenderManager_Vulkan10InitializeERK12mmDeviceDesc@plt>
  d3e144: 52802800     	mov	w0, #0x140              // =320
  d3e148: aa1f03e1     	mov	x1, xzr
  d3e14c: 52800202     	mov	w2, #0x10               // =16
  d3e150: 941656b8     	bl	0x12d3c30 <_ZnwmP16mmMemoryDummyArgm@plt>
  d3e154: aa0003f5     	mov	x21, x0
  d3e158: 94177aaa     	bl	0x131cc00 <_ZN23mmComputeManager_VulkanC2Ev@plt>
  d3e15c: f94002a8     	ldr	x8, [x21]
  d3e160: f9000e75     	str	x21, [x19, #0x18]
  d3e164: aa1503e0     	mov	x0, x21
  d3e168: f9400908     	ldr	x8, [x8, #0x10]
  d3e16c: d63f0100     	blr	x8
  d3e170: 36f800e0     	tbz	w0, #0x1f, 0xd3e18c <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x150>
  d3e174: f9400268     	ldr	x8, [x19]
  d3e178: 2a0003f4     	mov	w20, w0
  d3e17c: aa1303e0     	mov	x0, x19
  d3e180: f9401108     	ldr	x8, [x8, #0x20]
  d3e184: d63f0100     	blr	x8
  d3e188: 2a1403e0     	mov	w0, w20
  d3e18c: f94016e8     	ldr	x8, [x23, #0x28]
  d3e190: f9402fe9     	ldr	x9, [sp, #0x58]
  d3e194: eb09011f     	cmp	x8, x9
  d3e198: 540002a1     	b.ne	0xd3e1ec <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x1b0>
  d3e19c: a9484ff4     	ldp	x20, x19, [sp, #0x80]
  d3e1a0: a94757f6     	ldp	x22, x21, [sp, #0x70]
  d3e1a4: a9465ffe     	ldp	x30, x23, [sp, #0x60]
  d3e1a8: 910243ff     	add	sp, sp, #0x90
  d3e1ac: d65f03c0     	ret
  d3e1b0: 14000004     	b	0xd3e1c0 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x184>
  d3e1b4: aa0003f4     	mov	x20, x0
  d3e1b8: aa1603e0     	mov	x0, x22
  d3e1bc: 14000003     	b	0xd3e1c8 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x18c>
  d3e1c0: aa0003f4     	mov	x20, x0
  d3e1c4: aa1503e0     	mov	x0, x21
  d3e1c8: aa1f03e1     	mov	x1, xzr
  d3e1cc: 52800202     	mov	w2, #0x10               // =16
  d3e1d0: 94168df4     	bl	0x12e19a0 <_ZdlPvP16mmMemoryDummyArgm@plt>
  d3e1d4: f94016e8     	ldr	x8, [x23, #0x28]
  d3e1d8: f9402fe9     	ldr	x9, [sp, #0x58]
  d3e1dc: eb09011f     	cmp	x8, x9
  d3e1e0: 54000061     	b.ne	0xd3e1ec <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x1b0>
  d3e1e4: aa1403e0     	mov	x0, x20
  d3e1e8: 941622b3     	bl	0x12c6cb4 <mmRenderManager::WaitReady4RenderThread()+0x1ba4>
  d3e1ec: 94163411     	bl	0x12cb230 <__stack_chk_fail@plt>
  d3e1f0: 7100043f     	cmp	w1, #0x1
  d3e1f4: aa0003f4     	mov	x20, x0
  d3e1f8: 54fffee1     	b.ne	0xd3e1d4 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x198>
  d3e1fc: aa1403e0     	mov	x0, x20
  d3e200: 941636f8     	bl	0x12cbde0 <__cxa_begin_catch@plt>
  d3e204: f9400268     	ldr	x8, [x19]
  d3e208: f9401108     	ldr	x8, [x8, #0x20]
  d3e20c: aa1303e0     	mov	x0, x19
  d3e210: d63f0100     	blr	x8
  d3e214: 9416cd5f     	bl	0x12f1790 <__cxa_end_catch@plt>
  d3e218: 17ffffc6     	b	0xd3e130 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0xf4>
  d3e21c: aa0003f4     	mov	x20, x0
  d3e220: 9416cd5c     	bl	0x12f1790 <__cxa_end_catch@plt>
  d3e224: 17ffffec     	b	0xd3e1d4 <mmGPUDevice_Android::InitializeRenderSystem(mmDeviceDesc const&)+0x198>
  d3e228: 97f842ef     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>

0000000000d3e22c <ns1::emIf_Scroll(ns1::cmnEventData*)>:
  d3e22c: a9be7bfd     	stp	x29, x30, [sp, #-0x20]!
