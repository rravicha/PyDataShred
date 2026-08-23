"""Entity creation and delegation module for domain management."""
import json
import logging
from dataclasses import dataclass
from typing import Any

from datashredpy.helper.models import Domain

logger = logging.getLogger(__name__)


@dataclass
class CreateEntity:
    """Factory class for creating domain entities."""

    entity_type: Any
    entity_data: dict

    def __post_init__(self) -> None:
        """Initialize and validate entity creation.
        
        Raises:
            TypeError: If entity_type is invalid
        """
        if not isinstance(self.entity_type, str):
            raise TypeError(f"entity_type must be string, got {type(self.entity_type)}")
        
        if self.entity_type not in ['domain', 'app']:
            raise TypeError(f"Invalid entity type: {self.entity_type}")

        if self.entity_type == 'domain':
            obj = Domain(self.entity_data)
            logger.info(f"Created domain entity: {obj}")
            return obj

    

    

