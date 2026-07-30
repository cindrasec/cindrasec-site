// Cindrasec — site behavior (v2). Invariant: no third-party scripts, no cookies,
// no localStorage of PII. The only cross-origin request this site ever makes is
// the intentional form POST to https://api.web3forms.com.
'use strict';

// mobile nav
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');
hamburger.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  hamburger.setAttribute('aria-expanded', String(open));
});
navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  navLinks.classList.remove('open');
  hamburger.setAttribute('aria-expanded', 'false');
}));

// Language is no longer a client-side toggle. English lives at / and Bengali at
// /bn/, generated from one source by build.py, joined by reciprocal hreflang.
// Hiding one language behind an attribute meant search engines never counted
// it; the switch in the header is now a plain link a crawler can follow.

// currency toggle
function setCurrency(cur){
  document.querySelectorAll('[data-cur]').forEach(el => el.hidden = el.dataset.cur !== cur);
  document.querySelectorAll('[data-cur-btn]').forEach(b => {
    b.classList.toggle('active', b.dataset.curBtn === cur);
    b.setAttribute('aria-pressed', String(b.dataset.curBtn === cur));
  });
}
document.querySelectorAll('[data-cur-btn]').forEach(b => b.addEventListener('click', () => setCurrency(b.dataset.curBtn)));
setCurrency('bdt');

// exposure estimator — live client-side scoring, nothing transmitted
const estForm = document.getElementById('estForm');
const estScoreEl = document.getElementById('estScore');
const estBarFill = document.getElementById('estBarFill');
const estVerdict = document.getElementById('estVerdict');
const estCta = document.getElementById('estCta');
const estReset = document.getElementById('estReset');

const MAX_WEIGHT = 4 + 4 + 4 + 3; // max possible raw weight across 4 questions
function computeScore(){
  const groups = ['surface', 'ai', 'last', 'team'];
  let total = 0, answered = 0;
  groups.forEach(g => {
    const checked = estForm.querySelector(`input[name="${g}"]:checked`);
    if (checked){ total += Number(checked.dataset.w); answered++; }
  });
  if (answered === 0) return null;
  // scale to 0-100, weighted toward answered questions actually present
  const pct = Math.round((total / MAX_WEIGHT) * 100);
  return Math.max(4, Math.min(100, pct));
}

function renderScore(){
  const score = computeScore();
  if (score === null){
    estScoreEl.textContent = '–';
    estBarFill.style.width = '0%';
    estVerdict.textContent = 'Answer the four questions to see where you stand.';
    return;
  }
  estScoreEl.textContent = score;
  estBarFill.style.width = score + '%';

  let color, verdict, cta;
  if (score < 30){
    color = '#33E0C8';
    verdict = `<strong>Lower relative exposure.</strong> Your footprint is small and recently checked. A Snapshot is still worth doing once a year, or before anything ships — you have less surface area, not zero.`;
    cta = 'Get a baseline Snapshot →';
  } else if (score < 60){
    color = '#FFC169';
    verdict = `<strong>Moderate exposure.</strong> Login flows, APIs, or a stale last-check are the kind of thing that quietly turns into a P1. A Snapshot will tell you exactly where you stand in a few hours.`;
    cta = 'Request a free Snapshot →';
  } else if (score < 82){
    color = '#FF5A36';
    verdict = `<strong>High exposure.</strong> Multiple surfaces, no dedicated owner, and/or an AI system in the mix — this combination is exactly what Watch is built for: continuous monitoring instead of a once-a-year guess.`;
    cta = 'Start continuous Watch monitoring →';
  } else {
    color = '#FF3B1F';
    verdict = `<strong>Critical exposure profile.</strong> An AI agent with tool access, a large surface, and no recent check is a real-world breach setup. Start with an AI/LLM Security Assessment alongside a Snapshot.`;
    cta = 'Book an AI/LLM assessment →';
  }
  estBarFill.style.background = `linear-gradient(90deg, ${color}, ${color}cc)`;
  estScoreEl.style.color = color;
  estVerdict.innerHTML = verdict;
  estCta.textContent = cta;
}

if (estForm){
  estForm.addEventListener('change', renderScore);
  renderScore();
}
if (estReset){
  estReset.addEventListener('click', () => {
    estForm.reset();
    // re-apply the form's own default-checked radios, then recompute
    requestAnimationFrame(renderScore);
  });
}

// back to top visibility
const toTop = document.getElementById('toTop');
if (toTop) {
  window.addEventListener('scroll', () => {
    toTop.classList.toggle('show', window.scrollY > 900);
  }, { passive: true });
}

// intake form -> Web3Forms (delivers to contact@cindrasec.com).
// Falls back to the visitor's mail client if no key is set yet OR the network fails,
// so a lead is never silently lost.
//   Setup: create a free access key at https://web3forms.com (verify contact@cindrasec.com),
//   then paste it below. Until then, the form opens the mail client (works immediately).
const WEB3FORMS_KEY = 'd9db6024-74a2-4f77-8b8e-ab95bc03feba';
const intakeForm = document.getElementById('intakeForm');
const formStatus = document.getElementById('formStatus');
const intakeSubmit = document.getElementById('intakeSubmit');

