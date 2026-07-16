// Cindrasec service worker — minimal, cache-first for static shell, network-first fallback.
// Uses relative/scope-derived paths so it works whether deployed at a domain root
// or a GitHub Pages project subpath (https://username.github.io/repo-name/).
const CACHE_NAME = 'cindrasec-v3';
const SCOPE = self.registration.scope; // e.g. https://user.github.io/repo/
const PRECACHE = [
  SCOPE,
  SCOPE + 'index.html',
  SCOPE + 'styles.css',
  SCOPE + 'app.js',
  SCOPE + 'manifest.json',
  SCOPE + 'icon.svg',
  SCOPE + 'icon-192.png',
  SCOPE + 'icon-512.png',
  SCOPE + 'apple-touch-icon.png',
  SCOPE + 'fonts/inter-var.woff2',
  SCOPE + 'fonts/space-grotesk-var.woff2',
  SCOPE + 'fonts/jetbrains-mono-var.woff2',
  SCOPE + '404.html',
];

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

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  // Only handle same-origin requests; let cross-origin (fonts, etc.) pass through normally.
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    caches.match(request).then((cached) => {
      const network = fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => cached || caches.match(SCOPE + 'index.html'));
      return cached || network;
    })
  );
});
