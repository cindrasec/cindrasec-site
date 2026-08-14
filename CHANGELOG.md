# Changelog

## robots.txt: the crawl-block that only applied to one bot (2026-08-13)

### Fixed
- **`Disallow: /src/` and `Disallow: /build.py` applied to `cohere-ai` alone.** They sat
  at the very end of the file, directly after `User-agent: cohere-ai`, and under RFC 9309
  a rule belongs to the user-agent group that precedes it. So the one crawler that could
  not index the duplicate source was a mid-tier AI crawler, while Googlebot — the only
  one whose opinion on duplicate content actually matters — was free to index
  `src/index.src.html`, which reproduces both published pages almost verbatim. The
  comment above those lines said the file "should not be crawled in the first place";
  it had not been achieving that for any crawler that mattered.

  Moved into the `User-agent: *` group, which is the group Googlebot matches.

- **Ordered the `Disallow` lines before `Allow: /`.** Google resolves conflicting rules
  by longest match, under which `Disallow: /src/` wins regardless of order. Other
  parsers — Python's stdlib `robotparser` among them — return the first matching rule,
  and `Allow: /` matches every path, so under that reading the disallow never fired.
  Verified with a real parser before and after: the previous arrangement left `/src/`
  fetchable, the new one blocks it under both interpretations.

### Noted — not a repository change
Cloudflare is prepending a **managed robots.txt block** to what this repo serves, and it
disallows exactly the crawlers this file deliberately allows: `GPTBot`, `ClaudeBot`,
`Google-Extended` and `Applebot-Extended` (plus Amazonbot, Bytespider, CCBot,
meta-externalagent). The live file therefore contains two `User-agent: *` groups and two
`User-agent: GPTBot` groups with contradictory directives — precisely the "ambiguous
robots file" this file's own comment warns is "a reason for a crawler to skip a small
domain."

Scope, stated accurately rather than alarmingly: **Googlebot is not blocked**, so search
indexing and the Search Console submission are unaffected — `Google-Extended` governs
Gemini training, not search. Nor are `OAI-SearchBot`, `Claude-SearchBot`,
`PerplexityBot`, `ChatGPT-User` or `cohere-ai`. The blocked set is the bulk-crawl and
training bots. It still contradicts a deliberate decision recorded in this repo, and the
resolution is a Cloudflare dashboard setting (AI crawler blocking, default-on for new
zones), not a change here.

Found by SecretNode's own deep scan of cindrasec.com, which flagged the disallow-all —
correctly, against the served file, though not against the committed one.


## Correcting the service-worker's own claim about itself (2026-08-12)

### Fixed
- **The comment at the top of `sw.js` said freshness "no longer depends on
  remembering anything" and that `CACHE_NAME` "only has to change when the
  precache LIST changes." Both are wrong, and the v12 bump earlier today is
  the proof.** `store()` writes every network-first fetch into whatever cache
  `CACHE_NAME` currently names; that entry is the `.catch()` fallback on a
  later failed fetch, and it sits there until a fresh successful fetch
  overwrites it or a `CACHE_NAME` change forces `activate()` to delete it.
  Browsers only reinstall a worker whose script bytes changed, so leaving
  `CACHE_NAME` untouched after a content-only change (as happened when the
  research-page CSS shipped) leaves the old worker running indefinitely with
  stale entries a mobile visitor's failed fetch can still surface — no age
  ceiling. Rewrote the comment to say what's actually true: the bump
  discipline now protects the fallback path instead of being the only thing
  standing between a visitor and last week's deploy, but it did not go away.
  `README.md`'s "What's in the repo" table and post-deploy checklist matched
  the old, incorrect claim and are corrected to match.
- **`README.md`'s post-deploy checklist told a future maintainer to
  regenerate SRI hashes** — two sections above the one explaining, in detail,
  why SRI must never be reintroduced (it broke production once, `4a45b89`).
  Removed the contradiction.

## Accessibility pass: content invisible without JS, plain-language subheads (2026-08-12)

### Fixed
- **Every `.reveal` element was permanently invisible with JavaScript disabled.**
  `styles.css` sets `.reveal{ opacity:0 }` and only `app.js`'s scroll observer
  ever adds the `.is-visible` class that reveals it — which covers nearly
  every section on the page, including the hero terminal. A visitor with JS
  blocked (the exact audience the `<noscript>` banner is written for) saw the
  banner's promise that the site "works best with JavaScript enabled" but not
  a broken one — in practice most of the page was present in the DOM and
  unreadable. Added `noscript.css`, loaded only via a `<noscript><link>` (so
  JS-enabled visitors fetch nothing extra), that forces `.reveal` to its
  visible state. `styles.css`'s existing `prefers-reduced-motion` override
  uses the identical pattern, so this closes the same gap for the no-JS case.

### Added
- **A plain-language subhead under every major section heading.** The brand
  voice headings (`We find the spark before it becomes a fire`, `Three rules
  that never bend`, `The moat isn't the tool`, …) carry no search-relevant
  keywords, and two sections (How We Work, FAQ) had no descriptive line at
  all beneath their `<h2>`. Added a small `.section-kicker` line under each —
  bilingual, plainly worded, sitting between the heading and the existing
  flowing intro paragraph rather than replacing anything.

## Service-worker cache bump; llms.txt points at the site, not GitHub (2026-08-12)

