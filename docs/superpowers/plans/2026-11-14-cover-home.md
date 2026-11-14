# Cover Home Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 7-slide viewer with a full-viewport home page built from the cover's extracted elements, where each of the 4 cards opens its section (slides 2–5) in a blurred-backdrop popup.

**Architecture:** Cover elements are extracted once by a Python script into fixed-name WebP files under `src/assets/cover/`. `Home` lays them out with plain CSS sized by one viewport unit `--u` (so the 16:9 mockup percentages carry over and every aspect ratio fits without scrolling). `SectionDialog` is a native `<dialog>` hosting a Swiper of the 4 sections; `useSectionRoute` keeps the open section in the URL hash.

**Tech Stack:** Vite 8, React 19, TypeScript 7, Tailwind 4 (body/base only), Swiper 14, Python 3 + rembg (asset script only).

**Spec:** `docs/superpowers/specs/2026-11-14-cover-home-design.md`

## Global Constraints

- Sections, in order: `loi-ngo` "Lời ngỏ" (slide 2), `vung-ky-uc` "Vùng ký ức" (3), `cung-nhau-lon` "Cùng nhau lớn" (4), `loi-tri-an` "Lời tri ân" (5).
- Slides 6 and 7 are not on the site; originals 1, 6, 7 live in `design/canva-export/` (not bundled).
- Cover asset file names are fixed (users swap in Canva exports later): `title.webp`, `lighthouse.webp`, `ship.webp`, `bird.webp`, `logos.webp`, `sea-tile.webp`, `paper-tile.webp`, `card-<slug>.webp`.
- Backdrop: `rgb(0 0 0 / .55)` + `backdrop-filter: blur(6px)`.
- Subtitle is real text: "Ấn phẩm của L2T NEWS". Tab title: "Thắp sáng – L2T NEWS".
- Home is exactly `100svh`, never scrolls; portrait layout when `(max-aspect-ratio: 1/1)`.
- Hover/enter animations disabled under `prefers-reduced-motion: reduce`.
- No test framework is added. Verification = `pnpm lint`, `pnpm build`, and a Playwright script kept outside the repo at `$SCRATCH/pw/verify.mjs` driving system Chrome against `pnpm preview` on port 4173.
- Work on branch `feat/cover-home`; do not push without asking (push = deploy).

## Review Focus

- Short or very wide screens (1366×768, 2560×1080, phone landscape 844×390): title, cards and decorations must not overlap or overflow — pinned in Task 5's viewport sweep.
- Opening via a deep link (`/#loi-tri-an`) then pressing Back/close must stay on the site with the popup closed, not navigate away — pinned in Task 4.
- An unknown hash (`/#abc`) must show the home page with no popup and no error — pinned in Task 4.
- Swiper created while the dialog is hidden measures 0 width: the first open must show the slide at full size — pinned in Task 4 (image width > 0 right after first open).
- Tapping or double-tapping the image inside the popup must not close it; only the dark area, X, Esc or Back close it — pinned in Task 4.

---

### Task 1: Extract cover assets and reorganise slide files

**Files:**
- Create: `scripts/extract-cover.py`, `scripts/README.md`
- Create (generated): `src/assets/cover/*.webp` (13 files, names above)
- Move: `src/slides/{2,3,4,5}.webp` → `src/assets/sections/{loi-ngo,vung-ky-uc,cung-nhau-lon,loi-tri-an}.webp`
- Move: `src/slides/{1,6,7}.webp` → `design/canva-export/`
- Delete: `src/slides/.gitkeep`, `src/slides.ts`

**Interfaces:**
- Produces: the asset files above, consumed by Task 2.

- [ ] **Step 1: Branch** — `git switch -c feat/cover-home`.
- [ ] **Step 2: Move files** with `git mv` as listed.
- [ ] **Step 3: Write `scripts/extract-cover.py <cover.webp> <out_dir>`** — port of the brainstorm spike: boxes measured on a 795px-wide preview scaled by `width/795`; rembg session `isnet-general-use`; title alpha remapped `clip((a-150)*255/105)` and zeroed below 83% height right of 60% width; cards = stripe-detected rectangle (red: R>170,G<125,B<125; blue: B>120,R<130,B-R>40,G<150; column/row stripe ratio > 0.18) solid + rembg matte outside; sea tile = crop (418,985,545,1124) + its mirror; paper tile = crop (362,250,445,465) mirrored 2×2; logos = plain crop (545,1052,795,1124). Trim transparent margins. Save WebP (`quality=85`, `method=6`), long edge caps: title 2400, lighthouse 1600 (height), ship 1200, cards 900 (width), bird 400.
- [ ] **Step 4: Run it**
  Run: `U2NET_HOME=$SCRATCH/u2net $SCRATCH/venv/bin/python -I scripts/extract-cover.py design/canva-export/1.webp src/assets/cover`
  Expected: 13 files listed; total size < 2.5 MB.
