from fastapi import FastAPI
from app.db import get_conn, create_schema

app = FastAPI()

create_schema()

@app.get("/")
def default_endpoint():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT version()")
        return cur.fetchone() 

