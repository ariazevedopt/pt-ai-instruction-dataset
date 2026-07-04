import json
import random

from config import *
from responses import get_output
from scenarios import INTENT_MESSAGES
from templates import build_instruction
from validate import is_valid_row


def generate_output(task_type, intent, domain=None):
    return get_output(task_type, intent, domain=domain)


def generate_row(i):
    intent = random.choice(list(INTENT_MESSAGES.keys()))
    message = random.choice(INTENT_MESSAGES[intent])

    task = random.choice(TASK_TYPES)
    customer_tone = random.choice(CUSTOMER_TONES)
    agent_tone = random.choice(AGENT_TONES)

    domain = random.choice(DOMAINS)

    return {
        "id": f"lusosupport_pt_{i:06d}",
        "language": "pt",
        "variant": "pt-PT",
        "domain": domain,
        "subdomain": "placeholder",
        "task_type": task,
        "customer_intent": intent,
        "customer_tone": customer_tone,
        "agent_tone": agent_tone,
        "channel": random.choice(CHANNELS),
        "difficulty": random.choice(DIFFICULTY_LEVELS),
        "instruction": build_instruction(task, agent_tone),
        "input": f"Mensagem do cliente: {message}",
        "output": generate_output(task, intent, domain=domain),
        "metadata": {
            "requires_escalation": False,
            "contains_pii": False,
            "synthetic": True,
            "source_type": "template_generated"
        }
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
    valid = [r for r in data if is_valid_row(r)]
    save_jsonl(valid, args.out)
    print(f"Generated {len(data)} rows, {len(valid)} passed validation → {args.out}")


