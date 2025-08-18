import logging
import requests
from rdflib import Graph
from urllib.parse import urlparse
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib.plugins.sparql import prepareQuery
from rdflib.plugins.stores.sparqlstore import SPARQLStore

logging.getLogger().setLevel(logging.INFO)


def validate_url(url: str) -> tuple[bool, str]:
    """
    Validate if the URL is valid and return detailed error message.

    Args:
        url (str): The URL to validate
        
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, "URL cannot be empty"
    
    url = url.strip()
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            error_msg = f"Invalid URL format. Please provide a complete URL with protocol (http:// or https://)"
            logging.error(f"Invalid URL format: {url}")
            return False, error_msg

        if parsed.scheme not in ["http", "https"]:
            error_msg = f"Unsupported URL protocol '{parsed.scheme}'. Only HTTP and HTTPS are allowed"
            logging.error(f"Unsupported URL scheme: {parsed.scheme}")
            return False, error_msg
    except Exception as e:
        error_msg = f"Error parsing URL: {str(e)}"
        logging.error(f"Error parsing URL {url}: {e}")
        return False, error_msg
    
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 405:
            response = requests.get(url, timeout=10, allow_redirects=True, stream=True)

        if 200 <= response.status_code < 400:
            return True, ""
        else:
            error_msg = f"URL is not accessible (HTTP {response.status_code}). Please check the URL and try again"
            logging.error(f"URL returned status code {response.status_code}: {url}")
            return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error while validating URL: {str(e)}"
        logging.error(f"Unexpected error validating URL {url}: {e}")
        return False, error_msg


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


def check_sparql_endpoint_v2(endpoint_uri: str) -> bool:
    """
    Check if the SPARQL endpoint is accessible using SPARQLWrapper with a return format of JSON.

    Args:
        endpoint_uri (str): The URI of the SPARQL endpoint.

    Returns:
        bool: True if the endpoint is accessible and responds correctly, False otherwise.
    """
    try:
        sparql = SPARQLWrapper(endpoint_uri)
        sparql.setReturnFormat(JSON)
        sparql.setQuery("SELECT * WHERE { ?s ?p ?o } LIMIT 1")
        sparql.query().convert()

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
