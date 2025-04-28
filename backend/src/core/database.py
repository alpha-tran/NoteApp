from typing import Any, List, Optional, Tuple, Union
from sqlalchemy import text
from sqlalchemy.engine import Connection
import logging

logger = logging.getLogger(__name__)

def secure_sql_execute(
    connection: Connection,
    query: str,
    params: Optional[Union[dict, List[Any], Tuple[Any, ...]]] = None,
) -> Any:
    """
    Securely execute a SQL query using SQLAlchemy's parameterized queries.
    
    Args:
        connection: SQLAlchemy connection object
        query: SQL query with parameter placeholders
        params: Query parameters (dict for named params, list/tuple for positional)
    
    Returns:
        Query result
        
    Example:
        # Instead of string concatenation:
        # BAD: f"SELECT * FROM users WHERE id = {user_id}"  # VULNERABLE!
        
        # Use parameterized queries:
        # GOOD: secure_sql_execute(conn, "SELECT * FROM users WHERE id = :id", {"id": user_id})
    """
    try:
        # Convert query to SQLAlchemy text object with parameters
        sql = text(query)
        
        # Execute with parameters
        if params:
            result = connection.execute(sql, params)
        else:
            result = connection.execute(sql)
            
        return result
        
    except Exception as e:
        logger.error(f"SQL query failed: {query}")
        logger.error(f"Parameters: {params}")
        logger.error(f"Error: {str(e)}")
        raise 