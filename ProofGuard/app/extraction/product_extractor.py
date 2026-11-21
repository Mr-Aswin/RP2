"""
ProofGuard - Product Information Extraction Module
Authors:
  - Ashfaq (Ticket 1 - Data & System Foundation): Core extraction engine.
  - Arun Kumar S (Enhancement): None-input handling, M/N & S.No patterns,
    OCR noise cleaning, extract_from_document() helper, additional categories.

This module converts raw text extracted from OCR into structured product information
compatible with the ProofGuard ProductCreate Pydantic schema.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from typing import Any

import spacy
from spacy.language import Language

from app.schemas import ProductCreate

logger = logging.getLogger(__name__)

# Global singleton cache for spaCy NLP model
_NLP_MODEL: Language | None = None


def get_nlp() -> Language:
    """
    Lazy-load the spaCy English language model.
    Reuses the loaded model instance across extraction calls.
    """
    global _NLP_MODEL
    if _NLP_MODEL is None:
        try:
            _NLP_MODEL = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Loading blank 'en' model as fallback."
            )
            _NLP_MODEL = spacy.blank("en")
    return _NLP_MODEL


# Common known brands (canonical forms)
KNOWN_BRANDS: dict[str, str] = {
    "samsung": "Samsung",
    "lg": "LG",
    "whirlpool": "Whirlpool",
    "bosch": "Bosch",
    "sony": "Sony",
    "apple": "Apple",
    "philips": "Philips",
    "panasonic": "Panasonic",
    "haier": "Haier",
    "godrej": "Godrej",
    "ifb": "IFB",
    "dell": "Dell",
    "hp": "HP",
    "lenovo": "Lenovo",
    "toshiba": "Toshiba",
    "hitachi": "Hitachi",
    "electrolux": "Electrolux",
    "dyson": "Dyson",
    "miele": "Miele",
    "carrier": "Carrier",
    "voltas": "Voltas",
    "blue star": "Blue Star",
    "daikin": "Daikin",
    "xiaomi": "Xiaomi",
    "oneplus": "OnePlus",
    "asus": "Asus",
    "acer": "Acer",
    "canon": "Canon",
    "nikon": "Nikon",
    "kitchenaid": "KitchenAid",
    "delonghi": "DeLonghi",
    "morphy richards": "Morphy Richards",
    "kenstar": "Kenstar",
    "bajaj": "Bajaj",
    "crompton": "Crompton",
    "orient": "Orient",
    "usha": "Usha",
    "eureka forbes": "Eureka Forbes",
    "kent": "Kent",
    "general electric": "GE",
    "ge": "GE",
    # --- Arun Kumar S additions ---
    "siemens": "Siemens",
    "sharp": "Sharp",
    "bpl": "BPL",
    "videocon": "Videocon",
    "onida": "Onida",
    "intex": "Intex",
    "micromax": "Micromax",
    "realme": "Realme",
    "vivo": "Vivo",
    "oppo": "Oppo",
    "nokia": "Nokia",
    "motorola": "Motorola",
    "jbl": "JBL",
    "bose": "Bose",
    "harman": "Harman",
    "havells": "Havells",
    "v-guard": "V-Guard",
    "prestige": "Prestige",
    "pigeon": "Pigeon",
    "butterfly": "Butterfly",
    "preethi": "Preethi",
    "nilkamal": "Nilkamal",
    "amul": "Amul",
}

# Known product types mapped to their category and canonical naming
PRODUCT_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    # (regex, canonical product name, category)
    # Home Appliances
    (re.compile(r"\bfront\s+load(?:ing)?\s+washing\s+machine\b", re.IGNORECASE), "Front Load Washing Machine", "Home Appliance"),
    (re.compile(r"\btop\s+load(?:ing)?\s+washing\s+machine\b", re.IGNORECASE), "Top Load Washing Machine", "Home Appliance"),
    (re.compile(r"\bsemi\s+automatic\s+washing\s+machine\b", re.IGNORECASE), "Semi Automatic Washing Machine", "Home Appliance"),
    (re.compile(r"\bfully\s+automatic\s+washing\s+machine\b", re.IGNORECASE), "Fully Automatic Washing Machine", "Home Appliance"),
    (re.compile(r"\bwashing\s+machine\b", re.IGNORECASE), "Washing Machine", "Home Appliance"),
    (re.compile(r"\bclothes\s+dryer\b|\btumble\s+dryer\b", re.IGNORECASE), "Clothes Dryer", "Home Appliance"),
    (re.compile(r"\bdouble\s+door\s+refrigerator\b", re.IGNORECASE), "Double Door Refrigerator", "Home Appliance"),
    (re.compile(r"\bfrench\s+door\s+refrigerator\b", re.IGNORECASE), "French Door Refrigerator", "Home Appliance"),
    (re.compile(r"\bside\s+by\s+side\s+refrigerator\b", re.IGNORECASE), "Side-by-Side Refrigerator", "Home Appliance"),
    (re.compile(r"\brefrigerator\b|\bfridge\b", re.IGNORECASE), "Refrigerator", "Home Appliance"),
    (re.compile(r"\bsplit\s+(?:inverter\s+)?air\s+conditioner\b|\bsplit\s+ac\b", re.IGNORECASE), "Split Air Conditioner", "Home Appliance"),
    (re.compile(r"\bwindow\s+air\s+conditioner\b|\bwindow\s+ac\b", re.IGNORECASE), "Window Air Conditioner", "Home Appliance"),
    (re.compile(r"\bair\s+conditioner\b|\bac\s+unit\b", re.IGNORECASE), "Air Conditioner", "Home Appliance"),
    (re.compile(r"\bvacuum\s+cleaner\b|\brobot\s+vacuum\b", re.IGNORECASE), "Vacuum Cleaner", "Home Appliance"),
    (re.compile(r"\bwater\s+heater\b|\bgeyser\b", re.IGNORECASE), "Water Heater", "Home Appliance"),
    (re.compile(r"\bair\s+purifier\b", re.IGNORECASE), "Air Purifier", "Home Appliance"),

    # Kitchen Appliances
    (re.compile(r"\bconvection\s+microwave\s+oven\b", re.IGNORECASE), "Convection Microwave Oven", "Kitchen Appliance"),
    (re.compile(r"\bmicrowave\s+oven\b", re.IGNORECASE), "Microwave Oven", "Kitchen Appliance"),
    (re.compile(r"\bmicrowave\b", re.IGNORECASE), "Microwave Oven", "Kitchen Appliance"),
    (re.compile(r"\bdishwasher\b", re.IGNORECASE), "Dishwasher", "Kitchen Appliance"),
    (re.compile(r"\binduction\s+cooktop\b|\binduction\s+stove\b", re.IGNORECASE), "Induction Cooktop", "Kitchen Appliance"),
    (re.compile(r"\bblender\b|\bmixer\s+grinder\b|\bfood\s+processor\b", re.IGNORECASE), "Mixer Grinder", "Kitchen Appliance"),
    (re.compile(r"\bcoffee\s+maker\b|\bespresso\s+machine\b", re.IGNORECASE), "Coffee Maker", "Kitchen Appliance"),
    (re.compile(r"\belectric\s+kettle\b", re.IGNORECASE), "Electric Kettle", "Kitchen Appliance"),
    (re.compile(r"\bair\s+fryer\b", re.IGNORECASE), "Air Fryer", "Kitchen Appliance"),
    (re.compile(r"\btoaster\b|\bsandwich\s+maker\b", re.IGNORECASE), "Toaster", "Kitchen Appliance"),

    # Electronics
    (re.compile(r"\bsmart\s+tv\b|\bled\s+tv\b|\boled\s+tv\b|\b4k\s+tv\b", re.IGNORECASE), "Smart Television", "Electronics"),
    (re.compile(r"\btelevision\b|\btv\b", re.IGNORECASE), "Television", "Electronics"),
    (re.compile(r"\blaptop\b|\bnotebook\b|\bmacbook\b", re.IGNORECASE), "Laptop", "Electronics"),
    (re.compile(r"\bsmartphone\b|\bmobile\s+phone\b|\biphone\b", re.IGNORECASE), "Smartphone", "Electronics"),
    (re.compile(r"\btablet\b|\bipad\b", re.IGNORECASE), "Tablet", "Electronics"),
    (re.compile(r"\bdesktop\s+computer\b|\bpersonal\s+computer\b|\bpc\b", re.IGNORECASE), "Desktop Computer", "Electronics"),
    (re.compile(r"\bmonitor\b", re.IGNORECASE), "Monitor", "Electronics"),
    (re.compile(r"\bheadphones\b|\bearbuds\b|\bearphones\b", re.IGNORECASE), "Headphones", "Electronics"),
    (re.compile(r"\bsmartwatch\b|\bsmart\s+watch\b", re.IGNORECASE), "Smartwatch", "Electronics"),
    (re.compile(r"\bcamera\b|\bdslr\b", re.IGNORECASE), "Camera", "Electronics"),
    (re.compile(r"\bprinter\b|\bscanner\b", re.IGNORECASE), "Printer", "Electronics"),
]

# Category keyword associations for secondary classification
CATEGORY_KEYWORD_MAP: dict[str, list[str]] = {
    "Home Appliance": [
        "washing machine", "washer", "dryer", "refrigerator", "fridge", "freezer",
        "air conditioner", "ac unit", "cooling", "vacuum cleaner", "water heater",
        "geyser", "air purifier", "laundry", "appliance", "home appliance"
    ],
    "Kitchen Appliance": [
        "microwave", "oven", "dishwasher", "cooktop", "stove", "blender",
        "mixer", "grinder", "food processor", "coffee maker", "espresso",
        "kettle", "toaster", "air fryer", "kitchen", "kitchen appliance"
    ],
    "Electronics": [
        "television", "tv", "smart tv", "display", "screen", "laptop", "notebook",
        "computer", "pc", "desktop", "smartphone", "mobile phone", "tablet",
        "ipad", "headphones", "soundbar", "speaker", "audio", "camera", "smartwatch",
        "printer", "scanner", "electronics"
    ],
}

# Regex to identify false model/serial candidates (dates, invoices, phone numbers)
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)
INVOICE_PATTERN = re.compile(
    r"\b(?:INV|INVOICE|TEST-INV|BILL|ORDER|RECEIPT)[-_#:\s]*[A-Za-z0-9-_]+\b",
    re.IGNORECASE,
)

DISALLOWED_TOKENS = {
    "NUMBER", "NO", "CODE", "DETAILS", "NAME", "SPECIFICATION", "SPECIFICATIONS",
    "MANUAL", "CUSTOMER", "ADDRESS", "DATE", "TOTAL", "AMOUNT", "PRICE", "QUANTITY",
    "INR", "USD", "EUR", "STATUS", "PAID", "ITEM", "PRODUCT", "BRAND", "SERIAL",
    "MODEL", "ONLY", "TRUE", "FALSE", "NONE", "NULL", "YEAR", "WARRANTY", "REGISTRATION",
    "CARD", "INVOICE", "GUIDE", "DOCUMENT", "FILE", "ID", "EQUIPMENT", "DEVICE",
    "APPLIANCE", "TYPE", "INFORMATION", "INFO", "BATCH"
}


def preprocess_text(raw_text: str | None) -> str:
    """
    Clean, normalize, and prepare raw text extracted from OCR.

    - Validates string or None input type.
    - Normalizes unicode characters (NFKC).
    - Cleans excessive horizontal whitespace per line.
    - Standardizes line breaks while preserving document line structure.
    """
    if raw_text is None:
        return ""

    if not isinstance(raw_text, str):
        raise TypeError(f"Input text must be a string, got {type(raw_text).__name__}")

    if not raw_text.strip():
        return ""

    # Normalize unicode representations
    normalized = unicodedata.normalize("NFKC", raw_text)

    # Standardize line breaks
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    # Clean lines
    cleaned_lines: list[str] = []
    for line in normalized.split("\n"):
        cleaned = re.sub(r"[\xa0\t ]+", " ", line).strip()
        cleaned_lines.append(cleaned)

    # Rejoin lines, collapsing excessive blank lines
    result = "\n".join(cleaned_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def extract_brand(text: str, nlp_doc: spacy.tokens.Doc | None = None) -> str | None:
    """
    Extract brand or manufacturer name from the document text.

    Uses:
    1. Explicit brand/manufacturer labels (e.g. 'Brand: Samsung', 'Manufacturer: LG').
    2. 'Manufactured by ...' declarations.
    3. spaCy Named Entity Recognition (ORG entities).
    4. Dictionary matching against recognized brand names.

    Returns None if no brand can be identified.
    """
    if not text:
        return None

    # 1. Explicit brand label matching
    label_patterns = [
        r"(?i)\b(?:make\s*\/\s*brand|brand|manufacturer|make|mfr)[\t ]*[:=–-]+[\t ]*([A-Za-z0-9&.\- ]{2,35})",
    ]
    for pattern in label_patterns:
        match = re.search(pattern, text)
        if match:
            candidate = match.group(1).strip(" .,;:–-")
            candidate = re.split(r"[\n\r,;]", candidate)[0].strip()
            candidate_lower = candidate.lower()
            if candidate_lower in KNOWN_BRANDS:
                return KNOWN_BRANDS[candidate_lower]
            cleaned = re.sub(
                r"(?i)\s+(?:electronics|corporation|corp\.?|inc\.?|llc|gmbh|ltd\.?|private\s+limited|pvt\.?\s*ltd\.?)$",
                "",
                candidate,
            ).strip()
            if cleaned.lower() in KNOWN_BRANDS:
                return KNOWN_BRANDS[cleaned.lower()]
            if len(cleaned) >= 2 and cleaned.upper() not in DISALLOWED_TOKENS:
                return cleaned.title()

    # 2. 'Manufactured by ...' or 'Made by ...' pattern
    mfg_match = re.search(
        r"(?i)(?:manufactured|made)\s+by[\s:=–-]+([A-Za-z0-9&.\- ]{2,50})",
        text,
    )
    if mfg_match:
        mfg_candidate = mfg_match.group(1).strip(" .,;:–-")
        mfg_candidate = re.split(r"[\n\r,;]", mfg_candidate)[0].strip()
        for key, canonical in KNOWN_BRANDS.items():
            if re.search(rf"\b{re.escape(key)}\b", mfg_candidate, re.IGNORECASE):
                return canonical
        cleaned_mfg = re.sub(
            r"(?i)\s+(?:electronics|corporation|corp\.?|inc\.?|llc|gmbh|ltd\.?|private\s+limited|pvt\.?\s*ltd\.?)$",
            "",
            mfg_candidate,
        ).strip()
        if len(cleaned_mfg) >= 2 and cleaned_mfg.upper() not in DISALLOWED_TOKENS:
            return cleaned_mfg.title()

    # 3. spaCy Named Entity Recognition for ORG entities
    if nlp_doc is not None:
        for ent in nlp_doc.ents:
            if ent.label_ == "ORG":
                ent_clean = ent.text.strip(" .,;:–-")
                ent_lower = ent_clean.lower()
                for key, canonical in KNOWN_BRANDS.items():
                    if re.search(rf"\b{re.escape(key)}\b", ent_lower):
                        return canonical

    # 4. Dictionary matching across lines (prioritize earlier lines for prominent brands)
    lines = text.split("\n")
    for line in lines[:20]:
        line_clean = line.strip(" .,;:–-")
        line_lower = line_clean.lower()
        if line_lower in KNOWN_BRANDS:
            return KNOWN_BRANDS[line_lower]
        for key, canonical in KNOWN_BRANDS.items():
            if re.search(rf"\b{re.escape(key)}\b", line, re.IGNORECASE):
                return canonical

    # Fallback to entire text scan for known brands
    for key, canonical in KNOWN_BRANDS.items():
        if re.search(rf"\b{re.escape(key)}\b", text, re.IGNORECASE):
            return canonical

    return None


def extract_model_number(text: str) -> str | None:
    """
    Extract model number from document text.

    Looks for explicit model labels such as:
    - Model Number
    - Model No / Model No.
    - Product Model
    - Model Code / Model
    - Model / Item No

    Filters out dates, phone numbers, invoice numbers, and generic noise.
    """
    if not text:
        return None

    model_patterns = [
        # Explicit label with separator: Model Number: WW80T, M/N: WA70B, Model No: ...
        r"(?i)\b(?:product\s+)?(?:model(?:\s+(?:number|no\.?|code|id|#))?|m\/n|m\.?no\.?)[\t ]*[:=–-]+[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{1,35})",
        # Label followed by newline: Model Number:\nWW80T
        r"(?i)\b(?:product\s+)?(?:model(?:\s+(?:number|no\.?|code|id|#))?|m\/n|m\.?no\.?)[\t ]*[:=–-]?[\t ]*\n[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{1,35})",
        # Item / Product No:
        r"(?i)\b(?:item|product)\s*(?:model|no\.?|code|#)[\t ]*[:=–-]+[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{1,35})",
    ]

    for pattern in model_patterns:
        for match in re.finditer(pattern, text):
            candidate = match.group(1).strip(" .,;:()[]{}–-")

            if not _is_valid_model_candidate(candidate, text):
                continue

            return candidate

    return None


def _is_valid_model_candidate(candidate: str, full_text: str) -> bool:
    """
    Validate that an extracted candidate string is a plausible model number
    and not a date, phone number, invoice number, or generic label.
    """
    if not candidate or len(candidate) < 2 or len(candidate) > 35:
        return False

    candidate_upper = candidate.upper()

    # Reject if token is purely a disallowed word
    if candidate_upper in DISALLOWED_TOKENS:
        return False

    # Reject if candidate matches date pattern
    if DATE_PATTERN.fullmatch(candidate) or re.search(r"^\d{4}[/-]\d{2}[/-]\d{2}$", candidate):
        return False

    # Reject if candidate matches phone pattern
    if PHONE_PATTERN.fullmatch(candidate):
        return False

    # Reject if candidate matches invoice number in full text
    if candidate_upper.startswith(("INV-", "TEST-INV", "BILL-", "REC-")):
        return False

    invoice_matches = INVOICE_PATTERN.findall(full_text)
    for inv in invoice_matches:
        if candidate_upper in inv.upper():
            return False

    # Reject if candidate has only punctuation
    if not any(c.isalnum() for c in candidate):
        return False

    return True


def extract_serial_number(text: str, exclude_model: str | None = None) -> str | None:
    """
    Extract serial number from document text.

    Looks for serial labels such as:
    - Serial Number / Serial No / Serial No.
    - S/N / SN / Serial # / Serial Identifier
    - Sr No / Sr. No.

    Ensures serial number is not confused with model number or invoice number.
    """
    if not text:
        return None

    serial_patterns = [
        # Explicit label with separator: Serial Number: SN12345678, S.No: ..., SN: 4567890123
        r"(?i)\b(?:serial(?:\s+(?:number|no\.?|id|#|identifier))?|s\/n|sr\.?\s*no\.?|s\.?\s*no\.?|sn)[\t ]*[:=–-]+[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{2,35})",
        # Label followed by newline:
        r"(?i)\b(?:serial(?:\s+(?:number|no\.?|id|#|identifier))?|s\/n|sr\.?\s*no\.?|s\.?\s*no\.?|sn)[\t ]*[:=–-]?[\t ]*\n[\t ]*([A-Za-z0-9][A-Za-z0-9\-_\./]{2,35})",
    ]

    for pattern in serial_patterns:
        for match in re.finditer(pattern, text):
            candidate = match.group(1).strip(" .,;:()[]{}–-")

            if not _is_valid_serial_candidate(candidate, text, exclude_model):
                continue

            return candidate

    return None


def _is_valid_serial_candidate(
    candidate: str, full_text: str, exclude_model: str | None = None
) -> bool:
    """
    Validate that an extracted candidate string is a plausible serial number.
    """
    if not candidate or len(candidate) < 3 or len(candidate) > 35:
        return False

    candidate_upper = candidate.upper()

    if candidate_upper in DISALLOWED_TOKENS:
        return False

    # Ensure not identical to model number
    if exclude_model and candidate.lower() == exclude_model.lower():
        return False

    # Reject pure dates
    if DATE_PATTERN.fullmatch(candidate):
        return False

    # Reject invoice numbers
    if candidate_upper.startswith(("INV-", "TEST-INV", "BILL-", "REC-")):
        return False

    invoice_matches = INVOICE_PATTERN.findall(full_text)
    for inv in invoice_matches:
        if candidate_upper in inv.upper():
            return False

    return True


def extract_product_name(
    text: str, brand: str | None = None, nlp_doc: spacy.tokens.Doc | None = None
) -> str | None:
    """
    Extract product name from document text.

    Uses:
    1. Explicit product name labels (e.g. 'Product Name: Front Load Washing Machine', 'Equipment: Microwave Oven').
    2. Known product patterns (e.g. 'Washing Machine', 'Refrigerator').
    3. Standalone line detection and NLP noun phrase inspection.

    Cleans any leading brand repetition from the product name.
    """
    if not text:
        return None

    # 1. Explicit product name / equipment / appliance labels
    label_patterns = [
        r"(?i)\b(?:product\s+name|product\s+description|item\s+name|item\s+description|equipment|appliance|device)[\t ]*[:=–-]+[\t ]*([^\n\r]+)",
        r"(?i)\bproduct[\t ]*[:=–-]+[\t ]*([^\n\r]+)",
    ]

    for pattern in label_patterns:
        for match in re.finditer(pattern, text):
            candidate = match.group(1).strip(" .,;:–-")
            candidate_first_word = candidate.split()[0].upper() if candidate.split() else ""
            if candidate_first_word in DISALLOWED_TOKENS:
                continue

            candidate = re.split(r"(?i)\s+(?:qty|quantity|price|amount|model|serial|sn)\b", candidate)[0].strip()

            if brand and candidate.lower().startswith(brand.lower()):
                candidate = candidate[len(brand):].strip(" .,;:–-")

            if len(candidate) >= 3:
                for p_regex, canonical_name, _ in PRODUCT_PATTERNS:
                    if p_regex.search(candidate):
                        return canonical_name
                return candidate.title()

    # 2. Known product regex patterns in document text (longest match first)
    for p_regex, canonical_name, _ in PRODUCT_PATTERNS:
        if p_regex.search(text):
            return canonical_name

    # 3. Heading / standalone line inspection
    for line in text.split("\n"):
        line_clean = line.strip(" .,;:–-")
        if not line_clean:
            continue
        line_words = [w.upper() for w in line_clean.split()]
        if any(w in DISALLOWED_TOKENS for w in line_words):
            continue
        for p_regex, canonical_name, _ in PRODUCT_PATTERNS:
            if p_regex.search(line_clean):
                return canonical_name

    return None


def classify_category(product_name: str | None, text: str = "") -> str | None:
    """
    Identify the product category based on the extracted product name and document text.

    Supported initial categories:
    - Home Appliance
    - Kitchen Appliance
    - Electronics

    Returns None if category cannot be confidently identified.
    """
    # 1. Classify directly by product name
    if product_name:
        for p_regex, _, category in PRODUCT_PATTERNS:
            if p_regex.search(product_name):
                return category

        name_lower = product_name.lower()
        for cat, keywords in CATEGORY_KEYWORD_MAP.items():
            for kw in keywords:
                if kw in name_lower:
                    return cat

    # 2. Classify by analyzing document text
    if text:
        text_lower = text.lower()
        scores: dict[str, int] = {cat: 0 for cat in CATEGORY_KEYWORD_MAP}

        for cat, keywords in CATEGORY_KEYWORD_MAP.items():
            for kw in keywords:
                weight = 2 if " " in kw else 1
                matches = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
                scores[cat] += matches * weight

        best_cat = max(scores, key=scores.get)  # type: ignore[arg-type]
        if scores[best_cat] > 0:
            return best_cat

    return None


def extract_product_info(
    raw_text: str | None, as_dict: bool = False
) -> ProductCreate | dict[str, Any]:
    """
    Main extraction interface. Converts raw OCR text into structured product information.

    Workflow:
    1. Preprocesses raw text (validates type, handles None/empty, strips noise, normalizes unicode).
    2. Runs spaCy NLP pipeline.
    3. Extracts Brand, Product Name, Model Number, Serial Number, and Category.
    4. Validates structured data using the existing ProductCreate Pydantic schema.
    5. Returns a validated ProductCreate instance (or dict if as_dict=True).

    Args:
        raw_text: Raw text string extracted from OCR or document processor (or None).
        as_dict: If True, returns a Python dictionary; otherwise returns ProductCreate.

    Returns:
        ProductCreate instance or dictionary containing validated fields:
        product_name, brand, model_number, serial_number, product_category.

    Raises:
        TypeError: If raw_text is not a string or None.
    """
    if raw_text is None:
        empty_product = ProductCreate(
            product_name=None,
            brand=None,
            model_number=None,
            serial_number=None,
            product_category=None,
        )
        return empty_product.model_dump() if as_dict else empty_product

    if not isinstance(raw_text, str):
        raise TypeError(f"Input text must be a string, got {type(raw_text).__name__}")

    cleaned_text = preprocess_text(raw_text)

    # Empty text case: return schema with all None
    if not cleaned_text:
        empty_product = ProductCreate(
            product_name=None,
            brand=None,
            model_number=None,
            serial_number=None,
            product_category=None,
        )
        return empty_product.model_dump() if as_dict else empty_product

    # Run spaCy NLP on normalized text (capped at 100k chars for safety)
    nlp = get_nlp()
    doc = nlp(cleaned_text[:100000])

    # Extract fields
    brand = extract_brand(cleaned_text, nlp_doc=doc)
    model_number = extract_model_number(cleaned_text)
    serial_number = extract_serial_number(cleaned_text, exclude_model=model_number)
    product_name = extract_product_name(cleaned_text, brand=brand, nlp_doc=doc)
    product_category = classify_category(product_name, text=cleaned_text)

    # Construct and validate through existing ProductCreate schema
    product = ProductCreate(
        product_name=product_name,
        brand=brand,
        model_number=model_number,
        serial_number=serial_number,
        product_category=product_category,
    )

    if as_dict:
        return product.model_dump()

    return product


def extract_product_dict(raw_text: str) -> dict[str, Any]:
    """
    Convenience helper that extracts product information and returns a dictionary.
    """
    return extract_product_info(raw_text, as_dict=True)  # type: ignore[return-value]
