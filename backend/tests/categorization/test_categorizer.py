import uuid

import pytest

from app.models import TransactionType
from app.services.categorization.categorizer import Categorizer, KeywordRule

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
