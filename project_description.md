# Little Star Playhouse — Project Description & Codebase Documentation

## 1. Executive Summary

**Little Star Playhouse** is a modern, responsive, parent-first web application designed for a preschool and early-childhood learning center situated in Janakpurdham, Dhanusha, Nepal.

This codebase represents **Phase 1** of the Little Star Playhouse digital platform. It delivers a comprehensive, interactive frontend prototype consisting of:
- A warm, storybook-editorial public school website.
- Dynamic announcement notices feed with search, category filtering, and individual detail pages.
- A downloadable parent resource shelf and document library.
- Multilingual support for English (`en`) and Nepali (`ne`).
- An interactive administrative dashboard and content management system (CMS) prototype for publishing notices, managing parent documents, scheduling releases, and previewing file uploads in the browser.

The project strictly follows prototype integrity guidelines: all mock data is clearly isolated, user mutations update temporary browser state with transparent notices, and clean service seams are established for **Phase 2** backend, database, authentication, and cloud storage integration.

---

## 2. Institution Profile & Core Metadata

- **Institution Name:** Little Star Playhouse
- **Motto / Taglines:**
  - *"A safe place for little stars to shine."*
  - *"Big dreams begin with little steps!"*
  - *"Warm beginnings. Curious minds. Room to grow."*
  - *"Childhood is not a race. It is a world."*
- **Location:** Ward 4, Janakpurdham, Dhanusha, Nepal (Near the old Sanchaykosh Office, on the way to Kataiyachauri)
- **Primary Phone:** `9709142797` (`+977 9709142797`)
- **Primary Email:** `littlestarplayhouse2026@gmail.com`
- **WhatsApp Channel:** `https://wa.me/9779709142797`
- **Google Maps Location:** `https://maps.app.goo.gl/1PW44EVbxNpbGBfC8`
- **Target Age Groups:** Early childhood learners (Playgroup: Ages 2–3, Nursery Readiness: Ages 3–4, Creative Play: Ages 3–5)

---

## 3. Brand Identity & Design System

### 3.1 Design Direction: "Storybook Editorial Playfulness"
The visual identity is anchored in a clean, educational interface featuring expressive illustrated moments, warm soft cards, playful icon badges, and organic curves. Evaluated alternative aesthetics included Nordic classroom minimalism (score 0.07) and retro primary-school posters (score 0.06), with storybook editorial playfulness selected (score 0.87).

### 3.2 Color Tokens & Palette
Defined as CSS custom properties in `src/styles.css`:

| Token Name | Hex Code | Visual Role & Usage |
| :--- | :--- | :--- |
| `--blue` | `#1976D2` | Royal Blue: Primary brand color, sticky headers, footers, primary CTA buttons |
| `--yellow` | `#FFC107` | Warm Yellow: Star accents, highlights, primary badge markers, enquiry CTA |
| `--green` | `#8BC34A` | Leaf Green: Growth accents, playful cards |
| `--green-strong` | `#4CAF50` | Playhouse Green: Success states, admission banner, value highlights |
| `--sky` | `#2196F3` | Playhouse Sky Blue: Focus rings, active outlines |
| `--red` | `#F44336` | Playhouse Red: Urgent alert tags, PDF badges, deletion actions |
| `--orange` | `#FF9800` | Playhouse Orange: Movement & creative art accents, hover states |
| `--ink` | `#26364A` / `#23486F` | Deep Navy/Slate: Primary high-contrast text |
| `--muted` | `#657184` | Muted Slate: Secondary descriptions, metadata, subtitles |
| `--border` | `#E3EAF2` | Soft Blue-Grey: Subtle card and table borders |
| `--warm` | `#FFFCF5` | Warm White / Ivory: Main background canvas |
| `--pale-blue` | `#EAF5FF` | Soft Blue: Program cards, search inputs, active navigation |
| `--pale-yellow` | `#FFF7D6` | Soft Yellow: Notice tags, highlights, quote cards |
| `--pale-green` | `#EFF8E8` | Soft Green: Value highlights, admission section background |
| `--pale-coral` | `#FFF0EC` | Soft Coral: Activity cards, PDF icon backgrounds |

