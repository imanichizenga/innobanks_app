# Prompt: Redesign and extend britishschool.ac.tz (public site + admin panel)

Copy everything below the line into the coding agent that runs on the VPS.

---

You are a senior full-stack engineer and product designer. You are working **directly on the production VPS** that serves `https://britishschool.ac.tz`. Your job is to turn the existing school website into a beautiful, well-structured site that is easy to understand, and then to build a content-management admin panel at `adminsite.britishschool.ac.tz`.

Use your best judgement on UI, UX and information architecture throughout. You may change anything that makes the site better, but you **extend and modify**. You do not rebuild from scratch and you never destroy data.

## 0. Non-negotiable safety rules (read first, obey throughout)

1. **The database is shared with the live school management system.** The `website` Django app sits in the same project (`rps_project`) and database as `rps_app`, `finance`, `payroll` and `attendance`. Breaking a migration breaks the whole school's operations.
2. **Before any change:** take a full database dump (`pg_dump`/`mysqldump`, whichever engine `settings.DATABASES` uses) and a tarball of `MEDIA_ROOT`, both with timestamps. Then `git commit` or stash the current working state of the repo. Write the restore commands into `website/DEPLOY_NOTES.md`.
3. **Never** run `DELETE`, `TRUNCATE`, `DROP`, `flush`, `migrate <app> zero`, `--fake` on existing migrations, or `reset_db`, and never delete files in `MEDIA_ROOT`.
4. **Migrations must be additive only:** new nullable fields, or fields with defaults, plus new models. No renames, no removals, no type changes on existing columns. Run `makemigrations website --dry-run -v 3` and `sqlmigrate` first, and show the SQL before applying. Only touch the `website` app's migrations. (Check `migration_hold/` and the actual migration state on the server with `showmigrations website` before generating anything.)
5. **Seed data is insert-only and idempotent:** a management command such as `python manage.py seed_website_defaults` using `get_or_create` keyed on `slug` or a natural key. It must **never overwrite** a field that already has a value. It must support `--dry-run`.
6. **Existing placeholder or test records are not deleted.** List them in a report and ask the owner. If the owner approves, hide them with `is_active=False`. Records I know about from the live API:
   - `home-statistics`: "This is Home Statistics", "hello again staticsss", "another home statistics" (values like "trial to check static")
   - `home-gallery`: "Home Gallerys", "akila gasss"
   - `home-features`: "title slide", "official title"
   - `student-life-menu-items`: "learning", "playing"; `student-life-gallery`: "second gallery", "gallerie time"
   - `academic-gallery`: "Academic Gallery Title", "Another academic title"
   - `news-event-categories`: "staff events" (lower-case duplicate style)
   `HomeStatistic` has no `is_active` field, so add one (default `True`) so it can be hidden without deleting it.
7. Build and verify the new frontend **next to** the running one (a separate build directory, port or PM2 process). Switch traffic only after the tests in section 9 pass, and keep the previous build so you can roll back with one command.
8. Never commit secrets. Do not print `.env` values in logs.

## 1. What exists today (verified by inspection)

**Backend.** The Django app is `website/` with 52 models, DRF viewsets in `website/views.py`, and a router in `website/api_urls.py`, mounted at `/api/` (47 endpoints). Content is grouped as:
- **Home:** pages, sliders, features, statistics, gallery, videos, notices, testimonials, enquiries.
- **Courses:** categories, courses (A-Level combinations PCM, EGM, CBG, HKL, PCB, HGE, PGM), with details, requirements, outcomes, gallery and FAQs. `Course` has `department`, `level`, `duration` and `meta_*` fields.
- **Academics:** page, menu items (CSEE, ACSEE, FTNA, English Course, Computer Course, Nursery Teacher Education, …), sections, gallery, FAQs.
- **Admission:** page, categories (FTNA, CSEE, ACSEE, Childhood Education, English Course, Computer Course), sections, requirements, FAQs, gallery.
- **Contact:** page, info cards, offices (Main Campus, Campus B, Campus C), social links.
- **News and events:** page, categories, news items (`publish_date`, `author_name`), event items (`event_date`, `start_time`, `end_time`, `venue`, `organizer`, `registration_link`), event FAQs, gallery (15 images).
- **About:** page (`mission`, `vision`, `core_values`, `hero_image`), menu items, sections, FAQs, leadership members (`full_name`, `role`, `bio`, `image`, `email`, `phone`). **All of About is empty in production.** `about-pages`, `about-menu-items`, `about-sections` and `leadership-members` all return `[]`.
- **Student life:** page, menu items, sections (with `button_text`/`button_link`), gallery, FAQs.