### Fixed
- **`CACHE_NAME` `cindrasec-v11` → `cindrasec-v12`.** The research pages added
  CSS to `styles.css` without bumping the cache name. Documents, styles and
  scripts are network-first (see the strategy note at the top of `sw.js`), so
  a fresh visitor was never affected — but a returning visitor whose worker was
  still install-pinned to `v11` could be served the precache's stale copy on a
  slow or offline network path before the network-first fetch settled. This is
  the exact edge case the file's own comment warns about: `CACHE_NAME` "only
  has to change when the precache LIST changes," and the list didn't change
  here, but a build did land that assumes the new styles are already cached.
  Confirmed on a real device: `/research/` rendered unstyled on a phone
  carrying the old worker while `curl` showed the correct `styles.css` live.
  One-line bump, no logic change.
- **`llms.txt` linked the two research writeups to raw GitHub instead of the
  cindrasec.com pages that now exist for them.** Both writeups were published
  under `/research/` in the previous entry below, each with its own canonical
  tag, but `llms.txt` was never updated to match — so a model citing this
  file would send readers, and search-ranking signal, to GitHub instead of
  the domain the rest of the site is built to establish authority for. Both
  entries in the "Published research" section now point at
  `cindrasec.com/research/...`.

## Discoverability for answer engines (2026-08-12)

### Added
- **`/llms.txt`.** A condensed, factual summary of the studio, the four services
  with their real price ranges and delivery times, the published research with
  its actual figures (46.9% vs 10.2%, 95% CIs, the 4.6x gap and what it means),
  SecretNode's scope, and the data-handling policy. Assistants that answer
  "who does LLM security testing in Bangladesh" currently have to infer from
  marketing copy scattered across a landing page; this gives them something
  precise to quote, including the limits of what the research actually claims.
  Every number in it matches a published source.
- **Explicit crawler permissions for answer engines** in `robots.txt` — GPTBot,
  OAI-SearchBot, ChatGPT-User, ClaudeBot, Claude-User, Claude-SearchBot,
  PerplexityBot, Perplexity-User, Google-Extended, Applebot-Extended, cohere-ai.
  The existing `User-agent: *` wildcard already permitted them, but an explicit
  allow removes the ambiguity a crawler may otherwise resolve conservatively on
  a small, young domain. Being quoted accurately is worth more here than the
  click a link would have produced. A `LLMs:` pointer to `/llms.txt` sits beside
  the existing `Sitemap:` line.

## MCP named, offline shell repaired, SRI record corrected (2026-08-12)

### Fixed
- **The offline fallback could never fire.** When a document request failed and
  the exact URL was not in the cache, the service worker fell back to
  `caches.match(SCOPE + 'index.html')`. Nothing ever requests that literal path —
  a browser asks for `/`, so `store()` files the homepage under `/` — which meant
  the fallback key did not exist in the cache and the lookup always missed. An
  offline visitor to any page they had not already loaded got the browser's
  network-error screen instead of the site shell. The fallback now matches
  `SCOPE`, which is the key the homepage is actually stored under. `CACHE_NAME`
  is unchanged: the precache list did not change, and browsers reinstall a worker
  whose bytes differ regardless.
- **The changelog claimed a security control the site deliberately does not
  ship.** The v2 entry below lists "Subresource integrity (`sha384`) on
  `styles.css` and `app.js`" under Added, and nothing after it records what
  happened next: SRI was removed in `4a45b89` because Cloudflare's edge
  transforms rewrite the bytes, the browser's computed hash stops matching the
  attribute, and it refuses to apply the stylesheet — the page rendered
  completely unstyled in production. `README.md` documents the reasoning in
  full and instructs against reintroducing it. The changelog never caught up, so
  reading it top to bottom implied SRI was still active. That entry stays as
  written — it was true on 2026-07-15 — and this note is the correction. First-
  party, same-origin assets are covered by the strict CSP (`style-src 'self'`,
  `script-src 'self'`); SRI defends against a tampered third-party CDN, which is
  not the threat here.

### Added
- **MCP and agentic tool surfaces are named explicitly.** The AI/LLM card
  offered "Agent / tool-abuse testing", which describes the category from the
  outside; MCP is the term engineers building these systems actually use and
  search for. Added a fourth line item covering tool poisoning, indirect
  injection and consent flows, named MCP servers in the card description and the
  pricing comparison row, and extended the `knowsAbout` array and meta keywords
  with "MCP Security" and "Agentic AI Security". Both languages, no new claims
  about measured results — the tooling exists, the trial counts behind it do not
  yet meet the standard the published research holds itself to.

## Pricing — the currency toggle reaches the pricing table (2026-08-07)

### Fixed
- **A visitor who clicked "Pricing" in the nav could never see USD.** The only
  `৳ / $` toggle on the page lived in `#services`; the nav's "Pricing" link
  (and any direct link to `#pricing`) scrolls straight to a separate section
  further down, skipping over it entirely. That section's own copy says
  "Toggle ৳ / $ above" — true only for a visitor who happened to scroll down
  from the top of the page, not for anyone who arrived via the link meant to
  take them there directly. A global visitor landing on `#pricing` had no
  visible way to reach the USD figures the FAQ and JSON-LD both promise exist.

  Added a second instance of the same toggle at the top of `#pricing`.
  `setCurrency()` in `app.js` already binds every `[data-cur-btn]` and toggles
  every `[data-cur]` element document-wide, so this needed no script change —
  clicking either toggle keeps both in sync.

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
