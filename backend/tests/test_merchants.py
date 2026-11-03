import pytest

from app.services.categorization.categorizer import _padded
from app.services.merchants import merchant_name

# Shaped like real card statement lines; every name is made up.
CASES = [
    ("ÖRNEK MARKET KADIKÖY İSTANBUL", "ÖRNEK MARKET KADIKÖY"),
    ("ÖRNEK KASAP BOLU", "ÖRNEK KASAP"),
    ("ÖRNEK MAĞAZA ANKARA TR", "ÖRNEK MAĞAZA"),
    ("PAYTR/ÖRNEK TEKNOLOJ İSTANBUL TR", "ÖRNEK TEKNOLOJ"),
    ("PAYTR /ÖRNEKYAYINCILIK", "ÖRNEKYAYINCILIK"),
    ("IYZICO/ÖRNEKSHOP İSTANBUL", "ÖRNEKSHOP"),
    ("S/ÖRNEKBILET.COM İSTANB Satis Iade", "ÖRNEKBILET.COM"),
    ("ÖRNEK MAĞAZA İADESİ", "ÖRNEK MAĞAZA"),
    (
        "29/06 ÖRNEK AVM KAYSERI 02.Tak KAYSERİ 11.500,00 TL İşlemin 2/4 Taksidi",
        "ÖRNEK AVM",
    ),
    ("07/09 S/ÖRNEKSHOP 01.Tak İSTANBUL 1.200,00 TL İşlemin 1/3 Taksidi", "ÖRNEKSHOP"),
    ("Örnek Oyun Ultra London", "Örnek Oyun Ultra London"),
    # A name that is only a city stays, rather than becoming empty.
    ("BOLU", "BOLU"),
    ("ANKARA ÖRNEK BÜFE ANKARA", "ANKARA ÖRNEK BÜFE"),
]


@pytest.mark.parametrize(("description", "expected"), CASES)
def test_merchant_name(description: str, expected: str) -> None:
    assert merchant_name(description) == expected


@pytest.mark.parametrize("description", [description for description, _ in CASES])
def test_name_as_a_keyword_matches_its_own_description(description: str) -> None:
    # The page saves the name as a rule; it must catch the transaction it came from.
    assert _padded(merchant_name(description)) in _padded(description)