**Critical security bug.** `BaseModelViewSet` is a `ModelViewSet` with `permission_classes = [AllowAny]`. **Anyone on the internet can POST, PUT, PATCH or DELETE every piece of website content.** Fix this first:
- Give anonymous users read-only access.
- Allow writes only to authenticated staff, using a permission class that reuses the existing `user_can_manage_home_enquiries` pattern or adds a `can_manage_website` flag the same way.
- Keep anonymous `create` working for `home-enquiry-submissions` and `home-testimonials`. Testimonials must stay `is_approved=False` on create.
- Confirm that the current Next.js proxy routes (`src/app/api/home-enquiry-submissions`, `src/app/api/home-testimonials`) still work afterwards.
- Also make public list endpoints return only `is_active=True` records. Staff should see everything.

**Frontend.** `website/next-app` uses Next.js 15, React 19, Tailwind 3 and TypeScript, with `output: "standalone"`. Data comes from `src/lib/api.ts` (`fetchAPI`, `getMediaUrl`, which rewrites the legacy `british.schoolsoft.online` media host). Navigation is hard-coded in `src/lib/navigation.ts`.
- It was built from a **real-estate template** (the package is named `property_project`), and leftovers ship with it: `properties/`, `documentation/`, `(auth)/signin|signup|forgot-password`, `components/home/calculator`, `property-list`, `property-details`, `context-api/PropertyContext.tsx`, `public/data/propertydata.json`, `markdown/blogs`, template images, and a GitHub Pages workflow that expects `./out` and so is broken for a standalone build.
  - Remove these from routing and the sitemap, or redirect them, unless something real depends on them.
  - Delete template code only after a grep proves nothing imports it.
- **Typography is the biggest visual problem.**
  - There is no custom typeface; it uses only the default `font-sans`.
  - The live homepage HTML uses `text-sm` 123 times and `text-xs` 72 times, against only 20 uses of `text-base`. Body copy is too small to read comfortably.
- The colours are the template's generic blue (`#2F73F2`), not a school identity.
- **Branding is inconsistent.** `SITE_NAME` is "British Opening Schools", while the content says "British School" and "BRITISH SCHOOLS". Confirm the official name with the owner, and put it in one config value.
- **Contact data contradicts itself:**
  - `layout.tsx` hard-codes `255655400420` for the mobile action bar.
  - All three offices list `0655700420`.
  - The hero buttons link to `wa.me/255770036452`.
  - The WhatsApp social link is `wa.me/255655700420`.
  - All three campuses share the same address ("Mwenge ITV"), the same map embed, and "24 hrs" office hours.

  Report these to the owner. Read every phone number from the API and none from hard-coded values.
- The location is Kijitonyama / Mwenge ITV, Dar es Salaam, Tanzania. The curriculum is the Tanzanian NECTA system: Form II FTNA, Form IV CSEE, Form VI ACSEE, plus early-childhood, English, computer and nursery-teacher courses.

Start by re-verifying all of this yourself (read the code and `curl` every endpoint under `https://britishschool.ac.tz/api/`), and save a short audit to `website/AUDIT.md`.

## 2. Design system: make it beautiful, readable and consistent

Create one design system and use it everywhere, on the public site and the admin panel alike.

**Typography** (load with `next/font/google`, self-hosted, `display: swap`):
- Headings: a distinguished serif with character that fits a British-style school, such as **Fraunces**, **Playfair Display** or **Cormorant Garamond** (semi-bold or bold).
- Body and UI text: a highly legible humanist sans such as **Plus Jakarta Sans**, **Inter** or **DM Sans**.
- Pick one pairing and set it as Tailwind `fontFamily.heading` and `fontFamily.sans`.
- Type scale, fluid with `clamp()`:
  - body 17–18px minimum, line-height 1.65–1.75, max line length about 68ch
  - lead paragraph 20–22px
  - H1 40–64px, H2 32–44px, H3 24–28px
  - small or meta text never below 14px
- Add letter-spacing to uppercase eyebrow labels (0.08–0.12em).
- Replace `text-xs` and `text-sm` on body content across the codebase. Keep them only for genuinely tiny UI metadata.

**Colour.** Use a confident academic palette: deep navy or royal blue as the primary, a warm gold or crimson accent, and warm off-white surfaces. If the school logo has brand colours, derive the palette from those instead. Define the palette as CSS variables with Tailwind tokens, meet WCAG AA contrast, and support dark mode only if you can keep it polished; otherwise remove the theme toggle.

