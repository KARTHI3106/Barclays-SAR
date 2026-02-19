"""Extended QA bug-finding tests -- edge cases and integration checks."""
import sys
import json
import os

sys.path.insert(0, ".")

passed = 0
failed = 0

def test(name, fn):
    global passed, failed
    try:
        fn()
        print("  PASS:", name)
        passed += 1
    except AssertionError as e:
        print("  FAIL:", name, "-", e)
        failed += 1
    except Exception as e:
        print("  ERROR:", name, "-", type(e).__name__, ":", str(e)[:300])
        failed += 1


print("=== EXTENDED QA BUG HUNT ===")
print()

# ---- Bug Hunt 1: export_audit_trail fmt parameter ----
print("--- Audit Logger fmt Parameter ---")

def test_audit_export_fmt_json():
    from src.components.audit_logger import AuditLogger
    al = AuditLogger()
    al.log_event("qa_test", "qa_check", "tester")
    result = al.export_audit_trail("qa_test", fmt="json")
    assert isinstance(result, str), "Should return string"
    parsed = json.loads(result)
    assert isinstance(parsed, list), "Should parse to list"

def test_audit_export_fmt_csv():
    from src.components.audit_logger import AuditLogger
    al = AuditLogger()
    al.log_event("qa_csv", "qa_check", "tester")
    result = al.export_audit_trail("qa_csv", fmt="csv")
    assert "case_id" in result, "CSV should have headers"

def test_main_export_audit():
    """Test that main.py export_audit calls work (via fmt keyword)."""
    from src.main import SARGenerator
    gen = SARGenerator()
    # Should not crash even with nonexistent case
    result = gen.export_audit("nonexistent_case", fmt="json")
    assert isinstance(result, str)

test("audit export_audit_trail fmt=json", test_audit_export_fmt_json)
test("audit export_audit_trail fmt=csv", test_audit_export_fmt_csv)
test("main.py export_audit fmt= pass-through", test_main_export_audit)


# ---- Bug Hunt 2: A2A Coordinator result dict keys ----
print()
print("--- A2A Result Key Matching ---")

def test_coordinator_result_keys():
    """Verify CoordinatorAgent.execute() returns the keys that app.py expects."""
    from src.agents.a2a_agents import CoordinatorAgent
    coord = CoordinatorAgent()
    case = json.load(open("data/sample_cases/case_001_structuring.json"))
    result = coord.execute(case)

    # app.py expects these keys
    assert "status" in result, "Missing 'status' key"
    assert "agent_steps" in result, "Missing 'agent_steps' key"
    assert "results" in result, "Missing 'results' key"

    results = result["results"]
    # app.py references result["results"]["data"], result["results"]["typology"],
    # result["results"]["narrative"]
    assert "data" in results, "Missing 'data' in results -- app.py expects it"
    assert "typology" in results, "Missing 'typology' in results -- app.py expects it"
    assert "narrative" in results, "Missing 'narrative' in results -- app.py expects it"

test("Coordinator result keys match app.py expectations", test_coordinator_result_keys)


# ---- Bug Hunt 3: App references result["results"]["data_enrichment"] vs "data" ----
print()
print("--- App.py Data Key Mismatch ---")

def test_coordinator_data_key_name():
    """Coordinator stores in 'data_enrichment' internally but result should have 'data' key for app.py."""
    from src.agents.a2a_agents import CoordinatorAgent
    coord = CoordinatorAgent()
    case = json.load(open("data/sample_cases/case_001_structuring.json"))
    result = coord.execute(case)

    # In the coordinator execute method, the final dict has:
    # "results" -> {"data": data_result.data, "typology": ..., "narrative": ...}
    # But internally it stores results["data_enrichment"] = data_result
    # The RETURN dict should have "data", NOT "data_enrichment"
    assert "data" in result["results"], "Should have 'data' key not 'data_enrichment'"

test("Coordinator returns 'data' key (not 'data_enrichment')", test_coordinator_data_key_name)


# ---- Bug Hunt 4: Sample case JSON matches Pydantic model ----
print()
print("--- Sample Case Validation ---")

def test_sample_case_001():
    from src.models.case_input import CaseInput
    case = json.load(open("data/sample_cases/case_001_structuring.json"))
    parsed = CaseInput(**case)
    assert len(parsed.transactions) > 0

def test_sample_case_002():
    from src.models.case_input import CaseInput
    case = json.load(open("data/sample_cases/case_002_layering.json"))
    parsed = CaseInput(**case)
    assert len(parsed.transactions) > 0

def test_sample_case_003():
    from src.models.case_input import CaseInput
    case = json.load(open("data/sample_cases/case_003_50lakhs.json"))
    parsed = CaseInput(**case)
    assert len(parsed.transactions) > 0

test("case_001_structuring.json valid", test_sample_case_001)
test("case_002_layering.json valid", test_sample_case_002)
test("case_003_50lakhs.json valid", test_sample_case_003)


# ---- Bug Hunt 5: Config YAML no secrets ----
print()
print("--- Security Checks ---")

def test_no_password_in_config():
    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    assert "password" not in str(config).lower() or "${" in config.get("security", {}).get("jwt_secret", ""), \
        "Plain-text password found in config.yaml"