- [ ] **Step 5: Eyeball** — composite every output on a checkerboard into one sheet in `$SCRATCH` and view it; no grey ghosts on the title, cards keep butterfly/lily/photo overhangs.
- [ ] **Step 6: `scripts/README.md`** — how to rerun (venv + rembg) and that replacing a file with a same-name Canva export needs no code change.
- [ ] **Step 7: Commit** — `git add -A scripts src/assets design src/slides src/slides.ts && git commit -m "Extract cover elements into assets; move section slides"` (build is broken until Task 2; fine on a branch).

### Task 2: Section data

**Files:**
- Create: `src/sections.ts`

**Interfaces:**
- Produces:
  - `type SectionSlug = 'loi-ngo' | 'vung-ky-uc' | 'cung-nhau-lon' | 'loi-tri-an'`
  - `type Section = { slug: SectionSlug; title: string; page: string; card: string }` (`page`/`card` are imported asset URLs)
  - `const sections: readonly Section[]` in Global Constraints order
  - `function sectionIndexFromHash(hash: string): number` — `'#loi-ngo'` → 0 … `'#loi-tri-an'` → 3; `''`, `'#'`, unknown → `-1`; decodes `%`-escapes.

- [ ] **Step 1: Implement** with static imports of the 8 WebP files.
- [ ] **Step 2: Verify** — `pnpm exec tsc -b` passes (App still imports the deleted `slides.ts` → temporarily point `App.tsx` at a stub rendering `null`, replaced in Task 4).
- [ ] **Step 3: Commit** — `git commit -am "Add section data and hash lookup"` (include new file).

### Task 3: Home page

**Files:**
- Create: `src/Home.tsx`, `src/home.css`
- Modify: `index.html` (title "Thắp sáng – L2T NEWS", preload `title.webp` not needed — keep simple)

**Interfaces:**
- Consumes: `sections` (Task 2).
- Produces: `function Home(props: { onOpen: (index: number) => void }): JSX.Element`; each card is `<button class="home__card" aria-label={title} data-slug={slug}>`.

- [ ] **Step 1: Write the layout in `home.css`.**
  `.home { position: relative; height: 100svh; overflow: hidden; --u: min(1vw, 1.7778vh); background: linear-gradient(to bottom, rgb(194 214 223 / .85), transparent 45%), url(paper-tile.webp) repeat; }`
  Portrait (`@media (max-aspect-ratio: 1/1)`): `--u: min(1vw, 0.4615vh)`.
  All sizes/offsets in `calc(var(--u) * N)` taken from mockup `home-layout-a-v6.html` (desktop: title 52, cards 11.5 wide with ~1.5 gap, lighthouse height ≈ 74% of 56.25u, ship 19, sea band 15% height). Center column = absolutely centered flex column (title img, subtitle, 2×2 grid). Decorations pinned to edges: lighthouse `left:0; bottom`, sea band full width `bottom:0` with `mask-image` fade-top, ship over sea, logos bottom-right on a white rounded badge, 3 birds (one mirrored) in empty sky — none touching the title.
  Card hover: `translateY(calc(var(--u)*-.3)) scale(1.02)` + stronger drop-shadow; `:focus-visible` outline 3px #1f3f8f; both off under reduced motion.
- [ ] **Step 2: `Home.tsx`** renders the markup; decorative images `alt=""`, title `alt="Thắp sáng – Số 2011"`; subtitle letters of "L2T NEWS" alternate navy `#1f3f8f` / red `#c0392b`.
- [ ] **Step 3: Verify** — temporarily render `<Home onOpen={() => {}} />` from `App`, `pnpm build && pnpm preview`, screenshot 1440×900 and 390×844 with the verify script; compare against the v6 mockup.
- [ ] **Step 4: Commit** — `git add src/Home.tsx src/home.css index.html src/App.tsx && git commit -m "Add cover home page"`.

