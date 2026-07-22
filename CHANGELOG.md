# Changelog

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
