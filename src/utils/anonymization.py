import re
import hashlib
from src.models.case_input import CaseInput, CustomerInfo, Transaction
from typing import List


def anonymize_value(value: str, prefix: str = "ANON") -> str:
    h = hashlib.md5(value.encode()).hexdigest()[:6].upper()
    return f"[{prefix}-{h}]"


def anonymize_case(case: CaseInput) -> CaseInput:
    anon_customer = CustomerInfo(
        name=anonymize_value(case.customer.name, "NAME"),
        account_number=anonymize_value(case.customer.account_number, "ACCT"),
        kyc_risk_rating=case.customer.kyc_risk_rating,
        occupation=case.customer.occupation,
        account_open_date=case.customer.account_open_date,
        expected_monthly_volume=case.customer.expected_monthly_volume,
        declared_income=case.customer.declared_income,
        address=anonymize_value(case.customer.address, "ADDR") if case.customer.address else "",
        pan_number=anonymize_value(case.customer.pan_number, "PAN") if case.customer.pan_number else ""
    )

    anon_transactions = []
    for txn in case.transactions:
        anon_txn = Transaction(
            date=txn.date,
            amount=txn.amount,
            currency=txn.currency,
            type=txn.type,
            originator=anonymize_value(txn.originator, "ORIG"),
            beneficiary=anonymize_value(txn.beneficiary, "BENF"),
            description=txn.description
        )
        anon_transactions.append(anon_txn)

    return CaseInput(
        case_id=case.case_id,
        customer=anon_customer,
        transactions=anon_transactions,
        alert_reason=case.alert_reason,
        investigation_notes=case.investigation_notes,
        alert_date=case.alert_date,
        assigned_analyst=case.assigned_analyst
    )