**Layout.**
- Use an 8px spacing grid, a 1200–1280px container, and generous section padding (80–120px on desktop, 56–72px on mobile).
- Use a consistent card style with a shared radius, shadow and hover lift.
- Show images with `next/image` at sensible aspect ratios, with a gradient overlay wherever text sits on top.

**Motion.** Keep it subtle: fade or slide in on scroll (AOS is already installed, or use CSS), and respect `prefers-reduced-motion`.

**Components** to build once and reuse:
- page hero with breadcrumb
- section heading (eyebrow, title, lead)
- stat counter
- feature card
- person card
- event card (with a date badge)
- news card
- gallery grid with lightbox
- FAQ accordion
- call-to-action band
- contact card
- empty-state fallback

Extend the existing `components/school/*` rather than duplicating it.

## 3. Information architecture and navigation

Restructure the navigation so a parent, student or visitor can find anything in two clicks. Move the navigation config into `src/lib/navigation.ts` (or have it driven from the API) and use it for the header, mobile menu, footer and sitemap.

Suggested structure (adjust with judgement, keeping existing URLs working through redirects):

| Top level | Children |
|---|---|
| **About** | School Profile · Foundation & History · Mission, Vision & Values · Leadership · Campuses · Awards & Achievements · Careers |
| **Academics** | Overview · Programmes (FTNA / CSEE / ACSEE) · A-Level Combinations (existing courses) · Departments · Results & Performance · Nursery Teacher Education · English & Computer Courses |
| **Admissions** | How to Apply · Requirements by level (existing admission categories) · Scholarships · Enquire / Apply |
| **Student Life** | Student Profile · Clubs, Sports & Activities · Learning Environment · Life After School (university pathways, alumni) |
| **News & Events** | Latest News · Events (grouped by month) · School Calendar |
| **Gallery** | (standalone, top-level) |
| **Contact** | Contact Directory · Campuses & Map · Send an Enquiry |

The header and mobile menu must work like this:
- **Desktop:** a sticky header that shrinks on scroll, a mega-menu or clean dropdowns with a one-line description per link, an "Apply Now" primary button, and the phone number visible.
- **Mobile:** a full-screen drawer with accordion sub-menus, large tap targets (at least 48px), current-page highlighting, and the call / WhatsApp / apply buttons pinned at the bottom (reuse `MobileActionBar`). Lock body scroll while the drawer is open, and support closing with Esc and with the back gesture.
- **Accessibility:** keyboard navigable, `aria-expanded`, focus-visible rings, and a skip-to-content link.
- **Footer:** columns that mirror the nav, contact details and social icons from the API, campus addresses, and a small "Quick links" list.

## 4. New and extended pages: map them onto existing models first

Prefer existing tables. Add a new model only when nothing fits.

- **School Profile** (`/about-us/school-profile`): a one-page summary of the school. Cover:
  - an at-a-glance fact strip (levels offered, combinations, campuses, curriculum = NECTA, boarding/day, location)
  - mission, vision and core values (from `AboutPage`)
  - a short history
  - leadership highlights
  - academic programmes
  - results highlights
  - facilities
  - student life
  - admissions call to action

  Use `AboutPage` plus an `AboutMenuItem` with `slug="school-profile"` and its `AboutSection`s. Optionally offer a downloadable PDF profile through `AboutSection.file`.
- **Foundation & History**: an `AboutMenuItem` (`foundation-and-history`) whose sections render as a **vertical timeline**.
- **Leadership**: `LeadershipMember` records shown as person cards grouped by level (Governance → Head of School → Deputies → Heads of Department → Administration).
- **Campuses**: from `ContactOffice`, with an image, address, map, phone and hours per campus, plus a link to the contact directory.
- **Awards & Achievements**: an `AboutMenuItem` (`awards`) with sections per award, plus news items in the "Student Achievements" category.
- **Careers**: an `AboutMenuItem` (`careers`) for the culture or "work with us" page. Add a small additive `JobVacancy` model (title, department, type, deadline, description, `how_to_apply`, `is_active`) so openings can be managed. Show a friendly "no current vacancies, send your CV to …" state when there are none.
- **Departments**: add an additive `Department` model (name, slug, head (an FK to `LeadershipMember`, nullable), description, image, subjects, order, `is_active`), or `AcademicMenuItem` (`departments`) with sections. Pick one and justify it in `AUDIT.md`. Link existing `Course.department` values to it.
- **Student Profile** and **Life After School**: `StudentLifeMenuItem`s (`student-profile`, `life-after-school`) with sections; testimonials are reused where relevant.
- **Events grouped by month**: `/events` shows Upcoming and Past tabs.
  - Group events under month headings ("March 2026", "February 2026", …) using `event_date`.
  - Add a sticky month or year jump bar and a category filter (existing `news-event-categories`).
  - Each event card shows a large date badge, time, venue and category.
  - Event detail pages show the gallery, FAQs, an add-to-calendar (.ics) link, and a registration link if one is set.
  - The live data has events from Nov 2025 to Mar 2026, so test grouping against that data.
