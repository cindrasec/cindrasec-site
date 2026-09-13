// Diagnostic for /ga-debug.html. Temporary — delete with the page.
//
// WHAT IT IS FOR
// --------------
// Every check that can be run from a laptop against a local copy of this site
// passes, and Google Analytics still receives nothing. The one thing local
// testing structurally cannot see is a Content-Security-Policy delivered as an
// HTTP *header* by Cloudflare: GitHub Pages cannot set headers, so the local
// server sends none, and the page's own <meta> policy is all that applies.
//
// In a browser, a page is bound by the INTERSECTION of every policy it
// receives. A Cloudflare response-header CSP written before Analytics existed
// would omit googletagmanager.com, and would then block the tag on the page
// while leaving every other symptom untouched — the file still serves the right
// ID, the tag URL still loads when typed into the address bar (a top-level
// navigation is not subject to any page CSP), and nothing appears in reports.
//
// This script reads the headers the live site actually returns, which a
// same-origin fetch is allowed to do, and reports any CSP violation the browser
// raises. It turns an invisible failure into something readable on a phone.

const out = document.getElementById('out');

function line(label, value, state) {
  const row = document.createElement('div');
  row.className = 'row ' + (state || '');
  const k = document.createElement('div');
  k.className = 'k';
  k.textContent = label;
  const v = document.createElement('div');
  v.className = 'v';
  v.textContent = value;
  row.append(k, v);
  out.append(row);
}

function heading(text) {
  const h = document.createElement('h2');
  h.textContent = text;
  out.append(h);
}

// Any policy violation on this page, from the meta tag or from a header.
// originalPolicy is the full policy string that was violated, so it names the
// source of the rule even when the rule did not come from this document.
const violations = [];
document.addEventListener('securitypolicyviolation', (e) => {
  violations.push(e);
});

(async () => {
  heading('1. Headers the live site returns');

  // Same-origin, so the response headers are readable. cache:'no-store' and a
  // unique query keep an edge or browser cache from answering instead.
  let headers = null;
  try {
    const res = await fetch('/?gadebug=' + Date.now(), { cache: 'no-store' });
    headers = res.headers;
    const interesting = [
      'content-security-policy',
      'content-security-policy-report-only',
      'strict-transport-security',
      'x-frame-options',
      'x-content-type-options',
      'permissions-policy',
      'cf-cache-status',
      'server',
    ];
    let foundCsp = false;
    for (const name of interesting) {
      const value = headers.get(name);
      if (value) {
        if (name.startsWith('content-security-policy')) foundCsp = true;
        line(name, value, name.startsWith('content-security-policy') ? 'warn' : '');
      }
    }
    if (!foundCsp) {
      line('content-security-policy', 'NOT SENT as a header — only the <meta> policy applies', 'ok');
    }
  } catch (err) {
    line('fetch failed', String(err), 'bad');
  }

  heading('2. Does the CSP header allow Analytics?');
  const headerCsp = headers && (headers.get('content-security-policy') || '');
  if (!headerCsp) {
    line('verdict', 'No header CSP, so it cannot be blocking anything.', 'ok');
  } else {
    for (const [label, needle] of [
      ['script-src allows googletagmanager.com', 'googletagmanager.com'],
      ['connect-src allows google-analytics.com', 'google-analytics.com'],
    ]) {
      const present = headerCsp.includes(needle);
      line(label, present ? 'yes' : 'NO — THIS IS THE PROBLEM', present ? 'ok' : 'bad');
    }
  }

  heading('3. Can the tag actually load from this page?');
  // Built from parts so the literal URL is assembled at runtime rather than
  // sitting in the page source; this file is a diagnostic, not a second tag.
  const tagUrl = 'https://www.' + 'googletagmanager' + '.com/gtag/js?id=G-G55N8ZL68Z';
  const loaded = await new Promise((resolve) => {
    const s = document.createElement('script');
    s.async = true;
    s.src = tagUrl;
    s.onload = () => resolve(true);
    s.onerror = () => resolve(false);
    document.head.append(s);
    setTimeout(() => resolve(false), 8000);
  });
  line('gtag.js loaded', loaded ? 'YES' : 'NO — blocked or unreachable', loaded ? 'ok' : 'bad');
  line('gtag.js executed', typeof window.google_tag_data !== 'undefined' ? 'YES' : 'no',
       typeof window.google_tag_data !== 'undefined' ? 'ok' : 'bad');

  heading('4. Can a hit reach Google?');
  const beacon = await new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve('reached');
    img.onerror = () => resolve('blocked or refused');
    img.src = 'https://www.google-analytics.com/collect?v=1&t=pageview&tid=G-G55N8ZL68Z&cid=debug';
    setTimeout(() => resolve('timed out'), 6000);
  });
  line('image beacon', beacon, beacon === 'reached' ? 'ok' : 'warn');

  heading('5. CSP violations raised on this page');
  await new Promise((r) => setTimeout(r, 600));
  if (!violations.length) {
    line('violations', 'none', 'ok');
  } else {
    violations.forEach((v, i) => {
      line('blocked #' + (i + 1), v.blockedURI || '(inline)', 'bad');
      line('  directive', v.violatedDirective, 'bad');
      line('  policy', (v.originalPolicy || '').slice(0, 300), 'warn');
    });
  }

  heading('Summary');
  const blockedByHeader = headerCsp && !headerCsp.includes('googletagmanager.com');
  if (blockedByHeader) {
    line('CAUSE', 'A Cloudflare response-header CSP is blocking the tag. '
       + 'Fix it in Cloudflare: Rules -> Transform Rules -> Modify Response Header, '
       + 'and make its Content-Security-Policy match the one in the repo _headers file.', 'bad');
  } else if (!loaded) {
    line('CAUSE', 'The tag could not load, but not because of a header CSP. '
       + 'Check for an ad blocker, a VPN, or a Private DNS setting on this device.', 'bad');
  } else if (beacon !== 'reached') {
    line('CAUSE', 'The tag loads but the hit does not reach Google. Something on this '
       + 'network or device is dropping requests to google-analytics.com.', 'bad');
  } else {
    line('RESULT', 'Everything on this page works. The tag loads and a hit reaches '
       + 'Google, so the problem is on the Analytics side — most likely which '
       + 'property is being viewed, or a data filter excluding this traffic.', 'ok');
  }
})();
