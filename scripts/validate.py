def is_valid_row(row):

    if not row.get("id"):
        return False

    if row["language"] != "pt":
        return False

    if row["variant"] != "pt-PT":
        return False

    if len(row.get("output", "")) < 10:
        return False

    banned_words = ["celular", "senha", "nota fiscal"]
    if any(word in row["output"].lower() for word in banned_words):
        return False

    return True
