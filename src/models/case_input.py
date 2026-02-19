from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import math


class Transaction(BaseModel):
    date: str
    amount: float
    currency: str = "INR"
    type: str
    originator: str
    beneficiary: str
    description: str = ""

    @field_validator("amount")
    @classmethod
    def amount_must_be_finite(cls, v):
        if math.isnan(v) or math.isinf(v):
            raise ValueError("Transaction amount must be a finite number")
        return v

    @field_validator("date")
    @classmethod
    def date_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Transaction date cannot be empty")
        return v.strip()


class CustomerInfo(BaseModel):
    name: str
    account_number: str
    kyc_risk_rating: str = "Medium"
    occupation: str = ""
    account_open_date: str = ""
    expected_monthly_volume: float = 0.0
    declared_income: float = 0.0
    address: str = ""
    pan_number: str = ""

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Customer name cannot be empty")
        return v.strip()

    @field_validator("account_number")
    @classmethod
    def account_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Account number cannot be empty")
        return v.strip()


class CaseInput(BaseModel):
    case_id: str
    customer: CustomerInfo
    transactions: List[Transaction]
    alert_reason: str
    investigation_notes: str = ""
    alert_date: str = ""
    assigned_analyst: str = "system"

    @field_validator("case_id")
    @classmethod
    def case_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Case ID cannot be empty")
        return v.strip()

    @field_validator("transactions")
    @classmethod
    def transactions_must_not_be_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Transactions list cannot be empty")
        return v

    @field_validator("alert_reason")
    @classmethod
    def alert_reason_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Alert reason cannot be empty")
        return v.strip()
