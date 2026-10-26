# Naruto Storm Android — Full-App Widescreen Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` to carry out this plan task by task. Keep the checked items in this file current.

**Goal:** Adapt every playable and menu flow of Naruto Ultimate Ninja Storm 1.2.10 to fill the Galaxy S24 landscape display, with a Hor+ 3D scene, intentionally anchored UI, matching touch regions, preserved pt-BR/Exynos behavior, and no unintended 16:9 regressions.

**Architecture:** Keep display composition, 3D camera, 2D interface, input conversion, texture geometry, and video presentation as separate layers. Identify the active screen route and asset binding before each patch; prefer aspect-aware native geometry and anchors, and alter texture pixels only for a confirmed background or stretchable panel. Build each candidate from a hash-verified canonical APK and validate the signed candidate on the device before promotion.

**Tech Stack:** ARM64 static analysis/patches, Python repository tools, XFBIN/NUCC and AWB/CPK repacking, Android APK signing, ADB read-only inventory and device captures.

**Spec:** `docs/WIDESCREEN_ASSET_MAP.md`, especially “Matriz completa de cobertura do app” and “Critério para declarar o app widescreen completo”.

## Global Constraints

- Package `com.bandainamcoent.ultimateninjastorm`, version `1.2.10`, `versionCode 38`.
- First device target: Galaxy S24, landscape, `2340×1080`; preserve the 16:9 baseline `1920×1080`.
- Keep the accepted APK, original APK, signing identity, pt-BR catalogs, and Exynos fix intact; use a new candidate output for every build.
- Preserve save data; never uninstall or clear data during validation.
- Keep the accepted `ChangeRender` composition correction; reject any candidate that restores a fixed 16:9 destination on the S24 or produces X origin `210`.
- Do not edit a texture atlas, logo, HUD, map, text, or control art based only on its dimensions or appearance; prove the sprite/material/UV and active draw route first.
- No manifest/DEX/API changes. Do not replace the primary APK until device acceptance is complete and explicitly recorded.
- Mark evidence separately as static analysis, host emulation, APK integrity/signature, and real-device visual/input acceptance.

## Review Focus

- A rebuilt screen may still use a second composition route; pin `ChangeRender` and `SetRenderMode` to the device dimensions and test display corners.
- UI and touch can diverge when either path applies a different origin/scale; every changed layout needs forward/inverse transform checks and physical taps.
- Shared atlas pixels may serve multiple screens; prove the active UV before editing and compare unchanged chunks after repack.
- Text expansion in pt-BR can overflow a correctly positioned panel; inspect long strings, accents, and dynamic names per state.
- Fullscreen video and transitions can fill the display while distorting or leaving stale pixels; validate source aspect, alpha/depth, timing, and frame transitions independently.

---

## Work Packages

### Task 0: Reconcile the canonical base and device state

**Files:**
- Read: `docs/WIDESCREEN_COMPOSITION_VALIDATION_20261026.md`
- Read: `docs/WIDESCREEN_FOLLOWUP_RESULT_20261026.md`
- Read: `docs/PROGRESS.md`
- Record: `work/candidates/widescreen-app-completion/base-manifest.json`

- [x] Calculate SHA-256 for `build/Naruto Ultimate Ninja Storm.apk`; record package/version, certificate and ARM64 library hash.
- [ ] If ADB is connected, query `pm path` and pull the installed base APK to a new read-only evidence folder; verify package/version and SHA-256. Do not install or change device state in this task. **Pending: no device is connected.**
- [x] Reconcile local evidence for the `5DAC…` accepted build and later candidate records. The primary APK is the documented user-accepted composition build; the alternate APK at its current path is candidate-02 and its sidecar is stale. The live installed state remains unknown.
- [x] Write `base-manifest.json` with input APK, installed APK status, signing certificate, native Build ID, Exynos patch identity, pt-BR payload hashes and comparison result. Live installed APK comparison is pending.

**Gate:** no later work may use `717A…`, the original APK, or the `F94B…` candidate as a silent fallback. The exact chosen base and reason must be in the manifest.

