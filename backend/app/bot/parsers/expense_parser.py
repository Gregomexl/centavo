"""Natural language expense parser."""

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.models.transaction import TransactionType


@dataclass
class ParsedTransaction:
    """Parsed transaction data."""

    type: TransactionType
    amount: Decimal
    description: str
    category_hint: str | None = None
    raw_message: str | None = None


class ExpenseParser:
    """Parse natural language expense/income messages."""

    # Expense patterns (English)
    EXPENSE_PATTERNS_EN = [
        r"^(\d+(?:\.\d{2})?)\s+(.+)$",  # "50 lunch"
        r"^\$(\d+(?:\.\d{2})?)\s+(.+)$",  # "$50 lunch"
        r"^spent\s+(\d+(?:\.\d{2})?)\s+(?:on\s+)?(.+)$",  # "spent 50 on lunch"
    ]

    # Expense patterns (Spanish)
    EXPENSE_PATTERNS_ES = [
        r"^(\d+(?:\.\d{2})?)\s+(.+)$",  # "50 comida"
        r"^\$(\d+(?:\.\d{2})?)\s+(.+)$",  # "$50 comida"
        r"^gasté\s+(\d+(?:\.\d{2})?)\s+(?:en\s+)?(.+)$",  # "gasté 50 en comida"
    ]

    # Income patterns (English)
    INCOME_PATTERNS_EN = [
        r"^\+(\d+(?:\.\d{2})?)\s+(.+)$",  # "+1000 salary"
        r"^income\s+(\d+(?:\.\d{2})?)\s+(.+)$",  # "income 1000 salary"
        r"^earned\s+(\d+(?:\.\d{2})?)\s+(?:from\s+)?(.+)$",  # "earned 1000 from salary"
    ]

    # Income patterns (Spanish)
    INCOME_PATTERNS_ES = [
        r"^\+(\d+(?:\.\d{2})?)\s+(.+)$",  # "+1000 salario"
        r"^ingreso\s+(\d+(?:\.\d{2})?)\s+(.+)$",  # "ingreso 1000 salario"
        r"^gané\s+(\d+(?:\.\d{2})?)\s+(?:de\s+)?(.+)$",  # "gané 1000 de salario"
    ]

    # Category keywords (English)
    CATEGORY_KEYWORDS_EN = {
        "food": ["lunch", "dinner", "breakfast", "food", "restaurant", "cafe"],
        "transport": ["uber", "taxi", "bus", "metro", "gas", "fuel"],
        "shopping": ["shopping", "clothes", "amazon", "store"],
        "entertainment": ["movie", "cinema", "game", "concert", "netflix"],
    }

    # Category keywords (Spanish)
    CATEGORY_KEYWORDS_ES = {
        "food": ["almuerzo", "cena", "desayuno", "comida", "restaurante", "café"],
        "transport": ["uber", "taxi", "autobús", "metro", "gasolina"],
        "shopping": ["compras", "ropa", "tienda"],
        "entertainment": ["película", "cine", "juego", "concierto"],
    }

    def parse(self, message: str) -> ParsedTransaction | None:
        """Parse a message into a transaction."""
        message = message.strip().lower()

        # Try income patterns first
        transaction = self._try_parse_income(message)
        if transaction:
            return transaction

        # Try expense patterns
        transaction = self._try_parse_expense(message)
        if transaction:
            return transaction

        return None

    def _try_parse_income(self, message: str) -> ParsedTransaction | None:
        """Try to parse as income."""
        all_patterns = self.INCOME_PATTERNS_EN + self.INCOME_PATTERNS_ES

        for pattern in all_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                amount_str, description = match.groups()
                amount = Decimal(amount_str)

                return ParsedTransaction(
                    type=TransactionType.INCOME,
                    amount=amount,
                    description=description.strip(),
                    category_hint=self._detect_category(description),
                    raw_message=message,
                )

        return None

    def _try_parse_expense(self, message: str) -> ParsedTransaction | None:
        """Try to parse as expense."""
        all_patterns = self.EXPENSE_PATTERNS_EN + self.EXPENSE_PATTERNS_ES

        for pattern in all_patterns:
            match = re.match(pattern, message, re.IGNORECASE)
            if match:
                amount_str, description = match.groups()
                amount = Decimal(amount_str)

                return ParsedTransaction(
                    type=TransactionType.EXPENSE,
                    amount=amount,
                    description=description.strip(),
                    category_hint=self._detect_category(description),
                    raw_message=message,
                )

        return None

    def _detect_category(self, description: str) -> str | None:
        """Detect category from description keywords."""
        description_lower = description.lower()

        # Check English keywords
        for category, keywords in self.CATEGORY_KEYWORDS_EN.items():
            if any(keyword in description_lower for keyword in keywords):
                return category

        # Check Spanish keywords
        for category, keywords in self.CATEGORY_KEYWORDS_ES.items():
            if any(keyword in description_lower for keyword in keywords):
                return category

        return None
