import re
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

from src.config import CONFIG
from src.models.case_input import CaseInput
from src.models.sar_output import SARNarrative

logger = logging.getLogger(__name__)


class LLMCallback:
    """Captures LLM interaction details for audit trail."""

    def __init__(self):
        self.prompt_sent = ""
        self.response_received = ""
        self.model_used = ""
        self.start_time = None
        self.end_time = None
        self.token_count = 0

    def get_audit_data(self) -> Dict:
        duration = 0
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
        return {
            "prompt_length": len(self.prompt_sent),
            "response_length": len(self.response_received),
            "model": self.model_used,
            "duration_seconds": duration,
            "prompt_preview": self.prompt_sent[:500] if self.prompt_sent else "",
            "response_preview": self.response_received[:500] if self.response_received else "",
        }


class LLMOrchestrator:
    """Orchestrates LLM calls for SAR narrative generation using Ollama."""

    def __init__(self):
        self.model = CONFIG["llm"]["model"]
        self.temperature = CONFIG["llm"]["temperature"]
        self.max_tokens = CONFIG["llm"]["max_tokens"]
        self.base_url = CONFIG["llm"]["base_url"]

        # Load prompt templates with proper error handling
        prompts_dir = Path(__file__).parent.parent / "prompts"
        system_prompt_path = prompts_dir / "system_prompt.txt"
        user_prompt_path = prompts_dir / "user_prompt_template.txt"

        if system_prompt_path.exists():
            self.system_prompt = system_prompt_path.read_text(encoding="utf-8")
        else:
            logger.warning(
                "System prompt file not found at %s. Using default.",
                system_prompt_path
            )
            self.system_prompt = (
                "You are an expert compliance analyst specializing in "
                "Suspicious Transaction Reports under PMLA, 2002."
            )

        if user_prompt_path.exists():
            self.user_template = user_prompt_path.read_text(encoding="utf-8")
        else:
            logger.warning(
                "User prompt template not found at %s. Using default.",
                user_prompt_path
            )
            self.user_template = (
                "Generate a SAR narrative for case: {case_id}\n"
                "Alert: {alert_reason}\n"
                "Patterns: {patterns}\n"
                "Typology: {typology}\n"
                "Risk Score: {risk_score}/100"
            )

        logger.info("LLM Orchestrator initialized. Model: %s", self.model)

    def generate_narrative(
        self,
        case: CaseInput,
        stats: Dict,
        patterns: List[str],
        typology: str,
        risk_score: int,
        regulatory_context: str,
        template_reference: str,
    ) -> Tuple[SARNarrative, LLMCallback]:
        """Generate a SAR narrative using the LLM."""

        callback = LLMCallback()
        callback.model_used = self.model

        # Build prompt
        prompt = self._build_prompt(
            case, stats, patterns, typology, risk_score,
            regulatory_context, template_reference
        )
        callback.prompt_sent = prompt

        # Try LLM generation
        narrative_text = ""
        try:
            callback.start_time = time.time()
            narrative_text = self._call_ollama(prompt)
            callback.end_time = time.time()
            callback.response_received = narrative_text
            duration = callback.end_time - callback.start_time
            logger.info("LLM generation completed in %.1fs", duration)
        except Exception as e:
            logger.warning("LLM call failed: %s. Using fallback narrative.", e)
            callback.end_time = time.time()
            narrative_text = self._generate_fallback_narrative(
                case, stats, patterns, typology
            )
            callback.response_received = narrative_text

        # Parse sections
        sections = self._parse_narrative(narrative_text)

        # Build SAR output
        narrative = SARNarrative(
            case_id=case.case_id,
            narrative_text=narrative_text,
            sections=sections,
            confidence_score=risk_score,
            typology=typology,
            red_flags=patterns,
            templates_used=[],
            model_version=self.model,
            transaction_stats=stats,
        )

        return narrative, callback

    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API for text generation."""
        try:
            from langchain_ollama import OllamaLLM

            llm = OllamaLLM(
                model=self.model,
                base_url=self.base_url,
                temperature=self.temperature,
                num_predict=self.max_tokens,
            )

            full_prompt = f"{self.system_prompt}\n\n{prompt}"
            response = llm.invoke(full_prompt)
            return response

        except ImportError:
            logger.warning("langchain_ollama not available. Trying direct ollama.")
            try:
                import ollama

                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    options={
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                )
                return response["message"]["content"]
            except Exception as e:
                raise RuntimeError(f"All LLM backends failed: {e}")

    def _build_prompt(
        self, case, stats, patterns, typology, risk_score,
        regulatory_context, template_reference
    ) -> str:
        """Build the user prompt from template."""
        patterns_text = "\n".join(f"- {p}" for p in patterns)

        # Format transaction types
        txn_types = ", ".join(
            f"{k}: {v}" for k, v in stats.get("transaction_types", {}).items()
        )

        try:
            prompt = self.user_template.format(
                case_id=case.case_id,
                alert_date=case.alert_date or "N/A",
                alert_reason=case.alert_reason,
                customer_name=case.customer.name,
                account_number=case.customer.account_number,
                occupation=case.customer.occupation or "Not specified",
                risk_rating=case.customer.kyc_risk_rating,
                account_open_date=case.customer.account_open_date or "N/A",
                currency=stats.get("currency", "INR"),
                expected_volume=case.customer.expected_monthly_volume,
                declared_income=case.customer.declared_income,
                transaction_count=stats.get("total_transactions", 0),
                total_volume=stats.get("total_volume", 0),
                total_credits=stats.get("total_credits", 0),
                total_debits=stats.get("total_debits", 0),
                credit_count=stats.get("credit_count", 0),
                debit_count=stats.get("debit_count", 0),
                avg_amount=stats.get("avg_amount", 0),
                max_amount=stats.get("max_amount", 0),
                date_range_start=stats.get("date_range_start", "N/A"),
                date_range_end=stats.get("date_range_end", "N/A"),
                date_range_days=stats.get("date_range_days", 0),
                transaction_types=txn_types,
                patterns=patterns_text,
                typology=typology,
                risk_score=risk_score,
                investigation_notes=case.investigation_notes or "None provided",
                regulatory_context=regulatory_context,
                template_reference=(
                    template_reference[:2000] if template_reference
                    else "No template available"
                ),
            )
        except KeyError as e:
            logger.warning("Prompt template missing key: %s. Using simplified prompt.", e)
            prompt = (
                f"Generate a SAR narrative for case {case.case_id}.\n"
                f"Alert: {case.alert_reason}\n"
                f"Patterns: {patterns_text}\n"
                f"Typology: {typology}\n"
                f"Risk Score: {risk_score}/100\n"
                f"Regulatory Context: {regulatory_context}"
            )
        return prompt

    def _parse_narrative(self, text: str) -> Dict[str, str]:
        """Parse narrative text into structured sections."""
        sections = {}
        section_headers = [
            ("I", r"I\.\s*SUMMARY\s*OF\s*SUSPICIOUS\s*ACTIVITY"),
            ("II", r"II\.\s*ACCOUNT\s*AND\s*CUSTOMER\s*INFORMATION"),
            ("III", r"III\.\s*DESCRIPTION\s*OF\s*SUSPICIOUS\s*ACTIVITY"),
            ("IV", r"IV\.\s*EXPLANATION\s*OF\s*SUSPICION"),
            ("V", r"V\.\s*CONCLUSION"),
        ]

        for i, (key, pattern) in enumerate(section_headers):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start = match.end()
                if i + 1 < len(section_headers):
                    next_match = re.search(
                        section_headers[i + 1][1], text[start:], re.IGNORECASE
                    )
                    end = start + next_match.start() if next_match else len(text)
                else:
                    end = len(text)
                sections[key] = text[start:end].strip()

        # If parsing failed, put entire text in section I
        if not sections:
            sections["I"] = text.strip()

        return sections

    def _generate_fallback_narrative(self, case, stats, patterns, typology) -> str:
        """Generate a template-based narrative when LLM is unavailable."""
        currency = stats.get("currency", "INR")
        total_volume = stats.get("total_volume", 0)
        total_txns = stats.get("total_transactions", 0)
        date_start = stats.get("date_range_start", "N/A")
        date_end = stats.get("date_range_end", "N/A")
        expected_vol = case.customer.expected_monthly_volume

        patterns_text = "\n".join(f"- {p}" for p in patterns)

        return f"""I. SUMMARY OF SUSPICIOUS ACTIVITY

