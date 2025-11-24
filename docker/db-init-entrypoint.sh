#!/bin/bash
set -euo pipefail

echo "Starting DB init job..."

# Variables expected from Cloud Run Job envs (or set as defaults)
: "${DB_HOST:?DB_HOST is required}"
: "${DB_USER:?DB_USER is required}"
: "${DB_NAME:=nba_db}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"
: "${PGPORT:=5432}"

# Execute the init SQL against the server (connects to 'postgres' first so DB creation works)
export PGPASSWORD="${DB_PASSWORD}"

echo "Connecting to ${DB_HOST}:${PGPORT} as ${DB_USER} to initialize ${DB_NAME}..."
psql "host=${DB_HOST} port=${PGPORT} user=${DB_USER} dbname=postgres sslmode=require" -f /app/init.sql

echo "DB init finished."
