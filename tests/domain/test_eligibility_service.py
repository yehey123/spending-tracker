import pytest
from decimal import Decimal
from datetime import datetime

from src.domain.models.transaction import Transaction
from src.domain.services.eligibility_service import EligibilityService


class TestEligibilityService:
    def test_check_unionbank_naffl_eligible_category(self):
        transaction = Transaction(
            description="Test purchase",
            amount=Decimal("100.00"),
            category="Groceries",
            date=datetime.now(),
        )
        
        result = EligibilityService.check_unionbank_naffl(transaction)
        assert result is True

    def test_check_unionbank_naffl_quasi_cash_ineligible(self):
        transaction = Transaction(
            description="Gift card purchase",
            amount=Decimal("50.00"),
            category="Quasi-cash",
            date=datetime.now(),
        )
        
        result = EligibilityService.check_unionbank_naffl(transaction)
        assert result is False

    def test_check_unionbank_naffl_cash_in_ineligible(self):
        transaction = Transaction(
            description="Cash deposit",
            amount=Decimal("1000.00"),
            category="Cash-in",
            date=datetime.now(),
        )
        
        result = EligibilityService.check_unionbank_naffl(transaction)
        assert result is False

    def test_check_unionbank_naffl_various_categories(self):
        eligible_categories = ["Food", "Transportation", "Entertainment", "Utilities"]
        ineligible_categories = ["Quasi-cash", "Cash-in"]

        for category in eligible_categories:
            transaction = Transaction(
                description="Test",
                amount=Decimal("10.00"),
                category=category,
                date=datetime.now(),
            )
            assert EligibilityService.check_unionbank_naffl(transaction) is True

        for category in ineligible_categories:
            transaction = Transaction(
                description="Test",
                amount=Decimal("10.00"),
                category=category,
                date=datetime.now(),
            )
            assert EligibilityService.check_unionbank_naffl(transaction) is False
