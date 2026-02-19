import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from src.utils.db_utils import DatabaseManager

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self):
        self.db = DatabaseManager()
        self.db.connect()
        self.in_memory_trail: Dict[str, List[Dict]] = {}

    def log_event(self, case_id: str, event_type: str, user_id: str = "system",
                  input_data: Optional[Dict] = None,
                  retrieved_context: Optional[Dict] = None,
                  llm_reasoning: Optional[str] = None,
                  generated_output: Optional[str] = None,
                  human_edits: Optional[Dict] = None,
                  model_version: Optional[str] = None,
                  confidence_score: Optional[float] = None,
                  metadata: Optional[Dict] = None):

        event = {
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "input_data": input_data,
            "retrieved_context": retrieved_context,
            "llm_reasoning": llm_reasoning,
            "generated_output": generated_output,
            "human_edits": human_edits,
            "model_version": model_version,
            "confidence_score": confidence_score,
            "metadata": metadata,
        }

        if case_id not in self.in_memory_trail:
            self.in_memory_trail[case_id] = []
        self.in_memory_trail[case_id].append(event)

        self.db.log_audit_event(
            case_id=case_id, event_type=event_type, user_id=user_id,
            input_data=input_data, retrieved_context=retrieved_context,
            llm_reasoning=llm_reasoning, generated_output=generated_output,
            human_edits=human_edits, model_version=model_version,
            confidence_score=confidence_score, metadata=metadata,
        )

        logger.info("Audit event: %s | %s | %s", case_id, event_type, user_id)

    def get_audit_trail(self, case_id: str) -> List[Dict]:
        db_trail = self.db.get_audit_trail(case_id)
        if db_trail:
            return db_trail
        return self.in_memory_trail.get(case_id, [])

    def export_audit_trail(self, case_id: str, fmt: str = "json") -> str:
        trail = self.get_audit_trail(case_id)
        if fmt == "json":
            return json.dumps(trail, indent=2, default=str)
        elif fmt == "csv":
            if not trail:
                return "No audit trail found"
            headers = list(trail[0].keys())
            lines = [",".join(headers)]
            for event in trail:
                values = [str(event.get(h, "")).replace(",", ";") for h in headers]
                lines.append(",".join(values))
            return "\n".join(lines)
        return json.dumps(trail, indent=2, default=str)

    def close(self):
        self.db.close()
