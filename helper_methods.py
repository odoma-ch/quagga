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


def execute_sparql_query(query: str, endpoint_uri: str, limit: int = 20):
    """Run SPARQL query against endpoint and return list of bindings as dictionaries.

    Args:
        query (str): SPARQL query to execute.
        endpoint_uri (str): SPARQL endpoint URL.
        limit (int, optional): Maximum number of results to return. Defaults to 20.

    Returns:
        List[dict]: Query results where each dict maps variable names to their string values.
    """
    try:
        store = SPARQLStore(endpoint_uri)
        graph = Graph(store=store)

        # If user query lacks LIMIT, optionally append a limit to avoid huge payloads
        lowered = query.lower()
        if "limit" not in lowered:
            query_to_run = f"{query.strip()} LIMIT {limit}"
        else:
            query_to_run = query

        results = graph.query(query_to_run)

        formatted_results = []
        for row in results.bindings:
            formatted_row = {}
            for var, val in row.items():
                formatted_row[str(var)] = str(val)
            formatted_results.append(formatted_row)

        return formatted_results
    except Exception as e:
        logging.error(f"Error executing SPARQL query: {e}")
        raise
