# LusoSupport-PT — Dataset Schema (v1.0)

This document defines the **canonical schema** for the LusoSupport-PT dataset.
It is the single source of truth for dataset creation, generation, validation, and publication.

---

## 1. Scope

LusoSupport-PT is a **European Portuguese (pt-PT)** dataset focused on **customer support and business operations**.

The schema supports:
- instruction tuning
- support response generation
- email replies
- summarization
- intent classification
- urgency classification
- workflow / next-action suggestion
- future export to other dataset formats

---

## 2. Canonical row structure

Each dataset entry is a **single JSON object**.

Example (illustrative only):

    {
      "id": "lusosupport_pt_000001",
      "language": "pt",
      "variant": "pt-PT",
      "domain": "ecommerce",
      "subdomain": "returns_refunds",
      "task_type": "response_generation",
      "customer_intent": "refund_request",
      "customer_tone": "frustrated",
      "agent_tone": "empathetic",
      "channel": "email",
      "difficulty": "easy",
      "instruction": "Responde ao cliente em português de Portugal, com tom empático e profissional.",
      "input": "Mensagem do cliente …",
      "output": "Resposta do agente …",
      "metadata": {
        "requires_escalation": false,
        "contains_pii": false,
        "synthetic": true,
        "source_type": "manual_seed"
      }
    }

---

## 3. Required fields

Every row **must contain all** of the following fields:

- id
- language
- variant
- domain
- subdomain
- task_type
- customer_intent
- customer_tone
- agent_tone
- channel
- difficulty
- instruction
- input
- output
- metadata

A row missing any required field is **invalid**.

---

## 4. Field definitions

### 4.1 id

Type: string  
Required: yes  

Unique row identifier.

Format:
- lusosupport_pt_000001

Rules:
- globally unique
- zero‑padded sequence
- stable after publication
- must not encode personal or sensitive information

---

### 4.2 language

Type: string  
Required: yes  

Allowed values (v1):
- pt

For v1, this value is fixed:
- pt

---

### 4.3 variant

Type: string  
Required: yes  

Allowed values (v1):
- pt-PT

Rules:
- all v1 rows must use pt-PT
- do not mix pt-PT and pt-BR
- pt-BR may appear only in a future version or split

---

### 4.4 domain

Type: string  
Required: yes  

High‑level business context.

Allowed values:
- ecommerce
- subscriptions
- saas
- telecom
- utilities
- travel
- marketplace
- billing_accounts

---

### 4.5 subdomain

Type: string  
Required: yes  

Must match the selected domain.

Allowed values:

ecommerce:
- order_status
- delivery_delay
- returns_refunds
- damaged_item
- exchange_request

subscriptions:
- cancel_subscription
- change_plan
- renewal_question
- payment_failure

saas:
- account_access
- password_reset
- feature_question
- bug_report
- billing_question

telecom:
- internet_issue
- mobile_service_issue
- invoice_question
- plan_change
- service_activation

utilities:
- outage_report
- meter_question
- payment_plan
- invoice_clarification

travel:
- booking_change
- booking_cancellation
- refund_status
- checkin_issue

marketplace:
- seller_buyer_dispute
- damaged_item
- order_not_received
- return_request

billing_accounts:
- invoice_request
- duplicate_charge
- payment_confirmation
- account_update
- complaint
- billing_question

Rules:
- lowercase snake_case only
- no ad‑hoc values without schema update

---

### 4.6 task_type

Type: string  
Required: yes  

Allowed values:
- response_generation
- email_reply
- summarization
- intent_classification
- urgency_classification
- rewrite_professional
- next_action_suggestion
- faq_answer

---

### 4.7 customer_intent

Type: string  
Required: yes  

Allowed values (v1):
- refund_request
- return_request
- order_status
- delivery_delay
- damaged_item
- billing_question
- invoice_request
- cancel_subscription
- change_plan
- technical_issue
- password_reset
- account_access
- complaint
- escalation_request
- booking_change
- booking_cancellation
- payment_failure
- duplicate_charge

Rules:
- choose the primary operational intent
- do not invent new intent labels in v1

---

### 4.8 customer_tone

Type: string  
Required: yes  

Allowed values:
- calm
- confused
- frustrated
- urgent
- formal
- informal

---

### 4.9 agent_tone

Type: string  
Required: yes  

Allowed values:
- professional
- empathetic
- concise
- reassuring
- formal

---

### 4.10 channel

Type: string  
Required: yes  

Allowed values:
- email
- chat
- web_form
- phone_transcript

---

### 4.11 difficulty

Type: string  
Required: yes  

Allowed values:
- easy
- medium
- hard

Interpretation:
- easy: single‑step, low ambiguity
- medium: missing info or branching
- hard: complex context or escalation

---

### 4.12 instruction

Type: string  
Required: yes  

Natural‑language instruction for the model.

