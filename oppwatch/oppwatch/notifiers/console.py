"""Console notifier: prints digest to standard output."""


def send(text: str) -> bool:
    """Send the text to console. Return True only if delivery succeeded."""
    try:
        print(text)
        return True
    except Exception:
        return False
