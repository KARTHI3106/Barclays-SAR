from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class AuditEvent(BaseModel):
    case_id: str
    timestamp: datetime = None
    event_type: str  # data_input, rag_retrieval, llm_generation, human_edit, approval, rejection
    user_id: str = "system"
    input_data: Optional[Dict[str, Any]] = None
    retrieved_context: Optional[Dict[str, Any]] = None
    llm_reasoning: Optional[str] = None
    generated_output: Optional[str] = None
    human_edits: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.now()
