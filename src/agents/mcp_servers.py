"""
MCP (Model Context Protocol) Tool Servers for AuditWatch.

Three tool servers exposing SAR pipeline capabilities as callable tools:
1. TransactionAnalyzerServer -- transaction analysis and pattern detection
2. SARTemplateServer -- RAG retrieval and narrative generation
3. AuditTrailServer -- audit logging and trail management

Each server implements list_tools() and call_tool(name, args) following
the MCP tool server pattern. Any LLM client that supports MCP can call
these tools directly.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MCPToolDefinition:
    """Defines a single MCP tool with name, description, and input schema."""

    def __init__(self, name: str, description: str, input_schema: Dict):
        self.name = name
        self.description = description
        self.input_schema = input_schema

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.input_schema,
            },
        }


class MCPToolResult:
    """Result returned from an MCP tool call."""

    def __init__(self, content: Any, is_error: bool = False):
        self.content = content
        self.is_error = is_error

    def to_dict(self) -> Dict:
        return {
            "content": [{"type": "text", "text": json.dumps(self.content, default=str)}],
            "isError": self.is_error,
        }


# ---------------------------------------------------------------------------
# Server 1: Transaction Analyzer
# ---------------------------------------------------------------------------

class TransactionAnalyzerServer:
    """MCP Server: transaction_analyzer

    Exposes transaction analysis capabilities as MCP tools.
    Wraps DataParser functionality for external LLM consumption.
    """

    SERVER_NAME = "transaction_analyzer"
    SERVER_VERSION = "1.0.0"

    def __init__(self):
        from src.components.data_parser import DataParser
        self.parser = DataParser(anonymize=False)
        self._tools = self._register_tools()
        logger.info("MCP Server '%s' initialized with %d tools",
                     self.SERVER_NAME, len(self._tools))

    def _register_tools(self) -> Dict[str, MCPToolDefinition]:
        return {
            "analyze_transactions": MCPToolDefinition(
                name="analyze_transactions",
                description=(
                    "Analyze a complete case: parse transactions, calculate stats, "
                    "detect patterns, and compute risk score. Returns full analysis."
                ),
                input_schema={
                    "case_json": {
                        "type": "object",
                        "description": "Full case JSON with case_id, customer, transactions, alert_reason",
                    }
                },
            ),
            "calculate_baseline": MCPToolDefinition(
                name="calculate_baseline",
                description=(
                    "Calculate transaction baseline statistics for a list of transactions. "
                    "Returns total volume, averages, date ranges, and counterparty counts."
                ),
                input_schema={
                    "case_json": {
                        "type": "object",
                        "description": "Case JSON containing transactions to analyze",
                    }
                },
            ),
            "classify_typology": MCPToolDefinition(
                name="classify_typology",
                description=(
                    "Classify the crime typology based on detected patterns and alert reason. "
                    "Returns typology name and confidence percentage."
                ),
                input_schema={
                    "patterns": {
                        "type": "array",
                        "description": "List of detected suspicious patterns",
                    },
                    "alert_reason": {
                        "type": "string",
                        "description": "Original alert trigger reason",
                    },
                },
            ),
        }

    def list_tools(self) -> List[Dict]:
        """List all available tools on this MCP server."""
        return [tool.to_dict() for tool in self._tools.values()]

    def call_tool(self, name: str, arguments: Dict) -> MCPToolResult:
        """Call a tool by name with given arguments."""
        if name not in self._tools:
            return MCPToolResult(
                {"error": f"Unknown tool: {name}"},
                is_error=True,
            )

        try:
            if name == "analyze_transactions":
                return self._analyze_transactions(arguments.get("case_json", {}))
            elif name == "calculate_baseline":
                return self._calculate_baseline(arguments.get("case_json", {}))
            elif name == "classify_typology":
                return self._classify_typology(
                    arguments.get("patterns", []),
                    arguments.get("alert_reason", ""),
                )
        except Exception as e:
            logger.error("MCP tool '%s' failed: %s", name, e)
            return MCPToolResult({"error": str(e)}, is_error=True)

    def _analyze_transactions(self, case_json: Dict) -> MCPToolResult:
        case = self.parser.parse_case_input(case_json)
        stats = self.parser.calculate_transaction_stats(case.transactions)
        patterns = self.parser.identify_patterns(case, stats)
        risk_score = self.parser.calculate_risk_score(patterns, stats, case)

        return MCPToolResult({
            "case_id": case.case_id,
            "stats": stats,
            "patterns": patterns,
            "risk_score": risk_score,
            "pattern_count": len(patterns),
        })

    def _calculate_baseline(self, case_json: Dict) -> MCPToolResult:
        case = self.parser.parse_case_input(case_json)
        stats = self.parser.calculate_transaction_stats(case.transactions)

        return MCPToolResult({
            "case_id": case.case_id,
            "baseline": {
                "total_volume": stats.get("total_volume", 0),
                "avg_amount": stats.get("avg_amount", 0),
                "transaction_count": stats.get("total_transactions", 0),
                "date_range_days": stats.get("date_range_days", 0),
                "unique_originators": stats.get("unique_originators", 0),
                "unique_beneficiaries": stats.get("unique_beneficiaries", 0),
                "expected_monthly_volume": case.customer.expected_monthly_volume,
            },
        })

    def _classify_typology(self, patterns: List[str], alert_reason: str) -> MCPToolResult:
        from src.components.rag_engine import RAGEngine
        rag = RAGEngine()
        typology, confidence = rag.identify_typology(patterns, alert_reason)

        return MCPToolResult({
            "typology": typology,
            "confidence": confidence,
            "patterns_analyzed": len(patterns),
        })


# ---------------------------------------------------------------------------
# Server 2: SAR Template Engine
# ---------------------------------------------------------------------------

class SARTemplateServer:
    """MCP Server: sar_template_engine

    Exposes SAR template retrieval and narrative generation as MCP tools.
    Wraps RAGEngine and LLMOrchestrator.
    """

    SERVER_NAME = "sar_template_engine"
    SERVER_VERSION = "1.0.0"

    def __init__(self):
        self._tools = self._register_tools()
        logger.info("MCP Server '%s' initialized with %d tools",
                     self.SERVER_NAME, len(self._tools))

    def _register_tools(self) -> Dict[str, MCPToolDefinition]:
        return {
            "retrieve_templates": MCPToolDefinition(
                name="retrieve_templates",
                description=(
                    "Retrieve the most relevant SAR templates from the vector database "
                    "based on a case summary query."
                ),
                input_schema={
                    "query": {
                        "type": "string",
                        "description": "Case summary text for similarity search",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of templates to retrieve (default: 2)",
                    },
                },
            ),
            "generate_narrative": MCPToolDefinition(
                name="generate_narrative",
                description=(
                    "Generate a complete SAR narrative using RAG + LLM pipeline. "
                    "Takes full case data and returns structured narrative."
                ),
                input_schema={
                    "case_json": {
                        "type": "object",
                        "description": "Full case JSON input",
                    },
                },
            ),
            "get_regulatory_context": MCPToolDefinition(
                name="get_regulatory_context",
                description=(
                    "Get PMLA/RBI regulatory context for a specific crime typology."
                ),
                input_schema={
                    "typology": {
                        "type": "string",
                        "description": "Crime typology name (e.g., layering, structuring)",
                    },
                },
            ),
        }

    def list_tools(self) -> List[Dict]:
        return [tool.to_dict() for tool in self._tools.values()]

    def call_tool(self, name: str, arguments: Dict) -> MCPToolResult:
        if name not in self._tools:
            return MCPToolResult({"error": f"Unknown tool: {name}"}, is_error=True)

        try:
            if name == "retrieve_templates":
                return self._retrieve_templates(
                    arguments.get("query", ""),
                    arguments.get("top_k", 2),
                )
            elif name == "generate_narrative":
                return self._generate_narrative(arguments.get("case_json", {}))
            elif name == "get_regulatory_context":
                return self._get_regulatory_context(arguments.get("typology", ""))
        except Exception as e:
            logger.error("MCP tool '%s' failed: %s", name, e)
            return MCPToolResult({"error": str(e)}, is_error=True)

    def _retrieve_templates(self, query: str, top_k: int) -> MCPToolResult:
        from src.components.rag_engine import RAGEngine
        rag = RAGEngine()
        templates = rag.retrieve_templates(query, top_k=top_k)

        return MCPToolResult({
            "templates": [
                {
                    "id": t["id"],
                    "typology": t["metadata"].get("typology", "unknown"),
                    "distance": t.get("distance", 0),
                    "content_preview": t["content"][:300],
                }
                for t in templates
            ],
            "count": len(templates),
        })

    def _generate_narrative(self, case_json: Dict) -> MCPToolResult:
        from src.components.data_parser import DataParser
        from src.components.rag_engine import RAGEngine
        from src.components.llm_orchestrator import LLMOrchestrator

        parser = DataParser(anonymize=True)
        rag = RAGEngine()
        llm = LLMOrchestrator()

        case = parser.parse_case_input(case_json)
        stats = parser.calculate_transaction_stats(case.transactions)
        patterns = parser.identify_patterns(case, stats)
        risk_score = parser.calculate_risk_score(patterns, stats, case)

        case_summary = rag.build_case_summary(case, stats, patterns)
        templates = rag.retrieve_templates(case_summary)
        typology, confidence = rag.identify_typology(patterns, case.alert_reason)
        regulatory_context = rag.get_regulatory_context(typology)
        template_text = templates[0]["content"] if templates else ""

        narrative, callback = llm.generate_narrative(
            case=case, stats=stats, patterns=patterns,
            typology=typology, risk_score=risk_score,
            regulatory_context=regulatory_context,
            template_reference=template_text,
        )

        return MCPToolResult({
            "case_id": narrative.case_id,
            "narrative_text": narrative.narrative_text[:3000],
            "risk_score": risk_score,
            "typology": typology,
            "sections": list(narrative.sections.keys()),
            "generation_time": callback.get_audit_data().get("duration_seconds", 0),
        })

    def _get_regulatory_context(self, typology: str) -> MCPToolResult:
        from src.components.rag_engine import RAGEngine
        rag = RAGEngine()
        context = rag.get_regulatory_context(typology)

        return MCPToolResult({
            "typology": typology,
            "regulatory_context": context,
        })


# ---------------------------------------------------------------------------
# Server 3: Audit Trail Manager
# ---------------------------------------------------------------------------

class AuditTrailServer:
    """MCP Server: audit_trail_manager

    Exposes audit trail logging and retrieval as MCP tools.
    Wraps AuditLogger functionality.
    """

    SERVER_NAME = "audit_trail_manager"
    SERVER_VERSION = "1.0.0"

    def __init__(self):
        from src.components.audit_logger import AuditLogger
        self.audit = AuditLogger()
        self._tools = self._register_tools()
        logger.info("MCP Server '%s' initialized with %d tools",
                     self.SERVER_NAME, len(self._tools))

    def _register_tools(self) -> Dict[str, MCPToolDefinition]:
        return {
            "log_decision": MCPToolDefinition(
                name="log_decision",
                description=(
                    "Log a decision step in the audit trail with data points "
                    "and reasoning for regulatory traceability."
                ),
                input_schema={
                    "case_id": {"type": "string", "description": "Case identifier"},
                    "step": {"type": "string", "description": "Pipeline step name"},
                    "data_points": {"type": "object", "description": "Data accessed"},
                    "reasoning": {"type": "string", "description": "Decision reasoning"},
                },
            ),
            "get_audit_trail": MCPToolDefinition(
                name="get_audit_trail",
                description="Retrieve the complete audit trail for a case.",
                input_schema={
                    "case_id": {"type": "string", "description": "Case identifier"},
                },
            ),
            "export_audit": MCPToolDefinition(
                name="export_audit",
                description="Export audit trail in JSON or CSV format.",
                input_schema={
                    "case_id": {"type": "string", "description": "Case identifier"},
                    "format": {
                        "type": "string",
                        "description": "Export format: json or csv",
                    },
                },
            ),
        }

    def list_tools(self) -> List[Dict]:
        return [tool.to_dict() for tool in self._tools.values()]

    def call_tool(self, name: str, arguments: Dict) -> MCPToolResult:
        if name not in self._tools:
            return MCPToolResult({"error": f"Unknown tool: {name}"}, is_error=True)

        try:
            if name == "log_decision":
                return self._log_decision(
                    arguments.get("case_id", ""),
                    arguments.get("step", ""),
                    arguments.get("data_points", {}),
                    arguments.get("reasoning", ""),
                )
            elif name == "get_audit_trail":
                return self._get_audit_trail(arguments.get("case_id", ""))
            elif name == "export_audit":
                return self._export_audit(
                    arguments.get("case_id", ""),
                    arguments.get("format", "json"),
                )
        except Exception as e:
            logger.error("MCP tool '%s' failed: %s", name, e)
            return MCPToolResult({"error": str(e)}, is_error=True)

    def _log_decision(
        self, case_id: str, step: str, data_points: Dict, reasoning: str
    ) -> MCPToolResult:
        self.audit.log_event(
            case_id=case_id,
            event_type=step,
            user_id="mcp_agent",
            input_data=data_points,
            llm_reasoning=reasoning,
            metadata={"source": "mcp_tool_call", "step": step},
        )
        return MCPToolResult({
            "status": "logged",
            "case_id": case_id,
            "step": step,
            "timestamp": datetime.now().isoformat(),
        })

    def _get_audit_trail(self, case_id: str) -> MCPToolResult:
        trail = self.audit.get_audit_trail(case_id)
        return MCPToolResult({
            "case_id": case_id,
            "event_count": len(trail),
            "events": trail,
        })

    def _export_audit(self, case_id: str, fmt: str) -> MCPToolResult:
        export_data = self.audit.export_audit_trail(case_id, fmt)
        return MCPToolResult({
            "case_id": case_id,
            "format": fmt,
            "data": export_data,
        })
