import json
from dataclasses import dataclass

from typing import Any

import os, sys
if os.uname().nodename == 'zebronics':
    sys.path.append('/home/susi/workspace/github/PyDataShred')
else:
    sys.path.append('/workspaces/PyDataShred')

from datashredpy.helper.models import Domain

@dataclass
class CreateEntity:
    entity_type: Any
    entity_data: dict
    
    def __post__init(self):
        if os.uname().nodename == 'zebronics':
            sys.path.append('/home/susi/workspace/github/PyDataShred')
        else:
            sys.path.append('/workspaces/PyDataShred')

        from datashredpy.core.handler import DomainHandler, AppHandler, PipelineHandler

        if not instance(self.type, str):
            raise TypeError
        if self.type not in ['domain', 'app']:
            raise TypeError('Entity type error')
        
        if self.type == 'domain':
            obj = Domain(entity_data) 
            print(obj)
            return obj

    

    

