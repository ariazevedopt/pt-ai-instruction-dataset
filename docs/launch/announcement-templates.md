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

## Posting checklist

- [ ] AMALIA HF org/community post published
- [ ] PT gov-tech / dissemination-channel LinkedIn post published
- [ ] Direct outreach messages sent to the Stage-0 buyer list (issue #58) using the DM template
- [ ] All links (HF, GitHub, Gumroad) verified live before posting
- [ ] Replies tracked in `docs/launch/metrics-tracking.md` (AMALIA outreach replies row)
