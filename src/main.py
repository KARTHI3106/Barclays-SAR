import json
import logging
from pathlib import Path
from typing import Dict, Tuple

from src.config import CONFIG
from src.models.case_input import CaseInput
from src.models.sar_output import SARNarrative, ExplainabilityOutput
from src.components.data_parser import DataParser
from src.components.rag_engine import RAGEngine
from src.components.llm_orchestrator import LLMOrchestrator
from src.components.audit_logger import AuditLogger

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, CONFIG["app"].get("log_level", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)


class SARGenerator:
    """Main orchestrator for the SAR Narrative Generation pipeline."""

    def __init__(self):
        logger.info("Initializing SAR Generator pipeline...")
        self.parser = DataParser(
            anonymize=CONFIG["security"].get("anonymize_pii", True)
        )
        self.rag = RAGEngine()
        self.llm = LLMOrchestrator()
        self.audit = AuditLogger()
        logger.info("SAR Generator initialized successfully")

    def generate(
        self, case_json: dict, user_id: str = "system",
        progress_callback=None,
    ) -> Tuple[SARNarrative, ExplainabilityOutput]:
        """Full pipeline: Parse > Analyze > RAG > LLM > Audit > Output.

        Args:
            case_json: Raw case JSON data.
            user_id: ID of the user initiating generation.
            progress_callback: Optional callable(step, message) for UI updates.
        """

        def _progress(step: int, message: str):
            if progress_callback:
                progress_callback(step, message)

        # Step 1: Parse and validate input
        _progress(1, "Parsing and validating case input...")
        logger.info("Step 1: Parsing case input...")
        case = self.parser.parse_case_input(case_json)

        self.audit.log_event(
            case_id=case.case_id,
            event_type="data_input",
            user_id=user_id,
            input_data={
                "case_id": case.case_id,
                "transaction_count": len(case.transactions),
            },
            metadata={"step": "1_parse_input"},
        )

        # Step 2: Calculate transaction statistics
        _progress(2, "Calculating transaction statistics...")
        logger.info("Step 2: Calculating transaction statistics...")
        stats = self.parser.calculate_transaction_stats(case.transactions)

        self.audit.log_event(
            case_id=case.case_id,
            event_type="analysis",
            user_id=user_id,
            metadata={"step": "2_transaction_stats", "stats": stats},
        )

        # Step 3: Identify suspicious patterns
        _progress(3, "Detecting suspicious patterns...")
        logger.info("Step 3: Identifying suspicious patterns...")
        patterns = self.parser.identify_patterns(case, stats)
        risk_score = self.parser.calculate_risk_score(patterns, stats, case)

        self.audit.log_event(
            case_id=case.case_id,
            event_type="pattern_detection",
            user_id=user_id,
            metadata={
                "step": "3_pattern_detection",
                "patterns": patterns,
                "risk_score": risk_score,
            },
        )

        # Step 4: RAG retrieval
        _progress(4, "Retrieving templates and classifying typology...")
        logger.info("Step 4: RAG retrieval...")
        case_summary = self.rag.build_case_summary(case, stats, patterns)
        templates = self.rag.retrieve_templates(case_summary, top_k=2)
        typology, typology_confidence = self.rag.identify_typology(
            patterns, case.alert_reason
        )
        regulatory_context = self.rag.get_regulatory_context(typology)
        template_text = templates[0]["content"] if templates else ""

        self.audit.log_event(
            case_id=case.case_id,
            event_type="rag_retrieval",
            user_id=user_id,
            retrieved_context={
                "templates_used": [t["id"] for t in templates],
                "typology": typology,
                "typology_confidence": typology_confidence,
                "regulatory_context_snippet": regulatory_context[:500],
            },
            metadata={"step": "4_rag_retrieval"},
        )

        # Step 5: Generate narrative via LLM
        _progress(5, "Generating SAR narrative via LLM...")
        logger.info("Step 5: Generating narrative via LLM...")
        narrative, llm_callback = self.llm.generate_narrative(
            case=case,
            stats=stats,
            patterns=patterns,
            typology=typology,
            risk_score=risk_score,
            regulatory_context=regulatory_context,
            template_reference=template_text,
        )

        audit_data = llm_callback.get_audit_data()
        self.audit.log_event(
            case_id=case.case_id,
            event_type="llm_generation",
            user_id=user_id,
            llm_reasoning=json.dumps(audit_data, default=str)[:5000],
            generated_output=narrative.narrative_text[:5000],
            model_version=narrative.model_version,
            confidence_score=narrative.confidence_score,
            metadata={"step": "5_llm_generation"},
        )

        # Step 6: Build explainability output
        _progress(6, "Building explainability report...")
        logger.info("Step 6: Building explainability...")

        # Safe volume ratio calculation
        volume_ratio = "N/A"
        if case.customer.expected_monthly_volume > 0:
            ratio = stats.get("total_volume", 0) / case.customer.expected_monthly_volume
            volume_ratio = f"{ratio:.1f}x"

        explainability = ExplainabilityOutput(
            case_id=case.case_id,
            why_suspicious=narrative.red_flags,
            typology_matched=typology,
            typology_confidence=typology_confidence,
            similar_cases=[],
            templates_used=[t["id"] for t in templates],
            model_reasoning=(
                f"Risk score {risk_score}/100 based on "
                f"{len(patterns)} patterns detected"
            ),
            data_points_accessed=[
                f"{stats.get('total_transactions', 0)} transactions analyzed",
                "Customer KYC profile reviewed",
                "Transaction stats calculated",
                f"{len(templates)} templates retrieved",
            ],
            rules_matched=patterns,
            calculations={
                "total_volume": (
                    f"{stats.get('currency', 'INR')} "
                    f"{stats.get('total_volume', 0):,.2f}"
                ),
                "volume_vs_expected": volume_ratio,
                "risk_score": f"{risk_score}/100",
            },
        )

        self.audit.log_event(
            case_id=case.case_id,
            event_type="explainability",
            user_id=user_id,
            metadata={
                "step": "6_explainability",
                "red_flags": narrative.red_flags,
                "typology": typology,
                "confidence": typology_confidence,
            },
        )

        logger.info(
            "Pipeline complete for case %s. Risk: %d/100, Typology: %s",
            case.case_id, risk_score, typology,
        )
        return narrative, explainability

    def generate_with_agents(
        self, case_json: dict, user_id: str = "system"
    ) -> Dict:
        """Run the multi-agent (A2A) pipeline."""
        from src.agents.a2a_agents import CoordinatorAgent

        coordinator = CoordinatorAgent()
        return coordinator.execute(case_json, user_id=user_id)

    def approve_narrative(self, case_id: str, user_id: str, edited_text: str = None):
        """Approve a narrative and log to audit trail."""
        self.audit.log_event(
            case_id=case_id,
            event_type="approval",
            user_id=user_id,
            human_edits={"edited": edited_text is not None},
            metadata={"action": "approved"},
        )
        self.audit.db.update_case_status(case_id, "approved", approved_by=user_id)

    def reject_narrative(self, case_id: str, user_id: str, reason: str = ""):
        """Reject a narrative and log to audit trail."""
        self.audit.log_event(
            case_id=case_id,
            event_type="rejection",
            user_id=user_id,
            metadata={"action": "rejected", "reason": reason},
        )
        self.audit.db.update_case_status(case_id, "rejected")

    def get_audit_trail(self, case_id: str):
        """Get audit trail for a case."""
        return self.audit.get_audit_trail(case_id)

    def export_audit(self, case_id: str, fmt: str = "json"):
        """Export audit trail in given format."""
        return self.audit.export_audit_trail(case_id, fmt)
