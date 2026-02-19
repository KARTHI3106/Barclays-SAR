import logging
from typing import List, Dict
from datetime import datetime
from collections import Counter

from src.models.case_input import CaseInput, Transaction
from src.utils.anonymization import anonymize_case

logger = logging.getLogger(__name__)


class DataParser:
    """Parses and validates case input, calculates transaction stats,
    identifies suspicious patterns."""

    def __init__(self, anonymize: bool = True):
        self.anonymize = anonymize

    def parse_case_input(self, raw_json: dict) -> CaseInput:
        """Parse raw JSON into a validated CaseInput model."""
        case = CaseInput(**raw_json)
        logger.info(
            "Parsed case %s with %d transactions",
            case.case_id, len(case.transactions)
        )

        if self.anonymize:
            case = anonymize_case(case)
            logger.info("Case %s anonymized", case.case_id)

        return case

    def calculate_transaction_stats(self, transactions: List[Transaction]) -> Dict:
        """Calculate comprehensive transaction statistics."""
        if not transactions:
            logger.warning("No transactions provided for stats calculation")
            return {
                "total_transactions": 0,
                "total_volume": 0.0,
                "total_credits": 0.0,
                "total_debits": 0.0,
                "credit_count": 0,
                "debit_count": 0,
                "avg_amount": 0.0,
                "max_amount": 0.0,
                "min_amount": 0.0,
                "date_range_start": "N/A",
                "date_range_end": "N/A",
                "date_range_days": 0,
                "transaction_types": {},
                "currency": "INR",
                "unique_originators": 0,
                "unique_beneficiaries": 0,
            }

        amounts = [t.amount for t in transactions]
        credits = [t for t in transactions if t.amount > 0]
        debits = [t for t in transactions if t.amount < 0]

        dates = []
        for t in transactions:
            try:
                dates.append(datetime.strptime(t.date, "%Y-%m-%d"))
            except ValueError:
                try:
                    dates.append(datetime.strptime(t.date, "%d-%m-%Y"))
                except ValueError:
                    pass

        date_range_start = min(dates).strftime("%Y-%m-%d") if dates else "N/A"
        date_range_end = max(dates).strftime("%Y-%m-%d") if dates else "N/A"
        date_range_days = (max(dates) - min(dates)).days + 1 if len(dates) > 1 else 1

        txn_types = Counter(t.type for t in transactions)
        currency = transactions[0].currency if transactions else "INR"

        abs_amounts = [abs(a) for a in amounts]
        total_volume = sum(abs_amounts)

        stats = {
            "total_transactions": len(transactions),
            "total_volume": total_volume,
            "total_credits": sum(t.amount for t in credits),
            "total_debits": sum(abs(t.amount) for t in debits),
            "credit_count": len(credits),
            "debit_count": len(debits),
            "avg_amount": total_volume / len(amounts) if len(amounts) > 0 else 0.0,
            "max_amount": max(abs_amounts) if abs_amounts else 0.0,
            "min_amount": min(abs_amounts) if abs_amounts else 0.0,
            "date_range_start": date_range_start,
            "date_range_end": date_range_end,
            "date_range_days": date_range_days,
            "transaction_types": dict(txn_types),
            "currency": currency,
            "unique_originators": len(set(t.originator for t in transactions)),
            "unique_beneficiaries": len(set(t.beneficiary for t in transactions)),
        }

        logger.info(
            "Transaction stats: %d txns, volume: %s %s",
            stats["total_transactions"], currency,
            f"{stats['total_volume']:,.2f}"
        )
        return stats

    def identify_patterns(self, case: CaseInput, stats: Dict) -> List[str]:
        """Identify suspicious patterns from transaction data."""
        patterns = []

        if not case.transactions:
            return patterns

        # Pattern 1: Structuring (amounts below reporting threshold)
        threshold = 1000000  # 10 lakh INR
        near_threshold = [
            t for t in case.transactions
            if 0 < t.amount < threshold and t.amount > threshold * 0.8
        ]
        if len(near_threshold) >= 3:
            patterns.append(
                f"Structuring: {len(near_threshold)} transactions just below "
                f"INR {threshold:,.0f} reporting threshold"
            )

        # Pattern 2: Volume spike
        expected = case.customer.expected_monthly_volume
        if expected > 0 and stats.get("total_volume", 0) > 0:
            ratio = stats["total_volume"] / expected
            if ratio > 3:
                patterns.append(
                    f"Volume spike: {ratio:.1f}x above expected monthly volume"
                )

        # Pattern 3: Rapid movement (same-day credits and debits)
        dates_amounts = {}
        for t in case.transactions:
            if t.date not in dates_amounts:
                dates_amounts[t.date] = {"credits": 0.0, "debits": 0.0}
            if t.amount > 0:
                dates_amounts[t.date]["credits"] += t.amount
            else:
                dates_amounts[t.date]["debits"] += abs(t.amount)

        for date, vals in dates_amounts.items():
            if vals["credits"] > 0 and vals["debits"] > 0:
                patterns.append(
                    f"Rapid movement: Credits and debits on same day ({date})"
                )

        # Pattern 4: Multiple small deposits
        small_deposits = [t for t in case.transactions if 0 < t.amount < 200000]
        if len(small_deposits) >= 5:
            patterns.append(
                f"Multiple small deposits: {len(small_deposits)} deposits under INR 2,00,000"
            )

        # Pattern 5: Income mismatch
        declared = case.customer.declared_income
        if declared > 0 and stats.get("total_volume", 0) > 0:
            income_ratio = stats["total_volume"] / declared
            if income_ratio > 2:
                patterns.append(
                    f"Income mismatch: Transaction volume {income_ratio:.1f}x "
                    f"declared annual income"
                )

        # Pattern 6: Multiple unique counterparties
        originators = stats.get("unique_originators", 0)
        if originators > 10:
            patterns.append(
                f"Multiple originators: {originators} unique sources in "
                f"{stats.get('date_range_days', 0)} days"
            )

        # Pattern 7: Round-number transactions
        round_txns = [
            t for t in case.transactions
            if t.amount > 0 and t.amount % 10000 == 0
        ]
        if len(round_txns) >= 3:
            patterns.append(
                f"Round-number transactions: {len(round_txns)} transactions "
                f"in exact round amounts"
            )

        # Pattern 8: Large single transaction
        for t in case.transactions:
            if abs(t.amount) >= 5000000:  # 50 lakhs
                patterns.append(
                    f"Large transaction: {t.currency} {abs(t.amount):,.2f} on {t.date}"
                )

        # Pattern 9: High-risk transaction types
        high_risk_types = ["SWIFT", "Wire Transfer", "Hawala"]
        hr_txns = [t for t in case.transactions if t.type in high_risk_types]
        if hr_txns:
            types_found = ", ".join(set(t.type for t in hr_txns))
            patterns.append(
                f"High-risk transfer types: {len(hr_txns)} {types_found} transactions"
            )

        logger.info("Identified %d suspicious patterns", len(patterns))
        return patterns

    def calculate_risk_score(
        self, patterns: List[str], stats: Dict, case: CaseInput
    ) -> int:
        """Calculate a risk score from 0-100 based on patterns and stats."""
        score = 0

        # Base score from number of patterns
        score += min(len(patterns) * 10, 40)

        # Volume deviation (guard against division by zero)
        expected = case.customer.expected_monthly_volume
        total_volume = stats.get("total_volume", 0)
        if expected > 0 and total_volume > 0:
            ratio = total_volume / expected
            if ratio > 10:
                score += 25
            elif ratio > 5:
                score += 15
            elif ratio > 3:
                score += 10

        # KYC risk rating
        risk_map = {"High": 15, "Medium": 5, "Low": 0}
        score += risk_map.get(case.customer.kyc_risk_rating, 5)

        # Multiple counterparties
        originators = stats.get("unique_originators", 0)
        if originators > 20:
            score += 10
        elif originators > 10:
            score += 5

        # Cap at 100
        score = min(score, 100)
        logger.info("Risk score: %d/100", score)
        return score
