# LusoSupport-PT — Announcement Templates (AMALIA Pivot)

> **Project evolution:** these templates replace the original generic-audience templates (Reddit r/MachineLearning, r/LocalLLaMA, r/datasets, generic LinkedIn) with copy targeted at AMALIA-adjacent audiences, per the [2026-08-28 pivot strategy](../superpowers/specs/2026-08-28-amalia-pivot-strategy.md). The dataset, pricing, and links are unchanged — only the framing and target channels shifted. The original templates remain available in git history (see `git log -p -- docs/launch/announcement-templates.md`).

Ready-to-post copy for announcing the AMALIA-specialization positioning of LusoSupport-PT.

---

## 1. AMALIA Hugging Face org / community discussion

**Where:** the discussion tab on `amalia-llm/AMALIA-9B-0626-SFT` (or the current AMALIA model repo) and any AMALIA community Discord/forum.

**Title:**
> A customer-support fine-tuning dataset for AMALIA (pt-PT, 200 rows free)

**Body:**
```
Hi AMALIA community 👋

AMALIA's SFT data is general-purpose — great for conversational pt-PT, but not tuned for customer-support workflows (ticket triage, tone control, escalation, intent/urgency classification). I built LusoSupport-PT specifically to fill that gap: a structured, richly annotated pt-PT instruction dataset designed to fine-tune AMALIA (or any other model) into a support-ready agent.

**What's in it**
- 200 free rows on Hugging Face (full dataset: 10,828 rows)
- 8 domains: e-commerce, SaaS, telecoms, utilities, travel, marketplace, subscriptions, billing
- 8 task types: response generation, email reply, summarisation, intent classification, urgency classification, rewrite, next-action suggestion, FAQ answer
- 18 customer intents × 6 tones × 4 channels
- Alpaca JSONL export, ready to drop into an Unsloth/LLaMA-Factory fine-tune of AMALIA

🔗 Free sample: https://huggingface.co/datasets/ariazevedo/LusoSupport-PT
💻 GitHub (pipeline + docs, including an AMALIA fine-tuning walkthrough): https://github.com/ariazevedopt/pt-ai-instruction-dataset
💼 Full dataset: https://ariazevedo.gumroad.com/l/lusosupport-pt

I'd genuinely like to hear from anyone building support-facing products on AMALIA — is a support-ready fine-tune (or this dataset) actually useful to you, or would you rather fine-tune it yourselves? Happy to answer questions.
```

---

## 2. PT gov-tech / AI dissemination channels (gov.pt, IAedu, consortium networks)

