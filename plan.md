# Little Star Playhouse — Phase 1 Frontend Plan

## Scope and approach

Build a frontend-only, responsive React/TypeScript website for Little Star Playhouse with public school pages, mock notices and documents, and a complete admin prototype. No backend APIs, authentication, database, durable storage, publishing, or notifications are implemented. Mock content remains in a dedicated data layer and all mutation feedback explicitly says the result is temporary and browser-local.

Because the uploaded brief contains no logo/image file, the first pass will use an illustrated, replacement-ready brand lockup derived from the exact supplied logo description: smiling yellow star, royal-blue house, green base, colorful blocks, and the Little Star Playhouse wordmark/tagline. The public visual asset slot will be isolated so the official logo can replace it without changing layout code.

## Design direction

The chosen movement is **storybook editorial playfulness**: a clean educational interface with a small number of expressive illustrated moments.

Three candidate styles considered (low-probability alternatives):
- **Nordic classroom minimalism** — 0.07: quiet, paper-led layouts with restrained color blocks.
- **Retro primary-school poster** — 0.06: bold print-like shapes and high-contrast classroom graphics.
- **Storybook editorial playfulness** — 0.87: airy parent-first layouts punctuated by friendly stars, clouds, blocks, and warm illustrated scenes.

### Core principles

1. Parent clarity first: important information is scannable, actions are obvious, and public content stays calm despite the playful identity.
2. Logo-led joy: yellow star, blue house, green ground, and block forms recur as a coherent visual language.
3. Editorial variety: hero, activity mosaic, gallery, notices, and documents each have a distinct composition rather than repeated generic cards.
4. Honest prototype behavior: temporary mock states, local file previews, and development-only content are visible in the UI.

### Color philosophy

Royal blue is the dependable anchor for navigation, primary actions, and footer surfaces. Warm yellow marks moments of delight and attention. Leaf/playhouse greens signal growth and learning. Red and orange are reserved for controlled status and activity accents. Pale blue, yellow, green, coral, and warm white provide breathable section fields against main text #26364A and secondary text #657184.

### Layout paradigm

Use a responsive “little world” composition: an anchored two-column hero, offset editorial sections, a varied activity mosaic, and feed/list interfaces that remain straightforward for parents. Avoid a rigid centered-card grid; let illustration clusters and colored section bands create rhythm while content aligns to a readable max width.

### Signature elements

- A small smiling star with a four-point twinkle used as an identity cue and empty-state marker.
- Soft cloud and block shapes used as section anchors, not decoration everywhere.
- Rounded image frames with colored tabs/labels that echo the playhouse palette.

### Interaction and motion

Interactions feel gentle and tactile: hover lift is small, filters update immediately, accordions open with clear focus, and toasts confirm mock state changes. Clouds and stars use slow low-amplitude motion only; all animation is disabled or minimized under `prefers-reduced-motion`.

### Typography

Fredoka is used for display headings and playful labels. Nunito is used for body copy, controls, navigation, and admin UI. Noto Sans Devanagari is included for Nepali translations. Headline hierarchy uses rounded weight and short line lengths; controls remain compact and high contrast.

### Brand essence and voice

**Positioning:** A caring Janakpurdham play school where little learners build confidence through joyful exploration. Personality: warm, curious, dependable.

Voice lines: “Big dreams begin with little steps!” and “Let’s make room for one more happy discovery.” CTAs are direct, warm, and parent-friendly rather than salesy.

### Wordmark and signature color

The replacement-ready lockup combines a smiling yellow star above a small royal-blue house on a green base, with colorful block accents and a two-line Little Star Playhouse wordmark. The ownable signature color is warm yellow `#FFC107`, always paired with royal blue rather than used as a full-page background.

## Information architecture

- `/` — Home
- `/about` — About Us
- `/programs` — Programs
- `/our-little-world` — Our Little World
- `/notices` — Notices feed
- `/notices/:id` — Notice details
- `/documents` — Parent Resources & Downloads
- `/contact` — Contact
- `/admin` — Admin overview
- `/admin/notices` — Notices management
- `/admin/notices/new` — Notice composer
- `/admin/documents` — Documents management/upload UI
- `/admin/uploads` — Uploads workspace
- `/admin/settings` — Settings preview

## Project structure

- `src/App.tsx` — client-side route selection, shared language/toast/modal state, public/admin shells.
- `src/components/` — reusable header/footer, public sections, notices/documents, admin controls, dialogs, file UI.
- `src/data/mockData.ts` — typed mock notices, documents, programs, activities, gallery, FAQ, and admin metrics.
- `src/i18n/translations.ts` — English/Nepali interface dictionary and language helpers.
- `src/lib/` — route helpers, file preview/format utilities, mock service boundaries.
- `src/styles/` — design tokens, layout, responsive styles, component styles, reduced-motion rules.
- `public/` — route manifest and replacement-ready local assets.

## Build workflow

1. Create the Vite/React/TypeScript project files and install only the minimal runtime dependencies.
2. Add design tokens, font loading, route manifest, typed mock data, and translation dictionary.
3. Build public shell and homepage first, then notices/documents and dynamic detail routes.
4. Build admin shell, management views, notice composer, and document upload UI with local previews and prototype state.
5. Add responsive/accessibility refinements, validation, toasts, dialogs, reduced-motion behavior, and honest mock messaging.
6. Run diagnostics and production build, start the configured Preview server on port 3000, verify route manifest and key routes, then checkpoint the intended commit.

## Backend seam for Phase 2

Keep future service boundaries in `src/lib/mockServices.ts` and keep data types independent from view components. Phase 2 can replace mock reads/mutations with API/database/storage implementations without changing page composition or interaction contracts.


## Visual refinement update

The supplied 1024×338 Little Star Playhouse logo is now used as the single brand asset in the public header, footer, and admin shell. The prior CSS-drawn placeholder mark has been removed. Typography has been softened by lowering display and body emphasis, keeping Fredoka for expressive headings but using medium/regular weights for headings, paragraphs, navigation, controls, cards, and labels. Buttons and accents remain within the logo palette: royal blue for primary actions, warm yellow, leaf/playhouse green, orange, and red for controlled emphasis.
