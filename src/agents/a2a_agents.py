"""
A2A (Agent-to-Agent) Multi-Agent Architecture for AuditWatch.

Five specialized agents that coordinate via message passing:
1. CoordinatorAgent -- orchestrates the full pipeline
2. DataEnrichmentAgent -- parses and enriches case data
3. TypologyAgent -- classifies crime typology
4. NarrativeAgent -- generates SAR narrative via RAG + LLM
5. AuditAgent -- logs every step for regulatory traceability

Communication follows JSON-RPC style messages (in-process for MVP,
HTTP-ready for production scaling).
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentMessage:
    """Message passed between A2A agents."""

    def __init__(
        self,
        sender: str,
        receiver: str,
        task_type: str,
        payload: Dict,
        message_id: Optional[str] = None,
    ):
        self.sender = sender
        self.receiver = receiver
        self.task_type = task_type
        self.payload = payload
        self.message_id = message_id or f"msg-{int(time.time() * 1000)}"
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": self.task_type,
            "params": {
                "sender": self.sender,
                "receiver": self.receiver,
                "payload": self.payload,
                "timestamp": self.timestamp,
            },
        }


class AgentResult:
    """Result returned by an agent after processing a task."""

    def __init__(self, agent_name: str, status: str, data: Dict, duration: float = 0):
        self.agent_name = agent_name
        self.status = status
        self.data = data
        self.duration = duration
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "agent": self.agent_name,
            "status": self.status,
            "data": self.data,
            "duration_seconds": round(self.duration, 3),
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# Agent 1: Data Enrichment
# ---------------------------------------------------------------------------

class DataEnrichmentAgent:
    """Parses case input, calculates baseline stats, anonymizes PII."""

    AGENT_NAME = "data_enrichment_agent"

    def agent_card(self) -> Dict:
        return {
            "name": self.AGENT_NAME,
            "description": "Enriches raw case data with statistics and anonymization",
            "version": "1.0.0",
            "skills": [
                {
                    "id": "parse_case",
                    "name": "Parse Case Input",
                    "description": "Validate and parse raw JSON into structured case model",
                },
                {
                    "id": "calculate_stats",
                    "name": "Calculate Transaction Statistics",
                    "description": "Compute volume, averages, date ranges, counterparty counts",
                },
                {
                    "id": "detect_patterns",
                    "name": "Detect Suspicious Patterns",
                    "description": "Identify 9 types of suspicious transaction patterns",
                },
            ],
        }

    def execute(self, task: AgentMessage) -> AgentResult:
        start = time.time()
        try:
            from src.components.data_parser import DataParser

            case_json = task.payload.get("case_json", {})
            parser = DataParser(anonymize=True)
            case = parser.parse_case_input(case_json)
            stats = parser.calculate_transaction_stats(case.transactions)
            patterns = parser.identify_patterns(case, stats)
            risk_score = parser.calculate_risk_score(patterns, stats, case)

            duration = time.time() - start
            logger.info(
                "[%s] Enriched case %s: %d patterns, risk %d/100 in %.2fs",
                self.AGENT_NAME, case.case_id, len(patterns), risk_score, duration,
            )

            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="completed",
                data={
                    "case_id": case.case_id,
                    "case": case.model_dump(),
                    "stats": stats,
                    "patterns": patterns,
                    "risk_score": risk_score,
                },
                duration=duration,
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="failed",
                data={"error": str(e)},
                duration=time.time() - start,
            )


# ---------------------------------------------------------------------------
# Agent 2: Typology Classification
# ---------------------------------------------------------------------------

class TypologyAgent:
    """Classifies crime typology using RAG-based matching."""

    AGENT_NAME = "typology_agent"

    def agent_card(self) -> Dict:
        return {
            "name": self.AGENT_NAME,
            "description": "Classifies crime typology with confidence scoring",
            "version": "1.0.0",
            "skills": [
                {
                    "id": "classify_typology",
                    "name": "Classify Crime Typology",
                    "description": "Match patterns to known crime typologies with confidence scores",
                },
                {
                    "id": "get_regulatory_context",
                    "name": "Get Regulatory Context",
                    "description": "Retrieve PMLA/RBI references for identified typology",
                },
            ],
        }

    def execute(self, task: AgentMessage) -> AgentResult:
        start = time.time()
        try:
            from src.components.rag_engine import RAGEngine

            patterns = task.payload.get("patterns", [])
            alert_reason = task.payload.get("alert_reason", "")

            rag = RAGEngine()
            typology, confidence = rag.identify_typology(patterns, alert_reason)
            regulatory_context = rag.get_regulatory_context(typology)

            duration = time.time() - start
            logger.info(
                "[%s] Classified typology: %s (%.1f%%) in %.2fs",
                self.AGENT_NAME, typology, confidence, duration,
            )

            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="completed",
                data={
                    "typology": typology,
                    "confidence": confidence,
                    "regulatory_context": regulatory_context,
                },
                duration=duration,
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="failed",
                data={"error": str(e)},
                duration=time.time() - start,
            )


# ---------------------------------------------------------------------------
# Agent 3: Narrative Generation
# ---------------------------------------------------------------------------

class NarrativeAgent:
    """Generates SAR narrative using RAG templates + LLM."""

    AGENT_NAME = "narrative_agent"

    def agent_card(self) -> Dict:
        return {
            "name": self.AGENT_NAME,
            "description": "Generates structured SAR narratives using RAG + LLM",
            "version": "1.0.0",
            "skills": [
                {
                    "id": "retrieve_templates",
                    "name": "Retrieve SAR Templates",
                    "description": "Find relevant templates from vector database",
                },
                {
                    "id": "generate_narrative",
                    "name": "Generate SAR Narrative",
                    "description": "Generate 5-section SAR narrative using LLM",
                },
            ],
        }

    def execute(self, task: AgentMessage) -> AgentResult:
        start = time.time()
        try:
            from src.components.rag_engine import RAGEngine
            from src.components.llm_orchestrator import LLMOrchestrator
            from src.models.case_input import CaseInput

            payload = task.payload
            case = CaseInput(**payload["case"])
            stats = payload["stats"]
            patterns = payload["patterns"]
            typology = payload["typology"]
            risk_score = payload["risk_score"]
            regulatory_context = payload.get("regulatory_context", "")

            rag = RAGEngine()
            case_summary = rag.build_case_summary(case, stats, patterns)
            templates = rag.retrieve_templates(case_summary)
            template_text = templates[0]["content"] if templates else ""

            llm = LLMOrchestrator()
            narrative, callback = llm.generate_narrative(
                case=case, stats=stats, patterns=patterns,
                typology=typology, risk_score=risk_score,
                regulatory_context=regulatory_context,
                template_reference=template_text,
            )

            duration = time.time() - start
            logger.info(
                "[%s] Generated narrative for %s in %.2fs",
                self.AGENT_NAME, case.case_id, duration,
            )

            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="completed",
                data={
                    "narrative": narrative.model_dump(),
                    "llm_audit": callback.get_audit_data(),
                    "templates_used": [t["id"] for t in templates],
                },
                duration=duration,
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="failed",
                data={"error": str(e)},
                duration=time.time() - start,
            )


# ---------------------------------------------------------------------------
# Agent 4: Audit
# ---------------------------------------------------------------------------

class AuditAgent:
    """Logs every pipeline step for regulatory traceability."""

    AGENT_NAME = "audit_agent"

    def __init__(self):
        from src.components.audit_logger import AuditLogger
        self.audit = AuditLogger()

    def agent_card(self) -> Dict:
        return {
            "name": self.AGENT_NAME,
            "description": "Maintains complete audit trail for regulatory compliance",
            "version": "1.0.0",
            "skills": [
                {
                    "id": "log_step",
                    "name": "Log Pipeline Step",
                    "description": "Record a pipeline step with data points and reasoning",
                },
                {
                    "id": "get_trail",
                    "name": "Get Audit Trail",
                    "description": "Retrieve complete audit trail for a case",
                },
            ],
        }

    def execute(self, task: AgentMessage) -> AgentResult:
        start = time.time()
        try:
            case_id = task.payload.get("case_id", "")
            event_type = task.payload.get("event_type", "agent_step")

            self.audit.log_event(
                case_id=case_id,
                event_type=event_type,
                user_id=f"a2a:{task.sender}",
                input_data=task.payload.get("input_data"),
                metadata={
                    "source": "a2a_protocol",
                    "sender_agent": task.sender,
                    "step": task.payload.get("step", ""),
                },
            )

            duration = time.time() - start
            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="completed",
                data={"logged": True, "case_id": case_id, "event_type": event_type},
                duration=duration,
            )
        except Exception as e:
            return AgentResult(
                agent_name=self.AGENT_NAME,
                status="failed",
                data={"error": str(e)},
                duration=time.time() - start,
            )


# ---------------------------------------------------------------------------
# Agent 5: Coordinator (orchestrator)
# ---------------------------------------------------------------------------

class CoordinatorAgent:
    """Orchestrates the multi-agent SAR generation pipeline.

    Dispatches tasks to specialized agents and aggregates results.
    This is the entry point for the A2A pipeline.
    """

    AGENT_NAME = "coordinator_agent"

    def __init__(self):
        self.data_agent = DataEnrichmentAgent()
        self.typology_agent = TypologyAgent()
        self.narrative_agent = NarrativeAgent()
        self.audit_agent = AuditAgent()
        self.pipeline_log = []

    def agent_card(self) -> Dict:
        return {
            "name": self.AGENT_NAME,
            "description": "Coordinates multi-agent SAR generation pipeline",
            "version": "1.0.0",
            "skills": [
                {
                    "id": "orchestrate_sar",
                    "name": "Orchestrate SAR Generation",
                    "description": (
                        "Run full multi-agent pipeline: "
                        "Data Enrichment -> Typology -> Narrative -> Audit"
                    ),
                },
            ],
            "subordinate_agents": [
                self.data_agent.agent_card(),
                self.typology_agent.agent_card(),
                self.narrative_agent.agent_card(),
                self.audit_agent.agent_card(),
            ],
        }

    def execute(self, case_json: Dict, user_id: str = "system") -> Dict:
        """Run the full multi-agent pipeline."""
        pipeline_start = time.time()
        self.pipeline_log = []
        results = {}

        # Step 1: Data Enrichment
        msg1 = AgentMessage(
            sender=self.AGENT_NAME,
            receiver=self.data_agent.AGENT_NAME,
            task_type="enrich_case",
            payload={"case_json": case_json},
        )
        data_result = self.data_agent.execute(msg1)
        self.pipeline_log.append(data_result.to_dict())
        results["data_enrichment"] = data_result

        if data_result.status != "completed":
            return self._build_error_response("Data enrichment failed", data_result)

        # Audit: log data enrichment
        self._log_audit(
            case_id=data_result.data["case_id"],
            step="data_enrichment",
            sender=self.data_agent.AGENT_NAME,
            input_data={
                "patterns_found": len(data_result.data.get("patterns", [])),
                "risk_score": data_result.data.get("risk_score", 0),
            },
        )

        # Step 2: Typology Classification
        msg2 = AgentMessage(
            sender=self.AGENT_NAME,
            receiver=self.typology_agent.AGENT_NAME,
            task_type="classify_typology",
            payload={
                "patterns": data_result.data["patterns"],
                "alert_reason": case_json.get("alert_reason", ""),
            },
        )
        typology_result = self.typology_agent.execute(msg2)
        self.pipeline_log.append(typology_result.to_dict())
        results["typology"] = typology_result

        if typology_result.status != "completed":
            return self._build_error_response("Typology classification failed", typology_result)

        # Audit: log typology
        self._log_audit(
            case_id=data_result.data["case_id"],
            step="typology_classification",
            sender=self.typology_agent.AGENT_NAME,
            input_data={
                "typology": typology_result.data.get("typology", ""),
                "confidence": typology_result.data.get("confidence", 0),
            },
        )

        # Step 3: Narrative Generation
        msg3 = AgentMessage(
            sender=self.AGENT_NAME,
            receiver=self.narrative_agent.AGENT_NAME,
            task_type="generate_narrative",
            payload={
                "case": data_result.data["case"],
                "stats": data_result.data["stats"],
                "patterns": data_result.data["patterns"],
                "risk_score": data_result.data["risk_score"],
                "typology": typology_result.data["typology"],
                "regulatory_context": typology_result.data.get("regulatory_context", ""),
            },
        )
        narrative_result = self.narrative_agent.execute(msg3)
        self.pipeline_log.append(narrative_result.to_dict())
        results["narrative"] = narrative_result

        # Audit: log narrative generation
        self._log_audit(
            case_id=data_result.data["case_id"],
            step="narrative_generation",
            sender=self.narrative_agent.AGENT_NAME,
            input_data={
                "generation_time": narrative_result.duration,
                "status": narrative_result.status,
            },
        )

        pipeline_duration = time.time() - pipeline_start
        logger.info(
            "[%s] Pipeline completed in %.2fs with %d agent steps",
            self.AGENT_NAME, pipeline_duration, len(self.pipeline_log),
        )

        return {
            "status": "completed" if narrative_result.status == "completed" else "partial",
            "case_id": data_result.data.get("case_id", ""),
            "pipeline_duration": round(pipeline_duration, 3),
            "agent_steps": self.pipeline_log,
            "results": {
                "data": data_result.data,
                "typology": typology_result.data,
                "narrative": narrative_result.data,
            },
        }

    def _log_audit(self, case_id: str, step: str, sender: str, input_data: Dict):
        """Send audit log message to AuditAgent."""
        msg = AgentMessage(
            sender=sender,
            receiver=self.audit_agent.AGENT_NAME,
            task_type="log_step",
            payload={
                "case_id": case_id,
                "event_type": f"a2a_{step}",
                "step": step,
                "input_data": input_data,
            },
        )
        audit_result = self.audit_agent.execute(msg)
        self.pipeline_log.append(audit_result.to_dict())

    def _build_error_response(self, message: str, result: AgentResult) -> Dict:
        return {
            "status": "failed",
            "error": message,
            "agent_steps": self.pipeline_log,
            "failed_agent": result.to_dict(),
        }
