import re
import unicodedata
 
 
# ──────────────────────────────────────────────
# Phrases injected by CV template generators
# ──────────────────────────────────────────────
UNWANTED_PHRASES = [
    "Icônes pour CV à copier-coller",
    "Un modèle Word, c'est bien.",
    "Rendez-vous sur app.modeles-de-cv.com",
    "Générateur de CV en ligne avec IA",
    "Test ATS",
    "modeles-de-cv.com",
    "cvdesignr.com",
    "canva.com",
    "resumemaker",
    "Créez votre CV gratuitement",
    "Téléchargez votre CV",
]
 
# Unicode replacement map (ligatures, special dashes, etc.)
UNICODE_REPLACEMENTS = {
    "\u2019": "'",   # right single quotation mark
    "\u2018": "'",   # left single quotation mark
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u00b7": " ",   # middle dot (used as bullet)
    "\u2022": " ",   # bullet
    "\u25cf": " ",   # black circle (bullet variant)
    "\uf0b7": " ",   # private use area bullet
    "\u00a0": " ",   # non-breaking space
}
 
 
def normalize_unicode(text: str) -> str:
    """Replace known problematic unicode chars, then NFKC-normalise."""
    for char, replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    return unicodedata.normalize("NFKC", text)
 
 
def remove_template_noise(text: str) -> str:
    """Strip CV-generator watermarks and template phrases."""
    for phrase in UNWANTED_PHRASES:
        text = text.replace(phrase, "")
    return text
 
 
def remove_urls(text: str) -> str:
    return re.sub(r"https?://\S+|www\.\S+", "", text)
 
 
def remove_emails(text: str) -> str:
    """Redact emails (keep placeholder so we don't break sentence flow)."""
    return re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL]", text)
 
 
def normalize_whitespace(text: str) -> str:
    """Collapse multiple blank lines and trailing spaces."""
    text = re.sub(r"[ \t]+", " ", text)         # multiple spaces → one
    text = re.sub(r"\n{3,}", "\n\n", text)       # 3+ newlines → 2
    return text.strip()
 
 
def clean_cv_text(text: str, remove_urls_flag: bool = True, redact_emails: bool = False) -> str:
    """
    Full cleaning pipeline for raw CV text.
 
    Steps:
      1. Normalize unicode
      2. Remove template watermarks
      3. (Optional) Remove URLs
      4. (Optional) Redact emails
      5. Normalize whitespace
    """
    text = normalize_unicode(text)
    text = remove_template_noise(text)
    if remove_urls_flag:
        text = remove_urls(text)
    if redact_emails:
        text = remove_emails(text)
    text = normalize_whitespace(text)
    return text
 