### 3.3 Typography Stack
Loaded via Google Fonts in `index.html`:
- **Display & Headings:** `Fredoka` (`wght@400;500;600;700`) — Friendly, rounded, characterful headings and display numbers.
- **Body & Navigation:** `Nunito` (`wght@400;500;600;700;800`) — Highly legible, approachable sans-serif for reading, inputs, and tables.
- **Nepali Localization:** `Noto Sans Devanagari` (`wght@400;600;700`) — Clean rendering for native Devanagari script.

### 3.4 Key Visual & UI Signature Components
- **Official Brand Logo:** Rendered in `src/App.tsx` (`Logo` component) using `/assets/little-star-playhouse-logo.png` with a smiling yellow star, royal-blue house, green foundation, and colorful toy blocks.
- **Custom Vector Iconography:** Comprehensive inline SVG icon system in `src/App.tsx` (`iconPaths`) including: `star`, `arrow`, `chevron`, `menu`, `close`, `search`, `filter`, `phone`, `mail`, `pin`, `play`, `heart`, `book`, `brush`, `blocks`, `music`, `sparkle`, `file`, `pdf`, `image`, `download`, `external`, `bell`, `dashboard`, `notice`, `upload`, `settings`, `logout`, `plus`, `edit`, `eye`, `trash`, `calendar`, `link`, `heading`, `bold`, `italic`, `underline`, `undo`, `redo`, `list`, `check`, and `info`.
- **Accessibility & Reduced Motion:** Full `@media (prefers-reduced-motion: reduce)` rules zero out transforms, card lift animations, and transitions.

---

## 4. Technical Architecture & Tech Stack

### 4.1 Technology Overview
- **Runtime & View Library:** React 19 (`react`, `react-dom`)
- **Language:** TypeScript 5 (`strict: true`, target `ES2020`, module `ESNext`, module resolution `Bundler`)
- **Build Tool:** Vite 6 (`@vitejs/plugin-react`)
- **Package Manager:** `pnpm@10.15.1`
- **Development Server:** Configured on host `0.0.0.0`, port `3000`
- **Styling Strategy:** Pure responsive CSS (`src/styles.css`) without heavyweight utility dependencies, ensuring optimal bundle size, instant load times, and fine-grained design token enforcement.
- **Routing Engine:** Zero-dependency, client-side routing implemented in `src/App.tsx` responding to `window.location.pathname`, browser `popstate` events, and history state pushing, mapped 1-to-1 against `public/manus-routes.json`.

---

## 5. Repository File Structure

```
littlestar/
├── index.html                  # HTML entry point, SEO tags, preloads, and font links
├── package.json                # Project dependencies, scripts, and package metadata
├── pnpm-lock.yaml              # PNPM deterministic dependency lockfile
├── pnpm-workspace.yaml         # Workspace configuration
├── tsconfig.json               # Main TypeScript compiler configuration
├── tsconfig.node.json          # Node-specific TS configuration for build tooling
├── vite.config.ts              # Vite configuration (port 3000, host 0.0.0.0, react plugin)
├── vite.config.js              # Compiled/fallback Vite configuration
├── app.config.ts               # Application branding config and CDN logo URL reference
├── plan.md                     # Phase 1 architectural design and requirements document
├── TODO.md                     # Feature checklist and verification tracker
├── public/
│   ├── manus-routes.json       # Route manifest mapping all public and admin paths
│   └── assets/
│       ├── little-star-playhouse-logo.png # Official brand emblem & wordmark
│       ├── hero-full.webp                 # Full classroom illustration for Hero section
│       ├── gallery-classroom.webp         # Classroom discovery photo
│       ├── playgroup.webp                 # Playgroup program card image
│       ├── nursery-readiness.webp         # Nursery Readiness program card image
│       ├── creative-play.webp             # Creative Play program card image
│       └── notice-classroom.webp          # Notice cover illustration
└── src/
    ├── main.tsx                # Application mounting point with React.StrictMode
    ├── App.tsx                 # Core application: routing, public pages, admin CMS, UI components
    ├── data.ts                 # Type definitions, mock notices, documents, programs, FAQ, i18n
    ├── styles.css              # Complete design tokens, components, responsive layouts, admin styles
    └── vite-env.d.ts           # Vite client TypeScript declarations
```