**Where:** LinkedIn posts/comments in groups following the AMALIA rollout (gov.pt digital transformation updates, IAedu, university consortium members' own channels), and direct messages to identified contacts from Stage-0 outreach (issue #58).

**Post:**
```
🇵🇹 AMALIA proved Portugal can build its own sovereign, open-source LLM for European Portuguese. The next question for teams adopting it: how do you specialize a general-purpose model for a specific job — like customer support?

I built LusoSupport-PT to answer that for one concrete domain: a structured pt-PT instruction dataset (10,828 rows, 8 business domains, 8 task types, 18 customer intents) designed to fine-tune AMALIA into a support-ready agent — ticket responses, intent/urgency classification, escalation handling, all in the register a Portuguese support team actually uses.

If your team is building on AMALIA (or evaluating it) for a customer-facing product, I'd like to hear whether this is useful — as a dataset to fine-tune yourselves, or as a ready-made fine-tuned checkpoint.

🤗 Free 200-row sample: https://huggingface.co/datasets/ariazevedo/LusoSupport-PT
💻 GitHub: https://github.com/ariazevedopt/pt-ai-instruction-dataset
💼 Full dataset: https://ariazevedo.gumroad.com/l/lusosupport-pt

#AMALIA #NLP #PortugueseAI #LLM #FineTuning #SoberaniaDigital
```

---

## 3. PT SaaS / telecom / BPO-focused LinkedIn outreach (direct message template)

**Where:** direct 1:1 outreach to contacts identified in the Stage-0 buyer list (issue #58), not a public post.

**Message:**
```
Olá [Nome],

Estou a contactar equipas portuguesas que estão a construir ou avaliar produtos de apoio ao cliente com IA. Não estou a tentar vender-lhe nada — estou a validar se isto é um problema real.

Construí o LusoSupport-PT, um dataset de instruções em português europeu para especializar modelos (incluindo o AMALIA) em apoio ao cliente. A minha pergunta: a vossa equipa está a construir sobre o AMALIA, ou a considerar? Um fine-tune pronto para apoio ao cliente (ou o próprio dataset) seria útil, versus usar o modelo base geral?

10 minutos numa chamada, ou mesmo uma resposta rápida por aqui, já me ajuda imenso.

Obrigado,
[Assinatura]
```

*(English translation for internal reference — do not send the English version, this outreach is pt-PT specific):* "I'm reaching out to Portuguese teams building or evaluating AI customer-support products. I built LusoSupport-PT, a pt-PT instruction dataset to specialize models (including AMALIA) for customer support. Is your team building on AMALIA, or considering it? Would a support-ready fine-tune (or the dataset itself) be useful versus the general base model? Ten minutes on a call, or even a quick reply here, would help a lot."

---

## 4. LinkedIn post — tagged outreach to named Category-1/2/3 leads

**Where:** your personal LinkedIn feed. **Important:** LinkedIn only creates a real `@mention` tag
through its own compose-box autocomplete — type `@` then the company name and select it from the
dropdown while writing the post. A plain link or name pasted from elsewhere will NOT tag the
company; you must add each tag manually inside LinkedIn itself. Post the text below, then go back
and replace each **[TAG: Company]** marker by deleting the placeholder, typing `@`, and selecting
the verified company from LinkedIn's dropdown.

**Verified LinkedIn company pages (fetched and confirmed live as of 2026-08-29):**
- `linkedin.com/company/conectys` — Conectys
- `linkedin.com/company/infraspeak` — Infraspeak
- `linkedin.com/company/codacy` — Codacy
- `linkedin.com/company/talkdesk` — Talkdesk
- `linkedin.com/company/digiton-ai` — Digiton.AI
- `linkedin.com/company/phc-software` — PHC Software (now Cegid PHC)
- `linkedin.com/company/simmpleai` — Simmple.ai

Unverified in this pass (search directly in LinkedIn's tag dropdown before posting — do not guess
a slug): Altice Empresas, APCC, Startup Lisboa, and the rest of `stage0-outreach-leads.md`. Note
Altice's main corporate LinkedIn (`altice-portugal`) is Altice Portugal generally, not the
Empresas B2B unit specifically — verify before tagging.

**Post:**
```
🇵🇹 Depois de validar o produto e ajustar preço e posicionamento, o LusoSupport-PT está pronto
para uma nova fase: quero perceber se isto resolve um problema real para equipas portuguesas de
apoio ao cliente.

Construí um dataset de instruções em português europeu (pt-PT) — 10.828 linhas, 8 domínios, 8
tipos de tarefa, 18 intenções de cliente — pensado para especializar modelos como o AMALIA (o LLM
português open-source) em apoio ao cliente: respostas a tickets, classificação de urgência,
deteção de escalonamento, tudo no registo que uma equipa portuguesa realmente usa.

Se a vossa equipa lida com apoio ao cliente em português e está a explorar IA para esse trabalho,
gostava muito de ouvir se isto seria útil — como dataset para fine-tuning próprio, ou como base
para um modelo já especializado.

🤗 Amostra gratuita (200 linhas): https://huggingface.co/datasets/ariazevedo/LusoSupport-PT
💻 GitHub (pipeline + guia de integração): https://github.com/ariazevedopt/pt-ai-instruction-dataset
💼 Dataset completo: https://ariazevedo.gumroad.com/l/lusosupport-pt

[TAG: Conectys] [TAG: Infraspeak] [TAG: Codacy] [TAG: Talkdesk] [TAG: Digiton.AI]
[TAG: PHC Software] [TAG: Simmple.ai]

#AMALIA #AtendimentoAoCliente #IA #LLM #PortugalTech
```

**Posting checklist for this specific post:**
- [ ] Verify each `[TAG: ...]` company still exists/is active before tagging (re-check via LinkedIn search, not just the handles above — pages can be renamed/merged, e.g. PHC Software → Cegid PHC)
- [ ] Replace every `[TAG: ...]` placeholder with a real `@`-mention using LinkedIn's own autocomplete
- [ ] Remove any placeholder that doesn't resolve to a real, still-active company page rather than leaving unlinked text
- [ ] Cross-check against `docs/launch/stage0-outreach-leads.md` and update each org's Status column to `tagged in post` once live

---

## 5. Reddit post — name-checked leads (no native company-tag feature)

**Where:** r/PORTUGAL (per the buyer-side-community research in `stage0-outreach-leads.md`).
**Important:** Reddit has no mechanism to tag a company or organisation — only `u/username` for
individual Reddit accounts, which none of these organisations are known to have. Don't try to fake
a tag with a markdown link; it won't notify anyone or function as a mention. Instead, name-check
organisations in plain text as social proof / relevant context, and follow r/PORTUGAL's
self-promotion rules (transparent, not spammy, genuinely useful).

**Post:**
```
Title: Built a European Portuguese (pt-PT) customer-support dataset to fine-tune AMALIA — looking for real feedback from PT support/CX teams

Body:

Depois do lançamento do AMALIA, o modelo LLM português open-source, construí o LusoSupport-PT: um
dataset de instruções em pt-PT (10.828 linhas, 8 domínios, 18 intenções de cliente) para
especializar modelos como o AMALIA em apoio ao cliente.

Estou a validar se isto resolve um problema real para equipas na área — contact centers como a
Conectys, SaaS com equipas de suporte como a Infraspeak e a Codacy, ou consultoras de IA como a
Digiton.AI e a Simmple.ai. Se trabalhas em apoio ao cliente em português e já tentaste usar um LLM
para esse trabalho, gostava de ouvir o que funcionou e o que não funcionou.

Não estou a tentar vender nada neste post — só a validar se faz sentido continuar a desenvolver
isto. Amostra gratuita: https://huggingface.co/datasets/ariazevedo/LusoSupport-PT
```

**Posting checklist for this specific post:**
- [ ] Confirm r/PORTUGAL's current self-promotion rules before posting (subreddit rules can change)
- [ ] Only name-check organisations you've genuinely identified as relevant (see Category 1-3 in `stage0-outreach-leads.md`) — do not imply an endorsement or relationship that doesn't exist
- [ ] This counts as the Week-2 "post one problem-framed (not promotional) message in one buyer-side community" checklist item on issue #58 — mark it done once posted

---

## 6. Hugging Face post — name-checked leads (no native mention/tagging feature)

**Where:** `huggingface.co/posts` (new post) or the dataset's own Community tab
(`huggingface.co/datasets/ariazevedo/LusoSupport-PT` → Community). Follow-up to the LinkedIn post
(§4) — same 7 companies, name-checked in plain text.

**Important:** Hugging Face has no `@mention`/tagging feature on Posts or discussions at all —
typing `@CompanyName` is plain text, it does not link to or notify anyone, regardless of whether
the company has an HF account. Checked via the HF API: none of the 7 LinkedIn-tagged companies
(Conectys, Infraspeak, Codacy, Talkdesk, Digiton.AI, PHC Software, Simmple.ai) currently have an HF
org/user account either, so there's no profile to link to even manually. Name-checking in text is
the closest real equivalent on this platform.

**Post:** see the ready-to-paste version in `docs/launch/copy-paste/huggingface-post.txt`.

**Posting checklist for this specific post:**
- [ ] Publish via the HF web UI (no CLI/API support for creating Posts — must be done manually, logged in as the account owner)
- [ ] Decide: standalone HF Post (broader reach) vs. dataset Community tab post (more targeted to people already viewing the dataset) — or both
- [ ] Log as done on issue #57 (promotion) once published

---

## Posting checklist

- [ ] AMALIA HF org/community post published
- [ ] PT gov-tech / dissemination-channel LinkedIn post published
- [x] Tagged LinkedIn post (§4) published with verified @-mentions
- [ ] Reddit r/PORTUGAL name-checked post (§5) published
- [x] Hugging Face name-checked post (§6) published
- [ ] Direct outreach messages sent to the Stage-0 buyer list (issue #58) using the DM template
- [ ] All links (HF, GitHub, Gumroad) verified live before posting
- [ ] Replies tracked in `docs/launch/metrics-tracking.md` (AMALIA outreach replies row)