### Task 4: Section popup + hash routing

**Files:**
- Create: `src/SectionDialog.tsx`, `src/section-dialog.css`, `src/useSectionRoute.ts`
- Modify: `src/App.tsx` (rewrite: `Home` + `SectionDialog` + `useSectionRoute`), `src/index.css` (drop old `.slides-viewer` rules)
- Delete: `src/useFullscreen.ts`

**Interfaces:**
- Consumes: `sections`, `sectionIndexFromHash` (Task 2); `Home` (Task 3).
- Produces:
  - `function useSectionRoute(): { openIndex: number | null; open(i: number): void; close(): void; change(i: number): void }`
    - `open` → `history.pushState(null, '', '#'+slug)`; `change` → `replaceState`; `close` → `history.back()` only if this tab pushed the entry, else `replaceState` to `location.pathname`; `popstate` + initial load read `sectionIndexFromHash`.
  - `function SectionDialog(props: { index: number | null; onClose(): void; onChange(i: number): void }): JSX.Element`
    - `<dialog aria-labelledby>`; `showModal()` when `index !== null`, `close()` otherwise; native `cancel` (Esc) → `onClose`; click whose target is the `<dialog>` itself or the slide padding (not the `img`) → `onClose`.
    - Swiper (A11y, Keyboard, Navigation, Zoom; `initialSlide = index`; `observer`, `observeParents`; call `swiper.update()` after `showModal`), `onSlideChange` → `onChange`. Header: section title + `x / 4` + X button (`aria-label="Đóng"`). Slide image `object-fit: contain`, max height ≈ `calc(100svh - header)`.
    - Enter animation: fade + scale .98→1 over 180ms; none under reduced motion.

- [ ] **Step 1: Write the checks in `$SCRATCH/pw/verify.mjs`** (they fail until Step 3):
  - clicking each `.home__card` opens `dialog[open]` whose heading equals that card's title and whose active image `src` contains the slug; image `getBoundingClientRect().width > 0` on first open
  - `location.hash === '#'+slug` after opening; Esc closes and hash becomes `''`; X closes; clicking at (5,5) of the viewport closes; double-clicking the image keeps the dialog open
  - ArrowRight inside the dialog moves to the next section and updates hash via replace (history length unchanged)
  - `goto('/#loi-tri-an')` opens "Lời tri ân"; then `goBack`-equivalent close (X) leaves `page.url()` on the site with no hash
  - `goto('/#abc')` → no `dialog[open]`, no console errors
  - browser Back after opening from the home closes the dialog
- [ ] **Step 2: Run** — `node $SCRATCH/pw/verify.mjs` → FAIL (no dialog yet).
- [ ] **Step 3: Implement** the three files and rewrite `App.tsx`.
- [ ] **Step 4: Run** — `pnpm lint && pnpm build`, restart preview, `node $SCRATCH/pw/verify.mjs` → all PASS, `errors: none`.
- [ ] **Step 5: Commit** — `git add -A src && git commit -m "Open sections in a blurred-backdrop popup with hash links"`.

### Task 5: Viewport sweep, polish, docs

**Files:**
- Modify: `src/home.css` (tuning only), `README.md`

- [ ] **Step 1: Extend the verify script** with a sweep over 1920×1080, 1440×900, 1366×768, 1280×800, 2560×1080, 1024×768, 820×1180, 844×390, 390×844, 375×667: assert `scrollHeight <= innerHeight` and `scrollWidth <= innerWidth`; assert no two of {title, 4 cards} bounding boxes intersect; assert every card box is fully inside the viewport; save a screenshot per size.
- [ ] **Step 2: Run** → fix any failure by tuning `--u` factors / offsets in `home.css`; view every screenshot.
- [ ] **Step 3: README** — replace the "Thêm slide" section with: where sections and cover assets live, how to swap in Canva exports (same file names), how to rerun `scripts/extract-cover.py`.
- [ ] **Step 4: Final run** — `pnpm lint && pnpm build && node $SCRATCH/pw/verify.mjs` all pass.
- [ ] **Step 5: Commit** — `git commit -am "Tune home layout across viewports; update README"`.
