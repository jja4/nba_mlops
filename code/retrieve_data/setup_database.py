import psycopg2

# Database connection details
DB_HOST = "localhost"
DB_NAME = "nba_db"
DB_USER = "nba"
DB_PASSWORD = "mlops"

# Connect to the PostgreSQL server
conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# Create a cursor object
cur = conn.cursor()

# Create the 'users' table
cur.execute(
    """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL
        )
    """
    )

# Commit the changes and close the connection
conn.commit()
conn.close()
