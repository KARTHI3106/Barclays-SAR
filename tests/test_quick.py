import sys
sys.path.insert(0, '.')
import json
from src.components.data_parser import DataParser

dp = DataParser(anonymize=False)
data = json.load(open('data/sample_cases/case_003_50lakhs.json', encoding='utf-8'))
case = dp.parse_case_input(data)
stats = dp.calculate_transaction_stats(case.transactions)
patterns = dp.identify_patterns(case, stats)
risk = dp.calculate_risk_score(patterns, stats, case)

print(f"Case: {case.case_id}")
print(f"Transactions: {len(case.transactions)}")
print(f"Total Volume: INR {stats['total_volume']:,.2f}")
print(f"Patterns found: {len(patterns)}")
for p in patterns:
    print(f"  - {p}")
print(f"Risk Score: {risk}/100")
print()

# Test RAG engine
from src.components.rag_engine import RAGEngine
rag = RAGEngine()
case_summary = rag.build_case_summary(case, stats, patterns)
templates = rag.retrieve_templates(case_summary, top_k=2)
typology, confidence = rag.identify_typology(patterns, case.alert_reason)
print(f"Typology: {typology} (confidence: {confidence:.1f}%)")
print(f"Templates retrieved: {len(templates)}")
print()
print("ALL TESTS PASSED!")
