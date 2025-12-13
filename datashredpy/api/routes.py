"""Routes for client metadata registration and management."""
import json
import logging

from datashredpy.api.models import Client

logger = logging.getLogger(__name__)


class Register(Client):
    """Register class for metadata processing and client creation."""

    @classmethod
    def metadata(cls, metadata_json: str) -> Client:
        """Parse metadata JSON and create Client object.
        
        Args:
            metadata_json: JSON string containing client metadata
            
        Returns:
            Client: Instantiated Client object from metadata
        """
        logger.debug(f"Processing metadata: {metadata_json}")
        client_dict = json.loads(metadata_json)
        return Client(**client_dict)
