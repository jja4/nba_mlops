import psycopg2
from psycopg2 import OperationalError

# Database connection details
DB_HOST = "localhost"
DB_NAME = "nba_db"
DB_USER = "ubuntu"
DB_PASSWORD = "mlops"

# Connect to the PostgreSQL server
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
except OperationalError:
    # If the database doesn't exist, create it
    conn = psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    conn.close()

    # Reconnect to the newly created database
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()

# Check if the 'users' table exists
cur.execute(
    """
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.tables t
        JOIN information_schema.schemata s ON t.table_schema = s.schema_name
        WHERE t.table_name = 'users'
    )
    """
)
table_exists = cur.fetchone()[0]
print("users table exists:", table_exists)
if table_exists:
    # display the contents of the 'users' table
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    print("users table contents:")
    for row in rows:
        print(row)

# Create the 'users' table if it doesn't exist
if not table_exists:
    cur.execute(
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            disabled BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
    )

# Commit the changes
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()