def route(title):
    return "keep" if "ai" in title.lower() else "review"