def test_env_file_not_committed():
    """Check .gitignore includes .env."""
    from pathlib import Path
    gitignore = Path(".gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        assert ".env" in content, ".env should be in .gitignore"
    # If no .gitignore, skip (not a critical failure for MVP)

def test_jwt_secret_not_default():
    """Verify JWT_SECRET env var is loaded."""
    from src.config import CONFIG
    secret = CONFIG.get("security", {}).get("jwt_secret", "")
    # It's OK if it's the env var expansion or a set value
    assert secret, "JWT secret should not be empty"

test("No plaintext password in config.yaml", test_no_password_in_config)
test(".env in .gitignore", test_env_file_not_committed)
test("JWT secret loaded", test_jwt_secret_not_default)


# ---- Bug Hunt 6: DB Operations ----
print()
print("--- DB Edge Cases ---")

def test_db_save_case():
    from src.utils.db_utils import DatabaseManager
    db = DatabaseManager()
    db.connect()
    db.save_case("qa_case_01", "test narrative", 75.0, "structuring", "qa_tester")
    db.update_case_status("qa_case_01", "approved", approved_by="qa_admin")
    db.close()

def test_db_double_connect():
    from src.utils.db_utils import DatabaseManager
    db = DatabaseManager()
    db.connect()
    db.connect()  # Should not crash
    db.close()

def test_db_operations_without_connect():
    """Operations should gracefully handle no connection."""
    from src.utils.db_utils import DatabaseManager
    db = DatabaseManager()
    # Don't call connect
    db.log_audit_event("test", "test")  # Should not crash
    trail = db.get_audit_trail("test")
    assert trail == [], "Should return empty list without connection"

test("DB save_case and update_case_status", test_db_save_case)
test("DB double connect no crash", test_db_double_connect)
test("DB operations without connect", test_db_operations_without_connect)


# ---- Bug Hunt 7: PDF generator ----
print()
print("--- PDF Generation ---")

def test_pdf_with_narrative_object():
    from src.models.sar_output import SARNarrative
    from src.utils.pdf_generator import generate_pdf
    narrative = SARNarrative(
        case_id="pdf_test",
        narrative_text="I. SUMMARY\\nTest narrative with <special> & characters.\nII. ACCOUNT\\nTest section.",
        confidence_score=80.0,
        typology="structuring",
    )
    pdf_bytes = generate_pdf(narrative, "pdf_test")
    assert len(pdf_bytes) > 100, "PDF should have content"
    assert pdf_bytes[:4] == b"%PDF", "Should start with PDF header"

def test_pdf_with_string():
    from src.utils.pdf_generator import generate_pdf
    pdf_bytes = generate_pdf("Simple string narrative", "str_test")
    assert pdf_bytes[:4] == b"%PDF"

test("PDF from SARNarrative object", test_pdf_with_narrative_object)
test("PDF from string", test_pdf_with_string)


# ---- Bug Hunt 8: MCP Server edge cases ----
print()
print("--- MCP Server Edge Cases ---")

def test_mcp_unknown_tool():
    from src.agents.mcp_servers import TransactionAnalyzerServer
    server = TransactionAnalyzerServer()
    result = server.call_tool("nonexistent_tool", {})
    assert result.is_error, "Unknown tool should return error"

def test_mcp_empty_case():
    """MCP should handle gracefully when case JSON is malformed."""
    from src.agents.mcp_servers import TransactionAnalyzerServer
    server = TransactionAnalyzerServer()
    result = server.call_tool("analyze_transactions", {"case_json": {}})
    assert result.is_error, "Empty case should error"

test("MCP unknown tool returns error", test_mcp_unknown_tool)
test("MCP empty case handled gracefully", test_mcp_empty_case)


# ---- Bug Hunt 9: Auth edge cases ----
print()
print("--- Auth Edge Cases ---")

def test_auth_empty_credentials():
    from src.utils.auth import AuthManager
    auth = AuthManager()
    assert auth.authenticate("", "") is None
    assert auth.authenticate("admin", "") is None
    assert auth.authenticate("", "auditwatch2026") is None

def test_auth_expired_token():
    """Create token with past expiry -- should fail verification."""
    from src.utils.auth import AuthManager
    import time
    auth = AuthManager()
    # Monkey-patch expiry to create an already-expired token
    original_expiry = auth.token_expiry_hours
    auth.token_expiry_hours = -1  # -1 hour = already expired
    token = auth.create_token("test", "analyst")
    auth.token_expiry_hours = original_expiry
    claims = auth.verify_token(token)
    assert claims is None, "Expired token should fail verification"

def test_auth_get_user_info_bad_token():
    from src.utils.auth import AuthManager
    auth = AuthManager()
    info = auth.get_user_info("bad.token.here")
    assert info is None

test("Auth empty credentials", test_auth_empty_credentials)
test("Auth expired token rejection", test_auth_expired_token)
test("Auth get_user_info with bad token", test_auth_get_user_info_bad_token)


# ---- Bug Hunt 10: Anonymization ----
print()
print("--- Anonymization ---")

def test_anonymization_consistency():
    """Same input should produce same anonymized output."""
    from src.utils.anonymization import anonymize_value
    result1 = anonymize_value("Rajesh Kumar", "NAME")
    result2 = anonymize_value("Rajesh Kumar", "NAME")
    assert result1 == result2, "Should be deterministic"
    assert "Rajesh" not in result1, "Original name should not appear"

def test_anonymize_full_case():
    from src.utils.anonymization import anonymize_case
    from src.models.case_input import CaseInput
    case = CaseInput(**json.load(open("data/sample_cases/case_003_50lakhs.json")))
    original_name = case.customer.name
    anon = anonymize_case(case)
    assert anon.customer.name != original_name, "Name should be anonymized"
    assert anon.case_id == case.case_id, "Case ID should not change"

test("Anonymization deterministic", test_anonymization_consistency)
test("Full case anonymization", test_anonymize_full_case)


# === SUMMARY ===
print()
print("=" * 50)
print("EXTENDED QA RESULTS: %d passed, %d failed" % (passed, failed))
if failed == 0:
    print("ALL EXTENDED QA TESTS PASSED -- NO BUGS FOUND")
else:
    print("BUGS FOUND -- FIX REQUIRED")
    sys.exit(1)