---

## 6. Route Manifest & Information Architecture

Synchronized across `public/manus-routes.json` and `src/App.tsx`:

| Path | Page Name / Component | Description |
| :--- | :--- | :--- |
| `/` | **Home (`HomePage`)** | Landing page featuring Hero, Trust highlights, About preview, Programs, Activities, Gallery, FAQ, and CTAs |
| `/about` | **About Us (`AboutPage`)** | Deep dive into early childhood philosophy, values, and the Little Star promise |
| `/programs` | **Programs (`ProgramsPage`)** | Detailed breakdown of Playgroup, Nursery Readiness, and Creative Play programs |
| `/our-little-world` | **Our Little World (`WorldPage`)**| Rich activity mosaic highlighting Storytime, Art, Building, Music, and Dancing |
| `/gallery` | **Gallery (`GalleryPage`)** | Interactive photo gallery with expandable lightbox preview |
| `/notices` | **Notices Feed (`NoticesPage`)** | Searchable, categorizable school announcements feed with pagination |
| `/notices/:id` | **Notice Details (`NoticeDetailPage`)** | Dynamic notice reader with rich content, attachments sidebar, and native sharing |
| `/documents` | **Parent Resources (`DocumentsPage`)**| Downloads repository with search, multi-format filter, and sorting |
| `/contact` | **Contact Us (`ContactPage`)** | Campus directions, interactive enquiry form, direct phone, email, and WhatsApp links |
| `/admin` | **Admin Overview (`AdminOverview`)** | Dashboard with metrics counters, recent notices, quick action links |
| `/admin/notices` | **Notices Manager (`AdminNotices`)** | Full CRUD prototype table with status filters, publishing toggles, delete dialog |
| `/admin/notices/new` | **Notice Composer (`NoticeComposer`)**| Rich-text WYSIWYG editor, attachment dropzones, publication settings sidebar |
| `/admin/documents` | **Documents Manager (`AdminDocuments`)**| Resource uploader, format validator, mock publishing queue |
| `/admin/uploads` | **Uploads Workspace (`AdminSimple`)**| File workspace stub ready for Phase 2 cloud storage integration |
| `/admin/settings` | **School Settings (`AdminSimple`)** | School parameters, contact defaults, and preferences placeholder |

---

## 7. Data Models & State Architecture (`src/data.ts`)

### 7.1 TypeScript Type Definitions
```typescript
export type Category = 'Important' | 'General' | 'Events' | 'Holidays' | 'Documents';
export type NoticeStatus = 'Published' | 'Draft' | 'Scheduled';
export type DocumentCategory = 
  | 'Forms' 
  | 'School Circulars' 
  | 'Parent Guidelines' 
  | 'Event Documents' 
  | 'Learning Resources' 
  | 'Other Documents';

export type Notice = {
  id: string;
  title: string;
  category: Category;
  date: string;
  author: string;
  excerpt: string;
  body: string[];
  important?: boolean;
  pinned?: boolean;
  status: NoticeStatus;
  cover?: string;
  attachments?: { name: string; type: 'pdf' | 'doc' | 'image'; size: string }[];
};

export type DocRecord = {
  id: string;
  title: string;
  description: string;
  category: DocumentCategory;
  type: 'PDF' | 'DOCX' | 'JPG';
  size: string;
  date: string;
  status: 'Published' | 'Draft';
};
```

### 7.2 Seed Data Inventory
- **Notices (`notices`)**:
  - `welcome-circle`: *Important School Announcement* (Important, Pinned, Published) — Notes on settling into morning routines, PDF attachment.
  - `colour-day`: *Upcoming School Activity* (Events, Published) — Creative play morning, painting & music, attachments include guide PDF and preview JPG.
  - `parent-question`: *Information for Parents* (General, Published) — Orientation FAQ and visiting guide, DOCX attachment.
  - `learning-resources`: *New Learning Resources Available* (Documents, Draft) — Parent resource shelf prototype notification.
