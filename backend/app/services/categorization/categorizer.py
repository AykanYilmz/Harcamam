import uuid
from collections.abc import Iterable
from dataclasses import dataclass

from app.models import TransactionType
from app.services.parsing.formats import normalize_text


@dataclass(frozen=True)
class KeywordRule:
    keyword: str
    category_id: uuid.UUID


def _padded(text: str) -> str:
    # Surrounding spaces turn a substring check into a whole-word check:
    # " sok " is in " sok market " but not in " sokak lezzetleri ".
    return f" {normalize_text(text)} "


class Categorizer:
    """Picks a category for a transaction description. Pure logic: no database access.

    Order: the user's rules, then the default rules; within each, the longest keyword wins
    because it is the most specific. With no match, income goes to the income category and
    expenses to the fallback ("Diğer").
    """

    def __init__(
        self,
        user_rules: Iterable[KeywordRule],
        default_rules: Iterable[KeywordRule],
        income_category_id: uuid.UUID,
        other_category_id: uuid.UUID,
    ) -> None:
        self._rule_groups = [self._prepare(user_rules), self._prepare(default_rules)]
        self._income_category_id = income_category_id
        self._other_category_id = other_category_id

    @staticmethod
    def _prepare(rules: Iterable[KeywordRule]) -> list[tuple[str, uuid.UUID]]:
        prepared = [
            (_padded(rule.keyword), rule.category_id)
            for rule in rules
            if normalize_text(rule.keyword)
        ]
        # Stable sort: equally long keywords keep the order they were given in.
        return sorted(prepared, key=lambda item: len(item[0]), reverse=True)

    def categorize(self, description: str, transaction_type: TransactionType) -> uuid.UUID:
        text = _padded(description)
        for rules in self._rule_groups:
            for keyword, category_id in rules:
                if keyword in text:
                    return category_id
        if transaction_type is TransactionType.INCOME:
            return self._income_category_id
        return self._other_category_id