This report is filed regarding suspicious transactions identified in the account of {case.customer.name} (Account: {case.customer.account_number}). A total of {total_txns} transactions totaling {currency} {total_volume:,.2f} were identified during the review period from {date_start} to {date_end}. The activity is consistent with {typology}.

II. ACCOUNT AND CUSTOMER INFORMATION

Account holder {case.customer.name} maintains account {case.customer.account_number}, opened on {case.customer.account_open_date}. The customer's declared occupation is {case.customer.occupation} with expected monthly transaction volume of {currency} {expected_vol:,.2f}. Current KYC risk rating: {case.customer.kyc_risk_rating}.

III. DESCRIPTION OF SUSPICIOUS ACTIVITY

Alert Reason: {case.alert_reason}

Transaction Summary:
- Total Volume: {currency} {total_volume:,.2f}
- Transaction Count: {total_txns}
- Date Range: {date_start} to {date_end}

Suspicious Patterns:
{patterns_text}

IV. EXPLANATION OF SUSPICION

{case.investigation_notes or 'No additional investigation notes provided.'}

The identified patterns are consistent with {typology} typology under PMLA guidelines.

V. CONCLUSION AND RECOMMENDATION

Based on the analysis, this activity warrants reporting as a Suspicious Transaction Report (STR) under Section 12 of PMLA, 2002. The FIU-IND should be notified within the prescribed timeline. Enhanced monitoring is recommended for this account.

[This narrative was generated using template fallback -- LLM was unavailable]
"""
