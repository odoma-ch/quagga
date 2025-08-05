import logging
import requests
from rdflib.plugins.sparql import prepareQuery
from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore

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
    Check if the SPARQL endpoint is accessible using rdflib.

    Args:
        endpoint_uri (str): The URI of the SPARQL endpoint.

    Returns:
        bool: True if the endpoint is accessible and responds correctly, False otherwise.
    """
    try:
        store = SPARQLStore(endpoint_uri)
        graph = Graph(store=store)
        test_query = """
        SELECT * WHERE { 
            ?s ?p ?o 
        } LIMIT 1
        """

        results = graph.query(test_query)
        list(results)
        
        logging.info(f"SPARQL endpoint {endpoint_uri} is accessible and working")
        return True
        
    except Exception as e:
        logging.error(f"Cannot access SPARQL endpoint {endpoint_uri}: {e}")
        return False


def escape_string(text: str) -> str:
    """Escape special characters in strings for Turtle format"""
    if not text:
        return ""
    return text.replace('"', '\\"').replace('\\', '\\\\').replace('\n', '\\n')
