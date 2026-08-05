# Changelog

## Pricing — the Gig rejoins the local price book (2026-08-05)

### Fixed
- **The Productized Gig cost more than a Snapshot in taka.** It is described on
  the same card as "the lowest-commitment way to start" and delivers in 2–4
  hours, yet it was priced ৳16,000–55,000 against the Snapshot's ৳15,000–25,000
  — a full external scan taking 3–5 days. In USD the order was correct
  ($150–500 against $250–600), so the ladder inverted the moment a visitor
  pressed the currency toggle, and it read wrong by default on the Bengali page,
  which is the one the intended customer reads.

  The cause was that the Gig's taka figure had been converted at the market rate
  (~110 ৳/$) while Snapshot, Watch and the AI/LLM assessment were deliberately
  localised (~60, ~33 and ~20 respectively). One tier was quoting an exchange
  rate; the other three were quoting a price.

  Now **৳7,000–15,000**, which puts the Gig's local discount at ~47–33× — between
  Snapshot's and Watch's, so it obeys the same price book as everything else —
  and tops the entry tier out exactly where the Snapshot begins.

## Delivery correctness pass (2026-08-04)

### Fixed
- **The service worker served the previous deploy.** It answered every request
  cache-first and revalidated in the background, so a returning visitor saw the
  last release on this visit and the current one on the next. The only lever
  that shortened that window was bumping `CACHE_NAME` by hand — a step the
  privacy-notice release already missed while changing `index.html`,
  `bn/index.html` and `styles.css`. Documents, styles and scripts are now
  network-first with the cache as an offline fallback; fonts, icons and images
  stay cache-first. A deploy is live on the next request, and `CACHE_NAME` only
  has to move when the precache *list* changes.
- **`.nojekyll` added.** GitHub Pages runs Jekyll by default, and Jekyll skips
  paths beginning with a dot — which silently excluded `/.well-known/security.txt`,
  the disclosure contact a security vendor is least able to afford missing. The
  site uses no Jekyll templating, so disabling it changes nothing else.
- **`sitemap.xml` is generated, not hand-maintained.** It claimed `2026-07-31`
  while both pages had been rebuilt on `2026-08-04`. `build.py` now emits it and
  moves `lastmod` only when the built HTML actually changed, so an unchanged
  rebuild stays byte-identical and no page is re-announced without cause.
- **`sample-finding.pdf` no longer carries its toolchain in its metadata.** The
  title read `onepager.html`, the creator `HeadlessChrome/141`, the producer
  `Skia/PDF`. Retitled to the document's actual name; page content and rendering
  are byte-for-byte unchanged.

### Changed
- **`manifest.json` declares an explicit `id`.** Install identity no longer
  depends on `start_url` staying put.
- **`_headers` documents why `style-src` allows `'unsafe-inline'`.** It is there
  for `404.html`, which inlines its CSS so an error page costs one request. The
  published pages ship a stricter `<meta>` CSP (`style-src 'self'`) and browsers
  enforce the intersection, so the loosening never reaches them. It was reading
  as drift; it is a deliberate floor.

## SEO fix — FAQ structured-data parity (2026-07-22)

### Fixed
- **`FAQPage` JSON-LD now mirrors the visible FAQ.** The structured data listed only
  5 Q&As — including a phantom "How fast is delivery? → 3 to 5 hours" question that does
  not appear on the page, and a stale data-handling answer ("purge after engagement
  close" vs. the page's "auto-purged 30 days after delivery"). Rebuilt the markup to
  match all 8 visible questions and answers verbatim, restoring Google's requirement that
  FAQ markup reflect on-page content and removing the delivery-time inconsistency.

## v2 — Cyber-resilience pass (2026-07-15)

### Removed
- **All third-party runtime dependencies.** Google Fonts (`fonts.googleapis.com` +
  `fonts.gstatic.com`) removed from `index.html` and `404.html`; replaced with
  self-hosted latin-subset variable `.woff2` fonts in `/fonts` (~102 KB total,
  `font-display: swap`, preloaded). At runtime the site now contacts **zero external
  hosts** except the intentional form `POST` to `api.web3forms.com`.
- **Unclaimed LinkedIn company link** (`linkedin.com/company/cindrasec`) — removed from
  the contact buttons and from JSON-LD `sameAs`; replaced in the contact section with
  the real SecretNode GitHub repository.
- All inline `style=""` attributes (moved to classes so the CSP can drop
  `unsafe-inline` for styles).

### Added
- **Strict Content-Security-Policy meta** on `index.html`: `default-src 'self'`,
  `script-src 'self'` (no inline scripts, no `unsafe-eval`), `style-src 'self'`,
  `connect-src 'self' https://api.web3forms.com`, `img-src 'self' data:`,
  `base-uri 'self'`, `object-src 'none'`, `form-action 'self'`,
  `upgrade-insecure-requests`. A scoped CSP was also added to `404.html`.
- **`_headers` file** documenting the full edge header set (HSTS, `frame-ancestors`,
  `X-Content-Type-Options`, `Permissions-Policy`, `Referrer-Policy`, full CSP) to be
  mirrored as Cloudflare Transform Rules — these cannot be delivered via `<meta>`.
- **`/.well-known/security.txt`** (RFC 9116) with contact, expiry, languages, canonical.
- **"How We Work" trust section** (`#how-we-work`, bilingual): the RoE/authorization
  gate, data-handling commitments (self-hosted, encrypted at rest, deleted on request,
  no trackers/cookies), and disclosure ethics.
- **Subresource integrity** (`sha384`) on `styles.css` and `app.js`.
- **Form abuse resistance:** `maxlength` caps on all inputs and a 20-second client-side
  submit cooldown, alongside the existing honeypot. Status messages remain static
  strings rendered via `textContent` (no XSS sink).
- **Accessibility:** `aria-expanded`/`aria-controls` on the mobile menu,
  `aria-pressed` on the language and currency toggles, `aria-hidden` on the decorative
  terminal animation, `lang="bn"` on all Bangla text, and a contrast fix — `--muted-2`
  `#6E7580` → `#8A919C` (was 3.3–4.0:1 against the dark backgrounds, now ≥ 4.9:1;
  every other palette pair already passed WCAG 2.1 AA).
- **Web3Forms key wired** in `app.js` (public client-side key), so submissions deliver
  to the inbox with the `mailto:` fallback intact.

### Fixed
- `404.html` asset paths made absolute (`/icon.svg`, `/fonts/…`) — the page renders at
  arbitrary URLs, so relative paths 404'd on nested missing paths.
- Service worker cache list re-synced with shipped assets (`styles.css`, `app.js`,
  fonts, `404.html`, `apple-touch-icon.png`) and `CACHE_NAME` bumped `v1` → `v2` so no
  stale shell is served.
- `sitemap.xml` gained `<lastmod>`.

### Structure
- CSS and JS extracted from the single-file page into `styles.css` / `app.js`
  (still zero-build; this is what makes the no-inline-script CSP possible).
- README rewritten around the supply-chain invariant, the two-layer header model,
  SRI regeneration, and the deploy/verify checklist.

### Verified against v1 behavior (no regressions)
- Exposure Risk Estimator: identical scoring, still fully client-side, stores nothing.
- Contact form: Web3Forms POST + inline status + `mailto:` fallback + honeypot.
- ৳/$ currency toggle across all four tiers; EN/বাংলা language toggle.
- PWA install, offline shell, branded 404, print styles, reduced-motion handling.
