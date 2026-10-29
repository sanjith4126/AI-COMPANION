import os
import psycopg2

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
db_url = os.environ["SUPABASE_DB_URL"]
schema_path = os.path.join(os.path.dirname(__file__), "..", "database", "schema.sql")

print(f"Connecting to {db_url}...")
try:
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cursor = conn.cursor()
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        sql = f.read()
        
    print("Executing schema...")
    cursor.execute(sql)
    print("Schema executed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