Rules:
- explicit and task‑aligned
- mention PT‑PT when relevant
- never empty

---

### 4.13 input

Type: string  
Required: yes  

Customer message plus optional context.

Rules:
- sufficient to justify the output
- no real personal data
- may explicitly state missing policy/context

---

### 4.14 output

Type: string  
Required: yes  

Target response.

Rules:
- valid PT‑PT when natural language
- must match task_type
- no invented policies
- no real personal data

---

### 4.15 metadata

Type: object  
Required: yes  

Recommended keys:
- requires_escalation (boolean)
- contains_pii (boolean)
- synthetic (boolean)
- source_type (string)

Example:

    {
      "requires_escalation": false,
      "contains_pii": false,
      "synthetic": true,
      "source_type": "manual_seed"
    }

---

## 5. Validation rules

A row is valid only if:
- all required fields are present
- controlled vocabularies are respected
- domain and subdomain are compatible
- task_type matches the output shape
- PT‑PT language is used consistently
- no real PII is included
- no unsupported policy claims are made

---

## 6. PT‑PT linguistic guidelines (v1)

Preferred:
- fatura
- palavra‑passe
- telemóvel
- encomenda
- reembolso
- devolução

Avoid:
- nota fiscal
- senha
- celular
- Brazilian‑specific support idioms

---

## 7. Versioning

Current schema version: v1.0

Future versions may add fields but should avoid breaking changes.
Any breaking change must be documented explicitly.

---

## 8. Task‑specific output expectations

This section defines **expected output shapes and constraints** for each task type.
Generated or manually written outputs must conform to these expectations.

---

### 8.1 response_generation

Expected output:
- natural‑language customer support reply
- PT‑PT phrasing
- polite, professional, operational tone
- grounded strictly in provided context
- requests missing information when needed

Must NOT:
- invent company policies
- promise refunds, deadlines, or actions not stated in context

---

### 8.2 email_reply

Expected output:
- email‑style structure
- greeting and closing where appropriate
- complete sentences
- professional PT‑PT register

May include:
- courteous formulas (e.g. “Com os melhores cumprimentos”)

---

### 8.3 summarization

Expected output:
- concise summary of the issue
- bullet points or compact structured text
- optional structured object (JSON string)

Must:
- preserve factual content
- highlight missing information
- avoid inference or diagnosis not stated by the customer

---

### 8.4 intent_classification

Expected output:
- deterministic label OR
- small structured object (JSON string)

Example:
    {"intent":"invoice_request","urgency":"low","domain":"billing_accounts"}

Rules:
- consistent formatting across the dataset
- no free‑text explanations unless explicitly requested

---

### 8.5 urgency_classification

Expected output:
- urgency label (low / medium / high)
- optional short rationale

Rules:
- urgency refers to business priority, not emotion alone
- must reflect context impact, deadlines, or service disruption

---

### 8.6 rewrite_professional

Expected output:
- rewritten text in professional PT‑PT
- same semantic meaning
- improved clarity and register

Must NOT:
- add or remove information
- change intent or severity

---

### 8.7 next_action_suggestion

Expected output:
- numbered or bulleted list of steps
- operational and realistic
- suitable for agent workflow assistance

Rules:
- steps must be generic and safe
- avoid policy assumptions

---

### 8.8 faq_answer

Expected output:
- direct answer to the question
- PT‑PT phrasing
- concise but complete

If information is missing:
- explicitly request what is needed
- do not invent conditions

---

## 9. Metadata semantics

The `metadata` object is **mandatory** and designed to support
quality control, filtering, and future extensions.

### Required semantics

- `requires_escalation`
  - true → likely needs escalation or specialist handling
  - false → standard first‑line support handling

- `contains_pii`
  - true → contains personal identifiable information
  - false → default for v1 (almost always false)

- `synthetic`
  - true → fully synthetic or generated example
  - false → manually curated or derived (future use)

- `source_type`
  - manual_seed
  - template_generated
  - hybrid
  - curated

---

## 10. Quality and consistency rules

All dataset rows must satisfy **all** of the following:

### Structural
- valid JSON structure
- all required fields present
- allowed values respected

### Semantic
- domain ↔ subdomain consistency
- task_type ↔ output coherence
- instruction ↔ output alignment

### Linguistic
- PT‑PT terminology
- stable spelling conventions
- natural but controlled phrasing

### Safety
- no real personal data
- no regulated advice
- no hallucinated policy information

---

## 11. Common annotation errors to avoid

- mixing pt‑PT and pt‑BR vocabulary
- assigning multiple intents instead of a single primary one
- vague or underspecified instructions
- outputs that exceed the task scope
- conversational tone leaking into classification outputs
- overusing escalation flags
- inventing company‑specific rules

---

## 12. Minimal row acceptance checklist

Before accepting a row, verify:

