def route(note):
    text = note.lower()
    return "keep" if "agent" in text or "ai" in text else "review"