- **Gallery** (`/gallery`): a dedicated media hub that aggregates every gallery endpoint (`home-gallery`, `academic-gallery`, `admission-gallery`, `course-gallery`, `student-life-gallery`, `news-event-gallery`) plus `home-videos`.
  - Organise it as **albums**: one album per event or news item (using `news-event-gallery.event_item`/`news_item`), plus albums for Academics, Student Life, Campus and Admissions.
  - Use filter chips, a masonry or justified grid, lazy loading, and a keyboard- and swipe-friendly lightbox with captions.
  - Each event page links to its album, and the album links back to the event.
- **Contact Directory** (`/contact-us`): role-based contact cards built from `LeadershipMember` (role, name, phone, email). Add an additive boolean `show_in_directory` if needed.
  - Typical Tanzanian secondary-school roles: Head of School, Deputy Head / Second Master (Academics), Academic Master/Mistress, Discipline Master/Mistress, Admissions Officer, Bursar / Accounts, Patron & Matron (boarding), School Supervisor, plus the general office.
  - Add click-to-call, WhatsApp and mailto buttons, then the campuses and map, then the enquiry form (existing `EnquiryModalProvider` / submissions endpoint).

Keep every existing URL working, including `/admission/[slug]`, `/academics/[slug]`, `/courses/[slug]`, `/news/[slug]`, `/events/[slug]`, `/student-life/[slug]`, `/about-us/[slug]` and `/videos`, plus the existing redirects in `next.config.mjs`.

## 5. Homepage restructure

Use this order, and justify it:
1. Hero slider: the existing `home-sliders`, with bigger type, a darker overlay for readability, two CTAs (Apply, Explore Academics), and autoplay with pause controls.
2. Notice/announcement bar (`home-notices`).
3. "At a glance" statistics: real numbers only.
4. Welcome from the Head of School (photo, a short message, a link to the profile).
5. Programmes (FTNA / CSEE / ACSEE / other courses) as cards.
6. Why choose us (features).
7. Results and achievements highlight.
8. Upcoming events (next three) plus latest news (three).
9. Gallery teaser (an eight-image mosaic, linking to `/gallery`).
10. Videos (`home-videos`).
11. Testimonials.
12. Admissions call-to-action band.
13. Campuses and contact.

## 6. Default content: no blank areas

The site is database-driven. Write `seed_website_defaults` to fill every empty area (About, School Profile, History, Leadership, Departments, Student Profile, Life After School, Awards, Careers, Contact directory, and the FAQs per section).

- Learn the school's tone, programmes, locations and phone numbers from the existing records (sliders, courses, admission categories, news, events, contact offices), and reuse existing uploaded media URLs for images.
- Write realistic, professional, school-appropriate copy for a NECTA secondary school in Dar es Salaam.
- **Do not invent verifiable facts.** That covers founding year, founder names, staff names, exam pass rates, award names and registration numbers.
  - Use role titles in place of names ("Head of School").
  - Use neutral wording ("Founded with a vision to…").
  - Mark these records `[REVIEW]` in an internal field or in the admin panel, so the owner can replace them with true details.
- Also keep frontend fallbacks (`src/lib/fallbacks.ts`) so that a missing API record never shows an empty section. Render a graceful default instead.

## 7. SEO, performance and quality

- Per-page `generateMetadata` (using the existing `meta_title`/`meta_description` fields), Open Graph images from real photos rather than `favicon.ico`, and JSON-LD (`EducationalOrganization`, `Event`, `NewsArticle`, `BreadcrumbList`).
- Update `sitemap.ts` and `robots.ts` with the new routes, and remove the template routes from them.
- Lighthouse targets on mobile: Performance ≥ 85, Accessibility ≥ 95, Best Practices ≥ 95, SEO ≥ 95.
- Use ISR (`revalidate`), and add an on-demand revalidation endpoint that the admin calls after saves, so edits appear immediately.
- No horizontal scroll at any width from 320px to 1920px. Size images responsively. No layout shift from fonts.

