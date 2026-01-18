import re
from typing import Optional, Dict, List

def _clean_number(num_str: str) -> int:
    return int(re.sub(r"[^\d]", "", num_str))

def _extract_numbers(text: str) -> List[int]:
    return [_clean_number(n) for n in re.findall(r"\d[\d.,]*", text)]

def _is_estimation(text: str) -> bool:
    return any(w in text for w in [
        "sekitar", "kira", "kira-kira", "±",
        "kurang lebih", "mungkin", "mgkn",
        "kira2", "kayaknya", "keknya"
    ])

def _likely_money(n: int) -> bool:
    return n >= 1000


def normalize_amount(text: str) -> Dict[str, Optional[str | int]]:
    t = text.lower()

    result = {
        "amount": None,
        "normalized": None,
        "currency": "IDR",
        "confidence": "low",
        "source": None,
    }

    # 🔒 extract once, globally
    nums = [n for n in _extract_numbers(t) if _likely_money(n)]

    # 1. Explicit currency
    m = re.search(r"(rp\.?|idr|\@)\s*(\d[\d.,]*)", t)
    if m:
        amount = _clean_number(m.group(2))
        result.update({
            "amount": amount,
            "normalized": amount,
            "source": "explicit_currency",
            "confidence": "high"
        })
        return result

    # 2. Shorthand
    s = re.search(
        r"(\d+(?:[.,]\d+)?|\d{1,3}(?:[.,]\d{3})+)\s*(k|rb|ribu|jt|juta)",
        t
    )
    if s:
        value = float(s.group(1).replace(",", "."))
        unit = s.group(2)
        mult = {
            "k": 1_000,
            "rb": 1_000,
            "ribu": 1_000,
            "jt": 1_000_000,
            "juta": 1_000_000,
        }[unit]

        amount = int(value * mult)
        result.update({
            "amount": amount,
            "normalized": amount,
            "source": "shorthand",
            "confidence": "high"
        })
        return result

    # 3. Calculation
    if any(x in t for x in ["+", "=", "total", "jadi"]) and len(nums) >= 2:
        total = sum(nums)
        result.update({
            "amount": total,
            "normalized": total,
            "source": "calculation",
            "confidence": "medium"
        })
        return result

    # 4. Estimation
    if _is_estimation(t) and nums:
        amount = max(nums)
        result.update({
            "amount": amount,
            "normalized": amount,
            "source": "estimation",
            "confidence": "low"
        })
        return result

    # 5. Fallback
    if nums:
        amount = max(nums)
        result.update({
            "amount": amount,
            "normalized": amount,
            "source": "fallback",
            "confidence": "medium"
        })
        return result

    return result
