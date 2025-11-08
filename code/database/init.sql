-- Check if the database exists and create it if it doesn't
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'nba_db') THEN
        CREATE DATABASE nba_db;
    END IF;
END $$;

-- Connect to the nba_db database
\c nba_db

-- Create the users table if it doesn't exist
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    disabled BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    prediction INTEGER,
    user_verification INTEGER,
    input_parameters JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

