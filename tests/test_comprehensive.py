"""Comprehensive verification script for all bug fixes and features."""
import sys
import json

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
        print("  ERROR:", name, "-", type(e).__name__, str(e)[:200])
        failed += 1


# === BUG FIX TESTS ===
print("=== BUG FIX VERIFICATION ===")
print()

def test_empty_transactions():
    from src.models.case_input import CaseInput
    try:
        CaseInput(
            case_id="test", 
            customer={"name": "A", "account_number": "123"},
            transactions=[], 
            alert_reason="test"
        )
        assert False, "Should have raised validation error"
    except ValueError:
        pass

def test_division_by_zero():
    from src.components.data_parser import DataParser
    p = DataParser(anonymize=False)
    case = json.load(open("data/sample_cases/case_003_50lakhs.json"))
    case["customer"]["expected_monthly_volume"] = 0
    parsed = p.parse_case_input(case)
    stats = p.calculate_transaction_stats(parsed.transactions)
    score = p.calculate_risk_score([], stats, parsed)
    assert isinstance(score, int), "Score should be int"

def test_nan_amount():
    from src.models.case_input import Transaction
    try:
        Transaction(
            date="2025-01-01", amount=float("nan"),
            type="Credit", originator="A", beneficiary="B"
        )
        assert False, "Should have raised validation error"
    except ValueError:
        pass

def test_empty_case_id():
    from src.models.case_input import CaseInput
    try:
        CaseInput(
            case_id="",
            customer={"name": "A", "account_number": "123"},
            transactions=[{
                "date": "2025-01-01", "amount": 100,
                "type": "Credit", "originator": "A", "beneficiary": "B"
            }],
            alert_reason="test"
        )
        assert False, "Should have raised validation error"
    except ValueError:
        pass

def test_empty_stats():
    from src.components.data_parser import DataParser
    p = DataParser(anonymize=False)
    stats = p.calculate_transaction_stats([])
    assert stats["total_transactions"] == 0
    assert stats["total_volume"] == 0.0

test("Empty transactions validation", test_empty_transactions)
test("Division by zero guard", test_division_by_zero)
test("NaN amount validation", test_nan_amount)
test("Empty case_id validation", test_empty_case_id)
test("Empty stats handling", test_empty_stats)

# === AUTH TESTS ===
print()
print("=== AUTH TESTS ===")

def test_auth_create_verify():
    from src.utils.auth import AuthManager
    auth = AuthManager()
    token = auth.create_token("test_user", "analyst")
    claims = auth.verify_token(token)
    assert claims is not None, "Token should be valid"
    assert claims["sub"] == "test_user"
    assert claims["role"] == "analyst"

def test_auth_role_hierarchy():
    from src.utils.auth import AuthManager
    auth = AuthManager()
    token = auth.create_token("admin_user", "admin")
    assert auth.check_role(token, "analyst") == True
    assert auth.check_role(token, "reviewer") == True
    assert auth.check_role(token, "admin") == True

    analyst_token = auth.create_token("analyst", "analyst")
    assert auth.check_role(analyst_token, "admin") == False
    assert auth.check_role(analyst_token, "analyst") == True

def test_auth_login():
    from src.utils.auth import AuthManager
    auth = AuthManager()
    token = auth.authenticate("admin", "auditwatch2026")
    assert token is not None, "Admin login should succeed"
    info = auth.get_user_info(token)
    assert info["role"] == "admin"
    assert info["user_id"] == "admin"

    bad = auth.authenticate("admin", "wrong")
    assert bad is None, "Bad password should fail"

def test_auth_invalid_token():
    from src.utils.auth import AuthManager
    auth = AuthManager()
    claims = auth.verify_token("invalid.token.here")
    assert claims is None, "Invalid token should return None"

test("Token create and verify", test_auth_create_verify)
test("Role hierarchy", test_auth_role_hierarchy)
test("Login authentication", test_auth_login)
test("Invalid token rejection", test_auth_invalid_token)

# === DB TESTS ===
print()
print("=== SQLITE DB TESTS ===")

def test_db_connect():
    from src.utils.db_utils import DatabaseManager
    db = DatabaseManager()
    db.connect()
    assert db.conn is not None, "Connection should be established"
    db.close()

