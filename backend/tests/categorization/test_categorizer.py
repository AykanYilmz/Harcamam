import uuid

import pytest

from app.models import TransactionType
from app.services.categorization.categorizer import Categorizer, KeywordRule
from app.services.categorization.default_rules import DEFAULT_KEYWORDS

MARKET = uuid.uuid4()
ONLINE_MARKET = uuid.uuid4()
SUBSCRIPTIONS = uuid.uuid4()
CASH = uuid.uuid4()
HOBBY = uuid.uuid4()
INCOME = uuid.uuid4()
OTHER = uuid.uuid4()

DEFAULT_RULES = [
    KeywordRule("MIGROS", MARKET),
    KeywordRule("SOK", MARKET),
    KeywordRule("BIM", MARKET),
    KeywordRule("NETFLIX", SUBSCRIPTIONS),
    KeywordRule("NAKIT CEKIM", CASH),
]

EXPENSE = TransactionType.EXPENSE


def categorizer(user_rules: list[KeywordRule] | None = None) -> Categorizer:
    return Categorizer(user_rules or [], DEFAULT_RULES, INCOME, OTHER)


@pytest.mark.parametrize(
    ("description", "expected"),
    [
        ("MIGROS KADIKÖY İSTANBUL", MARKET),
        ("migros sanal market", MARKET),
        ("ŞOK MARKET", MARKET),
        ("BİM KADIKÖY", MARKET),
        ("NETFLIX.COM", SUBSCRIPTIONS),
        ("ATM NAKİT ÇEKİM", CASH),
    ],
)
def test_matches_default_keywords_ignoring_case_and_turkish_letters(
    description: str, expected: uuid.UUID
) -> None:
    assert categorizer().categorize(description, EXPENSE) == expected


@pytest.mark.parametrize("description", ["SOKAK LEZZETLERI", "BIMBO", "NAKIT", "XMIGROS"])
def test_keywords_match_whole_words_only(description: str) -> None:
    assert categorizer().categorize(description, EXPENSE) == OTHER


def test_unmatched_expense_goes_to_other() -> None:
    assert categorizer().categorize("BILINMEYEN DUKKAN", EXPENSE) == OTHER


@pytest.mark.parametrize("description", ["ÖRNEK.COM Satis Iade", "ÖRNEK MAĞAZA İADESİ"])
def test_unmatched_refund_lowers_spending_instead_of_counting_as_income(
    description: str,
) -> None:
    assert categorizer().categorize(description, TransactionType.INCOME) == OTHER


def test_matched_refund_goes_to_the_merchants_category() -> None:
    assert categorizer().categorize("MIGROS IADE", TransactionType.INCOME) == MARKET


def test_unmatched_income_goes_to_income() -> None:
    assert categorizer().categorize("BILINMEYEN ODEME", TransactionType.INCOME) == INCOME


def test_matched_income_uses_the_rule() -> None:
    assert categorizer().categorize("MIGROS IADE", TransactionType.INCOME) == MARKET


def test_user_rule_beats_default_rule() -> None:
    user_rules = [KeywordRule("MIGROS", HOBBY)]

    assert categorizer(user_rules).categorize("MIGROS KADIKOY", EXPENSE) == HOBBY


def test_short_user_rule_beats_longer_default_rule() -> None:
    user_rules = [KeywordRule("SANAL", HOBBY)]

    assert categorizer(user_rules).categorize("MIGROS SANAL MARKET", EXPENSE) == HOBBY


def test_longest_keyword_wins_within_a_group() -> None:
    user_rules = [KeywordRule("MIGROS", MARKET), KeywordRule("MIGROS SANAL", ONLINE_MARKET)]

    assert categorizer(user_rules).categorize("MIGROS SANAL MARKET", EXPENSE) == ONLINE_MARKET


def test_equal_length_keywords_keep_given_order() -> None:
    user_rules = [KeywordRule("ALPHA", HOBBY), KeywordRule("BRAVO", MARKET)]

    assert categorizer(user_rules).categorize("BRAVO ALPHA", EXPENSE) == HOBBY


def test_rules_without_letters_or_digits_are_ignored() -> None:
    user_rules = [KeywordRule(" - ", HOBBY)]

    assert categorizer(user_rules).categorize("A - B", EXPENSE) == OTHER


def test_match_returns_the_deciding_rule() -> None:
    user_rule = KeywordRule("MIGROS SANAL", ONLINE_MARKET)

    assert categorizer([user_rule]).match("MIGROS SANAL MARKET") == user_rule
    assert categorizer().match("ŞOK MARKET") == KeywordRule("SOK", MARKET)
    assert categorizer().match("BILINMEYEN DUKKAN") is None


@pytest.mark.parametrize(
    ("description", "category"),
    [
        ("ÖRNEK ECZANESİ", "Sağlık"),
        ("OTOBAN ÖRNEK GİŞESİ", "Ulaşım"),
        ("ÖRNEK GROSS MARKET", "Market"),
        ("ÖRNEK KAFE REST", "Yemek"),
        ("0000 ÖRNEK-KART Ödeme-teşekkür", "Transfer"),
        # The account side of paying the card bill: already counted as card purchases.
        ("KREDİ KARTI BORÇ ÖDEMESİ", "Transfer"),
        ("ÖRNEK KART ÖDEME 1234", "Transfer"),
        ("KART BORCU TAHSİLAT", "Transfer"),
        ("ÖRNEK PETROL ANKARA", "Ulaşım"),
        ("ÖRNEK KAHVE", "Yemek"),
        ("ÖRNEK ÇİĞKÖFTE", "Yemek"),
        ("ÖRNEK GIDA SANAYİ", "Market"),
        ("ÖRNEK TEKEL BAYİİ", "Market"),
        ("FLO MAĞAZACILIK", "Giyim"),
        ("ÖRNEK KİTAP", "Alışveriş"),
        ("T.C.SAĞLIK BAKANLIĞI", "Sağlık"),
    ],
)
def test_built_in_keywords_cover_card_statement_merchants(description: str, category: str) -> None:
    ids = {name: uuid.uuid4() for name in DEFAULT_KEYWORDS}
    rules = [
        KeywordRule(word, ids[name]) for name, words in DEFAULT_KEYWORDS.items() for word in words
    ]

    assert Categorizer([], rules, INCOME, OTHER).categorize(description, EXPENSE) == ids[category]
