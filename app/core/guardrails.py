import re

# List of compiled regex patterns to look for.
_INJECTION_PATTERNS = [
    re.compile(r"ignore previous instructions", re.IGNORECASE),
    re.compile(r"\[system\]", re.IGNORECASE),
    re.compile(r"you are now (a|an)", re.IGNORECASE),
]


def check_for_injection(text: str) -> None:
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            raise ValueError("400 Bad Request: The provided prompt violates security policies.")