def test_db_audit_log():
    from src.utils.db_utils import DatabaseManager
    db = DatabaseManager()
    db.connect()
    db.log_audit_event("test_case", "test_event", "test_user")
    trail = db.get_audit_trail("test_case")
    assert len(trail) >= 1, "Should have at least one event"
    db.close()

test("SQLite connect", test_db_connect)
test("SQLite audit log", test_db_audit_log)

# === MCP SERVER TESTS ===
print()
print("=== MCP SERVER TESTS ===")

def test_mcp_transaction_analyzer():
    from src.agents.mcp_servers import TransactionAnalyzerServer
    server = TransactionAnalyzerServer()
    tools = server.list_tools()
    assert len(tools) == 3, "Should have 3 tools"
    names = [t["name"] for t in tools]
    assert "analyze_transactions" in names
    assert "calculate_baseline" in names
    assert "classify_typology" in names

def test_mcp_analyze():
    from src.agents.mcp_servers import TransactionAnalyzerServer
    server = TransactionAnalyzerServer()
    case = json.load(open("data/sample_cases/case_003_50lakhs.json"))
    result = server.call_tool("analyze_transactions", {"case_json": case})
    assert not result.is_error, "Should not error"
    data = result.content
    assert "risk_score" in data
    assert "patterns" in data

def test_mcp_sar_template():
    from src.agents.mcp_servers import SARTemplateServer
    server = SARTemplateServer()
    tools = server.list_tools()
    assert len(tools) == 3

def test_mcp_audit_trail():
    from src.agents.mcp_servers import AuditTrailServer
    server = AuditTrailServer()
    tools = server.list_tools()
    assert len(tools) == 3

test("TransactionAnalyzer tools", test_mcp_transaction_analyzer)
test("TransactionAnalyzer analyze", test_mcp_analyze)
test("SARTemplateServer tools", test_mcp_sar_template)
test("AuditTrailServer tools", test_mcp_audit_trail)

# === A2A AGENT TESTS ===
print()
print("=== A2A AGENT TESTS ===")

def test_coordinator_card():
    from src.agents.a2a_agents import CoordinatorAgent
    coord = CoordinatorAgent()
    card = coord.agent_card()
    assert card["name"] == "coordinator_agent"
    assert "skills" in card
    assert "subordinate_agents" in card
    assert len(card["subordinate_agents"]) == 4

def test_data_enrichment():
    from src.agents.a2a_agents import DataEnrichmentAgent, AgentMessage
    agent = DataEnrichmentAgent()
    case = json.load(open("data/sample_cases/case_003_50lakhs.json"))
    msg = AgentMessage(
        sender="test", receiver=agent.AGENT_NAME,
        task_type="enrich", payload={"case_json": case}
    )
    result = agent.execute(msg)
    assert result.status == "completed"
    assert "patterns" in result.data
    assert "risk_score" in result.data

def test_agent_cards():
    from src.agents.a2a_agents import (
        DataEnrichmentAgent, TypologyAgent, NarrativeAgent, AuditAgent
    )
    for AgentClass in [DataEnrichmentAgent, TypologyAgent, NarrativeAgent, AuditAgent]:
        agent = AgentClass()
        card = agent.agent_card()
        assert "name" in card
        assert "skills" in card
        assert len(card["skills"]) >= 1

test("Coordinator agent card", test_coordinator_card)
test("DataEnrichment execution", test_data_enrichment)
test("All agent cards valid", test_agent_cards)

# === CONFIG TESTS ===
print()
print("=== CONFIG TESTS ===")

def test_no_hardcoded_password():
    import yaml
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    db = config.get("database", {})
    assert "password" not in db, "Password should not be in config.yaml"
    assert db.get("type") == "sqlite", "Should be sqlite"

def test_env_example_exists():
    from pathlib import Path
    assert Path(".env.example").exists(), ".env.example should exist"

test("No hardcoded password", test_no_hardcoded_password)
test(".env.example exists", test_env_example_exists)

# === SUMMARY ===
print()
print("=" * 50)
print("RESULTS: %d passed, %d failed" % (passed, failed))
if failed == 0:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")
    sys.exit(1)
