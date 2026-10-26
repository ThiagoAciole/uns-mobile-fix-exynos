
C:\Users\Thiago Aciole\Projetos\Jogos\naruto-storm-1\naruto-analysis\libultimateninjastorm.so:	file format elf64-littleaarch64

Disassembly of section .text:

00000000011ae91c <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv>:
 11ae91c: d10683ff     	sub	sp, sp, #0x1a0
 11ae920: a9147bfd     	stp	x29, x30, [sp, #0x140]
 11ae924: a9156ffc     	stp	x28, x27, [sp, #0x150]
 11ae928: a91667fa     	stp	x26, x25, [sp, #0x160]
 11ae92c: a9175ff8     	stp	x24, x23, [sp, #0x170]
 11ae930: a91857f6     	stp	x22, x21, [sp, #0x180]
 11ae934: a9194ff4     	stp	x20, x19, [sp, #0x190]
 11ae938: d53bd048     	mrs	x8, TPIDR_EL0
 11ae93c: f0001049     	adrp	x9, 0x13b9000
 11ae940: aa1f03f7     	mov	x23, xzr
 11ae944: f9000fe8     	str	x8, [sp, #0x18]
 11ae948: aa1f03f4     	mov	x20, xzr
 11ae94c: aa1f03f5     	mov	x21, xzr
 11ae950: f9401508     	ldr	x8, [x8, #0x28]
 11ae954: f9462529     	ldr	x9, [x9, #0xc48]
 11ae958: b27deffa     	mov	x26, #0x7ffffffffffffff8 // =9223372036854775800
 11ae95c: 92fc001b     	mov	x27, #0x1fffffffffffffff // =2305843009213693951
 11ae960: f9009fe8     	str	x8, [sp, #0x138]
 11ae964: f9400128     	ldr	x8, [x9]
 11ae968: 91400809     	add	x9, x0, #0x2, lsl #12   // =0x2000
 11ae96c: f9403816     	ldr	x22, [x0, #0x70]
 11ae970: 795bb12a     	ldrh	w10, [x9, #0xdd8]
 11ae974: 795bb529     	ldrh	w9, [x9, #0xdda]
 11ae978: f9000be0     	str	x0, [sp, #0x10]
 11ae97c: f9400508     	ldr	x8, [x8, #0x8]
 11ae980: f9001bea     	str	x10, [sp, #0x30]
 11ae984: f940111d     	ldr	x29, [x8, #0x20]
 11ae988: f90013e9     	str	x9, [sp, #0x20]
 11ae98c: 1400000a     	b	0x11ae9b4 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x98>
 11ae990: 8b080e88     	add	x8, x20, x8, lsl #3
 11ae994: 9a953115     	csel	x21, x8, x21, lo
 11ae998: f94003a0     	ldr	x0, [x29]
 11ae99c: 910183e2     	add	x2, sp, #0x60
 11ae9a0: aa1603e1     	mov	x1, x22
 11ae9a4: aa1403e3     	mov	x3, x20
 11ae9a8: 9404f782     	bl	0x12ec7b0 <vkGetPhysicalDeviceSurfaceFormatsKHR@plt>
 11ae9ac: 7100141f     	cmp	w0, #0x5
 11ae9b0: 54000721     	b.ne	0x11aea94 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x178>
 11ae9b4: f94003a0     	ldr	x0, [x29]
 11ae9b8: 910183e2     	add	x2, sp, #0x60
 11ae9bc: aa1603e1     	mov	x1, x22
 11ae9c0: aa1f03e3     	mov	x3, xzr
 11ae9c4: 9404f77b     	bl	0x12ec7b0 <vkGetPhysicalDeviceSurfaceFormatsKHR@plt>
 11ae9c8: 35ffff20     	cbnz	w0, 0x11ae9ac <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x90>
 11ae9cc: b94063e8     	ldr	w8, [sp, #0x60]
 11ae9d0: 34fffee8     	cbz	w8, 0x11ae9ac <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x90>
 11ae9d4: cb1402b9     	sub	x25, x21, x20
 11ae9d8: 9343ff29     	asr	x9, x25, #3
 11ae9dc: eb090113     	subs	x19, x8, x9
 11ae9e0: 54fffd89     	b.ls	0x11ae990 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x74>
 11ae9e4: cb1502e9     	sub	x9, x23, x21
 11ae9e8: eb890e7f     	cmp	x19, x9, asr #3
 11ae9ec: 54000349     	b.ls	0x11aea54 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x138>
 11ae9f0: cb1402e9     	sub	x9, x23, x20
 11ae9f4: 9342fd2a     	asr	x10, x9, #2
 11ae9f8: eb08015f     	cmp	x10, x8
 11ae9fc: 9a888148     	csel	x8, x10, x8, hi
 11aea00: eb1a013f     	cmp	x9, x26
 11aea04: 9a9b311c     	csel	x28, x8, x27, lo
 11aea08: d37dff88     	lsr	x8, x28, #61
 11aea0c: b5014ae8     	cbnz	x8, 0x11b1368 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x2a4c>
 11aea10: d37df380     	lsl	x0, x28, #3
 11aea14: 94045dcf     	bl	0x12c6150 <_Znwm@plt>
 11aea18: d37df278     	lsl	x24, x19, #3
 11aea1c: 8b190019     	add	x25, x0, x25
 11aea20: aa0003f7     	mov	x23, x0
 11aea24: aa1903e0     	mov	x0, x25
 11aea28: 2a1f03e1     	mov	w1, wzr
 11aea2c: aa1803e2     	mov	x2, x24
 11aea30: 94045a8c     	bl	0x12c5460 <memset@plt>
 11aea34: aa1903f3     	mov	x19, x25
 11aea38: eb1402bf     	cmp	x21, x20
 11aea3c: 540001a1     	b.ne	0x11aea70 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x154>
 11aea40: 8b1c0ef7     	add	x23, x23, x28, lsl #3
 11aea44: 8b180335     	add	x21, x25, x24
 11aea48: b50001f4     	cbnz	x20, 0x11aea84 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x168>
 11aea4c: aa1303f4     	mov	x20, x19
 11aea50: 17ffffd2     	b	0x11ae998 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x7c>
 11aea54: d37df278     	lsl	x24, x19, #3
 11aea58: aa1503e0     	mov	x0, x21
 11aea5c: 2a1f03e1     	mov	w1, wzr
 11aea60: aa1803e2     	mov	x2, x24
 11aea64: 94045a7f     	bl	0x12c5460 <memset@plt>
 11aea68: 8b1802b5     	add	x21, x21, x24
 11aea6c: 17ffffcb     	b	0x11ae998 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x7c>
 11aea70: f85f8ea8     	ldr	x8, [x21, #-0x8]!
 11aea74: eb1402bf     	cmp	x21, x20
 11aea78: f81f8e68     	str	x8, [x19, #-0x8]!
 11aea7c: 54fffe20     	b.eq	0x11aea40 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x124>
 11aea80: 17fffffc     	b	0x11aea70 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x154>
 11aea84: aa1403e0     	mov	x0, x20
 11aea88: 940459aa     	bl	0x12c5130 <_ZdlPv@plt>
 11aea8c: aa1303f4     	mov	x20, x19
 11aea90: 17ffffc2     	b	0x11ae998 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x7c>
 11aea94: 5286bfe8     	mov	w8, #0x35ff             // =13823
 11aea98: 72b88ca8     	movk	w8, #0xc465, lsl #16
 11aea9c: 6b08001f     	cmp	w0, w8
 11aeaa0: 5400206d     	b.le	0x11aeeac <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x590>
 11aeaa4: 11003408     	add	w8, w0, #0xd
 11aeaa8: f9400ffa     	ldr	x26, [sp, #0x18]
 11aeaac: 7100351f     	cmp	w8, #0xd
 11aeab0: 54002d88     	b.hi	0x11af060 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x744>
 11aeab4: b0ffa889     	adrp	x9, 0x6bf000 <g_quadPS+0xc00>
 11aeab8: 911b4129     	add	x9, x9, #0x6d0
 11aeabc: 1000008a     	adr	x10, 0x11aeacc <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x1b0>
 11aeac0: 7868792b     	ldrh	w11, [x9, x8, lsl #1]
 11aeac4: 8b0b094a     	add	x10, x10, x11, lsl #2
 11aeac8: d61f0140     	br	x10
 11aeacc: b94063e8     	ldr	w8, [sp, #0x60]
 11aead0: cb1402a9     	sub	x9, x21, x20
 11aead4: a90d7fff     	stp	xzr, xzr, [sp, #0xd0]
 11aead8: 9343fd29     	asr	x9, x9, #3
 11aeadc: f90067ff     	str	xzr, [sp, #0xc8]
 11aeae0: 8b080e8a     	add	x10, x20, x8, lsl #3
 11aeae4: eb08013f     	cmp	x9, x8
 11aeae8: 9a883123     	csel	x3, x9, x8, lo
 11aeaec: 9a958142     	csel	x2, x10, x21, hi
 11aeaf0: 910323e0     	add	x0, sp, #0xc8
 11aeaf4: aa1403e1     	mov	x1, x20
 11aeaf8: 9405a362     	bl	0x1317880 <_ZNSt6__ndk16vectorIN2vk16SurfaceFormatKHRENS_9allocatorIS2_EEE16__init_with_sizeB8ne180000IPS2_S7_EEvT_T0_m@plt>
 11aeafc: f000105c     	adrp	x28, 0x13b9000
 11aeb00: f9400bfb     	ldr	x27, [sp, #0x10]
 11aeb04: 9103a3fd     	add	x29, sp, #0xe8
 11aeb08: f946279c     	ldr	x28, [x28, #0xc48]
 11aeb0c: b4000074     	cbz	x20, 0x11aeb18 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x1fc>
 11aeb10: aa1403e0     	mov	x0, x20
 11aeb14: 94045987     	bl	0x12c5130 <_ZdlPv@plt>
 11aeb18: f94067e8     	ldr	x8, [sp, #0xc8]
 11aeb1c: 6f00e400     	movi	v0.2d, #0000000000000000
 11aeb20: f9400389     	ldr	x9, [x28]
 11aeb24: f9403b61     	ldr	x1, [x27, #0x70]
 11aeb28: f9400108     	ldr	x8, [x8]
 11aeb2c: f9003f68     	str	x8, [x27, #0x78]
 11aeb30: b0ffa5e8     	adrp	x8, 0x66b000
 11aeb34: f9400529     	ldr	x9, [x9, #0x8]
 11aeb38: ad0303e0     	stp	q0, q0, [sp, #0x60]
 11aeb3c: fd467100     	ldr	d0, [x8, #0xce0]
 11aeb40: f9401128     	ldr	x8, [x9, #0x20]
 11aeb44: f90043ff     	str	xzr, [sp, #0x80]
 11aeb48: fd0047e0     	str	d0, [sp, #0x88]
 11aeb4c: b90093ff     	str	wzr, [sp, #0x90]
 11aeb50: f9400100     	ldr	x0, [x8]
 11aeb54: 910183e2     	add	x2, sp, #0x60
 11aeb58: 9404f74a     	bl	0x12ec880 <vkGetPhysicalDeviceSurfaceCapabilitiesKHR@plt>
 11aeb5c: 35003be0     	cbnz	w0, 0x11af2d8 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x9bc>
 11aeb60: 294c27e8     	ldp	w8, w9, [sp, #0x60]
 11aeb64: f9403b6a     	ldr	x10, [x27, #0x70]
 11aeb68: fd403f60     	ldr	d0, [x27, #0x78]
 11aeb6c: f90037ff     	str	xzr, [sp, #0x68]
 11aeb70: b90073ff     	str	wzr, [sp, #0x70]
 11aeb74: 1100050b     	add	w11, w8, #0x1
 11aeb78: f9003fea     	str	x10, [sp, #0x78]
 11aeb7c: d0ffa5ea     	adrp	x10, 0x66c000
 11aeb80: 6b09017f     	cmp	w11, w9
 11aeb84: fc0843e0     	stur	d0, [sp, #0x84]
 11aeb88: fd44d140     	ldr	d0, [x10, #0x9a0]
 11aeb8c: 7a408924     	ccmp	w9, #0x0, #0x4, hi
 11aeb90: f90057ff     	str	xzr, [sp, #0xa8]
 11aeb94: 1a881528     	csinc	w8, w9, w8, ne
 11aeb98: f94013e9     	ldr	x9, [sp, #0x20]
 11aeb9c: fc0943e0     	stur	d0, [sp, #0x94]
 11aeba0: b90083e8     	str	w8, [sp, #0x80]
 11aeba4: f9401be8     	ldr	x8, [sp, #0x30]
 11aeba8: f90063ff     	str	xzr, [sp, #0xc0]
 11aebac: aa098108     	orr	x8, x8, x9, lsl #32
 11aebb0: 90ffa609     	adrp	x9, 0x66e000
 11aebb4: f809c3ff     	stur	xzr, [sp, #0x9c]
 11aebb8: 3dc28520     	ldr	q0, [x9, #0xa10]
 11aebbc: f90077ff     	str	xzr, [sp, #0xe8]
 11aebc0: f808c3e8     	stur	x8, [sp, #0x8c]
 11aebc4: f9400388     	ldr	x8, [x28]
 11aebc8: 3d802fe0     	str	q0, [sp, #0xb0]
 11aebcc: f9400513     	ldr	x19, [x8, #0x8]
 11aebd0: 5299bd08     	mov	w8, #0xcde8             // =52712
 11aebd4: 72a77348     	movk	w8, #0x3b9a, lsl #16
 11aebd8: f9425a60     	ldr	x0, [x19, #0x4b0]
 11aebdc: b90063e8     	str	w8, [sp, #0x60]
 11aebe0: 910183e1     	add	x1, sp, #0x60
 11aebe4: 9103a3e3     	add	x3, sp, #0xe8
 11aebe8: aa1f03e2     	mov	x2, xzr
 11aebec: 9404f74d     	bl	0x12ec920 <vkCreateSwapchainKHR@plt>
 11aebf0: 35003c20     	cbnz	w0, 0x11af374 <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0xa58>
 11aebf4: f94077e8     	ldr	x8, [sp, #0xe8]
 11aebf8: f9425a73     	ldr	x19, [x19, #0x4b0]
 11aebfc: 91020360     	add	x0, x27, #0x80
 11aec00: 9103a3e1     	add	x1, sp, #0xe8
 11aec04: f90077e8     	str	x8, [sp, #0xe8]
 11aec08: 9405a2d6     	bl	0x1317760 <_ZN2vk12UniqueHandleINS_12SwapchainKHRENS_20DispatchLoaderStaticEE5resetERKS1_@plt>
 11aec0c: d0001075     	adrp	x21, 0x13bc000
 11aec10: f94042b5     	ldr	x21, [x21, #0x80]
 11aec14: f9400388     	ldr	x8, [x28]
 11aec18: a9087f73     	stp	x19, xzr, [x27, #0x80]
 11aec1c: f9404f73     	ldr	x19, [x27, #0x98]
 11aec20: f9004b75     	str	x21, [x27, #0x90]
 11aec24: f9400516     	ldr	x22, [x8, #0x8]
 11aec28: a90effff     	stp	xzr, xzr, [sp, #0xe8]
 11aec2c: f9007fff     	str	xzr, [sp, #0xf8]
 11aec30: 14000007     	b	0x11aec4c <_ZN22mmRenderManager_Vulkan15CreateSwapchainEv+0x330>
 11aec34: f9425ac0     	ldr	x0, [x22, #0x4b0]
 11aec38: 910383e2     	add	x2, sp, #0xe0
 11aec3c: aa1303e1     	mov	x1, x19
