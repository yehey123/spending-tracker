import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.models.transaction import Transaction


class TestTransaction:
    def test_create_valid_transaction(self):
        transaction = Transaction(
            description="Test purchase",
            amount=Decimal("100.00"),
            category="Groceries",
            date=datetime.now(),
        )
        
        assert transaction.description == "Test purchase"
        assert transaction.amount == Decimal("100.00")
        assert transaction.category == "Groceries"
        assert transaction.is_naffl_eligible is True

    def test_create_transaction_with_default_date(self):
        transaction = Transaction(
            description="Test",
            amount=Decimal("50.00"),
            category="Food",
        )
        
        assert transaction.date is not None
        assert isinstance(transaction.date, datetime)

    def test_amount_validator_positive_only(self):
        with pytest.raises(ValueError):
            Transaction(
                description="Test",
                amount=Decimal("0"),
                category="Food",
            )

        with pytest.raises(ValueError):
            Transaction(
                description="Test",
                amount=Decimal("-10.00"),
                category="Food",
            )

    def test_amount_validator_valid_values(self):
        transaction = Transaction(
            description="Test",
            amount=Decimal("0.01"),
            category="Food",
        )
        
        assert transaction.amount == Decimal("0.01")