- all required fields exist
- id is unique
- variant = pt‑PT
- domain and subdomain are compatible
- task_type is valid
- customer_intent is valid
- instruction is explicit
- input provides sufficient context
- output matches task expectations
- language is PT‑PT
- metadata flags are coherent
- no real PII is present

---

## 13. Export and extensibility guidelines

The canonical schema is intentionally richer than minimal instruction formats.

From this schema, data can later be exported to:
- Alpaca‑style instruction format
- Chat / messages format
- Classification‑only subsets
- Evaluation benchmarks
- RAG‑oriented datasets

### Possible future field additions
(non‑breaking when added):

- resolution_status
- priority
- issue_severity
- language_register
- policy_grounded
- messages (for multi‑turn chat)
- english_translation

---

## 14. Schema versioning policy

Current version: **v1.0**

Rules:
- backward compatibility preferred
- additive changes favoured over breaking changes
- any breaking change must be documented clearly

---

## 15. Locale and terminology appendix (PT-PT)

This section defines **preferred terminology and linguistic conventions** to ensure
consistent **European Portuguese (pt-PT)** usage across the dataset.

### 15.1 Preferred PT-PT terminology (non‑exhaustive)

- fatura  
- palavra‑passe  
- telemóvel  
- encomenda  
- reembolso  
- devolução  
- apoio ao cliente  
- área de cliente  
- adesão ao serviço  
- tarifário  

### 15.2 Terms to avoid in v1 (PT‑BR leaning)

- nota fiscal  
- senha  
- celular  
- pedido (when “encomenda” is more appropriate in retail contexts)  

### 15.3 Neutral phrasing guidance

Some terms are neutral and acceptable in both variants. Prefer neutral wording
when no strong PT‑PT alternative is required, for example:

- conta  
- serviço  
- pagamento  

The objective is **consistency**, not linguistic purism.

---

## 16. Classification output formatting appendix

This section standardises **structured output formats** for classification tasks.

### 16.1 intent_classification

Preferred format: compact JSON string with fixed keys.

Example:

    {"intent":"invoice_request","urgency":"low","domain":"billing_accounts"}

Rules:
- fixed key order is recommended
- do not add extra keys
- values must come from controlled vocabularies
- output must be deterministic

---

### 16.2 urgency_classification

Minimal format:

    {"urgency":"high"}

Extended format with rationale:

    {"urgency":"high","rationale":"Interrupção de serviço com impacto imediato."}

Rules:
- allowed values: low | medium | high
- rationale must be short and factual
- avoid emotive or speculative language

---

## 17. Summarization formatting appendix

Summarization outputs may use **one of two styles**, depending on the instruction.

### 17.1 Bullet summary style

Example:

- Problema: cliente sem acesso à conta.  
- Impacto: necessidade urgente de envio de relatório.  
- Informação em falta: confirmação do e‑mail associado.  

Rules:
- preserve all factual information
- do not infer causes not stated
- keep bullets concise

---

### 17.2 Structured object style

Example:

    {"problema":"Cliente não consegue aceder à conta.","urgencia":"alta","proximo_passo":"Confirmar e‑mail associado."}

Rules:
- keys must be consistent across the dataset
- values must be factual and concise
- format must match the instruction exactly

---

## 18. Email tone and structure appendix

This section standardises **email responses** for the `email_reply` task type.

### 18.1 Recommended structure

1. Greeting  
2. Acknowledgement  
3. Main response content  
4. Request for missing information (if applicable)  
5. Polite closing  

### 18.2 Example skeleton

    Boa tarde,

    Agradecemos o seu contacto.

    [Corpo da resposta]

    Ficamos ao dispor para qualquer esclarecimento adicional.

    Com os melhores cumprimentos,

Rules:
- avoid informal greetings
- do not include personal names or signatures
- maintain a neutral professional register

---

## 19. Escalation flag guidance

The `requires_escalation` flag must be used **conservatively**.

### 19.1 Set to true when:
- service outages with critical impact
- repeated or duplicate billing charges
- explicit complaints or threats of formal complaint
- safety‑related situations
- prolonged unresolved technical failures

### 19.2 Set to false when:
- routine information requests
- first‑contact support cases
- standard procedural questions
- missing‑information scenarios

---

## 20. Safety and privacy appendix

Version 1 follows **strict safety and privacy constraints**.

### 20.1 Prohibited content
- real names combined with contact details
- real account numbers, IDs, IBANs
- realistic addresses linked to individuals
- medical, legal, or tax advice beyond generic process guidance

### 20.2 Acceptable placeholders
- “número da encomenda”
- “referência da fatura”
- generic error messages
- abstract time references (e.g. “ontem”, “na semana passada”)

---

## 21. Dataset evolution notes

This section documents **planned future evolution** without affecting v1.

Possible future extensions include:
- pt‑BR dataset as a separate release
- bilingual PT‑PT ↔ EN alignment
- multi‑turn conversation format
- resolution outcomes
- SLA or priority tagging
- domain‑specific subsets (e.g. telecom‑only)

