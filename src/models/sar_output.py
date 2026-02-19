from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime


class SARNarrative(BaseModel):
    case_id: str
    generated_at: datetime = None
    narrative_text: str = ""
    sections: Dict[str, str] = {}
    confidence_score: float = 0.0
    typology: str = ""
    red_flags: List[str] = []
    templates_used: List[str] = []
    model_version: str = ""
    transaction_stats: Dict = {}

    def __init__(self, **data):
        super().__init__(**data)
        if self.generated_at is None:
            self.generated_at = datetime.now()


class ExplainabilityOutput(BaseModel):
    case_id: str
    why_suspicious: List[str] = []
    typology_matched: str = ""
    typology_confidence: float = 0.0
    similar_cases: List[str] = []
    templates_used: List[str] = []
    model_reasoning: str = ""
    data_points_accessed: List[str] = []
    rules_matched: List[str] = []
    calculations: Dict[str, str] = {}
