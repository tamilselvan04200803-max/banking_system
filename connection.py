"""
Neo4j Database Connection and Helper Utilities
Smart Banking Mini-Project
"""

import os
import random
import string
from dotenv import load_dotenv

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

_driver = None


def get_driver():
    """
    Loads environment variables and returns a singleton Neo4j driver instance.
    Reads NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD from the environment.
    """
    global _driver
    if _driver is not None:
        return _driver

    load_dotenv()
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")

    if GraphDatabase is None:
        raise ImportError(
            "neo4j package is not installed. Please install it via 'pip install neo4j'."
        )

    _driver = GraphDatabase.driver(uri, auth=(user, password))
    return _driver


def close_driver():
    """
    Safely closes the active Neo4j driver instance if open.
    """
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


def run_query(cypher, params=None):
    """
    Executes any Cypher query (read or write) and returns a list of dictionaries,
    one per result row.
    """
    if params is None:
        params = {}

    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, params)
        return [record.data() for record in result]


def new_id(prefix):
    """
    Generates a unique prefixed identifier with 8 random uppercase
    alphanumeric characters (e.g. 'T3F9A12C', 'SR8B9A1C2').
    """
    chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}{chars}"