All future changes must preserve compatibility with the v1 canonical schema
or be released as new versions.

---

## 22. Final notes

This schema is designed to balance:

- PT‑PT linguistic consistency  
- realistic customer‑support scenarios  
- structured metadata for automation  
- reuse and monetisation potential  

All future dataset work must treat this document as **authoritative**.

---

## 23. Annotation workflow guidelines

This section defines **how rows should be created and reviewed** to ensure
consistency across manual and generated data.

### 23.1 Recommended creation order

When creating a new row, follow this sequence:

1. Select `domain` and `subdomain`
2. Select `task_type`
3. Define `customer_intent`
4. Determine `customer_tone` and `agent_tone`
5. Select `channel` and `difficulty`
6. Write a clear `instruction`
7. Write the customer `input`
8. Produce the correct `output`
9. Fill the `metadata` fields

This order helps avoid inconsistencies between intent, tone, and output style.

---

### 23.2 Manual seed examples

Manual seed examples should:

- represent **ideal** dataset quality
- use clear PT‑PT phrasing
- avoid edge cases unless explicitly intended
- serve as reference templates for automated generation
- always set `metadata.source_type = "manual_seed"`

Manual seeds are considered the **gold standard** for the dataset.

---

### 23.3 Template‑generated examples

Template‑generated examples must:

- be derived from approved manual seed patterns
- respect controlled vocabularies
- vary wording enough to avoid near‑duplicates
- be reviewed by validation scripts

Template‑generated rows should set:

- `metadata.synthetic = true`
- `metadata.source_type = "template_generated"`

---

### 23.4 Hybrid examples

Hybrid examples are those that:

- start from a generated template
- receive manual correction or rewriting

Hybrid rows should use:

- `metadata.synthetic = true`
- `metadata.source_type = "hybrid"`

---

## 24. Deduplication and similarity rules

To preserve dataset quality, duplication must be actively controlled.

### 24.1 What counts as a duplicate

A row is considered a duplicate if **any** of the following are true:

- identical `instruction`, `input`, and `output`
- same scenario with only trivial wording changes
- same intent, domain, tone, and structure with near‑identical phrasing

---

### 24.2 Acceptable variation

The following variations are acceptable:

- different domains or subdomains
- different tones or difficulty levels
- different channels (email vs chat)
- different task types applied to the same scenario
- materially different wording or structure

---

### 24.3 Deduplication strategy

Recommended approaches:

- exact string matching
- normalised text comparison (lowercase, punctuation removed)
- similarity scoring (cosine or edit distance)
- manual spot checks on generated batches

---

## 25. Difficulty calibration guidelines

Difficulty must remain **consistent and meaningful**.

### 25.1 Easy

Characteristics:
- clear intent
- minimal ambiguity
- single action or response
- little or no missing information

---

### 25.2 Medium

Characteristics:
- missing information that must be requested
- multiple response steps
- branching logic
- moderate nuance in tone or content

---

### 25.3 Hard

Characteristics:
- escalation likely
- conflicting information
- sensitive complaint handling
- layered context requiring careful phrasing

Difficulty should reflect **cognitive complexity**, not severity alone.

---

## 26. Channel influence appendix

Each channel implies stylistic constraints.

### 26.1 Email

- full sentences
- polite greetings and closings
- slightly more formal register
- lower use of abbreviations

---

### 26.2 Chat

- shorter sentences
- more direct phrasing
- still polite and professional
- minimal greetings

---

### 26.3 Web form

- concise responses
- direct instructions
- neutral tone

---

### 26.4 Phone transcript

- noisier input
- indirect phrasing allowed
- outputs often suited for summarization or classification

---

## 27. Controlled vocabulary stability rules

To preserve dataset stability:

- controlled values must not be renamed in v1
- removing values is discouraged
- new values require schema update
- deprecated values must be documented explicitly

Breaking vocabulary changes must result in **new schema version**.

---

## 28. Inter‑task consistency rules

When the same scenario is used across multiple task types:

- the core facts must remain consistent
- intent must not change
- tone may change only if explicitly justified
- differences must stem from task_type, not inconsistency

---

## 29. Review and acceptance process

A row should be accepted only after:

- automated schema validation passes
- language review confirms PT‑PT usage
- duplication checks pass
- metadata flags are verified
- output is deemed realistic and usable

---

## 30. End‑of‑schema declaration

This document defines the **complete authoritative schema** for LusoSupport‑PT
version 1.0.

Any dataset generation, validation, publication, or extension work must conform
to the rules and constraints specified in this schema.

---

## 31. Dataset splitting and release conventions

This section defines how the dataset should be **split, named, and released**
to ensure clarity and reproducibility.

### 31.1 Dataset granularity

