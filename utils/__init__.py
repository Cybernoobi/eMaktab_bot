def remove_prefix(text, prefix):
    if text.lower().startswith(prefix.lower()):
        return text[len(prefix):]
    return text  # or whatever


def mood_to_emoji(mood: str) -> str:
    return {
        "good": "🟢",
        "average": "🟡",
        "bad": "🔴"
    }.get(mood)
