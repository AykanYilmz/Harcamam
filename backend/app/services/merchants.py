"""Turns a raw statement description into the merchant's name.

"29/06 ÖRNEK AVM KAYSERI 02.Tak KAYSERİ 11.500,00 TL İşlemin 2/4 Taksidi" -> "ÖRNEK AVM"
"PAYTR/ÖRNEK TEKNOLOJ İSTANBUL TR" -> "ÖRNEK TEKNOLOJ"
"S/ÖRNEKBILET.COM İSTANB Satis Iade" -> "ÖRNEKBILET.COM"

The name doubles as a rule keyword: rules match whole words, so it matches every description
of that merchant however the bank decorates it.
"""

import re

from app.services.parsing.formats import fold_turkish, normalize_text

# The 81 provinces as normalize_text() writes them, plus how card terminals shorten the
# longest ones (descriptions are cut at a fixed width).
_CITIES = {
    *"""adana adiyaman afyonkarahisar agri aksaray amasya ankara antalya ardahan artvin aydin
    balikesir bartin batman bayburt bilecik bingol bitlis bolu burdur bursa canakkale cankiri
    corum denizli diyarbakir duzce edirne elazig erzincan erzurum eskisehir gaziantep giresun
    gumushane hakkari hatay igdir isparta istanbul izmir kahramanmaras karabuk karaman kars
    kastamonu kayseri kilis kirikkale kirklareli kirsehir kocaeli konya kutahya malatya manisa
    mardin mersin mugla mus nevsehir nigde ordu osmaniye rize sakarya samsun sanliurfa siirt
    sinop sivas sirnak tekirdag tokat trabzon tunceli usak van yalova yozgat zonguldak""".split(),  # noqa: SIM905
    "istanb",
    "afyon",
    "maras",
    "urfa",
    "antep",
}
# Country codes some terminals add after the city.
_COUNTRY_CODES = {"tr", "tur"}

# "29/06 " at the start of an installment line: the original purchase date.
_LEADING_DATE = re.compile(r"^\d{2}/\d{2}\s+")
# Payment facilitators and channel markers in front of the real merchant: "PAYTR/", "S/".
_PREFIX = re.compile(r"^[^\W\d_]{1,10}\s?/\s?")
# "02.Tak ... İşlemin 2/4 Taksidi": everything from the installment marker on.
_INSTALLMENT = re.compile(r"\s+\d{1,2}\.\s?tak\b.*$", re.IGNORECASE)
# Words describing the transaction rather than the merchant.
_TRAILING_NOTES = re.compile(r"\s+(satis\s+)?(iade|iadesi|refund)$", re.IGNORECASE)
_WHITESPACE = re.compile(r"\s+")


def _without_trailing_places(words: list[str]) -> list[str]:
    while len(words) > 1 and normalize_text(words[-1]) in _CITIES | _COUNTRY_CODES:
        words = words[:-1]
    return words


def merchant_name(description: str) -> str:
    text = _WHITESPACE.sub(" ", description).strip()
    text = _LEADING_DATE.sub("", text)
    text = _INSTALLMENT.sub("", text)
    if (stripped := _PREFIX.sub("", text)) and normalize_text(stripped):
        text = stripped
    # Searched in the folded text (same length) so "Satış İade" and "SATIS IADE" both go.
    if match := _TRAILING_NOTES.search(fold_turkish(text)):
        text = text[: match.start()]
    words = _without_trailing_places(text.split())
    return " ".join(words) or description.strip()
