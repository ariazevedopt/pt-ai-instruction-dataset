# LusoSupport-PT — Integration Guide

This guide covers each integration pattern in full detail: prerequisites, complete working code, configuration files, expected outputs, and common pitfalls to avoid.

---

## Table of Contents

1. [Loading the dataset](#1-loading-the-dataset)
2. [Fine-tuning with Unsloth (LLaMA / Mistral)](#2-fine-tuning-with-unsloth-llama--mistral)
3. [Fine-tuning with LLaMA-Factory](#3-fine-tuning-with-llama-factory)
4. [OpenAI fine-tuning (gpt-4o-mini)](#4-openai-fine-tuning-gpt-4o-mini)
5. [Few-shot prompting (no training)](#5-few-shot-prompting-no-training)
6. [Intent classification pipeline](#6-intent-classification-pipeline)
7. [RAG with LangChain + FAISS](#7-rag-with-langchain--faiss)
8. [RAG with ChromaDB (persistent)](#8-rag-with-chromadb-persistent)
9. [Evaluation and benchmarking](#9-evaluation-and-benchmarking)
10. [Pushing to Hugging Face Hub](#10-pushing-to-hugging-face-hub)

---

## 1. Loading the Dataset

### Prerequisites

```bash
pip install datasets
```

### Basic loading

```python
from datasets import load_dataset

ds = load_dataset(
    "json",
    data_files="datasets/processed/lusosupport_pt_v1.jsonl",
    split="train",
)

print(ds)
# Dataset({features: ['id', 'language', 'variant', 'domain', 'subdomain',
#   'task_type', 'customer_intent', 'customer_tone', 'agent_tone',
#   'channel', 'difficulty', 'instruction', 'input', 'output', 'metadata'],
#   num_rows: 1275})
```

### Train / validation split

Most trainers need a validation set. Split 90/10:

```python
split = ds.train_test_split(test_size=0.1, seed=42)
train_ds = split["train"]   # ~1147 rows
eval_ds  = split["test"]    # ~128 rows

print(f"Train: {len(train_ds)}  Eval: {len(eval_ds)}")
```

### Filtering by task or domain

```python
# Only response generation rows
response_ds = ds.filter(lambda r: r["task_type"] == "response_generation")

# Only ecommerce rows
ecommerce_ds = ds.filter(lambda r: r["domain"] == "ecommerce")

# Hard rows only (stress test / eval set)
hard_ds = ds.filter(lambda r: r["difficulty"] == "hard")

# Classification rows (intent + urgency)
clf_ds = ds.filter(lambda r: r["task_type"] in ("intent_classification", "urgency_classification"))

# Rows requiring escalation (for escalation detection)
escalation_ds = ds.filter(lambda r: r["metadata"]["requires_escalation"])
```

### Accessing fields

```python
row = ds[0]
print(row["instruction"])   # system prompt in PT-PT
print(row["input"])         # customer message
print(row["output"])        # expected agent response
print(row["domain"])        # e.g. "ecommerce"
print(row["task_type"])     # e.g. "response_generation"
print(row["customer_intent"])  # e.g. "refund_request"
```

---

## 2. Fine-tuning with Unsloth (LLaMA / Mistral)

Unsloth is the fastest way to fine-tune LLaMA and Mistral models locally on consumer GPUs. It uses 4-bit quantisation (QLoRA) and achieves 2–5× faster training than vanilla Hugging Face.

### Prerequisites

```bash
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install --no-deps "trl<0.9.0" peft accelerate bitsandbytes datasets
```

### Full training script

```python
# train_unsloth.py
import json
from pathlib import Path
from datasets import Dataset
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments

# ── 1. Load and format the dataset ──────────────────────────────────────────

ALPACA_PROMPT = """Abaixo está uma instrução que descreve uma tarefa de suporte ao cliente em português de Portugal, acompanhada de uma mensagem do cliente. Escreve uma resposta adequada.

### Instrução:
{}

### Mensagem do cliente:
{}

### Resposta:
{}"""

def load_rows(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]

rows = load_rows("datasets/processed/lusosupport_pt_v1.jsonl")

# Format each row into the Alpaca prompt template
EOS = "<|end_of_text|>"

formatted = [
    {"text": ALPACA_PROMPT.format(r["instruction"], r["input"], r["output"]) + EOS}
    for r in rows
]

dataset = Dataset.from_list(formatted)
split = dataset.train_test_split(test_size=0.1, seed=42)

# ── 2. Load the base model ───────────────────────────────────────────────────

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Meta-Llama-3.1-8B",   # or "unsloth/mistral-7b-v0.3"
    max_seq_length=2048,
    dtype=None,          # auto-detect float16 / bfloat16
    load_in_4bit=True,   # QLoRA — fits on a 16GB GPU
)

# ── 3. Add LoRA adapters ─────────────────────────────────────────────────────

model = FastLanguageModel.get_peft_model(
    model,
    r=16,                # LoRA rank — higher = more capacity, more VRAM
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=42,
)

# ── 4. Train ─────────────────────────────────────────────────────────────────

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=split["train"],
    eval_dataset=split["test"],
    dataset_text_field="text",
    max_seq_length=2048,
    dataset_num_proc=2,
    args=TrainingArguments(
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        num_train_epochs=3,
        learning_rate=2e-4,
        fp16=True,
        logging_steps=10,
        eval_steps=50,
        evaluation_strategy="steps",
        save_strategy="epoch",
        output_dir="outputs/lusosupport-llama",
        report_to="none",
    ),
)

trainer.train()

# ── 5. Save ──────────────────────────────────────────────────────────────────

model.save_pretrained("outputs/lusosupport-llama-final")
tokenizer.save_pretrained("outputs/lusosupport-llama-final")
print("Model saved to outputs/lusosupport-llama-final")
```

### Run inference

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "outputs/lusosupport-llama-final",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

ALPACA_PROMPT = """Abaixo está uma instrução que descreve uma tarefa de suporte ao cliente em português de Portugal, acompanhada de uma mensagem do cliente. Escreve uma resposta adequada.

### Instrução:
{}

### Mensagem do cliente:
{}

### Resposta:
"""

inputs = tokenizer(
    [ALPACA_PROMPT.format(
        "Responde ao cliente em português de Portugal, com tom profissional.",
        "Mensagem do cliente: A minha fatura apresenta um valor incorrecto.",
    )],
    return_tensors="pt",
).to("cuda")

outputs = model.generate(**inputs, max_new_tokens=256, use_cache=True)
print(tokenizer.batch_decode(outputs)[0])
```

---

## 3. Fine-tuning with LLaMA-Factory

LLaMA-Factory is a multi-model, multi-method training framework with a web UI. It supports LLaMA, Mistral, Qwen, Gemma, and many more.

### Prerequisites

```bash
git clone --depth 1 https://github.com/hiyouga/LLaMA-Factory.git
cd LLaMA-Factory
pip install -e ".[torch,metrics]"
```

### Export to Alpaca format

```bash
# From the pt-ai-instruction-dataset root:
make export
# Writes: datasets/exports/lusosupport_pt_v1_alpaca.jsonl
```

### Register the dataset

Copy the Alpaca file into LLaMA-Factory's data directory and register it:

```bash
cp datasets/exports/lusosupport_pt_v1_alpaca.jsonl /path/to/LLaMA-Factory/data/

# Add this block to /path/to/LLaMA-Factory/data/dataset_info.json:
```

```json
"lusosupport_pt": {
  "file_name": "lusosupport_pt_v1_alpaca.jsonl",
  "formatting": "alpaca",
  "columns": {
    "prompt": "instruction",
    "query": "input",
    "response": "output"
  }
}
```

### Training config (`examples/train_lora/llama3_lora_sft.yaml`)

```yaml
### Model
model_name_or_path: meta-llama/Meta-Llama-3.1-8B-Instruct
trust_remote_code: true

### Method
stage: sft
do_train: true
finetuning_type: lora
lora_target: all
lora_rank: 16
lora_alpha: 32

### Dataset
dataset: lusosupport_pt
template: llama3
cutoff_len: 2048
val_size: 0.1
overwrite_cache: true
preprocessing_num_workers: 4

### Output
output_dir: saves/llama3-lusosupport
logging_steps: 10
save_steps: 500
plot_loss: true
overwrite_output_dir: true

### Train
per_device_train_batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 1.0e-4
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
ddp_timeout: 180000000

### Eval
val_size: 0.1
per_device_eval_batch_size: 2
eval_strategy: steps
eval_steps: 500
```

Run training:

```bash
cd LLaMA-Factory
llamafactory-cli train examples/train_lora/llama3_lora_sft.yaml
```

---

## 4. OpenAI Fine-tuning (gpt-4o-mini)

### Prerequisites

```bash
pip install openai
export OPENAI_API_KEY="sk-..."
```

### Convert to chat format

```python
# prepare_openai_finetune.py
import json
from pathlib import Path

def to_chat(row):
    return {
        "messages": [
            {"role": "system",    "content": row["instruction"]},
            {"role": "user",      "content": row["input"]},
            {"role": "assistant", "content": row["output"]},
        ]
    }

rows = [
    json.loads(l)
    for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines()
    if l.strip()
]

# Use response_generation rows — these translate best to chat fine-tuning
chat_rows = [r for r in rows if r["task_type"] == "response_generation"]

# 90/10 train/val split
split = int(len(chat_rows) * 0.9)
train_rows = chat_rows[:split]
val_rows   = chat_rows[split:]

for fname, data in [("oai_train.jsonl", train_rows), ("oai_val.jsonl", val_rows)]:
    with open(fname, "w", encoding="utf-8") as f:
        for row in data:
            f.write(json.dumps(to_chat(row), ensure_ascii=False) + "\n")

print(f"Train: {len(train_rows)}  Val: {len(val_rows)}")
```

### Validate the format before uploading

```python
# OpenAI's format checker (adapted)
import json, tiktoken

enc = tiktoken.get_encoding("cl100k_base")

def count_tokens(messages):
    return sum(len(enc.encode(m["content"])) for m in messages)

with open("oai_train.jsonl") as f:
    examples = [json.loads(l) for l in f]

token_counts = [count_tokens(e["messages"]) for e in examples]
print(f"Examples: {len(examples)}")
print(f"Avg tokens/example: {sum(token_counts)/len(token_counts):.0f}")
print(f"Max tokens: {max(token_counts)}")
# OpenAI limit is 65536 tokens per example; typical rows are ~200-400 tokens
```

### Upload and start fine-tuning

```python
from openai import OpenAI

client = OpenAI()

# Upload training file
train_file = client.files.create(
    file=open("oai_train.jsonl", "rb"),
    purpose="fine-tune",
)
val_file = client.files.create(
    file=open("oai_val.jsonl", "rb"),
    purpose="fine-tune",
)

print(f"Training file ID:   {train_file.id}")
print(f"Validation file ID: {val_file.id}")

# Start fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    validation_file=val_file.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3,
        "batch_size": "auto",
        "learning_rate_multiplier": "auto",
    },
    suffix="lusosupport-pt",
)

print(f"Fine-tuning job ID: {job.id}")
print(f"Status: {job.status}")
```

### Monitor the job

```python
import time

while True:
    job = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {job.status}  |  Trained tokens: {job.trained_tokens}")
    if job.status in ("succeeded", "failed", "cancelled"):
        break
    time.sleep(30)

if job.status == "succeeded":
    print(f"Fine-tuned model: {job.fine_tuned_model}")
```

### Use the fine-tuned model

```python
fine_tuned_model = "ft:gpt-4o-mini-2024-07-18:lusosupport-pt:..."  # from job result

response = client.chat.completions.create(
    model=fine_tuned_model,
    messages=[
        {"role": "system",  "content": "Responde ao cliente em português de Portugal, com tom profissional e empático."},
        {"role": "user",    "content": "Mensagem do cliente: Recebi a encomenda errada e preciso de ajuda."},
    ],
    temperature=0.3,
    max_tokens=300,
)

print(response.choices[0].message.content)
```

---

## 5. Few-shot Prompting (No Training)

Use the dataset as a prompt library. No GPU, no training cost — just pick good examples and inject them.

### Build a few-shot prompt dynamically

```python
import json, random
from pathlib import Path

rows = [
    json.loads(l)
    for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines()
    if l.strip()
]

def build_few_shot_prompt(task_type, domain, customer_message, n_shots=3):
    """Build a system prompt with n examples from the dataset."""
    pool = [
        r for r in rows
        if r["task_type"] == task_type and r["domain"] == domain
    ]
    if not pool:
        pool = [r for r in rows if r["task_type"] == task_type]

    examples = random.sample(pool, min(n_shots, len(pool)))

    shots = "\n\n".join(
        f"Mensagem do cliente: {e['input'].replace('Mensagem do cliente: ', '')}\n"
        f"Resposta: {e['output']}"
        for e in examples
    )

    system_prompt = (
        "És um assistente de suporte ao cliente que responde em português de Portugal.\n\n"
        "Exemplos de respostas correctas:\n\n"
        f"{shots}\n\n"
        "Agora responde à seguinte mensagem seguindo o mesmo estilo e idioma:"
    )
    return system_prompt

# Use with any OpenAI-compatible API
from openai import OpenAI

client = OpenAI()

system = build_few_shot_prompt(
    task_type="response_generation",
    domain="ecommerce",
    customer_message="A minha encomenda ainda não chegou e já passaram 10 dias.",
    n_shots=3,
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system},
        {"role": "user",   "content": "A minha encomenda ainda não chegou e já passaram 10 dias."},
    ],
    temperature=0.3,
)

print(response.choices[0].message.content)
```

### Pick examples by similarity (semantic few-shot)

For better shot selection, embed both the pool and the query and pick the closest:

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

def embed(texts):
    response = client.embeddings.create(model="text-embedding-3-small", input=texts)
    return np.array([e.embedding for e in response.data])

# Pre-embed the pool (do this once, cache the result)
pool = [r for r in rows if r["task_type"] == "response_generation"]
pool_inputs = [r["input"] for r in pool]
pool_embeddings = embed(pool_inputs)   # shape: (N, 1536)

def get_similar_shots(query, n=3):
    q_emb = embed([query])             # shape: (1, 1536)
    scores = (pool_embeddings @ q_emb.T).squeeze()
    top_idx = scores.argsort()[-n:][::-1]
    return [pool[i] for i in top_idx]

shots = get_similar_shots("Não recebi o e-mail de recuperação de palavra-passe.")
for s in shots:
    print(s["output"][:80])
```

---

## 6. Intent Classification Pipeline

Use the `intent_classification` rows to build an automatic triage system that reads incoming customer messages and routes them.

### Option A — Prompt-based (zero training)

```python
import json
from openai import OpenAI
from pathlib import Path

client = OpenAI()

INTENTS = [
    "refund_request", "return_request", "order_status", "delivery_delay",
    "damaged_item", "billing_question", "invoice_request", "cancel_subscription",
    "change_plan", "technical_issue", "password_reset", "account_access",
    "complaint", "escalation_request", "booking_change", "booking_cancellation",
    "payment_failure", "duplicate_charge",
]

def classify_intent(customer_message):
    system = (
        "Classifica a seguinte mensagem de um cliente de acordo com a sua intenção principal.\n"
        f"Intents possíveis: {', '.join(INTENTS)}.\n"
        "Responde apenas com um objecto JSON com as chaves: intent, urgency (low/medium/high), confidence (0.0–1.0)."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": customer_message},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)

result = classify_intent("Fui cobrado duas vezes pelo mesmo serviço este mês.")
print(result)
# {"intent": "duplicate_charge", "urgency": "high", "confidence": 0.95}
```

### Option B — Fine-tuned classifier (lower cost at scale)

Train a small encoder model (e.g., `neuralmind/bert-base-portuguese-cased`) on the classification rows:

```python
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer,
)
import torch, json
from pathlib import Path

# Load classification rows
rows = [json.loads(l) for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines() if l.strip()]
clf_rows = [r for r in rows if r["task_type"] == "intent_classification"]

# Extract intent from the JSON output field
import re

INTENTS = sorted({
    json.loads(r["output"])["intent"]
    for r in clf_rows
    if "intent" in json.loads(r["output"])
})
label2id = {intent: i for i, intent in enumerate(INTENTS)}
id2label = {i: intent for intent, i in label2id.items()}

data = [
    {
        "text":  r["input"].replace("Mensagem do cliente: ", ""),
        "label": label2id[json.loads(r["output"])["intent"]],
    }
    for r in clf_rows
    if "intent" in json.loads(r["output"])
]

ds = Dataset.from_list(data).train_test_split(test_size=0.15, seed=42)

MODEL = "neuralmind/bert-base-portuguese-cased"
tokenizer = AutoTokenizer.from_pretrained(MODEL)

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128)

ds = ds.map(tokenize, batched=True)
ds = ds.rename_column("label", "labels")
ds.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL,
    num_labels=len(INTENTS),
    id2label=id2label,
    label2id=label2id,
)

trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="outputs/intent-classifier",
        num_train_epochs=5,
        per_device_train_batch_size=16,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    ),
    train_dataset=ds["train"],
    eval_dataset=ds["test"],
)

trainer.train()
model.save_pretrained("outputs/intent-classifier-final")
tokenizer.save_pretrained("outputs/intent-classifier-final")
```

### Inference with the fine-tuned classifier

```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="outputs/intent-classifier-final",
    tokenizer="outputs/intent-classifier-final",
)

result = classifier("Não consigo aceder à minha conta desde ontem de manhã.")
print(result)
# [{'label': 'account_access', 'score': 0.94}]
```

---

## 7. RAG with LangChain + FAISS

Build a retrieval-augmented support assistant that grounds its answers in known-good PT-PT responses.

### Prerequisites

```bash
pip install langchain langchain-community langchain-openai faiss-cpu
```

### Full RAG pipeline

```python
# rag_support.py
import json
from pathlib import Path
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ── 1. Load and index the dataset ────────────────────────────────────────────

rows = [
    json.loads(l)
    for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines()
    if l.strip()
]

# Index response_generation rows as retrieval documents
# page_content = the customer message (what we search against)
# metadata    = the ground-truth response + all labels
docs = [
    Document(
        page_content=row["input"].replace("Mensagem do cliente: ", ""),
        metadata={
            "output":   row["output"],
            "intent":   row["customer_intent"],
            "domain":   row["domain"],
            "task":     row["task_type"],
            "tone":     row["agent_tone"],
            "channel":  row["channel"],
        },
    )
    for row in rows
    if row["task_type"] == "response_generation"
]

print(f"Indexing {len(docs)} documents...")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(docs, embeddings)
vectorstore.save_local("faiss_index/lusosupport")
print("Index saved.")

# ── 2. Define the RAG prompt ──────────────────────────────────────────────────

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""És um assistente de suporte ao cliente que responde em português de Portugal.

Abaixo encontram-se exemplos de como responder a situações semelhantes:

{context}

---

Com base nos exemplos acima, responde à seguinte mensagem do cliente de forma profissional e em PT-PT:

{question}

Resposta:""",
)

# ── 3. Build the chain ────────────────────────────────────────────────────────

vectorstore = FAISS.load_local(
    "faiss_index/lusosupport",
    OpenAIEmbeddings(model="text-embedding-3-small"),
    allow_dangerous_deserialization=True,
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},
)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True,
)

# ── 4. Query ──────────────────────────────────────────────────────────────────

result = qa_chain.invoke("A minha encomenda chegou com o produto partido e quero um reembolso.")

print("=== Response ===")
print(result["result"])

print("\n=== Retrieved examples (top 4) ===")
for doc in result["source_documents"]:
    print(f"  Intent: {doc.metadata['intent']}  Domain: {doc.metadata['domain']}")
    print(f"  Stored response: {doc.metadata['output'][:100]}...")
    print()
```

### Domain-filtered retrieval

When you know the customer's domain (e.g., from URL or account type), filter retrieval to that domain:

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 4,
        "filter": {"domain": "ecommerce"},   # only retrieve ecommerce examples
    },
)
```

---

## 8. RAG with ChromaDB (Persistent)

ChromaDB stores the index on disk — useful for production deployments where you don't want to rebuild the index on every startup.

### Prerequisites

```bash
pip install chromadb langchain-chroma langchain-openai
```

### Build the persistent index

```python
import json
from pathlib import Path
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

rows = [
    json.loads(l)
    for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines()
    if l.strip()
]

docs = [
    Document(
        page_content=row["input"].replace("Mensagem do cliente: ", ""),
        metadata={
            "output":  row["output"],
            "intent":  row["customer_intent"],
            "domain":  row["domain"],
            "task":    row["task_type"],
        },
    )
    for row in rows
    if row["task_type"] == "response_generation"
]

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Persist to disk — only needs to run once
vectorstore = Chroma.from_documents(
    docs,
    embeddings,
    persist_directory="chroma_db/lusosupport",
    collection_name="support_responses",
)
print(f"Indexed {len(docs)} documents.")
```

### Query the persisted index

```python
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma(
    persist_directory="chroma_db/lusosupport",
    embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="support_responses",
)

results = vectorstore.similarity_search_with_score(
    "Fui cobrado duas vezes este mês.",
    k=3,
)

for doc, score in results:
    print(f"Score: {score:.3f}  Intent: {doc.metadata['intent']}")
    print(f"Response: {doc.metadata['output'][:120]}...")
    print()
```

---

## 9. Evaluation and Benchmarking

Use the dataset as a reference set to measure how well a model handles PT-PT support.

### Prerequisites

```bash
pip install evaluate rouge-score bert-score
```

### ROUGE score (text overlap)

```python
import json, evaluate
from pathlib import Path

rouge = evaluate.load("rouge")

rows = [json.loads(l) for l in Path("datasets/processed/lusosupport_pt_v1.jsonl").read_text().splitlines() if l.strip()]
eval_rows = [r for r in rows if r["task_type"] == "response_generation"][:100]

# Replace with your model's predictions
from openai import OpenAI
client = OpenAI()

predictions = []
references  = []

for row in eval_rows:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": row["instruction"]},
            {"role": "user",   "content": row["input"]},
        ],
        temperature=0,
        max_tokens=300,
    )
    predictions.append(resp.choices[0].message.content)
    references.append(row["output"])

scores = rouge.compute(predictions=predictions, references=references)
print(f"ROUGE-1: {scores['rouge1']:.3f}")
print(f"ROUGE-2: {scores['rouge2']:.3f}")
print(f"ROUGE-L: {scores['rougeL']:.3f}")
```

### BERTScore (semantic similarity)

```python
import evaluate

bertscore = evaluate.load("bertscore")

results = bertscore.compute(
    predictions=predictions,
    references=references,
    lang="pt",               # uses multilingual BERT
)

import numpy as np
print(f"BERTScore F1 (avg): {np.mean(results['f1']):.3f}")
```

### PT-PT compliance check (custom)

Check that model outputs don't contain pt-BR vocabulary:

```python
PTBR_BANNED = ["senha", "celular", "nota fiscal", "boleto", "cpf", "você", "voce"]

def ptpt_compliance_rate(predictions):
    violations = sum(
        1 for pred in predictions
        if any(term in pred.lower() for term in PTBR_BANNED)
    )
    return 1 - violations / len(predictions)

print(f"PT-PT compliance: {ptpt_compliance_rate(predictions):.1%}")
```

---

## 10. Pushing to Hugging Face Hub

Share your fine-tuned model or the dataset itself on the Hugging Face Hub.

### Push the dataset

```python
from datasets import load_dataset, DatasetDict

ds = load_dataset(
    "json",
    data_files="datasets/processed/lusosupport_pt_v1.jsonl",
    split="train",
)

split = ds.train_test_split(test_size=0.1, seed=42)
dataset_dict = DatasetDict({"train": split["train"], "validation": split["test"]})

dataset_dict.push_to_hub(
    "your-username/lusosupport-pt",
    private=False,
    token="hf_...",
)
```

### Push a fine-tuned model

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("outputs/lusosupport-llama-final")
tokenizer = AutoTokenizer.from_pretrained("outputs/lusosupport-llama-final")

model.push_to_hub("your-username/llama3-lusosupport-pt", token="hf_...")
tokenizer.push_to_hub("your-username/llama3-lusosupport-pt", token="hf_...")
```

---

## Quick Reference

| Goal | Section | Key library |
|---|---|---|
| Explore and filter data | §1 | `datasets` |
| Fine-tune open model (fast, local GPU) | §2 | `unsloth` |
| Fine-tune open model (multi-model, config-driven) | §3 | `llama-factory` |
| Fine-tune GPT-4o-mini (managed, no GPU) | §4 | `openai` |
| Improve any LLM with examples, no training | §5 | `openai` |
| Build a triage / routing classifier | §6 | `transformers` |
| RAG grounded support assistant (FAISS) | §7 | `langchain`, `faiss` |
| RAG with persistent disk index | §8 | `langchain`, `chromadb` |
| Measure model quality against ground truth | §9 | `evaluate`, `bert-score` |
| Share model or dataset publicly | §10 | `datasets`, `transformers` |
