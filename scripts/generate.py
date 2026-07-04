import json
import random

from config import *
from metadata import (
    derive_customer_tone,
    derive_confidence,
    derive_difficulty,
    derive_escalation,
    derive_subdomain,
    pick_message,
)
from responses import get_output
from scenarios import INTENT_DOMAINS
from templates import build_instruction
from validate import is_valid_row


def generate_output(task_type, intent, domain=None, agent_tone=None):
    return get_output(task_type, intent, domain=domain, agent_tone=agent_tone)


def generate_row(i):
    intent = random.choice(list(INTENT_DOMAINS.keys()))
    customer_tone = derive_customer_tone(intent)
    message = pick_message(intent, customer_tone)

    task = random.choice(TASK_TYPES)
    agent_tone = random.choice(AGENT_TONES)

    allowed_domains = INTENT_DOMAINS.get(intent, DOMAINS)
    domain = random.choice(allowed_domains)
    channel = random.choice(CHANNELS)

    difficulty = derive_difficulty(intent)

    return {
        "id": f"lusosupport_pt_{i:06d}",
        "language": "pt",
        "variant": "pt-PT",
        "domain": domain,
        "subdomain": derive_subdomain(intent, domain),
        "task_type": task,
        "customer_intent": intent,
        "customer_tone": customer_tone,
        "agent_tone": agent_tone,
        "channel": channel,
        "difficulty": difficulty,
        "instruction": build_instruction(task, agent_tone, domain, channel),
        "input": f"Mensagem do cliente: {message}",
        "output": generate_output(task, intent, domain=domain, agent_tone=agent_tone),
        "intent_classification": {
            "intent": intent,
            "confidence": derive_confidence(difficulty),
        },
        "metadata": {
            "requires_escalation": derive_escalation(intent, customer_tone),
            "contains_pii": False,
            "synthetic": True,
            "source_type": "template_generated",
        },
    }


def generate_dataset(n=50):
    return [generate_row(i) for i in range(n)]


def save_jsonl(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic LusoSupport-PT rows.")
    parser.add_argument("--n", type=int, default=50, help="Number of rows to generate")
    parser.add_argument("--out", default="../datasets/interim/generated.jsonl", help="Output path")
    args = parser.parse_args()

    data = generate_dataset(args.n)
    valid = [r for r in data if is_valid_row(r)[0]]
    save_jsonl(valid, args.out)
    print(f"Generated {len(data)} rows, {len(valid)} passed validation → {args.out}")


