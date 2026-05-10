DOMAINS = [
    "ecommerce", "subscriptions", "saas", "telecom",
    "utilities", "travel", "marketplace", "billing_accounts"
]

CUSTOMER_INTENTS = [
    "refund_request", "return_request", "order_status", "delivery_delay",
    "damaged_item", "billing_question", "invoice_request", "cancel_subscription",
    "change_plan", "technical_issue", "password_reset", "account_access",
    "complaint", "escalation_request", "booking_change", "booking_cancellation",
    "payment_failure", "duplicate_charge"
]

CUSTOMER_TONES = ["calm", "confused", "frustrated", "urgent", "formal", "informal"]
AGENT_TONES = ["professional", "empathetic", "concise", "reassuring", "formal"]
CHANNELS = ["email", "chat", "web_form", "phone_transcript"]
DIFFICULTY = ["easy", "medium", "hard"]

TASK_TYPES = [
    "response_generation", "email_reply", "summarization",
    "intent_classification", "urgency_classification",
    "rewrite_professional", "next_action_suggestion", "faq_answer"
]
