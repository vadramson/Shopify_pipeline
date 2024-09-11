#!/bin/bash
set -e

# Create the database and schemas
psql -U airflow <<-EOSQL
    CREATE DATABASE shopify_db;
    \c shopify_db
    CREATE SCHEMA raw;
    CREATE SCHEMA staging;
    CREATE SCHEMA analytics;
EOSQL