Version 1 of LusoSupport‑PT is expected to be released as:
- a **single canonical dataset**
- optionally partitioned later by task type or domain

At schema level, **no split field is required**.
Splits (e.g. train/validation) are treated as **distribution‑level concerns**.

---

### 31.2 Naming conventions

Recommended dataset naming pattern:

- Repository name: `LusoSupport-PT`
- Dataset name on Hugging Face: `lusosupport-pt`
- Version tag: `v1.0`

File naming examples:
- `lusosupport_pt_v1.jsonl`
- `lusosupport_pt_v1_response_generation.jsonl`
- `lusosupport_pt_v1_intent_classification.jsonl`

---

### 31.3 Versioning rules

- Schema version: `v1.0`
- Dataset version: `v1.0`
- Minor updates without schema changes should increment dataset version only
  (e.g. `v1.1`)
- Schema changes require a schema version increment

Schema and dataset versions must be documented together.

---

## 32. Quality metrics (qualitative)

LusoSupport‑PT prioritises **quality over size**.
The following qualitative metrics define acceptable quality.

### 32.1 Language quality
- correct PT‑PT grammar and vocabulary
- natural phrasing suitable for customer support
- avoidance of literal translation artefacts

### 32.2 Operational realism
- responses resemble real support interactions
- steps and requests are realistic
- no fictional company‑specific guarantees

### 32.3 Consistency
- similar tasks follow similar output conventions
- structured outputs are uniform
- tone usage is coherent across examples

---

## 33. What this dataset is *not*

For clarity and safe usage, LusoSupport‑PT explicitly does **not** aim to be:

- a real customer transcript dataset
- a compliance or policy reference
- a legal or medical advice dataset
- a complete corpus of Portuguese language usage
- representative of any specific real company

---

## 34. Ethical and usage considerations

Although synthetic, the dataset must be used responsibly.

### 34.1 Intended usage
- research and experimentation
- prototyping support assistants
- fine‑tuning or evaluation
- internal tooling and demos

### 34.2 Discouraged usage
- treating outputs as factual company policy
- using the dataset as a legal reference
- deploying outputs without downstream safeguards

---

## 35. Publishing checklist

Before publishing a dataset version, verify:

- schema version is documented
- dataset version is documented
- all rows pass schema validation
- PT‑PT consistency check completed
- duplication checks completed
- documentation is up to date
- examples reflect the released dataset
- license is clearly stated

---

## 36. Long‑term maintenance notes

To keep the dataset useful over time:

- prefer iterative improvements over breaking changes
- document all changes clearly
- keep schema backward‑compatible where possible
- add domains gradually
- avoid uncontrolled vocabulary growth

---

## 37. Final statement

This schema defines the **complete and authoritative specification**
for LusoSupport‑PT version 1.

Any future dataset generation, cleaning, validation, publication, or extension
must conform to this schema or explicitly introduce a new schema version.

---

## 38. Monetisation‑aware design notes

This section documents **design choices made with future monetisation in mind**.
It does **not** impose monetisation constraints, but explains how the schema
supports optional downstream commercial or semi‑commercial use.

### 38.1 Asset reusability

The schema is intentionally:

- metadata‑rich
- domain‑aware
- task‑explicit

This enables:
- extraction of domain‑specific subsets (e.g. telecom‑only)
- extraction of task‑specific subsets (e.g. only intent classification)
- creation of custom bundles for specific use cases

No schema changes are required to support these subsets.

---

### 38.2 Commercial adaptation friendliness

The following features facilitate commercial reuse without modifying the schema:

- clear separation of instruction / input / output
- absence of real personal data
- absence of company‑specific claims
- explicit synthetic labeling

This allows creation of:
- private fine‑tuning datasets
- customised tone or domain variants
- client‑specific extensions layered on top of the base schema

---

### 38.3 Dataset‑as‑signal strategy

In early monetisation phases, the dataset may act as:

- a demonstrator of competence
- a lead generator
- a credibility anchor

Where relevant, future releases may:
- add a `commercial_use_note` in README (outside schema)
- provide contact or sponsorship information
- reference paid extensions or services

The schema itself deliberately stays neutral.

---

## 39. Licensing‑aware schema considerations

The schema is compatible with permissive or restrictive licensing.

### 39.1 License neutrality

Nothing in the schema:
- embeds license assumptions
- enforces usage restrictions
- encodes legal terms

This ensures compatibility with:
- Apache‑2.0
- CC‑BY
- CC‑BY‑NC
- future dual‑licensing strategies

Licensing is handled at repository level, not schema level.

---

## 40. Hugging Face compatibility notes

This section documents how the schema aligns with Hugging Face dataset norms.

### 40.1 Dataset card alignment

Most schema sections map directly to dataset card sections:

- schema description → Dataset Structure
- domains and tasks → Supported Tasks
- language rules → Languages
- safety constraints → Ethical Considerations
- examples → Dataset Examples

---