- **Documents (`documents`)**:
  - `admission-enquiry`: *Admission Enquiry Form* (Forms, PDF, 420 KB, Published).
  - `welcome-guide`: *Parent Welcome Guide* (Parent Guidelines, PDF, 1.1 MB, Published).
  - `creative-play`: *Creative Play Activity Sheet* (Learning Resources, JPG, 760 KB, Published).
  - `holiday-note`: *Holiday Information Circular* (School Circulars, DOCX, 85 KB, Draft).
  - `music-morning`: *Music Morning Activity Note* (Event Documents, PDF, 690 KB, Published).
- **Curriculum Programs (`programs`)**:
  - `Playgroup` (Ages 2–3) — Gentle introduction to shared play, songs, routines.
  - `Nursery Readiness` (Ages 3–4) — Building vocabulary, language, curiosity, independence.
  - `Creative Play` (Ages 3–5) — Open-ended making, movement, music, and discovery.
- **Activity Themes (`activities`)**:
  - `Storytime` (Coral, wide card), `Creative art` (Yellow), `Building & discovery` (Blue), `Music & singing` (Green), `Dancing & movement` (Orange, wide card).
- **Frequently Asked Questions (`faq`)**:
  - 5 parent-focused questions covering age groups, programs offered, admission procedure, campus location in Janakpurdham, and fee confirmation guidelines.

---

## 8. Internationalization (i18n)

The application provides instantaneous bilingual language toggling without page reloading:
- **English (`en`)**: Complete terminology for navigation, call-to-action buttons, search hints, and status tags.
- **Nepali (`ne`)**: Fully localized dictionary featuring natural Nepali phrasing (e.g., `रमाइलोमा जोडिनुहोस्!` for "Let's Join the Fun!", `भर्नाबारे सोध्नुहोस्` for "Enquire About Admission", `हाम्रो सानो संसार` for "Our Little World").
- Authored school notices retain their authentic authored language while surrounding user interface elements update dynamically.

---

## 9. Comprehensive Feature Breakdown

### 9.1 Public Shell & Global Components
- **Top Announcement Ribbon:** Highlights the Janakpurdham campus location with a quick link to the contact/visiting page.
- **Sticky Navigation Header:** Displays the Little Star Playhouse official logo, main navigation routes, bilingual language switch (`EN / ने`), and a pill-shaped "Enquire" action button. Integrates an accessible mobile hamburger drawer on smaller screens.
- **Footer:** Deep royal-blue section displaying the logo on a soft badge, description, navigation columns, parent resource links, physical address with landmarks, phone, email, and social chat shortcuts (WhatsApp, Email, Call).

### 9.2 Public Pages
1. **Home Page (`/`)**:
   - Dynamic Hero section with organic blob photo frame, stickers (`play, learn, shine`), and immediate admission inquiry actions.
   - Trust highlights bar (Early childhood learning, Learning through play, Creative exploration, Welcoming environment).
   - "Little steps. Big discoveries." editorial split section with classroom imagery.
   - Programs preview grid with branded color themes and age tiers.
   - Activity mosaic presenting hands-on curriculum pillars.
   - Classroom gallery with full-size interactive lightbox modal.
   - High-contrast green Admission CTA banner with direct WhatsApp enquiry.
   - Collapsible accordion FAQ.
   - Campus contact banner.
2. **About Us (`/about`)**:
   - Highlights the core educational philosophy: "Childhood is not a race. It is a world."
   - 3-pillar breakdown: *Warm relationships*, *Playful learning*, and *Growing confidence*.
   - Star-branded Little Star institutional promise.
3. **Programs (`/programs`)**:
   - Expanded program cards with full checklists of developmental benefits.
   - Direct link to initiate admissions consultation.
4. **Our Little World (`/our-little-world`)**:
   - Detailed activity tiles highlighting stories, construction blocks, art, singing, and bodily movement.
5. **Gallery (`/gallery`)**:
   - Interactive classroom moments showcase with click-to-zoom modal dialog.
6. **Notices (`/notices` & `/notices/:id`)**:
   - Notice feed with live search filter across title, excerpt, and categories.
   - Filter chips for *All*, *Important*, *General*, *Events*, *Holidays*, and *Documents*.
   - Notice Cards display author, date, cover photo, category tag, pin marker, excerpt, and attachment previews.
   - Notice detail page includes back navigation, formatted paragraphs, callout tips, attachments sidebar, and native Web Share API / clipboard copy integration.
