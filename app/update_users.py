import time
import psycopg2
from psycopg2 import sql
from threading import Thread

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="master_db",
    user="postgres",
    password="MS2025@Secure!",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

def update_users_info():
    """Periodically updates users' ping values randomly."""
    while True:
        cursor.execute("""
            UPDATE users_info
            SET ping = ping + (random() * 20 - 10), updated_at = CURRENT_TIMESTAMP
            WHERE ping IS NOT NULL;
        """)
        conn.commit()
        time.sleep(10)  # Update every 10 seconds

# Start the update function in a separate thread
def start_updating():
    thread = Thread(target=update_users_info)
    thread.daemon = True
    thread.start()
