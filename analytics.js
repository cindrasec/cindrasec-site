// Google Analytics 4 bootstrap.
//
// WHY THIS IS A FILE AND NOT AN INLINE <script>
// ---------------------------------------------
// Google ships this as an inline block. This site's CSP is `script-src 'self'`
// with no 'unsafe-inline' and no nonce (there is no server to generate one —
// GitHub Pages serves static files), so an inline block would be refused by the
// browser and the tag would silently never fire. Pasting Google's snippet
// verbatim yields analytics that look installed and collect nothing.
//
// Moving the four lines into a first-party file keeps the policy at 'self' for
// everything except googletagmanager.com, which has to be allowed explicitly
// because that is where gtag.js is served from. The alternative — adding
// 'unsafe-inline' to script-src — would weaken every page on the site to make
// one tag work, and 'unsafe-inline' cannot be scoped to a single script.
//
// ORDERING
// --------
// gtag.js and this file both only touch window.dataLayer, and gtag.js drains
// whatever is queued there whenever it finishes loading. So the two can load in
// either order and the config still applies; neither needs to block the parser.

window.dataLayer = window.dataLayer || [];
function gtag() { dataLayer.push(arguments); }

gtag('js', new Date());

gtag('config', 'G-9B4D7PCBEJ', {
  // The bilingual build means / and /bn/ are separate URLs for the same page.
  // Without this the reports read as two unrelated sites and the language split
  // — the thing actually worth knowing here — has to be reconstructed by hand.
  content_group: document.documentElement.lang === 'bn' ? 'Bengali' : 'English',
});
