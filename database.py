import os
import logging
import sqlite3
import mysql.connector
from typing import Optional, List, Dict

from dotenv import load_dotenv

load_dotenv()
logging.getLogger().setLevel(logging.INFO)
run_mode = os.getenv("RUN_MODE")


def connect_db():
    """Gets a database connection."""
    if run_mode == "RENDER":
        db_path = "/var/tmp/app_database.db"
        conn = sqlite3.connect(db_path, timeout=10.0)
        return conn
    else:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        return conn


def init_db():
    """Initializes the database by creating the table if it doesn't exist."""
    default_endpoints = [
        (
            "Gesis",
            "Social science research data",
            "https://data.gesis.org/gesiskg/sparql",
            "https://data.gesis.org/gesiskg/",
            "socio",
        ),
        # (
        #     "Swiss Art Research - BSO",
        #     "Swiss art and cultural heritage knowledge graph",
        #     "https://bso.swissartresearch.net/sparql",
        #     "https://bso.swissartresearch.net/",
        #     "art",
        # ),
        # (
        #     "Smithsonian Art Museum KG",
        #     "Smithsonian Institution art and cultural collections",
        #     "https://triplydb.com/smithsonian/american-art-museum/sparql",
        #     "https://triplydb.com/smithsonian/american-art-museum/",
        #     "art,museo",
        # ),
    ]
    conn = connect_db()
    try:
        cursor = conn.cursor()
        auto_increment = (
            "INT PRIMARY KEY AUTO_INCREMENT"
            if run_mode != "RENDER"
            else "INTEGER PRIMARY KEY AUTOINCREMENT"
        )

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS submissions (
                id {auto_increment},
                kg_endpoint TEXT NOT NULL,
                nl_question TEXT NOT NULL,
                sparql_query TEXT,
                username TEXT
            )
        """
        )
        conn.commit()

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS kg_endpoints (
                id {auto_increment},
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                about_page TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                domains TEXT,
                is_dump {'BOOLEAN DEFAULT FALSE' if run_mode != 'RENDER' else 'INTEGER DEFAULT 0'}
            )
        """
        )
        conn.commit()

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS validation_results (
                id {auto_increment},
                endpoint TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                validation_status TEXT,
                validation_message TEXT,
                username TEXT,
                sparql_query TEXT,
                query_result TEXT
            )
        """
        )
        conn.commit()

        # Ensure the `domains` column exists in case of previous deployments without it
        try:
            cursor.execute("ALTER TABLE kg_endpoints ADD COLUMN domains TEXT")
            conn.commit()
        except Exception:
            # Column already exists
            pass

        # Ensure the `source` column exists in submissions table for previous deployments
        try:
            cursor.execute("ALTER TABLE submissions ADD COLUMN source TEXT")
            conn.commit()
        except Exception:
            # Column already exists
            pass

        # Ensure the `about_page` column exists in kg_endpoints table for previous deployments
        try:
            cursor.execute("ALTER TABLE kg_endpoints ADD COLUMN about_page TEXT")
            conn.commit()
        except Exception:
            # Column already exists
            pass

        # Ensure the `is_dump` column exists in kg_endpoints table for previous deployments
        try:
            if run_mode != "RENDER":
                cursor.execute("ALTER TABLE kg_endpoints ADD COLUMN is_dump BOOLEAN DEFAULT FALSE")
            else:
                cursor.execute("ALTER TABLE kg_endpoints ADD COLUMN is_dump INTEGER DEFAULT 0")
            conn.commit()
        except Exception:
            # Column already exists
            pass

        mid_str = "%s" if run_mode != "RENDER" else "?"
        for name, description, endpoint, about_page, domains_str in default_endpoints:
            cursor.execute(
                f"""
                INSERT INTO kg_endpoints (name, description, endpoint, about_page, domains)
                SELECT {mid_str}, {mid_str}, {mid_str}, {mid_str}, {mid_str}
                WHERE NOT EXISTS (
                    SELECT 1 FROM kg_endpoints WHERE name = {mid_str} OR endpoint = {mid_str}
                )
            """,
                (name, description, endpoint, about_page, domains_str, name, endpoint),
            )
            conn.commit()

        logging.info("Database initialized for submissions and endpoints.")
    finally:
        cursor.close()
        conn.close()


def insert_submission(
    kg_endpoint: str,
    nl_question: str,
    email: str,
    sparql_query: Optional[str],
    source: Optional[str] = None,
):
    """Inserts a new submission into the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        suffix = "(%s, %s, %s, %s, %s)" if run_mode != "RENDER" else "(?, ?, ?, ?, ?)"
        cursor.execute(
            f"INSERT INTO submissions (kg_endpoint, nl_question, username, sparql_query, source) VALUES {suffix}",
            (kg_endpoint, nl_question, email, sparql_query, source),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def insert_kg_endpoint(
    name: str, description: str, endpoint: str, about_page: str, domains: List[str], is_dump: bool = False
):
    """Inserts a new KG endpoint into the database."""
    conn = connect_db()
    domain_str = ",".join(domains)
    print(
        f"Inserting KG endpoint: {name}, {description}, {endpoint}, {about_page}, {domain_str}, is_dump: {is_dump}"
    )
    try:
        cursor = conn.cursor()
        suffix = "(%s, %s, %s, %s, %s, %s)" if run_mode != "RENDER" else "(?, ?, ?, ?, ?, ?)"
        cursor.execute(
            f"INSERT INTO kg_endpoints (name, description, endpoint, about_page, domains, is_dump) VALUES {suffix}",
            (name, description, endpoint, about_page, domain_str, is_dump),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def insert_validation_result(
    endpoint: str,
    validation_status: str,
    validation_message: str,
    username: str,
    sparql_query: str,
    query_result: str,
):
    """Inserts a new validation result into the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        suffix = (
            "(%s, %s, %s, %s, %s, %s)" if run_mode != "RENDER" else "(?, ?, ?, ?, ?, ?)"
        )
        cursor.execute(
            f"INSERT INTO validation_results (endpoint, validation_status, validation_message, username, sparql_query, query_result) VALUES {suffix}",
            (
                endpoint,
                validation_status,
                validation_message,
                username,
                sparql_query,
                query_result,
            ),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_if_endpoint_exists(endpoint: str) -> bool:
    """Checks if a KG endpoint exists in the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        suffix = "WHERE endpoint = %s" if run_mode != "RENDER" else "WHERE endpoint = ?"
        cursor.execute(f"SELECT COUNT(*) FROM kg_endpoints {suffix}", (endpoint,))
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()
        conn.close()


def get_all_submissions() -> List[Dict]:
    """Retrieves all submissions from the database."""
    conn = connect_db()
    try:
        if run_mode == "RENDER":
            conn.row_factory = sqlite3.Row

        cursor = conn.cursor(dictionary=True) if run_mode != "RENDER" else conn.cursor()
        cursor.execute(
            "SELECT id, kg_endpoint, nl_question, sparql_query, username, source FROM submissions"
        )
        return (
            cursor.fetchall()
            if run_mode != "RENDER"
            else [dict(row) for row in cursor.fetchall()]
        )
    finally:
        cursor.close()
        conn.close()


def get_all_kg_metadata(for_one: bool = False, endpoint: str = None) -> List[Dict]:
    """Retrieves all KG endpoints from the database."""
    conn = connect_db()
    try:
        if run_mode == "RENDER":
            conn.row_factory = sqlite3.Row

        cursor = conn.cursor(dictionary=True) if run_mode != "RENDER" else conn.cursor()
        if not for_one:
            cursor.execute(
                "SELECT id, name, description, endpoint, about_page, domains FROM kg_endpoints ORDER BY name"
            )
            return (
                cursor.fetchall()
                if run_mode != "RENDER"
                else [dict(row) for row in cursor.fetchall()]
            )
        else:
            suffix = (
                "WHERE endpoint = %s" if run_mode != "RENDER" else "WHERE endpoint = ?"
            )
            cursor.execute(
                f"SELECT name, description, endpoint, about_page, domains, is_dump FROM kg_endpoints {suffix}",
                (endpoint,),
            )
            return (
                cursor.fetchone() if run_mode != "RENDER" else dict(cursor.fetchone())
            )
    finally:
        cursor.close()
        conn.close()


def get_kg_metadata_with_user_contributions(user_email: str) -> List[Dict]:
    """Retrieves KG metadata for endpoints where the user has made submissions."""
    conn = connect_db()
    try:
        if run_mode == "RENDER":
            conn.row_factory = sqlite3.Row

        cursor = conn.cursor(dictionary=True) if run_mode != "RENDER" else conn.cursor()

        # Get KG endpoints where user has submissions, then join with kg_endpoints table
        suffix = (
            """
        SELECT DISTINCT k.id, k.name, k.description, k.endpoint, k.about_page, k.domains 
        FROM kg_endpoints k 
        INNER JOIN submissions s ON k.endpoint = s.kg_endpoint 
        WHERE s.username = %s
        ORDER BY k.name
        """
            if run_mode != "RENDER"
            else """
        SELECT DISTINCT k.id, k.name, k.description, k.endpoint, k.about_page, k.domains 
        FROM kg_endpoints k 
        INNER JOIN submissions s ON k.endpoint = s.kg_endpoint 
        WHERE s.username = ?
        ORDER BY k.name
        """
        )

        cursor.execute(suffix, (user_email,))
        return (
            cursor.fetchall()
            if run_mode != "RENDER"
            else [dict(row) for row in cursor.fetchall()]
        )
    finally:
        cursor.close()
        conn.close()


def get_unique_kg_endpoints() -> List[str]:
    """Retrieves a list of unique KG endpoints in the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT endpoint FROM kg_endpoints")
        res = [row[0] for row in cursor.fetchall()]
        return sorted(res)
    finally:
        cursor.close()
        conn.close()


def get_submission(id_submission: str) -> Dict:
    """Retrieves a submission by its ID."""
    conn = connect_db()
    try:
        cursor = conn.cursor(dictionary=True) if run_mode != "RENDER" else conn.cursor()
        suffix = "WHERE id = %s" if run_mode != "RENDER" else "WHERE id = ?"
        cursor.execute(
            f"SELECT id, kg_endpoint, nl_question, sparql_query, username, source FROM submissions {suffix}",
            (id_submission,),
        )
        return cursor.fetchone()

    finally:
        cursor.close()
        conn.close()


def get_submissions_by_kg(kg_endpoint: str) -> List[Dict]:
    """Retrieves submissions for a specific KG endpoint."""
    conn = connect_db()
    try:
        if run_mode == "RENDER":
            conn.row_factory = sqlite3.Row

        cursor = conn.cursor(dictionary=True) if run_mode != "RENDER" else conn.cursor()
        suffix = (
            "WHERE kg_endpoint = %s"
            if run_mode != "RENDER"
            else "WHERE kg_endpoint = ?"
        )
        cursor.execute(
            f"SELECT id, kg_endpoint, nl_question, sparql_query, username, source FROM submissions {suffix}",
            (kg_endpoint,),
        )
        return (
            cursor.fetchall()
            if run_mode != "RENDER"
            else [dict(row) for row in cursor.fetchall()]
        )
    finally:
        cursor.close()
        conn.close()


def modify_submission(
    kg_endpoint: str,
    id_submission: str,
    email: str,
    nl_question: Optional[str],
    sparql_query: Optional[str],
):
    """Modifies a submission in the database."""
    conn = connect_db()
    try:
        cursor = conn.cursor(dictionary=True) if run_mode != "RENDER" else conn.cursor()
        update_fields = []
        params = []
        placeholder = "%s" if run_mode != "RENDER" else "?"
        
        if nl_question is not None:
            update_fields.append(f"nl_question = {placeholder}")
            params.append(nl_question)
            
        if sparql_query is not None:
            update_fields.append(f"sparql_query = {placeholder}")
            params.append(sparql_query)
        
        # Add WHERE clause parameters
        params.extend([id_submission, email, kg_endpoint])
        
        if update_fields:
            query = f"""
                UPDATE submissions
                SET {', '.join(update_fields)}
                WHERE id = {placeholder} AND username = {placeholder} AND kg_endpoint = {placeholder}
            """
            cursor.execute(query, params)
            conn.commit()
            
    finally:
        cursor.close()
        conn.close()