## 8. Admin panel at `adminsite.britishschool.ac.tz`

Build a separate Next.js app (`website/admin-app`) that uses the same design tokens and fonts, so the two look like one family.

- **Auth:**
  - Log in against Django with the existing users, using session plus CSRF or JWT (`djangorestframework-simplejwt`; add it only if it isn't present, and keep it additive).
  - Only superusers or users with a `can_manage_website` permission can enter. Add that flag the same way `can_manage_home_enquiries` exists in `rps_app`, as a new field with `default=False`.
- **Configuration:**
  - Add `adminsite.britishschool.ac.tz` to `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` and CORS (scoped to the two origins only).
  - Add an nginx server block with TLS (certbot) proxying to the admin app's PM2 process. The owner will point the A record at the VPS IP, so issue the certificate once DNS resolves.
- **Layout:** a sidebar grouped like the public navigation (Home, About, Academics, Admissions, Student Life, News & Events, Gallery, Contact, Careers, Settings). It must collapse well on mobile.
- **Dashboard:** counts of the content in each section, new enquiries, pending testimonials, upcoming events, and records flagged `[REVIEW]` or placeholder.
- **For every resource:**
  - a list view with search, filters, sorting, pagination and an active/inactive toggle
  - a create/edit form with validation, image upload with preview and crop hints, rich text for content fields, a slug auto-generated from the title, and drag-to-reorder for `order` fields
  - nested editing: a menu item with its sections, FAQs and gallery on one screen
- **Deletion:** soft delete by default (set `is_active=False`). Hard delete is only for superusers, behind a typed confirmation.
- **Enquiries inbox:** mark as contacted and add notes (the fields already exist: `is_contacted`, `contacted_by`, `contact_notes`).
- **Testimonial moderation:** approve or reject.
- **Gallery manager:** bulk upload with album assignment.
- After each save, call the public site's revalidation endpoint, and show a toast with a "View on site" link.

## 9. Testing: prove it works before switching traffic

1. **Backend:**
   - Django tests showing that anonymous users can read but cannot write, delete or patch content.
   - Anonymous users can still create an enquiry and a testimonial.
   - Staff can perform full CRUD; non-staff are blocked.
   - Seed command checks: running it twice creates no duplicates, and it never overwrites existing values.
   - Run `python manage.py check --deploy` and `makemigrations --check` after applying.
2. **Frontend:** `npm run build` with zero type errors. Then use Playwright (Chromium is preinstalled) against the new build to:
   - Visit every route in the sitemap at 375×812, 768×1024 and 1440×900. Assert HTTP 200, no console errors, no horizontal overflow (`scrollWidth <= innerWidth`), no broken images, and no empty sections.
   - Open and close the mobile menu, expand every sub-menu and follow each link.
   - Check that events are grouped under correct month headings, and that the filter works.
   - Open the gallery lightbox and navigate it by keyboard.
   - Submit the enquiry form end to end.
   - Assert that the computed body font-size is ≥ 17px and that headings use the heading font family.
   - Take screenshots of every key page at mobile and desktop width, and review them critically yourself. Iterate until the design looks premium, balanced and consistent.
3. **Admin:** Playwright test that logs in, edits a record, uploads an image, reorders items, toggles active, and confirms the change appears on the public site after revalidation. Check that unauthorised users are redirected.
4. **Lighthouse** on Home, About/School Profile, Events and Gallery (mobile).
5. **Data integrity:** compare row counts for every `website_*` table before and after. They must be equal or higher. Also confirm the `rps_app` / `finance` / `payroll` tables are untouched.

## 10. Deliverables

- Working public site and admin panel, deployed with a rollback path.
- `website/AUDIT.md` (findings), `website/DEPLOY_NOTES.md` (backup, deploy, rollback, DNS/TLS steps for `adminsite`), and `website/CONTENT_REVIEW.md`. That last file lists every seeded `[REVIEW]` record, every suspected placeholder or test record, and every contradictory contact detail the owner must confirm.
- A short summary: what changed, test results with the actual output, screenshots, and anything left for the owner to decide.

Work in this order: safety backups → audit → API permission fix → design system → navigation/IA → pages → seed → tests → admin panel → admin tests → deploy. Commit after each step with clear messages.