7. **Parent Resources / Uploads (`/documents`)**:
   - Filterable document cards with file type indicators (PDF, DOCX, JPG), file sizes, and publication dates.
   - Multi-parameter filtering: text search, category select, file type dropdown, and sorting (Newest, Oldest, File Type).
   - Mock download and view actions trigger friendly, accessible toast notifications.
8. **Contact Us (`/contact`)**:
   - School location details, Google Maps shortcut, direct click-to-call, and click-to-email.
   - Interactive parent inquiry form with input validation and local submission feedback.

### 9.3 Administrative System & Content Management System (CMS)
Accessible under `/admin`, the prototype admin suite includes:
1. **Admin Layout & Navigation:**
   - Fixed desktop sidebar and mobile overlay drawer.
   - Breadcrumb navigation, prototype mode badge, notifications icon, and team profile avatar.
2. **Dashboard Overview (`/admin`)**:
   - Metric overview cards tracking *Published notices (12)*, *Draft notices (4)*, *Scheduled notices (3)*, and *Published documents (18)*.
   - Quick action panel: Create notice, Upload document, Review settings, View public site.
   - Recent notices feed with fast status inspection.
3. **Notices Management (`/admin/notices`)**:
   - Tabular list showing Title, Category, Status badge (Published, Draft, Scheduled), Creation date.
   - In-table actions:
     - View / Preview notice.
     - Edit notice (triggers toast guidance).
     - Publish / Unpublish instant toggle updating component state.
     - Delete notice with confirmation dialog (`window.confirm`).
4. **Notice Composer (`/admin/notices/new`)**:
   - Two-column responsive authoring workspace.
   - Left Column: Title input, category selector, external URL field, rich-text `contentEditable` editor equipped with formatting toolbar (Bold, Italic, Underline, H3, Lists, Hyperlink modal, Undo/Redo, Remove format).
   - Drag-and-drop attachment dropzones supporting image preview generation via browser `URL.createObjectURL` and document upload simulation with progress indicators and file removal.
   - Right Column: Publication settings sidebar for status (Draft, Published, Scheduled), scheduling date-time picker, expiry date picker, cover photo picker, and "Pin as important" toggle.
   - Prototype state save, preview, publish, and schedule actions with validation alerts.
5. **Documents Management (`/admin/documents`)**:
   - Document upload form with drag-and-drop zone supporting `.pdf, .doc, .docx, image/*` up to 10 MB.
   - File listing table with status change triggers, preview actions, and delete handlers.
6. **Uploads Workspace & Settings Stubs (`/admin/uploads`, `/admin/settings`)**:
   - Prepared blank-slate frontend views for seamless Phase 2 integration.

---

## 10. Phase 2 Backend Integration Roadmap

The Phase 1 architecture isolates data concerns to enable seamless backend enablement:

1. **Service Abstraction Layer:**
   - Replace direct imports from `src/data.ts` with API clients (e.g. `src/lib/api/notices.ts`, `src/lib/api/documents.ts`).
2. **Database & Persistence:**
   - Connect notices and documents to a relational database (e.g., PostgreSQL with Prisma/Drizzle) or document store.
3. **Authentication & Access Control:**
   - Protect `/admin/*` routes with session-based or token-based authentication (OAuth2 / Supabase Auth / Clerk / NextAuth).
4. **Cloud Asset Storage:**
   - Wire the `UploadDropzone` component to real presigned upload URLs (AWS S3, Cloudflare R2, or Supabase Storage) instead of local object URLs.
5. **Contact Inquiries:**
   - Connect the `/contact` form submission handler to a transactional email service (Resend, SendGrid) or school notification inbox.

---

## 11. How to Run & Build

### Development Server
```bash
pnpm run dev
# or
npm run dev
```
Starts the Vite development server on `http://localhost:3000` (listening on `0.0.0.0`).

### Production Build & Type Checking
```bash
pnpm run build
# or
npm run build
```
Executes `tsc -b` for project-wide TypeScript type checking followed by `vite build` to output the optimized static bundle into `dist/`.

### Previewing the Production Build
```bash
pnpm run preview
# or
npm run preview
```
Serves the generated production distribution on `http://0.0.0.0:3000`.

