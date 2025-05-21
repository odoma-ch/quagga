import logging
import requests
from rdflib.plugins.sparql import prepareQuery

logging.getLogger().setLevel(logging.INFO)


def validate_sparql_query(query: str) -> bool:
    """
    Validate a SPARQL query if it is syntactically correct

    Args:
        query (str): The SPARQL query to validate

    Returns:
        bool: True if the query is syntactically correct, False otherwise
    """
    try:
        prepareQuery(query)
        return True
    except Exception as e:
        logging.error(f"Invalid SPARQL syntax: {e}")
        return False


def check_sparql_endpoint(endpoint_uri: str) -> bool:
    """
    Check if the SPARQL endpoint is accessible.

    Args:
        endpoint_uri (str): The URI of the SPARQL endpoint.

    Returns:
        bool: True if the endpoint is accessible, False otherwise.
        str: The endpoint URI if accessible, None otherwise.
    """
    try:
        test_query = "SELECT * WHERE { ?s ?p ?o } LIMIT 1"
        response = requests.get(
            endpoint_uri,
            params={"query": test_query, "format": "json"},
            headers={"Accept": "application/sparql-results+json"},
        )
        if response.status_code != 200:
            logging.error(
                f"SPARQL endpoint not accessible (status code: {response.status_code})"
            )
            return False
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Cannot access SPARQL endpoint: {e}")
        return False


def escape_string(text: str) -> str:
    """Escape special characters in strings for Turtle format"""
    if not text:
        return ""
    return text.replace('"', '\\"').replace('\\', '\\\\').replace('\n', '\\n')