### 40.2 Dataset loading compatibility

The canonical JSONL schema is compatible with:

- JSONL‑based loading
- pandas ingestion
- direct `datasets` library parsing
- Parquet conversion

No custom dataset script is required for v1.

---

### 40.3 Split strategy on Hugging Face

Recommended approach:
- publish as a single split initially
- add derived splits later if needed
- keep schema unchanged across splits

Splits are a **distribution concern**, not a schema concern.

---

## 41. Schema stability contract (v1)

This section defines what **will not change** in version 1.x.

### 41.1 Guaranteed stable elements

For all v1.x releases:
- required fields remain unchanged
- field meanings remain unchanged
- controlled vocabularies are additive only
- PT‑PT remains the only variant

---

### 41.2 What may change in v1.x

Allowed changes without breaking compatibility:
- additional examples
- additional domains
- additional subdomains
- documentation improvements
- new optional metadata fields

---

### 41.3 Breaking changes

Breaking changes require:
- new schema version (v2.0)
- explicit documentation
- migration notes

---

## 42. Schema governance

Future schema changes should follow a simple governance model.

### 42.1 Change proposal process

Recommended steps:
1. identify need for change
2. document rationale
3. assess backward compatibility
4. update schema document
5. bump schema version if needed

---

### 42.2 Decision principles

Prefer changes that:
- increase clarity
- improve reuse
- preserve simplicity
- avoid over‑specialisation

Avoid changes that:
- fragment the dataset
- introduce niche‑only fields
- encode business logic

---

## 43. Final consolidation notes

This schema deliberately balances:

- expressiveness vs simplicity
- present needs vs future flexibility
- openness vs monetisation readiness
- documentation clarity vs verbosity

It is designed to be **“boring in the right ways”**:
stable, predictable, and reusable.

---

## 44. End of schema

This completes the **LusoSupport‑PT Dataset Schema v1.0**.

All future dataset work should treat this document as **authoritative** unless a
new schema version explicitly supersedes it.

---
## 45. Schema sanity checks for automation

This section defines **machine‑checkable invariants** that validation scripts
should enforce automatically before data is accepted.

### 45.1 Mandatory presence checks
A row must be rejected if any of the following are missing or empty:
- id
- language
- variant
- domain
- subdomain
- task_type
- customer_intent
- customer_tone
- agent_tone
- channel
- difficulty
- instruction
- input
- output
- metadata

---

### 45.2 Controlled vocabulary checks
Validation must confirm that:
- domain ∈ allowed domain list
- subdomain ∈ allowed list for the given domain
- task_type ∈ allowed task types
- customer_intent ∈ allowed intents
- customer_tone ∈ allowed tones
- agent_tone ∈ allowed tones
- channel ∈ allowed channels
- difficulty ∈ allowed difficulty levels

Any out‑of‑vocabulary value is a hard failure.

---

### 45.3 Structural consistency checks
Automated validation should ensure:
- metadata is a JSON object
- metadata.boolean fields are true booleans
- no unexpected top‑level fields exist (unless explicitly allowed)
- output type matches task_type expectations

---

## 46. Instruction–output alignment rules

This section defines **alignment constraints** between instructions and outputs.

### 46.1 Instruction specificity
Every instruction must:
- specify the task clearly
- imply the expected output format
- be compatible with the declared task_type

Example violation:
- task_type = intent_classification
- instruction asks for a free‑form reply

---

### 46.2 Output alignment
The output must:
- satisfy the instruction literally
- avoid extra information not requested
- avoid missing required structure

Mismatch between instruction and output is a validation failure.

---

## 47. Tone coherence rules

### 47.1 Customer vs agent tone separation
- customer_tone describes the **input**
- agent_tone constrains the **output**

The output must reflect agent_tone regardless of customer_tone.

---

### 47.2 Tone priority
If multiple tones could apply:
- agent_tone takes precedence over inferred tone
- clarity and professionalism take precedence over empathy verbosity

---

## 48. Cross‑row consistency guarantees

This section defines guarantees across multiple rows.

### 48.1 Intent reuse
If the same intent appears across rows:
- it must represent the same underlying meaning
- its operational interpretation must remain stable

---

### 48.2 Task reuse
If the same scenario is reused across task types:
- facts must remain identical
- variation must come from task_type, not inconsistency

---

## 49. Language leakage prevention

To preserve PT‑PT integrity, validation should detect:

- Brazilian‑specific spelling
- Brazilian support idioms
- inconsistent agreement patterns

Detected leakage must trigger:
- rejection for generated rows
- manual review for curated rows

---

## 50. Schema‑driven generation checklist

When generating new data programmatically, ensure:

- schema is loaded as the generation source of truth
- controlled vocabularies are injected programmatically
- instruction templates are task‑specific
- output templates respect task constraints
- metadata is computed, not guessed

---

## 51. Debugging and error categorisation