### Task 1: Build the screen/state and evidence ledger

**Files:**
- Modify: `docs/WIDESCREEN_ASSET_MAP.md`
- Create/update: `work/candidates/widescreen-app-completion/screen-state-ledger.json`
- References: `audit/frame_001.jpg`–`audit/frame_029.jpg`, `work/candidates/widescreen-followup-20261026-01/reference-manifest.json`

- [x] Create one record per flow in the map: 20 screen/state flows are registered, including boot/logo, menus, gameplay, battle, fades, video/events, credits, touch and pt-BR layout.
- [ ] Complete previous/next route and save-data reachability for each record; unknown or save-sensitive paths stay explicitly marked until a safe route is demonstrated.
- [ ] Capture a baseline only when the device is available. Use the canonical APK, S24 landscape, same screen state and stable animation phase; preserve existing `audit/` frames and record SHA-256 for new captures.
- [ ] Mark missing runtime captures explicitly; do not treat a static asset inventory as proof that a screen was exercised.

**Gate:** every user-visible screen/state is either listed with evidence or marked “unmapped”; none is silently omitted.

### Task 2: Map native draw routes, asset bindings, and coordinate spaces

**Files:**
- Update: `docs/WIDESCREEN_ASSET_MAP.md`
- Create: `work/candidates/widescreen-app-completion/render-route-ledger.json`
- Inputs: `work/candidates/widescreen-app-completion/canonical-base-cpk-inventory.json` (the older `work/assets/cpk-inventory.json` has stale offsets for this APK), `docs/WIDESCREEN_NATIVE_ASSET_BINDINGS_20261026.md`, `work/s24-title/findings.md`, `work/s24-controls/findings.md`, `work/s24-rpg-menu-analysis/manifest.json`, `work/s24-startmenu-analysis/manifest.json`, `work/widescreen/cover/analysis.md`

- [ ] For each screen record native entry/draw call path and ELF VA against the exact library Build ID from Task 0. **Partial: 11 shared routes are registered; most screen-specific asset/layout bindings remain unknown.**
- [ ] For each visible 2D element record XFBIN path/member, chunk kind/name, sprite/model ID, material, texture, UV rectangle, vertex bounds, transform, z/order and screen-space result.
- [ ] For 3D scenes record camera/projection path, source aspect, viewport, render target and HUD pass separately.
- [ ] For each control record displayed bounds, touch bounds, input path, pointer ID/gesture behavior, and forward/inverse transform.
- [ ] Tutorial panel route: **sprite and message binding completed statically** — `0x25b → cmn_tutorial.xfbin#xcmn_tutorial_win00`, helper `0x25e → #xcmn_tutorial_dmy`, header clump `0x36e → xcmn_mobile.xfbin#xcmn_hbase01_a01`; captured text is `dialog_014_01` (record 11565). `ccDispTutorial::Setup` scales panel X from logical width. Still resolve the active record's picture list, exact rendered bounds and hitbox; table path aliases do not yet match canonical CPK paths. Do not enlarge this atlas by assumption.
- [ ] Tutorial input path: **call chain mapped statically** — `ccDispTutorial::Ctrl → ccWindowHeader::Ctrl → ccCommonTouchButton::Ctrl → ccDispTouchButton::Ctrl/ccTouchButton`; `ccButtonSet` is a separate control. Measure each rendered/touch bound and verify S24 screen-to-render mapping on device.
- [ ] Mission-menu screenshots: resolve each visible sprite/material, final bounds and hitbox; the existing menu background layer expansion does not prove item alignment.
- [ ] Record unknowns with the exact evidence needed to resolve them; do not patch by visual resemblance.

**Gate:** a row becomes an editable target only after its runtime route and asset/layout binding are identified.

### Task 3: Lock display composition and Hor+ camera behavior

**Files:**
- Read: `docs/WIDESCREEN_COMPOSITION_FINDINGS.md`
- Read: `docs/WIDESCREEN_COMPOSITION_VALIDATION_20261026.md`
- Modify only after Task 0–2: `scripts/patch-widescreen.py`, `patches/widescreen/stubs.S` or a new hash-guarded incremental patch under `scripts/`
- Verify with: `scripts/test-widescreen-composition.py`, `scripts/test-s24-coverage.py`

