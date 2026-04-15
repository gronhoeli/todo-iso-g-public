import os, psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=psycopg.rows.dict_row)

def create_schema():
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("""
            
                CREATE TABLE IF NOT EXISTS todo_users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR NOT NULL
                );
                """)

    except Exception as e:
        print(f"Error while creating schema: {e}")