Validation errors should be reported using categories:

- MISSING_FIELD
- INVALID_VALUE
- DOMAIN_MISMATCH
- TASK_OUTPUT_MISMATCH
- LANGUAGE_VARIANT_LEAK
- DUPLICATE_CONTENT
- SAFETY_VIOLATION

This supports easier iteration during generation phases.

---

## 52. Closing guarantees

For LusoSupport‑PT v1.x, the following guarantees hold:

- every published row is schema‑valid
- every published row is PT‑PT consistent
- every published row is safe for public release
- schema structure remains stable within v1.x

---

## 53. Terminal statement

This concludes the **complete schema specification** for
**LusoSupport‑PT Dataset — Version 1.0**.

No further schema parts follow.

---

## 54. Dataset governance and stewardship

This section formalises **how the dataset and schema should be governed**
over time to preserve credibility, usefulness, and trust.

### 54.1 Single maintainer model (initial phase)

For v1.x, the dataset assumes:
- a single primary maintainer
- centralized decision‑making
- conservative acceptance of changes

This reduces fragmentation and inconsistency during early growth.

---

### 54.2 Contributor boundaries

External contributions (if enabled) should be limited to:
- additional examples that fully comply with the schema
- documentation improvements
- typo or language corrections

Contributions **must not**:
- introduce new controlled vocabulary without approval
- alter schema semantics
- add domain‑specific policies or advice

---

## 55. Schema–dataset alignment contract

The schema and the dataset must remain **strictly aligned**.

### 55.1 No implicit fields

- any field used in data must appear in the schema
- any new field requires a schema update
- undocumented fields are not allowed

---

### 55.2 No semantic drift

- fields must retain the same meaning across all rows
- intent values must not drift over time
- tone values must not be reinterpreted

If semantics change, a **new schema version** is required.

---

## 56. Documentation completeness guarantees

For every published dataset version, the following must exist:

- schema document
- examples document
- README describing scope and limits
- license file

Publishing data without matching documentation is not allowed.

---

## 57. Backward compatibility rules

### 57.1 v1.x compatibility guarantees

All v1.x releases guarantee:
- identical required fields
- identical field meanings
- additive-only vocabularies

Tools built for v1.0 must work for v1.1, v1.2, etc.

---

### 57.2 Migration to v2.x

A v2.x release may:
- restructure fields
- rename controlled vocabulary
- change task definitions

A v2.x release **must** include:
- migration notes
- compatibility impact summary

---

## 58. Evaluation and benchmarking guidance

Although not an evaluation dataset per se, LusoSupport‑PT can support evaluation.

### 58.1 Suitable evaluation uses

- intent classification accuracy
- urgency classification consistency
- response style adherence
- summarization completeness
- tone control

---

### 58.2 Unsuitable evaluation uses

- factual QA accuracy
- policy compliance verification
- legal or medical correctness
- conversational realism benchmarking

---

## 59. Dataset misuse prevention notes

This section clarifies **known risks** and how the schema mitigates them.

### 59.1 Potential misuse

- treating outputs as real company policy
- deploying without human oversight
- assuming legal or contractual validity

### 59.2 Mitigations built into the schema

- absence of company identifiers
- no real policy documents
- emphasis on requesting missing info
- explicit synthetic labeling

---

## 60. Long‑term sustainability notes

To keep the dataset sustainable:

- prefer incremental releases
- avoid large uncontrolled expansions
- keep domain growth intentional
- update examples with schema changes
- retire outdated patterns gradually

---

## 61. Archival and deprecation rules

### 61.1 Deprecating fields or values

When deprecating:
- mark as deprecated in documentation
- stop using in new data
- do not remove in v1.x

---

### 61.2 Archiving dataset versions

Older dataset versions:
- should remain accessible
- must not be silently replaced
- must reference the schema version they conform to

---

## 62. Final integrity statement

The LusoSupport‑PT schema defines:

- what the dataset **is**
- what the dataset **is not**
- how the dataset **may evolve**
- how the dataset **must be used**

Any data that does not fully comply with this schema must **not**
be published under the LusoSupport‑PT name.

---

## 63. Absolute end of schema

This concludes **Part 8** and finalises the complete schema specification for:

**LusoSupport‑PT Dataset — Schema Version 1.0**

---
## 64. Schema freeze declaration (v1.x)

This section formally **freezes the schema definition** for all v1.x releases.

### 64.1 Purpose of schema freeze

The schema freeze ensures:
- downstream tooling stability
- reproducible dataset builds
- predictable automation
- clear expectations for users and contributors

Once frozen, the schema serves as a **contract** between the dataset and its users.

---

### 64.2 What is frozen in v1.x

For all v1.x versions, the following are frozen:

- required fields list
- field semantics and meaning
- task_type definitions
- tone definitions
- intent meanings
- PT‑PT language exclusivity
- overall row structure

