# Little Star Playhouse — Phase 1 Outcomes

- [x] **Public Little Star brand shell**
  - Use the official described identity and exact brand palette: warm yellow #FFC107, royal blue #1976D2, leaf green #8BC34A, playhouse green #4CAF50, playhouse blue #2196F3, playhouse red #F44336, playhouse orange #FF9800, tagline grey #555555, supporting pale blue #EAF5FF, light yellow #FFF7D6, pale green #EFF8E8, pale coral #FFF0EC, warm white #FFFCF5, main text #26364A, secondary text #657184, borders #E3EAF2.
  - Use Fredoka, Nunito, and Noto Sans Devanagari with coherent spacing, borders, shadows, icons, and radii.
  - Provide responsive header with official/replacement-ready logo, required public links, English/Nepali toggle, mobile menu, and “Let’s Join the Fun!” admission CTA.
  - Provide royal-blue footer with logo, quick links, contact details, yellow/green details, and copyright.

- [x] **Public pages and homepage experience**
  - Implement Home, About Us, Programs, Our Little World, Notices, Notice Details, Documents, and Contact routes.
  - Homepage includes hero headline “Big dreams begin with little steps!”, exact supporting copy, admission/discovery CTAs, logo-inspired storybook illustration, trust highlights, “Little steps. Big discoveries.” about section, Playgroup/Nursery Readiness/Creative Play cards, varied activity themes, responsive gallery/lightbox, admission CTA, accessible FAQ, and contact actions.
  - Contact information is Little Star Playhouse, Ward 4, Janakpurdham, Dhanusha, Nepal, near the old Sanchaykosh Office on the way to Kataiyachauri, phone 9709142797, email littlestarplayhouse2026@gmail.com, with WhatsApp/call/email/directions buttons.
  - Avoid unsupported awards, ratings, statistics, fake testimonials, fabricated school policies, or invented facts.

- [x] **Notices feed and detail**
  - `/notices` provides the requested header, development-only mock notice records, identity/author/date/title/category/important badge/text preview/optional cover and attachments, full-notice and attachment actions, search, all requested category filters, pagination or load more, and loading/empty/no-results states.
  - Mock records include the requested example themes and are clearly marked as mock/development data.
  - Notice detail provides title, category, date, formatted body, links, images, attachment list, download buttons, back link, and functional frontend share behavior.

- [x] **Documents library**
  - `/documents` provides the requested title/supporting copy, all document category filters, reusable cards with file-type icon/title/description/category/format/size/upload date/view/download, search, category/file-type filters, newest sorting, and a friendly empty state.
  - Mock records are separate from the future backend integration layer.

- [x] **Admin dashboard and management screens**
  - `/admin` provides responsive sidebar/top bar/main area, active states, mobile drawer, required sidebar destinations, clearly labeled preview metrics, recent notices/uploads, quick actions, and create/upload actions.
  - Notices management provides responsive table/list with title/category/status/created/published/pinned/actions, mock Edit/Preview/Publish/Unpublish/Delete actions, search, filters, pagination, empty states, confirmation dialogs, and non-persistent messaging.
  - Documents management provides title/category/file type/size/upload date/status/actions Preview/Edit details/Replace file/Publish or unpublish/Download/Delete using the public design system.

- [x] **Notice composer**
  - `/admin/notices/new` provides responsive two-column editor/settings layout with title, category, rich-text editing, image/document attachments, optional link, settings for important pin/status/schedule/expiry/cover, and Save Draft/Preview/Publish/Schedule actions.
  - Rich-text toolbar includes bold, italic, underline, headings, paragraph, bullet list, numbered list, insert hyperlink with dialog, undo, redo, and clear formatting.
  - Image/document dropzones provide picker, local preview, filename, size, recognizable icon, remove action, progress appearance, and honest local-only wording.
  - Actions use prototype state only and provide meaningful validation, confirmation, success, and error feedback.

- [x] **Document upload UI**
  - `/admin/documents` provides title, description, category, file selection, thumbnail, publication status/date, expiry date, large dropzone, local image/PDF previews where feasible, file metadata, progress UI, remove/replace, validation errors, clear instructions, and Select File/Save Draft/Publish Document/Cancel actions.
  - The UI never claims permanent upload or backend persistence.

- [x] **Localization, reusable architecture, and accessibility**
  - English/Nepali switching updates navigation, homepage, programs, buttons, notices, documents, admin navigation, form labels, empty/error states, FAQ, and contact UI while preserving authored mock notice language where appropriate.
  - Separate UI components, routes, mock content, translations, styles/tokens, form state, file preview logic, and future service interfaces; use TypeScript types and no unnecessary dependencies.
  - Implement semantic HTML, keyboard navigation, visible focus states, accessible labels, contrast, reduced-motion support, responsive/lazy image behavior, no horizontal overflow, touch-friendly mobile controls, and useful loading/error/empty states.

- [x] **Runtime and delivery readiness**
  - Serve a synchronized `/manus-routes.json` with every page route and dynamic notice route pattern.
  - Configure diagnostics before the first application code batch, run the production build, start the app on the configured port, verify key routes and route manifest, and checkpoint the intended source changes.
  - Keep server/database/auth/storage/publishing capabilities disabled for this phase and preserve a clean seam for Phase 2 backend integration.
