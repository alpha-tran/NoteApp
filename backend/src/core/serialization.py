import json
from typing import Any, Optional, Type, TypeVar
from datetime import datetime
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar('T')

class SecureSerializer:
    """
    Secure serialization/deserialization using JSON instead of pickle/dill.
    Supports Pydantic models and basic Python types.
    """
    
    @staticmethod
    def serialize(obj: Any) -> str:
        """
        Securely serialize an object to JSON string.
        
        Args:
            obj: Object to serialize (must be JSON-serializable)
            
        Returns:
            JSON string
        """
        if isinstance(obj, BaseModel):
            # Handle Pydantic models
            return obj.model_dump_json()
        elif isinstance(obj, datetime):
            # Handle datetime objects
            return obj.isoformat()
        else:
            # Handle basic types
            try:
                return json.dumps(obj, default=str)
            except Exception as e:
                logger.error(f"Failed to serialize object: {obj}")
                logger.error(f"Error: {str(e)}")
                raise
    
    @staticmethod
    def deserialize(data: str, model: Optional[Type[T]] = None) -> Any:
        """
        Securely deserialize JSON string to object.
        
        Args:
            data: JSON string to deserialize
            model: Optional Pydantic model class to deserialize into
            
        Returns:
            Deserialized object
        """
        try:
            # Parse JSON
            parsed = json.loads(data)
            
            # Convert to model if specified
            if model is not None:
                if issubclass(model, BaseModel):
                    return model.model_validate(parsed)
                else:
                    raise ValueError(f"Model must be a Pydantic model, got {model}")
                    
            return parsed
            
        except Exception as e:
            logger.error(f"Failed to deserialize data: {data}")
            logger.error(f"Error: {str(e)}")
            raise

# Example usage:
"""
# Instead of pickle/dill:
# BAD:
# import pickle
# data = pickle.dumps(obj)  # VULNERABLE!
# obj = pickle.loads(data)  # VULNERABLE!

# Use secure serialization:
# GOOD:
serializer = SecureSerializer()
data = serializer.serialize(obj)
obj = serializer.deserialize(data, model=MyModel)
""" 