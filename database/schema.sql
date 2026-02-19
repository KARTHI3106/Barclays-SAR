CREATE DATABASE sar_audit_trail;

\c sar_audit_trail;

CREATE TABLE IF NOT EXISTS sar_audit_trail (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(50) DEFAULT 'system',
    input_data JSONB,
    retrieved_context JSONB,
    llm_reasoning TEXT,
    generated_output TEXT,
    human_edits JSONB,
    model_version VARCHAR(50),
    confidence_score FLOAT,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_case_id ON sar_audit_trail(case_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON sar_audit_trail(timestamp);
CREATE INDEX IF NOT EXISTS idx_event_type ON sar_audit_trail(event_type);

CREATE TABLE IF NOT EXISTS sar_cases (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    narrative_text TEXT,
    confidence_score FLOAT,
    typology VARCHAR(100),
    assigned_analyst VARCHAR(50),
    approved_by VARCHAR(50),
    approved_at TIMESTAMP,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS idx_cases_status ON sar_cases(status);
