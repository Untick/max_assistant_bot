-- Initial database schema for Personal Planner
-- Migration 001

-- Users table (single user identification by Telegram user_id)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_user_id BIGINT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Calendar events cache
CREATE TABLE IF NOT EXISTS calendar_events (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_user_id),
    event_id VARCHAR(255) NOT NULL,
    summary VARCHAR(500) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    location VARCHAR(500),
    attendees JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_user_id),
    task_id VARCHAR(255),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    deadline TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Meeting notes (карточки встреч)
CREATE TABLE IF NOT EXISTS meeting_notes (
    id SERIAL PRIMARY KEY,
    meeting_id VARCHAR(255) NOT NULL,
    user_id BIGINT REFERENCES users(telegram_user_id),
    title VARCHAR(500) NOT NULL,
    meeting_date TIMESTAMP WITH TIME ZONE NOT NULL,
    participants JSONB,
    key_decisions JSONB,
    action_items JSONB,
    next_steps JSONB,
    raw_transcript TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Dialog history (for RAG)
CREATE TABLE IF NOT EXISTS dialog_history (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_user_id),
    message_text TEXT NOT NULL,
    is_voice BOOLEAN DEFAULT FALSE,
    transcribed_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RAG index metadata
CREATE TABLE IF NOT EXISTS rag_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    source VARCHAR(100),
    embedding_vector VECTOR(768),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Scheduler reminders
CREATE TABLE IF NOT EXISTS reminders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_user_id),
    event_id VARCHAR(255),
    reminder_type VARCHAR(20) NOT NULL,
    send_at TIMESTAMP WITH TIME ZONE NOT NULL,
    sent BOOLEAN DEFAULT FALSE,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log (п. 6.4, 9.2)
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    service VARCHAR(100) NOT NULL,
    user_id BIGINT,
    action VARCHAR(200) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    latency_ms INTEGER,
    error TEXT
);

-- Encrypted tokens storage (п. 6.2)
CREATE TABLE IF NOT EXISTS encrypted_tokens (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_user_id),
    token_type VARCHAR(100) NOT NULL,
    encrypted_value TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_calendar_events_user ON calendar_events(user_id);
CREATE INDEX IF NOT EXISTS idx_calendar_events_start ON calendar_events(start_time);
CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);
CREATE INDEX IF NOT EXISTS idx_meeting_notes_user ON meeting_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_dialog_history_user ON dialog_history(user_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_source ON rag_chunks(source);
CREATE INDEX IF NOT EXISTS idx_reminders_send_at ON reminders(send_at);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);

-- FTS5 index for full-text search (п. 4.6)
CREATE INDEX IF NOT EXISTS idx_rag_chunks_fts ON rag_chunks USING gin(to_tsvector('russian', content));
