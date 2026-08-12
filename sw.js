// Cindrasec service worker.
//
// STRATEGY, AND WHY IT CHANGED
// ----------------------------
// The previous version answered every request cache-first and revalidated in the
// background. A returning visitor therefore saw the *previous* deploy on this
// visit and the current one on the next, and the only lever that shortened that
// window was remembering to bump CACHE_NAME by hand on every content change.
// That step was missed once already — the privacy-notice release changed
// index.html, bn/index.html and styles.css and left the cache name at v10 — which
// is a reliable sign it will be missed again.
//
// A visitor with a working connection no longer depends on remembering anything:
//
//   documents, styles, scripts  ->  network-first; cache is an offline fallback only
//   fonts, icons, images        ->  cache-first (immutable in practice)
//
// A deploy is live on the very next request over a working connection. But the
// bump discipline isn't fully gone, and claiming it was is what caused the next
// bug: store() writes every successful network-first fetch into whatever cache
// CACHE_NAME currently names, and that entry sits there — potentially serving
// as the .catch() fallback on a later failed fetch — until either a fresh
// successful fetch overwrites it or a CACHE_NAME change makes activate() delete
// the whole cache. Browsers only re-install a worker whose *script bytes*
// changed, so an unbumped CACHE_NAME after a content-only change leaves the old
// worker running indefinitely with its stale entries intact — a mobile visitor
// whose fetch fails once can be served pre-change bytes with no ceiling on how
// old they are. That's exactly what happened to /research/'s styles.css. So:
// CACHE_NAME still has to change on every deploy that touches a network-first
// asset's content, not only when the PRECACHE list changes — the difference
// from the old cache-first worker is that a bump now only protects the
// fallback path, rather than being the only thing standing between a visitor
// and last week's deploy.
//
// Paths are derived from the registration scope, so this works at a domain root or
// under a GitHub Pages project subpath (https://username.github.io/repo-name/).
const CACHE_NAME = 'cindrasec-v12';
const SCOPE = self.registration.scope;

// Only genuinely static assets are precached. HTML, CSS and JS are deliberately
// absent: they come from the network and are cached as a byproduct, so a stale
// copy can never be the first thing a visitor is handed.
const PRECACHE = [
  SCOPE + 'manifest.json',
  SCOPE + 'icon.svg',
  SCOPE + 'icon-192.png',
  SCOPE + 'icon-512.png',
  SCOPE + 'apple-touch-icon.png',
  SCOPE + 'fonts/inter-var.woff2',
  SCOPE + 'fonts/space-grotesk-var.woff2',
  SCOPE + 'fonts/jetbrains-mono-var.woff2',
  SCOPE + 'fonts/noto-sans-bengali-var.woff2',
];

// request.destination for the things that must never be served stale.
// The empty string covers requests the browser does not classify (e.g. a
// same-origin fetch for JSON), which are likewise better fresh than fast.
const NETWORK_FIRST = new Set(['document', 'style', 'script', '']);

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Cache only first-party 200s. `type === 'basic'` keeps opaque cross-origin
// responses out, which would otherwise poison the cache with unreadable entries.
function store(request, response) {
  if (response && response.status === 200 && response.type === 'basic') {
    const copy = response.clone();
    caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
  }
  return response;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  // Same-origin only; cross-origin requests are none of this worker's business.
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (NETWORK_FIRST.has(request.destination)) {
    event.respondWith(
      fetch(request)
        .then((response) => store(request, response))
        // Offline: the exact request first, then the cached shell. The shell is
        // matched as SCOPE, not SCOPE + 'index.html' — nothing ever requests the
        // literal /index.html path, so the homepage is stored under '/' and an
        // '/index.html' lookup could never hit.
        .catch(() => caches.match(request).then(
          (cached) => cached || caches.match(SCOPE)
        ))
    );
    return;
  }

  // Fonts, icons, images: cache-first, refreshed in the background so a replaced
  // asset is picked up without a hard reload.
  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => store(request, response))
        .catch(() => cached);
      return cached || network;
    })
  );
});
