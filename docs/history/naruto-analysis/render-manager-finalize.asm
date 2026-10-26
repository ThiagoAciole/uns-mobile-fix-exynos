
work\decoded\lib\arm64-v8a\libultimateninjastorm.so:	file format elf64-littleaarch64

Disassembly of section .text:

00000000011b48cc <mmRenderManager_Vulkan::Finalize()>:
 11b48cc: d10143ff     	sub	sp, sp, #0x50
 11b48d0: f9000bfe     	str	x30, [sp, #0x10]
 11b48d4: a9025ff8     	stp	x24, x23, [sp, #0x20]
 11b48d8: a90357f6     	stp	x22, x21, [sp, #0x30]
 11b48dc: a9044ff4     	stp	x20, x19, [sp, #0x40]
 11b48e0: d53bd057     	mrs	x23, TPIDR_EL0
 11b48e4: aa0003f3     	mov	x19, x0
 11b48e8: 91400c14     	add	x20, x0, #0x3, lsl #12  // =0x3000
 11b48ec: f94016e8     	ldr	x8, [x23, #0x28]
 11b48f0: f90007e8     	str	x8, [sp, #0x8]
 11b48f4: 52865408     	mov	w8, #0x32a0             // =12960
 11b48f8: 8b080000     	add	x0, x0, x8
 11b48fc: 390aca9f     	strb	wzr, [x20, #0x2b2]
 11b4900: 94055474     	bl	0x1309ad0 <_ZN12mmThreadCond6SignalEv@plt>
 11b4904: 52865308     	mov	w8, #0x3298             // =12952
 11b4908: 8b080260     	add	x0, x19, x8
 11b490c: 94059ee5     	bl	0x131c4a0 <_ZN8mmThread10WaitForEndER14mmThreadHandle@plt>
 11b4910: 52866008     	mov	w8, #0x3300             // =13056
 11b4914: 390c729f     	strb	wzr, [x20, #0x31c]
 11b4918: 8b080260     	add	x0, x19, x8
 11b491c: 9405546d     	bl	0x1309ad0 <_ZN12mmThreadCond6SignalEv@plt>
 11b4920: 52866108     	mov	w8, #0x3308             // =13064
 11b4924: 8b080260     	add	x0, x19, x8
 11b4928: 9405546a     	bl	0x1309ad0 <_ZN12mmThreadCond6SignalEv@plt>
 11b492c: 52866408     	mov	w8, #0x3320             // =13088
 11b4930: 8b080260     	add	x0, x19, x8
 11b4934: 94059edb     	bl	0x131c4a0 <_ZN8mmThread10WaitForEndER14mmThreadHandle@plt>
 11b4938: aa1303e0     	mov	x0, x19
 11b493c: 9405a581     	bl	0x131df40 <_ZN22mmRenderManager_Vulkan22FinalizeThreadLocalAllEv@plt>
 11b4940: f956ce74     	ldr	x20, [x19, #0x2d98]
 11b4944: f956d275     	ldr	x21, [x19, #0x2da0]
 11b4948: f956da68     	ldr	x8, [x19, #0x2db0]
 11b494c: eb15029f     	cmp	x20, x21
 11b4950: f916de68     	str	x8, [x19, #0x2db8]
 11b4954: 540000e0     	b.eq	0x11b4970 <mmRenderManager_Vulkan::Finalize()+0xa4>
 11b4958: f9400e81     	ldr	x1, [x20, #0x18]
 11b495c: b5001741     	cbnz	x1, 0x11b4c44 <mmRenderManager_Vulkan::Finalize()+0x378>
 11b4960: 91008294     	add	x20, x20, #0x20
 11b4964: eb15029f     	cmp	x20, x21
 11b4968: 54ffff81     	b.ne	0x11b4958 <mmRenderManager_Vulkan::Finalize()+0x8c>
 11b496c: f956ce74     	ldr	x20, [x19, #0x2d98]
 11b4970: f956c275     	ldr	x21, [x19, #0x2d80]
 11b4974: f956c676     	ldr	x22, [x19, #0x2d88]
 11b4978: f916d274     	str	x20, [x19, #0x2da0]
 11b497c: eb1602bf     	cmp	x21, x22
 11b4980: 540000e0     	b.eq	0x11b499c <mmRenderManager_Vulkan::Finalize()+0xd0>
 11b4984: f9400ea1     	ldr	x1, [x21, #0x18]
 11b4988: b5001641     	cbnz	x1, 0x11b4c50 <mmRenderManager_Vulkan::Finalize()+0x384>
 11b498c: 910082b5     	add	x21, x21, #0x20
 11b4990: eb1602bf     	cmp	x21, x22
 11b4994: 54ffff81     	b.ne	0x11b4984 <mmRenderManager_Vulkan::Finalize()+0xb8>
 11b4998: f956c275     	ldr	x21, [x19, #0x2d80]
 11b499c: f956b276     	ldr	x22, [x19, #0x2d60]
 11b49a0: f956b674     	ldr	x20, [x19, #0x2d68]
 11b49a4: f916c675     	str	x21, [x19, #0x2d88]
 11b49a8: eb1402df     	cmp	x22, x20
 11b49ac: 540000e0     	b.eq	0x11b49c8 <mmRenderManager_Vulkan::Finalize()+0xfc>
 11b49b0: f9400ec1     	ldr	x1, [x22, #0x18]
 11b49b4: b5001541     	cbnz	x1, 0x11b4c5c <mmRenderManager_Vulkan::Finalize()+0x390>
 11b49b8: 910082d6     	add	x22, x22, #0x20
 11b49bc: eb1402df     	cmp	x22, x20
 11b49c0: 54ffff81     	b.ne	0x11b49b0 <mmRenderManager_Vulkan::Finalize()+0xe4>
 11b49c4: f956b276     	ldr	x22, [x19, #0x2d60]
 11b49c8: f9568e74     	ldr	x20, [x19, #0x2d18]
 11b49cc: f9569275     	ldr	x21, [x19, #0x2d20]
 11b49d0: f916b676     	str	x22, [x19, #0x2d68]
 11b49d4: eb15029f     	cmp	x20, x21
 11b49d8: 540000e0     	b.eq	0x11b49f4 <mmRenderManager_Vulkan::Finalize()+0x128>
 11b49dc: aa1403e0     	mov	x0, x20
 11b49e0: 9405a53c     	bl	0x131ded0 <_ZN2vk12UniqueHandleINS_5FenceENS_20DispatchLoaderStaticEED2Ev@plt>
 11b49e4: 91008294     	add	x20, x20, #0x20
 11b49e8: eb15029f     	cmp	x20, x21
 11b49ec: 54ffff81     	b.ne	0x11b49dc <mmRenderManager_Vulkan::Finalize()+0x110>
 11b49f0: f9568e74     	ldr	x20, [x19, #0x2d18]
 11b49f4: f9566275     	ldr	x21, [x19, #0x2cc0]
 11b49f8: f9565e76     	ldr	x22, [x19, #0x2cb8]
 11b49fc: f9169274     	str	x20, [x19, #0x2d20]
 11b4a00: eb1602bf     	cmp	x21, x22
 11b4a04: 540000c0     	b.eq	0x11b4a1c <mmRenderManager_Vulkan::Finalize()+0x150>
 11b4a08: d10082b5     	sub	x21, x21, #0x20
 11b4a0c: aa1503e0     	mov	x0, x21
 11b4a10: 9405a550     	bl	0x131df50 <_ZN2vk12UniqueHandleINS_13CommandBufferENS_20DispatchLoaderStaticEED2Ev@plt>
 11b4a14: eb1602bf     	cmp	x21, x22
 11b4a18: 54ffff81     	b.ne	0x11b4a08 <mmRenderManager_Vulkan::Finalize()+0x13c>
 11b4a1c: 52859308     	mov	w8, #0x2c98             // =11416
 11b4a20: 910003e1     	mov	x1, sp
 11b4a24: f9166276     	str	x22, [x19, #0x2cc0]
 11b4a28: 8b080260     	add	x0, x19, x8
 11b4a2c: f90003ff     	str	xzr, [sp]
 11b4a30: 9405a54c     	bl	0x131df60 <_ZN2vk12UniqueHandleINS_11CommandPoolENS_20DispatchLoaderStaticEE5resetERKS1_@plt>
 11b4a34: f9564274     	ldr	x20, [x19, #0x2c80]
 11b4a38: f9564675     	ldr	x21, [x19, #0x2c88]
 11b4a3c: eb15029f     	cmp	x20, x21
 11b4a40: 54000260     	b.eq	0x11b4a8c <mmRenderManager_Vulkan::Finalize()+0x1c0>
 11b4a44: aa1403e0     	mov	x0, x20
 11b4a48: 9405a0ae     	bl	0x131cd00 <_ZN23mmGPUFramebuffer_Vulkan7ReleaseEv@plt>
 11b4a4c: f9405e81     	ldr	x1, [x20, #0xb8]
 11b4a50: b50010e1     	cbnz	x1, 0x11b4c6c <mmRenderManager_Vulkan::Finalize()+0x3a0>
 11b4a54: f9404e81     	ldr	x1, [x20, #0x98]
 11b4a58: b5001101     	cbnz	x1, 0x11b4c78 <mmRenderManager_Vulkan::Finalize()+0x3ac>
 11b4a5c: f9403e81     	ldr	x1, [x20, #0x78]
 11b4a60: b5001121     	cbnz	x1, 0x11b4c84 <mmRenderManager_Vulkan::Finalize()+0x3b8>
 11b4a64: f9402280     	ldr	x0, [x20, #0x40]
 11b4a68: b50000a0     	cbnz	x0, 0x11b4a7c <mmRenderManager_Vulkan::Finalize()+0x1b0>
 11b4a6c: 91030294     	add	x20, x20, #0xc0
 11b4a70: eb15029f     	cmp	x20, x21
 11b4a74: 54fffe81     	b.ne	0x11b4a44 <mmRenderManager_Vulkan::Finalize()+0x178>
 11b4a78: 14000004     	b	0x11b4a88 <mmRenderManager_Vulkan::Finalize()+0x1bc>
 11b4a7c: f9002680     	str	x0, [x20, #0x48]
 11b4a80: 94045bb0     	bl	0x12cb940 <_ZdlPv@plt>
 11b4a84: 17fffffa     	b	0x11b4a6c <mmRenderManager_Vulkan::Finalize()+0x1a0>
 11b4a88: f9564274     	ldr	x20, [x19, #0x2c80]
 11b4a8c: 91036260     	add	x0, x19, #0xd8
 11b4a90: f9164674     	str	x20, [x19, #0x2c88]
 11b4a94: 9405a0b3     	bl	0x131cd60 <_ZN22mmGPURenderPass_Vulkan7ReleaseEv@plt>
 11b4a98: f9406a74     	ldr	x20, [x19, #0xd0]
 11b4a9c: f9400288     	ldr	x8, [x20]
 11b4aa0: aa1403e0     	mov	x0, x20
 11b4aa4: f9400108     	ldr	x8, [x8]
 11b4aa8: d63f0100     	blr	x8
 11b4aac: aa1403e0     	mov	x0, x20
 11b4ab0: 94047c64     	bl	0x12d3c40 <_Z12mmEngineFreePv@plt>
 11b4ab4: a94bd674     	ldp	x20, x21, [x19, #0xb8]
 11b4ab8: f9006a7f     	str	xzr, [x19, #0xd0]
 11b4abc: eb1402bf     	cmp	x21, x20
 11b4ac0: 540005e1     	b.ne	0x11b4b7c <mmRenderManager_Vulkan::Finalize()+0x2b0>
 11b4ac4: f9405268     	ldr	x8, [x19, #0xa0]
 11b4ac8: 91020260     	add	x0, x19, #0x80
 11b4acc: 910003e1     	mov	x1, sp
 11b4ad0: f9006274     	str	x20, [x19, #0xc0]
 11b4ad4: f9005668     	str	x8, [x19, #0xa8]
 11b4ad8: f90003ff     	str	xzr, [sp]
 11b4adc: 9405a525     	bl	0x131df70 <_ZN2vk12UniqueHandleINS_12SwapchainKHRENS_20DispatchLoaderStaticEE5resetERKS1_@plt>
 11b4ae0: 91016260     	add	x0, x19, #0x58
 11b4ae4: 910003e1     	mov	x1, sp
 11b4ae8: f90003ff     	str	xzr, [sp]
 11b4aec: 9405a525     	bl	0x131df80 <_ZN2vk12UniqueHandleINS_10SurfaceKHRENS_20DispatchLoaderStaticEE5resetERKS1_@plt>
 11b4af0: 91010260     	add	x0, x19, #0x40
 11b4af4: 910003e1     	mov	x1, sp
 11b4af8: f90003ff     	str	xzr, [sp]
 11b4afc: 9405a525     	bl	0x131df90 <_ZN2vk12UniqueHandleINS_8InstanceENS_20DispatchLoaderStaticEE5resetERKS1_@plt>
 11b4b00: 52863a08     	mov	w8, #0x31d0             // =12752
 11b4b04: f958ee75     	ldr	x21, [x19, #0x31d8]
 11b4b08: 8b080274     	add	x20, x19, x8
 11b4b0c: eb1402bf     	cmp	x21, x20
 11b4b10: 54000480     	b.eq	0x11b4ba0 <mmRenderManager_Vulkan::Finalize()+0x2d4>
 11b4b14: 52863f18     	mov	w24, #0x31f8            // =12792
 11b4b18: f94016b6     	ldr	x22, [x21, #0x28]
 11b4b1c: b5000256     	cbnz	x22, 0x11b4b64 <mmRenderManager_Vulkan::Finalize()+0x298>
 11b4b20: f958fa68     	ldr	x8, [x19, #0x31f0]
 11b4b24: aa1503e0     	mov	x0, x21
 11b4b28: d1000508     	sub	x8, x8, #0x1
 11b4b2c: f918fa68     	str	x8, [x19, #0x31f0]
 11b4b30: 940553d8     	bl	0x1309a90 <_ZN5eastl15RBTreeIncrementEPKNS_16rbtree_node_baseE@plt>
 11b4b34: aa0003f6     	mov	x22, x0
 11b4b38: aa1503e0     	mov	x0, x21
 11b4b3c: aa1403e1     	mov	x1, x20
 11b4b40: 94055ab0     	bl	0x130b600 <_ZN5eastl11RBTreeEraseEPNS_16rbtree_node_baseES1_@plt>
 11b4b44: 8b180260     	add	x0, x19, x24
 11b4b48: aa1503e1     	mov	x1, x21
 11b4b4c: 52800602     	mov	w2, #0x30               // =48
 11b4b50: 94054f00     	bl	0x1308750 <_ZN5eastl9allocator10deallocateEPvm@plt>
 11b4b54: eb1402df     	cmp	x22, x20
 11b4b58: aa1603f5     	mov	x21, x22
 11b4b5c: 54fffde1     	b.ne	0x11b4b18 <mmRenderManager_Vulkan::Finalize()+0x24c>
 11b4b60: 14000010     	b	0x11b4ba0 <mmRenderManager_Vulkan::Finalize()+0x2d4>
 11b4b64: aa1603e0     	mov	x0, x22
 11b4b68: 9405a50e     	bl	0x131dfa0 <_ZN2vk12UniqueHandleINS_8PipelineENS_20DispatchLoaderStaticEED2Ev@plt>
 11b4b6c: aa1603e0     	mov	x0, x22
 11b4b70: 94047c34     	bl	0x12d3c40 <_Z12mmEngineFreePv@plt>
 11b4b74: f90016bf     	str	xzr, [x21, #0x28]
 11b4b78: 17ffffea     	b	0x11b4b20 <mmRenderManager_Vulkan::Finalize()+0x254>
 11b4b7c: f85f82a1     	ldur	x1, [x21, #-0x8]
 11b4b80: b50000a1     	cbnz	x1, 0x11b4b94 <mmRenderManager_Vulkan::Finalize()+0x2c8>
 11b4b84: d10082b5     	sub	x21, x21, #0x20
 11b4b88: eb1402bf     	cmp	x21, x20
 11b4b8c: 54ffff81     	b.ne	0x11b4b7c <mmRenderManager_Vulkan::Finalize()+0x2b0>
 11b4b90: 17ffffcd     	b	0x11b4ac4 <mmRenderManager_Vulkan::Finalize()+0x1f8>
 11b4b94: a97e0aa0     	ldp	x0, x2, [x21, #-0x20]
 11b4b98: 9404f836     	bl	0x12f2c70 <vkDestroyImageView@plt>
 11b4b9c: 17fffffa     	b	0x11b4b84 <mmRenderManager_Vulkan::Finalize()+0x2b8>
 11b4ba0: 52864008     	mov	w8, #0x3200             // =12800
 11b4ba4: f9590675     	ldr	x21, [x19, #0x3208]
 11b4ba8: 8b080274     	add	x20, x19, x8
 11b4bac: eb1402bf     	cmp	x21, x20
 11b4bb0: 54000360     	b.eq	0x11b4c1c <mmRenderManager_Vulkan::Finalize()+0x350>
 11b4bb4: 52864518     	mov	w24, #0x3228            // =12840
 11b4bb8: f94016b6     	ldr	x22, [x21, #0x28]
 11b4bbc: b5000256     	cbnz	x22, 0x11b4c04 <mmRenderManager_Vulkan::Finalize()+0x338>
 11b4bc0: f9591268     	ldr	x8, [x19, #0x3220]
 11b4bc4: aa1503e0     	mov	x0, x21
 11b4bc8: d1000508     	sub	x8, x8, #0x1
 11b4bcc: f9191268     	str	x8, [x19, #0x3220]
 11b4bd0: 940553b0     	bl	0x1309a90 <_ZN5eastl15RBTreeIncrementEPKNS_16rbtree_node_baseE@plt>
 11b4bd4: aa0003f6     	mov	x22, x0
 11b4bd8: aa1503e0     	mov	x0, x21
 11b4bdc: aa1403e1     	mov	x1, x20
 11b4be0: 94055a88     	bl	0x130b600 <_ZN5eastl11RBTreeEraseEPNS_16rbtree_node_baseES1_@plt>
 11b4be4: 8b180260     	add	x0, x19, x24
 11b4be8: aa1503e1     	mov	x1, x21
 11b4bec: 52800602     	mov	w2, #0x30               // =48
 11b4bf0: 94054ed8     	bl	0x1308750 <_ZN5eastl9allocator10deallocateEPvm@plt>
 11b4bf4: eb1402df     	cmp	x22, x20
 11b4bf8: aa1603f5     	mov	x21, x22
 11b4bfc: 54fffde1     	b.ne	0x11b4bb8 <mmRenderManager_Vulkan::Finalize()+0x2ec>
 11b4c00: 14000007     	b	0x11b4c1c <mmRenderManager_Vulkan::Finalize()+0x350>
 11b4c04: aa1603e0     	mov	x0, x22
 11b4c08: 9405a4e6     	bl	0x131dfa0 <_ZN2vk12UniqueHandleINS_8PipelineENS_20DispatchLoaderStaticEED2Ev@plt>
 11b4c0c: aa1603e0     	mov	x0, x22
 11b4c10: 94047c0c     	bl	0x12d3c40 <_Z12mmEngineFreePv@plt>
 11b4c14: f90016bf     	str	xzr, [x21, #0x28]
 11b4c18: 17ffffea     	b	0x11b4bc0 <mmRenderManager_Vulkan::Finalize()+0x2f4>
 11b4c1c: f94016e8     	ldr	x8, [x23, #0x28]
 11b4c20: f94007e9     	ldr	x9, [sp, #0x8]
 11b4c24: eb09011f     	cmp	x8, x9
 11b4c28: 54000201     	b.ne	0x11b4c68 <mmRenderManager_Vulkan::Finalize()+0x39c>
 11b4c2c: a9444ff4     	ldp	x20, x19, [sp, #0x40]
 11b4c30: f9400bfe     	ldr	x30, [sp, #0x10]
 11b4c34: a94357f6     	ldp	x22, x21, [sp, #0x30]
 11b4c38: a9425ff8     	ldp	x24, x23, [sp, #0x20]
 11b4c3c: 910143ff     	add	sp, sp, #0x50
 11b4c40: d65f03c0     	ret
 11b4c44: a9400a80     	ldp	x0, x2, [x20]
 11b4c48: 9404f826     	bl	0x12f2ce0 <vkDestroySemaphore@plt>
 11b4c4c: 17ffff45     	b	0x11b4960 <mmRenderManager_Vulkan::Finalize()+0x94>
 11b4c50: a9400aa0     	ldp	x0, x2, [x21]
 11b4c54: 9404f823     	bl	0x12f2ce0 <vkDestroySemaphore@plt>
 11b4c58: 17ffff4d     	b	0x11b498c <mmRenderManager_Vulkan::Finalize()+0xc0>
 11b4c5c: a9400ac0     	ldp	x0, x2, [x22]
 11b4c60: 9404f820     	bl	0x12f2ce0 <vkDestroySemaphore@plt>
 11b4c64: 17ffff55     	b	0x11b49b8 <mmRenderManager_Vulkan::Finalize()+0xec>
 11b4c68: 94045972     	bl	0x12cb230 <__stack_chk_fail@plt>
 11b4c6c: a94a0a80     	ldp	x0, x2, [x20, #0xa0]
 11b4c70: 9404f944     	bl	0x12f3180 <vkDestroyFramebuffer@plt>
 11b4c74: 17ffff78     	b	0x11b4a54 <mmRenderManager_Vulkan::Finalize()+0x188>
 11b4c78: a9480a80     	ldp	x0, x2, [x20, #0x80]
 11b4c7c: 9404f941     	bl	0x12f3180 <vkDestroyFramebuffer@plt>
 11b4c80: 17ffff77     	b	0x11b4a5c <mmRenderManager_Vulkan::Finalize()+0x190>
 11b4c84: a9460a80     	ldp	x0, x2, [x20, #0x60]
 11b4c88: 9404f93e     	bl	0x12f3180 <vkDestroyFramebuffer@plt>
 11b4c8c: 17ffff76     	b	0x11b4a64 <mmRenderManager_Vulkan::Finalize()+0x198>
 11b4c90: 97e66855     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>
 11b4c94: 97e66854     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>
 11b4c98: 97e66853     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>
 11b4c9c: 97e66852     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>
 11b4ca0: 97e66851     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>
 11b4ca4: 97e66850     	bl	0xb4ede4 <mmDrawCommand_BindShaderBuffer::~mmDrawCommand_BindShaderBuffer()+0x90>

00000000011b4ca8 <mmRenderManager_Vulkan::~mmRenderManager_Vulkan()>:
 11b4ca8: a9bf4ffe     	stp	x30, x19, [sp, #-0x10]!
 11b4cac: aa0003f3     	mov	x19, x0
 11b4cb0: 9405a4c0     	bl	0x131dfb0 <_ZN22mmRenderManager_VulkanD1Ev@plt>
 11b4cb4: aa1303e0     	mov	x0, x19
 11b4cb8: a8c14ffe     	ldp	x30, x19, [sp], #0x10
 11b4cbc: 14045b21     	b	0x12cb940 <_ZdlPv@plt>

00000000011b4cc0 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)>:
 11b4cc0: d101c3ff     	sub	sp, sp, #0x70
 11b4cc4: f90023fe     	str	x30, [sp, #0x40]
 11b4cc8: a90557f6     	stp	x22, x21, [sp, #0x50]
 11b4ccc: a9064ff4     	stp	x20, x19, [sp, #0x60]
 11b4cd0: d53bd055     	mrs	x21, TPIDR_EL0
 11b4cd4: b0001049     	adrp	x9, 0x13bd000
 11b4cd8: b000104a     	adrp	x10, 0x13bd000
 11b4cdc: f94016a8     	ldr	x8, [x21, #0x28]
 11b4ce0: f9428529     	ldr	x9, [x9, #0x508]
 11b4ce4: aa0003f3     	mov	x19, x0
 11b4ce8: f9001fe8     	str	x8, [sp, #0x38]
 11b4cec: 5285bb08     	mov	w8, #0x2dd8             // =11736
 11b4cf0: 79400129     	ldrh	w9, [x9]
 11b4cf4: f942814a     	ldr	x10, [x10, #0x500]
 11b4cf8: 8b080016     	add	x22, x0, x8
 11b4cfc: 790002c9     	strh	w9, [x22]
 11b4d00: 79400148     	ldrh	w8, [x10]
 11b4d04: 79000ac9     	strh	w9, [x22, #0x4]
 11b4d08: 790006c8     	strh	w8, [x22, #0x2]
 11b4d0c: 79000ec8     	strh	w8, [x22, #0x6]
 11b4d10: b9401428     	ldr	w8, [x1, #0x14]
 11b4d14: 7100511f     	cmp	w8, #0x14
 11b4d18: 54000120     	b.eq	0x11b4d3c <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x7c>
 11b4d1c: 7100f11f     	cmp	w8, #0x3c
 11b4d20: 540000a0     	b.eq	0x11b4d34 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x74>
 11b4d24: 7100791f     	cmp	w8, #0x1e
 11b4d28: 540000e1     	b.ne	0x11b4d44 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x84>
 11b4d2c: 52800028     	mov	w8, #0x1                // =1
 11b4d30: 14000004     	b	0x11b4d40 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x80>
 11b4d34: 2a1f03e8     	mov	w8, wzr
 11b4d38: 14000002     	b	0x11b4d40 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x80>
 11b4d3c: 52800048     	mov	w8, #0x2                // =2
 11b4d40: b92e4268     	str	w8, [x19, #0x2e40]
 11b4d44: 910043e8     	add	x8, sp, #0x10
 11b4d48: 910043f4     	add	x20, sp, #0x10
 11b4d4c: 940599ad     	bl	0x131b400 <_ZN9mmAndroid4util12GetModelNameEv@plt>
 11b4d50: 39409fe9     	ldrb	w9, [sp, #0x27]
 11b4d54: f9400fea     	ldr	x10, [sp, #0x18]
 11b4d58: 528002eb     	mov	w11, #0x17              // =23
 11b4d5c: 13001d28     	sxtb	w8, w9
 11b4d60: cb090169     	sub	x9, x11, x9
 11b4d64: 7100011f     	cmp	w8, #0x0
 11b4d68: 9a89b149     	csel	x9, x10, x9, lt
 11b4d6c: f100153f     	cmp	x9, #0x5
 11b4d70: 54000320     	b.eq	0x11b4dd4 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x114>
 11b4d74: f100193f     	cmp	x9, #0x6
 11b4d78: 54000481     	b.ne	0x11b4e08 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x148>
 11b4d7c: f9400be9     	ldr	x9, [sp, #0x10]
 11b4d80: 7100011f     	cmp	w8, #0x0
 11b4d84: 910043ea     	add	x10, sp, #0x10
 11b4d88: 9a8ab12b     	csel	x11, x9, x10, lt
 11b4d8c: 5289ea69     	mov	w9, #0x4f53             // =20307
 11b4d90: b940016c     	ldr	w12, [x11]
 11b4d94: 72a605a9     	movk	w9, #0x302d, lsl #16
 11b4d98: 7940096b     	ldrh	w11, [x11, #0x4]
 11b4d9c: 6b09019f     	cmp	w12, w9
 11b4da0: 5289662c     	mov	w12, #0x4b31            // =19249
 11b4da4: 7a4c0160     	ccmp	w11, w12, #0x0, eq
 11b4da8: 540002c0     	b.eq	0x11b4e00 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x140>
 11b4dac: f9400beb     	ldr	x11, [sp, #0x10]
 11b4db0: 7100011f     	cmp	w8, #0x0
 11b4db4: 9a8ab168     	csel	x8, x11, x10, lt
 11b4db8: b940010a     	ldr	w10, [x8]
 11b4dbc: 79400908     	ldrh	w8, [x8, #0x4]
 11b4dc0: 6b09015f     	cmp	w10, w9
 11b4dc4: 52896649     	mov	w9, #0x4b32             // =19250
 11b4dc8: 7a490100     	ccmp	w8, w9, #0x0, eq
 11b4dcc: 540001e1     	b.ne	0x11b4e08 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x148>
 11b4dd0: 1400000c     	b	0x11b4e00 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x140>
 11b4dd4: f9400be9     	ldr	x9, [sp, #0x10]
 11b4dd8: 7100011f     	cmp	w8, #0x0
 11b4ddc: 5289ea6a     	mov	w10, #0x4f53            // =20307
 11b4de0: 72a66aca     	movk	w10, #0x3356, lsl #16
 11b4de4: 9a94b128     	csel	x8, x9, x20, lt
 11b4de8: b9400109     	ldr	w9, [x8]
 11b4dec: 39401108     	ldrb	w8, [x8, #0x4]
 11b4df0: 6b0a013f     	cmp	w9, w10
 11b4df4: 528006c9     	mov	w9, #0x36               // =54
 11b4df8: 7a490100     	ccmp	w8, w9, #0x0, eq
 11b4dfc: 54000061     	b.ne	0x11b4e08 <mmRenderManager_Vulkan::Initialize(mmDeviceDesc const&)+0x148>
 11b4e00: 52800028     	mov	w8, #0x1                // =1
 11b4e04: 3912f2c8     	strb	w8, [x22, #0x4bc]
 11b4e08: d0001068     	adrp	x8, 0x13c2000
 11b4e0c: d0001069     	adrp	x9, 0x13c2000
 11b4e10: d000106a     	adrp	x10, 0x13c2000
 11b4e14: f946a108     	ldr	x8, [x8, #0xd40]
 11b4e18: f9191e73     	str	x19, [x19, #0x3238]
 11b4e1c: f946a529     	ldr	x9, [x9, #0xd48]
 11b4e20: f946a94a     	ldr	x10, [x10, #0xd50]
 11b4e24: f9192268     	str	x8, [x19, #0x3240]
 11b4e28: f9192669     	str	x9, [x19, #0x3248]
 11b4e2c: f9192a6a     	str	x10, [x19, #0x3250]
 11b4e30: aa1303e0     	mov	x0, x19
 11b4e34: 9405a46b     	bl	0x131dfe0 <_ZN22mmRenderManager_Vulkan13CreateSurfaceEv@plt>
 11b4e38: aa1303e0     	mov	x0, x19
 11b4e3c: 9405a46d     	bl	0x131dff0 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv@plt>
 11b4e40: 52864f14     	mov	w20, #0x3278            // =12920
 11b4e44: 8b140260     	add	x0, x19, x20
 11b4e48: 940552ce     	bl	0x1309980 <_ZN7mmMutex4LockEv@plt>
 11b4e4c: d0001060     	adrp	x0, 0x13c2000
 11b4e50: f9469800     	ldr	x0, [x0, #0xd30]
 11b4e54: 940459bf     	bl	0x12cb550 <__emutls_get_address@plt>
 11b4e58: b9727268     	ldr	w8, [x19, #0x3270]
 11b4e5c: 11000509     	add	w9, w8, #0x1
 11b4e60: b9327269     	str	w9, [x19, #0x3270]
 11b4e64: b9000008     	str	w8, [x0]
 11b4e68: d0001060     	adrp	x0, 0x13c2000
 11b4e6c: f946ac00     	ldr	x0, [x0, #0xd58]
 11b4e70: 940459b8     	bl	0x12cb550 <__emutls_get_address@plt>
 11b4e74: 3900001f     	strb	wzr, [x0]
 11b4e78: 8b140260     	add	x0, x19, x20
 11b4e7c: 940552c5     	bl	0x1309990 <_ZN7mmMutex6UnlockEv@plt>
 11b4e80: 90001068     	adrp	x8, 0x13c0000
 11b4e84: f9422d08     	ldr	x8, [x8, #0x458]
 11b4e88: f9400108     	ldr	x8, [x8]
 11b4e8c: f9400500     	ldr	x0, [x8, #0x8]
 11b4e90: 94059f74     	bl	0x131cc60 <_ZN19mmGPUDevice_Android20InitializeMainThreadEv@plt>
 11b4e94: aa1303e0     	mov	x0, x19
 11b4e98: 9405a45a     	bl	0x131e000 <_ZNK22mmRenderManager_Vulkan17CreateThreadLocalEv@plt>
 11b4e9c: aa1303e0     	mov	x0, x19
 11b4ea0: 9405a45c     	bl	0x131e010 <_ZN22mmRenderManager_Vulkan17CreateDepthBufferEv@plt>
 11b4ea4: aa1303e0     	mov	x0, x19
 11b4ea8: 9405a45e     	bl	0x131e020 <_ZN22mmRenderManager_Vulkan16CreateRenderPassEv@plt>
 11b4eac: aa1303e0     	mov	x0, x19
 11b4eb0: 9405a460     	bl	0x131e030 <_ZN22mmRenderManager_Vulkan17CreateFramebufferEv@plt>
 11b4eb4: aa1303e0     	mov	x0, x19
 11b4eb8: 9405a462     	bl	0x131e040 <_ZN22mmRenderManager_Vulkan19CreateCommandBufferEv@plt>
 11b4ebc: aa1303e0     	mov	x0, x19
 11b4ec0: 9405a464     	bl	0x131e050 <_ZN22mmRenderManager_Vulkan30InitializeSwapchainImageLayoutEv@plt>
 11b4ec4: aa1303e0     	mov	x0, x19
 11b4ec8: 9405a466     	bl	0x131e060 <_ZN22mmRenderManager_Vulkan26InitializeGraphicsPipelineEv@plt>
 11b4ecc: 52800200     	mov	w0, #0x10               // =16
 11b4ed0: 9405533c     	bl	0x1309bc0 <_Z18mmIsAlignSizeValidm@plt>
 11b4ed4: f0001049     	adrp	x9, 0x13bf000
 11b4ed8: b0ffa608     	adrp	x8, 0x675000
 11b4edc: f9418529     	ldr	x9, [x9, #0x308]
 11b4ee0: 3dc30100     	ldr	q0, [x8, #0xc00]
 11b4ee4: 91004128     	add	x8, x9, #0x10
 11b4ee8: 3d8cba60     	str	q0, [x19, #0x32e0]
 11b4eec: f90003e8     	str	x8, [sp]
 11b4ef0: 910003e0     	mov	x0, sp
 11b4ef4: 52800201     	mov	w1, #0x10               // =16
 11b4ef8: 52800202     	mov	w2, #0x10               // =16
 11b4efc: 9404fda5     	bl	0x12f4590 <_ZN14mmAppAllocator8AllocateEmm@plt>
