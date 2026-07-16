# CINDRASEC — Rules of Engagement & Authorization to Test
*security assessment agreement · RoE version 3.0*

> **In one line:** you authorize Cindrasec to safely test only the systems you list below, during the
> agreed window. **Nothing is scanned until both parties sign.**
> - ✓ Passive-first — your systems are not modified or taken offline.
> - ✓ Findings are confidential and go only to the person you name.
> - ✓ You can revoke this permission in writing at any time — testing stops at once.
>
> *স্বাক্ষর ছাড়া কোনো স্ক্যান নয়। অনুমতি লিখিতভাবে যেকোনো সময় প্রত্যাহারযোগ্য — প্রত্যাহারেই টেস্টিং বন্ধ।*

---

## 1. Engagement

| | |
|---|---|
| Reference | `CS-AUTH-[YYYY-MM-NNN]` · RoE version 3.0 |
| Client (company / person) | |
| Authorized signatory | Name ________  Title ________ |
| Client contact | Email ________  Phone ________ |
| Send findings only to | Name ________  Email ________ |
| Package | ☐ Free Pilot ☐ Snapshot ☐ Watch ☐ AI/LLM ☐ Other ____ |
| Testing window | ________ → ________ (date · time · timezone) ☐ Ongoing (Watch) |
| Cindrasec source IP(s) | ________ (for your allowlisting) |
| Emergency stop | Cindrasec [phone/email] ____ · Client ____ |

## 2. Scope — the only systems that may be tested

| # | In-scope asset (domain / IP / AI system) | Type | Client initials |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Out of scope (default):** anything not listed above · third-party infrastructure (shared hosting,
SaaS, payment processors, CDNs) · physical, social-engineering & phishing tests · any denial-of-service
or destructive action. New assets found while testing are **reported, not tested**, until added here in
writing (email from both contacts is enough). No verbal changes.

## 3. Rules

| Authorized | Not permitted without separate written consent |
|---|---|
| Passive recon & discovery (DNS, certificate transparency, OSINT) | Active exploitation — RCE, privilege escalation, lateral movement |
| Detecting exposed secrets, credentials & misconfigurations | Data exfiltration beyond a minimal proof; changing or deleting your data |
| Minimal verification: one minimum-necessary metadata call to a provider to confirm a found credential is live — nothing more | Denial-of-service, load / stress testing, breaking rate limits |
| Throttled automated scanning (≈ 2 requests/second per host) | Taking over real user accounts or accessing real user data |
| AI/LLM package: prompt-injection, jailbreak, data-leak & agent-abuse tests on the listed AI systems, using test accounts only | Physical access, social engineering, phishing; testing other tenants or the model provider |

## 4. Key terms

| | |
|---|---|
| **Data** | Encrypted on Cindrasec self-hosted infrastructure; credentials redacted in reports; raw data auto-deleted **30 days** after delivery, or sooner on written request. |
| **Confidentiality** | Findings are confidential and go only to the recipient named in §1. |
| **Reporting** | Final report within **3–5 working days** of scan completion — with a coverage & confidence statement even if nothing is found. Critical/High escalated by phone + email within **24 hours**. |
| **Assurance** | A point-in-time assessment — not a guarantee that every vulnerability is found. |
| **Liability** | Each party's total liability is capped at fees paid, or **BDT 10,000, whichever is higher**; no indirect or consequential loss. False authorization details (ownership, authority) are the Client's responsibility. |
| **Termination** | Either party may end this on 7 days' written notice; fees for completed work are non-refundable. Revoking authorization (§5) is always immediate. |
| **Governing law** | Bangladesh. A separate arbitration clause is added for international clients. |

## 5. Authorization & signatures

By signing, the Client authorizes **Md. Azmol Haque Rony** — independent security researcher,
operating as "Cindrasec" — to perform the assessment above, and confirms that:

- the signatory has authority to bind the Client;
- the Client owns or lawfully controls every in-scope asset (no third-party permission is needed, or it has been obtained);
- the Client keeps its own backups and change control.

*This authorization establishes authorized access under applicable law, including the Bangladesh
Cyber Security Ordinance 2025, and is revocable in writing at any time — on revocation all testing
stops immediately.*

| Client | Cindrasec |
|---|---|
| ☐ I confirm I am authorized to approve testing of the assets in §2. | |
| Name ________________ | Name  Md. Azmol Haque Rony |
| Title ________________ | Title  Independent Security Researcher — Cindrasec |
| Signature ____________ | Signature ____________ |
| Date __________ | Date __________ |

---
*Draft template — have a lawyer review before the first paid engagement, and always for
international clients. Not legal advice.*
