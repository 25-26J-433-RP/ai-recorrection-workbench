-- Akura AI - Feedback Tables Migration
-- Run this in Supabase SQL Editor to create the feedback tables

-- Table: correction_sessions
-- Stores each essay correction session by a teacher
CREATE TABLE IF NOT EXISTS correction_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_text TEXT NOT NULL,
    corrected_text TEXT,
    model_used VARCHAR(255),
    total_errors INT DEFAULT 0,
    accepted_count INT DEFAULT 0,
    rejected_count INT DEFAULT 0,
    edited_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Table: word_corrections
-- Stores individual word corrections within a session
CREATE TABLE IF NOT EXISTS word_corrections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES correction_sessions(id) ON DELETE CASCADE,
    original_word VARCHAR(255) NOT NULL,
    suggested_word VARCHAR(255),
    final_word VARCHAR(255),
    pattern VARCHAR(100),
    action VARCHAR(20),
    confidence FLOAT,
    position INT,
    created_at TIMESTAMP DEFAULT NOW(),
    action_timestamp TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_sessions_status ON correction_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON correction_sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_corrections_session_id ON word_corrections(session_id);
CREATE INDEX IF NOT EXISTS idx_corrections_action ON word_corrections(action);

-- Enable Row Level Security (optional, for production)
-- ALTER TABLE correction_sessions ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE word_corrections ENABLE ROW LEVEL SECURITY;

-- Grant access to the tables (adjust based on your auth setup)
-- GRANT ALL ON correction_sessions TO authenticated;
-- GRANT ALL ON word_corrections TO authenticated;
