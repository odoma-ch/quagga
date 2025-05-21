import os
import logging
import mysql.connector
from typing import Optional, List, Dict

from dotenv import load_dotenv

load_dotenv()
logging.getLogger().setLevel(logging.INFO)


def connect_db():
    """Gets a database connection."""
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    return conn


def init_db():
    """Initializes the database by creating the table if it doesn't exist."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INT PRIMARY KEY AUTO_INCREMENT,
                kg_endpoint TEXT NOT NULL,
                nl_question TEXT NOT NULL,
                sparql_query TEXT,
                username TEXT
            )
        """)
        conn.commit()
        logging.info("Database initialized.")
    finally:
        cursor.close()
        conn.close()


def insert_submission(kg_endpoint: str, nl_question: str, email: str, sparql_query: Optional[str]):
    """Inserts a new submission into the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO submissions (kg_endpoint, nl_question, username, sparql_query) VALUES (%s, %s, %s, %s)",
            (kg_endpoint, nl_question, email, sparql_query)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_all_submissions() -> List[Dict]:
    """Retrieves all submissions from the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, kg_endpoint, nl_question, sparql_query, username FROM submissions")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_unique_kg_endpoints() -> List[str]:
    """Retrieves a list of unique KG endpoints in the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT kg_endpoint FROM submissions")
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()


def get_submissions_by_kg(kg_endpoint: str) -> List[Dict]:
    """Retrieves submissions for a specific KG endpoint."""
    conn = connect_db()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, kg_endpoint, nl_question, sparql_query, username FROM submissions WHERE kg_endpoint = %s",
            (kg_endpoint,)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
