import re

# =========================
# Amount detection
# =========================

AMOUNT_REGEX = re.compile(
    r"""
    (                           # group angka + skala
        \d+(?:[.,]\d+)*         # 7500 | 7.500 | 1.5
        \s*                     # optional space
        (k|rb|ribu|jt|juta)\b   # shorthand rupiah
    )
    |
    (                           # angka langsung (anggap rupiah)
        \d{1,3}(?:[.,]\d{3})+   # 7.500 | 1,000,000
        |
        \d{4,}                  # 7500
    )
    """,
    re.VERBOSE
)

def has_amount(text: str) -> bool:
    return bool(AMOUNT_REGEX.search(text.lower()))


# =========================
# Edge flagger
# =========================

def edge_flagger(text: str):
    t = text.lower()
    flags = set()

    # --- PRIMARY (hard gate) ---
    if not has_amount(t):
        flags.add("missing_amount")
        return "rejected", flags

    # --- SECONDARY (contextual ambiguity) ---

    # multiple categories / items
    if "atau" in t or "," in t:
        flags.add("multiple_categories")

    # estimation language
    if any(x in t for x in ["sekitar", "kira", "±", "kurang lebih"]):
        flags.add("estimation")

    # operators (plus is allowed)
    if any(x in t for x in ["-", "x", "/"]):
        flags.add("non_plus_operator")

    # foreign currency
    if any(x in t for x in ["usd", "$", "yen", "jpy", "eur"]):
        flags.add("foreign_currency")

    # explicit calculation phrasing
    if any(x in t for x in ["=", "jadi", "total"]):
        flags.add("calculation")

    # --- DECORATIVE / NOISE ---
    if any(x in t for x in ["??", "wkwk", "hehe"]):
        flags.add("typo")

    if "pp" in t:
        flags.add("round_trip")

    if "@" in t and re.search(r"\d", t):
        flags.add("unit_price")

    status = "ambiguous" if flags else "ok"
    return status, flags