- [ ] Preserve the current real-width/height arguments to `SetRenderMode` on both initial resolution setup and `ChangeRender` paths.
- [ ] Verify final render-target and compositor bounds are `[0,0,W,H]` on full-display scenes; reject an unintended fixed 16:9 destination or `X=210` at `2340×1080`.
- [ ] Trace the camera used by village exploration, free battle, combat and any 3D mode preview. Use horizontal-FOV expansion that keeps vertical FOV and character scale stable; do not enlarge a 2D screenshot to fake a live scene.
- [ ] Parameterize aspect ratio only after confirming each callsite uses the same logical center; test `1920×1080`, `2340×1080` and `2560×1080`, including fractional logical bounds and symmetric rounding.
- [ ] Add/retain regression checks that fail if either render setup path reverts to 16:9 on the S24.

**Gate:** host emulation and static bytes pass; device acceptance remains separate.

### Task 4: Define per-screen UI anchors and exact touch transforms

**Files:**
- Modify: `patches/widescreen/stubs.S` only if a mapped route proves it necessary
- Update: `work/s24-ui-touch/verify_transforms.py` or focused per-screen verification files
- Map: `docs/WIDESCREEN_ASSET_MAP.md`

- [ ] Define normalized anchors for left HUD, center prompts/dialogs, right map/action controls, bottom navigation, and safe display edges.
- [ ] Keep icons, text, map geometry, logos and control discs at their intended aspect; move/resize layout containers and hitboxes as separate elements.
- [ ] Apply the same affine/piecewise transform to the rendered control bounds and its inverse to received touch coordinates; write the transform into the route ledger per screen.
- [ ] Verify center and all four corners, button boundaries, map opening, drag/scroll, double tap, simultaneous pointers and cancel/back paths. Verify gamepad input independently from touch overlay input.
- [ ] Exercise long Portuguese strings, accents, selected/disabled states and line wrapping in dialogs and menus.

**Gate:** no screen passes on screenshot alignment alone; every visible actionable control must respond inside its drawn bounds.

### Task 5: Apply only screen-specific background/panel asset changes

**Files:**
- Source/reimport tools: `scripts/xfbin_textures.py`, `scripts/patch-controls-bg-s24.py`, `scripts/patch-title-layers-s24.py`
- Targets only when proven in Task 2: exact XFBIN chunks listed in the ledger
- Output: new candidate tree below `work/candidates/widescreen-app-completion/`

- [ ] Keep `xoption_battlebg01` as the sole confirmed texture expansion in the current asset shortlist; its panorama is `assets/widescreen-expansion-png/opcoes/moption/xoption_battlebg01-widescreen.png`.
- [ ] Retain the title's four geometry-only coverage changes only if the title route/candidate comparison supports them; keep logo, text, UV and animation data unchanged.
- [ ] For mission and battle panels, use 9-slice/center-band expansion only after proving center/edge UV regions and shared users. For the tutorial panel, first test why a sprite with logical-width X scaling still appears constrained; do not resize its atlas. Do not resize entire atlases.
- [ ] Keep the village map and icons proportional. Fix its viewport/anchor only if the route ledger proves an alignment defect.
- [ ] For each XFBIN reimport, assert source SHA-256, exact changed chunk names, pixel round-trip, dimensions, unchanged neighboring chunks and successful reparse.

**Gate:** the exact source asset must be in the ledger and any image output must include dimensions/hash plus the source member path.

### Task 6: Handle fades, modal dimming, opening video, and cutscenes

**Files:**
- Read: `docs/WIDESCREEN_FOLLOWUP_PLAN.md`
- Read: `work/widescreen/cover/analysis.md`
- Modify: a new isolated patch under `scripts/` only after route identity is proved

