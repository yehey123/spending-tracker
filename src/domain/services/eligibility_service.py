from src.domain.models.transaction import Transaction


class EligibilityService:
    @staticmethod
    def check_unionbank_naffl(transaction: Transaction) -> bool:
        ineligible_categories = ["Quasi-cash", "Cash-in"]
        return transaction.category not in ineligible_categories
