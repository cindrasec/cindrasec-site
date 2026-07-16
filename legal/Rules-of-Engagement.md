# CINDRASEC — Authorization Letter & Rules of Engagement

**No signature, no scan.** · **স্বাক্ষর ছাড়া কোনো স্ক্যান নয়।**
This one document is the complete and only authority for the work described below. Its purpose is
to make every access by Cindrasec **authorized access** under applicable law, including the
Bangladesh Cyber Security Ordinance 2025.

> **Template v2 — canonical source.** Fill the `[bracketed]` fields per engagement. Have a lawyer
> review before the first *paid* engagement, and always for international clients. Not legal advice.

---

## 1 · Engagement

| Field | Detail |
|---|---|
| Reference no. | `CS-AUTH-[YYYY-MM-NNN]` |
| Client | `[legal name of company or person]` |
| Authorized signatory | `[name]` — `[title]` *(must have authority to bind the Client)* |
| Client contact | `[email]` · `[phone]` |
| Send findings to | `[name]` · `[email]` — findings go **only** to this person |
| Package | ☐ Free Pilot ☐ Snapshot ☐ Watch ☐ AI/LLM Assessment ☐ Other: `______` |
| Window | `[start date/time + timezone]` → `[end date/time]` ☐ Ongoing (Watch) |
| Testing source IP(s) | `[IPs for Client allowlisting]` |
| Emergency stop | Cindrasec: `[phone/email]` · Client: `[phone]` |

## 2 · Authorization

The Client, through the signatory above, gives **Md. Azmol Haque Rony — independent security
researcher, operating as "Cindrasec"** — clear written permission to perform the security
assessment defined in §3, and confirms that:

- the signatory is **authorized to bind the Client**;
- the Client **owns or lawfully controls every in-scope asset**, and no third party's permission is
  needed — or, where a host/cloud provider requires it, the Client has obtained it;
- the Client keeps its own backups and change control.

**এই অনুমতি লিখিত নোটিশে যেকোনো সময় তাৎক্ষণিকভাবে প্রত্যাহারযোগ্য — প্রত্যাহারেই সব টেস্টিং বন্ধ।**
This authorization is revocable in writing at any time; on revocation, all testing stops immediately.

## 3 · Scope

| # | In-scope asset (domain / IP / AI system) | Type |
|---|---|---|
| 1 | | |
| 2 | | |
| 3 | | |

**Out of scope by default:** anything not listed above · third-party infrastructure (shared hosting,
SaaS, payment processors, CDNs) · physical, social-engineering, or phishing testing · any
denial-of-service or destructive action. Assets found during discovery are **reported, not tested**,
until added here in writing (email confirmation from both contacts is enough). No verbal changes.

## 4 · Rules

| ✅ Authorized | 🚫 Prohibited (without separate written consent) |
|---|---|
| Passive recon & discovery — DNS, certificate transparency, OSINT | Active exploitation — RCE, privilege escalation, lateral movement |
| Detection of exposed secrets, credentials & misconfigurations | Data exfiltration beyond a minimal proof; altering or deleting Client data |
| **Minimal verification** — to confirm a found credential is live, one minimum-necessary metadata call to the issuing provider, nothing more | Denial-of-service, load / stress testing, breaking rate limits |
| Throttled automated scanning (≈ 2 requests/second per host) | Real-user account takeover or access to real user data |
| *AI/LLM package:* prompt-injection, jailbreak, data-leak & agent-abuse tests on listed AI systems, using test accounts only | Physical access, social engineering, phishing; testing other tenants or the model provider |

## 5 · Terms

| | |
|---|---|
| **Data** | Stored encrypted on Cindrasec's self-hosted infrastructure; credentials redacted in reports; raw data auto-purged **30 days** after delivery, or sooner on written request. |
| **Confidentiality** | Findings are confidential and go only to the recipient named in §1. |
| **Reporting** | Final report in **3–5 working days** of scan completion, with a coverage + confidence statement even if nothing is found. Critical/High findings escalated by phone + email within **24 hours** of confirmation. |
| **Assurance** | A point-in-time assessment, not a guarantee that every vulnerability is found. |
| **Liability** | Each party's total liability is capped at the fees paid, or ৳10,000, whichever is higher. Neither party is liable for indirect or consequential loss. False authorization info (ownership, authority) is the Client's responsibility. |
| **Termination** | Either party may end the engagement on 7 days' written notice; fees for completed work are non-refundable. Authorization revocation (§2) is always immediate. |
| **Governing law** | Bangladesh. A separate arbitration clause is added for international clients. |

## 6 · Case study *(optional)*

☐ **Yes** — after fixes are confirmed, Cindrasec may publish an anonymized, redacted case study;
the Client approves the final text first.
☐ **No** — no case study. *(Unticked = No.)*

## 7 · Signatures

| Client | Cindrasec |
|---|---|
| Name: | Name: Md. Azmol Haque Rony |
| Title: | Title: Independent Security Researcher — Cindrasec |
| Signature: | Signature: |
| Date: | Date: |
