import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import chromadb
from chromadb.config import Settings

from src.config import CONFIG
from src.models.case_input import CaseInput

logger = logging.getLogger(__name__)


class RAGEngine:
    """Retrieval-Augmented Generation engine using ChromaDB for template and regulatory retrieval."""

    def __init__(self):
        persist_dir = CONFIG["chromadb"]["persist_directory"]
        collection_name = CONFIG["chromadb"]["collection_name"]

        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            is_persistent=True,
            persist_directory=persist_dir
        ))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Load templates and regulatory data
        self._load_templates()
        self._load_regulatory_data()

        logger.info(f"RAG Engine initialized. Collection '{collection_name}' has {self.collection.count()} documents.")

    def _load_templates(self):
        """Load SAR templates into ChromaDB."""
        template_dir = Path(__file__).parent.parent.parent / "data" / "templates"
        if not template_dir.exists():
            logger.warning(f"Template directory not found: {template_dir}")
            return

        existing_ids = set()
        try:
            result = self.collection.get()
            existing_ids = set(result["ids"]) if result["ids"] else set()
        except Exception:
            pass

        for template_file in template_dir.glob("*.txt"):
            doc_id = f"template_{template_file.stem}"
            if doc_id in existing_ids:
                continue

            content = template_file.read_text(encoding="utf-8")
            self.collection.add(
                documents=[content],
                metadatas=[{
                    "type": "template",
                    "typology": template_file.stem.replace("_template", ""),
                    "source": str(template_file.name)
                }],
                ids=[doc_id]
            )
            logger.info(f"Loaded template: {template_file.name}")

    def _load_regulatory_data(self):
        """Load typology descriptions into ChromaDB."""
        reg_dir = Path(__file__).parent.parent.parent / "data" / "regulatory"
        typology_file = reg_dir / "typology_descriptions.json"

        if not typology_file.exists():
            logger.warning(f"Typology file not found: {typology_file}")
            return

        existing_ids = set()
        try:
            result = self.collection.get()
            existing_ids = set(result["ids"]) if result["ids"] else set()
        except Exception:
            pass

        with open(typology_file, "r", encoding="utf-8") as f:
            typologies = json.load(f)

        for key, data in typologies.items():
            doc_id = f"typology_{key}"
            if doc_id in existing_ids:
                continue

            content = f"{data['name']}\n{data['description']}\nIndicators: {', '.join(data['indicators'])}\n{data['pmla_reference']}\n{data['rbi_reference']}"
            self.collection.add(
                documents=[content],
                metadatas=[{
                    "type": "typology",
                    "typology": key,
                    "name": data["name"]
                }],
                ids=[doc_id]
            )
            logger.info(f"Loaded typology: {key}")

    def retrieve_templates(self, query: str, top_k: int = 2) -> List[Dict]:
        """Retrieve most relevant SAR templates for a given case summary."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"type": "template"}
        )

        templates = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                templates.append({
                    "id": results["ids"][0][i] if results["ids"] else f"template_{i}",
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })

        logger.info(f"Retrieved {len(templates)} templates for query")
        return templates

    def identify_typology(self, patterns: List[str], alert_reason: str) -> Tuple[str, float]:
        """Identify the most likely crime typology based on patterns."""
        query = f"Patterns: {'; '.join(patterns)}. Alert: {alert_reason}"

        results = self.collection.query(
            query_texts=[query],
            n_results=1,
            where={"type": "typology"}
        )

        if results and results["metadatas"] and results["metadatas"][0]:
            typology = results["metadatas"][0][0].get("typology", "unknown")
            distance = results["distances"][0][0] if results["distances"] else 1.0
            confidence = max(0, min(100, (1 - distance) * 100))

            # Boost confidence for keyword matches
            keyword_map = {
                "structuring": ["structuring", "threshold", "smurfing", "below reporting"],
                "layering": ["layering", "multiple accounts", "rapid transfer", "cross-border"],
                "wire_fraud": ["wire", "swift", "remittance", "foreign"],
                "cash_business": ["cash", "retail", "business volume"],
                "identity_theft": ["identity", "kyc", "synthetic", "document"],
                "rapid_movement": ["rapid", "same day", "immediate transfer"],
                "round_tripping": ["round-trip", "foreign investment", "circular"]
            }

            combined_text = (alert_reason + " " + " ".join(patterns)).lower()
            for typo, keywords in keyword_map.items():
                if any(kw in combined_text for kw in keywords):
                    if typo == typology:
                        confidence = min(100, confidence + 15)

            logger.info(f"Typology identified: {typology} (confidence: {confidence:.1f}%)")
            return typology, confidence

        return "unknown", 0.0

    def get_regulatory_context(self, typology: str) -> str:
        """Get regulatory context for a specific typology."""
        reg_file = Path(__file__).parent.parent.parent / "data" / "regulatory" / "typology_descriptions.json"
        if not reg_file.exists():
            return "PMLA Section 12 requires reporting of suspicious transactions to FIU-IND."

        with open(reg_file, "r", encoding="utf-8") as f:
            typologies = json.load(f)

        if typology in typologies:
            data = typologies[typology]
            return f"""Typology: {data['name']}
Description: {data['description']}
Key Indicators: {', '.join(data['indicators'])}
Legal Reference: {data['pmla_reference']}
Regulatory Reference: {data['rbi_reference']}
Filing Requirement: STR must be filed with FIU-IND within 7 days of suspicion determination under PMLA Section 12."""
        else:
            return """General regulatory context:
- PMLA Section 12: Obligation to report suspicious transactions to FIU-IND
- PMLA Section 3: Definition of money laundering offence
- RBI Master Direction on KYC: Customer due diligence requirements
- STR filing deadline: 7 days from date of suspicion determination"""

    def build_case_summary(self, case: CaseInput, stats: Dict, patterns: List[str]) -> str:
        """Build a text summary of the case for template retrieval."""
        return f"""Case {case.case_id}: {case.alert_reason}
Customer: {case.customer.occupation}, KYC: {case.customer.kyc_risk_rating}
Transactions: {stats.get('total_transactions', 0)} totaling {stats.get('currency', 'INR')} {stats.get('total_volume', 0):,.2f}
Patterns: {'; '.join(patterns)}
Period: {stats.get('date_range_start', 'N/A')} to {stats.get('date_range_end', 'N/A')}"""
