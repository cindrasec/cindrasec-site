# Cindrasec — cindrasec.com

The public site for Cindrasec: automated attack-surface & AI/LLM security monitoring.
A **zero-build static site** — plain HTML/CSS/JS, no framework, no bundler, no build step —
deployed on GitHub Pages behind Cloudflare.

## Invariants (do not regress these)

1. **Zero third-party runtime dependencies.** The page contacts **no external host** at
   runtime except one intentional `POST https://api.web3forms.com/submit` when a visitor
   sends the contact form. No CDN scripts, no external fonts, no analytics, no trackers,
   no cookies. Fonts are self-hosted variable `.woff2` files in `/fonts`. If an edit
   reintroduces an external origin, that edit is wrong — this is the supply-chain surface
   of the whole site, and keeping it first-party is what makes it tamper-simple.
2. **Zero build step.** Every file in this repo is served as-is.
3. **The contact form never loses a lead.** It posts to Web3Forms (the access key in
   `app.js` is a public client-side key by design) and falls back to a pre-filled
   `mailto:` if the network call fails. Keep the honeypot (`botcheck`), the submit
   cooldown, and the fallback intact.
4. **Honest positioning.** No fabricated clients, logos, metrics, or testimonials.
   Impact-led, not fear-led. All testing language must reflect the signed
   RoE + Authorization Letter gate.

## What's in the repo

| File | Purpose |
|---|---|
| `index.html` | The site. CSP + referrer meta in `<head>`; JSON-LD (`ProfessionalService`, `FAQPage`) |
| `styles.css` | All styling + `@font-face` for the self-hosted fonts |
| `app.js` | All behavior (external so the CSP can use `script-src 'self'` with no `unsafe-inline`) |
| `fonts/*.woff2` | Self-hosted latin-subset variable fonts (Inter, Space Grotesk, JetBrains Mono) |
| `sw.js` | Service worker — network-first for documents/styles/scripts, cache-first for fonts/icons. **Bump `CACHE_NAME` whenever any shipped asset's content changes** (not only when the `PRECACHE` list changes — see the comment at the top of the file for why) and keep `PRECACHE` in sync with the file list |
| `404.html` | Branded not-found page (self-contained; absolute asset paths because it renders at any URL) |
| `.well-known/security.txt` | Disclosure contact (RFC 9116). `Expires:` is set one year out — refresh it |
| `_headers` | Canonical list of HTTP response headers to mirror in Cloudflare (see below) |
| `manifest.json`, icons, `og-image.png` | PWA install + social sharing |
| `robots.txt`, `sitemap.xml`, `CNAME` | Crawling + custom-domain config |

## Security headers — two layers

GitHub Pages cannot set custom HTTP headers, so headers are enforced in two places:

- **In-page (already shipped):** a strict `Content-Security-Policy` `<meta>` tag in
  `index.html` (`default-src 'self'`; scripts/styles first-party only, no `unsafe-eval`,
  no inline scripts; `connect-src` limited to self + `api.web3forms.com`), plus a
  `referrer` meta.
- **At the edge (configure in Cloudflare):** `frame-ancestors`/`X-Frame-Options`, HSTS,
  `X-Content-Type-Options: nosniff`, and `Permissions-Policy` only work as real HTTP
  headers. Mirror everything in the `_headers` file via **Cloudflare → Rules →
  Transform Rules → Modify Response Header**. Belt and suspenders: keep the meta CSP
  even after the edge CSP exists.

## No SRI on first-party assets (by design)

`styles.css` and `app.js` are referenced **without** `integrity` (SRI) hashes — and they
must stay that way. SRI protects against a tampered *third-party CDN*; these are first-party,
same-origin files already covered by the strict CSP (`style-src 'self'`, `script-src 'self'`).
Behind the Cloudflare proxy, SRI is actively harmful: any edge transform (minification,
optimization) changes the bytes, the browser's computed hash no longer matches the attribute,
and it **refuses to apply the stylesheet/script — leaving a completely unstyled page.** This
happened once; don't reintroduce SRI here. Bump `sw.js` `CACHE_NAME` when you change assets.

## Contact form

Submissions go to `contact@cindrasec.com` via Web3Forms. The key in `app.js` is a
public, client-side key (that is how Web3Forms works — it is safe in the page). If it is
ever rotated: create a new key at web3forms.com for `contact@cindrasec.com` and replace
`WEB3FORMS_KEY`. Until/unless the key works, the form still functions — it opens the
visitor's mail client pre-filled, and it also does that automatically on network failure.

## Deploy (GitHub Pages + Cloudflare)

1. Push to `main`. Repo must be **Public** (free GitHub Pages).
2. GitHub **Settings → Pages** → Deploy from a branch → `main` / `root` → Save.
   Confirm the custom domain shows `cindrasec.com` and enable **Enforce HTTPS** once the
   certificate issues. (`CNAME` in the repo already carries the domain.)
3. **Cloudflare DNS:** four apex `A` records `@` → `185.199.108.153`, `185.199.109.153`,
   `185.199.110.153`, `185.199.111.153`; `CNAME www` → `<org>.github.io`. Keep records
   **DNS-only (grey cloud)** until GitHub verifies the domain and issues the cert, then
   the proxy (orange cloud) may be re-enabled. SSL/TLS mode **Full** (never Flexible).
4. Add the response headers from `_headers` as Cloudflare Transform Rules (see above).

## Post-deploy checklist

- `https://cindrasec.com` loads with a valid cert; `www` → apex works.
- DevTools → Network: the **only** external origin ever contacted is
  `api.web3forms.com`, and only on form submit.
- Send a real test through the form → arrives at `contact@cindrasec.com`; block the
  network and confirm the `mailto:` fallback fires.
- PWA installs; `404.html` renders on a bogus path; `/.well-known/security.txt` resolves.
- No console errors; Lighthouse ≥ 95 across Performance / Accessibility /
  Best Practices / SEO.
- After any asset change: `sw.js` `CACHE_NAME` bumped, `PRECACHE` list matches shipped
  files. (No SRI hashes to regenerate — see "No SRI on first-party assets" above;
  reintroducing them is the one thing on this list that would break the page.)

## Editing content

`index.html` and `bn/index.html` are **generated** — do not edit them directly.

The single source is `src/index.src.html`, which carries both languages as
`<span data-en>…</span><span data-bn hidden lang="bn">…</span>` pairs. After
editing it:

```
python3 build.py            # regenerate both pages
python3 build.py --check    # CI-friendly: exits 1 if the output is stale
```

English is served at `/`, Bengali at `/bn/`, joined by reciprocal `hreflang`.
They are generated from one file so the two languages cannot drift apart.

Why not the old single-page toggle: content hidden at load is discounted by
search engines, so the Bengali half of the page earned nothing in Bengali
search. Separate URLs with hreflang is what Google documents for multilingual
sites, and the language switch in the header is now a real link a crawler can
follow rather than a script.
