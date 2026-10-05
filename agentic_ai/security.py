from __future__ import annotations

import re
from typing import Any, Dict, List


SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{10,}"),
    re.compile(r"OPENAI_API_KEY\s*[:=]\s*['\"][^'\"]+['\"]"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
]

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"\b\+?[0-9]{10,15}\b")


def detect_secrets(value: str) -> List[str]:
    findings: List[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(value or ""):
            findings.append(pattern.pattern)
    return findings


def detect_pii(value: str) -> List[str]:
    findings: List[str] = []
    if EMAIL_PATTERN.search(value or ""):
        findings.append("email")
    if PHONE_PATTERN.search(value or ""):
        findings.append("phone")
    return findings


def contains_prompt_injection(value: str) -> bool:
    lower = (value or "").lower()
    suspicious_tokens = ["ignore previous instructions", "system prompt", "developer message", "override policy", "bypass validation"]
    return any(token in lower for token in suspicious_tokens)


def input_guardrails(input_payload: Dict[str, Any]) -> Dict[str, Any]:
    checks = {
        "secret_detected": False,
        "pii_detected": False,
        "prompt_injection_detected": False,
        "warnings": [],
    }
    raw_text = " ".join([str(value) for value in input_payload.values() if value is not None])
    if detect_secrets(raw_text):
        checks["secret_detected"] = True
        checks["warnings"].append("Secret-like content detected in the request.")
    if detect_pii(raw_text):
        checks["pii_detected"] = True
        checks["warnings"].append("PII-like content detected in the request.")
    if contains_prompt_injection(raw_text):
        checks["prompt_injection_detected"] = True
        checks["warnings"].append("Prompt injection pattern detected.")
    return checks


def output_guardrails(output: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = dict(output)
    if "final_response" in sanitized:
        text = sanitized["final_response"]
        sanitized["final_response"] = text.replace("OPENAI_API_KEY", "[REDACTED]")
    return sanitized