function buildMailto(f){
  const subject = `Snapshot Request — ${f.service.value}`;
  const body = [
    `Name: ${f.name.value.trim()}`,
    `Email: ${f.email.value.trim()}`,
    `Interested in: ${f.service.value}`,
    f.domain.value.trim() ? `Domain / target: ${f.domain.value.trim()}` : null,
    '',
    f.message.value.trim() || '(no additional message)'
  ].filter(Boolean).join('\n');
  return `mailto:contact@cindrasec.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}
function showStatus(cls, msg){
  if (!formStatus) return;
  formStatus.hidden = false;
  formStatus.className = 'form-status ' + cls;
  formStatus.textContent = msg;
}

const SUBMIT_COOLDOWN_MS = 20000;
let lastSubmitAt = 0;

if (intakeForm) {
  intakeForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (intakeForm.botcheck && intakeForm.botcheck.value) return;   // honeypot tripped
    if (!intakeForm.reportValidity()) return;
    const now = Date.now();
    if (now - lastSubmitAt < SUBMIT_COOLDOWN_MS){
      showStatus('error', 'Please wait a few seconds before sending again.');
      return;
    }
    lastSubmitAt = now;

    // No key configured yet → open the mail client (immediate, zero-setup).
    if (!WEB3FORMS_KEY || WEB3FORMS_KEY === 'YOUR_WEB3FORMS_ACCESS_KEY'){
      window.location.href = buildMailto(intakeForm);
      return;
    }

    intakeSubmit.disabled = true;
    showStatus('sending', 'Sending your request…');
    try {
      const res = await fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({
          access_key: WEB3FORMS_KEY,
          subject: `New Snapshot request — ${intakeForm.service.value}`,
          from_name: 'Cindrasec Website',
          name: intakeForm.name.value.trim(),
          email: intakeForm.email.value.trim(),
          service: intakeForm.service.value,
          domain: intakeForm.domain.value.trim(),
          message: intakeForm.message.value.trim(),
        }),
      });
      const data = await res.json();
      if (data.success){
        intakeForm.reset();
        showStatus('success', '✓ Request sent — we’ll reply within a day. Thank you.');
      } else {
        throw new Error(data.message || 'submit failed');
      }
    } catch (err){
      showStatus('error', 'Couldn’t send from here — opening your email app as a fallback…');
      setTimeout(() => { window.location.href = buildMailto(intakeForm); }, 900);
    } finally {
      intakeSubmit.disabled = false;
    }
  });
}

// copy email fallback
const copyBtn = document.getElementById('copyEmailBtn');
if (copyBtn) {
  copyBtn.addEventListener('click', async () => {
    const email = copyBtn.dataset.email;
    try {
      await navigator.clipboard.writeText(email);
    } catch {
      const ta = document.createElement('textarea');
      ta.value = email; document.body.appendChild(ta); ta.select();
      document.execCommand('copy'); document.body.removeChild(ta);
    }
    const original = copyBtn.textContent;
    copyBtn.textContent = 'Copied ✓';
    copyBtn.classList.add('copied');
    setTimeout(() => { copyBtn.textContent = original; copyBtn.classList.remove('copied'); }, 1800);
  });
}

// scroll reveal
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduceMotion && 'IntersectionObserver' in window) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); } });
  }, { threshold: 0.15 });
  document.querySelectorAll('.reveal').forEach(el => io.observe(el));
} else {
  document.querySelectorAll('.reveal').forEach(el => el.classList.add('is-visible'));
}

// terminal typing effect
const lines = [
  { text: '$ cindrasec scan --target yourcompany.com --mode passive', cls: '' },
  { text: '&gt; resolving attack surface... 42 assets discovered', cls: 'dim' },
  { text: '&gt; checking exposed configs, keys &amp; secrets...', cls: 'dim' },
  { text: '[ok]  TLS / DNS posture verified', cls: 'ok' },
  { text: '[!]   possible exposed credential pattern found (1)', cls: 'warn' },
  { text: '&gt; stage 2: verifying against live provider API...', cls: 'dim' },
  { text: '[verified] confirmed — active API key exposed', cls: 'verified' },
  { text: '&gt; generating report...', cls: 'dim' },
  { text: 'scan complete — 1 verified finding · 0 false positives · 38s', cls: 'ok' }
];
const termBody = document.getElementById('termBody');
function typeTerminal(){
  termBody.innerHTML = '';
  let li = 0;
  function nextLine(){
    if (li >= lines.length){
      termBody.innerHTML += '<span class="cursor"></span>';
      return;
    }
    const row = document.createElement('div');
    row.className = lines[li].cls;
    termBody.appendChild(row);
    const full = lines[li].text;
    let ci = 0;
    if (reduceMotion){ row.innerHTML = full; li++; nextLine(); return; }
    const speed = 14;
    const iv = setInterval(() => {
      ci += 2;
      row.innerHTML = full.slice(0, ci);
      if (ci >= full.length){ clearInterval(iv); li++; setTimeout(nextLine, 160); }
    }, speed);
  }
  nextLine();
}
const termObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting){ typeTerminal(); termObserver.disconnect(); } });
}, { threshold: 0.3 });
termObserver.observe(document.querySelector('.terminal'));

// service worker registration — safe no-op on file:// or unsupported browsers
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}
