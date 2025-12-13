"""Routes for registering and managing metadata."""
import json
import logging

from datashredpy.api.models import Domain, Client

logger = logging.getLogger(__name__)


class Register(Domain):
    """Register domain class for metadata management."""

    @classmethod
    def metadata(cls, metadata_json: str) -> Client:
        """Parse metadata JSON and return Client object.
        
        Args:
            metadata_json: JSON string containing client metadata
            
        Returns:
            Client: Parsed client object
        """
        client_dict = json.loads(metadata_json)
        return Client(**client_dict)