- [ ] Trace `ccDispFilter::Draw` for modal dimming and transition states; record viewport, alpha, depth, bounds and duration for each observed frame sequence.
- [ ] Distinguish intentional black/white transition frames from stale uncovered areas by comparing consecutive captures and state timing.
- [ ] Capture a real video frame, determine source dimensions and UV transform, then choose proportional crop, contain, or intentional bars per stream. Never stretch a 16:9 video without explicit visual approval.
- [ ] Keep logo aspect and opening clear/fade independent from the background/video quad.
- [ ] Validate subtitle and skip control positions and input while video is playing.

**Gate:** no generic global scale/cover patch may change unrelated sprites or HUD.

### Task 7: Build a single isolated full-app candidate

**Files:**
- Build scripts: `scripts/patch-cpk.py`, `scripts/repack-native-apk.py`, `scripts/build-ptbr-assets.py`, existing signing helpers
- Create: `build/Naruto Ultimate Ninja Storm - widescreen integral candidato.apk` and a build manifest

- [ ] Start from the exact Task 0 canonical APK and replace only mapped native/assets chunks from Tasks 3–6.
- [ ] Assert patch Exynos, pt-BR catalogs and translated graphics remain present; compare Manifest/DEX, unrelated CPK members, native bytes and payload hashes against the declared allowlist.
- [ ] Check package/version/code, certificate identity, APK v3 signature, 16 KiB alignment and installed payload hashes after signing.
- [ ] Keep the current primary APK untouched. Record source APK/native hashes, changed offsets/chunks, tools, output SHA-256 and validation status.

**Gate:** static, archive, signature and alignment checks all pass before device installation.

### Task 8: Device acceptance, complete screen walk, and promotion decision

**Files:**
- Create: `docs/WIDESCREEN_APP_ACCEPTANCE_<date>.md`
- Evidence: `work/candidates/widescreen-app-completion/captures/`

- [ ] Install only as an update (`adb install -r`) after the user requests installation; never uninstall or clear app data.
- [ ] Walk each mapped screen/state on the S24 at `2340×1080`: boot/title, mode, each options category, controls, village and map, tutorial/modal, mission/item/shop/minigame, battle selection/HUD/pause/result, video and credits where reachable.
- [ ] For every screen compare against the matching baseline: no side bars or uncovered rectangles, no center stretch, correct anchors, correct hitboxes, pt-BR text fits, transitions end cleanly, and no rendering regression.
- [ ] Capture gameplay at rest and moving; test camera recenter, controls, map, pause/resume/back and battle input. Record blocked/unreachable scenes rather than declaring them passed.
- [ ] Repeat at 16:9 on an available target or emulator; other ultrawide ratios remain “math-checked only” unless physically captured.
- [ ] Promote the candidate to the primary APK only after all required S24 gates pass and the user explicitly asks for promotion; otherwise retain it as a labeled candidate.

**Gate:** a build is “app completo widescreen” only when every matrix row has either a passing device capture/input record or an explicitly accepted intentional behavior (for example, proportional letterbox for a video).

## Dependency Order

`Task 0 → Tasks 1–2 → Task 3 → Task 4 → Tasks 5–6 → Task 7 → Task 8`.

Tasks 5 and 6 can be investigated independently after Task 2, but their edits must not be integrated until the render/input core and canonical base are fixed. No task after Task 2 may patch an unidentified route.

## Current Baseline of Evidence

- **Device-accepted:** S24 `2340×1080` composition correction removing the 210 px margin and aligning the observed touch path, per `docs/WIDESCREEN_COMPOSITION_VALIDATION_20261026.md`.
- **Static/candidate:** control panorama/XFBIN candidate, four title coverage meshes and filter/fade adjustments, per `docs/WIDESCREEN_FOLLOWUP_RESULT_20261026.md`.
- **Partial device observation:** gameplay reached the village and showed a widescreen frame; the later black capture is unresolved.
- **Still unverified:** all menu variants, every dialog, battle combat/pause/results, tutorial ID/content/bounds/touch for the captured prompt, video aspect, long pt-BR layout, screen-by-screen touch bounds and regression on all display ratios.
- **Baseline conflict:** the `5DAC…` validation and `F94B…` follow-up result describe different latest device states. Task 0 must resolve this before implementation.