No backward‑incompatible change is allowed inside v1.x.

---

### 64.3 What is NOT frozen in v1.x

The following may evolve in a backward‑compatible way:

- number of examples
- domain coverage expansion
- subdomain additions (additive only)
- additional metadata fields (optional, additive)
- documentation clarity improvements

---

## 65. Schema conformance assertion

Any dataset claiming to be **LusoSupport‑PT v1.x compliant** must satisfy:

- full conformance to this schema document
- zero schema validation errors
- zero PT‑BR language leakage
- consistent controlled vocabularies
- complete metadata population

Partial conformance is not acceptable.

---

## 66. Tooling expectations

Although tooling is not mandated, the schema assumes:

- programmatic validation is possible
- schema can be represented as JSON Schema / Pydantic / similar
- rows can be filtered deterministically by metadata
- task‑specific subsets can be extracted without transformation

Implementations that violate these assumptions risk dataset corruption.

---

## 67. Recommendation for derived datasets

Derived datasets based on LusoSupport‑PT should:

- reference the parent dataset explicitly
- retain original ids or map them transparently
- avoid rewriting original content
- introduce new fields only in derived layers
- document all deviations from the base schema

Example derived datasets:
- telecom‑only subsets
- classification‑only subsets
- tone‑specific subsets
- multilingual aligned variants

---

## 68. Attribution guidance

When redistributing or adapting data:

- reference the dataset name and version
- reference the schema version
- avoid implying endorsement
- do not attribute real company ownership

Attribution applies to data usage, not individual examples.

---

## 69. Schema checksum recommendation (optional)

For advanced reproducibility, it is recommended to:

- compute a checksum or hash of the schema document
- store it alongside dataset releases
- reference it in release notes

This helps detect undocumented schema drift.

---

## 70. Final closing statement

This document now fully specifies:

- the structure
- the meaning
- the constraints
- the evolution rules

for the **LusoSupport‑PT Dataset Schema v1.0**.

No additional schema parts exist beyond this point.

---

## 71. Absolute termination marker

This concludes **Part 9** and definitively closes the schema specification.

## Additions beyond Part 9 — Final Appendix (All-in-one)

The schema is already **complete and sufficient** for dataset creation, validation,
publication, and long-term reuse.  
However, there are **two optional but valuable additions** that strengthen
professionalism and long-term maintainability **without changing semantics**.

They are included below as a **single final appendix** so you can merge them
directly at the end of the schema file.

---

## 72. Optional changelog and release documentation appendix

While not strictly part of the schema mechanics, documenting **how the dataset
changes over time** prevents ambiguity and increases trust.

### 72.1 Recommended changelog structure

Each dataset release should optionally include a changelog entry that records:

- dataset version
- schema version
- date of release
- number of examples added or changed
- high-level description of changes

Example (documentation-only, not data):

    Version: v1.1
    Schema: v1.0
    Date: YYYY-MM-DD
    Changes:
    - Added 200 new examples (telecom, billing_accounts)
    - Improved wording in 12 manual seed examples
    - No schema changes

This appendix does **not** require a new schema field.

---

### 72.2 Breaking vs non-breaking changes

Non-breaking (allowed in v1.x):
- adding examples
- adding domains or subdomains
- adding optional metadata fields
- documentation updates

Breaking (require v2.0):
- changing field meanings
- renaming required fields
- renaming controlled vocabulary values
- altering task semantics

---

## 73. Derived-dataset declaration appendix (recommended)

To preserve clarity when creating derived datasets, it is recommended to
declare derivation explicitly (outside the data rows).

### 73.1 Derived dataset declaration format

Example declaration (documentation-level only):

    This dataset is derived from:
    - LusoSupport-PT v1.0
    - Schema version v1.0

    Modifications:
    - Filtered to telecom domain only
    - Retained original ids
    - No content rewriting

---

### 73.2 Rules for derived datasets

Derived datasets:
- must not silently modify original rows
- must preserve ids or map them explicitly
- must document all deviations
- must not claim to be the canonical dataset

---

## 74. Minimal compliance statement template

For publication (e.g. Hugging Face, README), it is recommended to include a
short compliance statement like:

    This dataset conforms fully to the LusoSupport-PT Schema v1.0.
    All examples are PT-PT, synthetic, and free of real personal data.

This improves clarity for users evaluating the dataset.

---

## 75. Final confirmation of completeness

With this appendix, the schema now covers:

- structural definition
- semantic constraints
- validation rules
- language policy
- safety boundaries
- task expectations
- automation enforcement
- governance
- versioning
- monetisation-aware design
- long-term maintenance
- derived dataset handling
- release hygiene

No additional schema content is required.

---

## 76. Absolute end marker (final)

This document is now **final**.

It fully defines the **LusoSupport-PT Dataset Schema v1.0**  
and requires no further additions unless a new schema version is introduced.

END OF SCHEMA.
