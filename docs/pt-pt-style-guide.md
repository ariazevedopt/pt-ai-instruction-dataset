# European Portuguese (pt-PT) Style Guide

This document defines the vocabulary policy for LusoSupport-PT, resolving
[issue #55](https://github.com/ariazevedopt/pt-ai-instruction-dataset/issues/55).

## Policy summary

- **Agent `output` fields must always use pt-PT vocabulary.** No exceptions.
  `scripts/validate.py` enforces this on every generated row (Rule 19).
- **Customer `input` fields may contain pt-BR-influenced vocabulary.** This is
  intentional, not a bug. Real European customers are exposed to Brazilian
  media, apps, and content daily, and naturally code-switch some everyday
  words. A support agent (human or AI) needs to *understand* these terms even
  though it should never *use* them. The dataset ships a small, deliberate
  set of example rows demonstrating exactly this: customer says "celular",
  agent replies about the "telemóvel".

## Canonical pt-BR → pt-PT term map (enforced on output)

| pt-BR term    | pt-PT term      | Notes                                   |
|---------------|------------------|------------------------------------------|
| celular       | telemóvel        | mobile phone                            |
| senha         | palavra-passe    | password                                |
| nota fiscal   | fatura           | invoice / receipt                       |
| contato       | contacto         | contact (pt-PT keeps the silent 'c')    |

These four terms are enforced by `_BANNED_WORDS` in `scripts/validate.py` and
must never appear in an `output` field.

## Terms previously (incorrectly) flagged as pt-BR

Two terms were removed from the banned list because they are standard
European Portuguese, not pt-BR exclusives:

- **assinatura** — used in pt-PT for both "signature" and "subscription"
  (e.g. "assinatura de um serviço"). Not pt-BR-exclusive.
- **código de rastreio** — the standard pt-PT term for "tracking code," used
  by CTT (the Portuguese national postal service) itself. The pt-BR
  equivalent is "rastreamento," not "rastreio."

Both terms may appear freely in either `input` or `output` fields.

## Why input is not filtered

Filtering pt-BR-influenced vocabulary out of customer `input` would produce a
dataset where every customer speaks in unnaturally "pure" pt-PT — unrealistic
for a real support inbox, and a missed opportunity to train a model that
correctly *recognizes* these terms as synonyms while still responding in
correct pt-PT. `scripts/scenarios.py` includes a handful of intentional
code-switch example messages (see `CODE_SWITCH_EXCEPTIONS` in
`tests/test_scenarios_tones.py`) covering all four banned-output terms from
the customer side.

## Adding new banned/allowed terms

1. Confirm the term is genuinely pt-BR-exclusive (not used in Portugal) —
   when in doubt, check a pt-PT dictionary or a Portuguese institutional
   source (e.g. CTT, Autoridade Tributária, government sites) rather than
   general usage.
2. Add it to `_BANNED_WORDS` in `scripts/validate.py` with a pt-PT equivalent
   comment.
3. Update this document's term map table.
4. Optionally add a customer-input example using the term to
   `scripts/scenarios.py`, plus a matching entry in `CODE_SWITCH_EXCEPTIONS`
   in `tests/test_scenarios_tones.py`.
